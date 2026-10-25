"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Button, Card, EmptyState, ErrorState, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  ageLabel,
  ageTone,
  disputeStatusLabel,
  disputeStatusTone,
  formatDateTime,
  formatToman,
  itemsOf,
  nextActionForOrder,
  orderStatusLabel,
  orderStatusTone,
  reconStatusLabel,
  reconStatusTone,
  str,
  supportPriorityLabel,
  supportPriorityTone,
  supportStatusLabel,
  supportStatusTone,
  type LoadState,
} from "../_shared";

type TabId = "orders" | "support" | "recon" | "rma";

const TABS: Array<{ id: TabId; label: string }> = [
  { id: "orders", label: "سفارش‌های فعال" },
  { id: "support", label: "تیکت‌های باز" },
  { id: "recon", label: "مغایرت‌های مالی" },
  { id: "rma", label: "مرجوعی و RMA" },
];

const OPEN_ORDER_STATUSES = new Set([
  "CREATED",
  "SUBMITTED",
  "ACCEPTED",
  "PARTIALLY_ACCEPTED",
  "PREPARING",
  "READY",
  "DISPATCHED",
]);

interface OrderRow {
  id: string;
  order_number?: string | null;
  order_status?: string | null;
  dispute_status?: string | null;
  total_amount_toman?: number | string | null;
  created_at?: string | null;
}

interface SupportRow {
  id: string;
  case_number?: string | null;
  subject?: string | null;
  case_type?: string | null;
  priority?: string | null;
  status?: string | null;
  created_at?: string | null;
}

interface ReconRow {
  id: string;
  status?: string | null;
  expected_amount_toman?: number | string | null;
  observed_amount_toman?: number | string | null;
  opened_at?: string | null;
}

interface RmaOrderRow extends OrderRow {
  has_returns?: boolean;
}

export default function OpsQueuesPage() {
  const [tab, setTab] = useState<TabId>("orders");
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [orders, setOrders] = useState<OrderRow[]>([]);
  const [support, setSupport] = useState<SupportRow[]>([]);
  const [recon, setRecon] = useState<ReconRow[]>([]);
  const [rmaOrders, setRmaOrders] = useState<RmaOrderRow[]>([]);

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const [o, s, r] = await Promise.all([
        getApi().get<unknown>("/api/v1/orders?limit=50&offset=0"),
        getApi().get<unknown>("/api/v1/support/cases"),
        getApi().get<unknown>("/api/v1/finance/reconciliation?limit=50&offset=0"),
      ]);
      const orderRows = itemsOf<OrderRow>(o, "orders");
      setOrders(orderRows);
      setSupport(itemsOf<SupportRow>(s, "cases"));
      setRecon(itemsOf<ReconRow>(r, "cases"));
      setRmaOrders(
        orderRows.filter(
          (row) =>
            (typeof row.dispute_status === "string" &&
              row.dispute_status !== "NONE" &&
              row.dispute_status !== "CLOSED") ||
            OPEN_ORDER_STATUSES.has(row.order_status ?? ""),
        ),
      );
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت صف‌ها ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const counts = useMemo(
    () => ({
      orders: orders.filter((o) => OPEN_ORDER_STATUSES.has(o.order_status ?? "")).length,
      support: support.filter((s) => s.status !== "CLOSED" && s.status !== "RESOLVED").length,
      recon: recon.filter((r) => r.status === "OPEN" || r.status === "MISMATCH").length,
      rma: rmaOrders.length,
    }),
    [orders, support, recon, rmaOrders],
  );

  if (state === "loading") {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری صف‌ها">
        <Skeleton className="h-9 w-48" />
        <div className="flex gap-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-8 w-28 rounded-full" />
          ))}
        </div>
        <div className="grid gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Card key={i} className="p-4">
              <Skeleton lines={3} />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت صف‌ها ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-[var(--pol-light-border-subtle)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[20px] md:text-[24px] font-bold text-[var(--pol-light-text-primary)]">
              صفوف یکپارچه عملیات
            </h1>
            <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-bold text-[var(--pol-light-text-secondary)]">
              O-02 · Multi-Queue
            </span>
          </div>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
            مرکز تریاژ و ارجاع سریع سفارش‌های نیازمند اقدام، تیکت‌های پشتیبانی و مغایرت‌های مالی
          </p>
        </div>

        <Button variant="secondary" size="sm" onClick={() => void load()}>
          به‌روزرسانی داده‌ها
        </Button>
      </header>

      {/* Queue Tabs */}
      <div role="tablist" aria-label="نوع صف" className="flex flex-wrap gap-2">
        {TABS.map((t) => {
          const isSelected = tab === t.id;
          const count = counts[t.id];
          return (
            <button
              key={t.id}
              role="tab"
              type="button"
              aria-selected={isSelected}
              onClick={() => setTab(t.id)}
              className={[
                "flex items-center gap-2 rounded-full px-4 py-1.5 text-[13px] font-medium transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]",
                isSelected
                  ? "bg-[var(--pol-light-brand-primary)] text-white shadow-sm"
                  : "border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)]",
              ].join(" ")}
            >
              <span>{t.label}</span>
              <span
                className={[
                  "rounded-full px-2 py-0.2 text-[11px] font-bold",
                  isSelected
                    ? "bg-white/25 text-white"
                    : "bg-[var(--pol-light-surface-subtle)] text-[var(--pol-light-text-secondary)]",
                ].join(" ")}
              >
                {count.toLocaleString("fa-IR")}
              </span>
            </button>
          );
        })}
      </div>

      {/* Tab Panels */}
      {tab === "orders" && <OrdersTab rows={orders} />}
      {tab === "support" && <SupportTab rows={support} />}
      {tab === "recon" && <ReconTab rows={recon} />}
      {tab === "rma" && <RmaTab rows={rmaOrders} />}
    </div>
  );
}

function OrdersTab({ rows }: { rows: OrderRow[] }) {
  const open = rows.filter((o) => OPEN_ORDER_STATUSES.has(o.order_status ?? ""));
  const list = open.length > 0 ? open : rows;

  if (list.length === 0) {
    return (
      <EmptyState
        title="هیچ سفارشی در صف انتظار نیست"
        description="سفارش‌های نیازمند اقدام در جریان توزیع اینجا قرار می‌گیرند."
      />
    );
  }

  return (
    <div className="grid gap-2.5">
      {list.map((o) => (
        <Card
          key={str(o.id)}
          className="p-3.5 transition-all duration-150 hover:border-[var(--pol-light-border-strong)]"
        >
          <div className="flex flex-col gap-2.5 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-wrap items-center gap-2">
              <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                {orderStatusLabel[o.order_status ?? ""] ?? "وضعیت نامشخص"}
              </StatusChip>
              {o.dispute_status && o.dispute_status !== "NONE" && (
                <StatusChip tone={disputeStatusTone[o.dispute_status] ?? "danger"}>
                  {disputeStatusLabel[o.dispute_status ?? ""] ?? "وضعیت نامشخص"}
                </StatusChip>
              )}
              <span className="font-mono text-[13px] font-bold text-[var(--pol-light-text-primary)]" dir="ltr">
                {o.order_number ?? str(o.id)}
              </span>
              <span className="rounded-md bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 px-2 py-0.5 text-[11px] font-bold text-amber-800 dark:text-amber-300">
                اقدام: {nextActionForOrder(o.order_status, o.dispute_status)}
              </span>
            </div>

            <div className="flex items-center justify-between gap-4 border-t border-[var(--pol-light-border-subtle)] pt-2 text-[12px] sm:border-0 sm:pt-0">
              <span className="text-[var(--pol-light-text-muted)]">
                {ageLabel(o.created_at)}
              </span>
              <span className="font-bold text-[var(--pol-light-text-primary)]">
                {formatToman(o.total_amount_toman)}
              </span>
              <Link
                href={`/ops/orders/${o.id}`}
                className="font-semibold text-[var(--pol-light-brand-primary)] hover:underline"
              >
                بررسی سفارش ←
              </Link>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}

function SupportTab({ rows }: { rows: SupportRow[] }) {
  if (rows.length === 0) {
    return (
      <div className="space-y-3">
        <EmptyState
          title="پرونده پشتیبانی بازی وجود ندارد"
          description="تیکت‌های جدید کاربران در این صف قرار می‌گیرند."
        />
        <div className="text-center">
          <Link
            href="/ops/support"
            className="text-[13px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
          >
            مشاهده کل میز پشتیبانی ←
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="grid gap-2.5">
        {rows.map((s) => (
          <Card
            key={str(s.id)}
            className="p-3.5 transition-all duration-150 hover:border-[var(--pol-light-border-strong)]"
          >
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-wrap items-center gap-2">
                <StatusChip tone={supportStatusTone[s.status ?? ""] ?? "neutral"}>
                  {supportStatusLabel[s.status ?? ""] ?? "وضعیت نامشخص"}
                </StatusChip>
                <StatusChip tone={supportPriorityTone[s.priority ?? ""] ?? "neutral"}>
                  {supportPriorityLabel[s.priority ?? ""] ?? s.priority ?? "—"}
                </StatusChip>
                <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
                  {s.case_type ?? "عمومی"}
                </span>
                <span className="font-semibold text-[13px] text-[var(--pol-light-text-primary)]">
                  {s.subject ?? "بدون موضوع"}
                </span>
              </div>

              <div className="flex items-center justify-between gap-4 text-[12px]">
                <span className="font-mono text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                  {s.case_number ?? str(s.id).slice(0, 8)}
                </span>
                <span className="text-[var(--pol-light-text-muted)]">
                  {ageLabel(s.created_at)}
                </span>
                <Link
                  href="/ops/support"
                  className="font-semibold text-[var(--pol-light-brand-primary)] hover:underline"
                >
                  پاسخگویی ←
                </Link>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="text-end">
        <Link
          href="/ops/support"
          className="text-[13px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
        >
          باز کردن میز کامل پشتیبانی ←
        </Link>
      </div>
    </div>
  );
}

function ReconTab({ rows }: { rows: ReconRow[] }) {
  if (rows.length === 0) {
    return (
      <div className="space-y-3">
        <EmptyState
          title="مورد مغایرت مالی ثبت نشده است"
          description="سیستم تطبیق تسویه‌ها به صورت مستمر بررسی مغایرت‌ها را انجام می‌دهد."
        />
        <div className="text-center">
          <Link
            href="/ops/reconciliation"
            className="text-[13px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
          >
            مشاهده کنسول تطبیق مالی ←
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="grid gap-2.5">
        {rows.map((r) => (
          <Card key={str(r.id)} className="p-3.5">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-wrap items-center gap-2.5">
                <StatusChip tone={reconStatusTone[r.status ?? ""] ?? "neutral"}>
                  {reconStatusLabel[r.status ?? ""] ?? "وضعیت نامشخص"}
                </StatusChip>
                <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
                  انتظار: <strong>{formatToman(r.expected_amount_toman)}</strong> · مشاهده:{" "}
                  <strong>{formatToman(r.observed_amount_toman)}</strong>
                </span>
              </div>

              <div className="flex items-center justify-between gap-4 text-[12px]">
                <span className="text-[var(--pol-light-text-muted)]">
                  {ageLabel(r.opened_at)}
                </span>
                <Link
                  href="/ops/reconciliation"
                  className="font-semibold text-[var(--pol-light-brand-primary)] hover:underline"
                >
                  رسیدگی به مغایرت ←
                </Link>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="text-end">
        <Link
          href="/ops/reconciliation"
          className="text-[13px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
        >
          باز کردن کنسول تطبیق مالی ←
        </Link>
      </div>
    </div>
  );
}

function RmaTab({ rows }: { rows: RmaOrderRow[] }) {
  if (rows.length === 0) {
    return (
      <div className="space-y-3">
        <EmptyState
          title="سفارشی با اختلاف یا مرجوعی باز وجود ندارد"
          description="اختلافات و درخواست‌های استرداد کالا به محض ثبت در این بخش لیست می‌شوند."
        />
        <div className="text-center">
          <Link
            href="/ops/rma"
            className="text-[13px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
          >
            مشاهده میز RMA ←
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="grid gap-2.5">
        {rows.map((o) => (
          <Card key={str(o.id)} className="p-3.5">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-wrap items-center gap-2">
                <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                  {orderStatusLabel[o.order_status ?? ""] ?? "وضعیت نامشخص"}
                </StatusChip>
                <StatusChip tone={disputeStatusTone[o.dispute_status ?? ""] ?? "neutral"}>
                  {disputeStatusLabel[o.dispute_status ?? ""] ?? o.dispute_status ?? "—"}
                </StatusChip>
                <span className="font-mono text-[13px] font-bold text-[var(--pol-light-text-primary)]" dir="ltr">
                  {o.order_number ?? str(o.id)}
                </span>
              </div>

              <div className="flex items-center justify-between gap-4 text-[12px]">
                <span className="text-[var(--pol-light-text-muted)]">
                  {formatDateTime(o.created_at)}
                </span>
                <Link
                  href="/ops/rma"
                  className="font-semibold text-[var(--pol-light-brand-primary)] hover:underline"
                >
                  رسیدگی به RMA ←
                </Link>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="text-end">
        <Link
          href="/ops/rma"
          className="text-[13px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
        >
          باز کردن میز RMA ←
        </Link>
      </div>
    </div>
  );
}
