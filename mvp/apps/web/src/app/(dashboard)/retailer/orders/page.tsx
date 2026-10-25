"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
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
  const router = useRouter();
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
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری سفارش‌ها">
        <Skeleton className="h-8 w-48" />
        {Array.from({ length: 5 }).map((_, i) => (
          <Card key={i} className="p-5">
            <Skeleton className="mb-2 h-4 w-1/3" />
            <Skeleton lines={2} />
          </Card>
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
    <div className="space-y-6 pb-10">
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-[var(--pol-light-border-subtle)] pb-5">
        <div>
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            تاریخچه سفارش‌ها
          </h1>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            پیگیری وضعیت سفارش‌ها، تسویه و خرید مجدد اقلام مورد نیاز
          </p>
        </div>
        <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-3 py-1 text-[12px] font-medium text-[var(--pol-light-text-secondary)] border border-[var(--pol-light-border-subtle)]">
          {items.length.toLocaleString("fa-IR")} سفارش
          {total !== null ? ` از ${total.toLocaleString("fa-IR")}` : ""}
        </span>
      </header>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2" role="group" aria-label="فیلتر وضعیت سفارش">
        {statusFilters.map((f) => (
          <button
            key={f.value}
            type="button"
            aria-pressed={status === f.value}
            onClick={() => setStatus(f.value)}
            className={[
              "rounded-full border px-3.5 py-1.5 text-[12px] font-medium transition-all duration-[160ms]",
              status === f.value
                ? "border-transparent bg-[var(--pol-light-brand-primary)] text-white shadow-2xs"
                : "border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)] hover:text-[var(--pol-light-text-primary)]",
            ].join(" ")}
          >
            {f.label}
          </button>
        ))}
      </div>

      {items.length === 0 ? (
        <Card variant="subtle" className="p-8">
          <EmptyState
            title="سفارشی با این مشخصات یافت نشد"
            description={
              status
                ? "هیچ سفارشی مطابق با فیلتر وضعیت انتخاب‌شده وجود ندارد. می‌توانید فیلتر را حذف کنید."
                : "هنوز سفارشی در پُل ثبت نکرده‌اید. برای شروع، اقلام مورد نیاز خود را از کاتالوگ انتخاب نمایید."
            }
            actionLabel={status ? "نمایش همه سفارش‌ها" : "مشاهده کاتالوگ کالاها"}
            onAction={() => {
              if (status) setStatus("");
              else router.push("/retailer/catalog");
            }}
          />
        </Card>
      ) : (
        <div className="space-y-3">
          {items.map((o) => (
            <Card
              key={String(o.id)}
              variant="interactive"
              className="p-4 sm:p-5 transition-all duration-[160ms] hover:border-[var(--pol-light-brand-primary)]/40 hover:shadow-card"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--pol-light-border-subtle)] pb-3">
                <div className="flex items-center gap-2">
                  <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                    {orderStatusLabel[o.order_status ?? ""] ?? "وضعیت نامشخص"}
                  </StatusChip>
                  {o.group_status ? (
                    <StatusChip tone={groupStatusTone[o.group_status] ?? "neutral"}>
                      گروه: {groupStatusLabel[o.group_status ?? ""] ?? "وضعیت نامشخص"}
                    </StatusChip>
                  ) : null}
                  {o.dispute_status && o.dispute_status !== "NONE" ? (
                    <StatusChip tone="danger">دارای اختلاف</StatusChip>
                  ) : null}
                </div>
                <span className="text-[12px] font-medium text-[var(--pol-light-text-muted)]">
                  {formatDateTime(o.created_at)}
                </span>
              </div>

              <div className="mt-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-3">
                    <span className="text-[12px] text-[var(--pol-light-text-muted)]">شماره سفارش:</span>
                    <Link
                      href={`/retailer/orders/${o.id}`}
                      className="font-mono text-[15px] font-bold text-[var(--pol-light-text-primary)] hover:text-[var(--pol-light-brand-primary)] hover:underline"
                      dir="ltr"
                    >
                      {o.order_number ?? String(o.id)}
                    </Link>
                  </div>
                  {o.order_group_id ? (
                    <div className="mt-1 flex items-center gap-2">
                      <span className="text-[11px] text-[var(--pol-light-text-muted)]">شناسه گروه:</span>
                      <Link
                        href={`/retailer/orders/group/${o.order_group_id}`}
                        className="font-mono text-[11px] text-[var(--pol-light-brand-primary)] hover:underline"
                        dir="ltr"
                      >
                        {o.order_group_id.slice(0, 12)}…
                      </Link>
                    </div>
                  ) : null}
                </div>

                <div className="flex items-center gap-4 self-end sm:self-center">
                  <div className="text-end">
                    <span className="text-[11px] text-[var(--pol-light-text-muted)] block">مبلغ سفارش:</span>
                    <span className="text-[16px] font-bold text-[var(--pol-light-text-primary)]">
                      {formatToman(o.total_amount_toman)}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-[var(--pol-light-border-subtle)] flex items-center justify-between">
                <Link
                  href={`/retailer/catalog?reorder=${o.id}`}
                  className="inline-flex items-center gap-1.5 text-[12px] font-medium text-[var(--pol-light-text-secondary)] hover:text-[var(--pol-light-brand-primary)]"
                >
                  <svg className="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>خرید مجدد این سفارش</span>
                </Link>

                <Link
                  href={`/retailer/orders/${o.id}`}
                  className="inline-flex items-center gap-1 text-[13px] font-bold text-[var(--pol-light-brand-primary)] hover:underline"
                >
                  <span>مشاهده جزئیات و رهگیری</span>
                  <span>←</span>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}

      {hasMore ? (
        <div className="flex justify-center pt-4">
          <Button variant="secondary" loading={loadingMore} onClick={() => void load(false)}>
            بارگذاری سفارش‌های بیشتر
          </Button>
        </div>
      ) : null}
    </div>
  );
}
