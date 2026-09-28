"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
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
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری مالی">
        <Skeleton className="h-9 w-48" />
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <Card key={i} className="p-5">
              <Skeleton lines={2} />
            </Card>
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
    <div className="space-y-6">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] md:text-[26px] font-bold text-[var(--pol-light-text-primary)]">
              امور مالی و گزارش‌های تسویه
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              V-17
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            خلاصه مبالغ تسویه‌شده، در جریان و فاکتورهای فروش صادرشده
          </p>
        </div>

        <Button variant="secondary" size="sm" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2">
        <Card className="p-5 border-emerald-300 bg-emerald-50/20 dark:border-emerald-800 dark:bg-emerald-950/20">
          <span className="text-[13px] font-medium text-[var(--pol-light-text-secondary)]">
            مجموع تسویه‌شده قطعی
          </span>
          <div className="mt-2 text-[26px] font-bold text-emerald-600 dark:text-emerald-400">
            {formatToman(paidTotal)}
          </div>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
            واریزشده به حساب بانکی شبا
          </p>
        </Card>

        <Card className="p-5 border-amber-300 bg-amber-50/20 dark:border-amber-800 dark:bg-amber-950/20">
          <span className="text-[13px] font-medium text-[var(--pol-light-text-secondary)]">
            مبالغ در حال پردازش و تسویه
          </span>
          <div className="mt-2 text-[26px] font-bold text-amber-700 dark:text-amber-400">
            {formatToman(pendingTotal)}
          </div>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
            در چرخه تسویه دوره‌ای پُل
          </p>
        </Card>
      </div>

      {/* Scope Disclaimer */}
      <div className="flex items-start gap-3 rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-4 text-[13px] text-[var(--pol-light-text-secondary)] leading-relaxed">
        <span className="text-base">ℹ️</span>
        <div>
          <strong className="font-semibold text-[var(--pol-light-text-primary)]">نکته تسویه:</strong>{" "}
          تسویه‌حساب‌ها طبق توافق‌نامه پایا/ساتنا به صورت دوره‌ای و پس از تحویل قطعی سفارش‌ها انجام
          می‌گردد. کیف پول اعتباری در فاز فعلی پشتیبانی نمی‌شود (D-021).
        </div>
      </div>

      {/* Settlements List */}
      <section aria-label="تسویه‌حساب‌ها" className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
            دستورهای تسویه‌حساب
          </h2>
          <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
            {settlements.length.toLocaleString("fa-IR")} مورد
          </span>
        </div>

        {settlements.length === 0 ? (
          <EmptyState
            title="هیچ تسویه‌ای ثبت نشده است"
            description="به محض اتمام اولین چرخه فروش و تحویل سفارش‌ها، دستور تسویه در این بخش ثبت می‌شود."
          />
        ) : (
          <div className="grid gap-3">
            {settlements.map((s) => (
              <Card key={s.id} className="p-4">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex items-center gap-2.5">
                    <StatusChip tone={settlementStatusTone[s.status ?? ""] ?? "neutral"}>
                      {settlementStatusLabel[s.status ?? ""] ?? s.status ?? "—"}
                    </StatusChip>
                    <span className="font-mono text-[14px] font-bold text-[var(--pol-light-text-primary)]" dir="ltr">
                      {s.settlement_number ?? `SETTLE-${s.id.slice(0, 8)}`}
                    </span>
                  </div>

                  <div className="flex items-center justify-between sm:gap-6 border-t border-[var(--pol-light-border-subtle)] pt-2 sm:border-0 sm:pt-0">
                    <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                      {formatDateTime(s.created_at)}
                    </span>
                    <span className="text-[16px] font-bold text-[var(--pol-light-text-primary)]">
                      {formatToman(s.amount_toman)}
                    </span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>

      {/* Invoices List */}
      <section aria-label="فاکتورهای فروش" className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
            فاکتورهای فروش
          </h2>
          <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
            {invoices.length.toLocaleString("fa-IR")} فاکتور
          </span>
        </div>

        {invoices.length === 0 ? (
          <EmptyState
            title="فاکتوری ثبت نشده است"
            description="فاکتورهای رسمی سفارش‌های تحویل‌شده در این بخش بایگانی می‌گردند."
          />
        ) : (
          <div className="grid gap-3">
            {invoices.map((inv) => (
              <Card key={inv.id} className="p-4">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex items-center gap-2.5">
                    <span className="font-mono text-[14px] font-bold text-[var(--pol-light-text-primary)]" dir="ltr">
                      {inv.invoice_number ?? `INV-${inv.id.slice(0, 8)}`}
                    </span>
                    {inv.order_id && (
                      <span className="text-[12px] text-[var(--pol-light-text-secondary)]" dir="ltr">
                        سفارش: {inv.order_id.slice(0, 8)}...
                      </span>
                    )}
                  </div>

                  <div className="flex items-center justify-between sm:gap-6 border-t border-[var(--pol-light-border-subtle)] pt-2 sm:border-0 sm:pt-0">
                    <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                      {formatDateTime(inv.issued_at ?? inv.created_at)}
                    </span>
                    <span className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                      {formatToman(inv.total_amount_toman)}
                    </span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
