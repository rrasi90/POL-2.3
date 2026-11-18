import { expect, test, type Page, type TestInfo } from "@playwright/test";
import {
  appAlert,
  deliveryOtp,
  line,
  loginAsRetailer,
  loginAsVendor,
  openBasket,
  resetTenant,
  retailerPhone,
  seedCart,
  vendorPhone,
} from "./helpers";

const REVIEW_BUTTON = "بررسی تخصیص و ادامه تسویه";
const ADDRESS = "اهواز، خیابان نادری، نبش خیابان سعدی، فروشگاه شایان";
const PLACE_ORDER_BUTTON = "تأیید نهایی و ثبت قطعی سفارش";
const CONFIRM_DELIVERY_BUTTON = "تأیید و ثبت نهایی تحویل سفارش";
const REFRESH_BUTTON = "به‌روزرسانی";
/** Disjoint from login.spec (0) and basket-sync (12) so OTP rate limits never collide. */
const PHONE_SALT = 20;

function childOrderId(links: string[]): string {
  const hit = links.find((href) => /\/retailer\/orders\/[0-9a-f-]{36}$/.test(href));
  if (!hit) throw new Error(`no child order link among: ${links.join(", ")}`);
  return hit.slice(hit.lastIndexOf("/") + 1);
}

async function placeOrder(page: Page): Promise<string> {
  await openBasket(page);
  await page.getByRole("button", { name: REVIEW_BUTTON }).click();
  await page.waitForURL("**/retailer/checkout");
  await expect(page.getByRole("heading", { name: "بررسی تخصیص و تسویه حساب" })).toBeVisible();
  await page.getByLabel(/آدرس دقیق تحویل سفارش/).fill(ADDRESS);
  await page.getByRole("button", { name: PLACE_ORDER_BUTTON }).click();
  await expect(page.getByRole("heading", { name: "سفارش شما با موفقیت ثبت شد" })).toBeVisible();
  const hrefs = await page
    .locator('a[href^="/retailer/orders/"]')
    .evaluateAll((anchors) => anchors.map((a) => a.getAttribute("href") ?? ""));
  const orderId = childOrderId(hrefs);
  await page.locator(`a[href="/retailer/orders/${orderId}"]`).first().click();
  await page.waitForURL(`**/retailer/orders/${orderId}`);
  return orderId;
}

async function vendorFulfillToDispatch(page: Page, orderId: string): Promise<void> {
  await page.getByRole("link", { name: "سفارش‌ها", exact: true }).click();
  await page.waitForURL("**/vendor/orders**");
  const row = page.locator(`a[href="/vendor/orders/${orderId}"]`);
  await expect(row).toBeVisible();
  await row.click();
  await page.waitForURL(`**/vendor/orders/${orderId}`);

  await page.getByRole("button", { name: "تأیید و پذیرش کامل" }).click();
  await expect(page.getByRole("button", { name: "شروع آماده‌سازی" })).toBeVisible();
  await page.getByRole("button", { name: "شروع آماده‌سازی" }).click();
  await expect(page.getByRole("button", { name: "علامت‌گذاری آماده" })).toBeVisible();
  await page.getByRole("button", { name: "علامت‌گذاری آماده" }).click();

  // Driver details are mandatory before the dispatch request is sent.
  await expect(page.getByLabel("نام راننده")).toBeVisible();
  await page.getByRole("button", { name: "ثبت ارسال", exact: true }).click();
  await expect(appAlert(page)).toContainText("نام راننده، پلاک و تلفن راننده الزامی است.");
  await page.getByLabel("نام راننده").fill("علی رضایی");
  await page.getByLabel("پلاک خودرو").fill("12-A-345");
  await page.getByLabel("تلفن راننده").fill("09121234567");
  await page.getByRole("button", { name: "ثبت ارسال", exact: true }).click();

  await expect(page.getByRole("button", { name: "جمع‌آوری شد" })).toBeVisible();
  // The retailer-only confirm endpoint must never be offered to the vendor.
  await expect(page.getByRole("button", { name: "ثبت تحویل", exact: true })).toHaveCount(0);
}

async function vendorAdvanceToArrived(page: Page): Promise<void> {
  await page.getByRole("button", { name: "جمع‌آوری شد" }).click();
  await expect(page.getByRole("button", { name: "در مسیر" })).toBeVisible();
  await page.getByRole("button", { name: "در مسیر" }).click();
  await expect(page.getByRole("button", { name: "رسید", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "رسید", exact: true }).click();
  // Delivery states are localized (DELIVERY_STATUS_LABELS): ARRIVED -> "رسیده به مقصد".
  await expect(page.getByText(/وضعیت تحویل: رسیده به مقصد/)).toBeVisible();
}

test("cross-persona delivery flow: checkout, vendor fulfillment, arrival, OTP confirmation", async ({
  browser,
}, testInfo: TestInfo) => {
  test.setTimeout(240_000);

  const retailer = retailerPhone(testInfo, PHONE_SALT);
  const vendor = vendorPhone();
  resetTenant(retailer);
  resetTenant(vendor);

  const retailerContext = await browser.newContext();
  const vendorContext = await browser.newContext();
  const rp = await retailerContext.newPage();
  const vp = await vendorContext.newPage();

  try {
    // ── Retailer: basket → checkout → order ─────────────────────────
    await seedCart(rp, [line("POL-E2E-1001", 1)]);
    await loginAsRetailer(rp, retailer);
    const orderId = await placeOrder(rp);
    expect(orderId).toMatch(/^[0-9a-f-]{36}$/);

    // Before dispatch no POD form exists and nothing has shipped yet.
    await expect(rp.getByText("ثبت‌شده", { exact: true })).toBeVisible();
    await expect(rp.getByRole("button", { name: CONFIRM_DELIVERY_BUTTON })).toHaveCount(0);

    // ── Vendor: accept → prepare → ready → dispatch ─────────────────
    await loginAsVendor(vp, vendor);
    await vendorFulfillToDispatch(vp, orderId);

    // ── Retailer: delivery exists but arrival has not happened ──────
    await rp.getByRole("button", { name: REFRESH_BUTTON }).click();
    const confirm = rp.getByRole("button", { name: CONFIRM_DELIVERY_BUTTON });
    await expect(confirm).toBeVisible();
    await expect(confirm).toBeDisabled();
    await expect(rp.getByText(/تا رسیدن بار به مقصد/)).toBeVisible();

    // ── Vendor: ASSIGNED → PICKED_UP → IN_TRANSIT → ARRIVED ─────────
    await vendorAdvanceToArrived(vp);

    // ── Retailer: recipient + outbox OTP → proof of delivery ────────
    await rp.getByRole("button", { name: REFRESH_BUTTON }).click();
    await expect(rp.getByText("رسیده به مقصد")).toBeVisible();
    await expect(rp.getByText(/تا رسیدن بار به مقصد/)).toHaveCount(0);

    await rp.getByLabel("نام شخص تحویل‌گیرنده").fill("مریم احمدی");
    await rp.getByLabel("کد ۴ رقمی OTP").fill(deliveryOtp(orderId));
    await expect(confirm).toBeEnabled();
    await confirm.click();

    await expect(rp.getByText("تأییدشده با کد OTP")).toBeVisible();
    await expect(rp.getByText("این سفارش قبلاً تحویل داده شده است.")).toBeVisible();
    await expect(confirm).toBeDisabled();
    await expect(rp.getByText("تحویل‌شده").first()).toBeVisible();
  } finally {
    await retailerContext.close();
    await vendorContext.close();
  }
});
