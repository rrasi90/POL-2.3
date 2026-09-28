"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  SearchField,
  Skeleton,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { formatDateTime, itemsOf, type LoadState } from "../_shared";

interface Customer {
  retailer_id: string;
  store_name?: string | null;
  city?: string | null;
  neighborhood?: string | null;
  full_name?: string | null;
  phone_number?: string | null;
  order_count?: number | null;
  last_order_at?: string | null;
}

export default function VendorCustomersPage() {
  const [rows, setRows] = useState<Customer[]>([]);
  const [query, setQuery] = useState("");
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setError(null);
    try {
      const qs = query.trim() ? `?query=${encodeURIComponent(query.trim())}` : "";
      const data = await getApi().get<unknown>(`/api/v1/vendors/customers${qs}`);
      setRows(itemsOf<Customer>(data, "customers"));
      setState("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "دریافت مشتریان ناموفق بود");
      setState("error");
    }
  }, [query]);

  useEffect(() => {
    void load();
  }, [load]);

  if (state === "loading") {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری مشتریان">
        <Skeleton className="h-9 w-48" />
        <div className="grid gap-3 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
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
        title="دریافت مشتریان ناموفق بود"
        description={error ?? undefined}
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
              شبکه مشتریان و خرده‌فروشان
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              V-09 · {rows.length.toLocaleString("fa-IR")} مشتری
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            سوپرمارکت‌ها و فروشگاه‌هایی که سابقه ثبت سفارش از بنکداری شما را دارند
          </p>
        </div>

        <Button variant="secondary" size="sm" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      {/* Search Bar */}
      <div className="max-w-md">
        <SearchField
          label="جستجوی مشتری"
          placeholder="جستجو با نام فروشگاه، نام مدیر یا شماره همراه..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {/* Customers List */}
      {rows.length === 0 ? (
        <EmptyState
          title="مشتری ثبت‌شده‌ای یافت نشد"
          description="مشتریان بر اساس تاریخچه سفارش‌های قطعی ثبت‌شده برای بنکداری شما نمایش داده می‌شوند."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {rows.map((row) => (
            <Card
              key={row.retailer_id}
              className="p-5 transition-all duration-200 hover:shadow-[var(--pol-shadow-md)] hover:border-[var(--pol-light-border-strong)]"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[var(--pol-light-surface-subtle)] text-[18px]">
                    🏪
                  </div>
                  <div>
                    <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                      {row.store_name ?? "فروشگاه خرده‌فروشی"}
                    </h2>
                    {row.full_name && (
                      <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
                        مدیریت: {row.full_name}
                      </span>
                    )}
                  </div>
                </div>

                <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-1 text-[11px] font-bold text-[var(--pol-light-text-secondary)]">
                  {Number(row.order_count ?? 0).toLocaleString("fa-IR")} سفارش
                </span>
              </div>

              <div className="mt-4 grid gap-2 border-t border-[var(--pol-light-border-subtle)] pt-3 text-[12px] text-[var(--pol-light-text-secondary)]">
                <div className="flex items-center justify-between">
                  <span>📍 محدوده:</span>
                  <span className="font-medium text-[var(--pol-light-text-primary)]">
                    {[row.city, row.neighborhood].filter(Boolean).join(" · ") || "نامشخص"}
                  </span>
                </div>
                {row.phone_number && (
                  <div className="flex items-center justify-between">
                    <span>شماره تماس:</span>
                    <span className="font-mono font-medium text-[var(--pol-light-text-primary)]" dir="ltr">
                      {row.phone_number}
                    </span>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span>آخرین سفارش:</span>
                  <span className="text-[var(--pol-light-text-muted)]">
                    {formatDateTime(row.last_order_at)}
                  </span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
