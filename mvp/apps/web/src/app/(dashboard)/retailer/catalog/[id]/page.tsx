"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  QtyStepper,
  Skeleton,
  StatusChip,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { useBasketStore } from "@/lib/basket";
import { formatToman } from "../../shared";

interface ProductDetail {
  id: string;
  master_sku?: string | null;
  canonical_name_fa: string;
  base_unit?: string | null;
  default_pack_unit?: string | null;
  default_pack_quantity?: number | null;
  net_weight_grams?: number | null;
  volume_ml?: number | null;
  description?: string | null;
  is_active?: boolean;
  is_verified?: boolean;
  brand_id?: string | null;
  brand_name?: string | null;
  category_id?: string | null;
  category_name?: string | null;
  subcategory_id?: string | null;
  subcategory_name?: string | null;
}

interface VendorOffer {
  vendor_product_id: string;
  vendor_id?: string | null;
  vendor_sku?: string | null;
  packaging_unit?: string | null;
  pack_quantity?: number | null;
  sales_unit?: string | null;
  physical_quantity?: number | null;
  available_quantity?: number | null;
  moq?: number | null;
  freshness_status?: string | null;
  price_toman?: number | null;
  business_name?: string | null;
  vendor_status?: string | null;
}

interface ComparePriceRow {
  vendor_product_id: string;
  business_name?: string | null;
  price_toman?: number | null;
  available_quantity?: number | null;
  moq?: number | null;
  pack_quantity?: number | null;
}

interface CompareInventoryRow {
  vendor_product_id: string;
  business_name?: string | null;
  available_quantity?: number | null;
  physical_quantity?: number | null;
  reserved_quantity?: number | null;
  moq?: number | null;
  price_toman?: number | null;
  freshness_status?: string | null;
}

type LoadState = "loading" | "error" | "ready";

export default function RetailerProductPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const productId = params.id;
  const addLine = useBasketStore((s) => s.addLine);

  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [offers, setOffers] = useState<VendorOffer[]>([]);
  const [prices, setPrices] = useState<ComparePriceRow[]>([]);
  const [inventory, setInventory] = useState<CompareInventoryRow[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [qty, setQty] = useState(1);
  const [added, setAdded] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!productId) return;
    setState("loading");
    setErrorMessage(null);
    try {
      const [p, v, cp, ci] = await Promise.all([
        getApi().get<ProductDetail>(`/api/v1/catalog/products/${productId}`),
        getApi().get<VendorOffer[] | { data: VendorOffer[] }>(
          `/api/v1/catalog/products/${productId}/vendors`,
        ),
        getApi()
          .get<ComparePriceRow[] | { data: ComparePriceRow[] }>(
            `/api/v1/catalog/products/${productId}/compare-prices`,
          )
          .catch(() => [] as ComparePriceRow[]),
        getApi()
          .get<CompareInventoryRow[] | { data: CompareInventoryRow[] }>(
            `/api/v1/catalog/products/${productId}/compare-inventory`,
          )
          .catch(() => [] as CompareInventoryRow[]),
      ]);
      setProduct(p);
      setOffers(Array.isArray(v) ? v : (v?.data ?? []));
      setPrices(Array.isArray(cp) ? cp : (cp?.data ?? []));
      setInventory(Array.isArray(ci) ? ci : (ci?.data ?? []));
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت کالا ناموفق بود");
      setState("error");
    }
  }, [productId]);

  useEffect(() => {
    void load();
  }, [load]);

  function addToBasket() {
    if (!product) return;
    setAddError(null);
    try {
      addLine({
        product_id: product.id,
        name: product.canonical_name_fa,
        master_sku: product.master_sku ?? null,
        unit: product.default_pack_unit ?? product.base_unit ?? null,
        quantity: qty,
        pack_quantity: product.default_pack_quantity && product.default_pack_quantity > 0
          ? product.default_pack_quantity
          : 1,
      });
      setAdded(true);
      window.setTimeout(() => setAdded(false), 2500);
    } catch {
      setAddError("افزودن به سبد ناموفق بود");
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری کالا">
        <Skeleton className="h-8 w-64" />
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <Skeleton lines={4} />
        </div>
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <Skeleton lines={3} />
        </div>
      </div>
    );
  }

  if (state === "error" || !product) {
    return (
      <ErrorState
        title="دریافت اطلاعات کالا ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  const bestPrice = prices.length > 0 ? prices[0] : null;
  const bestStock =
    inventory.length > 0
      ? inventory.reduce((a, b) =>
          Number(b.available_quantity ?? 0) > Number(a.available_quantity ?? 0) ? b : a,
        )
      : null;

  return (
    <div className="space-y-6 pb-10">
      <header className="flex flex-wrap items-start justify-between gap-4 border-b border-[var(--pol-light-border-subtle)] pb-5">
        <div>
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            {product.canonical_name_fa}
          </h1>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-[13px] text-[var(--pol-light-text-secondary)]">
            {product.brand_name ? <StatusChip tone="info">{product.brand_name}</StatusChip> : null}
            {product.category_name ? (
              <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[12px] border border-[var(--pol-light-border-subtle)]">
                {product.category_name}
              </span>
            ) : null}
            {product.subcategory_name ? (
              <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[12px] border border-[var(--pol-light-border-subtle)]">
                {product.subcategory_name}
              </span>
            ) : null}
            <span className="font-mono text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
              SKU: {product.master_sku ?? "—"}
            </span>
          </div>
        </div>
        <div>
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            ← بازگشت
          </Button>
        </div>
      </header>

      {/* Product Attributes Overview */}
      <Card className="p-5 shadow-xs">
        <h2 className="text-[14px] font-bold text-[var(--pol-light-text-primary)] mb-4">
          مشخصات استاندارد کالا
        </h2>
        <dl className="grid gap-4 sm:grid-cols-4">
          <div className="rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-3 border border-[var(--pol-light-border-subtle)]">
            <dt className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
              واحد پایه
            </dt>
            <dd className="mt-1 text-[14px] font-bold text-[var(--pol-light-text-primary)]">
              {product.base_unit ?? "—"}
            </dd>
          </div>
          <div className="rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-3 border border-[var(--pol-light-border-subtle)]">
            <dt className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
              بسته‌بندی
            </dt>
            <dd className="mt-1 text-[14px] font-bold text-[var(--pol-light-text-primary)]">
              {product.default_pack_quantity
                ? `${product.default_pack_quantity.toLocaleString("fa-IR")} ${product.default_pack_unit ?? ""}`
                : "—"}
            </dd>
          </div>
          <div className="rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-3 border border-[var(--pol-light-border-subtle)]">
            <dt className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
              وزن / حجم
            </dt>
            <dd className="mt-1 text-[14px] font-bold text-[var(--pol-light-text-primary)]">
              {product.net_weight_grams
                ? `${product.net_weight_grams.toLocaleString("fa-IR")} گرم`
                : product.volume_ml
                  ? `${product.volume_ml.toLocaleString("fa-IR")} میلی‌لیتر`
                  : "—"}
            </dd>
          </div>
          <div className="rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-3 border border-[var(--pol-light-border-subtle)]">
            <dt className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
              وضعیت تأیید پُل
            </dt>
            <dd className="mt-1">
              <StatusChip tone={product.is_verified ? "success" : "neutral"}>
                {product.is_verified ? "تأییدشده" : "در انتظار تأیید"}
              </StatusChip>
            </dd>
          </div>
        </dl>
        {product.description ? (
          <div className="mt-4 pt-4 border-t border-[var(--pol-light-border-subtle)]">
            <p className="text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
              {product.description}
            </p>
          </div>
        ) : null}
      </Card>

      {/* Add to Basket Action Card */}
      <Card variant="interactive" className="p-5 border-[var(--pol-light-brand-primary)]/30 bg-[var(--pol-light-brand-primary)]/3">
        <h2 className="text-[14px] font-bold text-[var(--pol-light-text-primary)] mb-3">
          سفارش‌گذاری و افزودن به سبد
        </h2>
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <p className="mb-1.5 text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
              تعداد بسته یا کارتن:
            </p>
            <QtyStepper value={qty} min={1} onChange={setQty} label="تعداد کالا" />
          </div>
          <Button onClick={addToBasket}>
            <svg
              className="size-4 me-1.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
              />
            </svg>
            افزودن به سبد خرید
          </Button>
          <Button variant="secondary" onClick={() => router.push("/retailer/basket")}>
            مشاهده سبد خرید
          </Button>
          {added ? (
            <div
              role="status"
              className="flex items-center gap-1.5 text-[13px] font-medium text-[var(--pol-light-semantic-success)]"
            >
              <svg className="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>با موفقیت به سبد خرید افزوده شد.</span>
            </div>
          ) : null}
          {addError ? (
            <p role="alert" className="text-[13px] font-medium text-[var(--pol-light-semantic-danger)]">
              {addError}
            </p>
          ) : null}
        </div>
      </Card>

      {/* Vendor Offers Comparison Table */}
      <section aria-label="پیشنهاد فروشندگان" className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <h2 className="text-[16px] leading-[24px] font-bold text-[var(--pol-light-text-primary)]">
              فروشندگان فعال این کالا
            </h2>
            <span className="text-[12px] text-[var(--pol-light-text-muted)]">
              ({offers.length.toLocaleString("fa-IR")} تأمین‌کننده)
            </span>
          </div>
          <div className="flex items-center gap-2">
            {bestPrice ? (
              <StatusChip tone="success">
                کمترین قیمت: {formatToman(bestPrice.price_toman)}
              </StatusChip>
            ) : null}
            {bestStock ? (
              <StatusChip tone="info">
                بیشترین موجودی: {Number(bestStock.available_quantity ?? 0).toLocaleString("fa-IR")}
              </StatusChip>
            ) : null}
          </div>
        </div>

        {offers.length === 0 ? (
          <Card variant="subtle" className="p-6">
            <EmptyState
              title="فروشنده‌ای برای این کالا یافت نشد"
              description="در حال حاضر هیچ تأمین‌کننده‌ای موجودی فعال برای این کالا ثبت نکرده است. موجودی‌ها به صورت روزانه توسط تأمین‌کنندگان به‌روزرسانی می‌شوند."
            />
          </Card>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>نام تأمین‌کننده</TableHead>
                <TableHead>قیمت هر واحد</TableHead>
                <TableHead>موجودی آزاد</TableHead>
                <TableHead>حداقل سفارش (MOQ)</TableHead>
                <TableHead>بسته‌بندی</TableHead>
                <TableHead>وضعیت تازگی</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {offers.map((o) => (
                <TableRow key={o.vendor_product_id}>
                  <TableCell className="font-semibold text-[var(--pol-light-text-primary)]">
                    {o.business_name ?? "—"}
                  </TableCell>
                  <TableCell className="font-bold text-[var(--pol-light-brand-primary)]">
                    {formatToman(o.price_toman)}
                  </TableCell>
                  <TableCell>
                    <StatusChip
                      tone={
                        Number(o.available_quantity ?? 0) > 0 ? "success" : "danger"
                      }
                    >
                      {Number(o.available_quantity ?? 0).toLocaleString("fa-IR")}
                    </StatusChip>
                  </TableCell>
                  <TableCell className="text-[var(--pol-light-text-secondary)]">
                    {o.moq != null ? o.moq.toLocaleString("fa-IR") : "—"}
                  </TableCell>
                  <TableCell className="text-[var(--pol-light-text-secondary)]">
                    {o.pack_quantity != null
                      ? `${o.pack_quantity.toLocaleString("fa-IR")} ${o.packaging_unit ?? ""}`
                      : "—"}
                  </TableCell>
                  <TableCell className="text-[var(--pol-light-text-secondary)]">
                    {o.freshness_status ?? "عادی"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </section>

      {/* Quick Comparison Cards */}
      <section aria-label="مقایسه قیمت و موجودی" className="grid gap-4 lg:grid-cols-2">
        <Card className="p-5 shadow-xs">
          <h3 className="text-[14px] font-bold text-[var(--pol-light-text-primary)] mb-3">
            رتبه‌بندی قیمت تأمین‌کنندگان
          </h3>
          {prices.length === 0 ? (
            <p className="text-[13px] text-[var(--pol-light-text-muted)]">
              داده‌ای برای مقایسه قیمت موجود نیست.
            </p>
          ) : (
            <ul role="list" className="space-y-2">
              {prices.map((r, i) => (
                <li
                  key={r.vendor_product_id}
                  className="flex items-center justify-between rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-2.5 text-[13px] border border-[var(--pol-light-border-subtle)]"
                >
                  <div className="flex items-center gap-2">
                    <span className="flex size-6 items-center justify-center rounded-full bg-[var(--pol-light-surface-default)] text-[11px] font-bold text-[var(--pol-light-text-secondary)] border border-[var(--pol-light-border-subtle)]">
                      {(i + 1).toLocaleString("fa-IR")}
                    </span>
                    <span className="font-medium text-[var(--pol-light-text-primary)]">
                      {r.business_name ?? "—"}
                    </span>
                  </div>
                  <span className="font-bold text-[var(--pol-light-text-primary)]">
                    {formatToman(r.price_toman)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card className="p-5 shadow-xs">
          <h3 className="text-[14px] font-bold text-[var(--pol-light-text-primary)] mb-3">
            رتبه‌بندی موجودی آزاد
          </h3>
          {inventory.length === 0 ? (
            <p className="text-[13px] text-[var(--pol-light-text-muted)]">
              داده‌ای برای مقایسه موجودی موجود نیست.
            </p>
          ) : (
            <ul role="list" className="space-y-2">
              {inventory.map((r) => (
                <li
                  key={r.vendor_product_id}
                  className="flex items-center justify-between rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-2.5 text-[13px] border border-[var(--pol-light-border-subtle)]"
                >
                  <span className="font-medium text-[var(--pol-light-text-primary)]">
                    {r.business_name ?? "—"}
                  </span>
                  <div className="flex items-center gap-2">
                    <StatusChip
                      tone={Number(r.available_quantity ?? 0) > 0 ? "success" : "danger"}
                    >
                      {Number(r.available_quantity ?? 0).toLocaleString("fa-IR")} موجود
                    </StatusChip>
                    {r.moq != null ? (
                      <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                        (حداقل {r.moq.toLocaleString("fa-IR")})
                      </span>
                    ) : null}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </section>
    </div>
  );
}
