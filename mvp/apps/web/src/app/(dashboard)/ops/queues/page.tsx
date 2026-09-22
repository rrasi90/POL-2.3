"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Button, EmptyState, ErrorState, Skeleton, StatusChip, type StatusTone } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  ageLabel,
  ageTone,
  cardCls,
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
  { id: "orders", label: "سفارش‌ها" },
  { id: "support", label: "پشتیبانی" },
  { id: "recon", label: "تطبیق مالی" },
  { id: "rma", label: "مرجوعی / RMA" },
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
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری صف‌ها">
        <Skeleton className="h-8 w-48" />
        <div className={cardCls}>
          <Skeleton lines={6} />
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
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          صفوف یکپارچه
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">O-02</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      <div role="tablist" aria-label="نوع صف" className="flex flex-wrap gap-2">
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            type="button"
            aria-selected={tab === t.id}
            onClick={() => setTab(t.id)}
            className={[
              "rounded-[8px] px-3 py-1.5 text-[13px] transition-colors duration-[160ms]",
              tab === t.id
                ? "bg-[var(--pol-light-surface-subtle)] font-semibold text-[var(--pol-light-text-primary)]"
                : "text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)]",
            ].join(" ")}
          >
            {t.label}
            <span className="ms-1.5 text-[11px] text-[var(--pol-light-text-muted)]">
              {counts[t.id].toLocaleString("fa-IR")}
            </span>
          </button>
        ))}
      </div>

      {tab === "orders" ? <OrdersTab rows={orders} /> : null}
      {tab === "support" ? <SupportTab rows={support} /> : null}
      {tab === "recon" ? <ReconTab rows={recon} /> : null}
      {tab === "rma" ? <RmaTab rows={rmaOrders} /> : null}
    </div>
  );
}

function OrdersTab({ rows }: { rows: OrderRow[] }) {
  const open = rows.filter((o) => OPEN_ORDER_STATUSES.has(o.order_status ?? ""));
  const list = open.length > 0 ? open : rows;
  if (list.length === 0) {
    return (
      <EmptyState
        title="سفارشی در صف نیست"
        description="هنگامی که سفارش ثبت شود، اینجا نمایش داده می‌شود."
      />
    );
  }
  return (
    <ul role="list" className="space-y-2">
      {list.map((o) => (
        <li key={str(o.id)} className={cardCls}>
          <div className="flex flex-wrap items-center gap-2">
            <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
              {orderStatusLabel[o.order_status ?? ""] ?? o.order_status ?? "—"}
            </StatusChip>
            <StatusChip tone={disputeStatusTone[o.dispute_status ?? ""] ?? "neutral"}>
              {disputeStatusLabel[o.dispute_status ?? ""] ?? o.dispute_status ?? "—"}
            </StatusChip>
            <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
              {ageLabel(o.created_at)}
            </span>
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-3">
            <span className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]" dir="ltr">
              {o.order_number ?? str(o.id)}
            </span>
            <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
              اقدام: {nextActionForOrder(o.order_status, o.dispute_status)}
            </span>
            <span className="ms-auto text-[13px] text-[var(--pol-light-text-primary)]">
              {formatToman(o.total_amount_toman)}
            </span>
          </div>
        </li>
      ))}
    </ul>
  );
}

function SupportTab({ rows }: { rows: SupportRow[] }) {
  if (rows.length === 0) {
    return (
      <div className="space-y-3">
        <EmptyState title="پرونده پشتیبانی نیست" description="پرونده‌های باز اینجا فهرست می‌شوند." />
        <Link
          href="/ops/support"
          className="inline-block text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
        >
          رفتن به میز پشتیبانی
        </Link>
      </div>
    );
  }
  return (
    <div className="space-y-3">
      <ul role="list" className="space-y-2">
        {rows.map((s) => (
          <li key={str(s.id)} className={cardCls}>
            <div className="flex flex-wrap items-center gap-2">
              <StatusChip tone={supportStatusTone[s.status ?? ""] ?? "neutral"}>
                {supportStatusLabel[s.status ?? ""] ?? s.status ?? "—"}
              </StatusChip>
              <StatusChip tone={supportPriorityTone[s.priority ?? ""] ?? "neutral"}>
                {supportPriorityLabel[s.priority ?? ""] ?? s.priority ?? "—"}
              </StatusChip>
              <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
                {s.case_type ?? "—"}
              </span>
              <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                {ageLabel(s.created_at)}
              </span>
            </div>
            <p className="mt-2 text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
              {s.subject ?? "بدون موضوع"}
            </p>
            <p className="text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
              {s.case_number ?? str(s.id)}
            </p>
          </li>
        ))}
      </ul>
      <Link
        href="/ops/support"
        className="inline-block text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
      >
        باز کردن میز پشتیبانی
      </Link>
    </div>
  );
}

function ReconTab({ rows }: { rows: ReconRow[] }) {
  if (rows.length === 0) {
    return (
      <div className="space-y-3">
        <EmptyState
          title="مورد تطبیقی نیست"
          description="مغایرت‌های مالی پس از ثبت، اینجا فهرست می‌شوند."
        />
        <Link
          href="/ops/reconciliation"
          className="inline-block text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
        >
          رفتن به تطبیق مالی
        </Link>
      </div>
    );
  }
  return (
    <div className="space-y-3">
      <ul role="list" className="space-y-2">
        {rows.map((r) => (
          <li key={str(r.id)} className={cardCls}>
            <div className="flex flex-wrap items-center gap-2">
              <StatusChip tone={reconStatusTone[r.status ?? ""] ?? "neutral"}>
                {reconStatusLabel[r.status ?? ""] ?? r.status ?? "—"}
              </StatusChip>
              <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
                انتظار: {formatToman(r.expected_amount_toman)} · مشاهده:{" "}
                {formatToman(r.observed_amount_toman)}
              </span>
              <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                {ageLabel(r.opened_at)}
              </span>
            </div>
          </li>
        ))}
      </ul>
      <Link
        href="/ops/reconciliation"
        className="inline-block text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
      >
        باز کردن تطبیق مالی
      </Link>
    </div>
  );
}

function RmaTab({ rows }: { rows: RmaOrderRow[] }) {
  if (rows.length === 0) {
    return (
      <div className="space-y-3">
        <EmptyState
          title="سفارشی با اختلاف یا وضعیت باز نیست"
          description="لیست سراسری مرجوعی‌ها موجود نیست (G-013) — از طریق سفارش وارد شوید."
        />
        <Link
          href="/ops/rma"
          className="inline-block text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
        >
          رفتن به میز RMA
        </Link>
      </div>
    );
  }
  return (
    <div className="space-y-3">
      <p className="text-[12px] text-[var(--pol-light-text-secondary)]">
        شکاف G-013: بدون لیست سراسری مرجوعی — ردیف‌ها از سفارش‌های دارای اختلاف/وضعیت باز استخراج
        شده‌اند.
      </p>
      <ul role="list" className="space-y-2">
        {rows.map((o) => (
          <li key={str(o.id)} className={cardCls}>
            <div className="flex flex-wrap items-center gap-2">
              <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                {orderStatusLabel[o.order_status ?? ""] ?? o.order_status ?? "—"}
              </StatusChip>
              <StatusChip tone={disputeStatusTone[o.dispute_status ?? ""] ?? "neutral"}>
                {disputeStatusLabel[o.dispute_status ?? ""] ?? o.dispute_status ?? "—"}
              </StatusChip>
              <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                {formatDateTime(o.created_at)}
              </span>
            </div>
            <span className="mt-2 block text-[14px] font-semibold" dir="ltr">
              {o.order_number ?? str(o.id)}
            </span>
          </li>
        ))}
      </ul>
      <Link
        href="/ops/rma"
        className="inline-block text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
      >
        باز کردن میز RMA
      </Link>
    </div>
  );
}
