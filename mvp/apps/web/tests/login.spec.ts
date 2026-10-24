import { expect, test } from "@playwright/test";
import { toE164 } from "../src/lib/auth/phone";
import { appAlert, localNumber, loginAsRetailer, resetTenant, retailerPhone } from "./helpers";

test.describe("login phone normalization", () => {
  test("toE164 accepts local, national and international digit forms", () => {
    expect(toE164("09123456789")).toBe("+989123456789");
    expect(toE164("9123456789")).toBe("+989123456789");
    expect(toE164("989123456789")).toBe("+989123456789");
    expect(toE164("+98 912 345 6789")).toBe("+989123456789");
    expect(toE164("12345")).toBeNull();
    expect(toE164("")).toBeNull();
  });

  test("request-otp carries the E.164 number the API contract requires", async ({
    page,
  }, testInfo) => {
    const phone = retailerPhone(testInfo);
    resetTenant(phone);
    const payloads: unknown[] = [];
    page.on("request", (request) => {
      if (request.url().includes("/api/v1/auth/request-otp")) {
        payloads.push(request.postDataJSON());
      }
    });

    await page.goto("/auth/login");
    await page.getByLabel(/شماره تلفن همراه/).fill(localNumber(phone));
    await page.getByRole("button", { name: "دریافت کد یکبار مصرف" }).click();
    await expect(page.locator('input[maxlength="6"]')).toBeVisible();

    expect(payloads).toEqual([{ mobile_number: phone }]);

    await page.locator('input[maxlength="6"]').fill("123456");
    await page.getByRole("button", { name: "تأیید و ورود به سامانه" }).click();
    await page.waitForURL(/\/retailer$/);
  });

  test("too-short number is rejected instead of sending an invalid payload", async ({
    page,
  }, testInfo) => {
    const phone = retailerPhone(testInfo);
    resetTenant(phone);
    await page.goto("/auth/login");
    await page.getByLabel(/شماره تلفن همراه/).fill("123");
    await page.getByRole("button", { name: "دریافت کد یکبار مصرف" }).click();

    await expect(appAlert(page)).toBeVisible();
    await expect(page.locator('input[maxlength="6"]')).toHaveCount(0);
  });

  test("complete OTP login lands on the retailer workspace", async ({ page }, testInfo) => {
    const phone = retailerPhone(testInfo);
    resetTenant(phone);
    await loginAsRetailer(page, phone);
    await expect(page).toHaveURL(/\/retailer$/);
  });
});
