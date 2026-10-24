import { test, expect } from "@playwright/test";
import { loginAsRetailer, loginAsVendor, resetTenant, retailerPhone, vendorPhone } from "./helpers";

test.describe("Accessibility snapshot guards", () => {
  test("retailer dashboard has basic a11y structure", async ({ page }, testInfo) => {
    const phone = retailerPhone(testInfo, 99);
    resetTenant(phone);
    await loginAsRetailer(page, phone);
    await page.goto("/retailer");
    await page.waitForLoadState("networkidle");

    const snapshot = await page.accessibility.snapshot();
    const tree = snapshot.tree.join("\n");

    // At least one main landmark
    expect(tree).toContain('role="main"');

    // At least one heading (h1-h6)
    expect(tree).toMatch(/<h[1-6]/);

    // No button without accessible name
    const buttons = tree.match(/<button[^>]*>/g) || [];
    for (const btn of buttons) {
      // a button must have aria-label, title, or inner text that is not whitespace-only
      const hasName = /aria-label|title|>[^<]*<!--.*--<!-->|>[^<>\s]/.test(btn);
      expect(hasName).toBeTruthy(`button missing accessible name: ${btn}`);
    }
  });

  test("vendor dashboard has basic a11y structure", async ({ page }, testInfo) => {
    const phone = vendorPhone(testInfo, 99);
    resetTenant(phone);
    await loginAsVendor(page, phone);
    await page.goto("/vendor");
    await page.waitForLoadState("networkidle");

    const snapshot = await page.accessibility.snapshot();
    const tree = snapshot.tree.join("\n");

    expect(tree).toContain('role="main"');
    expect(tree).toMatch(/<h[1-6]/);

    const buttons = tree.match(/<button[^>]*>/g) || [];
    for (const btn of buttons) {
      const hasName = /aria-label|title|>[^<]*<!--.*--<!-->|>[^<>\s]/.test(btn);
      expect(hasName).toBeTruthy(`button missing accessible name: ${btn}`);
    }
  });
});