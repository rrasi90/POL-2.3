"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { formatDateTime, formatToman, asRecordArray } from "../../shared";

interface VendorDetail {
  id: string;
  name?: string | null;
  display_name?: string | null;
  city?: string | null;
  description?: string | null;
  is_active?: boolean | null;
  created_at?: string | null;
}

interface VendorProduct {
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

type LoadState = "loading" | "error" | "ready";

/**
 * R-18 vendor storefront (read-only browse).
 * GET /storefront/vendors/{id}, GET /storefront/vendors/{id}/products
 */
export default function RetailerVendorStorefrontPage() {
  const params = useParams<{ id: string }>();
  const vendorId = params.id;

  const [vendor, setVendor] = useState<VendorDetail | null>(null);
  const [products, setProducts] = useState<VendorProduct[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!vendorId) return;
    setState("loading");
    setErrorMessage(null);
    try {
      const [v, p] = await Promise.all([
        getApi().get<VendorDetail>(`/api/v1/storefront/vendors/${vendorId}`),
        getApi().get<unknown>(`/api/v1/storefront/vendors/${vendorId}/products`),
      ]);
      setVendor(v);
      setProducts(asRecordArray(p) as unknown as VendorProduct[]);
      setState("ready");
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : "دریافت ویترین تأمین‌کننده ناموفق بود",
      );
      setState("error");
    }
  }, [vendorId]);

  useEffect(() => {
    void load();
  }, [load]);

  if (state === "loading") {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری ویترین">
        <Skeleton className="h-9 w-64" />
        <Card className="p-6">
          <Skeleton lines={4} />
        </Card>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="p-4">
              <Skeleton lines={4} />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (state === "error" || !vendor) {
    return (
      <ErrorState
        title="دریافت ویترین تأمین‌کننده ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  const name = vendor.name ?? vendor.display_name ?? "تأمین‌کننده بدون نام";
  const initial = name.charAt(0);

  return (
    <div className="space-y-6">
      {/* Header Profile Card */}
      <Card className="p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-4">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-[var(--pol-light-surface-subtle)] text-[22px] font-bold text-[var(--pol-light-brand-primary)]">
              {initial}
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-[20px] md:text-[24px] font-bold text-[var(--pol-light-text-primary)]">
                  {name}
                </h1>
                {vendor.is_active === false ? (
                  <StatusChip tone="neutral">غیرفعال</StatusChip>
                ) : (
                  <StatusChip tone="success">تأمین‌کننده فعال</StatusChip>
                )}
              </div>
              <div className="mt-1.5 flex flex-wrap items-center gap-3 text-[12px] text-[var(--pol-light-text-secondary)]">
                {vendor.city && <span>📍 شهر: {vendor.city}</span>}
                <span>·</span>
                <span>عضویت از {formatDateTime(vendor.created_at)}</span>
                <span>·</span>
                <span>{products.length.toLocaleString("fa-IR")} قلم کالای عرضه‌شده</span>
              </div>
              {vendor.description && (
                <p className="mt-3 text-[13px] leading-relaxed text-[var(--pol-light-text-secondary)]">
                  {vendor.description}
                </p>
              )}
            </div>
          </div>

          <div className="flex shrink-0 gap-2">
            <Button variant="ghost" size="sm" onClick={() => void load()}>
              به‌روزرسانی
            </Button>
            <Link
              href="/retailer/vendors"
              className="inline-flex items-center justify-center rounded-lg border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] font-medium text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)] transition-colors"
            >
              همه تأمین‌کنندگان
            </Link>
          </div>
        </div>
      </Card>

      {/* Catalog Grid */}
      <section aria-label="کالاهای فروشگاه" className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
              ویترین کالاهای عرضه‌شده
            </h2>
            <p className="text-[12px] text-[var(--pol-light-text-secondary)]">
              کالاهای دارای موجودی این بنکدار را مقایسه و سفارش دهید
            </p>
          </div>
          <Link
            href="/retailer/catalog"
            className="text-[13px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
          >
            جستجو در تمام کاتالوگ ←
          </Link>
        </div>

        {products.length === 0 ? (
          <EmptyState
            title="کالایی در ویترین نیست"
            description="این تأمین‌کننده در حال حاضر کالای فعالی برای نمایش ندارد."
          />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {products.map((p) => {
              const productName = p.product_name ?? p.name ?? "کالای بدون عنوان";
              return (
                <Card
                  key={String(p.id)}
                  className="flex flex-col justify-between p-4 transition-all duration-200 hover:shadow-[var(--pol-shadow-md)] hover:border-[var(--pol-light-border-strong)]"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="text-[14px] font-bold text-[var(--pol-light-text-primary)] line-clamp-2">
                        {productName}
                      </h3>
                      {p.is_available === false && (
                        <StatusChip tone="warning">ناموجود</StatusChip>
                      )}
                    </div>
                    {p.brand_name && (
                      <span className="mt-1 inline-block text-[12px] text-[var(--pol-light-text-secondary)]">
                        برند: {p.brand_name}
                      </span>
                    )}

                    <div className="mt-3 flex items-center justify-between text-[13px]">
                      <div>
                        <span className="block text-[11px] text-[var(--pol-light-text-secondary)]">
                          قیمت واحد
                        </span>
                        <span className="font-bold text-[var(--pol-light-text-primary)]">
                          {formatToman(p.price_toman)}
                        </span>
                      </div>
                      {p.stock_quantity != null && (
                        <div className="text-end">
                          <span className="block text-[11px] text-[var(--pol-light-text-secondary)]">
                            موجودی
                          </span>
                          <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
                            {Number(p.stock_quantity).toLocaleString("fa-IR")}{" "}
                            {p.packaging_unit ?? "بسته"}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {p.product_id && (
                    <div className="mt-4 border-t border-[var(--pol-light-border-subtle)] pt-3">
                      <Link
                        href={`/retailer/catalog/${p.product_id}`}
                        className="inline-flex w-full items-center justify-center rounded-lg bg-[var(--pol-light-surface-subtle)] py-2 text-[12px] font-semibold text-[var(--pol-light-brand-primary)] hover:bg-[var(--pol-light-surface-hover,var(--pol-light-surface-subtle))] transition-colors"
                      >
                        مقایسه قیمت و سفارش کالا
                      </Link>
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
