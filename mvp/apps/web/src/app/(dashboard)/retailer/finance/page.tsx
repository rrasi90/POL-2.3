"use client";

import { useCallback, useEffect, useState } from "react";
import { Button, Card, EmptyState, ErrorState, Skeleton, StatusChip } from "@pol/ui";
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
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری امور مالی">
        <Skeleton className="h-9 w-56" />
        <Card className="p-6">
          <Skeleton lines={5} />
        </Card>
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
              امور مالی و فاکتورها
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              R-16
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            مشاهده صورت‌حساب‌ها، فاکتورهای رسمی و سوابق پرداخت سفارش‌ها
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      {/* Scope Disclaimer Banner */}
      <div className="flex items-start gap-3 rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-4 text-[13px] text-[var(--pol-light-text-secondary)] leading-relaxed">
        <span className="text-base">ℹ️</span>
        <div>
          <strong className="font-semibold text-[var(--pol-light-text-primary)]">نکته اجرایی:</strong>{" "}
          کیف پول و موجودی اعتباری خارج از دامنه آزمایشی MVP است (D-021). صورت‌حساب‌ها و فاکتورهای
          سفارش به محض صدور توسط تأمین‌کنندگان در این بخش ثبت می‌گردند.
        </div>
      </div>

      {/* Invoices List */}
      <section aria-label="فاکتورها" className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-[16px] font-bold text-[var(--pol-light-text-primary)]">
            فهرست فاکتورها
          </h2>
          <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
            {invoices.length.toLocaleString("fa-IR")} فاکتور
          </span>
        </div>

        {invoices.length === 0 ? (
          <EmptyState
            title="فاکتوری یافت نشد"
            description="هنوز هیچ فاکتوری برای حساب خرده‌فروشی شما صادر نشده است."
          />
        ) : (
          <div className="grid gap-3">
            {invoices.map((inv) => (
              <Card
                key={String(inv.id)}
                className="p-4 transition-all duration-200 hover:shadow-[var(--pol-shadow-md)] hover:border-[var(--pol-light-border-strong)]"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[var(--pol-light-surface-subtle)] text-[18px]">
                      📄
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[14px] font-bold text-[var(--pol-light-text-primary)]" dir="ltr">
                          {inv.invoice_number ?? `INV-${String(inv.id).slice(0, 8)}`}
                        </span>
                        {inv.status ? (
                          <StatusChip tone="info">{inv.status}</StatusChip>
                        ) : (
                          <StatusChip tone="neutral">صادر شده</StatusChip>
                        )}
                      </div>
                      <div className="mt-1 flex flex-wrap items-center gap-2 text-[12px] text-[var(--pol-light-text-secondary)]">
                        {inv.order_id && (
                          <span dir="ltr" className="font-mono">
                            سفارش: {inv.order_id.slice(0, 8)}...
                          </span>
                        )}
                        <span>·</span>
                        <span>{formatDateTime(inv.issued_at ?? inv.created_at)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between border-t border-[var(--pol-light-border-subtle)] pt-3 sm:border-0 sm:pt-0 sm:justify-end sm:gap-4">
                    <div className="text-start sm:text-end">
                      <span className="block text-[11px] text-[var(--pol-light-text-secondary)]">
                        مبلغ کل
                      </span>
                      <span className="text-[16px] font-bold text-[var(--pol-light-text-primary)]">
                        {formatToman(inv.total_amount_toman)}
                      </span>
                    </div>
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
