"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { useAuthStore } from "@/lib/auth/store";
import {
  formatDateTime,
  formatToman,
  itemsOf,
  str,
  type LoadState,
} from "../_shared";

interface StorefrontVendor {
  id: string;
  name?: string | null;
  display_name?: string | null;
  city?: string | null;
  description?: string | null;
  is_active?: boolean | null;
  created_at?: string | null;
}

interface StorefrontProduct {
  id: string;
  product_id?: string | null;
  product_name?: string | null;
  name?: string | null;
  brand_name?: string | null;
  price_toman?: number | null;
  stock_quantity?: number | null;
  packaging_unit?: string | null;
  is_available?: boolean | null;
}

/**
 * V-14 storefront management — read-only (D-024).
 * GET /storefront/vendors, GET /storefront/vendors/{id}/products
 */
export default function VendorStorefrontPage() {
  const orgId = useAuthStore((s) => s.user?.organization_id);
  const [vendors, setVendors] = useState<StorefrontVendor[]>([]);
  const [selected, setSelected] = useState<StorefrontVendor | null>(null);
  const [products, setProducts] = useState<StorefrontProduct[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const list = await getApi().get<unknown>("/api/v1/storefront/vendors");
      const rows = itemsOf<StorefrontVendor>(list, "vendors");
      setVendors(rows);
      const match =
        rows.find((v) => v.id === orgId) ??
        rows.find((v) => str(v.id) === str(orgId)) ??
        rows[0] ??
        null;
      setSelected(match);
      if (match) {
        const prods = await getApi().get<unknown>(
          `/api/v1/storefront/vendors/${match.id}/products`,
        );
        setProducts(itemsOf<StorefrontProduct>(prods, "products"));
      } else {
        setProducts([]);
      }
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت ویترین ناموفق بود");
      setState("error");
    }
  }, [orgId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function selectVendor(v: StorefrontVendor) {
    setSelected(v);
    setProducts([]);
    try {
      const prods = await getApi().get<unknown>(
        `/api/v1/storefront/vendors/${v.id}/products`,
      );
      setProducts(itemsOf<StorefrontProduct>(prods, "products"));
    } catch {
      setProducts([]);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری ویترین">
        <Skeleton className="h-9 w-48" />
        <Card className="p-6">
          <Skeleton lines={4} />
        </Card>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت ویترین ناموفق بود"
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
              ویترین اختصاصی فروشگاه
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              V-14 · D-024
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            نمای ویترین عمومی بنکداری شما همان‌گونه که برای خرده‌فروشان و سوپرمارکت‌ها نمایش داده می‌شود
          </p>
        </div>

        <Button variant="secondary" size="sm" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      {/* Scope Notice Banner */}
      <div className="flex items-start gap-3 rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-4 text-[13px] text-[var(--pol-light-text-secondary)] leading-relaxed">
        <span className="text-base">ℹ️</span>
        <div>
          <strong className="font-semibold text-[var(--pol-light-text-primary)]">راهنما:</strong>{" "}
          اطلاعات ویترین به صورت خودکار از تنظیمات سازمانی و کاتالوگ فعال استخراج می‌شود. برای تغییر
          قیمت یا موجودی کالاها از بخش‌های کاتالوگ و مدیریت انبار استفاده فرمایید.
          <div className="mt-2.5 flex flex-wrap gap-2">
            <Link
              href="/vendor/catalog"
              className="rounded-lg border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1 text-[12px] font-semibold text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)] transition-colors"
            >
              کاتالوگ و قیمت‌ها
            </Link>
            <Link
              href="/vendor/inventory"
              className="rounded-lg border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1 text-[12px] font-semibold text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)] transition-colors"
            >
              مدیریت انبار
            </Link>
          </div>
        </div>
      </div>

      {/* Vendor Selector */}
      {vendors.length > 1 && (
        <div className="flex flex-wrap gap-2" role="group" aria-label="انتخاب فروشگاه">
          {vendors.map((v) => {
            const isSelected = selected?.id === v.id;
            return (
              <button
                key={String(v.id)}
                type="button"
                onClick={() => void selectVendor(v)}
                className={[
                  "rounded-full px-4 py-1.5 text-[13px] font-medium transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]",
                  isSelected
                    ? "bg-[var(--pol-light-brand-primary)] text-white shadow-sm"
                    : "border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)]",
                ].join(" ")}
              >
                {v.name ?? v.display_name ?? String(v.id)}
              </button>
            );
          })}
        </div>
      )}

      {/* Vendor Details Card */}
      {selected && (
        <Card className="p-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-[var(--pol-light-surface-subtle)] text-[22px]">
                🏪
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
                    {selected.name ?? selected.display_name ?? "بنکداری"}
                  </h2>
                  {selected.is_active === false ? (
                    <StatusChip tone="neutral">غیرفعال</StatusChip>
                  ) : (
                    <StatusChip tone="success">ویترین فعال</StatusChip>
                  )}
                </div>
                <div className="mt-1 flex flex-wrap items-center gap-2 text-[12px] text-[var(--pol-light-text-secondary)]">
                  {selected.city && <span>📍 شهر: {selected.city}</span>}
                  <span>·</span>
                  <span>عضویت از {formatDateTime(selected.created_at)}</span>
                </div>
              </div>
            </div>

            <span className="font-mono text-[12px] text-[var(--pol-light-text-muted)]" dir="ltr">
              ID: {selected.id}
            </span>
          </div>

          {selected.description && (
            <p className="mt-4 border-t border-[var(--pol-light-border-subtle)] pt-3 text-[13px] leading-relaxed text-[var(--pol-light-text-secondary)]">
              {selected.description}
            </p>
          )}
        </Card>
      )}

      {/* Storefront Products */}
      <section aria-label="کالاهای ویترین" className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
            کالاهای موجود در ویترین ({products.length.toLocaleString("fa-IR")} قلم)
          </h2>
          <Link
            href="/retailer/catalog"
            className="text-[12px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
          >
            مشاهده در کاتالوگ سراسری ←
          </Link>
        </div>

        {products.length === 0 ? (
          <EmptyState
            title="کالایی در ویترین نمایش داده نمی‌شود"
            description="پس از افزودن کالا و ثبت قیمت فعال در کاتالوگ فروشنده، اقلام در این بخش ظاهر می‌شوند."
          />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {products.map((p) => (
              <Card
                key={String(p.id)}
                className="flex flex-col justify-between p-4 transition-all duration-200 hover:shadow-[var(--pol-shadow-md)] hover:border-[var(--pol-light-border-strong)]"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="text-[14px] font-bold text-[var(--pol-light-text-primary)] line-clamp-2">
                      {p.product_name ?? p.name ?? "—"}
                    </h3>
                    {p.is_available === false && (
                      <StatusChip tone="warning">ناموجود</StatusChip>
                    )}
                  </div>

                  <div className="mt-3 flex items-center justify-between text-[13px]">
                    <span className="font-bold text-[var(--pol-light-text-primary)]">
                      {formatToman(p.price_toman)}
                    </span>
                    {p.stock_quantity != null && (
                      <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
                        موجودی: {Number(p.stock_quantity).toLocaleString("fa-IR")}{" "}
                        {p.packaging_unit ?? "بسته"}
                      </span>
                    )}
                  </div>
                </div>

                {p.product_id && (
                  <div className="mt-3 border-t border-[var(--pol-light-border-subtle)] pt-2 text-end">
                    <Link
                      href={`/retailer/catalog/${p.product_id}`}
                      className="text-[12px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
                    >
                      نمای عمومی کالا ←
                    </Link>
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
