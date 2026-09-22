"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Button, EmptyState, ErrorState, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  ageLabel,
  ageTone,
  cardCls,
  formatDateTime,
  formatToman,
  itemsOf,
  linkCardCls,
  orderStatusLabel,
  orderStatusTone,
  str,
  type LoadState,
} from "./_shared";

interface OrderRow {
  id: string;
  order_number?: string | null;
  order_status?: string | null;
  dispute_status?: string | null;
  total_amount_toman?: number | string | null;
  created_at?: string | null;
}

const PENDING_STATUSES = new Set(["CREATED", "SUBMITTED"]);
const FULFILLMENT_STATUSES = new Set([
  "ACCEPTED",
  "PARTIALLY_ACCEPTED",
  "PREPARING",
  "READY",
  "DISPATCHED",
]);

const navLinks = [
  { href: "/vendor/orders", title: "صف سفارش‌ها", desc: "پذیرش، رد و پذیرش جزئی" },
  { href: "/vendor/catalog", title: "کاتالوگ فروشنده", desc: "قیمت و موجودی کالاها" },
  { href: "/vendor/inventory", title: "موجودی", desc: "PATCH موجودی کالاها" },
  { href: "/vendor/inventory/daily", title: "تأیید روزانه موجودی", desc: "confirm / confirm-with-changes" },
  { href: "/vendor/referrals", title: "ارجاع‌ها", desc: "فقط نسبت‌دهی — بدون پاداش (D-016)" },
  { href: "/vendor/settlements", title: "تسویه و اسناد", desc: "vendor settlements + invoices" },
  { href: "/vendor/storefront", title: "ویترین", desc: "نمای خواندنی فروشگاه (D-024)" },
  { href: "/vendor/customers", title: "مشتریان", desc: "G-009 — بدون API" },
  { href: "/vendor/staff", title: "کارکنان", desc: "G-010 — بدون API" },
];

/**
 * V-01 vendor dashboard — queue-first.
 * GET /orders (pending + fulfillment counts), recent orders.
 */
export default function VendorHomePage() {
  const [orders, setOrders] = useState<OrderRow[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const data = await getApi().get<unknown>("/api/v1/orders?limit=50&offset=0");
      setOrders(itemsOf<OrderRow>(data, "orders"));
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت سفارش‌ها ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const pending = orders.filter((o) => PENDING_STATUSES.has(o.order_status ?? ""));
  const fulfilling = orders.filter((o) => FULFILLMENT_STATUSES.has(o.order_status ?? ""));

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری پنل تأمین‌کننده">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-3 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className={cardCls}>
              <Skeleton lines={2} />
            </div>
          ))}
        </div>
        <div className={cardCls}>
          <Skeleton lines={4} />
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت داشبورد تأمین‌کننده ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          پنل تأمین‌کننده
        </h1>
        <span className="text-[12px] leading-[18px] text-[var(--pol-light-text-muted)]">
          صف‌محور — V-01
        </span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      <section aria-label="خلاصه صف" className="grid gap-3 sm:grid-cols-3">
        <Link href="/vendor/orders?status=SUBMITTED" className={linkCardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">
            در انتظار پذیرش
          </p>
          <p className="mt-1 text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            {pending.length.toLocaleString("fa-IR")}
          </p>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
            CREATED + SUBMITTED
          </p>
        </Link>
        <Link href="/vendor/orders?status=ACCEPTED" className={linkCardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">در حال اجرا</p>
          <p className="mt-1 text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            {fulfilling.length.toLocaleString("fa-IR")}
          </p>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
            تا DISPATCHED
          </p>
        </Link>
        <Link href="/vendor/inventory/daily" className={linkCardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">
            تأیید روزانه موجودی
          </p>
          <p className="mt-1 text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            {new Date().toLocaleDateString("fa-IR")}
          </p>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
            daily inventory confirm
          </p>
        </Link>
      </section>

      <section aria-label="اقدامات فوری">
        <div className="flex items-center gap-2">
          <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
            نیازمند اقدام
          </h2>
          {pending.length > 0 ? (
            <StatusChip tone="warning">{pending.length.toLocaleString("fa-IR")} مورد</StatusChip>
          ) : null}
          <Link
            href="/vendor/orders"
            className="ms-auto text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
          >
            همه سفارش‌ها
          </Link>
        </div>
        {pending.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="سفارش جدیدی در انتظار نیست"
              description="وقتی خرده‌فروش سفارش ثبت کند، اینجا نمایش داده می‌شود."
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {pending.map((o) => (
              <li key={String(o.id)}>
                <Link
                  href={`/vendor/orders/${o.id}`}
                  className="flex flex-wrap items-center gap-2 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4 transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]"
                >
                  <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                    {orderStatusLabel[o.order_status ?? ""] ?? o.order_status ?? "—"}
                  </StatusChip>
                  <span className="text-[13px] text-[var(--pol-light-text-primary)]" dir="ltr">
                    {o.order_number ?? String(o.id)}
                  </span>
                  <StatusChip tone={ageTone(o.created_at, 4, 12)}>{ageLabel(o.created_at)}</StatusChip>
                  <span className="ms-auto text-[14px] font-medium text-[var(--pol-light-text-primary)]">
                    {formatToman(o.total_amount_toman)}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="سفارش‌های اخیر">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          سفارش‌های اخیر
        </h2>
        {orders.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="سفارشی وجود ندارد" description="هنوز سفارشی به شما اختصاص نیافته است." />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {orders.slice(0, 8).map((o) => (
              <li
                key={String(o.id)}
                className="flex flex-wrap items-center gap-2 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-3"
              >
                <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                  {orderStatusLabel[o.order_status ?? ""] ?? o.order_status ?? "—"}
                </StatusChip>
                <Link
                  href={`/vendor/orders/${o.id}`}
                  className="text-[13px] font-semibold text-[var(--pol-light-text-primary)] hover:underline"
                  dir="ltr"
                >
                  {o.order_number ?? String(o.id)}
                </Link>
                {o.dispute_status && o.dispute_status !== "NONE" ? (
                  <StatusChip tone="danger">
                    {str(o.dispute_status)}
                  </StatusChip>
                ) : null}
                <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                  {formatDateTime(o.created_at)}
                </span>
                <span className="text-[13px] font-medium text-[var(--pol-light-text-primary)]">
                  {formatToman(o.total_amount_toman)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="مقصدها">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          دسترسی سریع
        </h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {navLinks.map((l) => (
            <Link key={l.href} href={l.href} className={linkCardCls}>
              <p className="text-[14px] leading-[22px] font-semibold text-[var(--pol-light-text-primary)]">
                {l.title}
              </p>
              <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">{l.desc}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
