import assert from "node:assert/strict";

const { mockRequest, resetMockState } = await import("../src/mock/mockTransport.ts");
const { toAsciiDigits, formatFaNumber, formatTehranDateTime } = await import("../src/i18n/fa.ts");

const owner = { Authorization: "Bearer mock-vendor-owner-token" };
const staff = { Authorization: "Bearer mock-vendor-staff-token" };

async function req<T>(method: string, path: string, body?: unknown, headers = owner): Promise<T> {
  return mockRequest<T>(method, path, body, headers);
}

async function rejects(fn: () => Promise<unknown>, label: string): Promise<void> {
  await assert.rejects(fn, undefined, label);
}

resetMockState();

assert.equal(toAsciiDigits("۱۲۳۴٥٦"), "123456");
assert.ok(formatFaNumber(1234567).includes("۱٬۲۳۴٬۵۶۷"));
const localizedDate = formatTehranDateTime("2026-09-29T12:00:00Z");
assert.ok(localizedDate.includes("۱۴۰۵"));
assert.ok(localizedDate.includes("مهر"));

const orders = await req<{ orders: Array<{ id: string; order_status: string }> }>("GET", "/api/v1/orders");
assert.equal(orders.orders.length, 5);

const ownerAccepted = await req<{ order_status: string }>("POST", "/api/v1/orders/mock-order-1/accept", {}, owner);
assert.equal(ownerAccepted.order_status, "ACCEPTED");

await rejects(
  () => req("POST", "/api/v1/orders/mock-order-2/accept", {}, staff),
  "Vendor Staff cannot accept orders",
);

const staffPrep = await req<{ order_status: string }>("POST", "/api/v1/orders/mock-order-2/preparing", {}, staff);
assert.equal(staffPrep.order_status, "PREPARING");

const inventoryBefore = await req<{ products: Array<{ vendor_product_id: string; physical_quantity: number }> }>(
  "GET",
  "/api/v1/catalog/vendors/products",
  undefined,
  staff,
);
const inventoryId = inventoryBefore.products[0].vendor_product_id;

await req("PATCH", "/api/v1/catalog/vendors/products/" + inventoryId + "/inventory", { new_physical_quantity: 123 }, staff);
await rejects(
  () => req("POST", "/api/v1/catalog/vendors/products/" + inventoryId + "/prices", { price_toman: 555000 }, staff),
  "Vendor Staff cannot manage prices",
);
await req("POST", "/api/v1/catalog/vendors/products/" + inventoryId + "/prices", { price_toman: 555000 }, owner);

const dailyChanged = await req<{ status: string; lines: Array<{ confirmed_quantity: number }> }>(
  "POST",
  "/api/v1/inventory/daily/2026-07-29/confirm-with-changes",
  { changes: [{ vendor_product_id: inventoryId, declared_quantity: 111 }] },
  staff,
);
assert.equal(dailyChanged.status, "CONFIRMED");
assert.equal(dailyChanged.lines[0].confirmed_quantity, 111);

const invoices = await req<{ invoices: unknown[] }>("GET", "/api/v1/invoices", undefined, owner);
assert.equal(invoices.invoices.length, 2);
const invoiceDetail = await req<{ items: unknown[] }>("GET", "/api/v1/invoices/mock-invoice-1", undefined, owner);
assert.equal(invoiceDetail.items.length, 2);
await rejects(() => req("GET", "/api/v1/invoices", undefined, staff), "Vendor Staff cannot view invoices");

const settlements = await req<{ settlements: unknown[] }>("GET", "/api/v1/vendors/settlements", undefined, owner);
assert.equal(settlements.settlements.length, 2);
const settlementDetail = await req<{ adjustments: unknown[]; net_vendor_amount_toman: number }>("GET", "/api/v1/settlements/mock-settlement-1", undefined, owner);
assert.equal(settlementDetail.adjustments.length, 1);
assert.equal(settlementDetail.net_vendor_amount_toman, 16080000);
await rejects(() => req("GET", "/api/v1/vendors/settlements", undefined, staff), "Vendor Staff cannot view settlements");

const customers = await req<{ customers: unknown[] }>("GET", "/api/v1/vendors/customers?query=اروند", undefined, staff);
assert.equal(customers.customers.length, 1);

const staffList = await req<{ members: Array<{ membership_id: string }> }>("GET", "/api/v1/vendors/staff", undefined, staff);
assert.equal(staffList.members.length, 2);

await rejects(
  () => req("POST", "/api/v1/vendors/staff/invite", { phone_number: "+989160000003", full_name: "New Staff" }, staff),
  "Vendor Staff cannot invite members",
);

const permissions = await req<{ effective_permissions: string[] }>(
  "GET",
  "/api/v1/vendors/staff/mock-member-staff/permissions",
  undefined,
  owner,
);
assert.ok(permissions.effective_permissions.includes("inventory.scan"));

const storefront = await req<{ vendors: unknown[] }>("GET", "/api/v1/storefront/vendors", undefined, owner);
assert.equal(storefront.vendors.length, 1);

const storefrontProducts = await req<{ items: unknown[] }>(
  "GET",
  "/api/v1/storefront/vendors/mock-vendor/products?limit=50&offset=0",
  undefined,
  owner,
);
assert.equal(storefrontProducts.items.length, 4);

const exact = await req<{ match_type: string; product: { id: string } }>(
  "GET",
  "/api/v1/catalog/barcode/lookup?barcode=6260123456789",
  undefined,
  staff,
);
assert.equal(exact.match_type, "EXACT");
assert.equal(exact.product.id, "mock-product-1");

const ambiguous = await req<{ match_type: string; products: unknown[] }>(
  "GET",
  "/api/v1/catalog/barcode/lookup?barcode=6260123456796",
  undefined,
  staff,
);
assert.equal(ambiguous.match_type, "AMBIGUOUS");
assert.equal(ambiguous.products.length, 2);

const noMatch = await req<{ match_type: string }>(
  "POST",
  "/api/v1/products/match-barcode",
  { barcode: "6260123456802", create_candidate: false },
  staff,
);
assert.equal(noMatch.match_type, "NO_MATCH");

const candidate = await req<{ candidate_id: string }>(
  "POST",
  "/api/v1/products/match-barcode",
  { barcode: "6260123456802", create_candidate: true, proposed_title: "کالای جدید نمونه", vendor_sku: "MOCK-NEW-001" },
  staff,
);
assert.match(candidate.candidate_id, /^mock-candidate-/);

const scan = await req<{ accepted: boolean; session_id: string }>(
  "POST",
  "/api/v1/vendors/inventory/continuous-scan",
  { product_id: "mock-product-1", vendor_sku: "AZ-COLA-1500", packaging_unit: "CARTON", pack_quantity: 6, physical_quantity: 120, unit_price_toman: 555000, session_id: "mock-qa-session" },
  staff,
);
assert.equal(scan.accepted, true);
await req("POST", "/api/v1/vendors/inventory/publish", { session_id: scan.session_id }, staff);

const support = await req<{ id: string }>(
  "POST",
  "/api/v1/support/cases",
  { subject: "Mock support test", case_type: "ORDER", priority: "NORMAL", related_order_id: "mock-order-1" },
  staff,
);
assert.ok(support.id);

const message = await req<{ id: string }>(
  "POST",
  "/api/v1/support/cases/" + support.id + "/messages",
  { body: "پیام تستی" },
  staff,
);
assert.ok(message.id);

const profile = await req<{ membership: { role: string } }>("GET", "/api/v1/profile", undefined, staff);
assert.equal(profile.membership.role, "VENDOR_STAFF");

console.log("[MOCK-QA PASS] Vendor mock transport exercised successfully across auth, RBAC, orders, inventory, finance, storefront, barcode, scan/publish, support and profile.");
