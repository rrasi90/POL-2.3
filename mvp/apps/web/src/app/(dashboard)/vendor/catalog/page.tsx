"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Button,
  EmptyState,
  ErrorState,
  SearchField,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  cardCls,
  formatToman,
  itemsOf,
  str,
  type LoadState,
} from "../_shared";

interface VendorProduct {
  id: string;
  vendor_product_id?: string | null;
  product_id?: string | null;
  product_name?: string | null;
  name?: string | null;
  brand_name?: string | null;
  vendor_sku?: string | null;
  packaging_unit?: string | null;
  price_toman?: number | null;
  stock_quantity?: number | null;
  is_active?: boolean | null;
}

/**
 * V-04 vendor catalog.
 * GET /catalog/vendors/products
 */
export default function VendorCatalogPage() {
  const [products, setProducts] = useState<VendorProduct[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [query, setQuery] = useState("");

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const data = await getApi().get<unknown>("/api/v1/catalog/vendors/products");
      setProducts(itemsOf<VendorProduct>(data, "products"));
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت کاتالوگ ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const filtered = products.filter((p) => {
    if (!query.trim()) return true;
    const q = query.trim().toLowerCase();
    return (
      str(p.product_name ?? p.name, "").toLowerCase().includes(q) ||
      str(p.vendor_sku, "").toLowerCase().includes(q) ||
      str(p.brand_name, "").toLowerCase().includes(q)
    );
  });

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری کاتالوگ">
        <Skeleton className="h-8 w-48" />
        <div className={cardCls}>
          <Skeleton lines={5} />
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت کاتالوگ ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          کاتالوگ فروشنده
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">
          V-04 · {products.length.toLocaleString("fa-IR")} کالا
        </span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      <SearchField
        label="جستجوی کالا"
        placeholder="نام، برند یا SKU…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      {filtered.length === 0 ? (
        <EmptyState
          title="کالایی یافت نشد"
          description="کاتالوگ خالی است  عبارت جستجو را تغییر دهید."
        />
      ) : (
        <ul role="list" className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((p) => {
            const vpId = str(p.vendor_product_id ?? p.id, "");
            return (
              <li
                key={vpId}
                className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
              >
                <div className="flex flex-wrap items-start gap-2">
                  <p className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
                    {p.product_name ?? p.name ?? "—"}
                  </p>
                  {p.is_active === false ? (
                    <StatusChip tone="neutral">غیرفعال</StatusChip>
                  ) : (
                    <StatusChip tone="success">فعال</StatusChip>
                  )}
                </div>
                {p.brand_name ? (
                  <p className="mt-0.5 text-[12px] text-[var(--pol-light-text-secondary)]">
                    {p.brand_name}
                  </p>
                ) : null}
                <div className="mt-2 flex flex-wrap gap-2 text-[13px] text-[var(--pol-light-text-secondary)]">
                  <span>{formatToman(p.price_toman)}</span>
                  {p.stock_quantity != null ? (
                    <span>
                      موجودی {Number(p.stock_quantity).toLocaleString("fa-IR")}
                      {p.packaging_unit ? ` ${p.packaging_unit}` : ""}
                    </span>
                  ) : null}
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Link
                    href={`/vendor/catalog/${vpId}/prices`}
                    className="rounded-[8px] border border-[var(--pol-light-border-strong)] px-3 py-1.5 text-[12px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
                  >
                    قیمت
                  </Link>
                  <Link
                    href="/vendor/inventory"
                    className="rounded-[8px] border border-[var(--pol-light-border-strong)] px-3 py-1.5 text-[12px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
                  >
                    موجودی
                  </Link>
                  {p.product_id ? (
                    <Link
                      href={`/retailer/catalog/${p.product_id}`}
                      className="rounded-[8px] border border-[var(--pol-light-border-strong)] px-3 py-1.5 text-[12px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
                    >
                      مشاهده در کاتالوگ
                    </Link>
                  ) : null}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
