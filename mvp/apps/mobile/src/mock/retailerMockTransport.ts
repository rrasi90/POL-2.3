type RetailerRole = "RETAILER_OWNER" | "RETAILER_STAFF";

type RetailerProduct = {
  id: string;
  master_sku: string;
  canonical_name_fa: string;
  brand_name: string;
  base_unit: string;
  default_pack_unit: string;
  default_pack_quantity: number;
  lowest_unit_price_toman: number;
};

type RetailerOrder = {
  id: string;
  order_number: string;
  order_status: string;
  dispute_status: string;
  total_amount_toman: number;
  created_at: string;
  delivery_address: string;
  retailer_id: string;
};

type BasketItem = RetailerProduct & {
  id: string;
  product_id: string;
  requested_quantity: number;
  requested_unit: string;
  pack_quantity: number;
};

type RetailBasket = {
  basket_id: string;
  version: number;
  status: "OPEN" | "CHECKED_OUT";
  items: BasketItem[];
};

type RetailOrderItem = {
  id: string;
  product_id: string;
  product_name_snapshot: string;
  brand_name_snapshot: string;
  packaging_unit_snapshot: string;
  pack_quantity_snapshot: number;
  ordered_quantity: number;
  accepted_quantity: number;
  delivered_quantity: number;
  unit_price_toman: number;
  total_line_amount_toman: number;
  fulfillment_status: string;
};

type RetailerMockState = {
  products: RetailerProduct[];
  vendor: Record<string, unknown>;
  vendorProducts: Array<Record<string, unknown>>;
  basket: RetailBasket | null;
  basketSequence: number;
  allocation: { id: string; basket_id: string; total: number; item_count: number } | null;
  orders: RetailerOrder[];
  orderItems: Record<string, RetailOrderItem[]>;
  timelines: Record<string, Array<Record<string, unknown>>>;
  deliveries: Record<string, Record<string, unknown>>;
  returns: Array<Record<string, unknown>>;
  disputes: Array<Record<string, unknown>>;
  invoices: Array<Record<string, unknown>>;
  idempotency: Record<string, Record<string, unknown>>;
  supportCases: Array<Record<string, unknown>>;
  profile: Record<string, unknown>;
};

const fixedNow = "2026-10-26T10:00:00.000Z";

const productSeed: RetailerProduct[] = [
  { id: "mock-product-1", master_sku: "POL-PRD-0001", canonical_name_fa: "نوشابه خانواده کلاسیک", brand_name: "آذرنوش", base_unit: "PIECE", default_pack_unit: "CARTON", default_pack_quantity: 6, lowest_unit_price_toman: 540000 },
  { id: "mock-product-2", master_sku: "POL-PRD-0002", canonical_name_fa: "چیپس نمکی خانواده", brand_name: "نمکین", base_unit: "PIECE", default_pack_unit: "CARTON", default_pack_quantity: 12, lowest_unit_price_toman: 310000 },
  { id: "mock-product-3", master_sku: "POL-PRD-0003", canonical_name_fa: "رب گوجه ۸۰۰ گرمی", brand_name: "سرخینه", base_unit: "PIECE", default_pack_unit: "CARTON", default_pack_quantity: 24, lowest_unit_price_toman: 1280000 },
  { id: "mock-product-4", master_sku: "POL-PRD-0004", canonical_name_fa: "آب معدنی ۱.۵ لیتری", brand_name: "آبگون", base_unit: "PIECE", default_pack_unit: "PACK", default_pack_quantity: 6, lowest_unit_price_toman: 198000 },
  { id: "mock-product-5", master_sku: "POL-PRD-0005", canonical_name_fa: "مایع ظرفشویی لیمویی", brand_name: "پاک‌آور", base_unit: "PIECE", default_pack_unit: "CARTON", default_pack_quantity: 12, lowest_unit_price_toman: 720000 },
];

function freshState(): RetailerMockState {
  const products = productSeed.map((p) => ({ ...p }));
  const deliveredOrder: RetailerOrder = {
    id: "mock-retailer-order-100",
    order_number: "POL-AHV-R-0100",
    order_status: "DELIVERED",
    dispute_status: "NONE",
    total_amount_toman: 4320000,
    created_at: "2026-10-20T08:00:00.000Z",
    delivery_address: "اهواز، کیانپارس، خیابان نمونه، پلاک ۱۲",
    retailer_id: "mock-retailer-org",
  };
  const submittedOrder: RetailerOrder = {
    id: "mock-retailer-order-101",
    order_number: "POL-AHV-R-0101",
    order_status: "SUBMITTED",
    dispute_status: "NONE",
    total_amount_toman: 540000,
    created_at: fixedNow,
    delivery_address: "اهواز، گلستان، خیابان نمونه، پلاک ۸",
    retailer_id: "mock-retailer-org",
  };
  return {
    products,
    vendor: {
      id: "mock-vendor",
      name: "بنکداری نمونه اهواز",
      display_name: "بنکداری نمونه اهواز",
      city: "اهواز",
      description: "ویترین مصنوعی برای آزمایش اپ خرده‌فروش",
      is_active: true,
      product_count: 4,
    },
    vendorProducts: [
      { id: "mock-vp-1", product_id: "mock-product-1", product_name: products[0].canonical_name_fa, name: products[0].canonical_name_fa, brand_name: products[0].brand_name, price_toman: 540000, stock_quantity: 96, packaging_unit: "CARTON", is_available: true },
      { id: "mock-vp-2", product_id: "mock-product-2", product_name: products[1].canonical_name_fa, name: products[1].canonical_name_fa, brand_name: products[1].brand_name, price_toman: 310000, stock_quantity: 22, packaging_unit: "CARTON", is_available: true },
      { id: "mock-vp-3", product_id: "mock-product-3", product_name: products[2].canonical_name_fa, name: products[2].canonical_name_fa, brand_name: products[2].brand_name, price_toman: 1280000, stock_quantity: 2, packaging_unit: "CARTON", is_available: false },
      { id: "mock-vp-4", product_id: "mock-product-4", product_name: products[3].canonical_name_fa, name: products[3].canonical_name_fa, brand_name: products[3].brand_name, price_toman: 198000, stock_quantity: 60, packaging_unit: "PACK", is_available: true },
    ],
    basket: null,
    basketSequence: 0,
    allocation: null,
    orders: [deliveredOrder, submittedOrder],
    orderItems: {
      [deliveredOrder.id]: [{
        id: "mock-retail-item-100-1",
        product_id: products[0].id,
        product_name_snapshot: products[0].canonical_name_fa,
        brand_name_snapshot: products[0].brand_name,
        packaging_unit_snapshot: "CARTON",
        pack_quantity_snapshot: 6,
        ordered_quantity: 8,
        accepted_quantity: 8,
        delivered_quantity: 8,
        unit_price_toman: 540000,
        total_line_amount_toman: 4320000,
        fulfillment_status: "DELIVERED",
      }],
      [submittedOrder.id]: [{
        id: "mock-retail-item-101-1",
        product_id: products[0].id,
        product_name_snapshot: products[0].canonical_name_fa,
        brand_name_snapshot: products[0].brand_name,
        packaging_unit_snapshot: "CARTON",
        pack_quantity_snapshot: 6,
        ordered_quantity: 1,
        accepted_quantity: 1,
        delivered_quantity: 0,
        unit_price_toman: 540000,
        total_line_amount_toman: 540000,
        fulfillment_status: "PENDING",
      }],
    },
    timelines: {
      [deliveredOrder.id]: [
        { id: "mock-event-100-1", event_type: "ORDER_SUBMITTED", from_status: null, to_status: "SUBMITTED", created_at: "2026-10-20T08:00:00.000Z" },
        { id: "mock-event-100-2", event_type: "ORDER_DELIVERED", from_status: "DISPATCHED", to_status: "DELIVERED", created_at: "2026-10-20T12:00:00.000Z" },
      ],
      [submittedOrder.id]: [
        { id: "mock-event-101-1", event_type: "ORDER_SUBMITTED", from_status: null, to_status: "SUBMITTED", created_at: fixedNow },
      ],
    },
    deliveries: {
      [deliveredOrder.id]: { delivery_status: "DELIVERED", delivered_at: "2026-10-20T12:00:00.000Z" },
      [submittedOrder.id]: { delivery_status: "PENDING" },
    },
    returns: [],
    disputes: [],
    invoices: [
      { id: "mock-retail-invoice-100", invoice_number: "INV-AHV-R-0100", order_id: deliveredOrder.id, status: "ISSUED", total_amount_toman: 4320000, issued_at: "2026-10-20T12:00:00.000Z" },
    ],
    idempotency: {},
    supportCases: [],
    profile: {
      user_profile: { display_name: "مدیر فروشگاه نمونه", phone_number: "+989161110003", email: null, timezone: "Asia/Tehran" },
      membership: { id: "mock-retailer-member-owner", role: "RETAILER_OWNER", status: "ACTIVE", organization_name: "سوپرمارکت نمونه", organization_id: "mock-retailer-org" },
      membership_profile: {},
      persona_profile: {},
    },
  };
}

let state = freshState();

export function resetRetailerMockState(): void {
  state = freshState();
}

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function envelope<T>(value: T): T {
  return clone(value);
}

function bad(message: string): never {
  throw new Error(message);
}

function findOrder(id: string): RetailerOrder {
  const order = state.orders.find((row) => row.id === id);
  if (!order) return bad("Mock retailer order not found");
  return order;
}

function rowsOf<T extends Record<string, unknown>>(data: unknown, key: string): T[] {
  if (!data || typeof data !== "object") return [];
  const value = (data as Record<string, unknown>)[key];
  return Array.isArray(value) ? value as T[] : [];
}

export async function mockRetailerRequest<T>(
  method: string,
  path: string,
  body?: unknown,
  headers?: Record<string, string>,
): Promise<T> {
  const url = new URL("http://mock.local" + path);
  const pathname = url.pathname;
  const payload = (body && typeof body === "object" ? body : {}) as Record<string, unknown>;

  if (method === "POST" && pathname === "/api/v1/auth/request-otp") {
    return envelope({ otp_request_id: "mock-retailer-otp", expires_in_seconds: 120, resend_interval_seconds: 60 }) as T;
  }
  if (method === "POST" && pathname === "/api/v1/auth/verify-otp") {
    const phone = String(payload.mobile_number || "");
    const otp = String(payload.otp_code || "");
    if (!/^\+?[1-9]\d{7,14}$/.test(phone) || !/^\d{6}$/.test(otp)) {
      return bad("Mock OTP must contain an E.164 phone and 6 digits.");
    }
    const role: RetailerRole = phone.endsWith("0004") ? "RETAILER_STAFF" : "RETAILER_OWNER";
    const token = role === "RETAILER_STAFF" ? "mock-retailer-staff-token" : "mock-retailer-owner-token";
    return envelope({ access_token: token, refresh_token: token + "-refresh", role, current_organization: { id: "mock-retailer-org", role } }) as T;
  }

  if (method === "GET" && pathname === "/api/v1/catalog/search") {
    const q = (url.searchParams.get("q") || "").trim().toLocaleLowerCase();
    if (!q) return bad("Mock catalog search requires a query.");
    const matched = state.products.filter((p) =>
      [p.canonical_name_fa, p.brand_name, p.master_sku].some((v) => v.toLocaleLowerCase().includes(q))
      || q.length < 3
    );
    return envelope({ items: matched, query: url.searchParams.get("q"), total: matched.length }) as T;
  }

  if (method === "GET" && pathname === "/api/v1/catalog/categories") {
    return envelope({ categories: [
      { id: "mock-category-food", name_fa: "مواد غذایی", slug: "food" },
      { id: "mock-category-drinks", name_fa: "نوشیدنی‌ها", slug: "drinks" },
      { id: "mock-category-home", name_fa: "شوینده و نظافت", slug: "home-care" },
    ] }) as T;
  }
  if (method === "GET" && pathname === "/api/v1/categories") {
    return envelope({ categories: [
      { id: "mock-category-food", name_fa: "مواد غذایی", slug: "food" },
      { id: "mock-category-drinks", name_fa: "نوشیدنی‌ها", slug: "drinks" },
    ] }) as T;
  }

  if (method === "POST" && pathname === "/api/v1/baskets") {
    state.basketSequence += 1;
    const id = "mock-retailer-basket-" + state.basketSequence;
    state.basket = { basket_id: id, version: 1, status: "OPEN", items: [] };
    state.allocation = null;
    return envelope({ basket_id: id, version: 1 }) as T;
  }

  if (method === "GET" && pathname === "/api/v1/baskets/current") {
    if (!state.basket) {
      return envelope({ basket_id: null, version: 0, status: "EMPTY", items: [] }) as T;
    }
    return envelope(state.basket) as T;
  }

  const addItem = pathname.match(/^\/api\/v1\/baskets\/([^/]+)\/items$/);
  if (method === "POST" && addItem) {
    if (!state.basket || state.basket.basket_id !== addItem[1] || state.basket.status !== "OPEN") {
      return bad("Mock basket not found or closed.");
    }
    const productId = String(payload.product_id || "");
    const product = state.products.find((x) => x.id === productId);
    if (!product) return bad("Mock product not found.");
    const quantity = Number(payload.requested_quantity);
    const packQuantity = Number(payload.pack_quantity ?? product.default_pack_quantity);
    const expectedVersion = Number(payload.expected_version);
    if (!Number.isInteger(quantity) || quantity < 1 || !Number.isInteger(packQuantity) || packQuantity < 1) {
      return bad("Mock basket quantity and pack quantity must be positive integers.");
    }
    if (expectedVersion !== state.basket.version) {
      return bad("Mock basket version conflict.");
    }
    const existing = state.basket.items.find((x) => x.product_id === productId);
    if (existing) {
      existing.requested_quantity += quantity;
      existing.pack_quantity = packQuantity;
    } else {
      state.basket.items.push({
        ...product,
        id: "mock-retail-basket-item-" + (state.basket.items.length + 1),
        product_id: productId,
        requested_quantity: quantity,
        requested_unit: product.default_pack_unit,
        pack_quantity: packQuantity,
      });
    }
    state.basket.version += 1;
    state.allocation = null;
    return envelope({ basket_id: state.basket.basket_id, version: state.basket.version }) as T;
  }

  const allocationPreview = pathname.match(/^\/api\/v1\/baskets\/([^/]+)\/allocation-preview$/);
  if (method === "POST" && allocationPreview) {
    if (!state.basket || state.basket.basket_id !== allocationPreview[1] || state.basket.status !== "OPEN") {
      return bad("Mock basket not found or closed.");
    }
    if (!state.basket.items.length) return bad("Mock basket is empty.");
    const total = state.basket.items.reduce((sum, item) => sum + item.requested_quantity * item.lowest_unit_price_toman, 0);
    state.allocation = { id: "mock-retail-allocation-" + state.basketSequence, basket_id: state.basket.basket_id, total, item_count: state.basket.items.length };
    return envelope({
      allocation_plan_id: state.allocation.id,
      basket_version: state.basket.version,
      vendor_count: 1,
      summary: {
        total_items_requested: state.basket.items.reduce((sum, item) => sum + item.requested_quantity, 0),
        total_items_allocated: state.basket.items.reduce((sum, item) => sum + item.requested_quantity, 0),
        total_amount_toman: total,
        total_items_unfulfilled: 0,
      },
    }) as T;
  }

  if (method === "POST" && pathname === "/api/v1/orders") {
    const key = headers?.["Idempotency-Key"] || headers?.["idempotency-key"];
    if (!key) return bad("Mock checkout requires Idempotency-Key.");
    const prior = state.idempotency[key];
    if (prior) return envelope({ ...prior, idempotent_replay: true }) as T;
    const allocationId = String(payload.allocation_plan_id || "");
    if (!state.allocation || allocationId !== state.allocation.id || !state.basket || state.basket.status !== "OPEN") {
      return bad("Mock allocation is missing or stale.");
    }
    const orderId = "mock-retailer-order-" + (102 + state.orders.length - 2);
    const order: RetailerOrder = {
      id: orderId,
      order_number: "POL-AHV-R-" + orderId.split("-").pop(),
      order_status: "SUBMITTED",
      dispute_status: "NONE",
      total_amount_toman: state.allocation.total,
      created_at: new Date().toISOString(),
      delivery_address: String(payload.delivery_address || ""),
      retailer_id: "mock-retailer-org",
    };
    if (order.delivery_address.trim().length < 5) return bad("Mock delivery address is required.");
    state.orders.unshift(order);
    state.orderItems[orderId] = state.basket.items.map((item, index) => ({
      id: "mock-retail-item-" + orderId + "-" + index,
      product_id: item.product_id,
      product_name_snapshot: item.canonical_name_fa,
      brand_name_snapshot: item.brand_name,
      packaging_unit_snapshot: item.default_pack_unit,
      pack_quantity_snapshot: item.pack_quantity,
      ordered_quantity: item.requested_quantity,
      accepted_quantity: item.requested_quantity,
      delivered_quantity: 0,
      unit_price_toman: item.lowest_unit_price_toman,
      total_line_amount_toman: item.requested_quantity * item.lowest_unit_price_toman,
      fulfillment_status: "PENDING",
    }));
    state.timelines[orderId] = [{ id: "mock-event-" + orderId, event_type: "ORDER_SUBMITTED", from_status: null, to_status: "SUBMITTED", created_at: order.created_at }];
    state.deliveries[orderId] = { delivery_status: "PENDING" };
    state.basket.status = "CHECKED_OUT";
    const result = { order_group_id: "mock-retailer-order-group-" + orderId, group_status: "SUBMITTED", total_amount_toman: order.total_amount_toman, idempotent_replay: false };
    state.idempotency[key] = result;
    return envelope(result) as T;
  }

  if (method === "GET" && pathname === "/api/v1/orders") {
    const offset = Number(url.searchParams.get("offset") || 0);
    const limit = Number(url.searchParams.get("limit") || 50);
    return envelope({ orders: state.orders.slice(offset, offset + limit), total: state.orders.length, offset, limit }) as T;
  }

  const orderItems = pathname.match(/^\/api\/v1\/orders\/([^/]+)\/items$/);
  if (method === "GET" && orderItems) return envelope({ items: state.orderItems[orderItems[1]] || [] }) as T;

  const timeline = pathname.match(/^\/api\/v1\/orders\/([^/]+)\/timeline$/);
  if (method === "GET" && timeline) return envelope({ timeline: state.timelines[timeline[1]] || [] }) as T;

  const orderDelivery = pathname.match(/^\/api\/v1\/orders\/([^/]+)\/delivery$/);
  if (method === "GET" && orderDelivery) return envelope(state.deliveries[orderDelivery[1]] || { delivery_status: "PENDING" }) as T;

  const orderReturns = pathname.match(/^\/api\/v1\/orders\/([^/]+)\/returns$/);
  if (method === "GET" && orderReturns) {
    const result = state.returns.filter((x) => x.order_id === orderReturns[1]);
    return envelope({ returns: result }) as T;
  }
  if (method === "POST" && orderReturns) {
    const order = findOrder(orderReturns[1]);
    const itemList = rowsOf<Record<string, unknown>>(payload, "items");
    const row = { id: "mock-retailer-return-" + (state.returns.length + 1), order_id: order.id, status: "REQUESTED", items: itemList, reason: payload.reason || null, created_at: new Date().toISOString() };
    state.returns.push(row);
    return envelope(row) as T;
  }

  const orderDisputes = pathname.match(/^\/api\/v1\/orders\/([^/]+)\/disputes$/);
  if (method === "GET" && orderDisputes) {
    return envelope({ disputes: state.disputes.filter((x) => x.order_id === orderDisputes[1]) }) as T;
  }
  if (method === "POST" && orderDisputes) {
    const order = findOrder(orderDisputes[1]);
    if (!Number.isFinite(Number(payload.claimed_amount_toman)) || Number(payload.claimed_amount_toman) <= 0 || !String(payload.description || "").trim()) {
      return bad("Mock dispute requires a positive amount and description.");
    }
    order.dispute_status = "OPEN";
    const row = { id: "mock-retailer-dispute-" + (state.disputes.length + 1), order_id: order.id, dispute_status: "OPEN", claimed_amount_toman: Number(payload.claimed_amount_toman), description: String(payload.description), created_at: new Date().toISOString() };
    state.disputes.push(row);
    return envelope(row) as T;
  }

  const cancelOrder = pathname.match(/^\/api\/v1\/orders\/([^/]+)\/cancel$/);
  if (method === "POST" && cancelOrder) {
    const order = findOrder(cancelOrder[1]);
    order.order_status = "CANCELLED";
    (state.timelines[order.id] ||= []).push({ id: "mock-event-cancel-" + Date.now(), event_type: "ORDER_CANCELLED", from_status: null, to_status: "CANCELLED", created_at: new Date().toISOString() });
    return envelope(order) as T;
  }

  const orderById = pathname.match(/^\/api\/v1\/orders\/([^/]+)$/);
  if (method === "GET" && orderById) return envelope(findOrder(orderById[1])) as T;

  if (method === "GET" && pathname === "/api/v1/invoices") {
    return envelope({ invoices: state.invoices, limit: 50, offset: 0 }) as T;
  }
  const invoice = pathname.match(/^\/api\/v1\/invoices\/([^/]+)$/);
  if (method === "GET" && invoice) {
    const row = state.invoices.find((x) => x.id === invoice[1]);
    if (!row) return bad("Mock retailer invoice not found.");
    return envelope(row) as T;
  }
  const orderInvoice = pathname.match(/^\/api\/v1\/orders\/([^/]+)\/invoice$/);
  if (method === "GET" && orderInvoice) {
    const row = state.invoices.find((x) => x.order_id === orderInvoice[1]);
    if (!row) return bad("Mock invoice for order not found.");
    return envelope(row) as T;
  }

  if (method === "GET" && pathname === "/api/v1/storefront/vendors") {
    const q = (url.searchParams.get("q") || "").toLocaleLowerCase();
    const vendors = q ? [state.vendor].filter((v) => String(v.display_name || v.name).toLocaleLowerCase().includes(q)) : [state.vendor];
    return envelope({ items: vendors, total: vendors.length, page: 1, page_size: 20 }) as T;
  }
  if (method === "GET" && pathname === "/api/v1/storefront/vendors/mock-vendor") return envelope(state.vendor) as T;
  if (method === "GET" && pathname === "/api/v1/storefront/vendors/mock-vendor/products") {
    return envelope({ items: state.vendorProducts, total: state.vendorProducts.length, page: 1, page_size: 20 }) as T;
  }

  if (method === "GET" && pathname === "/api/v1/support/cases") {
    return envelope({ cases: state.supportCases.map(({ messages, ...row }) => row), limit: 50, offset: 0 }) as T;
  }
  if (method === "POST" && pathname === "/api/v1/support/cases") {
    const row = { id: "mock-retailer-case-" + (state.supportCases.length + 1), subject: String(payload.subject || ""), case_type: String(payload.case_type || "GENERAL"), priority: String(payload.priority || "NORMAL"), status: "OPEN", related_order_id: payload.related_order_id || null, created_at: new Date().toISOString(), messages: [] as Array<Record<string, unknown>> };
    if (!row.subject.trim()) return bad("Mock support case subject is required.");
    state.supportCases.push(row);
    return envelope(row) as T;
  }
  const supportCase = pathname.match(/^\/api\/v1\/support\/cases\/([^/]+)$/);
  if (method === "GET" && supportCase) {
    const row = state.supportCases.find((x) => x.id === supportCase[1]);
    if (!row) return bad("Mock retailer support case not found.");
    return envelope(row) as T;
  }
  const supportMessages = pathname.match(/^\/api\/v1\/support\/cases\/([^/]+)\/messages$/);
  if (method === "GET" && supportMessages) {
    const row = state.supportCases.find((x) => x.id === supportMessages[1]);
    if (!row) return bad("Mock retailer support case not found.");
    return envelope({ messages: row.messages }) as T;
  }
  if (method === "POST" && supportMessages) {
    const row = state.supportCases.find((x) => x.id === supportMessages[1]);
    if (!row) return bad("Mock retailer support case not found.");
    const message = { id: "mock-retailer-message-" + (row.messages as unknown[]).length + 1, body: String(payload.body || payload.message || ""), sender_role: headers?.Authorization?.includes("mock-retailer-staff") ? "RETAILER_STAFF" : "RETAILER_OWNER", created_at: new Date().toISOString() };
    (row.messages as Array<Record<string, unknown>>).push(message);
    return envelope(message) as T;
  }

  if (method === "GET" && pathname === "/api/v1/profile") {
    const role: RetailerRole = headers?.Authorization?.includes("mock-retailer-staff") ? "RETAILER_STAFF" : "RETAILER_OWNER";
    const profile = clone(state.profile);
    const membership = profile.membership as Record<string, unknown>;
    membership.role = role;
    membership.id = role === "RETAILER_STAFF" ? "mock-retailer-member-staff" : "mock-retailer-member-owner";
    return envelope(profile) as T;
  }
  if (method === "PUT" && pathname === "/api/v1/profile") {
    const oldUser = (state.profile.user_profile || {}) as Record<string, unknown>;
    state.profile.user_profile = { ...oldUser, ...payload };
    return envelope(state.profile) as T;
  }
  if (method === "GET" && pathname === "/api/v1/profile/context") {
    const role: RetailerRole = headers?.Authorization?.includes("mock-retailer-staff") ? "RETAILER_STAFF" : "RETAILER_OWNER";
    return envelope({ organization_id: "mock-retailer-org", organization_type: "RETAILER", role }) as T;
  }
  if (method === "GET" && pathname === "/api/v1/profile/completion") return envelope({ complete: true, missing_fields: [] }) as T;
  if (method === "GET" && pathname === "/api/v1/notifications") return envelope({ notifications: [], limit: 50, offset: 0 }) as T;
  if (method === "GET" && pathname === "/api/v1/notifications/preferences") return envelope([{ user_id: "mock-retailer-user", category: "ORDER_STATUS_CHANGED", push_enabled: true, sms_enabled: true }]) as T;
  if (method === "PUT" && pathname === "/api/v1/notifications/preferences") return envelope(payload) as T;
  if (method === "GET" && pathname === "/api/v1/auth/sessions/current") return envelope({ id: "mock-retailer-session", status: "ACTIVE", expires_at: new Date(Date.now() + 3600_000).toISOString() }) as T;
  if (method === "DELETE" && pathname === "/api/v1/auth/sessions/current") return envelope({ success: true }) as T;
  if (method === "POST" && pathname === "/api/v1/auth/logout-all") return envelope({ revoked_sessions: 1 }) as T;
  if (method === "GET" && pathname === "/healthz") return envelope({ status: "ok", mode: "mock" }) as T;
  if (method === "GET" && pathname === "/readyz") return envelope({ status: "ready", mode: "mock" }) as T;

  return bad("Mock retailer route not implemented: " + method + " " + path);
}
