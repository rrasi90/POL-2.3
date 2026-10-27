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
const published = await req<{ status: string; published_count: number; idempotent_replay: boolean }>(
  "POST",
  "/api/v1/vendors/inventory/publish",
  { session_id: scan.session_id },
  staff,
);
assert.equal(published.status, "PUBLISHED");
assert.equal(published.published_count, 1);
assert.equal(published.idempotent_replay, false);

const replayedPublish = await req<{ status: string; published_count: number; idempotent_replay: boolean }>(
  "POST",
  "/api/v1/vendors/inventory/publish",
  { session_id: scan.session_id },
  staff,
);
assert.equal(replayedPublish.status, "PUBLISHED");
assert.equal(replayedPublish.published_count, 1);
assert.equal(replayedPublish.idempotent_replay, true);

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

const profile = await req<{ membership: { role: string }; user_profile: { timezone: string } }>("GET", "/api/v1/profile", undefined, staff);
assert.equal(profile.membership.role, "VENDOR_STAFF");
assert.equal(profile.user_profile.timezone, "Asia/Tehran");
await req("PUT", "/api/v1/profile", { display_name: "انبار و سفارش" }, staff);
const preferences = await req<Array<{ category: string; push_enabled: boolean; sms_enabled: boolean }>>("GET", "/api/v1/notifications/preferences", undefined, staff);
assert.equal(preferences.length, 1);
assert.equal(preferences[0].push_enabled, true);
assert.equal(preferences[0].sms_enabled, true);
await req("PUT", "/api/v1/notifications/preferences", { event_name: "ORDER_STATUS_CHANGED", channel: "PUSH", is_enabled: false }, staff);

console.log("[MOCK-QA PASS] Vendor mock transport exercised successfully across auth, RBAC, orders, inventory, finance, storefront, barcode, scan/publish, support and profile.");


const logout = await req<{ success: boolean }>("DELETE", "/api/v1/auth/sessions/current", undefined, staff);
assert.equal(logout.success, true);


// Retailer mock coverage — keep this separate from vendor fixtures so role-specific
// behavior and the retail basket/checkout contract are actually exercised.
resetMockState();
const retailerHeaders = { Authorization: "Bearer mock-retailer-owner-token" };
const retailerStaffHeaders = { Authorization: "Bearer mock-retailer-staff-token" };

const retailerLogin = await req<{ role: string; access_token: string }>(
  "POST",
  "/api/v1/auth/verify-otp",
  { mobile_number: "+989161110003", otp_code: "123456" },
  {},
);
assert.equal(retailerLogin.role, "RETAILER_OWNER");
assert.equal(retailerLogin.access_token, "mock-retailer-owner-token");

const retailerContext = await req<{ organization_type: string; role: string }>(
  "GET", "/api/v1/profile/context", undefined, retailerHeaders,
);
assert.equal(retailerContext.organization_type, "RETAILER");
assert.equal(retailerContext.role, "RETAILER_OWNER");

const retailerSearch = await req<{ items: Array<{ id: string; canonical_name_fa: string }> }>(
  "GET", "/api/v1/catalog/search?q=" + encodeURIComponent("نوشابه") + "&limit=40", undefined, retailerHeaders,
);
assert.equal(retailerSearch.items.length, 1);
assert.equal(retailerSearch.items[0].id, "mock-product-1");

const retailBasket = await req<{ basket_id: string; version: number }>(
  "POST", "/api/v1/baskets", {}, retailerHeaders,
);
assert.equal(retailBasket.version, 1);
const retailBasketItem1 = await req<{ basket_id: string; version: number }>(
  "POST", "/api/v1/baskets/" + retailBasket.basket_id + "/items",
  { product_id: "mock-product-1", requested_quantity: 1, pack_quantity: 6, expected_version: retailBasket.version },
  retailerHeaders,
);
assert.equal(retailBasketItem1.version, 2);
const retailBasketItem2 = await req<{ basket_id: string; version: number }>(
  "POST", "/api/v1/baskets/" + retailBasket.basket_id + "/items",
  { product_id: "mock-product-2", requested_quantity: 1, pack_quantity: 12, expected_version: retailBasketItem1.version },
  retailerHeaders,
);
assert.equal(retailBasketItem2.version, 3);
await rejects(
  () => req("POST", "/api/v1/baskets/" + retailBasket.basket_id + "/items",
    { product_id: "mock-product-3", requested_quantity: 1, pack_quantity: 24, expected_version: 1 }, retailerHeaders),
  "Retailer basket rejects a stale version",
);

const retailAllocation = await req<{ allocation_plan_id: string; summary: { total_amount_toman: number; total_items_allocated: number } }>(
  "POST", "/api/v1/baskets/" + retailBasket.basket_id + "/allocation-preview", {}, retailerHeaders,
);
assert.equal(retailAllocation.summary.total_amount_toman, 850000);
assert.equal(retailAllocation.summary.total_items_allocated, 2);

const retailCheckoutKey = "af0f08f9-69d1-4f45-8a0b-047c2dc2b6b1";
const retailCheckoutBody = {
  allocation_plan_id: retailAllocation.allocation_plan_id,
  delivery_address: "اهواز، کیانپارس، خیابان نمونه، پلاک ۱۲",
  preferred_payment_method: "CASH_ON_DELIVERY",
};
const retailCheckout = await req<{ order_group_id: string; total_amount_toman: number; idempotent_replay: boolean }>(
  "POST", "/api/v1/orders", retailCheckoutBody,
  { ...retailerHeaders, "Idempotency-Key": retailCheckoutKey },
);
assert.equal(retailCheckout.total_amount_toman, 850000);
assert.equal(retailCheckout.idempotent_replay, false);
const retailCheckoutReplay = await req<{ order_group_id: string; idempotent_replay: boolean }>(
  "POST", "/api/v1/orders", retailCheckoutBody,
  { ...retailerHeaders, "Idempotency-Key": retailCheckoutKey },
);
assert.equal(retailCheckoutReplay.order_group_id, retailCheckout.order_group_id);
assert.equal(retailCheckoutReplay.idempotent_replay, true);

const retailOrders = await req<{ orders: Array<{ id: string; order_status: string }> }>(
  "GET", "/api/v1/orders?limit=50&offset=0", undefined, retailerHeaders,
);
assert.ok(retailOrders.orders.length >= 3);
assert.equal(retailOrders.orders[0].order_status, "SUBMITTED");
const latestRetailOrderId = retailOrders.orders[0].id;
const retailOrder = await req<{ id: string; delivery_address: string }>(
  "GET", "/api/v1/orders/" + latestRetailOrderId, undefined, retailerHeaders,
);
assert.equal(retailOrder.id, latestRetailOrderId);
assert.ok(retailOrder.delivery_address.includes("اهواز"));
const retailItems = await req<{ items: Array<{ ordered_quantity: number }> }>(
  "GET", "/api/v1/orders/" + latestRetailOrderId + "/items", undefined, retailerHeaders,
);
assert.equal(retailItems.items.length, 2);
const retailTimeline = await req<{ timeline: Array<{ event_type: string }> }>(
  "GET", "/api/v1/orders/" + latestRetailOrderId + "/timeline", undefined, retailerHeaders,
);
assert.equal(retailTimeline.timeline[0].event_type, "ORDER_SUBMITTED");

const retailers = await req<{ items: Array<{ id: string }> }>(
  "GET", "/api/v1/storefront/vendors", undefined, retailerHeaders,
);
assert.equal(retailers.items.length, 1);
const storefront = await req<{ items: Array<{ product_id: string }> }>(
  "GET", "/api/v1/storefront/vendors/mock-vendor/products?limit=50&offset=0", undefined, retailerHeaders,
);
assert.equal(storefront.items.length, 4);

const retailInvoices = await req<{ invoices: Array<{ id: string }> }>(
  "GET", "/api/v1/invoices?limit=50&offset=0", undefined, retailerHeaders,
);
assert.equal(retailInvoices.invoices.length, 1);

const retailSupport = await req<{ id: string }>(
  "POST", "/api/v1/support/cases",
  { subject: "آزمون پشتیبانی خرده‌فروش", case_type: "GENERAL", priority: "NORMAL" },
  retailerHeaders,
);
assert.ok(retailSupport.id);
const retailSupportMessage = await req<{ id: string }>(
  "POST", "/api/v1/support/cases/" + retailSupport.id + "/messages",
  { body: "پیام آزمایشی" },
  retailerHeaders,
);
assert.ok(retailSupportMessage.id);

const retailerStaffLogin = await req<{ role: string; access_token: string }>(
  "POST", "/api/v1/auth/verify-otp",
  { mobile_number: "+989161110004", otp_code: "123456" },
  {},
);
assert.equal(retailerStaffLogin.role, "RETAILER_STAFF");
assert.equal(retailerStaffLogin.access_token, "mock-retailer-staff-token");
const retailerStaffProfile = await req<{ membership: { role: string } }>(
  "GET", "/api/v1/profile", undefined, retailerStaffHeaders,
);
assert.equal(retailerStaffProfile.membership.role, "RETAILER_STAFF");

console.log("[MOCK-QA PASS] Retailer mock transport exercised across auth, catalog search, basket versioning, allocation, idempotent checkout, order detail/timeline, supplier storefront, invoices, support, and owner/staff role context.");
