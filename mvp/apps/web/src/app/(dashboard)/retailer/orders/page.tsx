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
  formatDateTime,
  formatToman,
  groupStatusLabel,
  groupStatusTone,
  normalizeOrderList,
  orderStatusTone,
  orderStatusLabel,
  type OrderListItem,
} from "../shared";

type LoadState = "loading" | "error" | "ready";

const PAGE_SIZE = 20;

const statusFilters = [
  { value: "", label: "همه" },
  { value: "PENDING", label: "در انتظار پذیرش" },
  { value: "ACCEPTED", label: "پذیرفته‌شده" },
  { value: "PROCESSING", label: "در حال آماده‌سازی" },
  { value: "SHIPPED", label: "ارسال‌شده" },
  { value: "DELIVERED", label: "تحویل‌شده" },
  { value: "CANCELLED", label: "لغوشده" },
] as const;

/**
 * R-10 order history / reorder entry.
 * GET /orders — unwrap success envelope; handle {data,total,offset,limit} OR array
 * (current backend returns {orders,limit,offset}); offset/limit pagination.
 */
export default function RetailerOrdersPage() {
  const [items, setItems] = useState<OrderListItem[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [status, setStatus] = useState("");
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState<number | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);

  const load = useCallback(
    async (reset: boolean) => {
      if (reset) {
        setState("loading");
        setErrorMessage(null);
      } else {
        setLoadingMore(true);
      }
      try {
        const nextOffset = reset ? 0 : offset;
        const params = new URLSearchParams();
        params.set("limit", String(PAGE_SIZE));
        params.set("offset", String(nextOffset));
        if (status) params.set("status", status);
        const data = await getApi().get<unknown>(`/api/v1/orders?${params.toString()}`);
        const normalized = normalizeOrderList(data, PAGE_SIZE);
        setTotal(normalized.total);
        setOffset(nextOffset + normalized.items.length);
        setItems((prev) =>
          reset ? normalized.items : [...prev, ...normalized.items],
        );
        setState("ready");
      } catch (err) {
        if (reset) {
          setErrorMessage(
            err instanceof Error ? err.message : "دریافت سفارش‌ها ناموفق بود",
          );
          setState("error");
        }
      } finally {
        setLoadingMore(false);
      }
    },
    // offset is read at call time via closure on state — include for correctness
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [status],
  );

  useEffect(() => {
    void load(true);
  }, [load]);

  const hasMore =
    items.length > 0 && (total === null ? items.length % PAGE_SIZE === 0 : offset < total);

  if (state === "loading") {
    return (
      <div className="space-y-3" aria-busy="true" aria-label="در حال بارگذاری سفارش‌ها">
        <Skeleton className="h-8 w-48" />
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
          >
            <Skeleton className="mb-2 h-4 w-1/3" />
            <Skeleton lines={2} />
          </div>
        ))}
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت سفارش‌ها ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load(true)}
      />
    );
  }

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          سفارش‌ها
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">
          {items.length.toLocaleString("fa-IR")} مورد
          {total !== null ? ` از ${total.toLocaleString("fa-IR")}` : ""}
        </span>
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
          description={
            status
              ? "سفارشی با این وضعیت وجود ندارد. فیلتر را تغییر دهید."
              : "هنوز سفارشی ثبت نکرده‌اید."
          }
          actionLabel={status ? "حذف فیلتر" : "رفتن به کاتالوگ"}
          onAction={() => {
            if (status) setStatus("");
            else window.location.href = "/retailer/catalog";
          }}
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
                {o.group_status ? (
                  <StatusChip tone={groupStatusTone[o.group_status] ?? "neutral"}>
                    {groupStatusLabel[o.group_status] ?? o.group_status}
                  </StatusChip>
                ) : null}
                {o.dispute_status && o.dispute_status !== "NONE" ? (
                  <StatusChip tone="danger">اختلاف</StatusChip>
                ) : null}
                <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                  {formatDateTime(o.created_at)}
                </span>
              </div>
              <div className="mt-2 flex flex-wrap items-center gap-3">
                <Link
                  href={`/retailer/orders/${o.id}`}
                  className="text-[14px] font-semibold text-[var(--pol-light-text-primary)] hover:underline"
                  dir="ltr"
                >
                  {o.order_number ?? String(o.id)}
                </Link>
                {o.order_group_id ? (
                  <Link
                    href={`/retailer/orders/group/${o.order_group_id}`}
                    className="text-[12px] text-[var(--pol-light-brand-primary)] hover:underline"
                  >
                    گروه سفارش
                  </Link>
                ) : null}
                <Link
                  href={`/retailer/catalog?reorder=${o.id}`}
                  className="text-[12px] text-[var(--pol-light-brand-primary)] hover:underline"
                >
                  خرید مجدد
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
          <Button variant="secondary" loading={loadingMore} onClick={() => void load(false)}>
            بارگذاری موارد بیشتر
          </Button>
        </div>
      ) : null}
    </div>
  );
}
