import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import path from "node:path";
import { expect, type Page, type TestInfo } from "@playwright/test";

export const REPO_ROOT = path.resolve(__dirname, "..", "..", "..", "..");
export const API_PORT = Number(process.env.POL_E2E_API_PORT ?? 8001);
export const API_URL = `http://127.0.0.1:${API_PORT}`;
export const OTP_CODE = "1234";

export interface FixtureProduct {
  product_id: string;
  master_sku: string;
  name: string;
  vendor_product_id: string;
  pack_quantity: number;
  unit: string;
  price_toman: number;
}

export interface E2EFixture {
  retailer_phones: string[];
  products: FixtureProduct[];
}

export interface BasketLineInput {
  product_id: string;
  name: string;
  master_sku?: string;
  unit?: string;
  quantity: number;
  pack_quantity: number;
}

export interface ServerBasketItem {
  product_id: string;
  requested_quantity: number;
  pack_quantity: number;
  requested_unit: string;
}

export interface ServerBasket {
  id: string;
  status: string;
  version: number;
  created_at: string;
  items: ServerBasketItem[];
}

export interface BasketCalls {
  creates: string[];
  itemWrites: string[];
  currentReads: number;
}

let cachedFixture: E2EFixture | null = null;

export function fixture(): E2EFixture {
  if (!cachedFixture) {
    const file = path.join(__dirname, ".e2e-fixture.json");
    cachedFixture = JSON.parse(readFileSync(file, "utf8")) as E2EFixture;
  }
  return cachedFixture;
}

export function product(sku: string): FixtureProduct {
  const found = fixture().products.find((p) => p.master_sku === sku);
  if (!found) throw new Error(`fixture product ${sku} not seeded`);
  return found;
}

export function line(sku: string, quantity: number): BasketLineInput {
  const p = product(sku);
  return {
    product_id: p.product_id,
    name: p.name,
    master_sku: p.master_sku,
    unit: p.unit,
    quantity,
    pack_quantity: p.pack_quantity,
  };
}

export function retailerPhone(testInfo: TestInfo, salt = 0): string {
  const phones = fixture().retailer_phones;
  const index = (testInfo.parallelIndex + salt) % phones.length;
  return phones[index];
}

export function appAlert(page: Page) {
  return page.locator('[role="alert"]:not(#__next-route-announcer__)');
}

export function localNumber(e164: string): string {
  return `0${e164.slice(3)}`;
}

function runDb(args: string[]): unknown {
  const output = execFileSync("python", [path.join(REPO_ROOT, "scripts", "e2e_db.py"), ...args], {
    cwd: REPO_ROOT,
    encoding: "utf8",
    maxBuffer: 8 * 1024 * 1024,
    windowsHide: true,
  });
  return JSON.parse(output);
}

export function serverBaskets(phone: string): ServerBasket[] {
  return runDb(["baskets", phone]) as ServerBasket[];
}

export function serverBasketCounts(phone: string): { total: number; open: number; statuses: string[] } {
  return runDb(["counts", phone]) as { total: number; open: number; statuses: string[] };
}

export function resetTenant(phone: string): void {
  runDb(["reset", phone]);
}

export async function seedCart(page: Page, lines: BasketLineInput[]): Promise<void> {
  await page.addInitScript((payload) => {
    window.localStorage.setItem("pol.basket", JSON.stringify(payload));
  }, { lines, serverBasketId: null });
}

export function recordBasketCalls(page: Page): BasketCalls {
  const calls: BasketCalls = { creates: [], itemWrites: [], currentReads: 0 };
  page.on("request", (request) => {
    let pathname: string;
    try {
      pathname = new URL(request.url()).pathname;
    } catch {
      return;
    }
    if (!pathname.startsWith("/api/v1/baskets")) return;
    if (request.method() === "GET" && pathname === "/api/v1/baskets/current") {
      calls.currentReads += 1;
    } else if (request.method() === "POST" && pathname === "/api/v1/baskets") {
      calls.creates.push(pathname);
    } else if (
      request.method() === "POST" &&
      /^\/api\/v1\/baskets\/[^/]+\/items$/.test(pathname)
    ) {
      calls.itemWrites.push(pathname);
    }
  });
  return calls;
}

export async function loginAsRetailer(page: Page, phone: string): Promise<void> {
  await page.goto("/auth/login");
  await page.getByLabel(/شماره تلفن همراه/).fill(localNumber(phone));
  await page.getByRole("button", { name: "دریافت کد یکبار مصرف" }).click();
  await page.locator('input[maxlength="4"]').fill(OTP_CODE);
  await page.getByRole("button", { name: "تأیید و ورود به سامانه" }).click();
  await page.waitForURL(/\/retailer$/);
}

export async function openBasket(page: Page): Promise<void> {
  await page.getByRole("link", { name: "سبد خرید" }).first().click();
  await page.waitForURL("**/retailer/basket");
  await expect(page.getByRole("heading", { name: "سبد خرید یکپارچه" })).toBeVisible();
}

export async function readBasketState(page: Page): Promise<{
  lines: BasketLineInput[];
  serverBasketId: string | null;
}> {
  const raw = await page.evaluate(() => window.localStorage.getItem("pol.basket"));
  return JSON.parse(raw ?? "{}") as { lines: BasketLineInput[]; serverBasketId: string | null };
}

export function errorEnvelope(code: string, message: string) {
  return {
    success: false,
    error: {
      code,
      message,
      details: {},
      timestamp: new Date().toISOString(),
    },
  };
}
