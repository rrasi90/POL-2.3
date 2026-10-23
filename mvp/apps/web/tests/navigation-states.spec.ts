import { expect, test, type Page } from "@playwright/test";
import {
  appAlert,
  errorEnvelope,
  localNumber,
  loginAsRetailer,
  resetTenant,
  retailerPhone,
  vendorPhone,
} from "./helpers";

/** Salt bands stay disjoint from login (0), basket-sync (12) and delivery (20). */
const PHONE_SALT = 30;
const EMPTY_ORDERS_TITLE = "سفارشی با این مشخصات یافت نشد";
const ORDERS_ERROR_TITLE = "دریافت سفارش‌ها ناموفق بود";

async function loginThroughUi(page: Page, phone: string): Promise<void> {
  await page.getByLabel(/شماره تلفن همراه/).fill(localNumber(phone));
  await page.getByRole("button", { name: "دریافت کد یکبار مصرف" }).click();
  await page.locator('input[maxlength="4"]').fill("1234");
  await page.getByRole("button", { name: "تأیید و ورود به سامانه" }).click();
}

test.describe("role routing and deep links", () => {
  test("vendor OTP login lands on the vendor workspace", async ({ page }) => {
    await page.goto("/auth/login");
    await loginThroughUi(page, vendorPhone());
    await page.waitForURL(/\/vendor$/);
    await expect(page.getByRole("link", { name: "سفارش‌ها", exact: true }).first()).toBeVisible();
  });

  test("unauthenticated deep link is preserved and restored after OTP login", async ({
    page,
  }, testInfo) => {
    const phone = retailerPhone(testInfo, PHONE_SALT);
    resetTenant(phone);

    await page.goto("/retailer/orders");
    await page.waitForURL(/\/auth\/login\?next=/);
    expect(new URL(page.url()).searchParams.get("next")).toBe("/retailer/orders");

    await loginThroughUi(page, phone);
    await page.waitForURL("**/retailer/orders");
    await expect(page.getByRole("heading", { name: "تاریخچه سفارش‌ها" })).toBeVisible();
  });

  test("a deep link the role may not open falls back to the role home", async ({ page }, testInfo) => {
    const phone = retailerPhone(testInfo, PHONE_SALT + 1);
    resetTenant(phone);

    await page.goto("/auth/login?next=/admin/users");
    await loginThroughUi(page, phone);
    await page.waitForURL(/\/retailer$/);
  });

  test("a retailer cannot open the vendor workspace", async ({ page }, testInfo) => {
    const phone = retailerPhone(testInfo, PHONE_SALT + 2);
    resetTenant(phone);
    await loginAsRetailer(page, phone);

    await page.goto("/vendor/orders");
    await page.waitForURL(/\/(retailer|vendor)(\/orders)?$/);
    expect(new URL(page.url()).pathname).toMatch(/^\/retailer/);
  });

  test("refresh keeps the session and browser back restores the previous screen", async ({
    page,
  }, testInfo) => {
    const phone = retailerPhone(testInfo, PHONE_SALT + 3);
    resetTenant(phone);
    await loginAsRetailer(page, phone);

    await page.getByRole("link", { name: "سفارش‌ها", exact: true }).click();
    await page.waitForURL("**/retailer/orders");
    await page.reload();
    await expect(page.getByRole("heading", { name: "تاریخچه سفارش‌ها" })).toBeVisible();
    expect(new URL(page.url()).pathname).toBe("/retailer/orders");

    await page.goBack();
    await page.waitForURL(/\/retailer$/);
  });

  test("an expired session with a dead refresh token returns to login", async ({
    page,
  }, testInfo) => {
    const phone = retailerPhone(testInfo, PHONE_SALT + 4);
    resetTenant(phone);
    await loginAsRetailer(page, phone);

    await page.route("**/api/v1/auth/refresh", (route) =>
      route.fulfill({ status: 401, json: errorEnvelope("INVALID_REFRESH_TOKEN", "expired") }),
    );
    await page.route("**/api/v1/orders?**", (route) =>
      route.fulfill({ status: 401, json: errorEnvelope("INVALID_ACCESS_TOKEN", "expired") }),
    );

    await page.goto("/retailer/orders");
    await page.waitForURL(/\/auth\/login/);
  });
});

test.describe("list states are explicit", () => {
  test("empty list shows an actionable empty state", async ({ page }, testInfo) => {
    const phone = retailerPhone(testInfo, PHONE_SALT + 5);
    resetTenant(phone);
    await loginAsRetailer(page, phone);

    await page.route("**/api/v1/orders?**", (route) =>
      route.fulfill({
        status: 200,
        json: {
          success: true,
          data: { orders: [], limit: 20, offset: 0, total: 0 },
        },
      }),
    );
    await page.goto("/retailer/orders");
    await expect(page.getByText(EMPTY_ORDERS_TITLE)).toBeVisible();
    await expect(page.getByRole("button", { name: "مشاهده کاتالوگ کالاها" })).toBeVisible();
  });

  test("loading state announces itself before the data arrives", async ({ page }, testInfo) => {
    const phone = retailerPhone(testInfo, PHONE_SALT + 6);
    resetTenant(phone);
    await loginAsRetailer(page, phone);

    await page.route("**/api/v1/orders?**", async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 1_500));
      await route.fulfill({
        status: 200,
        json: { success: true, data: { orders: [], limit: 20, offset: 0, total: 0 } },
      });
    });

    await page.goto("/retailer/orders");
    await expect(page.locator('[aria-busy="true"]')).toBeVisible();
    await expect(page.getByText(EMPTY_ORDERS_TITLE)).toBeVisible();
  });

  test("a failed list shows the error state and retry recovers", async ({ page }, testInfo) => {
    const phone = retailerPhone(testInfo, PHONE_SALT + 7);
    resetTenant(phone);
    await loginAsRetailer(page, phone);

    await page.route("**/api/v1/orders?**", (route) =>
      route.fulfill({
        status: 500,
        json: errorEnvelope("INTERNAL_ERROR", "temporary failure"),
      }),
    );
    await page.goto("/retailer/orders");
    await expect(page.getByText(ORDERS_ERROR_TITLE)).toBeVisible();

    await page.unroute("**/api/v1/orders?**");
    await page.getByRole("button", { name: /تلاش مجدد|دوباره/ }).click();
    await expect(page.getByText(ORDERS_ERROR_TITLE)).toBeHidden();
  });

  test("an API failure keeps the alert message readable", async ({ page }, testInfo) => {
    const phone = retailerPhone(testInfo, PHONE_SALT + 8);
    resetTenant(phone);
    await page.goto("/auth/login");
    await page.route("**/api/v1/auth/request-otp", (route) =>
      route.fulfill({
        status: 429,
        json: errorEnvelope("OTP_RATE_LIMITED", "Rate limit exceeded. Max 3 OTP requests per 5 minutes."),
      }),
    );
    await page.getByLabel(/شماره تلفن همراه/).fill(localNumber(phone));
    await page.getByRole("button", { name: "دریافت کد یکبار مصرف" }).click();
    await expect(appAlert(page)).toContainText("Max 3 OTP requests");
  });
});
