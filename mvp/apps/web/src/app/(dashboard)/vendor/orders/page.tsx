"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  Button,
  EmptyState,
  ErrorState,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  ageLabel,
  ageTone,
  cardCls,
  formatDateTime,
  formatToman,
  itemsOf,
  orderStatusLabel,
  orderStatusTone,
  type LoadState,
} from "../_shared";

interface OrderRow {
  id: string;
  order_number?: string | null;
  order_status?: string | null;
  dispute_status?: string | null;
  total_amount_toman?: number | string | null;
  created_at?: string | null;
  retailer_id?: string | null;
}

const PAGE_SIZE = 20;

const statusFilters = [
  { value: "", label: "همه" },
  { value: "SUBMITTED", label: "در انتظار پذیرش" },
  { value: "CREATED", label: "ایجادشده" },
  { value: "ACCEPTED", label: "پذیرفته‌شده" },
  { value: "PARTIALLY_ACCEPTED", label: "پذیرش جزئی" },
  { value: "PREPARING", label: "آماده‌سازی" },
  { value: "READY", label: "آماده ارسال" },
  { value: "DISPATCHED", label: "ارسال‌شده" },
  { value: "DELIVERED", label: "تحویل‌شده" },
  { value: "REJECTED", label: "ردشده" },
] as const;

/**
 * V-02 vendor orders queue.
 * GET /orders with status filter + offset pagination.
 */
export default function VendorOrdersPage() {
  const searchParams = useSearchParams();
  const initialStatus = searchParams.get("status") ?? "";

  const [items, setItems] = useState<OrderRow[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [status, setStatus] = useState(initialStatus);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState<number | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);

  const load = useCallback(
    async (reset: boolean, nextStatus: string) => {
      if (reset) {
        setState("loading");
        setErrorMessage(null);
      } else {
        setLoadingMore(true);
      }
      try {
        const params = new URLSearchParams();
        params.set("limit", String(PAGE_SIZE));
        params.set("offset", String(reset ? 0 : offset));
        if (nextStatus) params.set("status", nextStatus);
        const data = await getApi().get<unknown>(`/api/v1/orders?${params.toString()}`);
        const rows = itemsOf<OrderRow>(data, "orders");
        const obj = (data && typeof data === "object" ? data : {}) as Record<string, unknown>;
        const t = typeof obj.total === "number" ? obj.total : null;
        setTotal(t);
        setOffset((reset ? 0 : offset) + rows.length);
        setItems((prev) => (reset ? rows : [...prev, ...rows]));
        setState("ready");
      } catch (err) {
        if (reset) {
          setErrorMessage(err instanceof Error ? err.message : "دریافت سفارش‌ها ناموفق بود");
          setState("error");
        }
      } finally {
        setLoadingMore(false);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [status],
  );

  useEffect(() => {
    void load(true, status);
  }, [status]); // eslint-disable-line react-hooks/exhaustive-deps

  const hasMore =
    items.length > 0 && (total === null ? items.length % PAGE_SIZE === 0 : offset < total);

  if (state === "loading") {
    return (
      <div className="space-y-3" aria-busy="true" aria-label="در حال بارگذاری صف سفارش‌ها">
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
        title="دریافت سفارش‌ها ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load(true, status)}
      />
    );
  }

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          صف سفارش‌ها
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">
          V-02 · {items.length.toLocaleString("fa-IR")} مورد
          {total !== null ? ` از ${total.toLocaleString("fa-IR")}` : ""}
        </span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load(true, status)}>
          به‌روزرسانی
        </Button>
      </header>

      <div className="flex flex-wrap gap-2" role="group" aria-label="فیلتر وضعیت">
        {statusFilters.map((f) => (
          <button
            key={f.value}
            type="button"
            aria-pressed={status === f.value}
            onClick={() => setStatus(f.value)}
            className={[
              "rounded-full border px-3 py-1 text-[12px] transition-colors duration-[160ms]",
              status === f.value
                ? "border-transparent bg-[var(--pol-light-brand-primary)] text-white"
                : "border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)]",
            ].join(" ")}
          >
            {f.label}
          </button>
        ))}
      </div>

      {items.length === 0 ? (
        <EmptyState
          title="سفارشی یافت نشد"
          description={status ? "سفارشی با این وضعیت وجود ندارد." : "صف سفارش خالی است."}
          actionLabel={status ? "حذف فیلتر" : undefined}
          onAction={status ? () => setStatus("") : undefined}
        />
      ) : (
        <ul role="list" className="space-y-2">
          {items.map((o) => (
            <li
              key={String(o.id)}
              className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4 transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]"
            >
              <div className="flex flex-wrap items-center gap-2">
                <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                  {orderStatusLabel[o.order_status ?? ""] ?? o.order_status ?? "—"}
                </StatusChip>
                {o.dispute_status && o.dispute_status !== "NONE" ? (
                  <StatusChip tone="danger">اختلاف</StatusChip>
                ) : null}
                <StatusChip tone={ageTone(o.created_at, 4, 12)}>{ageLabel(o.created_at)}</StatusChip>
                <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                  {formatDateTime(o.created_at)}
                </span>
              </div>
              <div className="mt-2 flex flex-wrap items-center gap-3">
                <Link
                  href={`/vendor/orders/${o.id}`}
                  className="text-[14px] font-semibold text-[var(--pol-light-text-primary)] hover:underline"
                  dir="ltr"
                >
                  {o.order_number ?? String(o.id)}
                </Link>
                <span className="ms-auto text-[14px] font-medium text-[var(--pol-light-text-primary)]">
                  {formatToman(o.total_amount_toman)}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}

      {hasMore ? (
        <div className="flex justify-center pt-2">
          <Button variant="secondary" loading={loadingMore} onClick={() => void load(false, status)}>
            بارگذاری موارد بیشتر
          </Button>
        </div>
      ) : null}
    </div>
  );
}
