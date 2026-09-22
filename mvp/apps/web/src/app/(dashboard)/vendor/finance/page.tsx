"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Button,
  EmptyState,
  ErrorState,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  cardCls,
  formatDateTime,
  formatToman,
  itemsOf,
  settlementStatusLabel,
  settlementStatusTone,
  type LoadState,
} from "../_shared";

interface InvoiceRow {
  id: string;
  invoice_number?: string | null;
  order_id?: string | null;
  status?: string | null;
  total_amount_toman?: number | null;
  issued_at?: string | null;
  created_at?: string | null;
}

interface SettlementRow {
  id: string;
  settlement_number?: string | null;
  status?: string | null;
  amount_toman?: number | null;
  created_at?: string | null;
}

/**
 * V-17 financial activity — settlements + invoices summary.
 * Wallet UI out of scope (D-021).
 * GET /vendors/settlements, GET /invoices
 */
export default function VendorFinancePage() {
  const [settlements, setSettlements] = useState<SettlementRow[]>([]);
  const [invoices, setInvoices] = useState<InvoiceRow[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const [s, inv] = await Promise.all([
        getApi().get<unknown>("/api/v1/vendors/settlements"),
        getApi().get<unknown>("/api/v1/invoices"),
      ]);
      setSettlements(itemsOf<SettlementRow>(s, "settlements"));
      setInvoices(itemsOf<InvoiceRow>(inv, "invoices"));
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت فعالیت مالی ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const paidTotal = settlements
    .filter((s) => s.status === "PAID")
    .reduce((sum, s) => sum + (Number(s.amount_toman) || 0), 0);
  const pendingTotal = settlements
    .filter((s) => s.status === "PENDING" || s.status === "PROCESSING")
    .reduce((sum, s) => sum + (Number(s.amount_toman) || 0), 0);

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری مالی">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-3 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className={cardCls}>
              <Skeleton lines={2} />
            </div>
          ))}
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
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          فعالیت مالی
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">V-17</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      <section aria-label="کیف پول" className="rounded-[12px] border border-dashed border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-subtle)] p-4">
        <p className="text-[13px] text-[var(--pol-light-text-secondary)]">
          کیف پول و موجودی ذخیره‌شده خارج از دامنه MVP است (D-021). فقط تسویه و فاکتور.
        </p>
      </section>

      <section aria-label="خلاصه" className="grid gap-3 sm:grid-cols-3">
        <div className={cardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">تسویه‌شده</p>
          <p className="mt-1 text-[20px] font-bold text-[var(--pol-light-text-primary)]">
            {formatToman(paidTotal)}
          </p>
        </div>
        <div className={cardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">در انتظار</p>
          <p className="mt-1 text-[20px] font-bold text-[var(--pol-light-text-primary)]">
            {formatToman(pendingTotal)}
          </p>
        </div>
        <div className={cardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">فاکتورها</p>
          <p className="mt-1 text-[20px] font-bold text-[var(--pol-light-text-primary)]">
            {invoices.length.toLocaleString("fa-IR")}
          </p>
        </div>
      </section>

      <section aria-label="آخرین تسویه‌ها">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          تسویه‌ها
        </h2>
        {settlements.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="تسویه‌ای ثبت نشده" />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {settlements.slice(0, 10).map((s) => (
              <li key={String(s.id)} className="flex flex-wrap items-center gap-2 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-3">
                <StatusChip tone={settlementStatusTone[s.status ?? ""] ?? "neutral"}>
                  {settlementStatusLabel[s.status ?? ""] ?? s.status ?? "—"}
                </StatusChip>
                <span className="text-[13px] text-[var(--pol-light-text-primary)]" dir="ltr">
                  {s.settlement_number ?? String(s.id)}
                </span>
                <span className="ms-auto text-[13px] font-medium text-[var(--pol-light-text-primary)]">
                  {formatToman(s.amount_toman)}
                </span>
                <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                  {formatDateTime(s.created_at)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="آخرین فاکتورها">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          فاکتورها
        </h2>
        {invoices.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="فاکتوری یافت نشد" />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {invoices.slice(0, 10).map((inv) => (
              <li key={String(inv.id)} className="flex flex-wrap items-center gap-2 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-3">
                {inv.status ? <StatusChip tone="info">{inv.status}</StatusChip> : null}
                <span className="text-[13px] font-semibold text-[var(--pol-light-text-primary)]" dir="ltr">
                  {inv.invoice_number ?? String(inv.id)}
                </span>
                <span className="ms-auto text-[13px] font-medium text-[var(--pol-light-text-primary)]">
                  {formatToman(inv.total_amount_toman)}
                </span>
                <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                  {formatDateTime(inv.issued_at ?? inv.created_at)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
