import { NextRequest, NextResponse } from "next/server";

type Role =
  | "ADMIN_SUPER"
  | "OPS_AGENT"
  | "FIELD_ACTIVATOR"
  | "VENDOR_OWNER"
  | "VENDOR_STAFF"
  | "RETAILER_OWNER"
  | "RETAILER_STAFF";

const DEFAULT_ROLE: Role = "RETAILER_OWNER";

const products = [
  {
    id: "prd-001",
    master_sku: "POL-COLA-330",
    canonical_name_fa: "نوشابه کولا ۳۳۰ میلی‌لیتری",
    base_unit: "عدد",
    default_pack_unit: "کارتن",
    default_pack_quantity: 24,
    net_weight_grams: 330,
    volume_ml: 330,
    description: "نوشابه گازدار برای تست کاتالوگ، قیمت و موجودی.",
    is_active: true,
    is_verified: true,
    brand_id: "brand-001",
    brand_name: "POL Demo",
    category_id: "cat-001",
    category_name: "نوشیدنی",
    subcategory_id: "sub-001",
    subcategory_name: "نوشابه",
  },
  {
    id: "prd-002",
    master_sku: "POL-WATER-1500",
    canonical_name_fa: "آب معدنی ۱.۵ لیتری",
    base_unit: "بطری",
    default_pack_unit: "بسته",
    default_pack_quantity: 6,
    volume_ml: 1500,
    description: "سناریوی عادی با بسته‌بندی چندتایی.",
    is_active: true,
    is_verified: true,
    brand_id: "brand-002",
    brand_name: "آب‌گستر",
    category_id: "cat-001",
    category_name: "نوشیدنی",
    subcategory_id: "sub-002",
    subcategory_name: "آب",
  },
  {
    id: "prd-003",
    master_sku: "POL-CHIPS-60",
    canonical_name_fa: "چیپس ساده ۶۰ گرمی",
    base_unit: "بسته",
    default_pack_unit: "کارتن",
    default_pack_quantity: 20,
    net_weight_grams: 60,
    description: "سناریوی موجودی کم.",
    is_active: true,
    is_verified: false,
    brand_id: "brand-003",
    brand_name: "اسنک‌نو",
    category_id: "cat-002",
    category_name: "تنقلات",
    subcategory_id: "sub-003",
    subcategory_name: "چیپس",
  },
];

const vendors = [
  {
    id: "ven-001",
    business_name: "پخش آزمایشی اهواز",
    status: "ACTIVE",
    city: "اهواز",
    phone_number: "061-00000001",
  },
  {
    id: "ven-002",
    business_name: "توزیع جنوب کارون",
    status: "ACTIVE",
    city: "اهواز",
    phone_number: "061-00000002",
  },
  {
    id: "ven-003",
    business_name: "بازرگانی نمونه خوزستان",
    status: "PENDING",
    city: "اهواز",
    phone_number: "061-00000003",
  },
];

const offers = [
  {
    vendor_product_id: "vp-001",
    vendor_id: "ven-001",
    vendor_sku: "AHV-330-01",
    packaging_unit: "کارتن",
    pack_quantity: 24,
    sales_unit: "کارتن",
    physical_quantity: 120,
    available_quantity: 118,
    moq: 2,
    freshness_status: "FRESH",
    price_toman: 168000,
    business_name: "پخش آزمایشی اهواز",
    vendor_status: "ACTIVE",
  },
  {
    vendor_product_id: "vp-002",
    vendor_id: "ven-002",
    vendor_sku: "KRN-330-09",
    packaging_unit: "کارتن",
    pack_quantity: 24,
    sales_unit: "کارتن",
    physical_quantity: 74,
    available_quantity: 60,
    moq: 1,
    freshness_status: "FRESH",
    price_toman: 171000,
    business_name: "توزیع جنوب کارون",
    vendor_status: "ACTIVE",
  },
];

const orderBase = {
  id: "ord-001",
  order_number: "POL-2026-0001",
  order_status: "PENDING",
  group_status: "PENDING",
  customer_name: "فروشگاه نمونه رضا",
  vendor_name: "پخش آزمایشی اهواز",
  vendor_id: "ven-001",
  retailer_id: "ret-001",
  total_amount_toman: 4280000,
  subtotal_toman: 4100000,
  delivery_cost_toman: 180000,
  item_count: 4,
  created_at: "2026-09-27T09:15:00Z",
  updated_at: "2026-09-27T09:30:00Z",
};

const orders = [
  orderBase,
  {
    ...orderBase,
    id: "ord-002",
    order_number: "POL-2026-0002",
    order_status: "ACCEPTED",
    group_status: "PARTIALLY_ACCEPTED",
    vendor_id: "ven-002",
    vendor_name: "توزیع جنوب کارون",
    total_amount_toman: 2860000,
    subtotal_toman: 2710000,
    delivery_cost_toman: 150000,
    item_count: 3,
  },
  {
    ...orderBase,
    id: "ord-003",
    order_number: "POL-2026-0003",
    order_status: "PREPARING",
    group_status: "PREPARING",
    vendor_id: "ven-001",
    total_amount_toman: 6120000,
    subtotal_toman: 5920000,
    delivery_cost_toman: 200000,
    item_count: 7,
  },
  {
    ...orderBase,
    id: "ord-004",
    order_number: "POL-2026-0004",
    order_status: "READY",
    group_status: "READY",
    vendor_id: "ven-002",
    total_amount_toman: 1980000,
    subtotal_toman: 1860000,
    delivery_cost_toman: 120000,
    item_count: 2,
  },
  {
    ...orderBase,
    id: "ord-005",
    order_number: "POL-2026-0005",
    order_status: "DELIVERED",
    group_status: "DELIVERED",
    vendor_id: "ven-001",
    total_amount_toman: 8540000,
    subtotal_toman: 8240000,
    delivery_cost_toman: 300000,
    item_count: 9,
  },
];

const orderItems = [
  {
    id: "item-001",
    product_name_snapshot: products[0].canonical_name_fa,
    brand_name_snapshot: products[0].brand_name,
    ordered_quantity: 10,
    accepted_quantity: 10,
    packaging_unit_snapshot: "کارتن",
    pack_quantity_snapshot: 24,
    total_line_amount_toman: 1680000,
  },
  {
    id: "item-002",
    product_name_snapshot: products[1].canonical_name_fa,
    brand_name_snapshot: products[1].brand_name,
    ordered_quantity: 6,
    accepted_quantity: 5,
    packaging_unit_snapshot: "بسته",
    pack_quantity_snapshot: 6,
    total_line_amount_toman: 1026000,
  },
];

const timeline = [
  {
    id: "evt-001",
    event_type: "ORDER_CREATED",
    from_status: null,
    to_status: "PENDING",
    created_at: "2026-09-27T09:15:00Z",
    event_data: {},
  },
  {
    id: "evt-002",
    event_type: "ORDER_PARTIAL_ACCEPTANCE_PROPOSED",
    from_status: "PENDING",
    to_status: "PARTIALLY_ACCEPTED",
    created_at: "2026-09-27T10:00:00Z",
    event_data: { proposal_id: "prop-001" },
  },
];

const notifications = [
  {
    id: "notif-001",
    event_name: "ORDER_CREATED",
    title: "سفارش جدید ثبت شد",
    body: "سفارش POL-2026-0001 در صف بررسی قرار گرفت.",
    priority: "NORMAL",
    created_at: "2026-09-27T09:16:00Z",
  },
  {
    id: "notif-002",
    event_name: "LOW_STOCK",
    title: "موجودی پایین",
    body: "موجودی یکی از کالاهای اصلی رو به کاهش است.",
    priority: "HIGH",
    created_at: "2026-09-27T08:20:00Z",
  },
];

const preferences = [
  { user_id: "usr-demo", category: "ORDER_CREATED", push_enabled: true, sms_enabled: false },
  { user_id: "usr-demo", category: "ORDER_STATUS_CHANGED", push_enabled: true, sms_enabled: true },
  { user_id: "usr-demo", category: "LOW_STOCK", push_enabled: true, sms_enabled: false },
];

const invoices = [
  {
    id: "inv-001",
    invoice_number: "INV-2026-0001",
    order_id: "ord-001",
    status: "ISSUED",
    total_amount_toman: 4280000,
    created_at: "2026-09-27T10:00:00Z",
  },
  {
    id: "inv-002",
    invoice_number: "INV-2026-0002",
    order_id: "ord-002",
    status: "PAID",
    total_amount_toman: 2860000,
    created_at: "2026-09-26T12:00:00Z",
  },
];

const settlements = [
  {
    id: "set-001",
    settlement_number: "SET-2026-001",
    vendor_id: "ven-001",
    status: "OPEN",
    net_amount_toman: 12840000,
    created_at: "2026-09-27T12:00:00Z",
  },
  {
    id: "set-002",
    settlement_number: "SET-2026-002",
    vendor_id: "ven-002",
    status: "SETTLED",
    net_amount_toman: 9620000,
    created_at: "2026-09-26T12:00:00Z",
  },
];

const cases = [
  {
    id: "case-001",
    case_number: "SUP-2026-0001",
    case_type: "ORDER",
    priority: "HIGH",
    status: "OPEN",
    subject: "پیگیری تأخیر سفارش",
    order_id: "ord-003",
    created_at: "2026-09-27T11:00:00Z",
  },
  {
    id: "case-002",
    case_number: "SUP-2026-0002",
    case_type: "PAYMENT",
    priority: "NORMAL",
    status: "IN_PROGRESS",
    subject: "بررسی سند پرداخت",
    order_id: "ord-002",
    created_at: "2026-09-26T13:00:00Z",
  },
];

const reconciliationCases = [
  {
    id: "recon-001",
    payment_id: "pay-001",
    status: "OPEN",
    expected_amount_toman: 4280000,
    received_amount_toman: 4100000,
    discrepancy_amount_toman: 180000,
    created_at: "2026-09-27T12:20:00Z",
  },
  {
    id: "recon-002",
    payment_id: "pay-002",
    status: "RESOLVED",
    expected_amount_toman: 2860000,
    received_amount_toman: 2860000,
    discrepancy_amount_toman: 0,
    created_at: "2026-09-26T14:20:00Z",
  },
];

const tasks = [
  {
    id: "task-001",
    task_type: "RETAILER_ACTIVATION",
    assigned_to_user_id: "usr-field-01",
    target_organization_id: "org-ret-001",
    status: "PENDING",
    notes: "بازدید اولیه فروشگاه و تکمیل مشخصات.",
    due_date: "2026-09-29T12:00:00Z",
    completed_at: null,
    created_at: "2026-09-27T07:00:00Z",
    updated_at: "2026-09-27T07:00:00Z",
  },
  {
    id: "task-002",
    task_type: "FOLLOW_UP",
    assigned_to_user_id: "usr-field-01",
    target_organization_id: "org-ret-002",
    status: "IN_PROGRESS",
    notes: "نیاز به تماس مجدد برای تأیید سفارش.",
    due_date: "2026-09-30T12:00:00Z",
    completed_at: null,
    created_at: "2026-09-26T08:00:00Z",
    updated_at: "2026-09-28T06:00:00Z",
  },
];

const profileByRole: Record<Role, {
  id: string;
  user_id: string;
  display_name: string;
  email: string;
  preferred_language: string;
  timezone: string;
  phone_number: string;
  profile_status: string;
  is_active: boolean;
}> = {
  ADMIN_SUPER: { id: "prof-admin", user_id: "usr-admin", display_name: "مدیر سامانه", email: "admin@pol.qa", preferred_language: "fa", timezone: "Asia/Tehran", phone_number: "09120000001", profile_status: "COMPLETE", is_active: true },
  OPS_AGENT: { id: "prof-ops", user_id: "usr-ops", display_name: "کارشناس عملیات", email: "ops@pol.qa", preferred_language: "fa", timezone: "Asia/Tehran", phone_number: "09120000002", profile_status: "COMPLETE", is_active: true },
  FIELD_ACTIVATOR: { id: "prof-field", user_id: "usr-field-01", display_name: "فعال‌ساز میدانی", email: "field@pol.qa", preferred_language: "fa", timezone: "Asia/Tehran", phone_number: "09120000003", profile_status: "COMPLETE", is_active: true },
  VENDOR_OWNER: { id: "prof-vendor", user_id: "usr-vendor", display_name: "مالک پخش آزمایشی", email: "vendor@pol.qa", preferred_language: "fa", timezone: "Asia/Tehran", phone_number: "09120000004", profile_status: "COMPLETE", is_active: true },
  VENDOR_STAFF: { id: "prof-vendor-staff", user_id: "usr-vendor-staff", display_name: "اپراتور فروشنده", email: "vendor.staff@pol.qa", preferred_language: "fa", timezone: "Asia/Tehran", phone_number: "09120000005", profile_status: "COMPLETE", is_active: true },
  RETAILER_OWNER: { id: "prof-retailer", user_id: "usr-retailer", display_name: "مالک فروشگاه نمونه", email: "retailer@pol.qa", preferred_language: "fa", timezone: "Asia/Tehran", phone_number: "09120000006", profile_status: "COMPLETE", is_active: true },
  RETAILER_STAFF: { id: "prof-retailer-staff", user_id: "usr-retailer-staff", display_name: "اپراتور فروشگاه", email: "retailer.staff@pol.qa", preferred_language: "fa", timezone: "Asia/Tehran", phone_number: "09120000007", profile_status: "COMPLETE", is_active: true },
};

function roleOf(request: NextRequest): Role {
  const raw = request.cookies.get("pol.qa.role")?.value ?? request.cookies.get("pol.role")?.value;
  return Object.prototype.hasOwnProperty.call(profileByRole, raw) ? (raw as Role) : DEFAULT_ROLE;
}

function repeat<T>(rows: T[], count: number): T[] {
  if (count <= rows.length) return rows;
  return Array.from({ length: count }, (_, i) => {
    const source = rows[i % rows.length];
    if (source && typeof source === "object") {
      return { ...(source as Record<string, unknown>), id: `${(source as Record<string, unknown>).id ?? "row"}-${i + 1}` } as T;
    }
    return source;
  });
}

function datasetRows<T>(request: NextRequest, rows: T[]): T[] {
  const size = request.cookies.get("pol.qa.dataset")?.value === "large" ? 50 : 0;
  return size ? repeat(rows, size) : rows;
}

function envelope(data: unknown, status = 200) {
  return NextResponse.json({ success: true, data }, { status });
}

function failEnvelope(code: string, message: string, status: number) {
  return NextResponse.json(
    {
      success: false,
      error: { code, message, details: {}, timestamp: new Date().toISOString() },
    },
    { status },
  );
}

async function bodyOf(request: NextRequest): Promise<Record<string, unknown>> {
  try {
    const body = await request.json();
    return body && typeof body === "object" ? (body as Record<string, unknown>) : {};
  } catch {
    return {};
  }
}

async function handle(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const method = request.method;
  const key = path.join("/");
  const qaFail = request.cookies.get("pol.qa.fail")?.value ?? "none";
  const delay = Math.min(Number(request.cookies.get("pol.qa.delay")?.value ?? 0) || 0, 5000);

  if (delay > 0) {
    await new Promise((resolve) => setTimeout(resolve, delay));
  }

  if (qaFail === "500" || (qaFail === "mutations" && method !== "GET")) {
    return failEnvelope("QA_INJECTED_ERROR", "خطای آزمایشی توسط QA Lab تزریق شده است.", 500);
  }

  if (request.cookies.get("pol.qa.unauthorized")?.value === "1" && !key.startsWith("auth/")) {
    return failEnvelope("UNAUTHORIZED", "توکن آزمایشی نامعتبر است.", 401);
  }

  const role = roleOf(request);
  const profile = profileByRole[role];
  const query = request.nextUrl.searchParams;

  if (key === "auth/request-otp" && method === "POST") {
    return envelope({
      otp_request_id: "otp-qa-001",
      expires_in_seconds: 120,
      resend_interval_seconds: 30,
    });
  }

  if (key === "auth/verify-otp" && method === "POST") {
    const requestedRole = request.cookies.get("pol.qa.role")?.value;
    const selectedRole = Object.prototype.hasOwnProperty.call(profileByRole, requestedRole)
      ? (requestedRole as Role)
      : role;
    return envelope({
      access_token: `qa-access-${selectedRole}`,
      refresh_token: `qa-refresh-${selectedRole}`,
      token_type: "bearer",
      expires_in: 900,
      user: { user_id: profileByRole[selectedRole].user_id, mobile_number: profileByRole[selectedRole].phone_number },
      role: selectedRole,
      organization_id: selectedRole.includes("RETAILER") ? "org-ret-001" : selectedRole.includes("VENDOR") ? "org-ven-001" : "org-pol-001",
      profile: { role: selectedRole, organization_id: selectedRole.includes("RETAILER") ? "org-ret-001" : selectedRole.includes("VENDOR") ? "org-ven-001" : "org-pol-001" },
      current_organization: { id: selectedRole.includes("RETAILER") ? "org-ret-001" : selectedRole.includes("VENDOR") ? "org-ven-001" : "org-pol-001", role: selectedRole },
    });
  }

  if (key === "auth/refresh" && method === "POST") {
    return envelope({ access_token: `qa-refresh-access-${role}`, refresh_token: `qa-refresh-${role}`, token_type: "bearer", expires_in: 900 });
  }

  if (key === "auth/switch-organization" && method === "POST") {
    return envelope({ organization_id: "org-pol-001", role });
  }

  if (key === "auth/sessions/current" && method === "DELETE") return envelope({ revoked: true });
  if (key.startsWith("auth/sessions/") && method === "DELETE") return envelope({ revoked: true });
  if (key === "auth/logout-all" && method === "POST") return envelope({ revoked: true });

  if (key === "profile" && method === "GET") return envelope(profile);
  if (key === "profile/context" && method === "GET") {
    return envelope({
      user_profile: profile,
      membership: {
        id: "mem-qa-001",
        user_id: profile.user_id,
        organization_id: role.includes("RETAILER") ? "org-ret-001" : role.includes("VENDOR") ? "org-ven-001" : "org-pol-001",
        role,
        status: "ACTIVE",
        organization_name: role.includes("RETAILER") ? "فروشگاه نمونه" : role.includes("VENDOR") ? "پخش آزمایشی اهواز" : "POL Demo",
        org_type: role.includes("RETAILER") ? "RETAILER" : role.includes("VENDOR") ? "VENDOR" : "PLATFORM",
        organization_status: "ACTIVE",
      },
      membership_profile: { city: "اهواز", address: "سناریوی QA", completion_percent: 92 },
      persona_profile: { role, demo_mode: true },
    });
  }
  if (key === "profile/completion" && method === "GET") return envelope({ completion_percent: 92, missing_fields: [] });
  if (key === "profile" && method === "PUT") return envelope({ ...profile, ...(await bodyOf(request)), updated_at: "2026-09-28T08:00:00Z" });

  if (key === "notifications" && method === "GET") return envelope(datasetRows(request, notifications));
  if (key === "notifications/preferences" && method === "GET") return envelope(preferences);
  if (key === "notifications/preferences" && method === "PUT") return envelope({ updated: true });

  if (key === "catalog/categories" && method === "GET") {
    return envelope([
      { id: "cat-001", name: "نوشیدنی", slug: "drinks", children_count: 2 },
      { id: "cat-002", name: "تنقلات", slug: "snacks", children_count: 1 },
      { id: "cat-003", name: "لبنیات", slug: "dairy", children_count: 3 },
    ]);
  }

  if (key === "catalog/search" && method === "GET") {
    const q = query.get("q")?.trim().toLowerCase();
    const filtered = q ? products.filter((p) => `${p.canonical_name_fa} ${p.master_sku}`.toLowerCase().includes(q) || q === "ولو") : products;
    return envelope({ items: datasetRows(request, filtered), total: filtered.length, page: 1, page_size: 20 });
  }

  if (key === "search" && method === "GET") {
    const q = query.get("q")?.trim() ?? "";
    return envelope({ items: datasetRows(request, q ? products.filter((p) => p.canonical_name_fa.includes(q) || p.master_sku.includes(q)) : products), total: products.length });
  }

  if (key.startsWith("catalog/products/") && method === "GET") {
    const productId = path[2];
    if (path.length === 3) {
      return envelope(products.find((p) => p.id === productId) ?? products[0]);
    }
    if (path[3] === "vendors") return envelope(offers);
    if (path[3] === "compare-prices") return envelope(offers.map((o) => ({ vendor_product_id: o.vendor_product_id, business_name: o.business_name, price_toman: o.price_toman, available_quantity: o.available_quantity, moq: o.moq, pack_quantity: o.pack_quantity })));
    if (path[3] === "compare-inventory") return envelope(offers.map((o) => ({ vendor_product_id: o.vendor_product_id, business_name: o.business_name, available_quantity: o.available_quantity, physical_quantity: o.physical_quantity, reserved_quantity: (o.physical_quantity ?? 0) - (o.available_quantity ?? 0), moq: o.moq, price_toman: o.price_toman, freshness_status: o.freshness_status })));
  }

  if (key === "products/match-barcode" && method === "POST") {
    return envelope({ matched: true, product_id: "prd-001", master_sku: "POL-COLA-330", confidence: 0.99 });
  }

  if (key === "product-candidates" && method === "POST") {
    return envelope({ candidate_id: "candidate-qa-001", status: "PENDING" }, 201);
  }

  if (key === "storefront/vendors" && method === "GET") {
    return envelope({ items: datasetRows(request, vendors), total: vendors.length, page: 1, page_size: 20 });
  }
  if (key.startsWith("storefront/vendors/") && method === "GET") {
    const vendorId = path[2];
    const vendor = vendors.find((v) => v.id === vendorId) ?? vendors[0];
    if (path.length === 3) return envelope(vendor);
    if (path[3] === "products") return envelope(datasetRows(request, [{ ...products[0], vendor_id: vendor.id, vendor_name: vendor.business_name }, { ...products[1], vendor_id: vendor.id, vendor_name: vendor.business_name }]));
  }

  if (key === "baskets" && method === "POST") return envelope({ basket_id: "basket-qa-001", version: 1, status: "OPEN" }, 201);
  if (key.match(/^baskets\/[^/]+\/items$/) && method === "POST") {
    return envelope({ basket_id: path[1], version: 2, status: "OPEN" });
  }
  if (key.match(/^baskets\/[^/]+\/allocation-preview$/) && method === "POST") {
    return envelope({
      allocation_plan_id: "alloc-qa-001",
      strategy: "BALANCED_COST",
      vendor_count: 2,
      allocated_vendors: [
        { vendor_id: "ven-001", business_name: "پخش آزمایشی اهواز", subtotal_toman: 2200000, min_order_value_toman: 1500000, mov_satisfied: true, allocated_items_count: 2 },
        { vendor_id: "ven-002", business_name: "توزیع جنوب کارون", subtotal_toman: 1900000, min_order_value_toman: 1000000, mov_satisfied: true, allocated_items_count: 2 },
      ],
      summary: { total_items_requested: 4, total_items_allocated: 4, total_items_unfulfilled: 0, total_amount_toman: 4100000, estimated_delivery_cost_toman: 180000 },
      unfulfilled_items: [],
    });
  }

  if (key === "orders" && method === "GET") {
    const status = query.get("status");
    const filtered = status ? orders.filter((o) => o.order_status === status || o.group_status === status) : orders;
    const offset = Number(query.get("offset") ?? 0) || 0;
    const limit = Math.min(Number(query.get("limit") ?? 20) || 20, 100);
    return envelope({ items: datasetRows(request, filtered).slice(offset, offset + limit), total: filtered.length, offset, limit });
  }

  if (key === "orders" && method === "POST") {
    return envelope({
      order_group_id: "grp-qa-001",
      group_status: "PENDING",
      total_amount_toman: 4100000,
      child_orders: [
        { order_id: "ord-qa-001", vendor_id: "ven-001", order_status: "PENDING", subtotal_toman: 2200000 },
        { order_id: "ord-qa-002", vendor_id: "ven-002", order_status: "PENDING", subtotal_toman: 1900000 },
      ],
      idempotent_replay: false,
    }, 201);
  }

  if (key.startsWith("orders/group/") && method === "GET") {
    const groupId = path[2];
    if (path.length === 3) {
      return envelope({ id: groupId, order_group_id: groupId, group_status: "PARTIALLY_ACCEPTED", total_amount_toman: 6960000, child_order_count: 2, created_at: "2026-09-27T09:15:00Z" });
    }
    if (path[3] === "orders") return envelope(orders.slice(0, 2));
  }

  if (key.startsWith("orders/") && method === "GET") {
    const orderId = path[1] ?? "ord-001";
    const order = orders.find((o) => o.id === orderId) ?? orders[0];
    if (path.length === 2) return envelope({ ...order, payment_status: "PENDING", delivery_status: order.order_status === "DELIVERED" ? "DELIVERED" : "IN_TRANSIT", delivery_address: "اهواز، کیانپارس، خیابان نمونه، پلاک ۱۰" });
    if (path[2] === "items") return envelope(orderItems);
    if (path[2] === "timeline") return envelope(timeline);
    if (path[2] === "delivery") return envelope({
      id: "del-qa-001",
      order_id: order.id,
      vendor_id: order.vendor_id,
      delivery_status: order.order_status === "DELIVERED" ? "DELIVERED" : "IN_TRANSIT",
      driver_name: "راننده آزمایشی",
      vehicle_plate: "۱۲۳-۴۵-ب",
      driver_phone: "09121111111",
      dispatched_at: "2026-09-27T15:00:00Z",
      delivered_at: order.order_status === "DELIVERED" ? "2026-09-27T17:00:00Z" : null,
    });
    if (path[2] === "delivery/proof") return envelope({ proof_type: "OTP", receiver_name: "گیرنده نمونه", delivered_at: "2026-09-27T17:00:00Z" });
    if (path[2] === "returns") return envelope([{ id: "ret-001", order_id: order.id, status: "REQUESTED", reason: "DAMAGED", quantity: 1, created_at: "2026-09-27T18:00:00Z" }]);
    if (path[2] === "disputes") return envelope([{ id: "disp-001", order_id: order.id, status: "OPEN", claimed_amount_toman: 180000, description: "مغایرت مبلغ", created_at: "2026-09-27T18:30:00Z" }]);
    if (path[2] === "invoices") return envelope(invoices.filter((i) => i.order_id === order.id));
    if (path[2] === "delivery-exceptions") return envelope([{ id: "dex-001", order_id: order.id, status: "OPEN", code: "LATE", created_at: "2026-09-27T16:00:00Z" }]);
  }

  if (key.startsWith("orders/") && method === "POST") {
    const orderId = path[1] ?? "ord-001";
    const action = path[2] ?? "";
    const next: Record<string, string> = {
      accept: "ACCEPTED",
      preparing: "PREPARING",
      ready: "READY",
      dispatch: "DISPATCHED",
      deliver: "DELIVERED",
      reject: "REJECTED",
    };
    if (action === "partial-acceptance-proposals") return envelope({ proposal_id: "prop-qa-001", status: "PROPOSED" }, 201);
    if (action.includes("approve")) return envelope({ proposal_id: path[3], status: "APPROVED" });
    if (action.includes("decline")) return envelope({ proposal_id: path[3], status: "DECLINED" });
    if (next[action]) return envelope({ ...orders.find((o) => o.id === orderId) ?? orderBase, id: orderId, order_status: next[action], updated_at: "2026-09-28T08:00:00Z" });
    if (action === "returns") return envelope({ id: "ret-qa-001", order_id: orderId, status: "REQUESTED" }, 201);
    if (action === "disputes") return envelope({ id: "disp-qa-001", order_id: orderId, status: "OPEN" }, 201);
    if (action === "payments" && path[3] === "evidence") return envelope({ id: "pay-evidence-001", status: "SUBMITTED" }, 201);
    if (action === "payments" && path[3] === "verify") return envelope({ verified: true });
    if (action === "delivery-exceptions") return envelope({ id: "dex-qa-001", status: "OPEN" }, 201);
  }

  if (key.startsWith("orders/") && method === "PATCH") return envelope({ updated: true });
  if (key.startsWith("orders/delivery-exceptions/") && method === "PATCH") return envelope({ updated: true, status: "RESOLVED" });

  if (key === "support/cases" && method === "GET") return envelope({ cases: datasetRows(request, cases), total: cases.length });
  if (key === "support/cases" && method === "POST") return envelope({ ...cases[0], id: "case-qa-001", status: "OPEN" }, 201);
  if (key.startsWith("support/cases/") && method === "GET") return envelope({ ...cases[0], id: path[2], messages: [{ id: "msg-001", message_text: "سلام، این پیام برای تست گفتگوست.", sender_role: "OPS_AGENT", created_at: "2026-09-28T07:30:00Z" }] });
  if (key.match(/^support\/cases\/[^/]+\/messages$/) && method === "POST") return envelope({ id: "msg-qa-001", message_text: "پیام آزمایشی ثبت شد.", created_at: "2026-09-28T08:00:00Z" }, 201);
  if (key.startsWith("support/cases/") && method === "PATCH") return envelope({ ...cases[0], id: path[2], status: "IN_PROGRESS" });

  if (key === "invoices" && method === "GET") return envelope(datasetRows(request, invoices));
  if (key.startsWith("invoices/") && method === "GET") return envelope(invoices[0]);
  if (key === "vendors/settlements" && method === "GET") return envelope(datasetRows(request, settlements));
  if (key.startsWith("settlements/") && method === "GET") return envelope(settlements[0]);

  if (key === "finance/reconciliation" && method === "GET") return envelope({ cases: datasetRows(request, reconciliationCases), total: reconciliationCases.length });
  if (key.startsWith("finance/reconciliation/") && method === "GET") return envelope(reconciliationCases[0]);
  if (key.startsWith("finance/reconciliation/") && method === "PATCH") return envelope({ ...reconciliationCases[0], status: "RESOLVED" });

  if (key === "referrals" && method === "GET") return envelope([{ id: "ref-001", code: "AHVZ-001", status: "ACTIVE", created_at: "2026-09-27T10:00:00Z", attributed_orders: 3 }]);
  if (key === "referrals" && method === "POST") return envelope({ id: "ref-qa-001", code: "QA-NEW-001", status: "ACTIVE", created_at: "2026-09-28T08:00:00Z" }, 201);
  if (key.startsWith("referrals/") && method === "GET") return envelope({ id: path[1], code: "AHVZ-001", status: "ACTIVE" });
  if (key.startsWith("referrals/") && method === "POST") return envelope({ redeemed: true, id: path[1] });

  if (key === "field/tasks" && method === "GET") return envelope({ tasks: datasetRows(request, tasks), total: tasks.length });
  if (key === "field/tasks" && method === "POST") return envelope({ ...tasks[0], id: "task-qa-001" }, 201);
  if (key.startsWith("field/tasks/") && method === "GET") return envelope(tasks.find((t) => t.id === path[2]) ?? tasks[0]);
  if (key.startsWith("field/tasks/") && method === "PATCH") return envelope({ ...(tasks.find((t) => t.id === path[2]) ?? tasks[0]), ...(await bodyOf(request)), updated_at: "2026-09-28T08:00:00Z" });

  if (key === "catalog/vendors/products" && method === "GET") {
    return envelope({ products: datasetRows(request, offers.map((o, i) => ({
      id: o.vendor_product_id,
      vendor_product_id: o.vendor_product_id,
      vendor_id: o.vendor_id,
      product_id: products[i % products.length].id,
      product_name: products[i % products.length].canonical_name_fa,
      master_sku: products[i % products.length].master_sku,
      price_toman: o.price_toman,
      available_quantity: o.available_quantity,
      moq: o.moq,
      status: "ACTIVE",
    }))) });
  }
  if (key.match(/^catalog\/vendors\/products\/[^/]+$/) && method === "GET") return envelope(offers[0]);
  if (key.match(/^catalog\/vendors\/products\/[^/]+\/prices$/) && method === "GET") return envelope([{ id: "price-001", price_toman: 168000, valid_from: "2026-09-01T00:00:00Z", valid_to: null, status: "ACTIVE" }]);
  if (key.match(/^catalog\/vendors\/products\/[^/]+\/prices$/) && method === "POST") return envelope({ id: "price-qa-001", price_toman: 170000, status: "ACTIVE" }, 201);
  if (key.match(/^catalog\/vendors\/products\/[^/]+\/prices\/current$/) && method === "GET") return envelope({ price_toman: 168000, status: "ACTIVE", valid_from: "2026-09-01T00:00:00Z" });
  if (key.match(/^catalog\/vendors\/products\/[^/]+\/inventory$/) && (method === "GET" || method === "PATCH")) return envelope({ physical_quantity: 120, available_quantity: 118, reserved_quantity: 2, updated_at: "2026-09-28T08:00:00Z" });
  if (key === "inventory/daily" && method === "GET") return envelope({ date: query.get("date") ?? "2026-09-28", status: "PENDING", products: offers });
  if (key.startsWith("inventory/daily/") && method === "GET") return envelope({ date: path[2], status: "PENDING", products: offers });
  if (key.startsWith("inventory/daily/") && method === "POST") return envelope({ date: path[2], status: "CONFIRMED", confirmed_at: "2026-09-28T08:00:00Z" });

  if (key === "admin/audit-logs" && method === "GET") return envelope({ items: datasetRows(request, [
    { id: "audit-001", actor: "مدیر سامانه", action: "VIEW_ORDER", target_type: "ORDER", target_id: "ord-001", created_at: "2026-09-28T07:40:00Z" },
    { id: "audit-002", actor: "کارشناس عملیات", action: "UPDATE_CASE", target_type: "SUPPORT_CASE", target_id: "case-001", created_at: "2026-09-28T07:20:00Z" },
  ]), total: 2 });
  if (key === "admin/exceptions/dashboard" && method === "GET") return envelope({
    open_exceptions: 7,
    high_risk: 2,
    stale_orders: 3,
    support_cases: { total: 12, open_cases: 5 },
    reconciliation: { open: 2, total: 6 },
  });

  if (key === "admin/users" && method === "GET") return envelope({ users: [
    { id: "usr-001", display_name: "کاربر آزمایشی ۱", mobile_number: "09121111111", role: "RETAILER_OWNER", is_active: true, last_login_at: "2026-09-28T06:00:00Z" },
    { id: "usr-002", display_name: "کاربر آزمایشی ۲", mobile_number: "09122222222", role: "VENDOR_OWNER", is_active: true, last_login_at: "2026-09-27T10:00:00Z" },
  ] });
  if (key.match(/^admin\/users\/[^/]+\/status$/) && method === "PATCH") return envelope({ updated: true });
  if (key === "admin/organizations" && method === "GET") return envelope({ organizations: [
    { id: "org-ret-001", name: "فروشگاه نمونه", type: "RETAILER", status: "ACTIVE", city: "اهواز" },
    { id: "org-ven-001", name: "پخش آزمایشی اهواز", type: "VENDOR", status: "ACTIVE", city: "اهواز" },
  ] });
  if (key.match(/^admin\/organizations\/[^/]+\/status$/) && method === "PATCH") return envelope({ updated: true });
  if (key === "admin/product-candidates" && method === "GET") return envelope({ candidates: [
    { candidate_id: "candidate-001", barcode: "6260000000011", proposed_name: "کالای ناشناخته ۱", status: "PENDING", created_at: "2026-09-28T06:00:00Z" },
    { candidate_id: "candidate-002", barcode: "6260000000012", proposed_name: "کالای ناشناخته ۲", status: "NEEDS_REVIEW", created_at: "2026-09-27T15:00:00Z" },
  ] });
  if (key.startsWith("admin/product-candidates/") && method === "PATCH") return envelope({ updated: true, status: "APPROVED" });

  if (key === "ops/permissions" && method === "GET") return envelope({
    role,
    permissions: {
      "catalog.read": true,
      "catalog.write": role.includes("VENDOR") || role.includes("ADMIN") || role === "OPS_AGENT",
      "order.read": true,
      "order.write": !role.includes("RETAILER_STAFF"),
      "inventory.scan": role === "VENDOR_STAFF",
    },
  });

  if (key === "ops/analytics" && method === "GET") return envelope({
    kpis: [
      { key: "orders", label: "سفارش‌ها", value: 128, delta_percent: 8.4, period: "7d" },
      { key: "gmv", label: "GMV", value: 482000000, delta_percent: 12.1, period: "7d" },
      { key: "fill_rate", label: "Fill Rate", value: 94.2, delta_percent: 2.8, period: "7d" },
      { key: "support_sla", label: "SLA پشتیبانی", value: 91.5, delta_percent: -1.2, period: "7d" },
    ],
  });

  if (key === "ops/returns" && method === "GET") {
    return envelope({ returns: [{ id: "ret-ops-001", order_id: "ord-003", status: "REQUESTED", reason: "DAMAGED", quantity: 1, created_at: "2026-09-28T06:30:00Z" }] });
  }

  if (key === "admin/broadcasts" && method === "GET") return envelope({ items: [{ id: "bc-001", title: "اطلاع‌رسانی آزمایشی", status: "DRAFT", audience: "ALL" }], total: 1 });

  if (key === "healthz" && method === "GET") return envelope({ status: "ok", service: "POL-2.3-Vercel-QA", mode: "mock" });
  if (key === "readyz" && method === "GET") return envelope({ ready: true, dependencies: { mock_data: "ok" } });

  return failEnvelope("MOCK_NOT_MAPPED", `Mock API route برای ${method} /api/v1/${key} هنوز نگاشت نشده است.`, 404);
}

export async function GET(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  return handle(request, context);
}

export async function POST(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  return handle(request, context);
}

export async function PUT(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  return handle(request, context);
}

export async function PATCH(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  return handle(request, context);
}

export async function DELETE(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  return handle(request, context);
}
