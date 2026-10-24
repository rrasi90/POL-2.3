import { test, expect } from "@playwright/test";
import { loginAsRetailer, loginAsVendor, resetTenant, retailerPhone, vendorPhone } from "./helpers";

type CWVMetrics = {
  LCP?: number;
  CLS?: number;
  TTFB?: number;
  INP?: number;
};

async function collectCWV(page: any): Promise<CWVMetrics> {
  return await page.evaluate(async () => {
    const metrics: CWVMetrics = {};

    // Measure Largest Contentful Paint
    await new Promise<void>((resolve) => {
      let lcp = 0;
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const last = entries[entries.length - 1];
        if (last) lcp = last.startTime;
      });
      lcpObserver.observe({ type: "largest-contentful-paint", buffered: true });
      setTimeout(resolve, 2000);
      lcpObserver.disconnect();
      metrics.LCP = lcp;
    });

    // Measure Cumulative Layout Shift
    let cls = 0;
    await new Promise<void>((resolve) => {
      const clsObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) cls += entry.value;
        }
      });
      clsObserver.observe({ type: "layout-shift", buffered: true });
      setTimeout(resolve, 2000);
      clsObserver.disconnect();
      metrics.CLS = cls;
    });

    // Measure Time to First Byte
    await new Promise<void>((resolve) => {
      const navObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntriesByType("navigation")) {
          metrics.TTFB = entry.responseStart - entry.requestStart;
        }
      });
      navObserver.observe({ type: "navigation", buffered: true });
      setTimeout(resolve, 1000);
      navObserver.disconnect();
    });

    // Measure Interaction to Next Paint (requires user input; may be undefined)
    metrics.INP = undefined; // captured only on user gesture; leave undefined

    return metrics;
  });
}

async function measureRoute(page: any, route: string, label: string) {
  console.log(`[CWV] Measuring ${label} at ${route}`);
  await page.goto(route);
  await page.waitForLoadState("networkidle");
  const metrics = await collectCWV(page);
  console.log(`[CWV] ${label}:`, JSON.stringify(metrics));
  return metrics;
}

test.describe("Core Web Vitals (authenticated routes)", () => {
  test("retailer dashboard (authed)", async ({ page }, testInfo) => {
    const phone = retailerPhone(testInfo, 99);
    resetTenant(phone);
    await loginAsRetailer(page, phone);
    const metrics = await measureRoute(page, "/retailer", "retailer-dashboard");
    // LCP budget: ≤2500 ms; CLS budget: ≤0.1
    expect(metrics.LCP).toBeLessThanOrEqual(2500);
    expect(metrics.CLS).toBeLessThanOrEqual(0.1);
  });

  test("vendor dashboard (authed)", async ({ page }, testInfo) => {
    const phone = vendorPhone(testInfo, 99);
    resetTenant(phone);
    await loginAsVendor(page, phone);
    const metrics = await measureRoute(page, "/vendor", "vendor-dashboard");
    expect(metrics.LCP).toBeLessThanOrEqual(2500);
    expect(metrics.CLS).toBeLessThanOrEqual(0.1);
  });
});