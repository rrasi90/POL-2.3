"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Button,
  EmptyState,
  ErrorState,
  QtyStepper,
  Skeleton,
  StatusChip,
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
    <div className="space-y-6">
      <header className="flex flex-wrap items-start gap-3">
        <div>
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            {product.canonical_name_fa}
          </h1>
          <p className="mt-1 flex flex-wrap items-center gap-2 text-[13px] text-[var(--pol-light-text-secondary)]">
            {product.brand_name ? <StatusChip tone="info">{product.brand_name}</StatusChip> : null}
            {product.category_name ? <span>{product.category_name}</span> : null}
            {product.subcategory_name ? <span>· {product.subcategory_name}</span> : null}
            <span className="text-[var(--pol-light-text-muted)]" dir="ltr">
              {product.master_sku ?? ""}
            </span>
          </p>
        </div>
        <div className="ms-auto">
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            بازگشت
          </Button>
        </div>
      </header>

      <section
        aria-label="اطلاعات کالا"
        className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
      >
        <dl className="grid gap-4 sm:grid-cols-4">
          <div>
            <dt className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
              واحد پایه
            </dt>
            <dd className="mt-1 text-[14px] text-[var(--pol-light-text-primary)]">
              {product.base_unit ?? "—"}
            </dd>
          </div>
          <div>
            <dt className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
              بسته‌بندی
            </dt>
            <dd className="mt-1 text-[14px] text-[var(--pol-light-text-primary)]">
              {product.default_pack_quantity
                ? `${product.default_pack_quantity.toLocaleString("fa-IR")} ${product.default_pack_unit ?? ""}`
                : "—"}
            </dd>
          </div>
          <div>
            <dt className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
              وزن / حجم
            </dt>
            <dd className="mt-1 text-[14px] text-[var(--pol-light-text-primary)]">
              {product.net_weight_grams
                ? `${product.net_weight_grams.toLocaleString("fa-IR")} گرم`
                : product.volume_ml
                  ? `${product.volume_ml.toLocaleString("fa-IR")} میلی‌لیتر`
                  : "—"}
            </dd>
          </div>
          <div>
            <dt className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
              تأییدشده
            </dt>
            <dd className="mt-1">
              <StatusChip tone={product.is_verified ? "success" : "neutral"}>
                {product.is_verified ? "بله" : "خیر"}
              </StatusChip>
            </dd>
          </div>
        </dl>
        {product.description ? (
          <p className="mt-3 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
            {product.description}
          </p>
        ) : null}
      </section>

      <section aria-label="افزودن به سبد">
        <div className="flex flex-wrap items-end gap-4 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <div>
            <p className="mb-1.5 text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
              تعداد
            </p>
            <QtyStepper value={qty} min={1} onChange={setQty} label="تعداد کالا" />
          </div>
          <Button onClick={addToBasket}>افزودن به سبد</Button>
          <Button variant="secondary" onClick={() => router.push("/retailer/basket")}>
            رفتن به سبد
          </Button>
          {added ? (
            <p
              role="status"
              className="text-[13px] text-[var(--pol-light-semantic-success)]"
            >
              به سبد اضافه شد.
            </p>
          ) : null}
          {addError ? (
            <p role="alert" className="text-[13px] text-[var(--pol-light-semantic-danger)]">
              {addError}
            </p>
          ) : null}
        </div>
      </section>

      <section aria-label="پیشنهاد فروشندگان">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
            فروشندگان این کالا
          </h2>
          {bestPrice ? (
            <StatusChip tone="success">
              بهترین قیمت: {formatToman(bestPrice.price_toman)}
            </StatusChip>
          ) : null}
          {bestStock ? (
            <StatusChip tone="info">
              بیشترین موجودی: {Number(bestStock.available_quantity ?? 0).toLocaleString("fa-IR")}
            </StatusChip>
          ) : null}
        </div>

        {offers.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="فروشنده‌ای برای این کالا یافت نشد"
              description="موجودی فروشندگان به‌روزرسانی می‌شود؛ بعداً دوباره بررسی کنید."
            />
          </div>
        ) : (
          <div className="mt-3 overflow-x-auto rounded-[12px] border border-[var(--pol-light-border-subtle)]">
            <table className="w-full min-w-[640px] border-collapse bg-[var(--pol-light-surface-default)] text-[13px]">
              <thead>
                <tr className="border-b border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] text-[12px] text-[var(--pol-light-text-secondary)]">
                  <th className="px-4 py-2 text-start font-medium">فروشنده</th>
                  <th className="px-4 py-2 text-start font-medium">قیمت</th>
                  <th className="px-4 py-2 text-start font-medium">موجودی</th>
                  <th className="px-4 py-2 text-start font-medium">حداقل خرید</th>
                  <th className="px-4 py-2 text-start font-medium">بسته</th>
                  <th className="px-4 py-2 text-start font-medium">تازگی</th>
                </tr>
              </thead>
              <tbody>
                {offers.map((o) => (
                  <tr
                    key={o.vendor_product_id}
                    className="border-b border-[var(--pol-light-border-subtle)] last:border-b-0"
                  >
                    <td className="px-4 py-3 text-[var(--pol-light-text-primary)]">
                      {o.business_name ?? "—"}
                    </td>
                    <td className="px-4 py-3 text-[var(--pol-light-text-primary)]">
                      {formatToman(o.price_toman)}
                    </td>
                    <td className="px-4 py-3">
                      <StatusChip
                        tone={
                          Number(o.available_quantity ?? 0) > 0 ? "success" : "danger"
                        }
                      >
                        {Number(o.available_quantity ?? 0).toLocaleString("fa-IR")}
                      </StatusChip>
                    </td>
                    <td className="px-4 py-3 text-[var(--pol-light-text-secondary)]">
                      {o.moq != null ? o.moq.toLocaleString("fa-IR") : "—"}
                    </td>
                    <td className="px-4 py-3 text-[var(--pol-light-text-secondary)]">
                      {o.pack_quantity != null
                        ? `${o.pack_quantity.toLocaleString("fa-IR")} ${o.packaging_unit ?? ""}`
                        : "—"}
                    </td>
                    <td className="px-4 py-3 text-[var(--pol-light-text-secondary)]">
                      {o.freshness_status ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section aria-label="مقایسه قیمت و موجودی" className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <h3 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
            مقایسه قیمت
          </h3>
          {prices.length === 0 ? (
            <p className="mt-2 text-[13px] text-[var(--pol-light-text-muted)]">
              داده‌ای برای مقایسه قیمت موجود نیست.
            </p>
          ) : (
            <ul role="list" className="mt-2 space-y-1.5">
              {prices.map((r, i) => (
                <li
                  key={r.vendor_product_id}
                  className="flex items-center gap-2 text-[13px]"
                >
                  <span className="w-6 text-[var(--pol-light-text-muted)]">
                    {(i + 1).toLocaleString("fa-IR")}.
                  </span>
                  <span className="text-[var(--pol-light-text-primary)]">
                    {r.business_name ?? "—"}
                  </span>
                  <span className="ms-auto text-[var(--pol-light-text-primary)]">
                    {formatToman(r.price_toman)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <h3 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
            مقایسه موجودی
          </h3>
          {inventory.length === 0 ? (
            <p className="mt-2 text-[13px] text-[var(--pol-light-text-muted)]">
              داده‌ای برای مقایسه موجودی موجود نیست.
            </p>
          ) : (
            <ul role="list" className="mt-2 space-y-1.5">
              {inventory.map((r) => (
                <li
                  key={r.vendor_product_id}
                  className="flex items-center gap-2 text-[13px]"
                >
                  <span className="text-[var(--pol-light-text-primary)]">
                    {r.business_name ?? "—"}
                  </span>
                  <StatusChip
                    tone={Number(r.available_quantity ?? 0) > 0 ? "success" : "danger"}
                  >
                    موجودی {Number(r.available_quantity ?? 0).toLocaleString("fa-IR")}
                  </StatusChip>
                  {r.moq != null ? (
                    <span className="ms-auto text-[12px] text-[var(--pol-light-text-muted)]">
                      حداقل {r.moq.toLocaleString("fa-IR")}
                    </span>
                  ) : null}
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </div>
  );
}
