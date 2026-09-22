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
    return name.includes(q) || String(v.id).toLowerCase().includes(q) || (v.city ?? "").toLowerCase().includes(q);
  });

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری تأمین‌کنندگان">
        <Skeleton className="h-8 w-48" />
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <Skeleton lines={5} />
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
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          تأمین‌کنندگان
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">R-17</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      <SearchField
        label="جستجوی تأمین‌کننده"
        placeholder="نام یا شهر…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      {filtered.length === 0 ? (
        <EmptyState
          title="تأمین‌کننده‌ای یافت نشد"
          description="فهرست فروشندگان فعال خالی است ا عبارت جستجو را تغییر دهید."
        />
      ) : (
        <ul role="list" className="space-y-2">
          {filtered.map((v) => (
            <li key={String(v.id)}>
              <Link
                href={`/retailer/vendors/${v.id}`}
                className="flex flex-wrap items-center gap-3 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4 transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]"
              >
                <div>
                  <p className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
                    {v.name ?? v.display_name ?? "—"}
                  </p>
                  <p className="mt-0.5 text-[12px] text-[var(--pol-light-text-secondary)]">
                    {v.city ?? "—"}
                    {v.product_count != null
                      ? ` · ${Number(v.product_count).toLocaleString("fa-IR")} کالا`
                      : ""}
                  </p>
                </div>
                {v.is_active === false ? (
                  <StatusChip tone="neutral">غیرفعال</StatusChip>
                ) : (
                  <StatusChip tone="success">فعال</StatusChip>
                )}
                <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                  {formatDateTime(v.created_at)}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
