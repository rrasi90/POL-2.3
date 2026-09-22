"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Button, EmptyState, ErrorState, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { useBasketStore } from "@/lib/basket";
import {
  formatDateTime,
  formatToman,
  groupStatusTone,
  groupStatusLabel,
  isOpenOrderStatus,
  normalizeOrderList,
  orderStatusTone,
  orderStatusLabel,
  type OrderListItem,
} from "./shared";

type LoadState = "loading" | "error" | "ready";

const PAGE_LIMIT = 20;

export default function RetailerHomePage() {
  const lines = useBasketStore((s) => s.lines);
  const [orders, setOrders] = useState<OrderListItem[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const data = await getApi().get<unknown>(
        `/api/v1/orders?limit=${PAGE_LIMIT}&offset=0`,
      );
      setOrders(normalizeOrderList(data, PAGE_LIMIT).items);
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت سفارش‌ها ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const openOrders = orders.filter((o) => isOpenOrderStatus(o.order_status));
  const actionsNeeded = openOrders.filter((o) => o.order_status === "PENDING");

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری خانه">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-3 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
            >
              <Skeleton lines={2} />
            </div>
          ))}
        </div>
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <Skeleton lines={4} />
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت اطلاعات خانه ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          بازار خرده‌فروشی
        </h1>
        <span className="text-[12px] leading-[18px] text-[var(--pol-light-text-muted)]">
          {orders.length.toLocaleString("fa-IR")} سفارش اخیر
        </span>
      </header>

      <section aria-label="دسترسی سریع" className="grid gap-3 sm:grid-cols-3">
        <Link
          href="/retailer/catalog"
          className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4 transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]"
        >
          <p className="text-[14px] leading-[22px] font-semibold text-[var(--pol-light-text-primary)]">
            جستجوی کالا
          </p>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
            جستجو در کاتالوگ و دسته‌بندی‌ها
          </p>
        </Link>
        <Link
          href="/retailer/catalog?tab=categories"
          className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4 transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]"
        >
          <p className="text-[14px] leading-[22px] font-semibold text-[var(--pol-light-text-primary)]">
            دسته‌بندی‌ها
          </p>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
            مرور گروه کالایی
          </p>
        </Link>
        <Link
          href="/retailer/basket"
          className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4 transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]"
        >
          <p className="text-[14px] leading-[22px] font-semibold text-[var(--pol-light-text-primary)]">
            سبد خرید
          </p>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
            {lines.length > 0
              ? `${lines.length.toLocaleString("fa-IR")} قلم در سبد`
              : "سبد خالی است"}
          </p>
        </Link>
      </section>

      <section aria-label="اقدامات لازم">
        <div className="flex items-center gap-2">
          <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
            اقدامات لازم
          </h2>
          {actionsNeeded.length > 0 ? (
            <StatusChip tone="warning">
              {actionsNeeded.length.toLocaleString("fa-IR")} مورد
            </StatusChip>
          ) : null}
        </div>
        {actionsNeeded.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="اقدام فوری لازم نیست"
              description="سفارشی در انتظار پذیرش تأمین‌کننده نیست."
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {actionsNeeded.map((o) => (
              <li key={String(o.id)}>
                <Link
                  href={`/retailer/orders/${o.id}`}
                  className="flex flex-wrap items-center gap-2 rounded-[12px] border border-[var(--pol-light-warning, var(--pol-light-border-strong))] bg-[var(--pol-light-surface-default)] p-4 transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]"
                >
                  <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                    {orderStatusLabel[o.order_status ?? ""] ?? o.order_status ?? "—"}
                  </StatusChip>
                  <span className="text-[13px] text-[var(--pol-light-text-secondary)]" dir="ltr">
                    {o.order_number ?? String(o.id).slice(0, 8)}
                  </span>
                  <span className="ms-auto text-[13px] font-medium text-[var(--pol-light-text-primary)]">
                    {formatToman(o.total_amount_toman)}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="سفارش‌های باز">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
            سفارش‌های باز
          </h2>
          <Link
            href="/retailer/orders"
            className="ms-auto text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
          >
            همه سفارش‌ها
          </Link>
        </div>
        {openOrders.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="سفارش بازی نیست"
              description="برای شروع خرید از کاتالوگ، کالا انتخاب کنید."
              actionLabel="رفتن به کاتالوگ"
              onAction={() => {
                window.location.href = "/retailer/catalog";
              }}
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {openOrders.map((o) => (
              <li
                key={String(o.id)}
                className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                    {orderStatusLabel[o.order_status ?? ""] ?? o.order_status ?? "—"}
                  </StatusChip>
                  {o.group_status ? (
                    <StatusChip tone={groupStatusTone[o.group_status] ?? "neutral"}>
                      گروه: {groupStatusLabel[o.group_status] ?? o.group_status}
                    </StatusChip>
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
                      نمایش گروه سفارش
                    </Link>
                  ) : null}
                  <span className="ms-auto text-[14px] font-medium text-[var(--pol-light-text-primary)]">
                    {formatToman(o.total_amount_toman)}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <div className="flex justify-start border-t border-[var(--pol-light-border-subtle)] pt-4">
        <Button variant="secondary" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </div>
    </div>
  );
}
