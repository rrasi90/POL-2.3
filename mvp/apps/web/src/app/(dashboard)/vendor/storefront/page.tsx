"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Button,
  EmptyState,
  ErrorState,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { useAuthStore } from "@/lib/auth/store";
import {
  cardCls,
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
 * Manage mutations: no storefront-write HTTP in API map → no fake edit success.
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
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری ویترین">
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
        title="دریافت ویترین ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          مدیریت ویترین
        </h1>
        <StatusChip tone="info">D-024 · فقط خواندنی</StatusChip>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">V-14</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      <section
        aria-label="محدودیت ویرایش"
        className="rounded-[12px] border border-dashed border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-subtle)] p-4"
      >
        <p className="text-[13px] text-[var(--pol-light-text-secondary)]">
          HTTP نوشتن ویترین (تغییر توضیح، بنر، ترتیب) در API map وجود ندارد. ویرایش شبیه‌سازی
          نمی‌شود. برای قیمت و موجودی از کاتالوگ استفاده کنید.
        </p>
        <div className="mt-2 flex flex-wrap gap-2">
          <Link
            href="/vendor/catalog"
            className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
          >
            کاتالوگ و قیمت
          </Link>
          <Link
            href="/vendor/inventory"
            className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
          >
            موجودی
          </Link>
        </div>
      </section>

      <section aria-label="فروشگاه">
        {vendors.length === 0 ? (
          <EmptyState
            title="ویترینی یافت نشد"
            description="فروشگاهی در storefront ثبت نشده است."
          />
        ) : (
          <div className="flex flex-wrap gap-2">
            {vendors.map((v) => (
              <button
                key={String(v.id)}
                type="button"
                onClick={() => void selectVendor(v)}
                className={[
                  "rounded-full border px-3 py-1.5 text-[12px] transition-colors duration-[160ms]",
                  selected?.id === v.id
                    ? "border-transparent bg-[var(--pol-light-brand-primary)] text-white"
                    : "border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)]",
                ].join(" ")}
              >
                {v.name ?? v.display_name ?? String(v.id)}
              </button>
            ))}
          </div>
        )}
      </section>

      {selected ? (
        <section aria-label="جزئیات فروشگاه" className={cardCls}>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
              {selected.name ?? selected.display_name ?? "—"}
            </h2>
            {selected.is_active === false ? (
              <StatusChip tone="neutral">غیرفعال</StatusChip>
            ) : (
              <StatusChip tone="success">فعال</StatusChip>
            )}
            <span className="ms-auto text-[12px] text-[var(--pol-light-text-muted)]">
              {selected.city ?? "—"} · {formatDateTime(selected.created_at)}
            </span>
          </div>
          {selected.description ? (
            <p className="mt-2 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
              {selected.description}
            </p>
          ) : null}
          <div className="mt-3 text-[12px] text-[var(--pol-light-text-muted)]" dir="ltr">
            vendor_id={selected.id}
          </div>
        </section>
      ) : null}

      <section aria-label="کالاهای ویترین">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          کالاها در ویترین
        </h2>
        {products.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="کالایی در ویترین نیست"
              description="پس از فعال‌سازی کالا در کاتالوگ، اینجا نمایش داده می‌شود."
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {products.map((p) => (
              <li key={String(p.id)} className={cardCls}>
                <div className="flex flex-wrap items-start gap-2">
                  <p className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
                    {p.product_name ?? p.name ?? "—"}
                  </p>
                  {p.is_available === false ? (
                    <StatusChip tone="warning">ناموجود</StatusChip>
                  ) : null}
                </div>
                <div className="mt-2 flex flex-wrap gap-2 text-[13px] text-[var(--pol-light-text-secondary)]">
                  <span>{formatToman(p.price_toman)}</span>
                  {p.stock_quantity != null ? (
                    <span>
                      {Number(p.stock_quantity).toLocaleString("fa-IR")}
                      {p.packaging_unit ? ` ${p.packaging_unit}` : ""}
                    </span>
                  ) : null}
                </div>
                {p.product_id ? (
                  <Link
                    href={`/retailer/catalog/${p.product_id}`}
                    className="mt-2 inline-block text-[12px] text-[var(--pol-light-brand-primary)] hover:underline"
                  >
                    مشاهده عمومی
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
