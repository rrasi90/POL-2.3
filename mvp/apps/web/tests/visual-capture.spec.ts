import { test, expect, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { loginAsRetailer, loginAsVendor, loginAsAdmin, loginAsField, resetTenant, retailerPhone, vendorPhone } from "./helpers";

const SCREENSHOT_DIR = path.resolve(__dirname, "../../../../.pol-design/evidence/screenshots");

test.describe("Visual Quality Assurance Suite", () => {
  test.beforeAll(() => {
    if (!fs.existsSync(SCREENSHOT_DIR)) {
      fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
    }
  });

  const publicRoutes = [
    { name: "corporate-home", route: "/" },
    { name: "about-mission", route: "/about" },
    { name: "how-it-works", route: "/how" },
    { name: "pilot-ahvaz", route: "/pilot" },
    { name: "contact-support", route: "/contact" },
    { name: "legal-terms", route: "/legal" },
    { name: "retailers-info", route: "/retailers" },
    { name: "vendors-info", route: "/vendors" },
    { name: "auth-login", route: "/auth/login" },
  ];

  for (const item of publicRoutes) {
    test(`capture public screen: ${item.name}`, async ({ page }) => {
      await page.setViewportSize({ width: 1440, height: 900 });
      await page.goto(item.route);
      await page.waitForLoadState("networkidle");

      const htmlDir = await page.getAttribute("html", "dir");
      expect(htmlDir).toBe("rtl");
      const htmlLang = await page.getAttribute("html", "lang");
      expect(htmlLang).toBe("fa");

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-desktop-light.png`),
        fullPage: true,
      });

      await page.setViewportSize({ width: 390, height: 844 });
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-mobile-light.png`),
        fullPage: true,
      });
    });
  }

  test("capture authenticated retailer golden surfaces", async ({ page }, testInfo) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    const phone = retailerPhone(testInfo, 10);
    resetTenant(phone);
    await loginAsRetailer(page, phone);

    const retailerRoutes = [
      { name: "retailer-dashboard", route: "/retailer" },
      { name: "retailer-catalog", route: "/retailer/catalog" },
      { name: "retailer-basket", route: "/retailer/basket" },
      { name: "retailer-orders", route: "/retailer/orders" },
      { name: "retailer-finance", route: "/retailer/finance" },
      { name: "retailer-support", route: "/retailer/support" },
      { name: "retailer-vendors", route: "/retailer/vendors" },
    ];

    for (const item of retailerRoutes) {
      if (item.route !== "/retailer") {
        await page.locator(`a[href="${item.route}"]`).first().click();
        await page.waitForURL(`**${item.route}**`);
      }
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(400);

      await page.setViewportSize({ width: 1440, height: 900 });
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-desktop.png`),
        fullPage: true,
      });

      await page.setViewportSize({ width: 390, height: 844 });
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-mobile.png`),
        fullPage: true,
      });
      await page.setViewportSize({ width: 1440, height: 900 });
    }
  });

  test("capture authenticated vendor golden surfaces", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    const phone = vendorPhone();
    resetTenant(phone);
    await loginAsVendor(page, phone);

    const vendorNavRail = [
      { name: "vendor-dashboard", route: "/vendor" },
      { name: "vendor-orders", route: "/vendor/orders" },
      { name: "vendor-catalog", route: "/vendor/catalog" },
      { name: "vendor-inventory", route: "/vendor/inventory" },
      { name: "vendor-inventory-daily", route: "/vendor/inventory/daily" },
      { name: "vendor-settlements", route: "/vendor/settlements" },
    ];

    for (const item of vendorNavRail) {
      if (item.route !== "/vendor") {
        await page.locator(`a[href="${item.route}"]`).first().click();
        await page.waitForURL(`**${item.route}**`);
      }
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(400);

      await page.setViewportSize({ width: 1440, height: 900 });
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-desktop.png`),
        fullPage: true,
      });

      await page.setViewportSize({ width: 390, height: 844 });
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-mobile.png`),
        fullPage: true,
      });
      await page.setViewportSize({ width: 1440, height: 900 });
    }

    // Secondary vendor pages from /vendor dashboard navLinks
    const vendorSubPages = [
      { name: "vendor-customers", route: "/vendor/customers" },
      { name: "vendor-storefront", route: "/vendor/storefront" },
      { name: "vendor-staff", route: "/vendor/staff" },
      { name: "vendor-referrals", route: "/vendor/referrals" },
      { name: "vendor-finance", route: "/vendor/finance" },
    ];

    for (const item of vendorSubPages) {
      await page.locator('a[href="/vendor"]').first().click();
      await page.waitForURL("**/vendor");
      await page.waitForLoadState("networkidle");

      await page.locator(`a[href="${item.route}"]`).first().click();
      await page.waitForURL(`**${item.route}**`);
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(400);

      await page.setViewportSize({ width: 1440, height: 900 });
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-desktop.png`),
        fullPage: true,
      });

      await page.setViewportSize({ width: 390, height: 844 });
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-mobile.png`),
        fullPage: true,
      });
      await page.setViewportSize({ width: 1440, height: 900 });
    }
  });

  test("capture operations and admin triage surfaces", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await loginAsAdmin(page);

    const opsNavRail = [
      { name: "ops-dashboard", route: "/ops" },
      { name: "ops-queues", route: "/ops/queues" },
      { name: "ops-support", route: "/ops/support" },
      { name: "ops-reconciliation", route: "/ops/reconciliation" },
      { name: "ops-rma", route: "/ops/rma" },
      { name: "ops-admin", route: "/ops/admin" },
      { name: "admin-root", route: "/admin" },
    ];

    for (const item of opsNavRail) {
      if (item.route !== "/ops") {
        await page.locator(`a[href="${item.route}"]`).first().click();
        await page.waitForURL(`**${item.route}**`);
      }
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(400);

      await page.setViewportSize({ width: 1440, height: 900 });
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-desktop.png`),
        fullPage: true,
      });

      await page.setViewportSize({ width: 390, height: 844 });
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-mobile.png`),
        fullPage: true,
      });
      await page.setViewportSize({ width: 1440, height: 900 });
    }

    // Secondary ops pages from /ops overview navLinks
    const opsSubPages = [
      { name: "ops-catalog-candidates", route: "/ops/catalog-candidates" },
      { name: "ops-permissions", route: "/ops/permissions" },
      { name: "ops-analytics", route: "/ops/analytics" },
      { name: "ops-risk", route: "/ops/risk" },
    ];

    for (const item of opsSubPages) {
      await page.locator('a[href="/ops"]').first().click();
      await page.waitForURL("**/ops");
      await page.waitForLoadState("networkidle");

      await page.locator(`a[href="${item.route}"]`).first().click();
      await page.waitForURL(`**${item.route}**`);
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(400);

      await page.setViewportSize({ width: 1440, height: 900 });
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-desktop.png`),
        fullPage: true,
      });

      await page.setViewportSize({ width: 390, height: 844 });
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-mobile.png`),
        fullPage: true,
      });
      await page.setViewportSize({ width: 1440, height: 900 });
    }

    // Admin subpages from /admin
    const adminSubPages = [
      { name: "admin-users", route: "/admin/users" },
      { name: "admin-orgs", route: "/admin/orgs" },
    ];

    for (const item of adminSubPages) {
      await page.locator('a[href="/admin"]').first().click();
      await page.waitForURL("**/admin");
      await page.waitForLoadState("networkidle");

      await page.locator(`a[href="${item.route}"]`).first().click();
      await page.waitForURL(`**${item.route}**`);
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(400);

      await page.setViewportSize({ width: 1440, height: 900 });
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-desktop.png`),
        fullPage: true,
      });

      await page.setViewportSize({ width: 390, height: 844 });
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-mobile.png`),
        fullPage: true,
      });
      await page.setViewportSize({ width: 1440, height: 900 });
    }
  });

  test("capture field activator golden surfaces", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await loginAsField(page);

    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(400);

    await page.setViewportSize({ width: 1440, height: 900 });
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "field-dashboard-desktop.png"),
      fullPage: true,
    });

    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "field-dashboard-mobile.png"),
      fullPage: true,
    });
  });
});
