"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  SearchField,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { formatPackagingUnit } from "@/lib/format-labels";
import {
  formatToman,
  itemsOf,
  vendorProductDisplayName,
  str,
  type LoadState,
} from "../_shared";

interface VendorProduct {
  id: string;
  vendor_product_id?: string | null;
  product_id?: string | null;
  product_name?: string | null;
  canonical_name_fa?: string | null;
  master_sku?: string | null;
  candidate_id?: string | null;
  name?: string | null;
  brand_name?: string | null;
  vendor_sku?: string | null;
  packaging_unit?: string | null;
  price_toman?: number | null;
  stock_quantity?: number | null;
  available_quantity?: number | null;
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
      str(vendorProductDisplayName(p.canonical_name_fa, p.product_name, p.name), "").toLowerCase().includes(q) ||
      str(p.vendor_sku, "").toLowerCase().includes(q) ||
      str(p.brand_name, "").toLowerCase().includes(q)
    );
  });

  if (state === "loading") {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری کاتالوگ">
        <Skeleton className="h-9 w-48" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="p-5">
              <Skeleton lines={4} />
            </Card>
          ))}
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
    <div className="space-y-6">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] md:text-[26px] font-bold text-[var(--pol-light-text-primary)]">
              کاتالوگ کالاهای بنکداری
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              V-04
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            مدیریت قیمت‌های فعال، موجودی و وضعیت نمایش اقلام در سامانه پُل
          </p>
        </div>

        <Button variant="secondary" size="sm" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      {/* Search and Counts */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="w-full max-w-md">
          <SearchField
            label="جستجوی کالا"
            placeholder="نام کالا، برند یا کد SKU..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
          {filtered.length.toLocaleString("fa-IR")} از {products.length.toLocaleString("fa-IR")} قلم کالا
        </span>
      </div>

      {/* Products Grid */}
      {filtered.length === 0 ? (
        <EmptyState
          title="کالایی یافت نشد"
          description="کاتالوگ فروشگاه شما خالی است یا با عبارت جستجو مطابقت ندارد."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((p) => {
            const vpId = str(p.vendor_product_id ?? p.id, "");
            const canonicalName = vendorProductDisplayName(p.canonical_name_fa, p.product_name, p.name);
            const hasCanonicalName = Boolean(canonicalName);
            const productName = canonicalName || (p.vendor_sku ? `کالای کد ${p.vendor_sku}` : "کالای ثبت‌نشده");
            const needsCatalogMatch = !p.product_id || !hasCanonicalName;

            return (
              <Card
                key={vpId}
                className="flex flex-col justify-between p-5 transition-all duration-200 hover:shadow-[var(--pol-shadow-md)] hover:border-[var(--pol-light-border-strong)]"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)] line-clamp-2">
                      {productName}
                    </h2>
                    {needsCatalogMatch ? (
                      <StatusChip tone="warning">نیازمند تطبیق کاتالوگ</StatusChip>
                    ) : p.is_active === false ? (
                      <StatusChip tone="neutral">غیرفعال</StatusChip>
                    ) : (
                      <StatusChip tone="success">فعال</StatusChip>
                    )}
                  </div>

                  <div className="mt-2 flex flex-wrap items-center gap-2 text-[12px] text-[var(--pol-light-text-secondary)]">
                    {p.brand_name && <span>برند: {p.brand_name}</span>}
                    {p.vendor_sku && (
                      <>
                        <span>·</span>
                        <span dir="ltr" className="font-mono">
                          کد فروشنده: {p.vendor_sku}
                        </span>
                      </>
                    )}
                  </div>

                  <div className="mt-4 flex items-center justify-between border-t border-[var(--pol-light-border-subtle)] pt-3 text-[13px]">
                    <div>
                      <span className="block text-[11px] text-[var(--pol-light-text-secondary)]">
                        قیمت پایه
                      </span>
                      <span className="font-bold text-[var(--pol-light-text-primary)]">
                        {formatToman(p.price_toman)}
                      </span>
                    </div>

                    <div className="text-end">
                      <span className="block text-[11px] text-[var(--pol-light-text-secondary)]">
                        موجودی انبار
                      </span>
                      <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
                        {Number(p.stock_quantity ?? p.available_quantity ?? 0).toLocaleString("fa-IR")}{" "}
                        {formatPackagingUnit(p.packaging_unit)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 border-t border-[var(--pol-light-border-subtle)] pt-3">
                  <Link
                    href={`/vendor/catalog/${vpId}/prices`}
                    className="inline-flex w-full items-center justify-center rounded-lg bg-[var(--pol-light-surface-subtle)] py-2 text-[12px] font-semibold text-[var(--pol-light-brand-primary)] hover:bg-[var(--pol-light-surface-hover,var(--pol-light-surface-subtle))] transition-colors"
                  >
                    مدیریت و تاریخچه قیمت‌ها ←
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
