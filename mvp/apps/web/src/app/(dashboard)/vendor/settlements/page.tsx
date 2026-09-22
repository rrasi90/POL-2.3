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
import {
  cardCls,
  formatDateTime,
  formatToman,
  itemsOf,
  settlementStatusLabel,
  settlementStatusTone,
  str,
  type LoadState,
} from "../_shared";

interface SettlementRow {
  id: string;
  settlement_number?: string | null;
  status?: string | null;
  amount_toman?: number | null;
  period_start?: string | null;
  period_end?: string | null;
  paid_at?: string | null;
  created_at?: string | null;
}

interface InvoiceRow {
  id: string;
  invoice_number?: string | null;
  order_id?: string | null;
  status?: string | null;
  total_amount_toman?: number | null;
  issued_at?: string | null;
  created_at?: string | null;
}

/**
 * V-10 settlements + invoices (reconciliation / documents).
 * GET /vendors/settlements, GET /invoices
 */
export default function VendorSettlementsPage() {
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
      setErrorMessage(err instanceof Error ? err.message : "دریافت تسویه‌ها ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری تسویه‌ها">
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
        title="دریافت تسویه و اسناد ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          تسویه و اسناد
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">V-10</span>
        <Link
          href="/vendor/finance"
          className="text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
        >
          فعالیت مالی
        </Link>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      <section aria-label="تسویه‌ها">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          تسویه‌ها
        </h2>
        {settlements.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="تسویه‌ای ثبت نشده"
              description="هنوز دوره تسویه‌ای برای شما باز نشده است."
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {settlements.map((s) => (
              <li key={String(s.id)} className={cardCls}>
                <div className="flex flex-wrap items-center gap-2">
                  <StatusChip tone={settlementStatusTone[s.status ?? ""] ?? "neutral"}>
                    {settlementStatusLabel[s.status ?? ""] ?? s.status ?? "—"}
                  </StatusChip>
                  <span className="text-[13px] text-[var(--pol-light-text-primary)]" dir="ltr">
                    {s.settlement_number ?? String(s.id)}
                  </span>
                  <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(s.created_at)}
                  </span>
                </div>
                <div className="mt-2 flex flex-wrap gap-3 text-[13px]">
                  <span className="font-medium text-[var(--pol-light-text-primary)]">
                    {formatToman(s.amount_toman)}
                  </span>
                  {s.period_start || s.period_end ? (
                    <span className="text-[var(--pol-light-text-secondary)]">
                      دوره: {formatDateTime(s.period_start)} — {formatDateTime(s.period_end)}
                    </span>
                  ) : null}
                  {s.paid_at ? (
                    <span className="text-[var(--pol-light-text-secondary)]">
                      پرداخت: {formatDateTime(s.paid_at)}
                    </span>
                  ) : null}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="فاکتورها">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          فاکتورها
        </h2>
        {invoices.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="فاکتوری یافت نشد" description="سندی صادر نشده است." />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {invoices.map((inv) => (
              <li key={String(inv.id)} className={cardCls}>
                <div className="flex flex-wrap items-center gap-2">
                  {inv.status ? <StatusChip tone="info">{inv.status}</StatusChip> : null}
                  <span className="text-[13px] font-semibold text-[var(--pol-light-text-primary)]" dir="ltr">
                    {inv.invoice_number ?? str(inv.id)}
                  </span>
                  <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(inv.issued_at ?? inv.created_at)}
                  </span>
                </div>
                <div className="mt-2 flex flex-wrap gap-3 text-[13px]">
                  <span className="font-medium text-[var(--pol-light-text-primary)]">
                    {formatToman(inv.total_amount_toman)}
                  </span>
                  {inv.order_id ? (
                    <Link
                      href={`/vendor/orders/${inv.order_id}`}
                      className="text-[var(--pol-light-brand-primary)] hover:underline"
                      dir="ltr"
                    >
                      order {inv.order_id}
                    </Link>
                  ) : null}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
