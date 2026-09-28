"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  Skeleton,
  StatusChip,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
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
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری تسویه‌ها">
        <Skeleton className="h-9 w-48" />
        <Card className="p-6">
          <Skeleton lines={5} />
        </Card>
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
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] md:text-[26px] font-bold text-[var(--pol-light-text-primary)]">
              تسویه‌حساب‌ها و اسناد مالی
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              V-10
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            جزئیات دوره‌های تسویه بانکی، مبالغ واریز شده و مدارک فاکتورهای رسمی
          </p>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <Link
            href="/vendor/finance"
            className="rounded-lg border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)] transition-colors"
          >
            داشبورد مالی
          </Link>
          <Button variant="secondary" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
        </div>
      </header>

      {/* Settlements Table */}
      <section aria-label="فهرست تسویه‌ها" className="space-y-3">
        <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
          دوره‌های تسویه‌حساب ({settlements.length.toLocaleString("fa-IR")} مورد)
        </h2>

        {settlements.length === 0 ? (
          <EmptyState
            title="هیچ ردیف تسویه‌ای موجود نیست"
            description="تسویه‌حساب‌ها به طور خودکار طبق برنامه زمانی تعیین‌شده تولید و واریز خواهند شد."
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>شماره پیگیری تسویه</TableHead>
                <TableHead>وضعیت</TableHead>
                <TableHead>بازه زمانی دوره</TableHead>
                <TableHead>تاریخ واریز / ایجاد</TableHead>
                <TableHead>مبلغ واریزی</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {settlements.map((s) => (
                <TableRow key={s.id}>
                  <TableCell className="font-mono font-bold" dir="ltr">
                    {s.settlement_number ?? `SETTLE-${s.id.slice(0, 8)}`}
                  </TableCell>
                  <TableCell>
                    <StatusChip tone={settlementStatusTone[s.status ?? ""] ?? "neutral"}>
                      {settlementStatusLabel[s.status ?? ""] ?? s.status ?? "—"}
                    </StatusChip>
                  </TableCell>
                  <TableCell className="text-[12px] text-[var(--pol-light-text-secondary)]">
                    {s.period_start ? formatDateTime(s.period_start) : "—"} تا{" "}
                    {s.period_end ? formatDateTime(s.period_end) : "—"}
                  </TableCell>
                  <TableCell className="text-[12px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(s.paid_at ?? s.created_at)}
                  </TableCell>
                  <TableCell className="font-bold">
                    {formatToman(s.amount_toman)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </section>

      {/* Invoices Table */}
      <section aria-label="فهرست فاکتورها" className="space-y-3">
        <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
          فاکتورهای رسمی صادرشده ({invoices.length.toLocaleString("fa-IR")} مورد)
        </h2>

        {invoices.length === 0 ? (
          <EmptyState title="هیچ فاکتوری ثبت نشده است" />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>شماره فاکتور</TableHead>
                <TableHead>سفارش مرتبط</TableHead>
                <TableHead>وضعیت فاکتور</TableHead>
                <TableHead>تاریخ صدور</TableHead>
                <TableHead>مبلغ کل</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {invoices.map((inv) => (
                <TableRow key={inv.id}>
                  <TableCell className="font-mono font-bold" dir="ltr">
                    {inv.invoice_number ?? `INV-${inv.id.slice(0, 8)}`}
                  </TableCell>
                  <TableCell className="font-mono text-[12px] text-[var(--pol-light-text-secondary)]" dir="ltr">
                    {inv.order_id ? inv.order_id.slice(0, 8) + "..." : "—"}
                  </TableCell>
                  <TableCell>
                    <StatusChip tone="info">{inv.status ?? "صادرشده"}</StatusChip>
                  </TableCell>
                  <TableCell className="text-[12px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(inv.issued_at ?? inv.created_at)}
                  </TableCell>
                  <TableCell className="font-bold">
                    {formatToman(inv.total_amount_toman)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </section>
    </div>
  );
}
