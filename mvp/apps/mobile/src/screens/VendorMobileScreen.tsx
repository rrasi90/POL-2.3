import React, { useCallback, useEffect, useMemo, useState } from "react";
import { ScrollView, StyleSheet, Text, View, Pressable } from "react-native";
import { api } from "../api";
import { Btn, Card, Empty, ErrorBox, Input, Screen, StatusChip } from "../components/ui";
import type { Role } from "../types";
import { spacing, useTheme, useThemedStyles, type Palette } from "../theme";

type MainTab = "home" | "orders" | "inventory" | "finance" | "more";
type InventoryTab = "stock" | "daily";
type FinanceTab = "invoices" | "settlements";
type MoreTab = "customers" | "referrals" | "staff";

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
  const n = Number(value);
  return Number.isFinite(n) ? n.toLocaleString("fa-IR") + " تومان" : "—";
}

function numberFa(value: number | string | null | undefined): string {
  const n = Number(value);
  return Number.isFinite(n) ? n.toLocaleString("fa-IR") : "—";
}

function dateTimeFa(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("fa-IR", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(date);
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

function BottomNav(props: { tab: MainTab; onChange: (tab: MainTab) => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const items: Array<{ tab: MainTab; label: string; short: string }> = [
    { tab: "home", label: "خانه", short: "خانه" },
    { tab: "orders", label: "سفارش‌ها", short: "سفارش" },
    { tab: "inventory", label: "انبار", short: "انبار" },
    { tab: "finance", label: "مالی", short: "مالی" },
    { tab: "more", label: "بیشتر", short: "بیشتر" },
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
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [staff, setStaff] = useState<Staff[]>([]);
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [daily, setDaily] = useState<Daily | null>(null);

  const [customerQuery, setCustomerQuery] = useState("");
  const [invitePhone, setInvitePhone] = useState("");
  const [inviteName, setInviteName] = useState("");
  const [dailyDate, setDailyDate] = useState(new Date().toISOString().slice(0, 10));
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
      promise = financeTab === "invoices" ? loadInvoices() : loadSettlements();
    } else if (tab === "more") {
      promise = moreTab === "customers" ? loadCustomers() : moreTab === "referrals" ? loadReferrals() : loadStaff();
    } else if (tab === "inventory" && inventoryTab === "daily") {
      promise = loadDaily();
    } else if (tab === "orders") {
      promise = loadOrders();
    }
    if (!promise) return;
    setLoading(true);
    setError(null);
    void promise.catch((e) => setError(e instanceof Error ? e.message : "بارگذاری ناموفق بود")).finally(() => setLoading(false));
  }, [tab, financeTab, inventoryTab, moreTab, loadInvoices, loadSettlements, loadCustomers, loadReferrals, loadStaff, loadDaily, loadOrders]);

  async function orderAction(orderId: string, actionName: "accept" | "preparing" | "ready"): Promise<void> {
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
    const quantity = Number(raw);
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
    const price = Number(raw);
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
            declared_quantity: Number(dailyEdits[line.id] || 0),
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
          <QuickAction label="مالی" detail="فاکتور و تسویه" onPress={() => setTab("finance")} />
        </View>

        <SectionHeader title="سفارش‌های منتظر اقدام" action="مشاهده همه" onAction={() => setTab("orders")} />
        {pendingOrders.length === 0 ? (
          <Empty title="صف سفارش خالی است" description="در حال حاضر سفارشی برای بررسی فوری وجود ندارد." />
        ) : (
          pendingOrders.slice(0, 3).map((order) => <OrderCard key={order.id} order={order} onOpen={props.onOpenOrder} onAction={orderAction} loading={loading} />)
        )}

        <SectionHeader title="تازه‌ترین موجودی‌ها" action="مشاهده انبار" onAction={() => setTab("inventory")} />
        {inventory.length === 0 ? (
          <Empty title="کالایی ثبت نشده" description="اولین داده‌های کاتالوگ و موجودی بنکداری را از پنل عملیاتی ثبت کنید." />
        ) : (
          inventory.slice(0, 3).map((row) => <InventoryCard key={row.id} row={row} onSaveInventory={saveInventory} onSavePrice={savePrice} loading={loading} compact />)
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
          orders.map((order) => <OrderCard key={order.id} order={order} onOpen={props.onOpenOrder} onAction={orderAction} loading={loading} />)
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
        <Segmented labels={[["stock", "موجودی کالا"], ["daily", "تأیید روزانه"]]} selected={inventoryTab} onChange={(value) => setInventoryTab(value as InventoryTab)} />
        <ErrorBox message={error} />
        {inventoryTab === "stock" ? (
          inventory.length === 0 ? (
            <Empty title="موجودی‌ای ثبت نشده" description="فهرست کالاهای بنکداری از API فعلی خالی برگشت." />
          ) : (
            inventory.map((row) => <InventoryCard key={row.id} row={row} onSaveInventory={saveInventory} onSavePrice={savePrice} loading={loading} />)
          )
        ) : (
          <View>
            <Card>
              <Input label="تاریخ تأیید" value={dailyDate} onChangeText={setDailyDate} />
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
          <Text style={styles.pageTitle}>فعالیت مالی بنکداری</Text>
          <Text style={styles.pageBody}>نمایش فاکتورها و وضعیت تسویه بدون ساخت wallet یا custody جدید.</Text>
        </View>
        <Segmented labels={[["invoices", "فاکتورها"], ["settlements", "تسویه‌ها"]]} selected={financeTab} onChange={(value) => setFinanceTab(value as FinanceTab)} />
        <ErrorBox message={error} />
        {financeTab === "invoices" ? (
          invoices.length === 0 ? (
            <Empty title="فاکتوری موجود نیست" description="از API فاکتور کانونیکال، رکوردی برای این بنکداری دریافت نشد." />
          ) : (
            invoices.map((invoice) => (
              <Card key={invoice.id}>
                <View style={styles.rowBetween}>
                  <StatusChip label={statusLabel(invoice.status)} tone="info" />
                  <Text style={styles.meta}>{dateTimeFa(invoice.issued_at)}</Text>
                </View>
                <Text style={styles.itemTitle}>{invoice.invoice_number || invoice.id}</Text>
                <Text style={styles.metricSmall}>{money(invoice.total_amount_toman)}</Text>
              </Card>
            ))
          )
        ) : (
          settlements.length === 0 ? (
            <Empty title="تسویه‌ای ثبت نشده" description="وضعیت تسویه از API فعلی خالی برگشت." />
          ) : (
            settlements.map((settlement) => (
              <Card key={settlement.id}>
                <View style={styles.rowBetween}>
                  <StatusChip label={statusLabel(settlement.status)} tone={settlement.status === "PAID" ? "ok" : "info"} />
                  <Text style={styles.itemTitle}>{settlement.settlement_number || settlement.id}</Text>
                </View>
                <Text style={styles.metricSmall}>{money(settlement.amount_toman)}</Text>
              </Card>
            ))
          )
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
          labels={[["customers", "مشتریان"], ["referrals", "ارجاع"], ["staff", "همکاران"]]}
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
          {loading ? <Text style={styles.loadingLabel}>در حال به‌روزرسانی</Text> : <Text style={styles.loadingLabel}>آنلاین</Text>}
          <StatusChip label={props.role === "VENDOR_OWNER" ? "مالک" : "همکار"} tone="info" />
        </View>
      </View>

      <View style={styles.main}>
        {tab === "home" ? renderHome() : tab === "orders" ? renderOrders() : tab === "inventory" ? renderInventory() : tab === "finance" ? renderFinance() : renderMore()}
      </View>

      <BottomNav tab={tab} onChange={setTab} />
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
            <Btn label="پذیرش" onPress={() => void props.onAction(props.order.id, "accept")} disabled={props.loading} />
            <Btn label="جزئیات / رد" tone="ghost" onPress={() => props.onOpen(props.order.id)} disabled={props.loading} />
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
      {!props.compact ? <Input label="قیمت فعلی (تومان)" value={price} onChangeText={setPrice} keyboardType="numeric" /> : null}

      <View style={styles.actionRow}>
        <Btn label="ذخیره موجودی" onPress={() => void props.onSaveInventory(props.row, quantity)} loading={props.loading} disabled={props.loading} />
        {!props.compact ? <Btn label="ذخیره قیمت" tone="ghost" onPress={() => void props.onSavePrice(props.row, price)} loading={props.loading} disabled={props.loading} /> : null}
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
      justifyContent: "space-between",
      alignItems: "center",
      paddingHorizontal: spacing.xs,
      paddingBottom: spacing.sm,
    },
    brand: { color: colors.text, fontSize: 24, fontWeight: "800", lineHeight: 26 },
    context: { color: colors.textSecondary, fontSize: 11, marginTop: 2 },
    topMeta: { alignItems: "flex-end", gap: spacing.xs },
    loadingLabel: { color: colors.textMuted, fontSize: 10 },
    main: { flex: 1 },
    scrollContent: { paddingBottom: 120 },
    hero: {
      flexDirection: "row",
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
    eyebrow: { color: colors.brand, fontSize: 11, fontWeight: "700", marginBottom: 4 },
    heroTitle: { color: colors.text, fontSize: 26, fontWeight: "800", marginBottom: 4 },
    heroBody: { color: colors.textSecondary, fontSize: 13, lineHeight: 20 },
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
    roleBadgeText: { color: colors.brand, fontSize: 12, fontWeight: "700" },
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
    metricLabel: { color: colors.textSecondary, fontSize: 11, fontWeight: "600" },
    metricValue: { color: colors.text, fontSize: 26, fontWeight: "800", marginTop: 7 },
    metricHint: { color: colors.textMuted, fontSize: 10, lineHeight: 15, marginTop: 3 },
    sectionHeader: {
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "center",
      marginBottom: spacing.sm,
      marginTop: spacing.sm,
    },
    sectionTitle: { color: colors.text, fontSize: 16, fontWeight: "700" },
    sectionAction: { color: colors.brand, fontSize: 12, fontWeight: "700" },
    quickGrid: { gap: spacing.sm, marginBottom: spacing.lg },
    quickAction: {
      borderWidth: 1,
      borderColor: colors.border,
      borderRadius: 12,
      backgroundColor: colors.surface,
      padding: spacing.md,
    },
    quickActionWarn: { borderColor: colors.warning + "55", backgroundColor: colors.warningBg },
    quickLabel: { color: colors.text, fontSize: 14, fontWeight: "700" },
    quickDetail: { color: colors.textSecondary, fontSize: 11, lineHeight: 17, marginTop: 3 },
    pageIntro: { marginBottom: spacing.md },
    pageTitle: { color: colors.text, fontSize: 24, fontWeight: "800", marginBottom: 4 },
    pageBody: { color: colors.textSecondary, fontSize: 12, lineHeight: 19 },
    rowBetween: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: spacing.sm },
    actionRow: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginTop: spacing.sm },
    itemTitle: { color: colors.text, fontSize: 14, fontWeight: "700", marginBottom: 3 },
    metricSmall: { color: colors.text, fontSize: 20, fontWeight: "800", marginTop: spacing.sm },
    meta: { color: colors.textSecondary, fontSize: 11, lineHeight: 18 },
    segmented: {
      flexDirection: "row",
      backgroundColor: colors.neutralBg,
      borderRadius: 10,
      padding: 3,
      marginBottom: spacing.md,
    },
    segment: { flex: 1, minHeight: 40, borderRadius: 8, alignItems: "center", justifyContent: "center", paddingHorizontal: spacing.sm },
    segmentSelected: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border },
    segmentText: { color: colors.textSecondary, fontSize: 12, fontWeight: "600" },
    segmentTextSelected: { color: colors.text, fontWeight: "750" },
    inventoryStats: {
      flexDirection: "row",
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
    statValue: { color: colors.text, fontSize: 16, fontWeight: "800" },
    statLabel: { color: colors.textMuted, fontSize: 10, marginTop: 2 },
    chipWrap: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginVertical: spacing.sm },
    permissionPanel: {
      borderTopWidth: StyleSheet.hairlineWidth,
      borderTopColor: colors.border,
      marginTop: spacing.md,
      paddingTop: spacing.md,
    },
    grantRow: { flexDirection: "row", alignItems: "center", gap: spacing.sm, marginTop: spacing.sm },
    flexOne: { flex: 1 },
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
    navLabel: { color: colors.textSecondary, fontSize: 11, fontWeight: "600" },
    navLabelSelected: { color: colors.brand, fontWeight: "800" },
    navPressed: { opacity: 0.78 },
  });
}
