"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  EmptyState,
  ErrorState,
  Skeleton,
  StatusChip,
} from "@pol/ui";
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
  const router = useRouter();
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
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری خانه">
        <div className="space-y-2">
          <Skeleton className="h-8 w-56" />
          <Skeleton className="h-4 w-72" />
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="p-5">
              <Skeleton className="size-10 rounded-lg mb-3" />
              <Skeleton className="h-5 w-28 mb-2" />
              <Skeleton lines={2} />
            </Card>
          ))}
        </div>
        <Card className="p-5">
          <Skeleton className="h-6 w-36 mb-4" />
          <Skeleton lines={4} />
        </Card>
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
    <div className="space-y-8 pb-10">
      {/* Header Banner */}
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-[var(--pol-light-border-subtle)] pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
              بازار خرده‌فروشی پُل
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[12px] font-medium text-[var(--pol-light-text-secondary)] border border-[var(--pol-light-border-subtle)]">
              {orders.length.toLocaleString("fa-IR")} سفارش اخیر
            </span>
          </div>
          <p className="mt-1 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
            جستجو و خرید تجمیعی کالاها، رهگیری ارسال و مدیریت سفارش‌های فعال
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={() => void load()}>
            <svg
              className="size-4 me-1.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            به‌روزرسانی
          </Button>
        </div>
      </header>

      {/* Quick Action Discovery Cards */}
      <section aria-label="دسترسی سریع" className="grid gap-4 sm:grid-cols-3">
        <Link href="/retailer/catalog" className="group">
          <Card
            variant="interactive"
            className="h-full p-5 transition-all duration-[180ms] group-hover:border-[var(--pol-light-brand-primary)]"
          >
            <div className="flex items-start justify-between">
              <div className="flex size-11 items-center justify-center rounded-[10px] bg-[var(--pol-light-brand-primary)]/10 text-[var(--pol-light-brand-primary)]">
                <svg
                  className="size-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
              <svg
                className="size-4 text-[var(--pol-light-text-muted)] transition-transform duration-[160ms] group-hover:-translate-x-1 group-hover:text-[var(--pol-light-brand-primary)]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </div>
            <h3 className="mt-4 text-[15px] font-bold text-[var(--pol-light-text-primary)]">
              جستجوی کالا
            </h3>
            <p className="mt-1 text-[12px] leading-[18px] text-[var(--pol-light-text-secondary)]">
              جستجو در کاتالوگ جامع، بررسی مقایسه قیمت و تأمین‌کنندگان
            </p>
          </Card>
        </Link>

        <Link href="/retailer/catalog?tab=categories" className="group">
          <Card
            variant="interactive"
            className="h-full p-5 transition-all duration-[180ms] group-hover:border-[var(--pol-light-brand-primary)]"
          >
            <div className="flex items-start justify-between">
              <div className="flex size-11 items-center justify-center rounded-[10px] bg-amber-500/10 text-amber-600 dark:text-amber-400">
                <svg
                  className="size-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
                  />
                </svg>
              </div>
              <svg
                className="size-4 text-[var(--pol-light-text-muted)] transition-transform duration-[160ms] group-hover:-translate-x-1 group-hover:text-[var(--pol-light-brand-primary)]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </div>
            <h3 className="mt-4 text-[15px] font-bold text-[var(--pol-light-text-primary)]">
              دسته‌بندی‌های کالا
            </h3>
            <p className="mt-1 text-[12px] leading-[18px] text-[var(--pol-light-text-secondary)]">
              مرور سلسله‌مراتبی گروه‌های کالایی و اقلام ضروری FMCG
            </p>
          </Card>
        </Link>

        <Link href="/retailer/basket" className="group">
          <Card
            variant="interactive"
            className="h-full p-5 transition-all duration-[180ms] group-hover:border-[var(--pol-light-brand-primary)]"
          >
            <div className="flex items-start justify-between">
              <div className="flex size-11 items-center justify-center rounded-[10px] bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                <svg
                  className="size-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
                  />
                </svg>
              </div>
              {lines.length > 0 ? (
                <span className="rounded-full bg-emerald-600 px-2 py-0.5 text-[11px] font-bold text-white">
                  {lines.length.toLocaleString("fa-IR")} قلم
                </span>
              ) : (
                <svg
                  className="size-4 text-[var(--pol-light-text-muted)] transition-transform duration-[160ms] group-hover:-translate-x-1 group-hover:text-[var(--pol-light-brand-primary)]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              )}
            </div>
            <h3 className="mt-4 text-[15px] font-bold text-[var(--pol-light-text-primary)]">
              سبد خرید یکپارچه
            </h3>
            <p className="mt-1 text-[12px] leading-[18px] text-[var(--pol-light-text-secondary)]">
              {lines.length > 0
                ? `${lines.length.toLocaleString("fa-IR")} قلم آماده بررسی و تخصیص هوشمند`
                : "سبد خرید در حال حاضر خالی است"}
            </p>
          </Card>
        </Link>
      </section>

      {/* Pending Actions */}
      <section aria-label="اقدامات لازم" className="space-y-3">
        <div className="flex items-center gap-2">
          <div className="size-2 rounded-full bg-[var(--pol-light-warning)]" />
          <h2 className="text-[16px] leading-[24px] font-bold text-[var(--pol-light-text-primary)]">
            اقدامات لازم
          </h2>
          {actionsNeeded.length > 0 ? (
            <StatusChip tone="warning">
              {actionsNeeded.length.toLocaleString("fa-IR")} مورد نیازمند پیگیری
            </StatusChip>
          ) : null}
        </div>

        {actionsNeeded.length === 0 ? (
          <Card variant="subtle" className="p-4">
            <EmptyState
              title="اقدام فوری لازم نیست"
              description="تمام سفارش‌های شما در مسیر پردازش یا تحویل قرار دارند و نیازی به تأیید فوری نیست."
            />
          </Card>
        ) : (
          <div className="space-y-2">
            {actionsNeeded.map((o) => (
              <Link key={String(o.id)} href={`/retailer/orders/${o.id}`} className="block group">
                <Card
                  variant="interactive"
                  className="flex flex-wrap items-center justify-between gap-3 border-[var(--pol-light-warning)]/40 bg-[var(--pol-light-warning)]/5 p-4 transition-all duration-[160ms] hover:border-[var(--pol-light-warning)]"
                >
                  <div className="flex items-center gap-3">
                    <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "warning"}>
                      {orderStatusLabel[o.order_status ?? ""] ?? o.order_status ?? "—"}
                    </StatusChip>
                    <div>
                      <span className="font-mono text-[13px] font-medium text-[var(--pol-light-text-primary)]" dir="ltr">
                        {o.order_number ?? String(o.id).slice(0, 8)}
                      </span>
                      <p className="text-[11px] text-[var(--pol-light-text-muted)]">
                        در انتظار تأیید یا اقدام توسط شما
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <span className="font-bold text-[14px] text-[var(--pol-light-text-primary)]">
                      {formatToman(o.total_amount_toman)}
                    </span>
                    <span className="text-[12px] font-medium text-[var(--pol-light-brand-primary)] group-hover:underline">
                      مشاهده و اقدام ←
                    </span>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Open Orders */}
      <section aria-label="سفارش‌های باز" className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <div className="size-2 rounded-full bg-[var(--pol-light-brand-primary)]" />
            <h2 className="text-[16px] leading-[24px] font-bold text-[var(--pol-light-text-primary)]">
              سفارش‌های باز
            </h2>
            <span className="text-[12px] text-[var(--pol-light-text-muted)]">
              ({openOrders.length.toLocaleString("fa-IR")} سفارش در جریان)
            </span>
          </div>
          <Link
            href="/retailer/orders"
            className="text-[13px] font-semibold text-[var(--pol-light-brand-primary)] hover:underline"
          >
            مشاهده همه سفارش‌ها ←
          </Link>
        </div>

        {openOrders.length === 0 ? (
          <Card variant="subtle" className="p-4">
            <EmptyState
              title="سفارش بازی نیست"
              description="برای شروع سفارش‌گذاری جدید، کالاهای مورد نیاز را از کاتالوگ انتخاب کنید."
              actionLabel="رفتن به کاتالوگ"
              onAction={() => {
                router.push("/retailer/catalog");
              }}
            />
          </Card>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {openOrders.map((o) => (
              <Card key={String(o.id)} variant="interactive" className="p-4">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--pol-light-border-subtle)] pb-3">
                  <div className="flex items-center gap-2">
                    <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                      {orderStatusLabel[o.order_status ?? ""] ?? o.order_status ?? "—"}
                    </StatusChip>
                    {o.group_status ? (
                      <StatusChip tone={groupStatusTone[o.group_status] ?? "neutral"}>
                        {groupStatusLabel[o.group_status] ?? o.group_status}
                      </StatusChip>
                    ) : null}
                  </div>
                  <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(o.created_at)}
                  </span>
                </div>

                <div className="mt-3 flex items-center justify-between">
                  <div>
                    <Link
                      href={`/retailer/orders/${o.id}`}
                      className="font-mono text-[14px] font-bold text-[var(--pol-light-text-primary)] hover:text-[var(--pol-light-brand-primary)] hover:underline"
                      dir="ltr"
                    >
                      {o.order_number ?? String(o.id)}
                    </Link>
                    {o.order_group_id ? (
                      <p className="mt-0.5">
                        <Link
                          href={`/retailer/orders/group/${o.order_group_id}`}
                          className="text-[11px] text-[var(--pol-light-brand-primary)] hover:underline"
                        >
                          مشاهده گروه سفارش
                        </Link>
                      </p>
                    ) : null}
                  </div>
                  <span className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                    {formatToman(o.total_amount_toman)}
                  </span>
                </div>

                <div className="mt-3 pt-3 border-t border-[var(--pol-light-border-subtle)] flex items-center justify-end">
                  <Link
                    href={`/retailer/orders/${o.id}`}
                    className="text-[12px] font-semibold text-[var(--pol-light-brand-primary)] hover:underline"
                  >
                    جزئیات سفارش ←
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
