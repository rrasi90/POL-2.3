import { test, expect, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { loginAsRetailer, loginAsVendor, loginAsAdmin, loginAsField, resetTenant, retailerPhone, vendorPhone } from "./helpers";

const SCREENSHOT_DIR = path.resolve(__dirname, "../../../../.pol-design/evidence/screenshots");
const pageErrors = new WeakMap<Page, string[]>();

async function assertResponsiveDocument(page: Page, expectedPath: string): Promise<void> {
  const documentContract = await page.evaluate(() => {
    if (!document.getElementById("pol-visual-capture-overrides")) {
      const style = document.createElement("style");
      style.id = "pol-visual-capture-overrides";
      style.textContent = "nextjs-portal { display: none !important; }";
      document.head.appendChild(style);
    }
    return {
      language: document.documentElement.lang,
      direction: document.documentElement.dir,
      viewportWidth: window.innerWidth,
      documentWidth: document.documentElement.scrollWidth,
      bodyWidth: document.body.scrollWidth,
      bodyTextLength: document.body.innerText.trim().length,
      path: window.location.pathname,
    };
  });

  expect(documentContract.language, "document language should be Persian").toBe("fa");
  expect(documentContract.direction, "document direction should be RTL").toBe("rtl");
  expect(documentContract.path, "the captured route should match the expected route").toBe(expectedPath);
  expect(documentContract.viewportWidth).toBeGreaterThan(0);
  expect(documentContract.bodyTextLength, `blank page captured at ${expectedPath}`).toBeGreaterThan(0);
  expect(
    documentContract.documentWidth,
    `document horizontal overflow on ${expectedPath}: ${documentContract.documentWidth}px > ${documentContract.viewportWidth}px`,
  ).toBeLessThanOrEqual(documentContract.viewportWidth);
  expect(
    documentContract.bodyWidth,
    `body horizontal overflow on ${expectedPath}: ${documentContract.bodyWidth}px > ${documentContract.viewportWidth}px`,
  ).toBeLessThanOrEqual(documentContract.viewportWidth);
}

async function assertCanonicalUserFacingCopy(page: Page, expectedPath: string): Promise<void> {
  const visibleText = await page.locator("body").innerText();
  for (const internalTerm of [
    "Precision Commerce",
    "FMCG",
    "B2B",
    "OTIF",
    "RBAC",
    "MVP Constraints",
    "G-007",
    "O-10B",
  ]) {
    expect(visibleText, `${expectedPath} contains internal/English term: ${internalTerm}`).not.toContain(internalTerm);
  }

  if (expectedPath === "/contact") {
    expect(visibleText).toMatch(/این فرم هنوز به ثبت سروری متصل نیست|ارسال آنلاین این فرم هنوز فعال نیست/);
    expect(visibleText).not.toContain("پیام شما با موفقیت ثبت شد");
    expect(visibleText).not.toContain("C-07");
  }

  if (expectedPath.startsWith("/admin")) {
    expect(visibleText).not.toContain("G-007");
    expect(visibleText).not.toContain("O-10B");
  }

  if (expectedPath === "/notifications/preferences") {
    expect(visibleText).toContain("اعلان برنامه");
    expect(visibleText).toContain("پیامک");
    expect(visibleText).not.toContain("پوش");
  }
}

async function captureAuthenticatedRoute(
  page: Page,
  route: string,
  name: string,
): Promise<void> {
  await page.goto(route);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(300);

  await page.setViewportSize({ width: 1440, height: 900 });
  await assertResponsiveDocument(page, route);
  await assertCanonicalUserFacingCopy(page, route);
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, `${name}-desktop.png`),
    fullPage: true,
  });

  await page.setViewportSize({ width: 390, height: 844 });
  await assertResponsiveDocument(page, route);
  await assertCanonicalUserFacingCopy(page, route);
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, `${name}-mobile.png`),
    fullPage: false,
  });
}

test.describe("Visual Quality Assurance Suite", () => {
  test.beforeEach(async ({ page }) => {
    const errors: string[] = [];
    pageErrors.set(page, errors);
    page.on("pageerror", (error) => errors.push(error.message));
  });

  test.afterEach(async ({ page }) => {
    expect(pageErrors.get(page) ?? [], "uncaught browser page errors").toEqual([]);
  });

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

      await assertResponsiveDocument(page, item.route);

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-desktop-light.png`),
        fullPage: true,
      });

      await page.setViewportSize({ width: 390, height: 844 });
      await assertResponsiveDocument(page, item.route);
      if (item.route !== "/auth/login") {
        await expect(page.getByRole("navigation", { name: "پیوندهای اصلی موبایل" })).toBeVisible();
        const publicCopy = await page.locator("body").innerText();
        for (const internalTerm of [
          "PRECISION COMMERCE",
          "MVP Constraints",
          "D-001",
          "D-014",
          "D-018",
          "B2B",
          "FMCG",
          "RBAC",
          "OTIF",
        ]) {
          expect(publicCopy, `public page ${item.route} contains internal/English term: ${internalTerm}`).not.toContain(internalTerm);
        }
        await assertCanonicalUserFacingCopy(page, item.route);
      }

      if (item.route === "/") {
        const homeText = await page.locator("body").innerText();
        expect(homeText).not.toContain("MVP Constraints");
        expect(homeText).not.toContain("D-001");
        expect(homeText).not.toContain("D-014");
        expect(homeText).not.toContain("D-018");
      }

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-mobile-light.png`),
        fullPage: false,
      });
    });
  }

  test("contact form never claims server success without a live submission endpoint", async ({ page }) => {
    await page.goto("/contact");
    await page.waitForLoadState("networkidle");
    await page.getByLabel(/نام و نام خانوادگی/).fill("فروشگاه آزمایشی");
    await page.getByLabel("شماره تلفن همراه").fill("09123456789");
    await page.getByLabel("متن پیام یا پرسش شما").fill("آزمون جلوگیری از اعلام موفقیت کاذب");
    await page.getByRole("button", { name: "ارسال فرم ارتباطی" }).click();

    const status = page.getByRole("status");
    await expect(status).toContainText("ارسال آنلاین این فرم هنوز فعال نیست");
    const visibleText = await page.locator("body").innerText();
    expect(visibleText).not.toContain("پیام شما با موفقیت ثبت شد");
    expect(visibleText).not.toContain("C-07");
    await assertCanonicalUserFacingCopy(page, "/contact");
  });

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

      if (item.route === "/retailer/catalog") {
        const categoryNames = (await page.locator('section[aria-label="دسته‌بندی‌ها"] button').allTextContents())
          .map((name) => name.trim().replace(/\s+/g, " ").toLocaleLowerCase("en-US"));
        expect(new Set(categoryNames).size, "catalog category labels must be unique").toBe(categoryNames.length);
        expect(categoryNames).not.toContain("fulfillment category");
        expect(categoryNames).not.toContain("proof category");
        expect(categoryNames).not.toContain("seed cat");
      }

      await page.setViewportSize({ width: 1440, height: 900 });
      await assertResponsiveDocument(page, item.route);
      await assertCanonicalUserFacingCopy(page, item.route);

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-desktop.png`),
        fullPage: true,
      });

      await page.setViewportSize({ width: 390, height: 844 });
      await assertResponsiveDocument(page, item.route);

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-mobile.png`),
        fullPage: false,
      });
      await page.setViewportSize({ width: 1440, height: 900 });
    }

    // These authenticated routes are real product surfaces but are not reached
    // from the retailer's primary navigation during the golden-surface sweep.
    for (const item of [
      { name: "retailer-profile", route: "/profile" },
      { name: "notifications-inbox", route: "/notifications" },
      { name: "notification-preferences", route: "/notifications/preferences" },
    ]) {
      await captureAuthenticatedRoute(page, item.route, item.name);
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

      if (item.route === "/vendor/inventory" || item.route === "/vendor/catalog") {
        await expect(page.getByText("کالای بدون نام", { exact: true })).toHaveCount(0);
        await expect(page.getByText("CARTON", { exact: true })).toHaveCount(0);
        await expect(page.getByText("PACK", { exact: true })).toHaveCount(0);
      }

      await page.setViewportSize({ width: 1440, height: 900 });
      await assertResponsiveDocument(page, item.route);

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-desktop.png`),
        fullPage: true,
      });

      await page.setViewportSize({ width: 390, height: 844 });
      await assertResponsiveDocument(page, item.route);

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-mobile.png`),
        fullPage: false,
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
      await assertResponsiveDocument(page, item.route);

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-desktop.png`),
        fullPage: true,
      });

      await page.setViewportSize({ width: 390, height: 844 });
      await assertResponsiveDocument(page, item.route);

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-mobile.png`),
        fullPage: false,
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

      if (item.route === "/ops") {
        await expect(page.getByText("DELIVERED", { exact: true })).toHaveCount(0);
      }

      await page.setViewportSize({ width: 1440, height: 900 });
      await assertResponsiveDocument(page, item.route);
      await assertCanonicalUserFacingCopy(page, item.route);

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-desktop.png`),
        fullPage: true,
      });

      await page.setViewportSize({ width: 390, height: 844 });
      await assertResponsiveDocument(page, item.route);

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-mobile.png`),
        fullPage: false,
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

    await captureAuthenticatedRoute(page, "/ops/notifications", "ops-notifications");

    for (const item of opsSubPages) {
      await page.locator('a[href="/ops"]').first().click();
      await page.waitForURL("**/ops");
      await page.waitForLoadState("networkidle");

      await page.locator(`a[href="${item.route}"]`).first().click();
      await page.waitForURL(`**${item.route}**`);
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(400);

      await page.setViewportSize({ width: 1440, height: 900 });
      await assertResponsiveDocument(page, item.route);

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-desktop.png`),
        fullPage: true,
      });

      await page.setViewportSize({ width: 390, height: 844 });
      await assertResponsiveDocument(page, item.route);

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-mobile.png`),
        fullPage: false,
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
      await assertResponsiveDocument(page, item.route);

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-desktop.png`),
        fullPage: true,
      });

      await page.setViewportSize({ width: 390, height: 844 });
      await assertResponsiveDocument(page, item.route);

      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${item.name}-mobile.png`),
        fullPage: false,
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
    await assertResponsiveDocument(page, "/field");

    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "field-dashboard-desktop.png"),
      fullPage: true,
    });

    await page.setViewportSize({ width: 390, height: 844 });
    await assertResponsiveDocument(page, "/field");

    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, "field-dashboard-mobile.png"),
      fullPage: false,
    });
  });
});
