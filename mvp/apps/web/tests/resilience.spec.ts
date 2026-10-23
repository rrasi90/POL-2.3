import { expect, test } from "@playwright/test";
import { getLastCorrelationId } from "@pol/api-client";
import { appAlert, localNumber, retailerPhone } from "./helpers";

test.describe("resilience and error surfaces", () => {
  test("api client exposes the correlation id used by error surfaces", () => {
    const value = getLastCorrelationId();
    expect(value === null || typeof value === "string").toBe(true);
  });

  test("unknown route renders the branded Persian not-found page", async ({ page }) => {
    const response = await page.goto("/auth/definitely-not-a-pol-route");
    expect(response?.status()).toBe(404);
    await expect(page.getByRole("heading", { name: "این صفحه پیدا نشد" })).toBeVisible();
    await expect(page.getByRole("link", { name: "بازگشت به صفحهٔ اصلی" })).toBeVisible();
  });

  test("a server 500 during OTP request shows an alert and never a fake success", async ({
    page,
  }, testInfo) => {
    await page.route("**/api/v1/auth/request-otp", (route) =>
      route.fulfill({
        status: 500,
        contentType: "text/html",
        body: "<html><body>internal error</body></html>",
      }),
    );
    await page.goto("/auth/login");
    await page.getByLabel(/شماره تلفن همراه/).fill(localNumber(retailerPhone(testInfo)));
    await page.getByRole("button", { name: "دریافت کد یکبار مصرف" }).click();

    await expect(appAlert(page)).toBeVisible();
    await expect(page.locator('input[maxlength="4"]')).toHaveCount(0);
    const bodyText = await page.locator("body").innerText();
    expect(bodyText.trim().length).toBeGreaterThan(20);
  });

  test("a 200 response without the success envelope is rejected, not treated as data", async ({
    page,
  }, testInfo) => {
    await page.route("**/api/v1/auth/request-otp", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ foo: "bar" }),
      }),
    );
    await page.goto("/auth/login");
    await page.getByLabel(/شماره تلفن همراه/).fill(localNumber(retailerPhone(testInfo)));
    await page.getByRole("button", { name: "دریافت کد یکبار مصرف" }).click();

    await expect(appAlert(page)).toBeVisible();
    await expect(appAlert(page)).toContainText(/success/i);
    await expect(page.locator('input[maxlength="4"]')).toHaveCount(0);
  });

  test("an unparsable JSON response surfaces an error instead of a crash", async ({
    page,
  }, testInfo) => {
    await page.route("**/api/v1/auth/request-otp", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: '{"success": tr',
      }),
    );
    await page.goto("/auth/login");
    await page.getByLabel(/شماره تلفن همراه/).fill(localNumber(retailerPhone(testInfo)));
    await page.getByRole("button", { name: "دریافت کد یکبار مصرف" }).click();

    await expect(appAlert(page)).toBeVisible();
    await expect(page.locator('input[maxlength="4"]')).toHaveCount(0);
  });

  test("a dropped connection surfaces a network error and keeps the form usable", async ({
    page,
  }, testInfo) => {
    await page.route("**/api/v1/auth/request-otp", (route) => route.abort("connectionreset"));
    await page.goto("/auth/login");
    const input = page.getByLabel(/شماره تلفن همراه/);
    await input.fill(localNumber(retailerPhone(testInfo)));
    await page.getByRole("button", { name: "دریافت کد یکبار مصرف" }).click();

    await expect(appAlert(page)).toBeVisible();
    await expect(input).toBeEditable();
    await expect(page.locator('input[maxlength="4"]')).toHaveCount(0);
  });
});
