"use client";

import { useCallback, useEffect, useState } from "react";
import { Button, EmptyState, ErrorState, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { formatDateTime, formatToman, asRecordArray } from "../shared";

interface InvoiceRow {
  id: string;
  invoice_number?: string | null;
  order_id?: string | null;
  status?: string | null;
  total_amount_toman?: number | null;
  issued_at?: string | null;
  created_at?: string | null;
}

type LoadState = "loading" | "error" | "ready";

/**
 * R-16 financial activity — invoices only.
 * Wallet UI out of scope (D-021); no settlements for retailer.
 * GET /invoices
 */
export default function RetailerFinancePage() {
  const [invoices, setInvoices] = useState<InvoiceRow[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const data = await getApi().get<unknown>("/api/v1/invoices");
      setInvoices(asRecordArray(data) as unknown as InvoiceRow[]);
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت فاکتورها ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری مالی">
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
        title="دریافت فعالیت مالی ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          فعالیت مالی
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">R-16 · فاکتورها</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      <section aria-label="کیف پول" className="rounded-[12px] border border-dashed border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-subtle)] p-4">
        <p className="text-[13px] text-[var(--pol-light-text-secondary)]">
          کیف پول و موجودی ذخیره‌شده خارج از دامنه MVP است (D-021). فقط فاکتورها نمایش داده
          می‌شوند.
        </p>
      </section>

      <section aria-label="فاکتورها">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          فاکتورها
        </h2>
        {invoices.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="فاکتوری یافت نشد"
              description="هنوز فاکتوری برای حساب شما صادر نشده است."
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {invoices.map((inv) => (
              <li
                key={String(inv.id)}
                className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
              >
                <div className="flex flex-wrap items-center gap-2">
                  {inv.status ? <StatusChip tone="info">{inv.status}</StatusChip> : null}
                  <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(inv.issued_at ?? inv.created_at)}
                  </span>
                </div>
                <div className="mt-2 flex flex-wrap items-center gap-3">
                  <span className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]" dir="ltr">
                    {inv.invoice_number ?? String(inv.id)}
                  </span>
                  {inv.order_id ? (
                    <span className="text-[12px] text-[var(--pol-light-text-muted)]" dir="ltr">
                      order {inv.order_id}
                    </span>
                  ) : null}
                  <span className="ms-auto text-[14px] font-medium text-[var(--pol-light-text-primary)]">
                    {formatToman(inv.total_amount_toman)}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
