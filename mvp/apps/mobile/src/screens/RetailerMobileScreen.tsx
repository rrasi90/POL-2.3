import React, { useState } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { api } from "../api";
import { Btn, Card, Empty, ErrorBox, Input, Screen, StatusChip, Title } from "../components/ui";
import type { Role } from "../types";
import { colors, spacing } from "../theme";

type Product = {
  id: string;
  master_sku?: string | null;
  canonical_name_fa?: string | null;
  brand_name?: string | null;
  base_unit?: string | null;
  default_pack_unit?: string | null;
  default_pack_quantity?: number | null;
};
type Order = { id: string; order_number?: string | null; order_status?: string | null; total_amount_toman?: number | string | null };
type Vendor = { id: string; name?: string | null; display_name?: string | null; city?: string | null; description?: string | null; is_active?: boolean | null; product_count?: number | null };
type VendorProduct = { id: string; product_id?: string | null; product_name?: string | null; name?: string | null; brand_name?: string | null; price_toman?: number | null; stock_quantity?: number | null; packaging_unit?: string | null; is_available?: boolean | null };
type Allocation = {
  allocation_plan_id: string;
  vendor_count?: number;
  summary?: { total_items_requested?: number; total_items_allocated?: number; total_amount_toman?: number; total_items_unfulfilled?: number };
};
type Checkout = { order_group_id: string; group_status: string; total_amount_toman: number; idempotent_replay: boolean };

function rows<T>(data: unknown, key = "items"): T[] {
  if (Array.isArray(data)) return data as T[];
  if (!data || typeof data !== "object") return [];
  const obj = data as Record<string, unknown>;
  for (const k of [key, "items", "products", "orders", "data", "results"]) {
    if (Array.isArray(obj[k])) return obj[k] as T[];
  }
  return [];
}
function money(v: number | string | null | undefined): string {
  const n = Number(v);
  return Number.isFinite(n) ? n.toLocaleString("fa-IR") + " تومان" : "—";
}
function keyV4(): string {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const n = c === "x" ? r : (r & 3) | 8;
    return n.toString(16);
  });
}
export function RetailerMobileScreen(props: { role: Extract<Role, "RETAILER_OWNER" | "RETAILER_STAFF"> }): React.ReactNode {
  const [tab, setTab] = useState<"catalog" | "basket" | "orders" | "vendors">("catalog");
  const [q, setQ] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [basket, setBasket] = useState<Array<Product & { quantity: number }>>([]);
  const [serverBasketId, setServerBasketId] = useState<string | null>(null);
  const [allocation, setAllocation] = useState<Allocation | null>(null);
  const [address, setAddress] = useState("");
  const [orders, setOrders] = useState<Order[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [vendorQuery, setVendorQuery] = useState("");
  const [selectedVendor, setSelectedVendor] = useState<Vendor | null>(null);
  const [vendorProducts, setVendorProducts] = useState<VendorProduct[]>([]);
  const [checkout, setCheckout] = useState<Checkout | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function search(): Promise<void> {
    if (!q.trim()) { setError("عبارت جستجو الزامی است."); return; }
    setLoading(true); setError(null);
    try {
      const data = await api.get<unknown>("/api/v1/catalog/search?q=" + encodeURIComponent(q.trim()) + "&limit=40");
      setProducts(rows<Product>(data, "items"));
    } catch (e) { setError(e instanceof Error ? e.message : "جستجوی کاتالوگ ناموفق بود"); }
    finally { setLoading(false); }
  }

  async function createBasket(): Promise<void> {
    if (!basket.length) { setError("سبد خالی است."); return; }
    setLoading(true); setError(null);
    try {
      const created = await api.post<{ basket_id: string; version: number }>("/api/v1/baskets");
      let version = created.version;
      for (const item of basket) {
        const next = await api.post<{ basket_id: string; version: number }>(
          "/api/v1/baskets/" + created.basket_id + "/items",
          { product_id: item.id, requested_quantity: item.quantity, pack_quantity: item.default_pack_quantity && item.default_pack_quantity > 0 ? item.default_pack_quantity : 1, expected_version: version },
        );
        version = next.version;
      }
      setServerBasketId(created.basket_id);
      setAllocation(null);
      setError(null);
    } catch (e) { setError(e instanceof Error ? e.message : "ثبت سبد ناموفق بود"); }
    finally { setLoading(false); }
  }

  async function preview(): Promise<void> {
    if (!serverBasketId) { setError("ابتدا سبد را روی سرور ثبت کنید."); return; }
    setLoading(true); setError(null);
    try {
      const data = await api.post<Allocation>("/api/v1/baskets/" + serverBasketId + "/allocation-preview");
      setAllocation(data);
    } catch (e) { setError(e instanceof Error ? e.message : "بررسی تخصیص ناموفق بود"); }
    finally { setLoading(false); }
  }

  async function placeOrder(): Promise<void> {
    if (!allocation) { setError("ابتدا بررسی تخصیص را اجرا کنید."); return; }
    if (address.trim().length < 5) { setError("آدرس تحویل باید حداقل ۵ نویسه باشد."); return; }
    setLoading(true); setError(null);
    try {
      const data = await api.post<Checkout>("/api/v1/orders", {
        allocation_plan_id: allocation.allocation_plan_id,
        delivery_address: address.trim(),
        preferred_payment_method: "CASH_ON_DELIVERY",
      }, { headers: { "Idempotency-Key": keyV4() } });
      setCheckout(data);
      setBasket([]);
      setServerBasketId(null);
      setAllocation(null);
      setAddress("");
      setTab("orders");
      await loadOrders();
    } catch (e) { setError(e instanceof Error ? e.message : "ثبت سفارش ناموفق بود"); }
    finally { setLoading(false); }
  }

  async function loadOrders(): Promise<void> {
    try {
      const data = await api.get<unknown>("/api/v1/orders?limit=50&offset=0");
      setOrders(rows<Order>(data, "orders"));
    } catch (e) { setError(e instanceof Error ? e.message : "دریافت سفارش‌ها ناموفق بود"); }
  }

  async function loadVendors(): Promise<void> {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<unknown>("/api/v1/storefront/vendors");
      setVendors(rows<Vendor>(data, "items"));
    } catch (e) { setError(e instanceof Error ? e.message : "دریافت فروشندگان ناموفق بود"); }
    finally { setLoading(false); }
  }

  async function loadVendor(vendorId: string): Promise<void> {
    setLoading(true);
    setError(null);
    try {
      const [vendor, products] = await Promise.all([
        api.get<Vendor>("/api/v1/storefront/vendors/" + vendorId),
        api.get<unknown>("/api/v1/storefront/vendors/" + vendorId + "/products"),
      ]);
      setSelectedVendor(vendor);
      setVendorProducts(rows<VendorProduct>(products, "items"));
    } catch (e) { setError(e instanceof Error ? e.message : "دریافت ویترین ناموفق بود"); }
    finally { setLoading(false); }
  }

  function addVendorProduct(item: VendorProduct): void {
    if (!item.product_id) {
      setError("شناسه Master Product از ویترین دریافت نشد؛ کالا به سبد اضافه نشد.");
      return;
    }
    const product: Product = {
      id: String(item.product_id),
      canonical_name_fa: item.product_name || item.name || null,
      brand_name: item.brand_name,
      master_sku: null,
      base_unit: null,
      default_pack_unit: item.packaging_unit,
      default_pack_quantity: null,
    };
    add(product);
  }

  function add(item: Product): void {
    setBasket((prev) => {
      const found = prev.find((x) => x.id === item.id);
      return found ? prev.map((x) => x.id === item.id ? { ...x, quantity: x.quantity + 1 } : x) : prev.concat({ ...item, quantity: 1 });
    });
    setError(null);
  }

  return (
    <Screen>
      <Title badge={props.role}>ریتیلر موبایل</Title>
      <View style={styles.tabs}>
        <Btn label="کاتالوگ" onPress={() => setTab("catalog")} tone={tab === "catalog" ? "primary" : "ghost"} />
        <Btn label={"سبد (" + basket.length + ")"} onPress={() => setTab("basket")} tone={tab === "basket" ? "primary" : "ghost"} />
        <Btn label="سفارش‌ها" onPress={() => { setTab("orders"); void loadOrders(); }} tone={tab === "orders" ? "primary" : "ghost"} />
        <Btn label="فروشندگان" onPress={() => { setTab("vendors"); void loadVendors(); }} tone={tab === "vendors" ? "primary" : "ghost"} />
      </View>
      <ErrorBox message={error} />
      {tab === "vendors" ? (
        <ScrollView>
          <Input label="جستجوی فروشنده" placeholder="نام یا شهر…" value={vendorQuery} onChangeText={setVendorQuery} />
          <Btn label="بارگذاری فروشندگان" onPress={() => void loadVendors()} loading={loading} />
          {!selectedVendor ? (
            <>
              {vendors.filter((v) => {
                const needle = vendorQuery.trim().toLowerCase();
                if (!needle) return true;
                return (v.name || v.display_name || "").toLowerCase().includes(needle)
                  || (v.city || "").toLowerCase().includes(needle)
                  || String(v.id).toLowerCase().includes(needle);
              }).length === 0 ? <Empty title="فروشنده‌ای یافت نشد" /> :
                vendors.filter((v) => {
                  const needle = vendorQuery.trim().toLowerCase();
                  if (!needle) return true;
                  return (v.name || v.display_name || "").toLowerCase().includes(needle)
                    || (v.city || "").toLowerCase().includes(needle)
                    || String(v.id).toLowerCase().includes(needle);
                }).map((v) => (
                  <Card key={v.id}>
                    <StatusChip label={v.is_active === false ? "غیرفعال" : "فعال"} tone={v.is_active === false ? "neutral" : "ok"} />
                    <Text style={styles.h2}>{v.name || v.display_name || v.id}</Text>
                    <Text style={styles.meta}>{v.city || "—"} · کالا: {String(v.product_count || 0)}</Text>
                    <Btn label="باز کردن ویترین" onPress={() => void loadVendor(v.id)} loading={loading} />
                  </Card>
                ))}
            </>
          ) : (
            <>
              <Btn label="بازگشت به فهرست فروشندگان" tone="ghost" onPress={() => setSelectedVendor(null)} />
              <Card>
                <StatusChip label={selectedVendor.is_active === false ? "غیرفعال" : "فعال"} tone={selectedVendor.is_active === false ? "neutral" : "ok"} />
                <Text style={styles.h2}>{selectedVendor.name || selectedVendor.display_name || selectedVendor.id}</Text>
                <Text style={styles.meta}>{selectedVendor.city || "—"}</Text>
                {selectedVendor.description ? <Text style={styles.body}>{selectedVendor.description}</Text> : null}
              </Card>
              {vendorProducts.length === 0 ? <Empty title="کالایی در ویترین نیست" /> : vendorProducts.map((p) => (
                <Card key={p.id}>
                  <StatusChip label={p.is_available === false ? "ناموجود" : "موجود"} tone={p.is_available === false ? "warn" : "ok"} />
                  <Text style={styles.h2}>{p.product_name || p.name || p.id}</Text>
                  <Text style={styles.meta}>{p.brand_name || ""} · {p.packaging_unit || ""}</Text>
                  <Text style={styles.metric}>{money(p.price_toman)}</Text>
                  <Text style={styles.meta}>موجودی: {String(p.stock_quantity ?? "—")}</Text>
                  <Btn label="افزودن به سبد" onPress={() => addVendorProduct(p)} disabled={p.is_available === false} />
                </Card>
              ))}
            </>
          )}
        </ScrollView>
      ) : tab === "catalog" ? (
        <ScrollView>
          <Input label="جستجوی کاتالوگ" placeholder="نام کالا یا SKU…" value={q} onChangeText={setQ} />
          <Btn label="جستجو" onPress={() => void search()} loading={loading} disabled={!q.trim()} />
          {products.length === 0 ? <Empty title="نتیجه‌ای نیست" description="عبارت جستجو را وارد کنید." /> :
            products.map((p) => (
              <Card key={p.id}>
                <Text style={styles.h2}>{p.canonical_name_fa || "—"}</Text>
                <Text style={styles.meta}>{p.master_sku || ""}</Text>
                <Text style={styles.meta}>{p.brand_name || ""}</Text>
                <Btn label="افزودن به سبد" onPress={() => add(p)} />
              </Card>
            ))}
        </ScrollView>
      ) : tab === "basket" ? (
        <ScrollView>
          {basket.length === 0 ? <Empty title="سبد خالی است" description="از کاتالوگ کالا اضافه کنید." /> :
            basket.map((x) => (
              <Card key={x.id}>
                <Text style={styles.h2}>{x.canonical_name_fa || "—"}</Text>
                <Text style={styles.meta}>تعداد: {x.quantity.toLocaleString("fa-IR")}</Text>
                <View style={styles.row}>
                  <Btn label="+" onPress={() => setBasket((p) => p.map((z) => z.id === x.id ? { ...z, quantity: z.quantity + 1 } : z))} />
                  <Btn label="−" tone="ghost" onPress={() => setBasket((p) => p.flatMap((z) => z.id !== x.id ? [z] : z.quantity > 1 ? [{ ...z, quantity: z.quantity - 1 }] : []))} />
                </View>
              </Card>
            ))}
          <Btn label="ثبت سبد روی سرور" onPress={() => void createBasket()} loading={loading} disabled={!basket.length || loading} />
          <Btn label="بررسی تخصیص" onPress={() => void preview()} tone="ghost" loading={loading} disabled={!serverBasketId || loading} />
          {allocation ? (
            <Card>
              <StatusChip label={"فروشنده: " + String(allocation.vendor_count || 0)} tone="info" />
              <Text style={styles.body}>درخواست: {String(allocation.summary?.total_items_requested || 0)} · تخصیص: {String(allocation.summary?.total_items_allocated || 0)}</Text>
              <Text style={styles.metric}>{money(allocation.summary?.total_amount_toman)}</Text>
              <Input label="آدرس تحویل" value={address} onChangeText={setAddress} multiline numberOfLines={3} />
              <Btn label="ثبت سفارش" onPress={() => void placeOrder()} loading={loading} disabled={loading} />
            </Card>
          ) : null}
        </ScrollView>
      ) : (
        <ScrollView>
          {checkout ? <Card><StatusChip label={checkout.group_status} tone="ok" /><Text style={styles.h2}>آخرین گروه سفارش</Text><Text selectable style={styles.meta}>{checkout.order_group_id}</Text><Text style={styles.metric}>{money(checkout.total_amount_toman)}</Text></Card> : null}
          {orders.length === 0 ? <Empty title="سفارشی نیست" /> : orders.map((o) => (
            <Card key={o.id}>
              <StatusChip label={o.order_status || "—"} tone={o.order_status === "DELIVERED" ? "ok" : "info"} />
              <Text style={styles.h2}>{o.order_number || o.id}</Text>
              <Text style={styles.metric}>{money(o.total_amount_toman)}</Text>
              <Btn label="جزئیات سفارش" tone="ghost" onPress={() => props.onOpenOrder(o.id)} />
            </Card>
          ))}
        </ScrollView>
      )}
    </Screen>
  );
}
const styles = StyleSheet.create({
  tabs: { flexDirection: "row", gap: spacing.sm, flexWrap: "wrap", marginBottom: spacing.md },
  row: { flexDirection: "row", gap: spacing.sm, flexWrap: "wrap" },
  h2: { color: colors.text, fontSize: 15, fontWeight: "700", marginBottom: 4 },
  body: { color: colors.textSecondary, fontSize: 13, lineHeight: 20 },
  meta: { color: colors.textSecondary, fontSize: 11, lineHeight: 18 },
  metric: { color: colors.text, fontSize: 20, fontWeight: "700", marginVertical: spacing.sm },
});
