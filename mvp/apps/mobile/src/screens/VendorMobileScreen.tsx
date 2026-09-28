import React, { useCallback, useEffect, useMemo, useState } from "react";
import { ScrollView, StyleSheet, Text, View, Pressable } from "react-native";
import { api } from "../api";
import { Btn, Card, Empty, ErrorBox, Input, Screen, StatusChip } from "../components/ui";
import type { Role } from "../types";
import { spacing, useTheme, useThemedStyles, type Palette } from "../theme";
import { SupportMobileScreen } from "./SupportMobileScreen";
import { formatFaNumber, formatTehranDateTime, formatToman, todayTehranIso, toAsciiDigits } from "../i18n/fa";

type MainTab = "home" | "orders" | "inventory" | "finance" | "more" | "support";
type InventoryTab = "stock" | "daily";
type FinanceTab = "invoices" | "settlements";
type MoreTab = "customers" | "referrals" | "staff" | "storefront";

type Order = {
  id: string;
  order_number?: string | null;
  order_status?: string | null;
  total_amount_toman?: number | string | null;
  created_at?: string | null;
  retailer_name?: string | null;
  retailer_store_name?: string | null;
};

type Inv = {
  id: string;
  vendor_product_id?: string | null;
  product_name?: string | null;
  vendor_sku?: string | null;
  packaging_unit?: string | null;
  pack_quantity?: number | null;
  physical_quantity?: number | null;
  available_quantity?: number | null;
  reserved_quantity?: number | null;
  current_price_toman?: number | string | null;
  price_toman?: number | string | null;
  freshness_status?: string | null;
  is_stale?: boolean | null;
};

type Invoice = {
  id: string;
  invoice_number?: string | null;
  status?: string | null;
  total_amount_toman?: number | string | null;
  total_amount?: number | string | null;
  currency?: string | null;
  issued_at?: string | null;
};

type Referral = {
  id: string;
  status?: string | null;
  referral_code?: string | null;
  referred_organization_id?: string | null;
};

type Settlement = {
  id: string;
  settlement_number?: string | null;
  status?: string | null;
  amount_toman?: number | string | null;
  net_vendor_amount_toman?: number | string | null;
  gross_amount_toman?: number | string | null;
};

type Customer = {
  retailer_id: string;
  store_name?: string | null;
  city?: string | null;
  neighborhood?: string | null;
  user_id?: string | null;
  full_name?: string | null;
  phone_number?: string | null;
  order_count?: number | null;
  last_order_at?: string | null;
};

type Staff = {
  membership_id: string;
  user_id: string;
  phone_number?: string | null;
  full_name?: string | null;
  role?: "VENDOR_OWNER" | "VENDOR_STAFF" | null;
  status?: "INVITED" | "ACTIVE" | "SUSPENDED" | "REVOKED" | null;
};

type PermissionGrant = {
  id: string;
  permission_key: string;
  status: "GRANTED" | "REVOKED";
  granted_at?: string | null;
  revoked_at?: string | null;
};

type PermissionDetail = {
  membership_id: string;
  full_name?: string | null;
  role?: string | null;
  grantable_permissions: string[];
  delegated_grants: PermissionGrant[];
  effective_permissions: string[];
};

type DailyLine = {
  id: string;
  vendor_product_id?: string | null;
  product_id?: string | null;
  product_name?: string | null;
  expected_quantity?: number | null;
  confirmed_quantity?: number | null;
};

type Daily = {
  status?: string | null;
  lines?: DailyLine[];
};

type StorefrontVendor = {
  id: string;
  name?: string | null;
  display_name?: string | null;
  city?: string | null;
  description?: string | null;
  is_active?: boolean | null;
  created_at?: string | null;
  product_count?: number | null;
};

type StorefrontProduct = {
  id: string;
  product_id?: string | null;
  product_name?: string | null;
  name?: string | null;
  brand_name?: string | null;
  price_toman?: number | null;
  stock_quantity?: number | null;
  packaging_unit?: string | null;
  is_available?: boolean | null;
};

type BarcodeProduct = {
  id?: string | null;
  master_sku?: string | null;
  canonical_name_fa?: string | null;
  brand_name?: string | null;
  base_unit?: string | null;
  default_pack_unit?: string | null;
  default_pack_quantity?: number | null;
};

type BarcodeResult = {
  match_type?: string | null;
  match_status?: string | null;
  confidence_score?: number | null;
  product?: BarcodeProduct | null;
  products?: BarcodeProduct[];
  candidate_id?: string | null;
  vendor_product_id?: string | null;
  suggested_action?: string | null;
};

function rows<T>(data: unknown, key: string): T[] {
  if (Array.isArray(data)) return data as T[];
  if (!data || typeof data !== "object") return [];
  const obj = data as Record<string, unknown>;
  for (const k of [key, "items", "data", "products", "orders", "settlements"]) {
    if (Array.isArray(obj[k])) return obj[k] as T[];
  }
  return [];
}

function money(value: number | string | null | undefined): string {
  return formatToman(value);
}

function numberFa(value: number | string | null | undefined): string {
  return formatFaNumber(value);
}

function dateTimeFa(value: string | null | undefined): string {
  return formatTehranDateTime(value);
}

function barcodeStatusLabel(status: string | null | undefined): string {
  const map: Record<string, string> = {
    EXACT: "تطبیق قطعی",
    HIGH_CONFIDENCE: "تطبیق با اطمینان بالا",
    AMBIGUOUS: "چند تطبیق",
    NO_MATCH: "یافت نشد",
  };
  return status ? map[status] || status : "نامشخص";
}

function statusLabel(status: string | null | undefined): string {
  const map: Record<string, string> = {
    SUBMITTED: "منتظر بررسی",
    CREATED: "جدید",
    ACCEPTED: "پذیرفته‌شده",
    PARTIALLY_ACCEPTED: "پذیرش جزئی",
    REJECTED: "ردشده",
    PREPARING: "در حال آماده‌سازی",
    READY: "آماده ارسال",
    DISPATCHED: "ارسال‌شده",
    DELIVERED: "تحویل‌شده",
    CANCELLED: "لغوشده",
    PENDING: "در انتظار",
    ACTIVE: "فعال",
    SUSPENDED: "معلق",
    REVOKED: "لغوشده",
    INVITED: "دعوت‌شده",
    CALCULATED: "محاسبه‌شده",
    PAID: "پرداخت‌شده",
  };
  return map[status ?? ""] ?? status ?? "—";
}

function toneForOrderStatus(status: string | null | undefined): "neutral" | "warn" | "ok" | "info" | "danger" {
  if (["DELIVERED", "PAID", "ACCEPTED"].includes(status ?? "")) return "ok";
  if (["SUBMITTED", "CREATED", "PREPARING", "READY", "DISPATCHED", "PARTIALLY_ACCEPTED"].includes(status ?? "")) return "info";
  if (status === "CANCELLED" || status === "REJECTED") return "danger";
  return "neutral";
}

function MetricCard(props: { label: string; value: string; hint: string; tone?: "neutral" | "warn" | "ok" | "info" }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const { colors } = useTheme();
  const accent = props.tone === "warn" ? colors.warning : props.tone === "ok" ? colors.success : props.tone === "info" ? colors.brand : colors.border;
  return (
    <View style={[styles.metricCard, { borderTopColor: accent }]}>
      <Text style={styles.metricLabel}>{props.label}</Text>
      <Text style={styles.metricValue}>{props.value}</Text>
      <Text style={styles.metricHint}>{props.hint}</Text>
    </View>
  );
}

function SectionHeader(props: { title: string; action?: string; onAction?: () => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>{props.title}</Text>
      {props.action && props.onAction ? (
        <Pressable accessibilityRole="button" onPress={props.onAction}>
          <Text style={styles.sectionAction}>{props.action}</Text>
        </Pressable>
      ) : null}
    </View>
  );
}

function BottomNav(props: { tab: MainTab; role: "VENDOR_OWNER" | "VENDOR_STAFF"; onChange: (tab: MainTab) => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const items: Array<{ tab: MainTab; label: string; short: string }> = [
    { tab: "home", label: "خانه", short: "خانه" },
    { tab: "orders", label: "سفارش‌ها", short: "سفارش" },
    { tab: "inventory", label: "انبار", short: "انبار" },
    ...(props.role === "VENDOR_OWNER" ? [{ tab: "finance" as MainTab, label: "مالی", short: "مالی" }] : []),
    { tab: "more", label: "بیشتر", short: "بیشتر" },
    { tab: "support", label: "پشتیبانی", short: "پشتیبانی" },
  ];
  return (
    <View style={styles.bottomNav}>
      {items.map((item) => {
        const selected = props.tab === item.tab;
        return (
          <Pressable
            key={item.tab}
            accessibilityRole="button"
            accessibilityState={{ selected }}
            onPress={() => props.onChange(item.tab)}
            style={({ pressed }) => [styles.navItem, selected && styles.navItemSelected, pressed && styles.navPressed]}
          >
            <Text style={[styles.navLabel, selected && styles.navLabelSelected]}>{item.short}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

export function VendorMobileScreen(props: {
  role: Extract<Role, "VENDOR_OWNER" | "VENDOR_STAFF">;
  onOpenOrder: (orderId: string) => void;
}): React.ReactNode {
  const styles = useThemedStyles(makeStyles);

  const [tab, setTab] = useState<MainTab>("home");
  const [inventoryTab, setInventoryTab] = useState<InventoryTab>("stock");
  const [financeTab, setFinanceTab] = useState<FinanceTab>("invoices");
  const [moreTab, setMoreTab] = useState<MoreTab>("customers");

  const [orders, setOrders] = useState<Order[]>([]);
  const [inventory, setInventory] = useState<Inv[]>([]);
  const [settlements, setSettlements] = useState<Settlement[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [invoiceDetail, setInvoiceDetail] = useState<Invoice | null>(null);
  const [settlementDetail, setSettlementDetail] = useState<Settlement | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [staff, setStaff] = useState<Staff[]>([]);
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [daily, setDaily] = useState<Daily | null>(null);
  const [storefrontVendor, setStorefrontVendor] = useState<StorefrontVendor | null>(null);
  const [storefrontProducts, setStorefrontProducts] = useState<StorefrontProduct[]>([]);
  const [barcode, setBarcode] = useState("");
  const [barcodeResult, setBarcodeResult] = useState<BarcodeResult | null>(null);
  const [candidateTitle, setCandidateTitle] = useState("");
  const [candidateBrand, setCandidateBrand] = useState("");
  const [candidateSku, setCandidateSku] = useState("");
  const [candidateCreatedId, setCandidateCreatedId] = useState<string | null>(null);
  const [scanSessionId, setScanSessionId] = useState("");
  const [scanProductId, setScanProductId] = useState("");
  const [scanSku, setScanSku] = useState("");
  const [scanPackaging, setScanPackaging] = useState("CARTON");
  const [scanPackQuantity, setScanPackQuantity] = useState("1");
  const [scanPhysicalQuantity, setScanPhysicalQuantity] = useState("");
  const [scanUnitPrice, setScanUnitPrice] = useState("");
  const [scanStatus, setScanStatus] = useState<string | null>(null);
  const [publishStatus, setPublishStatus] = useState<string | null>(null);

  const [customerQuery, setCustomerQuery] = useState("");
  const [invitePhone, setInvitePhone] = useState("");
  const [inviteName, setInviteName] = useState("");
  const [dailyDate, setDailyDate] = useState(todayTehranIso());
  const [dailyEdits, setDailyEdits] = useState<Record<string, string>>({});

  const [permissionMemberId, setPermissionMemberId] = useState<string | null>(null);
  const [permissionDetail, setPermissionDetail] = useState<PermissionDetail | null>(null);
  const [permissionKey, setPermissionKey] = useState("");
  const [permissionReason, setPermissionReason] = useState("");

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadOrders = useCallback(async () => {
    const data = await api.get<unknown>("/api/v1/orders?limit=50&offset=0");
    setOrders(rows<Order>(data, "orders"));
  }, []);

  const loadInventory = useCallback(async () => {
    const data = await api.get<unknown>("/api/v1/catalog/vendors/products");
    setInventory(rows<Inv>(data, "products"));
  }, []);

  const loadDaily = useCallback(async () => {
    const data = await api.get<Daily>("/api/v1/inventory/daily/" + dailyDate);
    setDaily(data);
    const next: Record<string, string> = {};
    for (const line of data.lines ?? []) next[line.id] = String(line.confirmed_quantity ?? line.expected_quantity ?? 0);
    setDailyEdits(next);
  }, [dailyDate]);

  const loadInvoiceDetail = useCallback(async (invoiceId: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<Invoice>("/api/v1/invoices/" + invoiceId);
      setInvoiceDetail(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "جزئیات فاکتور ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }, []);

  const loadSettlementDetail = useCallback(async (settlementId: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<Settlement>("/api/v1/settlements/" + settlementId);
      setSettlementDetail(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "جزئیات تسویه ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }, []);

  const loadInvoices = useCallback(async () => {
    const data = await api.get<unknown>("/api/v1/invoices?limit=50&offset=0");
    setInvoices(rows<Invoice>(data, "invoices"));
  }, []);

  const loadSettlements = useCallback(async () => {
    const data = await api.get<unknown>("/api/v1/vendors/settlements");
    setSettlements(rows<Settlement>(data, "settlements"));
  }, []);

  const loadReferrals = useCallback(async () => {
    const data = await api.get<unknown>("/api/v1/referrals?limit=50&offset=0");
    setReferrals(rows<Referral>(data, "referrals"));
  }, []);

  const loadCustomers = useCallback(async () => {
    const q = customerQuery.trim() ? "&query=" + encodeURIComponent(customerQuery.trim()) : "";
    const data = await api.get<unknown>("/api/v1/vendors/customers?limit=50&offset=0" + q);
    setCustomers(rows<Customer>(data, "customers"));
  }, [customerQuery]);

  const loadStaff = useCallback(async () => {
    const data = await api.get<unknown>("/api/v1/vendors/staff?limit=100&offset=0");
    setStaff(rows<Staff>(data, "members"));
  }, []);

  const loadStorefront = useCallback(async () => {
    const data = await api.get<unknown>("/api/v1/storefront/vendors");
    const vendors = rows<StorefrontVendor>(data, "vendors");
    const selected = vendors[0] ?? null;
    setStorefrontVendor(selected);
    if (!selected) {
      setStorefrontProducts([]);
      return;
    }
    const productData = await api.get<unknown>("/api/v1/storefront/vendors/" + selected.id + "/products?limit=50&offset=0");
    setStorefrontProducts(rows<StorefrontProduct>(productData, "products"));
  }, []);

  async function scanBarcode(): Promise<void> {
    const value = barcode.trim();
    if (value.length < 8 || value.length > 32) {
      setError("بارکد باید بین ۸ تا ۳۲ نویسه باشد.");
      return;
    }
    setLoading(true);
    setError(null);
    setCandidateCreatedId(null);
    try {
      const data = await api.get<BarcodeResult>(
        "/api/v1/catalog/barcode/lookup?barcode=" + encodeURIComponent(value),
      );
      setBarcodeResult(data);
      if (data.product?.id) setScanProductId(data.product.id);
      if (data.product?.master_sku) setScanSku(data.product.master_sku);
      if (data.product?.default_pack_unit) setScanPackaging(data.product.default_pack_unit);
      if (data.product?.default_pack_quantity) setScanPackQuantity(String(data.product.default_pack_quantity));
    } catch (e) {
      setBarcodeResult(null);
      setError(e instanceof Error ? e.message : "استعلام بارکد ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }

  async function submitContinuousScan(): Promise<void> {
    const productId = scanProductId || barcodeResult?.product?.id || "";
    const sku = scanSku || barcodeResult?.product?.master_sku || "";
    const packQuantity = Number(toAsciiDigits(scanPackQuantity).replace(/[٬,\s]/g, ""));
    const physicalQuantity = Number(toAsciiDigits(scanPhysicalQuantity).replace(/[٬,\s]/g, ""));
    const unitPrice = Number(toAsciiDigits(scanUnitPrice).replace(/[٬,\s]/g, ""));
    if (!productId || !sku) {
      setError("ابتدا یک کالای تطبیق‌شده را انتخاب کنید.");
      return;
    }
    if (!Number.isInteger(packQuantity) || packQuantity < 1 || !Number.isInteger(physicalQuantity) || physicalQuantity < 0 || !Number.isFinite(unitPrice) || unitPrice <= 0) {
      setError("تعداد بسته، موجودی فیزیکی و قیمت را با مقدار معتبر وارد کنید.");
      return;
    }
    const sessionId = scanSessionId || "android-vendor-" + Date.now().toString(36);
    setScanSessionId(sessionId);
    setLoading(true);
    setError(null);
    try {
      const data = await api.post<{ session_id?: string; status?: string }>(
        "/api/v1/vendors/inventory/continuous-scan",
        {
          product_id: productId,
          vendor_sku: sku,
          packaging_unit: scanPackaging,
          pack_quantity: packQuantity,
          physical_quantity: physicalQuantity,
          unit_price_toman: unitPrice,
          session_id: sessionId,
        },
      );
      setScanStatus(data.status || "ثبت شد");
      setPublishStatus(null);
      await loadInventory();
    } catch (e) {
      setError(e instanceof Error ? e.message : "ثبت اسکن موجودی ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }

  async function publishContinuousScan(): Promise<void> {
    if (!scanSessionId) {
      setError("ابتدا حداقل یک قلم را در یک جلسه اسکن ثبت کنید.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await api.post<{ status?: string; published_count?: number }>(
        "/api/v1/vendors/inventory/publish",
        { session_id: scanSessionId },
      );
      setPublishStatus(data.status || (data.published_count != null ? `${data.published_count} قلم منتشر شد` : "منتشر شد"));
      await loadInventory();
    } catch (e) {
      setError(e instanceof Error ? e.message : "انتشار موجودی ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }

  async function createBarcodeCandidate(): Promise<void> {
    if (!barcode.trim() || !candidateTitle.trim()) {
      setError("برای کالای ناشناخته، عنوان پیشنهادی الزامی است.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await api.post<{ candidate_id?: string }>("/api/v1/product-candidates", {
        proposed_title: candidateTitle.trim(),
        proposed_brand: candidateBrand.trim() || null,
        barcode: barcode.trim(),
        vendor_sku: candidateSku.trim() || null,
      });
      setCandidateCreatedId(data.candidate_id || "ثبت شد");
      setCandidateTitle("");
      setCandidateBrand("");
      setCandidateSku("");
      await loadInventory();
    } catch (e) {
      setError(e instanceof Error ? e.message : "ثبت کاندیدای کالا ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }

  const refreshCore = useCallback(async () => {
    setLoading(true);
    setError(null);
    const results = await Promise.allSettled([loadOrders(), loadInventory(), loadDaily()]);
    if (results.every((r) => r.status === "rejected")) {
      setError("بارگذاری اطلاعات اصلی بنکدار ناموفق بود.");
    } else if (results.some((r) => r.status === "rejected")) {
      setError("بعضی اطلاعات با خطا بارگذاری شد. برای تلاش مجدد، صفحه را تازه کنید.");
    }
    setLoading(false);
  }, [loadOrders, loadInventory, loadDaily]);

  useEffect(() => {
    void refreshCore();
  }, [refreshCore]);

  useEffect(() => {
    let promise: Promise<void> | null = null;
    if (tab === "finance") {
      if (props.role !== "VENDOR_OWNER") {
        setTab("home");
        return;
      }
      promise = financeTab === "invoices" ? loadInvoices() : loadSettlements();
    } else if (tab === "more") {
      promise =
        moreTab === "customers"
          ? loadCustomers()
          : moreTab === "referrals"
            ? loadReferrals()
            : moreTab === "staff"
              ? loadStaff()
              : props.role === "VENDOR_OWNER"
                ? loadStorefront()
                : loadCustomers();
    } else if (tab === "inventory" && inventoryTab === "daily") {
      promise = loadDaily();
    } else if (tab === "orders") {
      promise = loadOrders();
    }
    if (!promise) return;
    setLoading(true);
    setError(null);
    void promise.catch((e) => setError(e instanceof Error ? e.message : "بارگذاری ناموفق بود")).finally(() => setLoading(false));
  }, [tab, financeTab, inventoryTab, moreTab, loadInvoices, loadInvoiceDetail, loadSettlements, loadSettlementDetail, loadCustomers, loadReferrals, loadStaff, loadStorefront, loadDaily, loadOrders, props.role]);

  async function orderAction(orderId: string, actionName: "accept" | "preparing" | "ready"): Promise<void> {
    if (actionName === "accept" && props.role !== "VENDOR_OWNER") {
      setError("پذیرش سفارش فقط برای مالک بنکداری مجاز است.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await api.post("/api/v1/orders/" + orderId + "/" + actionName, {});
      await loadOrders();
    } catch (e) {
      setError(e instanceof Error ? e.message : "عملیات سفارش ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }

  async function saveInventory(row: Inv, raw: string): Promise<void> {
    const quantity = Number(toAsciiDigits(raw).replace(/[٬,\s]/g, ""));
    if (!Number.isFinite(quantity) || quantity < 0) {
      setError("موجودی باید عددی غیرمنفی باشد.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await api.patch("/api/v1/catalog/vendors/products/" + String(row.vendor_product_id || row.id) + "/inventory", {
        new_physical_quantity: quantity,
      });
      await loadInventory();
    } catch (e) {
      setError(e instanceof Error ? e.message : "ذخیره موجودی ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }

  async function savePrice(row: Inv, raw: string): Promise<void> {
    const price = Number(toAsciiDigits(raw).replace(/[٬,\s]/g, ""));
    if (!Number.isFinite(price) || price <= 0) {
      setError("قیمت باید بیشتر از صفر باشد.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await api.post("/api/v1/catalog/vendors/products/" + String(row.vendor_product_id || row.id) + "/prices", {
        price_toman: price,
      });
      await loadInventory();
    } catch (e) {
      setError(e instanceof Error ? e.message : "ذخیره قیمت ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }

  async function confirmDaily(changes: boolean): Promise<void> {
    setLoading(true);
    setError(null);
    try {
      if (!changes) {
        await api.post("/api/v1/inventory/daily/" + dailyDate + "/confirm", {});
      } else {
        await api.post("/api/v1/inventory/daily/" + dailyDate + "/confirm-with-changes", {
          changes: (daily?.lines ?? []).map((line) => ({
            vendor_product_id: line.vendor_product_id || line.id,
            declared_quantity: Number(toAsciiDigits(dailyEdits[line.id] || "0").replace(/[٬,\s]/g, "")),
          })),
        });
      }
      await loadDaily();
    } catch (e) {
      setError(e instanceof Error ? e.message : "تأیید موجودی ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }

  async function inviteStaff(): Promise<void> {
    if (props.role !== "VENDOR_OWNER") {
      setError("فقط مالک بنکداری می‌تواند همکار جدید دعوت کند.");
      return;
    }
    if (!/^\+[1-9]\d{7,14}$/.test(invitePhone.trim())) {
      setError("شماره موبایل باید با قالب بین‌المللی وارد شود.");
      return;
    }
    if (!inviteName.trim()) {
      setError("نام همکار الزامی است.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await api.post("/api/v1/vendors/staff/invite", { phone_number: invitePhone.trim(), full_name: inviteName.trim() });
      setInvitePhone("");
      setInviteName("");
      await loadStaff();
    } catch (e) {
      setError(e instanceof Error ? e.message : "دعوت همکار ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }

  async function updateStaff(membershipId: string, patch: { status?: Staff["status"] }): Promise<void> {
    if (props.role !== "VENDOR_OWNER") {
      setError("فقط مالک بنکداری می‌تواند وضعیت همکاران را تغییر دهد.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await api.patch("/api/v1/vendors/staff/" + membershipId, patch);
      await loadStaff();
    } catch (e) {
      setError(e instanceof Error ? e.message : "ویرایش همکار ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }

  async function loadStaffPermissions(membershipId: string): Promise<void> {
    if (props.role !== "VENDOR_OWNER") {
      setError("فقط مالک بنکداری می‌تواند مجوزهای تفویضی را مدیریت کند.");
      return;
    }
    setPermissionMemberId(membershipId);
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<PermissionDetail>("/api/v1/vendors/staff/" + membershipId + "/permissions");
      setPermissionDetail(data);
      setPermissionKey(data.grantable_permissions[0] || "");
      setPermissionReason("");
    } catch (e) {
      setPermissionDetail(null);
      setError(e instanceof Error ? e.message : "دریافت مجوزها ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }

  async function grantStaffPermission(): Promise<void> {
    if (!permissionMemberId || !permissionKey || !permissionReason.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await api.post("/api/v1/vendors/staff/" + permissionMemberId + "/permissions", {
        permission_key: permissionKey,
        reason: permissionReason.trim(),
        client: "ANDROID",
      });
      await loadStaffPermissions(permissionMemberId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "اعطای مجوز ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }

  async function revokeStaffPermission(permission: string): Promise<void> {
    if (!permissionMemberId || !permissionReason.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await api.post(
        "/api/v1/vendors/staff/" + permissionMemberId + "/permissions/" + encodeURIComponent(permission) + "/revoke",
        { reason: permissionReason.trim(), client: "ANDROID" },
      );
      await loadStaffPermissions(permissionMemberId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "لغو مجوز ناموفق بود.");
    } finally {
      setLoading(false);
    }
  }

  const pendingOrders = useMemo(
    () => orders.filter((order) => ["SUBMITTED", "CREATED"].includes(order.order_status ?? "")),
    [orders],
  );
  const activeOrders = useMemo(
    () => orders.filter((order) => ["ACCEPTED", "PARTIALLY_ACCEPTED", "PREPARING", "READY", "DISPATCHED"].includes(order.order_status ?? "")),
    [orders],
  );
  const staleInventory = useMemo(
    () => inventory.filter((row) => row.is_stale === true || ["STALE", "EXPIRED"].includes(row.freshness_status ?? "")),
    [inventory],
  );

  function renderHome(): React.ReactNode {
    return (
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.hero}>
          <View style={styles.heroCopy}>
            <Text style={styles.eyebrow}>فضای عملیاتی بنکداری</Text>
            <Text style={styles.heroTitle}>پل بنکدار</Text>
            <Text style={styles.heroBody}>سفارش، موجودی و آماده‌سازی را از یک نقطه مدیریت کنید.</Text>
          </View>
          <View style={styles.roleBadge}>
            <Text style={styles.roleBadgeText}>{props.role === "VENDOR_OWNER" ? "مالک" : "همکار"}</Text>
          </View>
        </View>

        <ErrorBox message={error} />

        <View style={styles.metricGrid}>
          <MetricCard label="منتظر اقدام" value={numberFa(pendingOrders.length)} hint="سفارش جدید" tone={pendingOrders.length > 0 ? "warn" : "ok"} />
          <MetricCard label="در جریان" value={numberFa(activeOrders.length)} hint="آماده‌سازی و ارسال" tone="info" />
          <MetricCard label="کالاها" value={numberFa(inventory.length)} hint="ثبت‌شده در کاتالوگ" />
          <MetricCard label="موجودی نیازمند توجه" value={numberFa(staleInventory.length)} hint="بر اساس وضعیت تازگی" tone={staleInventory.length > 0 ? "warn" : "ok"} />
        </View>

        <SectionHeader title="اقدام‌های امروز" />
        <View style={styles.quickGrid}>
          <QuickAction label="صف سفارش" detail={pendingOrders.length ? "سفارش منتظر بررسی دارید" : "موردی در صف نیست"} onPress={() => setTab("orders")} tone={pendingOrders.length ? "warn" : "neutral"} />
          <QuickAction label="موجودی روزانه" detail={daily?.status ? statusLabel(daily.status) : "وضعیت امروز را ببینید"} onPress={() => { setInventoryTab("daily"); setTab("inventory"); }} tone={daily?.status === "PENDING" ? "warn" : "neutral"} />
          <QuickAction label="موجودی کالاها" detail={inventory.length ? numberFa(inventory.length) + " قلم ثبت شده" : "کاتالوگ خالی است"} onPress={() => { setInventoryTab("stock"); setTab("inventory"); }} />
          props.role === "VENDOR_OWNER" ? <QuickAction label="مالی" detail="فاکتور و تسویه" onPress={() => setTab("finance")} /> : null
          <QuickAction label="پشتیبانی" detail="ثبت و پیگیری پرونده‌های پشتیبانی" onPress={() => setTab("support")} />
        </View>

        <SectionHeader title="سفارش‌های منتظر اقدام" action="مشاهده همه" onAction={() => setTab("orders")} />
        {pendingOrders.length === 0 ? (
          <Empty title="صف سفارش خالی است" description="در حال حاضر سفارشی برای بررسی فوری وجود ندارد." />
        ) : (
          pendingOrders.slice(0, 3).map((order) => <OrderCard key={order.id} order={order} role={props.role} onOpen={props.onOpenOrder} onAction={orderAction} loading={loading} />)
        )}

        <SectionHeader title="تازه‌ترین موجودی‌ها" action="مشاهده انبار" onAction={() => setTab("inventory")} />
        {inventory.length === 0 ? (
          <Empty title="کالایی ثبت نشده" description="اولین داده‌های کاتالوگ و موجودی بنکداری را از پنل عملیاتی ثبت کنید." />
        ) : (
          inventory.slice(0, 3).map((row) => <InventoryCard key={row.id} row={row} onSaveInventory={saveInventory} onSavePrice={savePrice} loading={loading} editablePrice={props.role === "VENDOR_OWNER"} compact />)
        )}
      </ScrollView>
    );
  }

  function renderOrders(): React.ReactNode {
    return (
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.pageIntro}>
          <Text style={styles.eyebrow}>عملیات سفارش</Text>
          <Text style={styles.pageTitle}>صف سفارش‌ها</Text>
          <Text style={styles.pageBody}>ابتدا سفارش‌های منتظر بررسی را ببینید؛ وضعیت‌های بعدی بر اساس پاسخ سرور نمایش داده می‌شوند.</Text>
        </View>
        <ErrorBox message={error} />
        {orders.length === 0 ? (
          <Empty title="صف سفارش خالی است" description="سفارشی برای این بنکداری از API دریافت نشد." />
        ) : (
          orders.map((order) => <OrderCard key={order.id} order={order} role={props.role} onOpen={props.onOpenOrder} onAction={orderAction} loading={loading} />)
        )}
      </ScrollView>
    );
  }

  function renderInventory(): React.ReactNode {
    return (
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.pageIntro}>
          <Text style={styles.eyebrow}>کالا و موجودی</Text>
          <Text style={styles.pageTitle}>انبار بنکداری</Text>
          <Text style={styles.pageBody}>موجودی فیزیکی، رزرو و فروش‌پذیر را جدا نگه می‌داریم؛ قیمت نیز از API کانونیکال خوانده و ثبت می‌شود.</Text>
        </View>
        <Card>
          <Text style={styles.itemTitle}>استعلام بارکد</Text>
          <Text style={styles.meta}>مسیر دستی برای تست و عملیات؛ دوربین واقعی در مرحله device runtime اضافه و گواهی می‌شود.</Text>
          <Input
            label="بارکد"
            value={barcode}
            onChangeText={(value) => setBarcode(toAsciiDigits(value).replace(/[^0-9A-Za-z]/g, ""))}
            direction="ltr"
            keyboardType="number-pad"
            placeholder="6260123456789"
            maxLength={32}
          />
          <Btn label="استعلام بارکد" onPress={() => void scanBarcode()} loading={loading} disabled={loading || barcode.trim().length < 8} />
          {barcodeResult ? (
            <View style={styles.scanResult}>
              <View style={styles.rowBetween}>
                <StatusChip label={barcodeStatusLabel(barcodeResult.match_type || barcodeResult.match_status)} tone={barcodeResult.match_type === "NO_MATCH" ? "warn" : barcodeResult.match_type === "AMBIGUOUS" ? "danger" : "ok"} />
                {barcodeResult.confidence_score != null ? (
                  <Text style={styles.meta}>اطمینان: {numberFa(Math.round(Number(barcodeResult.confidence_score) * 100))}%</Text>
                ) : null}
              </View>
              {barcodeResult.product ? (
                <View style={styles.scanProduct}>
                  <Text style={styles.itemTitle}>{barcodeResult.product.canonical_name_fa || "کالای تطبیق‌شده"}</Text>
                  <Text style={styles.meta}>SKU: {barcodeResult.product.master_sku || "—"} · برند: {barcodeResult.product.brand_name || "—"}</Text>
                  <Text style={styles.meta}>بسته‌بندی: {barcodeResult.product.default_pack_unit || "—"} · تعداد: {numberFa(barcodeResult.product.default_pack_quantity)}</Text>
                </View>
              ) : null}
              {barcodeResult.product ? (
                <View style={styles.candidatePanel}>
                  <Text style={styles.itemTitle}>ثبت در موجودی با اسکن</Text>
                  <Text style={styles.meta}>در این مرحله دوربین واقعی هنوز device-gated است؛ همین فرم همان contract اسکن پیوسته را با داده متصل می‌کند.</Text>
                  <Input label="SKU فروشنده" value={scanSku} onChangeText={setScanSku} direction="ltr" />
                  <Input label="واحد بسته‌بندی" value={scanPackaging} onChangeText={setScanPackaging} direction="ltr" />
                  <Input label="تعداد در بسته" value={scanPackQuantity} onChangeText={setScanPackQuantity} keyboardType="numeric" />
                  <Input label="موجودی فیزیکی" value={scanPhysicalQuantity} onChangeText={setScanPhysicalQuantity} keyboardType="numeric" />
                  <Input label="قیمت فروش (تومان)" value={scanUnitPrice} onChangeText={setScanUnitPrice} keyboardType="numeric" />
                  <Btn label="ثبت در جلسه اسکن" onPress={() => void submitContinuousScan()} loading={loading} disabled={loading} />
                  {scanSessionId ? <Text style={styles.meta}>جلسه: {scanSessionId}</Text> : null}
                  {scanStatus ? <Text style={styles.successNote}>وضعیت ثبت: {scanStatus}</Text> : null}
                  {scanSessionId ? <Btn label="انتشار موجودی جلسه" tone="ghost" onPress={() => void publishContinuousScan()} loading={loading} disabled={loading} /> : null}
                  {publishStatus ? <Text style={styles.successNote}>وضعیت انتشار: {publishStatus}</Text> : null}
                </View>
              ) : null}
              {barcodeResult.products?.length ? (
                <View style={styles.scanProduct}>
                  <Text style={styles.itemTitle}>چند تطبیق پیدا شد</Text>
                  {barcodeResult.products.slice(0, 5).map((product, index) => (
                    <Text key={product.id || index} style={styles.meta}>
                      {numberFa(index + 1)}. {product.canonical_name_fa || "—"} · {product.master_sku || "—"}
                    </Text>
                  ))}
                </View>
              ) : null}
              {barcodeResult.match_type === "NO_MATCH" ? (
                <View style={styles.candidatePanel}>
                  <Text style={styles.itemTitle}>کالای ناشناخته</Text>
                  <Text style={styles.meta}>بارکد ناشناخته به Master Product تبدیل نمی‌شود؛ فقط می‌توان کاندیدای بررسی ثبت کرد.</Text>
                  <Input label="عنوان پیشنهادی" value={candidateTitle} onChangeText={setCandidateTitle} />
                  <Input label="برند پیشنهادی" value={candidateBrand} onChangeText={setCandidateBrand} />
                  <Input label="SKU بنکداری (اختیاری)" value={candidateSku} onChangeText={setCandidateSku} direction="ltr" />
                  <Btn label="ثبت کاندیدای کالا" onPress={() => void createBarcodeCandidate()} loading={loading} disabled={loading || !candidateTitle.trim()} />
                  {candidateCreatedId ? <Text style={styles.successNote}>کاندید ثبت شد: {candidateCreatedId}</Text> : null}
                </View>
              ) : null}
            </View>
          ) : null}
        </Card>
        <Segmented labels={[["stock", "موجودی کالا"], ["daily", "تأیید روزانه"]]} selected={inventoryTab} onChange={(value) => setInventoryTab(value as InventoryTab)} />
        <ErrorBox message={error} />
        {inventoryTab === "stock" ? (
          inventory.length === 0 ? (
            <Empty title="موجودی‌ای ثبت نشده" description="فهرست کالاهای بنکداری از API فعلی خالی برگشت." />
          ) : (
            inventory.map((row) => <InventoryCard key={row.id} row={row} onSaveInventory={saveInventory} onSavePrice={savePrice} loading={loading} editablePrice={props.role === "VENDOR_OWNER"} />)
          )
        ) : (
          <View>
            <Card>
              <Input label="تاریخ تأیید" value={dailyDate} onChangeText={(value) => setDailyDate(value.replace(/[^0-9-]/g, ""))} direction="ltr" keyboardType="default" />
              <Btn label="بارگذاری روز" tone="ghost" onPress={() => void loadDaily().catch((e) => setError(e instanceof Error ? e.message : "خطا"))} />
            </Card>
            <StatusCard status={daily?.status} />
            {daily?.lines?.length ? daily.lines.map((line) => (
              <Card key={line.id}>
                <Text style={styles.itemTitle}>{line.product_name || line.id}</Text>
                <Text style={styles.meta}>مقدار مورد انتظار: {numberFa(line.expected_quantity)}</Text>
                <Input label="مقدار تأییدشده" value={dailyEdits[line.id] || ""} onChangeText={(value) => setDailyEdits((prev) => ({ ...prev, [line.id]: value }))} keyboardType="numeric" />
              </Card>
            )) : <Empty title="ردیفی برای تأیید وجود ندارد" />}
            {daily?.lines?.length ? (
              <View style={styles.actionRow}>
                <Btn label="تأیید بدون تغییر" onPress={() => void confirmDaily(false)} loading={loading} disabled={loading} />
                <Btn label="تأیید با تغییرات" tone="ghost" onPress={() => void confirmDaily(true)} loading={loading} disabled={loading} />
              </View>
            ) : null}
          </View>
        )}
      </ScrollView>
    );
  }

  function renderFinance(): React.ReactNode {
    return (
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.pageIntro}>
          <Text style={styles.eyebrow}>مالی</Text>
          <Text style={styles.pageTitle}>{invoiceDetail ? "جزئیات فاکتور" : settlementDetail ? "جزئیات تسویه" : "فعالیت مالی بنکداری"}</Text>
          <Text style={styles.pageBody}>
            {invoiceDetail
              ? "اقلام فاکتور و مبلغ ثبت‌شده را از منبع کانونیکال ببینید."
              : settlementDetail
                ? "مبلغ ناخالص، کمیسیون و تعدیلات تسویه را از منبع کانونیکال ببینید."
                : "نمایش فاکتورها و وضعیت تسویه بدون ساخت wallet یا custody جدید."}
          </Text>
        </View>
        <ErrorBox message={error} />

        {invoiceDetail ? (
          <View>
            <Btn label="بازگشت به فهرست فاکتورها" tone="ghost" onPress={() => setInvoiceDetail(null)} />
            <Card>
              <View style={styles.rowBetween}>
                <StatusChip label={statusLabel(invoiceDetail.status)} tone="info" />
                <Text style={styles.meta}>{dateTimeFa(invoiceDetail.issued_at)}</Text>
              </View>
              <Text style={styles.itemTitle}>{invoiceDetail.invoice_number || invoiceDetail.id}</Text>
              {invoiceDetail.order_id ? <Text style={styles.meta}>سفارش: {invoiceDetail.order_id}</Text> : null}
              <Text style={styles.metricSmall}>{money(invoiceDetail.total_amount_toman ?? invoiceDetail.total_amount)}</Text>
            </Card>
            {(invoiceDetail.items || []).map((item) => (
              <Card key={item.id}>
                <Text style={styles.itemTitle}>{item.product_name || "—"}</Text>
                <Text style={styles.meta}>تعداد: {numberFa(item.quantity)} · قیمت واحد: {money(item.unit_price)}</Text>
                <Text style={styles.metricSmall}>{money(item.total_line_amount)}</Text>
              </Card>
            ))}
          </View>
        ) : settlementDetail ? (
          <View>
            <Btn label="بازگشت به فهرست تسویه‌ها" tone="ghost" onPress={() => setSettlementDetail(null)} />
            <Card>
              <View style={styles.rowBetween}>
                <StatusChip label={statusLabel(settlementDetail.status)} tone={settlementDetail.status === "PAID" ? "ok" : "info"} />
                <Text style={styles.meta}>{dateTimeFa(settlementDetail.settled_at)}</Text>
              </View>
              <Text style={styles.itemTitle}>{settlementDetail.settlement_number || settlementDetail.id}</Text>
              <Text style={styles.metricSmall}>{money(settlementDetail.net_vendor_amount_toman ?? settlementDetail.amount_toman)}</Text>
              <Text style={styles.meta}>ناخالص: {money(settlementDetail.gross_amount_toman)} · کمیسیون: {money(settlementDetail.commission_amount_toman)}</Text>
              <Text style={styles.meta}>تعدیلات: {money(settlementDetail.adjustment_amount_toman)}</Text>
            </Card>
            {(settlementDetail.adjustments || []).map((adj, index) => (
              <Card key={adj.id || index}>
                <Text style={styles.itemTitle}>{adj.adjustment_type || "تعدیل"}</Text>
                <Text style={styles.meta}>{adj.reason || "بدون توضیح"}</Text>
                <Text style={styles.metricSmall}>{money(adj.amount_toman)}</Text>
              </Card>
            ))}
          </View>
        ) : (
          <>
            <Segmented labels={[["invoices", "فاکتورها"], ["settlements", "تسویه‌ها"]]} selected={financeTab} onChange={(value) => setFinanceTab(value as FinanceTab)} />
            {financeTab === "invoices" ? (
              invoices.length === 0 ? (
                <Empty title="فاکتوری موجود نیست" description="از API فاکتور کانونیکال، رکوردی برای این بنکداری دریافت نشد." />
              ) : (
                invoices.map((invoice) => (
                  <Pressable key={invoice.id} accessibilityRole="button" onPress={() => void loadInvoiceDetail(invoice.id)}>
                    <Card>
                      <View style={styles.rowBetween}>
                        <StatusChip label={statusLabel(invoice.status)} tone="info" />
                        <Text style={styles.meta}>{dateTimeFa(invoice.issued_at)}</Text>
                      </View>
                      <Text style={styles.itemTitle}>{invoice.invoice_number || invoice.id}</Text>
                      <Text style={styles.metricSmall}>{money(invoice.total_amount_toman ?? invoice.total_amount)}</Text>
                    </Card>
                  </Pressable>
                ))
              )
            ) : settlements.length === 0 ? (
              <Empty title="تسویه‌ای ثبت نشده" description="وضعیت تسویه از API فعلی خالی برگشت." />
            ) : (
              settlements.map((settlement) => (
                <Pressable key={settlement.id} accessibilityRole="button" onPress={() => void loadSettlementDetail(settlement.id)}>
                  <Card>
                    <View style={styles.rowBetween}>
                      <StatusChip label={statusLabel(settlement.status)} tone={settlement.status === "PAID" ? "ok" : "info"} />
                      <Text style={styles.itemTitle}>{settlement.settlement_number || settlement.id}</Text>
                    </View>
                    <Text style={styles.metricSmall}>{money(settlement.amount_toman ?? settlement.net_vendor_amount_toman ?? settlement.gross_amount_toman)}</Text>
                  </Card>
                </Pressable>
              ))
            )}
          </>
        )}
      </ScrollView>
    );
  }

  function renderMore(): React.ReactNode {
    return (
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.pageIntro}>
          <Text style={styles.eyebrow}>مدیریت بنکداری</Text>
          <Text style={styles.pageTitle}>بیشتر</Text>
          <Text style={styles.pageBody}>مشتریان، ارجاع‌ها و همکاران در این بخش قرار دارند تا navigation روزانه خلوت بماند.</Text>
        </View>
        <Segmented
          labels={[
            ["customers", "مشتریان"],
            ["referrals", "ارجاع"],
            ["staff", "همکاران"],
            ...(props.role === "VENDOR_OWNER" ? [["storefront", "ویترین"] as [string, string]] : []),
          ]}
          selected={moreTab}
          onChange={(value) => setMoreTab(value as MoreTab)}
        />
        <ErrorBox message={error} />

        {moreTab === "customers" ? (
          <>
            <Card>
              <Input label="جست‌وجوی مشتری" value={customerQuery} onChangeText={setCustomerQuery} placeholder="نام، فروشگاه یا تلفن" />
              <Btn label="جست‌وجو" tone="ghost" onPress={() => void loadCustomers().catch((e) => setError(e instanceof Error ? e.message : "خطا"))} />
            </Card>
            {customers.length === 0 ? <Empty title="مشتری‌ای یافت نشد" /> : customers.map((customer) => (
              <Card key={customer.retailer_id}>
                <Text style={styles.itemTitle}>{customer.store_name || customer.full_name || customer.retailer_id}</Text>
                <Text style={styles.meta}>{customer.full_name || "—"} · {customer.phone_number || "—"}</Text>
                <Text style={styles.meta}>{customer.city || "—"} {customer.neighborhood ? "· " + customer.neighborhood : ""}</Text>
                <Text style={styles.meta}>سفارش: {numberFa(customer.order_count)} · آخرین سفارش: {dateTimeFa(customer.last_order_at)}</Text>
              </Card>
            ))}
          </>
        ) : null}

        {moreTab === "referrals" ? (
          referrals.length === 0 ? <Empty title="ارجاعی ثبت نشده" description="Referral در MVP برای attribution استفاده می‌شود؛ reward wallet در این نسخه وجود ندارد." /> : referrals.map((referral) => (
            <Card key={referral.id}>
              <View style={styles.rowBetween}>
                <StatusChip label={statusLabel(referral.status)} tone="info" />
                <Text style={styles.meta}>{referral.referral_code || "—"}</Text>
              </View>
              <Text style={styles.meta}>سازمان ارجاع‌شده: {referral.referred_organization_id || "—"}</Text>
            </Card>
          ))
        ) : null}

        {moreTab === "storefront" && props.role === "VENDOR_OWNER" ? (
          <>
            <Card>
              <View style={styles.rowBetween}>
                <View style={styles.flexOne}>
                  <Text style={styles.itemTitle}>{storefrontVendor?.name || storefrontVendor?.display_name || "ویترین بنکداری"}</Text>
                  <Text style={styles.meta}>
                    {storefrontVendor?.city ? "شهر: " + storefrontVendor.city + " · " : ""}
                    {storefrontVendor?.is_active === false ? "غیرفعال" : "ویترین فعال"}
                  </Text>
                </View>
                <Btn label="به‌روزرسانی" tone="ghost" onPress={() => void loadStorefront().catch((e) => setError(e instanceof Error ? e.message : "خطا"))} disabled={loading} />
              </View>
              <Text style={styles.meta}>این نما read-only است؛ قیمت و موجودی از بخش‌های عملیاتی خودشان مدیریت می‌شوند.</Text>
            </Card>
            {storefrontProducts.length === 0 ? (
              <Empty title="کالایی در ویترین نیست" description="کاتالوگ فعال و قیمت جاری از API دریافت نشد." />
            ) : (
              storefrontProducts.map((product) => (
                <Card key={product.id}>
                  <View style={styles.rowBetween}>
                    <Text style={styles.itemTitle}>{product.product_name || product.name || "—"}</Text>
                    {product.is_available === false ? <StatusChip label="ناموجود" tone="warn" /> : <StatusChip label="فعال" tone="ok" />}
                  </View>
                  <Text style={styles.meta}>{product.brand_name || "—"} · بسته‌بندی: {product.packaging_unit || "—"}</Text>
                  <Text style={styles.metricSmall}>{money(product.price_toman)}</Text>
                  {product.stock_quantity != null ? <Text style={styles.meta}>موجودی ویترین: {numberFa(product.stock_quantity)} {product.packaging_unit || ""}</Text> : null}
                </Card>
              ))
            )}
          </>
        ) : null}

        {moreTab === "staff" ? (
          <>
            {props.role === "VENDOR_OWNER" ? (
              <Card>
                <Text style={styles.itemTitle}>دعوت همکار</Text>
                <Input label="شماره موبایل" value={invitePhone} onChangeText={setInvitePhone} keyboardType="phone-pad" />
                <Input label="نام همکار" value={inviteName} onChangeText={setInviteName} />
                <Btn label="ارسال دعوت" onPress={() => void inviteStaff()} loading={loading} disabled={loading} />
              </Card>
            ) : (
              <Card>
                <Text style={styles.meta}>مدیریت وضعیت همکاران فقط برای مالک بنکداری مجاز است.</Text>
              </Card>
            )}
            {staff.length === 0 ? <Empty title="همکاری ثبت نشده" /> : staff.map((member) => (
              <Card key={member.membership_id}>
                <View style={styles.rowBetween}>
                  <StatusChip label={statusLabel(member.status)} tone={member.status === "ACTIVE" ? "ok" : "neutral"} />
                  <Text style={styles.itemTitle}>{member.full_name || member.user_id}</Text>
                </View>
                <Text style={styles.meta}>{member.phone_number || "—"} · {member.role || "—"}</Text>
                {props.role === "VENDOR_OWNER" && member.role !== "VENDOR_OWNER" ? (
                  <View style={styles.actionRow}>
                    <Btn label="فعال" onPress={() => void updateStaff(member.membership_id, { status: "ACTIVE" })} disabled={loading} />
                    <Btn label="تعلیق" tone="ghost" onPress={() => void updateStaff(member.membership_id, { status: "SUSPENDED" })} disabled={loading} />
                    <Btn label="لغو" tone="ghost" onPress={() => void updateStaff(member.membership_id, { status: "REVOKED" })} disabled={loading} />
                    <Btn label="مجوزها" tone="ghost" onPress={() => void loadStaffPermissions(member.membership_id)} disabled={loading} />
                  </View>
                ) : null}

                {permissionMemberId === member.membership_id && permissionDetail && props.role === "VENDOR_OWNER" ? (
                  <View style={styles.permissionPanel}>
                    <Text style={styles.itemTitle}>Effective Access</Text>
                    <Text style={styles.meta}>{numberFa(permissionDetail.effective_permissions.length)} مجوز مؤثر</Text>
                    <View style={styles.chipWrap}>
                      {permissionDetail.effective_permissions.map((permission) => <StatusChip key={permission} label={permission} tone="info" />)}
                    </View>
                    <Text style={styles.meta}>مجوزهای قابل اعطا</Text>
                    <View style={styles.chipWrap}>
                      {permissionDetail.grantable_permissions.map((permission) => (
                        <Btn key={permission} label={permission} tone={permissionKey === permission ? "primary" : "ghost"} onPress={() => setPermissionKey(permission)} />
                      ))}
                    </View>
                    <Input label="دلیل" value={permissionReason} onChangeText={setPermissionReason} />
                    <Btn label="اعطای مجوز" onPress={() => void grantStaffPermission()} loading={loading} disabled={!permissionKey || !permissionReason.trim() || loading} />
                    {permissionDetail.delegated_grants.map((grant) => (
                      <View key={grant.id} style={styles.grantRow}>
                        <StatusChip label={grant.status} tone={grant.status === "GRANTED" ? "ok" : "neutral"} />
                        <Text style={styles.meta}>{grant.permission_key}</Text>
                        {grant.status === "GRANTED" ? (
                          <Btn label="لغو" tone="ghost" onPress={() => void revokeStaffPermission(grant.permission_key)} disabled={loading || !permissionReason.trim()} />
                        ) : null}
                      </View>
                    ))}
                  </View>
                ) : null}
              </Card>
            ))}
          </>
        ) : null}
      </ScrollView>
    );
  }

  return (
    <Screen>
      <View style={styles.topBar}>
        <View>
          <Text style={styles.brand}>پل</Text>
          <Text style={styles.context}>بنکدار</Text>
        </View>
        <View style={styles.topMeta}>
          {loading ? <Text style={styles.loadingLabel}>در حال به‌روزرسانی</Text> : <Text style={styles.loadingLabel}>محیط بنکدار</Text>}
          <StatusChip label={props.role === "VENDOR_OWNER" ? "مالک" : "همکار"} tone="info" />
        </View>
      </View>

      <View style={styles.main}>
        {tab === "home" ? renderHome() : tab === "orders" ? renderOrders() : tab === "inventory" ? renderInventory() : tab === "finance" ? renderFinance() : tab === "more" ? renderMore() : <SupportMobileScreen role={props.role} />}
      </View>

      <BottomNav tab={tab} role={props.role} onChange={setTab} />
    </Screen>
  );
}

function QuickAction(props: { label: string; detail: string; onPress: () => void; tone?: "neutral" | "warn" }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <Pressable accessibilityRole="button" onPress={props.onPress} style={({ pressed }) => [styles.quickAction, props.tone === "warn" && styles.quickActionWarn, pressed && styles.navPressed]}>
      <Text style={styles.quickLabel}>{props.label}</Text>
      <Text style={styles.quickDetail}>{props.detail}</Text>
    </Pressable>
  );
}

function Segmented(props: { labels: Array<[string, string]>; selected: string; onChange: (value: string) => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <View style={styles.segmented}>
      {props.labels.map(([value, label]) => (
        <Pressable
          key={value}
          accessibilityRole="button"
          accessibilityState={{ selected: props.selected === value }}
          onPress={() => props.onChange(value)}
          style={[styles.segment, props.selected === value && styles.segmentSelected]}
        >
          <Text style={[styles.segmentText, props.selected === value && styles.segmentTextSelected]}>{label}</Text>
        </Pressable>
      ))}
    </View>
  );
}

function StatusCard(props: { status: string | null | undefined }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <Card>
      <View style={styles.rowBetween}>
        <Text style={styles.itemTitle}>وضعیت تأیید امروز</Text>
        <StatusChip label={statusLabel(props.status)} tone={props.status === "PENDING" ? "warn" : "ok"} />
      </View>
    </Card>
  );
}

function OrderCard(props: {
  order: Order;
  role: "VENDOR_OWNER" | "VENDOR_STAFF";
  onOpen: (orderId: string) => void;
  onAction: (orderId: string, action: "accept" | "preparing" | "ready") => Promise<void>;
  loading: boolean;
}): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const status = props.order.order_status ?? "";
  return (
    <Card>
      <View style={styles.rowBetween}>
        <StatusChip label={statusLabel(status)} tone={toneForOrderStatus(status)} />
        <Text style={styles.meta}>{dateTimeFa(props.order.created_at)}</Text>
      </View>
      <Text style={styles.itemTitle}>{props.order.order_number || props.order.id}</Text>
      {props.order.retailer_store_name || props.order.retailer_name ? (
        <Text style={styles.meta}>{props.order.retailer_store_name || props.order.retailer_name}</Text>
      ) : null}
      <Text style={styles.metricSmall}>{money(props.order.total_amount_toman)}</Text>
      <View style={styles.actionRow}>
        {["SUBMITTED", "CREATED"].includes(status) ? (
          <>
            {props.role === "VENDOR_OWNER" ? (
              <Btn label="پذیرش" onPress={() => void props.onAction(props.order.id, "accept")} disabled={props.loading} />
            ) : null}
            <Btn label={props.role === "VENDOR_OWNER" ? "جزئیات / رد" : "جزئیات"} tone="ghost" onPress={() => props.onOpen(props.order.id)} disabled={props.loading} />
          </>
        ) : null}
        {["ACCEPTED", "PARTIALLY_ACCEPTED"].includes(status) ? (
          <Btn label="شروع آماده‌سازی" onPress={() => void props.onAction(props.order.id, "preparing")} disabled={props.loading} />
        ) : null}
        {status === "PREPARING" ? (
          <Btn label="آماده ارسال" onPress={() => void props.onAction(props.order.id, "ready")} disabled={props.loading} />
        ) : null}
        <Btn label="جزئیات سفارش" tone="ghost" onPress={() => props.onOpen(props.order.id)} disabled={props.loading} />
      </View>
    </Card>
  );
}

function InventoryCard(props: {
  row: Inv;
  onSaveInventory: (row: Inv, value: string) => Promise<void>;
  onSavePrice: (row: Inv, value: string) => Promise<void>;
  loading: boolean;
  editablePrice: boolean;
  compact?: boolean;
}): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const [quantity, setQuantity] = useState(String(props.row.physical_quantity ?? 0));
  const [price, setPrice] = useState(String(props.row.current_price_toman ?? props.row.price_toman ?? ""));
  useEffect(() => setQuantity(String(props.row.physical_quantity ?? 0)), [props.row.physical_quantity]);
  useEffect(() => setPrice(String(props.row.current_price_toman ?? props.row.price_toman ?? "")), [props.row.current_price_toman, props.row.price_toman]);

  return (
    <Card>
      <View style={styles.rowBetween}>
        <View style={styles.flexOne}>
          <Text style={styles.itemTitle}>{props.row.product_name || props.row.id}</Text>
          <Text style={styles.meta}>
            {props.row.vendor_sku ? "SKU: " + props.row.vendor_sku : "SKU ثبت نشده"}
            {props.row.packaging_unit ? " · " + props.row.packaging_unit : ""}
            {props.row.pack_quantity ? " · " + numberFa(props.row.pack_quantity) : ""}
          </Text>
        </View>
        {props.row.is_stale === true || ["STALE", "EXPIRED"].includes(props.row.freshness_status ?? "") ? (
          <StatusChip label="نیازمند توجه" tone="warn" />
        ) : (
          <StatusChip label="عادی" tone="ok" />
        )}
      </View>

      <View style={styles.inventoryStats}>
        <Stat label="فیزیکی" value={numberFa(props.row.physical_quantity)} />
        <Stat label="رزرو" value={numberFa(props.row.reserved_quantity)} />
        <Stat label="فروش‌پذیر" value={numberFa(props.row.available_quantity)} />
      </View>

      <Input label="موجودی فیزیکی" value={quantity} onChangeText={setQuantity} keyboardType="numeric" />
      {!props.compact && props.editablePrice ? (
        <Input label="قیمت فعلی (تومان)" value={price} onChangeText={setPrice} keyboardType="numeric" />
      ) : null}
      {!props.compact && !props.editablePrice ? (
        <Text style={styles.meta}>قیمت فعلی: {money(price)}</Text>
      ) : null}

      <View style={styles.actionRow}>
        <Btn label="ذخیره موجودی" onPress={() => void props.onSaveInventory(props.row, quantity)} loading={props.loading} disabled={props.loading} />
        {!props.compact && props.editablePrice ? <Btn label="ذخیره قیمت" tone="ghost" onPress={() => void props.onSavePrice(props.row, price)} loading={props.loading} disabled={props.loading} /> : null}
      </View>
    </Card>
  );
}

function Stat(props: { label: string; value: string }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <View style={styles.stat}>
      <Text style={styles.statValue}>{props.value}</Text>
      <Text style={styles.statLabel}>{props.label}</Text>
    </View>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
    topBar: {
      flexDirection: "row",
      direction: "rtl",
      justifyContent: "space-between",
      alignItems: "center",
      paddingHorizontal: spacing.xs,
      paddingBottom: spacing.sm,
    },
    brand: { color: colors.text, fontSize: 24, fontWeight: "800", fontFamily: "Vazirmatn-Bold", lineHeight: 30 },
    context: { color: colors.textSecondary, fontSize: 11, marginTop: 2, fontFamily: "Vazirmatn-Regular", textAlign: "right" },
    topMeta: { alignItems: "flex-end", gap: spacing.xs },
    loadingLabel: { color: colors.textMuted, fontSize: 10, fontFamily: "Vazirmatn-Regular" },
    main: { flex: 1 },
    scrollContent: { paddingBottom: 120 },
    hero: {
      flexDirection: "row",
      direction: "rtl",
      justifyContent: "space-between",
      gap: spacing.md,
      backgroundColor: colors.surface,
      borderWidth: 1,
      borderColor: colors.border,
      borderRadius: 16,
      padding: spacing.lg,
      marginBottom: spacing.md,
    },
    heroCopy: { flex: 1 },
    eyebrow: { color: colors.brand, fontSize: 11, fontWeight: "700", fontFamily: "Vazirmatn-SemiBold", marginBottom: 4, textAlign: "right" },
    heroTitle: { color: colors.text, fontSize: 26, fontWeight: "800", fontFamily: "Vazirmatn-Bold", marginBottom: 4, textAlign: "right" },
    heroBody: { color: colors.textSecondary, fontSize: 13, lineHeight: 22, fontFamily: "Vazirmatn-Regular", textAlign: "right" },
    roleBadge: {
      minWidth: 56,
      height: 56,
      borderRadius: 16,
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: colors.infoBg,
      borderWidth: 1,
      borderColor: colors.brand + "33",
    },
    roleBadgeText: { color: colors.brand, fontSize: 12, fontWeight: "700", fontFamily: "Vazirmatn-SemiBold" },
    metricGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginBottom: spacing.lg },
    metricCard: {
      width: "48%",
      minHeight: 112,
      backgroundColor: colors.surface,
      borderWidth: 1,
      borderColor: colors.border,
      borderTopWidth: 3,
      borderRadius: 12,
      padding: spacing.md,
    },
    metricLabel: { color: colors.textSecondary, fontSize: 11, fontWeight: "600", fontFamily: "Vazirmatn-SemiBold", textAlign: "right" },
    metricValue: { color: colors.text, fontSize: 26, fontWeight: "800", fontFamily: "Vazirmatn-Bold", marginTop: 7, textAlign: "right" },
    metricHint: { color: colors.textMuted, fontSize: 10, lineHeight: 16, fontFamily: "Vazirmatn-Regular", marginTop: 3, textAlign: "right" },
    sectionHeader: {
      flexDirection: "row",
      direction: "rtl",
      justifyContent: "space-between",
      alignItems: "center",
      marginBottom: spacing.sm,
      marginTop: spacing.sm,
    },
    sectionTitle: { color: colors.text, fontSize: 16, fontWeight: "700", fontFamily: "Vazirmatn-SemiBold", textAlign: "right" },
    sectionAction: { color: colors.brand, fontSize: 12, fontWeight: "700", fontFamily: "Vazirmatn-SemiBold" },
    quickGrid: { gap: spacing.sm, marginBottom: spacing.lg },
    quickAction: {
      borderWidth: 1,
      borderColor: colors.border,
      borderRadius: 12,
      backgroundColor: colors.surface,
      padding: spacing.md,
    },
    quickActionWarn: { borderColor: colors.warning + "55", backgroundColor: colors.warningBg },
    quickLabel: { color: colors.text, fontSize: 14, fontWeight: "700", fontFamily: "Vazirmatn-SemiBold", textAlign: "right" },
    quickDetail: { color: colors.textSecondary, fontSize: 11, lineHeight: 18, fontFamily: "Vazirmatn-Regular", marginTop: 3, textAlign: "right" },
    pageIntro: { marginBottom: spacing.md },
    pageTitle: { color: colors.text, fontSize: 24, fontWeight: "800", fontFamily: "Vazirmatn-Bold", marginBottom: 4, textAlign: "right" },
    pageBody: { color: colors.textSecondary, fontSize: 12, lineHeight: 20, fontFamily: "Vazirmatn-Regular", textAlign: "right" },
    rowBetween: { flexDirection: "row", direction: "rtl", alignItems: "center", justifyContent: "space-between", gap: spacing.sm },
    actionRow: { flexDirection: "row", direction: "rtl", flexWrap: "wrap", gap: spacing.sm, marginTop: spacing.sm },
    itemTitle: { color: colors.text, fontSize: 14, fontWeight: "700", fontFamily: "Vazirmatn-SemiBold", marginBottom: 3, textAlign: "right" },
    metricSmall: { color: colors.text, fontSize: 20, fontWeight: "800", fontFamily: "Vazirmatn-Bold", marginTop: spacing.sm, textAlign: "right" },
    meta: { color: colors.textSecondary, fontSize: 11, lineHeight: 19, fontFamily: "Vazirmatn-Regular", textAlign: "right" },
    segmented: {
      flexDirection: "row",
      direction: "rtl",
      backgroundColor: colors.neutralBg,
      borderRadius: 10,
      padding: 3,
      marginBottom: spacing.md,
    },
    segment: { flex: 1, minHeight: 40, borderRadius: 8, alignItems: "center", justifyContent: "center", paddingHorizontal: spacing.sm },
    segmentSelected: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border },
    segmentText: { color: colors.textSecondary, fontSize: 12, fontWeight: "600", fontFamily: "Vazirmatn-SemiBold" },
    segmentTextSelected: { color: colors.text, fontWeight: "700", fontFamily: "Vazirmatn-SemiBold" },
    inventoryStats: {
      flexDirection: "row",
      direction: "rtl",
      gap: spacing.sm,
      marginTop: spacing.md,
      marginBottom: spacing.sm,
    },
    stat: {
      flex: 1,
      backgroundColor: colors.neutralBg,
      borderRadius: 8,
      padding: spacing.sm,
      minHeight: 58,
      justifyContent: "center",
    },
    statValue: { color: colors.text, fontSize: 16, fontWeight: "800", fontFamily: "Vazirmatn-Bold", textAlign: "center" },
    statLabel: { color: colors.textMuted, fontSize: 10, fontFamily: "Vazirmatn-Regular", marginTop: 2, textAlign: "center" },
    chipWrap: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginVertical: spacing.sm },
    permissionPanel: {
      borderTopWidth: StyleSheet.hairlineWidth,
      borderTopColor: colors.border,
      marginTop: spacing.md,
      paddingTop: spacing.md,
    },
    grantRow: { flexDirection: "row", direction: "rtl", alignItems: "center", gap: spacing.sm, marginTop: spacing.sm },
    flexOne: { flex: 1 },
    scanProduct: { marginTop: spacing.sm, paddingTop: spacing.sm, borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: colors.border },
    candidatePanel: { marginTop: spacing.md, paddingTop: spacing.md, borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: colors.border },
    successNote: { color: colors.success, fontSize: 12, fontFamily: "Vazirmatn-SemiBold", marginTop: spacing.sm, textAlign: "right" },
    scanResult: { marginTop: spacing.md },
    bottomNav: {
      flexDirection: "row",
      backgroundColor: colors.surface,
      borderWidth: 1,
      borderColor: colors.border,
      borderRadius: 16,
      padding: 4,
      marginTop: spacing.sm,
    },
    navItem: { flex: 1, minHeight: 48, borderRadius: 12, alignItems: "center", justifyContent: "center" },
    navItemSelected: { backgroundColor: colors.infoBg },
    navLabel: { color: colors.textSecondary, fontSize: 11, fontWeight: "600", fontFamily: "Vazirmatn-SemiBold" },
    navLabelSelected: { color: colors.brand, fontWeight: "800", fontFamily: "Vazirmatn-Bold" },
    navPressed: { opacity: 0.78 },
  });
}
