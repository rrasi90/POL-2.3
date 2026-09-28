"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Button,
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
  cardCls,
  formatDateTime,
  formatToman,
  itemsOf,
  reconStatusLabel,
  reconStatusTone,
  type LoadState,
} from "../_shared";

interface ExceptionsDashboard {
  delivery_exceptions?: { total?: number; open_count?: number; resolved_count?: number; escalated_count?: number };
  disputes?: { total?: number; open_disputes?: number };
  support_cases?: { total?: number; open_cases?: number };
}

interface ReconCase {
  id: string;
  status?: string | null;
  expected_amount_toman?: number | string | null;
  observed_amount_toman?: number | string | null;
  opened_at?: string | null;
  attempt_count?: number | null;
}

export default function OpsRiskPage() {
  const [dashboard, setDashboard] = useState<ExceptionsDashboard | null>(null);
  const [recon, setRecon] = useState<ReconCase[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setError(null);
    try {
      const [d, r] = await Promise.all([
        getApi().get<ExceptionsDashboard>("/api/v1/admin/exceptions/dashboard"),
        getApi().get<unknown>("/api/v1/finance/reconciliation?status=OPEN&limit=10&offset=0"),
      ]);
      setDashboard(d);
      setRecon(itemsOf<ReconCase>(r, "cases"));
      setState("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "دریافت سیگنال‌های ریسک ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری سیگنال‌های ریسک">
        <Skeleton className="h-8 w-56" />
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className={cardCls}><Skeleton lines={3} /></div>
          ))}
        </div>
        <div className={cardCls}><Skeleton lines={6} /></div>
      </div>
    );
  }

  if (state === "error") {
    return <ErrorState title="دریافت سیگنال‌های ریسک ناموفق بود" description={error ?? undefined} onRetry={() => void load()} />;
  }

  const delivery = dashboard?.delivery_exceptions ?? {};
  const disputes = dashboard?.disputes ?? {};
  const support = dashboard?.support_cases ?? {};

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline justify-between gap-3 border-b border-[var(--pol-light-border-subtle)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] leading-[30px] font-bold text-[var(--pol-light-text-primary)]">
              ریسک و تاب‌آوری عملیاتی
            </h1>
            <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              O-07
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-muted)]">
            پایش آنی نقاط اصطکاک زنجیره تأمین، مغایرت‌های مالی و استثناهای تسویه‌نشده
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
        </div>
      </header>

      {/* Operational Policy Callout */}
      <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-3.5 text-[12px] leading-[20px] text-[var(--pol-light-text-secondary)]">
        <strong className="font-semibold text-[var(--pol-light-text-primary)]">سیاست محاسبه ریسک: </strong>
        این کنسول از امتیاز ریسک تصنعی استفاده نمی‌کند و فقط بازتاب‌دهنده رویدادها و موارد باز واقعی در سیستم تحویل، پشتیبانی و تطبیق حسابداری است.
      </div>

      {/* Signal Counters */}
      <section aria-label="سیگنال‌های عملیاتی" className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className={cardCls}>
          <div className="flex items-center justify-between">
            <p className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">استثناهای تحویل باز</p>
            {(delivery.open_count ?? 0) > 0 ? (
              <StatusChip tone="danger">فوری</StatusChip>
            ) : (
              <StatusChip tone="success">عادی</StatusChip>
            )}
          </div>
          <p className="mt-2 text-[26px] font-extrabold tabular-nums text-[var(--pol-light-text-primary)]">
            {(delivery.open_count ?? 0).toLocaleString("fa-IR")}
          </p>
          <div className="mt-2 border-t border-[var(--pol-light-border-subtle)] pt-2 text-[11px] text-[var(--pol-light-text-muted)]">
            کل: {Number(delivery.total ?? 0).toLocaleString("fa-IR")} · ارجاع‌شده: {Number(delivery.escalated_count ?? 0).toLocaleString("fa-IR")}
          </div>
        </div>

        <div className={cardCls}>
          <div className="flex items-center justify-between">
            <p className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">اختلافات سفارشات</p>
            {(disputes.open_disputes ?? 0) > 0 ? (
              <StatusChip tone="warning">نیازمند بررسی</StatusChip>
            ) : (
              <StatusChip tone="neutral">صفر</StatusChip>
            )}
          </div>
          <p className="mt-2 text-[26px] font-extrabold tabular-nums text-[var(--pol-light-text-primary)]">
            {(disputes.open_disputes ?? 0).toLocaleString("fa-IR")}
          </p>
          <div className="mt-2 border-t border-[var(--pol-light-border-subtle)] pt-2 text-[11px] text-[var(--pol-light-text-muted)]">
            کل اختلافات ثبت‌شده: {Number(disputes.total ?? 0).toLocaleString("fa-IR")}
          </div>
        </div>

        <div className={cardCls}>
          <div className="flex items-center justify-between">
            <p className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">پرونده‌های پشتیبانی باز</p>
            {(support.open_cases ?? 0) > 0 ? (
              <StatusChip tone="info">در جریان</StatusChip>
            ) : (
              <StatusChip tone="neutral">پاک</StatusChip>
            )}
          </div>
          <p className="mt-2 text-[26px] font-extrabold tabular-nums text-[var(--pol-light-text-primary)]">
            {(support.open_cases ?? 0).toLocaleString("fa-IR")}
          </p>
          <div className="mt-2 border-t border-[var(--pol-light-border-subtle)] pt-2 text-[11px] text-[var(--pol-light-text-muted)]">
            کل پرونده‌ها: {Number(support.total ?? 0).toLocaleString("fa-IR")}
          </div>
        </div>

        <div className={cardCls}>
          <div className="flex items-center justify-between">
            <p className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">مغایرت‌های تطبیق مالی</p>
            {recon.length > 0 ? (
              <StatusChip tone="danger">اقدام لازم</StatusChip>
            ) : (
              <StatusChip tone="success">تراز</StatusChip>
            )}
          </div>
          <p className="mt-2 text-[26px] font-extrabold tabular-nums text-[var(--pol-light-text-primary)]">
            {recon.length.toLocaleString("fa-IR")}
          </p>
          <div className="mt-2 border-t border-[var(--pol-light-border-subtle)] pt-2 text-[11px] text-[var(--pol-light-text-muted)]">
            پرونده‌های OPEN در تطبیق مالی
          </div>
        </div>
      </section>

      {/* Open Reconciliation Table */}
      <section aria-label="موارد تطبیق باز" className={cardCls}>
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--pol-light-border-subtle)] pb-3">
          <div className="flex items-center gap-2">
            <h2 className="text-[14px] font-bold text-[var(--pol-light-text-primary)]">
              پرونده‌های تطبیق مالی باز
            </h2>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              {recon.length.toLocaleString("fa-IR")} مورد
            </span>
          </div>
          <Link
            href="/ops/reconciliation"
            className="text-[12px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
          >
            مشاهده کنسول کامل تطبیق مالی ←
          </Link>
        </div>

        {recon.length === 0 ? (
          <div className="py-6">
            <EmptyState
              title="مورد باز در تطبیق مالی وجود ندارد"
              description="تمام تراکنش‌ها و اقلام حسابداری تسویه و تطبیق داده شده‌اند."
            />
          </div>
        ) : (
          <div className="mt-3">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>شناسه پرونده</TableHead>
                  <TableHead>وضعیت</TableHead>
                  <TableHead>مبلغ انتظاری</TableHead>
                  <TableHead>مبلغ مشاهده‌شده</TableHead>
                  <TableHead>دفعات تلاش</TableHead>
                  <TableHead>زمان ثبت</TableHead>
                  <TableHead className="text-end">اقدام</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recon.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell className="font-mono text-[11px]" dir="ltr">
                      {item.id}
                    </TableCell>
                    <TableCell>
                      <StatusChip tone={reconStatusTone[item.status ?? ""] ?? "warning"}>
                        {reconStatusLabel[item.status ?? ""] ?? item.status ?? "OPEN"}
                      </StatusChip>
                    </TableCell>
                    <TableCell className="font-medium tabular-nums">
                      {item.expected_amount_toman != null ? formatToman(item.expected_amount_toman) : "—"}
                    </TableCell>
                    <TableCell className="font-medium tabular-nums">
                      {item.observed_amount_toman != null ? formatToman(item.observed_amount_toman) : "—"}
                    </TableCell>
                    <TableCell className="tabular-nums">
                      {Number(item.attempt_count ?? 0).toLocaleString("fa-IR")}
                    </TableCell>
                    <TableCell className="text-[12px] text-[var(--pol-light-text-muted)]">
                      {formatDateTime(item.opened_at)}
                    </TableCell>
                    <TableCell className="text-end">
                      <Link
                        href={`/ops/reconciliation`}
                        className="inline-flex h-7 items-center rounded-md border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-2.5 text-[11px] font-medium text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
                      >
                        بررسی
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </section>
    </div>
  );
}
