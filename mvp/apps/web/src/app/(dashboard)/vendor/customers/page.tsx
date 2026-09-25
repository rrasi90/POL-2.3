"use client";

import { useCallback, useEffect, useState } from "react";
import { Button, EmptyState, ErrorState, Field, Skeleton } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, formatDateTime, itemsOf, type LoadState } from "../_shared";

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

  useEffect(() => { void load(); }, [load]);

  if (state === "loading") {
    return <div className="space-y-4" aria-busy="true"><Skeleton className="h-8 w-48" /><div className={cardCls}><Skeleton lines={6} /></div></div>;
  }
  if (state === "error") {
    return <ErrorState title="دریافت مشتریان ناموفق بود" description={error ?? undefined} onRetry={() => void load()} />;
  }

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">مشتریان</h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">V-09 · {rows.length.toLocaleString("fa-IR")} مشتری</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>به‌روزرسانی</Button>
      </header>

      <section className={cardCls} aria-label="جستجوی مشتری">
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-[220px] flex-1">
            <Field label="جستجو" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="نام فروشگاه، نام یا موبایل" dir="rtl" />
          </div>
          <Button onClick={() => void load()}>جستجو</Button>
        </div>
      </section>

      {rows.length === 0 ? (
        <EmptyState title="مشتری ثبت‌شده‌ای نیست" description="مشتریان بر اساس سفارش‌های واقعی این فروشنده نمایش داده می‌شوند." />
      ) : (
        <ul role="list" className="space-y-2">
          {rows.map((row) => (
            <li key={row.retailer_id} className={cardCls}>
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-[15px] font-semibold text-[var(--pol-light-text-primary)]">{row.store_name ?? "فروشگاه"}</span>
                <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">{formatDateTime(row.last_order_at)}</span>
              </div>
              <div className="mt-2 grid gap-2 text-[13px] text-[var(--pol-light-text-secondary)] md:grid-cols-3">
                <span>{row.full_name ?? "—"}</span>
                <span dir="ltr">{row.phone_number ?? "—"}</span>
                <span>{[row.city, row.neighborhood].filter(Boolean).join(" · ") || "—"}</span>
              </div>
              <div className="mt-2 text-[12px] text-[var(--pol-light-text-muted)]">
                تعداد سفارش: {Number(row.order_count ?? 0).toLocaleString("fa-IR")}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
