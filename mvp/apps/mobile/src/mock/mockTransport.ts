type MockRole = "VENDOR_OWNER" | "VENDOR_STAFF";

type MockOrder = {
  id: string;
  order_number: string;
  order_status: string;
  total_amount_toman: number;
  created_at: string;
  retailer_name: string;
  retailer_store_name: string;
};

type MockInventory = {
  id: string;
  vendor_product_id: string;
  product_name: string;
  vendor_sku: string;
  packaging_unit: string;
  pack_quantity: number;
  physical_quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  current_price_toman: number;
  freshness_status: string;
  is_stale: boolean;
};

type MockOrderItem = {
  id: string;
  product_id: string;
  product_name_snapshot: string;
  brand_name_snapshot: string;
  vendor_sku_snapshot: string;
  packaging_unit_snapshot: string;
  pack_quantity_snapshot: number;
  ordered_quantity: number;
  accepted_quantity: number;
  delivered_quantity: number;
  unit_price_toman: number;
  total_line_amount_toman: number;
  fulfillment_status: string;
};

type MockState = {
  orders: MockOrder[];
  orderItems: Record<string, MockOrderItem[]>;
  timelines: Record<string, Array<Record<string, unknown>>>;
  inventory: MockInventory[];
  daily: {
    status: string;
    lines: Array<{ id: string; vendor_product_id: string; product_id: string; product_name: string; expected_quantity: number; confirmed_quantity: number }>;
  };
  invoices: Array<Record<string, unknown>>;
  settlements: Array<Record<string, unknown>>;
  referrals: Array<Record<string, unknown>>;
  customers: Array<Record<string, unknown>>;
  staff: Array<Record<string, unknown>>;
  permissions: Record<string, {
    membership_id: string;
    full_name: string;
    role: MockRole;
    grantable_permissions: string[];
    delegated_grants: Array<Record<string, unknown>>;
    effective_permissions: string[];
  }>;
  storefrontVendor: Record<string, unknown>;
  storefrontProducts: Array<Record<string, unknown>>;
  supportCases: Array<Record<string, unknown>>;
  barcodeMap: Record<string, Record<string, unknown>>;
  candidates: Array<Record<string, unknown>>;
};

const now = new Date("2026-09-29T09:30:00+03:30");

function iso(hours = 0): string {
  return new Date(now.getTime() + hours * 3600_000).toISOString();
}

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function makeState(): MockState {
  const items1: MockOrderItem[] = [
    {
      id: "mock-item-1",
      product_id: "mock-product-1",
      product_name_snapshot: "نوشابه خانواده کلاسیک",
      brand_name_snapshot: "آذرنوش",
      vendor_sku_snapshot: "AZ-COLA-1500",
      packaging_unit_snapshot: "CARTON",
      pack_quantity_snapshot: 6,
      ordered_quantity: 12,
      accepted_quantity: 12,
      delivered_quantity: 0,
      unit_price_toman: 540000,
      total_line_amount_toman: 6480000,
      fulfillment_status: "PENDING",
    },
    {
      id: "mock-item-2",
      product_id: "mock-product-2",
      product_name_snapshot: "چیپس نمکی خانواده",
      brand_name_snapshot: "نمکین",
      vendor_sku_snapshot: "NAM-SALT-12",
      packaging_unit_snapshot: "CARTON",
      pack_quantity_snapshot: 12,
      ordered_quantity: 8,
      accepted_quantity: 6,
      delivered_quantity: 0,
      unit_price_toman: 310000,
      total_line_amount_toman: 2480000,
      fulfillment_status: "PENDING",
    },
  ];

  return {
    orders: [
      { id: "mock-order-1", order_number: "POL-AHV-1001", order_status: "SUBMITTED", total_amount_toman: 8960000, created_at: iso(-1), retailer_name: "احمد رضایی", retailer_store_name: "سوپرمارکت اروند" },
      { id: "mock-order-2", order_number: "POL-AHV-1000", order_status: "ACCEPTED", total_amount_toman: 5120000, created_at: iso(-3), retailer_name: "مریم کریمی", retailer_store_name: "فروشگاه کارون" },
      { id: "mock-order-3", order_number: "POL-AHV-0997", order_status: "PREPARING", total_amount_toman: 7340000, created_at: iso(-8), retailer_name: "حسین موسوی", retailer_store_name: "سوپر محله" },
      { id: "mock-order-4", order_number: "POL-AHV-0995", order_status: "READY", total_amount_toman: 4680000, created_at: iso(-12), retailer_name: "سمیه احمدی", retailer_store_name: "فروشگاه نخل" },
      { id: "mock-order-5", order_number: "POL-AHV-0990", order_status: "DISPATCHED", total_amount_toman: 9230000, created_at: iso(-24), retailer_name: "رضا مرادی", retailer_store_name: "مارکت ساحل" },
    ],
    orderItems: {
      "mock-order-1": items1,
      "mock-order-2": items1.map((x) => ({ ...x, id: x.id + "-2", accepted_quantity: x.ordered_quantity, total_line_amount_toman: x.ordered_quantity * x.unit_price_toman })),
      "mock-order-3": items1.map((x) => ({ ...x, id: x.id + "-3", fulfillment_status: "PREPARING" })),
      "mock-order-4": items1.map((x) => ({ ...x, id: x.id + "-4", fulfillment_status: "READY" })),
      "mock-order-5": items1.map((x) => ({ ...x, id: x.id + "-5", fulfillment_status: "DISPATCHED" })),
    },
    timelines: {
      "mock-order-1": [{ event_type: "ORDER_SUBMITTED", created_at: iso(-1), actor_label: "خرده‌فروشی" }],
      "mock-order-2": [{ event_type: "ORDER_ACCEPTED", created_at: iso(-2.5), actor_label: "بنکدار" }],
      "mock-order-3": [{ event_type: "ORDER_ACCEPTED", created_at: iso(-9), actor_label: "بنکدار" }, { event_type: "ORDER_PREPARING", created_at: iso(-8), actor_label: "بنکدار" }],
      "mock-order-4": [{ event_type: "ORDER_READY", created_at: iso(-12), actor_label: "بنکدار" }],
      "mock-order-5": [{ event_type: "ORDER_DISPATCHED", created_at: iso(-24), actor_label: "بنکدار" }],
    },
    inventory: [
      { id: "mock-vp-1", vendor_product_id: "mock-vp-1", product_name: "نوشابه خانواده کلاسیک", vendor_sku: "AZ-COLA-1500", packaging_unit: "CARTON", pack_quantity: 6, physical_quantity: 120, reserved_quantity: 24, available_quantity: 96, current_price_toman: 540000, freshness_status: "FRESH", is_stale: false },
      { id: "mock-vp-2", vendor_product_id: "mock-vp-2", product_name: "چیپس نمکی خانواده", vendor_sku: "NAM-SALT-12", packaging_unit: "CARTON", pack_quantity: 12, physical_quantity: 40, reserved_quantity: 18, available_quantity: 22, current_price_toman: 310000, freshness_status: "FRESH", is_stale: false },
      { id: "mock-vp-3", vendor_product_id: "mock-vp-3", product_name: "رب گوجه ۸۰۰ گرمی", vendor_sku: "ROB-800-24", packaging_unit: "CARTON", pack_quantity: 24, physical_quantity: 12, reserved_quantity: 10, available_quantity: 2, current_price_toman: 1280000, freshness_status: "STALE", is_stale: true },
      { id: "mock-vp-4", vendor_product_id: "mock-vp-4", product_name: "آب معدنی ۱.۵ لیتری", vendor_sku: "AB-1500-6", packaging_unit: "PACK", pack_quantity: 6, physical_quantity: 75, reserved_quantity: 15, available_quantity: 60, current_price_toman: 198000, freshness_status: "FRESH", is_stale: false },
    ],
    daily: {
      status: "PENDING",
      lines: [
        { id: "mock-daily-1", vendor_product_id: "mock-vp-1", product_id: "mock-product-1", product_name: "نوشابه خانواده کلاسیک", expected_quantity: 120, confirmed_quantity: 120 },
        { id: "mock-daily-2", vendor_product_id: "mock-vp-2", product_id: "mock-product-2", product_name: "چیپس نمکی خانواده", expected_quantity: 40, confirmed_quantity: 40 },
        { id: "mock-daily-3", vendor_product_id: "mock-vp-3", product_id: "mock-product-3", product_name: "رب گوجه ۸۰۰ گرمی", expected_quantity: 12, confirmed_quantity: 12 },
      ],
    },
    invoices: [
      { id: "mock-invoice-1", invoice_number: "INV-AHV-1001", status: "ISSUED", total_amount_toman: 8960000, issued_at: iso(-1) },
      { id: "mock-invoice-2", invoice_number: "INV-AHV-0997", status: "ISSUED", total_amount_toman: 7340000, issued_at: iso(-8) },
    ],
    settlements: [
      { id: "mock-settlement-1", settlement_number: "SET-AHV-202609", status: "CALCULATED", amount_toman: 16080000 },
      { id: "mock-settlement-2", settlement_number: "SET-AHV-202608", status: "PAID", amount_toman: 27840000 },
    ],
    referrals: [
      { id: "mock-ref-1", status: "ACTIVE", referral_code: "POLV-AHV001", referred_organization_id: "mock-retailer-org-1" },
      { id: "mock-ref-2", status: "REDEEMED", referral_code: "POLV-AHV002", referred_organization_id: "mock-retailer-org-2" },
    ],
    customers: [
      { retailer_id: "mock-retailer-1", store_name: "سوپرمارکت اروند", city: "اهواز", neighborhood: "کیانپارس", full_name: "احمد رضایی", phone_number: "+989161110001", order_count: 14, last_order_at: iso(-1) },
      { retailer_id: "mock-retailer-2", store_name: "فروشگاه کارون", city: "اهواز", neighborhood: "گلستان", full_name: "مریم کریمی", phone_number: "+989161110002", order_count: 9, last_order_at: iso(-3) },
      { retailer_id: "mock-retailer-3", store_name: "مارکت ساحل", city: "اهواز", neighborhood: "زیتون کارمندی", full_name: "رضا مرادی", phone_number: "+989161110003", order_count: 5, last_order_at: iso(-24) },
    ],
    staff: [
      { membership_id: "mock-member-owner", user_id: "mock-owner", phone_number: "+989160000001", full_name: "مالک بنکداری", role: "VENDOR_OWNER", status: "ACTIVE" },
      { membership_id: "mock-member-staff", user_id: "mock-staff", phone_number: "+989160000002", full_name: "انبار و سفارش", role: "VENDOR_STAFF", status: "ACTIVE" },
    ],
    permissions: {
      "mock-member-staff": {
        membership_id: "mock-member-staff",
        full_name: "انبار و سفارش",
        role: "VENDOR_STAFF",
        grantable_permissions: ["inventory.adjust", "inventory.scan", "order.fulfillment"],
        delegated_grants: [],
        effective_permissions: ["catalog.view", "inventory.view", "inventory.scan", "inventory.adjust", "price.view", "order.view", "order.fulfillment", "delivery.dispatch"],
      },
    },
    storefrontVendor: {
      id: "mock-vendor",
      name: "بنکداری نمونه اهواز",
      display_name: "پل بنکدار اهواز",
      city: "اهواز",
      description: "ویترین نمونه برای تست Android Vendor",
      is_active: true,
      product_count: 4,
      created_at: iso(-720),
    },
    storefrontProducts: [
      { id: "mock-vs-1", product_id: "mock-product-1", product_name: "نوشابه خانواده کلاسیک", name: "نوشابه خانواده کلاسیک", brand_name: "آذرنوش", price_toman: 540000, stock_quantity: 96, packaging_unit: "CARTON", is_available: true },
      { id: "mock-vs-2", product_id: "mock-product-2", product_name: "چیپس نمکی خانواده", name: "چیپس نمکی خانواده", brand_name: "نمکین", price_toman: 310000, stock_quantity: 22, packaging_unit: "CARTON", is_available: true },
      { id: "mock-vs-3", product_id: "mock-product-3", product_name: "رب گوجه ۸۰۰ گرمی", name: "رب گوجه ۸۰۰ گرمی", brand_name: "سرخینه", price_toman: 1280000, stock_quantity: 2, packaging_unit: "CARTON", is_available: false },
      { id: "mock-vs-4", product_id: "mock-product-4", product_name: "آب معدنی ۱.۵ لیتری", name: "آب معدنی ۱.۵ لیتری", brand_name: "آبگون", price_toman: 198000, stock_quantity: 60, packaging_unit: "PACK", is_available: true },
    ],
    supportCases: [
      { id: "mock-case-1", subject: "کسری کالای سفارش POL-AHV-1001", case_type: "ORDER", priority: "HIGH", status: "OPEN", related_order_id: "mock-order-1", created_at: iso(-2), messages: [{ id: "mock-msg-1", body: "دو کارتن چیپس در موجودی تحویل اختلاف دارد.", sender_role: "VENDOR_OWNER", created_at: iso(-1.5) }] },
    ],
    barcodeMap: {
      "6260123456789": {
        match_type: "EXACT",
        confidence_score: 1,
        product: { id: "mock-product-1", master_sku: "SKU-AZ-COLA", canonical_name_fa: "نوشابه خانواده کلاسیک", brand_name: "آذرنوش", base_unit: "PIECE", default_pack_unit: "CARTON", default_pack_quantity: 6 },
        candidate_id: null,
        vendor_product_id: "mock-vp-1",
      },
      "6260123456796": {
        match_type: "AMBIGUOUS",
        confidence_score: 0,
        products: [
          { id: "mock-product-1", master_sku: "SKU-AZ-COLA", canonical_name_fa: "نوشابه خانواده کلاسیک", brand_name: "آذرنوش" },
          { id: "mock-product-4", master_sku: "SKU-AZ-COLA-PACK", canonical_name_fa: "نوشابه خانواده کلاسیک پک اقتصادی", brand_name: "آذرنوش" },
        ],
        candidate_id: null,
        vendor_product_id: null,
      },
      "6260123456819": {
        match_type: "HIGH_CONFIDENCE",
        confidence_score: 0.94,
        product: { id: "mock-product-2", master_sku: "SKU-NAM-SALT", canonical_name_fa: "چیپس نمکی خانواده", brand_name: "نمکین", base_unit: "PIECE", default_pack_unit: "CARTON", default_pack_quantity: 12 },
        candidate_id: null,
        vendor_product_id: "mock-vp-2",
      },
      "6260123456802": {
        match_type: "NO_MATCH",
        confidence_score: 0,
        product: null,
        candidate_id: null,
        vendor_product_id: null,
      },
    },
    candidates: [],
  };
}

let state = makeState();

export function resetMockState(): void {
  state = makeState();
}

function roleFromHeaders(headers?: Record<string, string>): MockRole {
  const token = headers?.Authorization || "";
  return token.includes("mock-vendor-staff") ? "VENDOR_STAFF" : "VENDOR_OWNER";
}

function findOrder(id: string): MockOrder {
  const order = state.orders.find((row) => row.id === id);
  if (!order) throw new Error("Mock order not found");
  return order;
}

function envelope<T>(value: T): T {
  return clone(value);
}

function notFound(path: string): never {
  throw new Error("Mock route not implemented: " + path);
}

export async function mockRequest<T>(
  method: string,
  path: string,
  body?: unknown,
  headers?: Record<string, string>,
): Promise<T> {
  const url = new URL("http://mock.local" + path);
  const pathname = url.pathname;
  const role = roleFromHeaders(headers);

  if (method === "POST" && pathname === "/api/v1/auth/request-otp") {
    return envelope({ otp_request_id: "mock-otp-request", expires_in_seconds: 120, resend_interval_seconds: 60 });
  }

  if (method === "POST" && pathname === "/api/v1/auth/verify-otp") {
    const phone = String((body as Record<string, unknown> | undefined)?.mobile_number || "");
    const mockRole: MockRole = phone.endsWith("0002") ? "VENDOR_STAFF" : "VENDOR_OWNER";
    const token = mockRole === "VENDOR_STAFF" ? "mock-vendor-staff-token" : "mock-vendor-owner-token";
    return envelope({ access_token: token, refresh_token: token + "-refresh", role: mockRole, current_organization: { id: "mock-vendor-org", role: mockRole } });
  }

  if (method === "GET" && pathname === "/api/v1/orders") return envelope({ orders: state.orders, limit: 50, offset: 0 });
  if (method === "GET" && /^\/api\/v1\/orders\/[^/]+$/.test(pathname)) return envelope(findOrder(pathname.split("/").pop()!));
  if (method === "GET" && /^\/api\/v1\/orders\/[^/]+\/items$/.test(pathname)) {
    const id = pathname.split("/")[4];
    return envelope({ items: state.orderItems[id] || [] });
  }
  if (method === "GET" && /^\/api\/v1\/orders\/[^/]+\/timeline$/.test(pathname)) {
    const id = pathname.split("/")[4];
    return envelope({ timeline: state.timelines[id] || [] });
  }

  if (method === "POST" && /^\/api\/v1\/orders\/[^/]+\/(accept|preparing|ready)$/.test(pathname)) {
    const parts = pathname.split("/");
    const id = parts[4];
    const action = parts[5];
    const order = findOrder(id);
    if (action === "accept") {
      if (role !== "VENDOR_OWNER") throw new Error("Mock permission denied: order.accept");
      order.order_status = "ACCEPTED";
      (state.timelines[id] ||= []).push({ event_type: "ORDER_ACCEPTED", created_at: new Date().toISOString(), actor_label: "بنکدار" });
    } else if (action === "preparing") {
      order.order_status = "PREPARING";
      (state.timelines[id] ||= []).push({ event_type: "ORDER_PREPARING", created_at: new Date().toISOString(), actor_label: "بنکدار" });
    } else {
      order.order_status = "READY";
      (state.timelines[id] ||= []).push({ event_type: "ORDER_READY", created_at: new Date().toISOString(), actor_label: "بنکدار" });
    }
    return envelope(order);
  }

  if (method === "POST" && /^\/api\/v1\/orders\/[^/]+\/reject$/.test(pathname)) {
    if (role !== "VENDOR_OWNER") throw new Error("Mock permission denied: order.accept");
    const id = pathname.split("/")[4];
    const order = findOrder(id);
    order.order_status = "REJECTED";
    return envelope(order);
  }

  if (method === "POST" && /^\/api\/v1\/orders\/[^/]+\/partial-acceptance-proposals$/.test(pathname)) {
    if (role !== "VENDOR_OWNER") throw new Error("Mock permission denied: order.accept");
    const id = pathname.split("/")[4];
    return envelope({ id: "mock-proposal-" + id, order_id: id, status: "PENDING", items: (body as Record<string, unknown>)?.items || [] });
  }

  if (method === "POST" && /^\/api\/v1\/orders\/[^/]+\/dispatch$/.test(pathname)) {
    const id = pathname.split("/")[4];
    const order = findOrder(id);
    order.order_status = "DISPATCHED";
    return envelope(order);
  }

  if (method === "GET" && pathname === "/api/v1/catalog/vendors/products") {
    return envelope({ products: state.inventory });
  }

  if (method === "PATCH" && /^\/api\/v1\/catalog\/vendors\/products\/[^/]+\/inventory$/.test(pathname)) {
    const id = pathname.split("/")[6];
    const row = state.inventory.find((x) => x.vendor_product_id === id || x.id === id);
    if (!row) throw new Error("Mock inventory row not found");
    const n = Number((body as Record<string, unknown> | undefined)?.new_physical_quantity);
    if (!Number.isFinite(n) || n < 0) throw new Error("Mock invalid quantity");
    row.physical_quantity = n;
    row.available_quantity = Math.max(0, n - row.reserved_quantity);
    return envelope(row);
  }

  if (method === "POST" && /^\/api\/v1\/catalog\/vendors\/products\/[^/]+\/prices$/.test(pathname)) {
    if (role !== "VENDOR_OWNER") throw new Error("Mock permission denied: price.manage");
    const id = pathname.split("/")[6];
    const row = state.inventory.find((x) => x.vendor_product_id === id || x.id === id);
    if (!row) throw new Error("Mock inventory row not found");
    row.current_price_toman = Number((body as Record<string, unknown> | undefined)?.price_toman || 0);
    return envelope(row);
  }

  if (method === "GET" && /^\/api\/v1\/inventory\/daily\/[^/]+$/.test(pathname)) {
    return envelope(state.daily);
  }

  if (method === "POST" && /^\/api\/v1\/inventory\/daily\/[^/]+\/confirm$/.test(pathname)) {
    state.daily.status = "CONFIRMED";
    return envelope(state.daily);
  }

  if (method === "POST" && /^\/api\/v1\/inventory\/daily\/[^/]+\/confirm-with-changes$/.test(pathname)) {
    state.daily.status = "CONFIRMED";
    const changes = (((body as Record<string, unknown>) || {}).changes || []) as Array<Record<string, unknown>>;
    for (const change of changes) {
      const line = state.daily.lines.find((x) => x.vendor_product_id === String(change.vendor_product_id));
      if (line) line.confirmed_quantity = Number(change.declared_quantity);
    }
    return envelope(state.daily);
  }

  if (method === "GET" && pathname === "/api/v1/invoices") return envelope({ invoices: state.invoices, limit: 50, offset: 0 });
  if (method === "GET" && pathname === "/api/v1/vendors/settlements") return envelope({ settlements: state.settlements, limit: 50, offset: 0 });

  if (method === "GET" && pathname === "/api/v1/referrals") return envelope({ referrals: state.referrals, limit: 50, offset: 0 });

  if (method === "GET" && pathname === "/api/v1/vendors/customers") {
    const query = (url.searchParams.get("query") || "").trim().toLowerCase();
    const filtered = query
      ? state.customers.filter((x) => String(x.store_name).toLowerCase().includes(query) || String(x.full_name).toLowerCase().includes(query) || String(x.phone_number).toLowerCase().includes(query))
      : state.customers;
    return envelope({ customers: filtered, limit: 50, offset: 0 });
  }

  if (method === "GET" && pathname === "/api/v1/vendors/staff") return envelope({ members: state.staff });

  if (method === "POST" && pathname === "/api/v1/vendors/staff/invite") {
    if (role !== "VENDOR_OWNER") throw new Error("Mock permission denied: membership.manage");
    const payload = (body || {}) as Record<string, unknown>;
    const member = { membership_id: "mock-member-" + (state.staff.length + 1), user_id: "mock-user-" + (state.staff.length + 1), phone_number: String(payload.phone_number || ""), full_name: String(payload.full_name || ""), role: "VENDOR_STAFF", status: "INVITED" };
    state.staff.push(member);
    return envelope(member);
  }

  if (method === "PATCH" && /^\/api\/v1\/vendors\/staff\/[^/]+$/.test(pathname)) {
    if (role !== "VENDOR_OWNER") throw new Error("Mock permission denied: membership.manage");
    const id = pathname.split("/")[5];
    const member = state.staff.find((x) => x.membership_id === id);
    if (!member) throw new Error("Mock staff member not found");
    Object.assign(member, body || {});
    return envelope(member);
  }

  if (method === "GET" && /^\/api\/v1\/vendors\/staff\/[^/]+\/permissions$/.test(pathname)) {
    if (role !== "VENDOR_OWNER") throw new Error("Mock permission denied: membership.manage");
    const id = pathname.split("/")[5];
    return envelope(state.permissions[id] || {
      membership_id: id,
      full_name: "همکار",
      role: "VENDOR_STAFF",
      grantable_permissions: ["inventory.adjust", "inventory.scan", "order.fulfillment"],
      delegated_grants: [],
      effective_permissions: ["catalog.view", "inventory.view", "inventory.scan", "inventory.adjust", "price.view", "order.view", "order.fulfillment", "delivery.dispatch"],
    });
  }

  if (method === "POST" && /^\/api\/v1\/vendors\/staff\/[^/]+\/permissions$/.test(pathname)) {
    if (role !== "VENDOR_OWNER") throw new Error("Mock permission denied: membership.manage");
    const id = pathname.split("/")[5];
    const current = state.permissions[id] || {
      membership_id: id,
      full_name: "همکار",
      role: "VENDOR_STAFF" as MockRole,
      grantable_permissions: ["inventory.adjust", "inventory.scan", "order.fulfillment"],
      delegated_grants: [],
      effective_permissions: ["catalog.view", "inventory.view", "inventory.scan", "inventory.adjust", "price.view", "order.view", "order.fulfillment", "delivery.dispatch"],
    };
    const permissionKey = String((body as Record<string, unknown>)?.permission_key || "");
    current.delegated_grants.push({ id: "mock-grant-" + Date.now(), permission_key: permissionKey, status: "GRANTED", granted_at: new Date().toISOString() });
    current.effective_permissions = Array.from(new Set([...current.effective_permissions, permissionKey]));
    state.permissions[id] = current;
    return envelope(current);
  }

  if (method === "POST" && /^\/api\/v1\/vendors\/staff\/[^/]+\/permissions\/[^/]+\/revoke$/.test(pathname)) {
    if (role !== "VENDOR_OWNER") throw new Error("Mock permission denied: membership.manage");
    const parts = pathname.split("/");
    const id = parts[5];
    const permission = decodeURIComponent(parts[7]);
    const current = state.permissions[id];
    if (current) {
      current.delegated_grants = current.delegated_grants.map((g) => String(g.permission_key) === permission ? { ...g, status: "REVOKED", revoked_at: new Date().toISOString() } : g);
      current.effective_permissions = current.effective_permissions.filter((p) => p !== permission);
    }
    return envelope(current || { membership_id: id });
  }

  if (method === "GET" && pathname === "/api/v1/storefront/vendors") return envelope({ vendors: [state.storefrontVendor] });
  if (method === "GET" && /^\/api\/v1\/storefront\/vendors\/[^/]+\/products$/.test(pathname)) return envelope({ items: state.storefrontProducts, total: state.storefrontProducts.length });

  if (method === "GET" && pathname === "/api/v1/catalog/barcode/lookup") {
    const value = url.searchParams.get("barcode") || "";
    return envelope(state.barcodeMap[value] || { match_type: "NO_MATCH", confidence_score: 0, product: null, candidate_id: null, vendor_product_id: null });
  }

  if (method === "POST" && pathname === "/api/v1/products/match-barcode") {
    const payload = (body || {}) as Record<string, unknown>;
    const value = String(payload.barcode || payload.raw_barcode || "");
    const result = state.barcodeMap[value] || { match_type: "NO_MATCH", confidence_score: 0, product: null, candidate_id: null, vendor_product_id: null };
    if (payload.create_candidate && result.match_type === "NO_MATCH" && String(payload.proposed_title || "").trim()) {
      const candidateId = "mock-candidate-" + (state.candidates.length + 1);
      state.candidates.push({ id: candidateId, barcode: value, proposed_title: String(payload.proposed_title), proposed_brand: payload.proposed_brand || null, vendor_sku: payload.vendor_sku || null, status: "PENDING_REVIEW" });
      return envelope({ ...result, candidate_id: candidateId });
    }
    return envelope(result);
  }

  if (method === "POST" && pathname === "/api/v1/product-candidates") {
    const payload = (body || {}) as Record<string, unknown>;
    const candidateId = "mock-candidate-" + (state.candidates.length + 1);
    const candidate = { id: candidateId, barcode: payload.barcode || null, proposed_title: payload.proposed_title, proposed_brand: payload.proposed_brand || null, vendor_sku: payload.vendor_sku || null, status: "PENDING_REVIEW" };
    state.candidates.push(candidate);
    return envelope({ candidate_id: candidateId, ...candidate });
  }

  if (method === "POST" && pathname === "/api/v1/vendors/inventory/continuous-scan") {
    const payload = (body || {}) as Record<string, unknown>;
    return envelope({ accepted: true, session_id: payload.session_id || "mock-scan-session", verification_source: "BARCODE_SCAN" });
  }

  if (method === "GET" && pathname === "/api/v1/support/cases") return envelope({ cases: state.supportCases.map(({ messages, ...row }) => row), limit: 50, offset: 0 });
  if (method === "POST" && pathname === "/api/v1/support/cases") {
    const payload = (body || {}) as Record<string, unknown>;
    const item = { id: "mock-case-" + (state.supportCases.length + 1), subject: payload.subject, case_type: payload.case_type || "GENERAL", priority: payload.priority || "NORMAL", status: "OPEN", related_order_id: payload.related_order_id || null, created_at: new Date().toISOString(), messages: [] };
    state.supportCases.push(item);
    return envelope(item);
  }

  if (method === "GET" && /^\/api\/v1\/support\/cases\/[^/]+$/.test(pathname)) {
    const id = pathname.split("/")[5];
    const item = state.supportCases.find((x) => x.id === id);
    if (!item) throw new Error("Mock support case not found");
    return envelope(item);
  }

  if (method === "POST" && /^\/api\/v1\/support\/cases\/[^/]+\/messages$/.test(pathname)) {
    const id = pathname.split("/")[5];
    const item = state.supportCases.find((x) => x.id === id);
    if (!item) throw new Error("Mock support case not found");
    const payload = (body || {}) as Record<string, unknown>;
    const message = { id: "mock-message-" + Date.now(), body: payload.body || payload.message || "", sender_role: role, created_at: new Date().toISOString() };
    ((item.messages as Array<Record<string, unknown>>) ||= []).push(message);
    return envelope(message);
  }

  if (method === "GET" && pathname === "/api/v1/profile") return envelope({
    user_profile: { display_name: role === "VENDOR_OWNER" ? "مالک بنکداری" : "انبار و سفارش", phone_number: role === "VENDOR_OWNER" ? "+989160000001" : "+989160000002", email: null, timezone: "Asia/Tehran" },
    membership: { id: role === "VENDOR_OWNER" ? "mock-member-owner" : "mock-member-staff", role, status: "ACTIVE" },
    membership_profile: {},
    persona_profile: {},
  });

  if (method === "GET" && pathname === "/api/v1/profile/context") return envelope({ organization_id: "mock-vendor-org", organization_type: "VENDOR", role });

  if (method === "GET" && pathname === "/api/v1/notifications") return envelope({ notifications: [], limit: 50, offset: 0 });
  if (method === "GET" && pathname === "/api/v1/notifications/preferences") return envelope({ push_enabled: true, sms_enabled: true, email_enabled: false });
  if (method === "PATCH" && pathname === "/api/v1/notifications/preferences") return envelope(body || {});

  if (method === "GET" && pathname === "/api/v1/auth/sessions/current") return envelope({ id: "mock-session", status: "ACTIVE", expires_at: new Date(Date.now() + 3600_000).toISOString() });

  if (method === "GET" && pathname === "/healthz") return envelope({ status: "ok", mode: "mock" });
  if (method === "GET" && pathname === "/readyz") return envelope({ status: "ready", mode: "mock" });
  if (method === "GET" && pathname === "/api/v1/categories") return envelope({ categories: [] });

  return notFound(method + " " + path);
}
