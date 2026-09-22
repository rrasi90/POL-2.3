"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Button,
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
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری ویترین">
        <Skeleton className="h-8 w-64" />
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <Skeleton lines={4} />
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

  const name = vendor.name ?? vendor.display_name ?? "—";

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-start gap-3">
        <div>
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            {name}
          </h1>
          <p className="mt-1 flex flex-wrap items-center gap-2">
            {vendor.city ? (
              <span className="text-[13px] text-[var(--pol-light-text-secondary)]">
                {vendor.city}
              </span>
            ) : null}
            <span className="text-[11px] text-[var(--pol-light-text-muted)]">
              {formatDateTime(vendor.created_at)}
            </span>
          </p>
        </div>
        <div className="ms-auto flex flex-wrap gap-2">
          <Button variant="ghost" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
          <Link
            href="/retailer/vendors"
            className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
          >
            همه تأمین‌کنندگان
          </Link>
        </div>
      </header>

      <section
        aria-label="خلاصه فروشگاه"
        className="flex flex-wrap items-center gap-2 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
      >
        {vendor.is_active === false ? (
          <StatusChip tone="neutral">غیرفعال</StatusChip>
        ) : (
          <StatusChip tone="success">فعال</StatusChip>
        )}
        <span className="text-[13px] text-[var(--pol-light-text-secondary)]">
          {products.length.toLocaleString("fa-IR")} کالا در ویترین
        </span>
      </section>

      {vendor.description ? (
        <section
          aria-label="درباره فروشگاه"
          className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
        >
          <p className="text-[13px] leading-[22px] text-[var(--pol-light-text-secondary)]">
            {vendor.description}
          </p>
        </section>
      ) : null}

      <section aria-label="کالاهای فروشگاه">
        <div className="flex items-center gap-2">
          <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
            کالاها
          </h2>
          <Link
            href="/retailer/catalog"
            className="ms-auto text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
          >
            جستجوی سراسری کاتالوگ
          </Link>
        </div>
        {products.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="کالایی در ویترین نیست"
              description="این تأمین‌کننده در حال حاضر کالایی ارائه نمی‌دهد."
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {products.map((p) => (
              <li
                key={String(p.id)}
                className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
              >
                <div className="flex flex-wrap items-start gap-2">
                  <p className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
                    {p.product_name ?? p.name ?? "—"}
                  </p>
                  {p.is_available === false ? (
                    <StatusChip tone="warning">ناموجود</StatusChip>
                  ) : null}
                </div>
                {p.brand_name ? (
                  <p className="mt-0.5 text-[12px] text-[var(--pol-light-text-secondary)]">
                    {p.brand_name}
                  </p>
                ) : null}
                <div className="mt-2 flex flex-wrap items-center gap-2 text-[13px]">
                  <span className="font-medium text-[var(--pol-light-text-primary)]">
                    {formatToman(p.price_toman)}
                  </span>
                  {p.stock_quantity != null ? (
                    <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
                      موجودی {Number(p.stock_quantity).toLocaleString("fa-IR")}
                      {p.packaging_unit ? ` ${p.packaging_unit}` : ""}
                    </span>
                  ) : null}
                </div>
                {p.product_id ? (
                  <Link
                    href={`/retailer/catalog/${p.product_id}`}
                    className="mt-2 inline-block text-[12px] text-[var(--pol-light-brand-primary)] hover:underline"
                  >
                    مقایسه قیمت و فروشندگان
                  </Link>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
