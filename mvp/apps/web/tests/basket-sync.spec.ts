import { expect, test, type Page, type TestInfo } from "@playwright/test";
import {
  appAlert,
  errorEnvelope,
  line,
  loginAsRetailer,
  openBasket,
  readBasketState,
  recordBasketCalls,
  resetTenant,
  retailerPhone,
  seedCart,
  serverBaskets,
  serverBasketCounts,
  type BasketCalls,
  type BasketLineInput,
} from "./helpers";

const SYNC_BUTTON = "ثبت سبد در سرور";
const REVIEW_BUTTON = "بررسی تخصیص و ادامه تسویه";
const RETRY_BUTTON = "تلاش مجدد";
const NO_OPEN_BASKET = "No OPEN basket exists for the active retailer organization.";
const PHONE_SALT = 12;

async function startBasket(
  page: Page,
  testInfo: TestInfo,
  lines: BasketLineInput[],
): Promise<{ phone: string; calls: BasketCalls }> {
  const phone = retailerPhone(testInfo, PHONE_SALT);
  resetTenant(phone);
  await seedCart(page, lines);
  const calls = recordBasketCalls(page);
  await loginAsRetailer(page, phone);
  await openBasket(page);
  return { phone, calls };
}

test("syncs a basket to the server exactly once and writes every item", async ({
  page,
}, testInfo) => {
  const { phone, calls } = await startBasket(page, testInfo, [
    line("POL-E2E-1001", 2),
    line("POL-E2E-1002", 1),
  ]);

  await page.getByRole("button", { name: SYNC_BUTTON }).click();

  await expect(page.getByRole("status").first()).toContainText("در سرور ثبت شد");
  expect(calls.creates).toHaveLength(1);
  expect(calls.itemWrites).toHaveLength(2);

  const state = await readBasketState(page);
  expect(state.serverBasketId).toBeTruthy();

  const baskets = serverBaskets(phone);
  expect(baskets).toHaveLength(1);
  expect(baskets[0].status).toBe("OPEN");
  expect(baskets[0].id).toBe(state.serverBasketId);
  expect(baskets[0].items).toHaveLength(2);
  const quantities = baskets[0].items
    .map((item) => item.requested_quantity)
    .sort((a, b) => a - b);
  expect(quantities).toEqual([1, 2]);
});

test("repeated review clicks never create a second basket", async ({ page }, testInfo) => {
  const { phone, calls } = await startBasket(page, testInfo, [line("POL-E2E-1003", 3)]);

  await page.evaluate(() => {
    const review = [...document.querySelectorAll("button")].find((button) =>
      button.textContent?.includes("بررسی تخصیص"),
    );
    if (!review) throw new Error("review button not found");
    review.click();
    review.click();
  });

  await page.waitForURL("**/retailer/checkout");
  expect(calls.creates).toHaveLength(1);
  expect(calls.itemWrites).toHaveLength(1);

  const counts = serverBasketCounts(phone);
  expect(counts.total).toBe(1);
  expect(counts.open).toBe(1);
});

test("recovers from a failed sync and the retry reaches checkout", async ({
  page,
}, testInfo) => {
  const { phone, calls } = await startBasket(page, testInfo, [line("POL-E2E-1001", 1)]);
  await page.route("**/api/v1/baskets/current", (route) =>
    route.fulfill({
      status: 500,
      contentType: "application/json",
      json: errorEnvelope("INTERNAL_ERROR", "Internal server error."),
    }),
  );

  await page.getByRole("button", { name: REVIEW_BUTTON }).click();
  await expect(appAlert(page)).toBeVisible();
  await expect(page).toHaveURL(/\/retailer\/basket/);
  expect(calls.creates).toHaveLength(0);
  expect(serverBasketCounts(phone).total).toBe(0);

  await page.unroute("**/api/v1/baskets/current");
  await page.getByRole("button", { name: RETRY_BUTTON }).click();

  await page.waitForURL("**/retailer/checkout");
  expect(calls.creates).toHaveLength(1);
  expect(serverBasketCounts(phone).open).toBe(1);
});

test("an empty basket never reaches checkout and writes nothing", async ({
  page,
}, testInfo) => {
  const { phone, calls } = await startBasket(page, testInfo, []);

  await expect(page.getByRole("heading", { name: "سبد خرید شما خالی است" })).toBeVisible();
  await expect(page).toHaveURL(/\/retailer\/basket/);
  expect(calls.creates).toHaveLength(0);
  expect(serverBasketCounts(phone).total).toBe(0);

  await page.getByRole("button", { name: "مشاهده و جستجوی کاتالوگ" }).click();
  await page.waitForURL("**/retailer/catalog");
  expect(calls.creates).toHaveLength(0);
});

test("editing the cart after a sync invalidates the stale server basket", async ({
  page,
}, testInfo) => {
  const { phone, calls } = await startBasket(page, testInfo, [
    line("POL-E2E-1001", 2),
    line("POL-E2E-1002", 1),
  ]);

  await page.getByRole("button", { name: SYNC_BUTTON }).click();
  await expect(page.getByRole("status").first()).toContainText("در سرور ثبت شد");
  const first = serverBaskets(phone);
  expect(first).toHaveLength(1);

  await page.getByRole("button", { name: "افزایش تعداد" }).first().click();
  expect((await readBasketState(page)).serverBasketId).toBeNull();

  await page.getByRole("button", { name: SYNC_BUTTON }).click();
  await expect(page.getByRole("status").first()).toContainText("در سرور ثبت شد");
  expect(calls.creates).toHaveLength(2);

  await page.getByRole("button", { name: /^حذف/ }).nth(1).click();
  await page.getByRole("button", { name: SYNC_BUTTON }).click();
  await expect(page.getByRole("status").first()).toContainText("در سرور ثبت شد");

  expect(calls.creates).toHaveLength(3);
  const baskets = serverBaskets(phone);
  expect(baskets).toHaveLength(3);

  const state = await readBasketState(page);
  const current = baskets[2];
  expect(state.serverBasketId).toBe(current.id);
  expect(state.serverBasketId).not.toBe(baskets[0].id);
  expect(state.serverBasketId).not.toBe(baskets[1].id);
  expect(current.items).toHaveLength(1);
  expect(current.items[0].product_id).toBe(line("POL-E2E-1001", 1).product_id);
  expect(current.items[0].requested_quantity).toBe(3);
});

test("a basket that disappeared on the server is recreated without an error", async ({
  page,
}, testInfo) => {
  const { phone, calls } = await startBasket(page, testInfo, [line("POL-E2E-1001", 1)]);

  await page.getByRole("button", { name: SYNC_BUTTON }).click();
  await expect(page.getByRole("status").first()).toContainText("در سرور ثبت شد", { timeout: 30_000 });
  expect(serverBasketCounts(phone).total).toBe(1);

  await page.route("**/api/v1/baskets/current", (route) =>
    route.fulfill({
      status: 404,
      contentType: "application/json",
      json: errorEnvelope("NOT_FOUND", NO_OPEN_BASKET),
    }),
  );

  await page.getByRole("button", { name: SYNC_BUTTON }).click();
  await expect(page.getByRole("status").first()).toContainText("در سرور ثبت شد");
  await expect(appAlert(page)).toHaveCount(0);

  expect(calls.creates).toHaveLength(2);
  const baskets = serverBaskets(phone);
  expect(baskets).toHaveLength(2);
  const state = await readBasketState(page);
  expect(state.serverBasketId).toBe(baskets[1].id);
  expect(state.serverBasketId).not.toBe(baskets[0].id);
});

test("an auth failure during sync creates no replacement basket", async ({
  page,
}, testInfo) => {
  const { phone, calls } = await startBasket(page, testInfo, [line("POL-E2E-1001", 1)]);
  await page.route("**/api/v1/baskets**", (route) =>
    route.fulfill({
      status: 401,
      contentType: "application/json",
      json: errorEnvelope("INVALID_ACCESS_TOKEN", "Invalid or expired access token."),
    }),
  );

  await page.getByRole("button", { name: SYNC_BUTTON }).click();

  await page.waitForURL(/\/auth\/login/);
  await expect(appAlert(page)).toContainText("نشست شما منقضی شده است");
  expect(calls.creates).toHaveLength(0);
  expect(serverBasketCounts(phone).total).toBe(0);
});

test("a network failure during sync creates no replacement basket", async ({
  page,
}, testInfo) => {
  const { phone, calls } = await startBasket(page, testInfo, [line("POL-E2E-1001", 1)]);
  await page.route("**/api/v1/baskets**", (route) => route.abort());

  await page.getByRole("button", { name: SYNC_BUTTON }).click();

  await expect(appAlert(page)).toBeVisible();
  await expect(page).toHaveURL(/\/retailer\/basket/);
  expect(calls.creates).toHaveLength(0);
  expect(serverBasketCounts(phone).total).toBe(0);
});

test("a server failure during sync creates no replacement basket", async ({
  page,
}, testInfo) => {
  const { phone, calls } = await startBasket(page, testInfo, [line("POL-E2E-1001", 1)]);
  await page.route("**/api/v1/baskets/current", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      json: errorEnvelope("SERVICE_UNAVAILABLE", "Service unavailable."),
    }),
  );

  await page.getByRole("button", { name: SYNC_BUTTON }).click();

  await expect(appAlert(page)).toBeVisible();
  await expect(page).toHaveURL(/\/retailer\/basket/);
  expect(calls.creates).toHaveLength(0);
  expect(serverBasketCounts(phone).total).toBe(0);
});

test("a failed item write keeps the user out of checkout", async ({ page }, testInfo) => {
  const { phone, calls } = await startBasket(page, testInfo, [
    line("POL-E2E-1001", 2),
    line("POL-E2E-1002", 1),
  ]);
  await page.route("**/api/v1/baskets/*/items", (route) =>
    route.fulfill({
      status: 500,
      contentType: "application/json",
      json: errorEnvelope("INTERNAL_ERROR", "Item write failed."),
    }),
  );

  await page.getByRole("button", { name: REVIEW_BUTTON }).click();

  await expect(appAlert(page)).toBeVisible();
  await expect(page).toHaveURL(/\/retailer\/basket/);
  expect(calls.creates).toHaveLength(1);

  const baskets = serverBaskets(phone);
  expect(baskets).toHaveLength(1);
  expect(baskets[0].items).toHaveLength(0);
});

test("a lost item response is reconciled against the server on retry", async ({
  page,
}, testInfo) => {
  const { phone, calls } = await startBasket(page, testInfo, [
    line("POL-E2E-1001", 2),
    line("POL-E2E-1002", 1),
  ]);

  let handled = 0;
  await page.route("**/api/v1/baskets/*/items", async (route) => {
    const response = await route.fetch();
    handled += 1;
    if (handled >= 2) {
      await route.abort();
    } else {
      await route.fulfill({ response });
    }
  });

  await page.getByRole("button", { name: REVIEW_BUTTON }).click();
  await expect(appAlert(page)).toBeVisible();
  await expect(page).toHaveURL(/\/retailer\/basket/);

  await page.unroute("**/api/v1/baskets/*/items");
  await page.getByRole("button", { name: RETRY_BUTTON }).click();

  await page.waitForURL("**/retailer/checkout");
  expect(calls.creates).toHaveLength(1);
  expect(calls.currentReads).toBeGreaterThanOrEqual(2);

  const baskets = serverBaskets(phone);
  const open = baskets.filter((basket) => basket.status === "OPEN");
  expect(open).toHaveLength(1);
  expect(open[0].items).toHaveLength(2);

  const state = await readBasketState(page);
  expect(state.serverBasketId).toBe(open[0].id);
});

test("sync then checkout renders the allocation preview from the API", async ({
  page,
}, testInfo) => {
  const { phone, calls } = await startBasket(page, testInfo, [
    line("POL-E2E-1001", 1),
    line("POL-E2E-1003", 2),
  ]);

  await page.getByRole("button", { name: REVIEW_BUTTON }).click();

  await page.waitForURL("**/retailer/checkout");
  await expect(
    page.getByRole("heading", { name: "بررسی تخصیص و تسویه حساب" }),
  ).toBeVisible();
  await expect(page.getByText("بنکداری آزمایشی پل")).toBeVisible();

  expect(calls.creates).toHaveLength(1);
  expect(calls.itemWrites).toHaveLength(2);
  const counts = serverBasketCounts(phone);
  expect(counts.total).toBe(1);
  expect(counts.open).toBe(1);
});
