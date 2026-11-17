import React, { useEffect, useMemo, useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { api, ApiError } from "../api";
import { Btn, Card, Empty, ErrorBox, IconBadge, Input, Screen, StatusChip } from "../components/ui";
import type { Role } from "../types";
import { spacing, useTheme, useThemedStyles, type Palette } from "../theme";
import { SupportMobileScreen } from "./SupportMobileScreen";

type Product = {
  id: string;
  master_sku?: string | null;
  canonical_name_fa?: string | null;
  brand_name?: string | null;
  base_unit?: string | null;
  default_pack_unit?: string | null;
  default_pack_quantity?: number | null;
};
type Invoice = { id: string; invoice_number?: string | null; status?: string | null; total_amount_toman?: number | string | null; issued_at?: string | null };
type Order = { id: string; order_number?: string | null; order_status?: string | null; total_amount_toman?: number | string | null };
type Vendor = { id: string; name?: string | null; display_name?: string | null; city?: string | null; description?: string | null; is_active?: boolean | null; product_count?: number | null };
type VendorProduct = { id: string; product_id?: string | null; product_name?: string | null; name?: string | null; brand_name?: string | null; price_toman?: number | null; stock_quantity?: number | null; packaging_unit?: string | null; is_available?: boolean | null };
type Allocation = {
  allocation_plan_id: string;
  basket_version?: number;
  vendor_count?: number;
  summary?: { total_items_requested?: number; total_items_allocated?: number; total_amount_toman?: number; total_items_unfulfilled?: number };
};
type Checkout = { order_group_id: string; group_status: string; total_amount_toman: number; idempotent_replay: boolean };
type Tab = "home" | "categories" | "products" | "basket" | "orders" | "vendors" | "support" | "finance";

const categories = [
  ["🥫", "مواد غذایی", "brand"],
  ["🥤", "نوشیدنی‌ها", "success"],
  ["🧴", "بهداشت و سلامت", "warning"],
  ["🧼", "شوینده و نظافت", "danger"],
  ["🧻", "کاغذی و سلولزی", "brand"],
  ["🍫", "تنقلات و شیرینی", "warning"],
  ["👶", "کالاهای کودک", "success"],
  ["📦", "سایر کالاها", "neutral"],
] as const;

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
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const n = c === "x" ? r : (r & 3) | 8;
    return n.toString(16);
  });
}

export function RetailerMobileScreen(props: {
  role: Extract<Role, "RETAILER_OWNER" | "RETAILER_STAFF">;
  onOpenOrder: (orderId: string) => void;
  onOpenAccount?: () => void;
}): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const { colors } = useTheme();
  const [tab, setTab] = useState<Tab>("home");
  const [q, setQ] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [basket, setBasket] = useState<Array<Product & { quantity: number }>>([]);
  const [serverBasketId, setServerBasketId] = useState<string | null>(null);
  const [serverBasketVersion, setServerBasketVersion] = useState<number | null>(null);
  const [allocation, setAllocation] = useState<Allocation | null>(null);
  const [address, setAddress] = useState("");
  const [orders, setOrders] = useState<Order[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [vendorQuery, setVendorQuery] = useState("");
  const [selectedVendor, setSelectedVendor] = useState<Vendor | null>(null);
  const [vendorProducts, setVendorProducts] = useState<VendorProduct[]>([]);
  const [checkout, setCheckout] = useState<Checkout | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (tab === "orders") void loadOrders();
  }, [tab]);

  async function search(nextQuery = q): Promise<void> {
    const query = nextQuery.trim();
    if (!query) {
      setError("عبارت جستجو الزامی است.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<unknown>("/api/v1/catalog/search?q=" + encodeURIComponent(query) + "&limit=40");
      setProducts(rows<Product>(data, "items"));
      setSelectedProduct(null);
      setTab("products");
    } catch (e) {
      setError(e instanceof Error ? e.message : "جستجوی کاتالوگ ناموفق بود");
    } finally {
      setLoading(false);
    }
  }

  async function createBasket(): Promise<void> {
    if (!basket.length) { setError("سبد خالی است."); return; }
    setLoading(true);
    setError(null);
    try {
      const created = await api.post<{ basket_id: string; version: number }>("/api/v1/baskets");
      let version = created.version;
      for (const item of basket) {
        const next = await api.post<{ basket_id: string; version: number }>(
          "/api/v1/baskets/" + created.basket_id + "/items",
          {
            product_id: item.id,
            requested_quantity: item.quantity,
            pack_quantity: item.default_pack_quantity && item.default_pack_quantity > 0 ? item.default_pack_quantity : 1,
            expected_version: version,
          },
        );
        version = next.version;
      }
      setServerBasketId(created.basket_id);
      setServerBasketVersion(version);
      setAllocation(null);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "ثبت سبد ناموفق بود");
    } finally {
      setLoading(false);
    }
  }

  async function preview(): Promise<void> {
    if (!serverBasketId) { setError("ابتدا سبد را روی سرور ثبت کنید."); return; }
    setLoading(true);
    setError(null);
    try {
      const data = await api.post<Allocation>("/api/v1/baskets/" + serverBasketId + "/allocation-preview");
      setAllocation(data);
      if (typeof data.basket_version === "number") setServerBasketVersion(data.basket_version);
    } catch (e) {
      setError(e instanceof Error ? e.message : "بررسی تخصیص ناموفق بود");
    } finally {
      setLoading(false);
    }
  }

  async function placeOrder(): Promise<void> {
    if (!allocation) { setError("ابتدا بررسی تخصیص را اجرا کنید."); return; }
    if (address.trim().length < 5) {
      setError("آدرس تحویل باید حداقل ۵ نویسه باشد.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await api.post<Checkout>(
        "/api/v1/orders",
        {
          allocation_plan_id: allocation.allocation_plan_id,
          delivery_address: address.trim(),
          preferred_payment_method: "CASH_ON_DELIVERY",
        },
        { headers: { "Idempotency-Key": keyV4() } },
      );
      setCheckout(data);
      setShowSuccess(true);
      setBasket([]);
      setServerBasketId(null);
      setServerBasketVersion(null);
      setAllocation(null);
      setAddress("");
      await loadOrders();
    } catch (e) {
      if (e instanceof ApiError && e.status === 409 && e.code === "CONFLICT") {
        try {
          const current = await api.get<{
            basket_id: string;
            version: number;
            status: string;
            items: Array<{
              id: string;
              product_id: string;
              master_sku?: string | null;
              canonical_name_fa?: string | null;
              requested_quantity: number;
              requested_unit?: string | null;
              pack_quantity?: number | null;
            }>;
          }>("/api/v1/baskets/current");
          const previousByProduct = new Map(basket.map((item) => [item.id, item]));
          setServerBasketId(current.basket_id);
          setServerBasketVersion(current.version);
          setAllocation(null);
          setBasket(
            current.items.map((item) => ({
              ...(previousByProduct.get(item.product_id) || {
                id: item.product_id,
                canonical_name_fa: item.canonical_name_fa,
                master_sku: item.master_sku,
              }),
              id: item.product_id,
              quantity: item.requested_quantity,
              default_pack_quantity: item.pack_quantity,
              default_pack_unit: item.requested_unit,
            })),
          );
          setError("سبد روی سرور تغییر کرده است؛ تخصیص قبلی باطل شد و نسخه جدید بارگذاری شد.");
        } catch {
          setAllocation(null);
          setError("نسخه سبد تغییر کرده است؛ تخصیص قبلی باطل شد. سبد فعلی را دوباره بارگذاری کنید.");
        }
      } else {
        setError(e instanceof Error ? e.message : "ثبت سفارش ناموفق بود");
      }
    } finally {
      setLoading(false);
    }
  }

  async function loadOrders(): Promise<void> {
    try {
      const data = await api.get<unknown>("/api/v1/orders?limit=50&offset=0");
      setOrders(rows<Order>(data, "orders"));
    } catch (e) {
      setError(e instanceof Error ? e.message : "دریافت سفارش‌ها ناموفق بود");
    }
  }

  async function loadInvoices(): Promise<void> {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<unknown>("/api/v1/invoices?limit=50&offset=0");
      setInvoices(rows<Invoice>(data, "invoices"));
    } catch (e) {
      setError(e instanceof Error ? e.message : "دریافت صورتحساب‌ها ناموفق بود");
    } finally {
      setLoading(false);
    }
  }

  async function loadVendors(): Promise<void> {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<unknown>("/api/v1/storefront/vendors");
      setVendors(rows<Vendor>(data, "items"));
    } catch (e) {
      setError(e instanceof Error ? e.message : "دریافت فروشندگان ناموفق بود");
    } finally {
      setLoading(false);
    }
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
    } catch (e) {
      setError(e instanceof Error ? e.message : "دریافت ویترین ناموفق بود");
    } finally {
      setLoading(false);
    }
  }

  function add(item: Product): void {
    setBasket((prev) => {
      const found = prev.find((x) => x.id === item.id);
      return found
        ? prev.map((x) => (x.id === item.id ? { ...x, quantity: x.quantity + 1 } : x))
        : prev.concat({ ...item, quantity: 1 });
    });
    setError(null);
  }

  function addVendorProduct(item: VendorProduct): void {
    if (!item.product_id) {
      setError("شناسهٔ کالای اصلی از ویترین دریافت نشد؛ کالا به سبد اضافه نشد.");
      return;
    }
    add({
      id: String(item.product_id),
      canonical_name_fa: item.product_name || item.name || null,
      brand_name: item.brand_name,
      master_sku: null,
      base_unit: null,
      default_pack_unit: item.packaging_unit,
      default_pack_quantity: null,
    });
  }

  function changeQty(id: string, delta: number): void {
    setBasket((prev) =>
      prev.flatMap((item) => {
        if (item.id !== id) return [item];
        const quantity = item.quantity + delta;
        return quantity > 0 ? [{ ...item, quantity }] : [];
      }),
    );
  }

  const basketTotal = useMemo(() => basket.reduce((sum, x) => sum + x.quantity, 0), [basket]);

  function categoryPress(label: string): void {
    setQ(label);
    void search(label);
  }

  function home(): React.ReactNode {
    return (
      <>
        <View style={styles.header}>
          <View style={styles.brandBlock}>
            <View style={styles.logo}><Text style={styles.logoText}>پل</Text></View>
            <View>
              <Text style={styles.brandName}>پل</Text>
              <Text style={styles.brandSub}>بازار عمده برای مغازه شما</Text>
            </View>
          </View>
          <Pressable onPress={props.onOpenAccount} style={styles.profileButton} accessibilityRole="button">
            <Text style={styles.profileIcon}>◯</Text>
          </Pressable>
        </View>

        <View style={styles.locationRow}>
          <View>
            <Text style={styles.eyebrow}>موقعیت فعلی</Text>
            <Text style={styles.locationText}>اهواز</Text>
          </View>
          <Pressable style={styles.locationButton} accessibilityRole="button">
            <Text style={styles.locationButtonText}>تغییر شهر</Text>
          </Pressable>
        </View>

        <View style={styles.searchBox}>
          <Text style={styles.searchIcon}>⌕</Text>
          <Input
            label=""
            value={q}
            onChangeText={setQ}
            placeholder="جست‌وجوی کالا، برند یا شناسهٔ کالا…"
            onSubmitEditing={() => void search()}
            returnKeyType="search"
            style={styles.searchInput}
          />
        </View>
        <Btn label="جستجوی کالا" onPress={() => void search()} loading={loading} disabled={!q.trim()} />

        <Card style={styles.heroCard}>
          <View style={styles.heroCopy}>
            <Text style={styles.heroKicker}>خرید عمده سریع‌تر و آسان‌تر</Text>
            <Text style={styles.heroTitle}>قیمت و موجودی را یکجا ببینید</Text>
            <Text style={styles.heroBody}>از چند فروشنده مقایسه کنید و یک سفارش کامل بسازید.</Text>
          </View>
          <View style={styles.heroArt}>
            <Text style={styles.heroCarton}>▦</Text>
            <Text style={styles.heroBag}>▥</Text>
          </View>
        </Card>

        <SectionTitle title="دسته‌بندی کالاها" action="مشاهده همه" onPress={() => setTab("categories")} />
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.categoryRow}>
          {categories.slice(0, 6).map(([icon, label, tone]) => (
            <Pressable key={label} onPress={() => categoryPress(label)} style={styles.categoryCard}>
              <IconBadge symbol={icon} tone={tone} />
              <Text style={styles.categoryText}>{label}</Text>
            </Pressable>
          ))}
        </ScrollView>

        <SectionTitle title="پیشنهادهای ویژه" action="مشاهده همه" onPress={() => setTab("products")} />
        {products.length ? (
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.productRow}>
            {products.slice(0, 6).map((p) => <ProductMiniCard key={p.id} product={p} onOpen={() => setSelectedProduct(p)} onAdd={() => add(p)} />)}
          </ScrollView>
        ) : (
          <Card style={styles.emptyCommerce}>
            <Text style={styles.emptyCommerceTitle}>کالاهای منتخب اینجا نمایش داده می‌شوند</Text>
            <Text style={styles.emptyCommerceBody}>یک کالا، برند یا SKU جستجو کنید تا کارت‌های واقعی کاتالوگ اینجا قرار بگیرند.</Text>
          </Card>
        )}

        <SectionTitle title="دسترسی سریع" />
        <View style={styles.quickGrid}>
          <QuickAction icon="🏪" label="بنکداران" onPress={() => { setTab("vendors"); void loadVendors(); }} />
          <QuickAction icon="🧾" label="فاکتورها" onPress={() => { setTab("finance"); void loadInvoices(); }} />
          <QuickAction icon="🎧" label="پشتیبانی" onPress={() => setTab("support")} />
        </View>
      </>
    );
  }

  function categoriesPage(): React.ReactNode {
    return (
      <>
        <PageHeader title="دسته‌بندی کالاها" onBack={() => setTab("home")} />
        <Input label="جستجو" value={q} onChangeText={setQ} placeholder="مثلاً نوشیدنی یا تنقلات…" onSubmitEditing={() => void search()} />
        <View style={styles.categoryList}>
          {categories.map(([icon, label, tone]) => (
            <Pressable key={label} onPress={() => categoryPress(label)} style={styles.categoryListItem}>
              <Text style={styles.chevron}>‹</Text>
              <Text style={styles.categoryListText}>{label}</Text>
              <IconBadge symbol={icon} tone={tone} />
            </Pressable>
          ))}
        </View>
      </>
    );
  }

  function productsPage(): React.ReactNode {
    return (
      <>
        <PageHeader title="لیست محصولات" onBack={() => setTab("home")} />
        <Input label="جستجوی کالا" value={q} onChangeText={setQ} placeholder="نام یا شناسهٔ کالا…" onSubmitEditing={() => void search()} />
        <Btn label="جستجو" onPress={() => void search()} loading={loading} disabled={!q.trim()} />
        <View style={styles.resultHeader}>
          <Text style={styles.meta}>{products.length.toLocaleString("fa-IR")} کالا</Text>
          <StatusChip label="مرتبط‌ترین" tone="info" />
        </View>
        {products.length === 0 ? (
          <Empty title="نتیجه‌ای نیست" description="عبارت جستجو را وارد کنید." />
        ) : (
          products.map((p) => <ProductRow key={p.id} product={p} onOpen={() => setSelectedProduct(p)} onAdd={() => add(p)} />)
        )}
      </>
    );
  }

  function productDetail(): React.ReactNode {
    if (!selectedProduct) return null;
    return (
      <>
        <PageHeader title="جزئیات محصول" onBack={() => setSelectedProduct(null)} />
        <Card style={styles.productHero}>
          <View style={styles.productVisual}><Text style={styles.productEmoji}>🛍️</Text></View>
          <View style={styles.productHeroCopy}>
            <Text style={styles.productTitle}>{selectedProduct.canonical_name_fa || "بدون نام"}</Text>
            <Text style={styles.meta}>{selectedProduct.brand_name || "برند ثبت نشده"}</Text>
            <Text style={styles.sku}>{selectedProduct.master_sku || selectedProduct.id}</Text>
          </View>
        </Card>
        <Card>
          <Text style={styles.sectionCardTitle}>اطلاعات محصول</Text>
          <InfoRow label="واحد پایه" value={selectedProduct.base_unit || "—"} />
          <InfoRow label="نوع بسته‌بندی" value={selectedProduct.default_pack_unit || "—"} />
          <InfoRow label="تعداد در بسته" value={String(selectedProduct.default_pack_quantity ?? "—")} />
        </Card>
        <Card style={styles.priceCard}>
          <Text style={styles.meta}>قیمت از ویترین فروشندگان</Text>
          <Text style={styles.priceLarge}>مقایسه و انتخاب</Text>
          <Btn label="افزودن به سبد خرید" onPress={() => { add(selectedProduct); setSelectedProduct(null); setTab("basket"); }} />
        </Card>
      </>
    );
  }

  function basketPage(): React.ReactNode {
    return (
      <>
        <PageHeader title="سبد خرید" onBack={() => setTab("home")} action={basket.length ? "پاک کردن همه" : undefined} onAction={basket.length ? () => setBasket([]) : undefined} />
        {basket.length === 0 ? (
          <Empty title="سبد خالی است" description="از کاتالوگ کالا اضافه کنید." />
        ) : (
          basket.map((x) => (
            <Card key={x.id} style={styles.cartCard}>
              <View style={styles.cartVisual}><Text style={styles.cartEmoji}>📦</Text></View>
              <View style={styles.cartMain}>
                <Text style={styles.productTitle}>{x.canonical_name_fa || "—"}</Text>
                <Text style={styles.meta}>{x.brand_name || ""} · {x.default_pack_unit || "بسته"}</Text>
                <View style={styles.qtyRow}>
                  <Pressable onPress={() => changeQty(x.id, 1)} style={styles.qtyButton}><Text style={styles.qtyText}>+</Text></Pressable>
                  <Text style={styles.qtyValue}>{x.quantity.toLocaleString("fa-IR")}</Text>
                  <Pressable onPress={() => changeQty(x.id, -1)} style={styles.qtyButtonSecondary}><Text style={styles.qtyTextSecondary}>−</Text></Pressable>
                </View>
              </View>
            </Card>
          ))
        )}

        {checkout && !showSuccess ? (
          <Card style={styles.checkoutCard}>
            <StatusChip label={"فروشنده: " + String(allocation?.vendor_count || 0)} tone="info" />
            <Text style={styles.sectionCardTitle}>خلاصه سفارش</Text>
            <Text style={styles.meta}>اقلام درخواستی: {String(allocation?.summary?.total_items_requested || 0)}</Text>
            <Text style={styles.meta}>تخصیص‌یافته: {String(allocation?.summary?.total_items_allocated || 0)}</Text>
            <Text style={styles.priceLarge}>{money(allocation?.summary?.total_amount_toman)}</Text>
          </Card>
        ) : null}

        {!allocation && basket.length ? (
          <View style={styles.actionStack}>
            <Btn label="ثبت سبد روی سرور" onPress={() => void createBasket()} loading={loading} disabled={loading} />
            <Btn label="بررسی تخصیص" onPress={() => void preview()} tone="ghost" loading={loading} disabled={!serverBasketId || loading} />
          </View>
        ) : null}

        {allocation && !showSuccess ? (
          <Card style={styles.checkoutCard}>
            <StatusChip label={(allocation.vendor_count || 0).toLocaleString("fa-IR") + " فروشنده"} tone="info" />
            <Text style={styles.sectionCardTitle}>تایید سفارش</Text>
            <Text style={styles.meta}>جمع تقریبی سفارش</Text>
            <Text style={styles.priceLarge}>{money(allocation.summary?.total_amount_toman)}</Text>
            <Input label="آدرس تحویل" value={address} onChangeText={setAddress} multiline numberOfLines={3} placeholder="آدرس کامل فروشگاه…" />
            <Btn label="ثبت نهایی سفارش" onPress={() => void placeOrder()} loading={loading} disabled={loading} />
          </Card>
        ) : null}
      </>
    );
  }

  function successPage(): React.ReactNode {
    return (
      <>
        <View style={styles.successWrap}>
          <View style={styles.successIcon}><Text style={styles.successCheck}>✓</Text></View>
          <Text style={styles.successTitle}>سفارش شما ثبت شد!</Text>
          <Text style={styles.successBody}>سفارش با موفقیت ثبت شد و از همین‌جا می‌توانید وضعیت آن را پیگیری کنید.</Text>
          {checkout ? <Text selectable style={styles.orderCode}>{checkout.order_group_id}</Text> : null}
          {checkout ? <Text style={styles.priceLarge}>{money(checkout.total_amount_toman)}</Text> : null}
          <Btn label="مشاهده سفارش‌ها" onPress={() => { setShowSuccess(false); setTab("orders"); void loadOrders(); }} />
          <Btn label="بازگشت به خانه" tone="ghost" onPress={() => { setShowSuccess(false); setTab("home"); }} />
        </View>
      </>
    );
  }

  function ordersPage(): React.ReactNode {
    return (
      <>
        <PageHeader title="سفارش‌های من" onBack={() => setTab("home")} />
        <View style={styles.orderFilters}>
          <StatusChip label="همه" tone="info" />
          <StatusChip label="در حال بررسی" />
          <StatusChip label="در حال ارسال" />
          <StatusChip label="تحویل شده" tone="ok" />
        </View>
        {orders.length === 0 ? (
          <Empty title="سفارشی نیست" description="سفارش‌های ثبت‌شده شما اینجا نمایش داده می‌شوند." />
        ) : (
          orders.map((o) => (
            <Pressable key={o.id} onPress={() => props.onOpenOrder(o.id)} accessibilityRole="button">
              <Card style={styles.orderCard}>
                <View style={styles.orderTop}>
                  <StatusChip label={o.order_status || "—"} tone={o.order_status === "DELIVERED" ? "ok" : "info"} />
                  <Text style={styles.orderNumber}>{o.order_number || o.id}</Text>
                </View>
                <Text style={styles.priceMedium}>{money(o.total_amount_toman)}</Text>
                <Text style={styles.meta}>برای مشاهده جزئیات و خط زمانی سفارش لمس کنید.</Text>
              </Card>
            </Pressable>
          ))
        )}
      </>
    );
  }

  function vendorsPage(): React.ReactNode {
    const filtered = vendors.filter((v) => {
      const needle = vendorQuery.trim().toLowerCase();
      if (!needle) return true;
      return (v.name || v.display_name || "").toLowerCase().includes(needle)
        || (v.city || "").toLowerCase().includes(needle)
        || String(v.id).toLowerCase().includes(needle);
    });
    if (selectedVendor) {
      return (
        <>
          <PageHeader title="ویترین بنکدار" onBack={() => setSelectedVendor(null)} />
          <Card style={styles.vendorHero}>
            <View style={styles.vendorAvatar}><Text style={styles.vendorAvatarText}>🏪</Text></View>
            <View style={styles.vendorCopy}>
              <StatusChip label={selectedVendor.is_active === false ? "غیرفعال" : "فعال"} tone={selectedVendor.is_active === false ? "neutral" : "ok"} />
              <Text style={styles.productTitle}>{selectedVendor.name || selectedVendor.display_name || selectedVendor.id}</Text>
              <Text style={styles.meta}>{selectedVendor.city || "—"} · {String(selectedVendor.product_count || 0)} کالا</Text>
            </View>
          </Card>
          {selectedVendor.description ? <Card><Text style={styles.body}>{selectedVendor.description}</Text></Card> : null}
          {vendorProducts.length === 0 ? <Empty title="کالایی در ویترین نیست" /> : vendorProducts.map((p) => (
            <Card key={p.id} style={styles.vendorProductCard}>
              <View style={styles.productVisualSmall}><Text>📦</Text></View>
              <View style={styles.grow}>
                <Text style={styles.productTitle}>{p.product_name || p.name || p.id}</Text>
                <Text style={styles.meta}>{p.brand_name || ""} · {p.packaging_unit || ""}</Text>
                <Text style={styles.priceMedium}>{money(p.price_toman)}</Text>
                <Text style={styles.meta}>موجودی: {String(p.stock_quantity ?? "—")}</Text>
              </View>
              <Btn compact label="+" onPress={() => addVendorProduct(p)} disabled={p.is_available === false} />
            </Card>
          ))}
        </>
      );
    }

    return (
      <>
        <PageHeader title="بنکداران" onBack={() => setTab("home")} />
        <Input label="جستجوی بنکدار" value={vendorQuery} onChangeText={setVendorQuery} placeholder="نام یا شهر…" />
        <Btn label="نمایش بنکداران" onPress={() => void loadVendors()} loading={loading} />
        {filtered.length === 0 ? <Empty title="بنکداری یافت نشد" description="لیست واقعی فروشندگان از API بارگذاری می‌شود." /> : filtered.map((v) => (
          <Pressable key={v.id} onPress={() => void loadVendor(v.id)} accessibilityRole="button">
            <Card style={styles.vendorCard}>
              <View style={styles.vendorAvatar}><Text style={styles.vendorAvatarText}>🏪</Text></View>
              <View style={styles.grow}>
                <StatusChip label={v.is_active === false ? "غیرفعال" : "فعال"} tone={v.is_active === false ? "neutral" : "ok"} />
                <Text style={styles.productTitle}>{v.name || v.display_name || v.id}</Text>
                <Text style={styles.meta}>{v.city || "—"} · {String(v.product_count || 0)} کالا</Text>
              </View>
              <Text style={styles.chevron}>‹</Text>
            </Card>
          </Pressable>
        ))}
      </>
    );
  }

  function supportPage(): React.ReactNode {
    return <SupportMobileScreen role={props.role} onBack={() => setTab("home")} />;
  }

  function financePage(): React.ReactNode {
    return (
      <>
        <PageHeader title="فاکتورها" onBack={() => setTab("home")} />
        {invoices.length === 0 ? (
          <Empty title="فاکتوری نیست" description="فاکتورهای صادرشده شما اینجا نمایش داده می‌شوند." />
        ) : invoices.map((i) => (
          <Card key={i.id} style={styles.orderCard}>
            <StatusChip label={i.status || "—"} tone="info" />
            <Text style={styles.orderNumber}>{i.invoice_number || i.id}</Text>
            <Text style={styles.priceMedium}>{money(i.total_amount_toman)}</Text>
            <Text style={styles.meta}>{i.issued_at || "—"}</Text>
          </Card>
        ))}
      </>
    );
  }

  const content = showSuccess ? successPage()
    : selectedProduct ? productDetail()
    : tab === "home" ? home()
    : tab === "categories" ? categoriesPage()
    : tab === "products" ? productsPage()
    : tab === "basket" ? basketPage()
    : tab === "orders" ? ordersPage()
    : tab === "vendors" ? vendorsPage()
    : tab === "support" ? supportPage()
    : tab === "finance" ? financePage()
    : home();

  return (
    <Screen>
      <View style={styles.root}>
        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
          <ErrorBox message={error} />
          {content}
        </ScrollView>
        <View style={styles.bottomNav}>
          <NavItem label="حساب" icon="◯" onPress={() => props.onOpenAccount?.()} active={false} />
          <NavItem label="سبد" icon="🛒" badge={basketTotal} onPress={() => setTab("basket")} active={tab === "basket"} />
          <NavItem label="سفارش‌ها" icon="▤" onPress={() => setTab("orders")} active={tab === "orders"} />
          <NavItem label="خانه" icon="⌂" onPress={() => { setShowSuccess(false); setSelectedProduct(null); setTab("home"); }} active={tab === "home"} />
        </View>
      </View>
    </Screen>
  );
}

function ProductMiniCard(props: { product: Product; onOpen: () => void; onAdd: () => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <Pressable onPress={props.onOpen} style={styles.miniProduct} accessibilityRole="button">
      <View style={styles.productThumb}><Text style={styles.productEmoji}>📦</Text></View>
      <Text numberOfLines={2} style={styles.miniTitle}>{props.product.canonical_name_fa || "کالا"}</Text>
      <Text style={styles.meta}>{props.product.brand_name || "—"}</Text>
      <Btn compact label="+" onPress={props.onAdd} />
    </Pressable>
  );
}

function ProductRow(props: { product: Product; onOpen: () => void; onAdd: () => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <Card style={styles.productRowCard}>
      <Pressable onPress={props.onOpen} style={styles.grow} accessibilityRole="button">
        <Text style={styles.productTitle}>{props.product.canonical_name_fa || "—"}</Text>
        <Text style={styles.meta}>{props.product.brand_name || ""}</Text>
        <Text style={styles.sku}>{props.product.master_sku || props.product.id}</Text>
      </Pressable>
      <Btn compact label="افزودن" onPress={props.onAdd} />
    </Card>
  );
}

function QuickAction(props: { icon: string; label: string; onPress: () => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <Pressable onPress={props.onPress} style={styles.quickCard} accessibilityRole="button">
      <Text style={styles.quickIcon}>{props.icon}</Text>
      <Text style={styles.quickText}>{props.label}</Text>
    </Pressable>
  );
}

function NavItem(props: { label: string; icon: string; onPress: () => void; active: boolean; badge?: number }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <Pressable onPress={props.onPress} style={styles.navItem} accessibilityRole="button">
      {props.badge ? <View style={styles.navBadge}><Text style={styles.navBadgeText}>{props.badge}</Text></View> : null}
      <Text style={[styles.navIcon, props.active && styles.navIconActive]}>{props.icon}</Text>
      <Text style={[styles.navLabel, props.active && styles.navLabelActive]}>{props.label}</Text>
    </Pressable>
  );
}

function SectionTitle(props: { title: string; action?: string; onPress?: () => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>{props.title}</Text>
      {props.action && props.onPress ? <Pressable onPress={props.onPress} accessibilityRole="button"><Text style={styles.sectionAction}>{props.action}</Text></Pressable> : null}
    </View>
  );
}

function PageHeader(props: { title: string; onBack?: () => void; action?: string; onAction?: () => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <View style={styles.pageHeader}>
      <Pressable onPress={props.onBack} style={styles.backButton} accessibilityRole="button"><Text style={styles.backText}>›</Text></Pressable>
      <Text style={styles.pageTitle}>{props.title}</Text>
      {props.action && props.onAction ? <Pressable onPress={props.onAction}><Text style={styles.pageAction}>{props.action}</Text></Pressable> : <View style={styles.headerSpacer} />}
    </View>
  );
}

function InfoRow(props: { label: string; value: string }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoValue}>{props.value}</Text>
      <Text style={styles.infoLabel}>{props.label}</Text>
    </View>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
    root: { flex: 1 },
    scrollContent: { paddingBottom: 92 },
    header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: spacing.md },
    brandBlock: { flexDirection: "row", alignItems: "center", gap: spacing.sm },
    logo: { width: 46, height: 46, borderRadius: 15, backgroundColor: colors.brand, alignItems: "center", justifyContent: "center" },
    logoText: { color: "#fff", fontSize: 24, fontWeight: "900" },
    brandName: { color: colors.text, fontSize: 19, fontWeight: "900", textAlign: "right" },
    brandSub: { color: colors.textSecondary, fontSize: 10, marginTop: 1, textAlign: "right" },
    profileButton: { width: 42, height: 42, borderRadius: 21, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center" },
    profileIcon: { color: colors.textSecondary, fontSize: 18 },
    locationRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: spacing.md },
    eyebrow: { color: colors.textMuted, fontSize: 10, textAlign: "right" },
    locationText: { color: colors.text, fontSize: 15, fontWeight: "800", textAlign: "right", marginTop: 2 },
    locationButton: { borderWidth: 1, borderColor: colors.border, borderRadius: 999, paddingHorizontal: 10, paddingVertical: 7, backgroundColor: colors.surface },
    locationButtonText: { color: colors.brand, fontSize: 11, fontWeight: "700" },
    searchBox: { position: "relative", marginBottom: spacing.sm },
    searchIcon: { position: "absolute", zIndex: 2, right: 12, top: 17, color: colors.textMuted, fontSize: 18 },
    searchInput: { paddingRight: 38, borderRadius: 16, backgroundColor: colors.surface, marginBottom: 0 },
    heroCard: { backgroundColor: colors.brand, borderColor: colors.brand, minHeight: 150, padding: spacing.lg, overflow: "hidden" },
    heroCopy: { flex: 1, paddingRight: 88 },
    heroKicker: { color: "#DBEAFE", fontSize: 11, fontWeight: "700", textAlign: "right", marginBottom: 6 },
    heroTitle: { color: "#fff", fontSize: 19, fontWeight: "900", lineHeight: 28, textAlign: "right" },
    heroBody: { color: "#EAF2FF", fontSize: 12, lineHeight: 19, marginTop: 6, textAlign: "right" },
    heroArt: { position: "absolute", left: 14, bottom: 10, width: 84, height: 96, alignItems: "center", justifyContent: "center", transform: [{ rotate: "-8deg" }] },
    heroCarton: { color: "#BFDBFE", fontSize: 58, fontWeight: "900" },
    heroBag: { position: "absolute", color: "#fff", fontSize: 28, bottom: 2, right: 1 },
    sectionHeader: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginTop: spacing.lg, marginBottom: spacing.sm },
    sectionTitle: { color: colors.text, fontSize: 16, fontWeight: "900", textAlign: "right" },
    sectionAction: { color: colors.brand, fontSize: 11, fontWeight: "700" },
    categoryRow: { gap: spacing.sm, paddingBottom: 2 },
    categoryCard: { width: 94, minHeight: 92, backgroundColor: colors.surface, borderColor: colors.border, borderWidth: 1, borderRadius: 16, padding: spacing.sm, alignItems: "center", justifyContent: "center" },
    categoryText: { color: colors.text, fontSize: 11, fontWeight: "700", marginTop: 6, textAlign: "center" },
    emptyCommerce: { paddingVertical: spacing.xl, alignItems: "center" },
    emptyCommerceTitle: { color: colors.text, fontWeight: "800", fontSize: 14, textAlign: "center" },
    emptyCommerceBody: { color: colors.textSecondary, fontSize: 12, lineHeight: 19, marginTop: 5, textAlign: "center" },
    productRow: { gap: spacing.sm, paddingBottom: 2 },
    miniProduct: { width: 150, backgroundColor: colors.surface, borderColor: colors.border, borderWidth: 1, borderRadius: 16, padding: spacing.sm },
    productThumb: { height: 100, borderRadius: 13, backgroundColor: colors.neutralBg, alignItems: "center", justifyContent: "center", marginBottom: spacing.sm },
    productEmoji: { fontSize: 42 },
    miniTitle: { color: colors.text, fontSize: 12, fontWeight: "800", textAlign: "right", minHeight: 34 },
    quickGrid: { flexDirection: "row", gap: spacing.sm, marginBottom: spacing.md },
    quickCard: { flex: 1, minHeight: 86, borderRadius: 16, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center" },
    quickIcon: { fontSize: 22 },
    quickText: { color: colors.text, fontSize: 11, fontWeight: "700", marginTop: 5 },
    pageHeader: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: spacing.md },
    backButton: { width: 42, height: 42, borderRadius: 13, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, alignItems: "center", justifyContent: "center" },
    backText: { color: colors.text, fontSize: 26, lineHeight: 28 },
    pageTitle: { flex: 1, color: colors.text, fontSize: 21, fontWeight: "900", textAlign: "right", marginRight: spacing.sm },
    pageAction: { color: colors.danger, fontSize: 11, fontWeight: "700" },
    headerSpacer: { width: 42 },
    resultHeader: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginVertical: spacing.md },
    productRowCard: { flexDirection: "row", alignItems: "center", gap: spacing.sm },
    productTitle: { color: colors.text, fontSize: 14, fontWeight: "800", textAlign: "right", lineHeight: 21 },
    sku: { color: colors.textMuted, fontSize: 10, marginTop: 3, textAlign: "right" },
    meta: { color: colors.textSecondary, fontSize: 11, lineHeight: 17, textAlign: "right" },
    body: { color: colors.text, fontSize: 13, lineHeight: 21, textAlign: "right" },
    grow: { flex: 1, minWidth: 0 },
    productHero: { flexDirection: "row", gap: spacing.md, alignItems: "center" },
    productVisual: { width: 120, height: 150, borderRadius: 18, backgroundColor: colors.neutralBg, alignItems: "center", justifyContent: "center" },
    productHeroCopy: { flex: 1 },
    productVisualSmall: { width: 62, height: 62, borderRadius: 16, backgroundColor: colors.neutralBg, alignItems: "center", justifyContent: "center" },
    sectionCardTitle: { color: colors.text, fontSize: 15, fontWeight: "900", textAlign: "right", marginBottom: spacing.sm },
    infoRow: { flexDirection: "row", justifyContent: "space-between", borderTopWidth: 1, borderTopColor: colors.border, paddingTop: spacing.sm, marginTop: spacing.sm },
    infoValue: { flex: 1, color: colors.text, fontSize: 12, textAlign: "left" },
    infoLabel: { color: colors.textSecondary, fontSize: 12, textAlign: "right" },
    priceCard: { backgroundColor: colors.brandSoft },
    priceLarge: { color: colors.text, fontSize: 22, fontWeight: "900", marginVertical: spacing.sm, textAlign: "right" },
    priceMedium: { color: colors.text, fontSize: 17, fontWeight: "900", marginTop: 6, textAlign: "right" },
    cartCard: { flexDirection: "row", gap: spacing.md, alignItems: "center" },
    cartVisual: { width: 74, height: 86, borderRadius: 15, backgroundColor: colors.neutralBg, alignItems: "center", justifyContent: "center" },
    cartEmoji: { fontSize: 33 },
    cartMain: { flex: 1, minWidth: 0 },
    qtyRow: { flexDirection: "row", alignItems: "center", justifyContent: "flex-start", gap: spacing.sm, marginTop: spacing.sm },
    qtyButton: { width: 36, height: 36, borderRadius: 10, backgroundColor: colors.brand, alignItems: "center", justifyContent: "center" },
    qtyText: { color: "#fff", fontSize: 19, fontWeight: "900" },
    qtyButtonSecondary: { width: 36, height: 36, borderRadius: 10, backgroundColor: colors.neutralBg, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center" },
    qtyTextSecondary: { color: colors.text, fontSize: 19, fontWeight: "900" },
    qtyValue: { minWidth: 28, color: colors.text, fontSize: 14, fontWeight: "900", textAlign: "center" },
    actionStack: { gap: spacing.sm, marginTop: spacing.sm, marginBottom: spacing.sm },
    checkoutCard: { borderColor: colors.brand + "55", backgroundColor: colors.surface },
    successWrap: { alignItems: "center", justifyContent: "center", paddingHorizontal: spacing.lg, paddingTop: 80 },
    successIcon: { width: 92, height: 92, borderRadius: 46, backgroundColor: colors.successBg, alignItems: "center", justifyContent: "center", marginBottom: spacing.lg },
    successCheck: { color: colors.success, fontSize: 54, fontWeight: "700" },
    successTitle: { color: colors.text, fontSize: 24, fontWeight: "900", textAlign: "center" },
    successBody: { color: colors.textSecondary, fontSize: 13, lineHeight: 21, textAlign: "center", marginTop: spacing.sm, marginBottom: spacing.lg },
    orderCode: { color: colors.textSecondary, fontSize: 11, marginBottom: spacing.sm, textAlign: "center" },
    orderFilters: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginBottom: spacing.sm },
    orderCard: { paddingVertical: spacing.md },
    orderTop: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: spacing.sm },
    orderNumber: { color: colors.text, fontSize: 13, fontWeight: "900", flex: 1, textAlign: "right" },
    categoryList: { gap: spacing.sm },
    categoryListItem: { minHeight: 70, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, borderRadius: 15, paddingHorizontal: spacing.md, flexDirection: "row", alignItems: "center", gap: spacing.md },
    categoryListText: { flex: 1, color: colors.text, fontSize: 14, fontWeight: "800", textAlign: "right" },
    chevron: { color: colors.textMuted, fontSize: 22 },
    vendorHero: { flexDirection: "row", gap: spacing.md, alignItems: "center" },
    vendorAvatar: { width: 64, height: 64, borderRadius: 32, backgroundColor: colors.brandSoft, alignItems: "center", justifyContent: "center" },
    vendorAvatarText: { fontSize: 28 },
    vendorCopy: { flex: 1 },
    vendorCard: { flexDirection: "row", alignItems: "center", gap: spacing.md },
    vendorProductCard: { flexDirection: "row", alignItems: "center", gap: spacing.md },
    navBadge: { position: "absolute", top: -2, right: 11, minWidth: 18, height: 18, borderRadius: 9, backgroundColor: colors.danger, alignItems: "center", justifyContent: "center", zIndex: 2 },
    navBadgeText: { color: "#fff", fontSize: 9, fontWeight: "900" },
    bottomNav: { position: "absolute", left: 0, right: 0, bottom: 0, height: 74, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border, flexDirection: "row", alignItems: "center", justifyContent: "space-around", paddingHorizontal: 4 },
    navItem: { width: 70, height: 62, alignItems: "center", justifyContent: "center" },
    navIcon: { color: colors.textMuted, fontSize: 21, lineHeight: 25 },
    navIconActive: { color: colors.brand },
    navLabel: { color: colors.textMuted, fontSize: 10, fontWeight: "700", marginTop: 3 },
    navLabelActive: { color: colors.brand },
  });
}
