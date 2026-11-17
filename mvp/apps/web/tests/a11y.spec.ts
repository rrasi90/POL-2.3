import { test, expect } from "@playwright/test";
import { loginAsRetailer, loginAsVendor, resetTenant, retailerPhone, vendorPhone } from "./helpers";

test.describe("Accessibility snapshot guards", () => {
  test("retailer dashboard has basic a11y structure", async ({ page }, testInfo) => {
    const phone = retailerPhone(testInfo, 99);
    resetTenant(phone);
    await loginAsRetailer(page, phone);
    await page.goto("/retailer");
    await page.waitForLoadState("networkidle");

    const mainLandmark = page.getByRole("main");
    await expect(mainLandmark.first()).toBeVisible();

    const heading = page.getByRole("heading");
    await expect(heading.first()).toBeVisible();

    const buttons = await page.getByRole("button").all();
    for (const btn of buttons) {
      const name = await btn.innerText().catch(() => "");
      const ariaLabel = await btn.getAttribute("aria-label");
      const title = await btn.getAttribute("title");
      const hasName = Boolean((name && name.trim().length > 0) || ariaLabel || title);
      expect(hasName).toBeTruthy();
    }
  });

  test("vendor dashboard has basic a11y structure", async ({ page }, testInfo) => {
    const phone = vendorPhone(testInfo, 99);
    resetTenant(phone);
    await loginAsVendor(page, phone);
    await page.goto("/vendor");
    await page.waitForLoadState("networkidle");

    const mainLandmark = page.getByRole("main");
    await expect(mainLandmark.first()).toBeVisible();

    const heading = page.getByRole("heading");
    await expect(heading.first()).toBeVisible();

    const buttons = await page.getByRole("button").all();
    for (const btn of buttons) {
      const name = await btn.innerText().catch(() => "");
      const ariaLabel = await btn.getAttribute("aria-label");
      const title = await btn.getAttribute("title");
      const hasName = Boolean((name && name.trim().length > 0) || ariaLabel || title);
      expect(hasName).toBeTruthy();
    }
  });
});
