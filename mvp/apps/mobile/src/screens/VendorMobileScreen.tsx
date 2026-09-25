import React, { useCallback, useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { api } from "../api";
import { Btn, Card, Empty, ErrorBox, Input, Screen, StatusChip, Title } from "../components/ui";
import type { Role } from "../types";
import { spacing, useThemedStyles, type Palette } from "../theme";

type Order = { id: string; order_number?: string | null; order_status?: string | null; total_amount_toman?: number | string | null };
type Inv = { id: string; vendor_product_id?: string | null; product_name?: string | null; stock_quantity?: number | null; available_quantity?: number | null; reserved_quantity?: number | null };
type Invoice = { id: string; invoice_number?: string | null; status?: string | null; total_amount_toman?: number | string | null; issued_at?: string | null };
type Referral = { id: string; status?: string | null; referral_code?: string | null; referred_organization_id?: string | null };
type Settlement = { id: string; settlement_number?: string | null; status?: string | null; amount_toman?: number | string | null };
type Daily = { status?: string | null; lines?: Array<{ id: string; vendor_product_id?: string | null; product_id?: string | null; product_name?: string | null; expected_quantity?: number | null; confirmed_quantity?: number | null }> };

function rows<T>(data: unknown, key: string): T[] {
  if (Array.isArray(data)) return data as T[];
  if (!data || typeof data !== "object") return [];
  const obj = data as Record<string, unknown>;
  for (const k of [key, "items", "data", "products", "orders", "settlements"]) if (Array.isArray(obj[k])) return obj[k] as T[];
  return [];
}
function money(v: number | string | null | undefined): string {
  const n = Number(v);
  return Number.isFinite(n) ? n.toLocaleString("fa-IR") + " تومان" : "—";
}
export function VendorMobileScreen(props: { role: Extract<Role, "VENDOR_OWNER" | "VENDOR_STAFF">; onOpenOrder: (orderId: string) => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const [tab, setTab] = useState<"orders" | "inventory" | "daily" | "settlements" | "finance" | "referrals">("orders");
  const [orders, setOrders] = useState<Order[]>([]);
  const [inventory, setInventory] = useState<Inv[]>([]);
  const [settlements, setSettlements] = useState<Settlement[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [daily, setDaily] = useState<Daily | null>(null);
  const [dailyDate, setDailyDate] = useState(new Date().toISOString().slice(0, 10));
  const [dailyEdits, setDailyEdits] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadOrders = useCallback(async () => {
    const d = await api.get<unknown>("/api/v1/orders?limit=50&offset=0");
    setOrders(rows<Order>(d, "orders"));
  }, []);
  const loadInventory = useCallback(async () => {
    const d = await api.get<unknown>("/api/v1/catalog/vendors/products");
    setInventory(rows<Inv>(d, "products"));
  }, []);
  const loadSettlements = useCallback(async () => {
    const d = await api.get<unknown>("/api/v1/vendors/settlements");
    setSettlements(rows<Settlement>(d, "settlements"));
  }, []);
  const loadInvoices = useCallback(async () => { const d = await api.get<unknown>("/api/v1/invoices?limit=50&offset=0"); setInvoices(rows<Invoice>(d, "invoices")); }, []);
  const loadReferrals = useCallback(async () => { const d = await api.get<unknown>("/api/v1/referrals?limit=50&offset=0"); setReferrals(rows<Referral>(d, "referrals")); }, []);
  const loadDaily = useCallback(async () => {
    const d = await api.get<Daily>("/api/v1/inventory/daily/" + dailyDate);
    setDaily(d);
    const next: Record<string, string> = {};
    for (const line of d.lines || []) next[line.id] = String(line.confirmed_quantity ?? line.expected_quantity ?? 0);
    setDailyEdits(next);
  }, [dailyDate]);

  useEffect(() => {
    setLoading(true); setError(null);
    const p = tab === "orders" ? loadOrders() : tab === "inventory" ? loadInventory() : tab === "daily" ? loadDaily() : tab === "settlements" ? loadSettlements() : tab === "finance" ? loadInvoices() : loadReferrals();
    void p.catch((e) => setError(e instanceof Error ? e.message : "بارگذاری ناموفق بود")).finally(() => setLoading(false));
  }, [tab, loadOrders, loadInventory, loadDaily, loadSettlements, loadInvoices, loadReferrals]);

  async function action(orderId: string, actionName: "accept" | "preparing" | "ready"): Promise<void> {
    setLoading(true); setError(null);
    try { await api.post("/api/v1/orders/" + orderId + "/" + actionName, {}); await loadOrders(); }
    catch (e) { setError(e instanceof Error ? e.message : "عملیات ناموفق بود"); }
    finally { setLoading(false); }
  }
  async function saveInventory(row: Inv, raw: string): Promise<void> {
    const n = Number(raw);
    if (!Number.isFinite(n) || n < 0) { setError("موجودی باید عددی غیرمنفی باشد."); return; }
    setLoading(true); setError(null);
    try { await api.patch("/api/v1/catalog/vendors/products/" + String(row.vendor_product_id || row.id) + "/inventory", { new_physical_quantity: n }); await loadInventory(); }
    catch (e) { setError(e instanceof Error ? e.message : "ذخیره موجودی ناموفق بود"); }
    finally { setLoading(false); }
  }
  async function confirmDaily(changes: boolean): Promise<void> {
    setLoading(true); setError(null);
    try {
      if (!changes) await api.post("/api/v1/inventory/daily/" + dailyDate + "/confirm", {});
      else await api.post("/api/v1/inventory/daily/" + dailyDate + "/confirm-with-changes", { changes: (daily?.lines || []).map((x) => ({ vendor_product_id: x.vendor_product_id || x.id, declared_quantity: Number(dailyEdits[x.id] || 0) })) });
      await loadDaily();
    } catch (e) { setError(e instanceof Error ? e.message : "تأیید موجودی ناموفق بود"); }
    finally { setLoading(false); }
  }

  return (
    <Screen>
      <Title badge={props.role}>فروشنده موبایل</Title>
      <View style={styles.tabs}>
        <Btn label="صف سفارش" onPress={() => setTab("orders")} tone={tab === "orders" ? "primary" : "ghost"} />
        <Btn label="موجودی" onPress={() => setTab("inventory")} tone={tab === "inventory" ? "primary" : "ghost"} />
        <Btn label="روزانه" onPress={() => setTab("daily")} tone={tab === "daily" ? "primary" : "ghost"} />
        <Btn label="تسویه" onPress={() => setTab("settlements")} tone={tab === "settlements" ? "primary" : "ghost"} />
        <Btn label="مالی" onPress={() => setTab("finance")} tone={tab === "finance" ? "primary" : "ghost"} />
        <Btn label="ارجاع‌ها" onPress={() => setTab("referrals")} tone={tab === "referrals" ? "primary" : "ghost"} />
      </View>
      <ErrorBox message={error} />
      {loading && <Text style={styles.meta}>در حال بارگذاری…</Text>}
      {tab === "orders" ? (
        <ScrollView>{orders.length === 0 ? <Empty title="صف خالی است" /> : orders.map((o) => (
          <Card key={o.id}>
            <StatusChip label={o.order_status || "—"} tone={o.order_status === "REJECTED" ? "neutral" : "info"} />
            <Text style={styles.h2}>{o.order_number || o.id}</Text>
            <Text style={styles.metric}>{money(o.total_amount_toman)}</Text>
            <View style={styles.row}>
              {["SUBMITTED", "CREATED"].includes(o.order_status || "") ? <><Btn label="پذیرش" onPress={() => void action(o.id, "accept")} disabled={loading} /><Btn label="رد با جزئیات" tone="ghost" onPress={() => props.onOpenOrder(o.id)} disabled={loading} /></> : null}
              {["ACCEPTED", "PARTIALLY_ACCEPTED"].includes(o.order_status || "") ? <Btn label="آماده‌سازی" onPress={() => void action(o.id, "preparing")} disabled={loading} /> : null}
              {o.order_status === "PREPARING" ? <Btn label="آماده ارسال" onPress={() => void action(o.id, "ready")} disabled={loading} /> : null}
              {o.order_status === "READY" ? <Btn label="ثبت ارسال با جزئیات" onPress={() => props.onOpenOrder(o.id)} disabled={loading} /> : null}
            </View>
            <Btn label="جزئیات سفارش" tone="ghost" onPress={() => props.onOpenOrder(o.id)} />
          </Card>
        ))}</ScrollView>
      ) : tab === "inventory" ? (
        <ScrollView>{inventory.length === 0 ? <Empty title="موجودی‌ای نیست" /> : inventory.map((r) => (
          <InventoryEditor key={r.id} row={r} onSave={saveInventory} />
        ))}</ScrollView>
      ) : tab === "daily" ? (
        <ScrollView>
          <Input label="تاریخ" value={dailyDate} onChangeText={setDailyDate} />
          <Btn label="بارگذاری" tone="ghost" onPress={() => void loadDaily().catch((e) => setError(e instanceof Error ? e.message : "خطا"))} />
          {!daily?.lines?.length ? <Empty title="ردیفی نیست" /> : daily.lines.map((x) => <Card key={x.id}><Text style={styles.h2}>{x.product_name || x.id}</Text><Text style={styles.meta}>انتظار: {String(x.expected_quantity ?? 0)}</Text><Input label="تأیید" value={dailyEdits[x.id] || ""} onChangeText={(v) => setDailyEdits((p) => ({ ...p, [x.id]: v }))} keyboardType="numeric" /></Card>)}
          {daily?.lines?.length ? <><Btn label="تأیید بدون تغییر" onPress={() => void confirmDaily(false)} disabled={loading} /><Btn label="تأیید با تغییرات" tone="ghost" onPress={() => void confirmDaily(true)} disabled={loading} /></> : null}
        </ScrollView>
      ) : (
        <ScrollView>{settlements.length === 0 ? <Empty title="تسویه‌ای نیست" /> : settlements.map((s) => <Card key={s.id}><StatusChip label={s.status || "—"} tone="info" /><Text style={styles.h2}>{s.settlement_number || s.id}</Text><Text style={styles.metric}>{money(s.amount_toman)}</Text></Card>)}</ScrollView>
      )}
    </Screen>
  );
}
function InventoryEditor(props: { row: Inv; onSave: (row: Inv, raw: string) => Promise<void> }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const [value, setValue] = useState(String(props.row.stock_quantity ?? 0));
  useEffect(() => setValue(String(props.row.stock_quantity ?? 0)), [props.row.stock_quantity]);
  return (
    <Card>
      <Text style={styles.h2}>{props.row.product_name || props.row.id}</Text>
      <Text style={styles.meta}>
        در دسترس: {String(props.row.available_quantity ?? "—")} · رزرو: {String(props.row.reserved_quantity ?? "—")}
      </Text>
      <Input label="موجودی" value={value} onChangeText={setValue} keyboardType="numeric" />
      <Btn label="ذخیره" onPress={() => void props.onSave(props.row, value)} />
    </Card>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
  tabs: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginBottom: spacing.md },
  row: { flexDirection: "row", gap: spacing.sm, flexWrap: "wrap" },
  h2: { color: colors.text, fontSize: 15, fontWeight: "700", marginBottom: 4 },
  meta: { color: colors.textSecondary, fontSize: 11, lineHeight: 18 },
  metric: { color: colors.text, fontSize: 20, fontWeight: "700", marginVertical: spacing.sm },
  });
}
