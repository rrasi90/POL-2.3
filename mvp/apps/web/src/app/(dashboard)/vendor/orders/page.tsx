"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
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
  ageLabel,
  ageTone,
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
  { value: "", label: "همه سفارش‌ها" },
  { value: "SUBMITTED", label: "در انتظار پذیرش" },
  { value: "CREATED", label: "ایجادشده" },
  { value: "ACCEPTED", label: "پذیرفته‌شده" },
  { value: "PARTIALLY_ACCEPTED", label: "پذیرش جزئی" },
  { value: "PREPARING", label: "در حال آماده‌سازی" },
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
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری صف سفارش‌ها">
        <Skeleton className="h-9 w-52" />
        <div className="flex gap-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-8 w-24 rounded-full" />
          ))}
        </div>
        <div className="grid gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Card key={i} className="p-5">
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
        title="دریافت سفارش‌ها ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load(true, status)}
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
              صف مدیریت سفارش‌ها
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              V-02
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            نمایش {items.length.toLocaleString("fa-IR")} سفارش
            {total !== null ? ` از مجموع ${total.toLocaleString("fa-IR")} سفارش` : ""}
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={() => void load(true, status)}>
          به‌روزرسانی صف
        </Button>
      </header>

      {/* Filter Tabs */}
      <div
        className="no-scrollbar -mx-4 flex gap-2 overflow-x-auto px-4 pb-1 sm:mx-0 sm:flex-wrap sm:px-0"
        role="group"
        aria-label="فیلتر وضعیت سفارش‌ها"
      >
        {statusFilters.map((f) => {
          const isActive = status === f.value;
          return (
            <button
              key={f.value}
              type="button"
              aria-pressed={isActive}
              onClick={() => setStatus(f.value)}
              className={[
                "shrink-0 rounded-full px-4 py-1.5 text-[13px] font-medium transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]",
                isActive
                  ? "bg-[var(--pol-light-brand-primary)] text-white shadow-sm"
                  : "border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)] hover:text-[var(--pol-light-text-primary)]",
              ].join(" ")}
            >
              {f.label}
            </button>
          );
        })}
      </div>

      {/* Orders List */}
      {items.length === 0 ? (
        <EmptyState
          title="سفارشی با این مشخصات یافت نشد"
          description={status ? "سفارشی با وضعیت انتخاب‌شده در سیستم وجود ندارد." : "صف سفارش‌های فروشگاه شما خالی است."}
          actionLabel={status ? "نمایش همه سفارش‌ها" : undefined}
          onAction={status ? () => setStatus("") : undefined}
        />
      ) : (
        <div className="grid gap-3">
          {items.map((o) => (
            <Link
              key={String(o.id)}
              href={`/vendor/orders/${o.id}`}
              className="group block rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
            >
              <Card className="p-4 transition-all duration-200 group-hover:shadow-[var(--pol-shadow-md)] group-hover:border-[var(--pol-light-border-strong)]">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                      {orderStatusLabel[o.order_status ?? ""] ?? "وضعیت نامشخص"}
                    </StatusChip>
                    {o.dispute_status && o.dispute_status !== "NONE" && (
                      <StatusChip tone="danger">اختلاف ثبت‌شده</StatusChip>
                    )}
                    <StatusChip tone={ageTone(o.created_at, 4, 12)}>
                      {ageLabel(o.created_at)}
                    </StatusChip>
                    <span className="font-mono text-[14px] font-bold text-[var(--pol-light-text-primary)]" dir="ltr">
                      {o.order_number ?? String(o.id)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between border-t border-[var(--pol-light-border-subtle)] pt-3 sm:border-0 sm:pt-0 sm:gap-6">
                    <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                      {formatDateTime(o.created_at)}
                    </span>
                    <span className="text-[16px] font-bold text-[var(--pol-light-text-primary)]">
                      {formatToman(o.total_amount_toman)}
                    </span>
                    <span className="hidden text-[13px] font-semibold text-[var(--pol-light-brand-primary)] group-hover:underline sm:inline-block">
                      مدیریت سفارش ←
                    </span>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination Load More */}
      {hasMore && (
        <div className="flex justify-center pt-2">
          <Button
            variant="secondary"
            loading={loadingMore}
            onClick={() => void load(false, status)}
          >
            بارگذاری ۲۰ سفارش دیگر
          </Button>
        </div>
      )}
    </div>
  );
}
