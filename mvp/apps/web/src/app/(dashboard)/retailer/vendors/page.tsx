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
import { formatDateTime, asRecordArray } from "../shared";

interface VendorRow {
  id: string;
  name?: string | null;
  display_name?: string | null;
  city?: string | null;
  is_active?: boolean | null;
  product_count?: number | null;
  created_at?: string | null;
}

type LoadState = "loading" | "error" | "ready";

/**
 * R-17 vendor search (storefront browse).
 * GET /storefront/vendors
 */
export default function RetailerVendorsPage() {
  const [vendors, setVendors] = useState<VendorRow[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [query, setQuery] = useState("");

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const data = await getApi().get<unknown>("/api/v1/storefront/vendors");
      setVendors(asRecordArray(data) as unknown as VendorRow[]);
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت تأمین‌کنندگان ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const filtered = vendors.filter((v) => {
    if (!query.trim()) return true;
    const q = query.trim().toLowerCase();
    const name = (v.name ?? v.display_name ?? "").toLowerCase();
    return (
      name.includes(q) ||
      String(v.id).toLowerCase().includes(q) ||
      (v.city ?? "").toLowerCase().includes(q)
    );
  });

  if (state === "loading") {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری تأمین‌کنندگان">
        <Skeleton className="h-9 w-52" />
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
        title="دریافت تأمین‌کنندگان ناموفق بود"
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
              شبکه تأمین‌کنندگان پُل
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              R-17
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            مشاهده بنکداران و تأمین‌کنندگان معتبر عضو سامانه و بررسی ویترین اختصاصی
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      {/* Search and Filter */}
      <div className="max-w-md">
        <SearchField
          label="جستجوی تأمین‌کننده"
          placeholder="جستجو بر اساس نام بنکدار، نام شرکت یا شهر..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {/* Vendors Grid */}
      {filtered.length === 0 ? (
        <EmptyState
          title="تأمین‌کننده‌ای یافت نشد"
          description="فهرست فروشندگان خالی است یا با عبارت جستجو مطابقت ندارد."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((v) => {
            const displayName = v.name ?? v.display_name ?? "تأمین‌کننده بدون نام";
            const initial = displayName.charAt(0);

            return (
              <Link
                key={String(v.id)}
                href={`/retailer/vendors/${v.id}`}
                className="group block focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)] rounded-xl"
              >
                <Card className="h-full p-5 transition-all duration-200 group-hover:shadow-[var(--pol-shadow-md)] group-hover:border-[var(--pol-light-border-strong)]">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[var(--pol-light-surface-subtle)] text-[16px] font-bold text-[var(--pol-light-brand-primary)]">
                        {initial}
                      </div>
                      <div>
                        <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)] group-hover:text-[var(--pol-light-brand-primary)] transition-colors">
                          {displayName}
                        </h2>
                        {v.city && (
                          <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
                            📍 {v.city}
                          </span>
                        )}
                      </div>
                    </div>

                    {v.is_active === false ? (
                      <StatusChip tone="neutral">غیرفعال</StatusChip>
                    ) : (
                      <StatusChip tone="success">فعال</StatusChip>
                    )}
                  </div>

                  <div className="mt-4 flex items-center justify-between border-t border-[var(--pol-light-border-subtle)] pt-3 text-[12px]">
                    <span className="text-[var(--pol-light-text-secondary)]">
                      {v.product_count != null
                        ? `${Number(v.product_count).toLocaleString("fa-IR")} کالای فعال`
                        : "تنوع کالا نامشخص"}
                    </span>
                    <span className="text-[var(--pol-light-text-muted)]">
                      {formatDateTime(v.created_at)}
                    </span>
                  </div>

                  <div className="mt-3 flex items-center justify-end text-[12px] font-medium text-[var(--pol-light-brand-primary)] group-hover:underline">
                    مشاهده ویترین و کاتالوگ ←
                  </div>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
