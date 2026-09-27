"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Button, Card, EmptyState, ErrorState, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  ageLabel,
  ageTone,
  formatDateTime,
  formatToman,
  itemsOf,
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
  { href: "/vendor/orders", title: "صف سفارش‌ها", desc: "پذیرش، رد، پذیرش جزئی و رهگیری ارسال", icon: "📋" },
  { href: "/vendor/inventory/daily", title: "تأیید روزانه موجودی", desc: "مراسم صبحگاهی اعلام موجودی معتبر", icon: "⏰" },
  { href: "/vendor/catalog", title: "کاتالوگ فروشنده", desc: "مدیریت تنوع کالا و سطوح قیمت‌گذاری", icon: "📦" },
  { href: "/vendor/inventory", title: "مدیریت انبار و موجودی", desc: "به‌روزرسانی سریع موجودی اقلام", icon: "📊" },
  { href: "/vendor/settlements", title: "تسویه‌حساب و فاکتورها", desc: "مشاهده دوره‌های تسویه مالی و اسناد", icon: "💳" },
  { href: "/vendor/customers", title: "فهرست مشتریان", desc: "سوپرمارکت‌ها و خرده‌فروشان طرف قرارداد", icon: "👥" },
  { href: "/vendor/storefront", title: "ویترین فروشگاه", desc: "نمای عمومی محصولات برای خرده‌فروشان", icon: "🏪" },
  { href: "/vendor/staff", title: "دسترسی کارکنان", desc: "مدیریت دسترسی‌های پرسنل بنکداری", icon: "🔑" },
  { href: "/vendor/referrals", title: "ارجاع و بازاریابی", desc: "کدهای معرفی و انتساب فروش", icon: "🔗" },
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
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری پنل تأمین‌کننده">
        <Skeleton className="h-9 w-56" />
        <div className="grid gap-4 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="p-5">
              <Skeleton lines={2} />
            </Card>
          ))}
        </div>
        <Card className="p-6">
          <Skeleton lines={5} />
        </Card>
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
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] md:text-[26px] font-bold text-[var(--pol-light-text-primary)]">
              مرکز عملیات بنکداری
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              V-01 · صف‌محور
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            مدیریت سفارش‌های دریافتی، تأیید موجودی روزانه و فرآیند پردازش و ارسال
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={() => void load()}>
          به‌روزرسانی اطلاعات
        </Button>
      </header>

      {/* KPI Highlight Cards */}
      <section aria-label="خلاصه صف" className="grid gap-4 sm:grid-cols-3">
        <Link
          href="/vendor/orders?status=SUBMITTED"
          className="group block rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
        >
          <Card
            className={[
              "p-5 transition-all duration-200 group-hover:shadow-[var(--pol-shadow-md)]",
              pending.length > 0
                ? "border-amber-300 bg-amber-50/40 dark:border-amber-700/50 dark:bg-amber-950/20"
                : "group-hover:border-[var(--pol-light-border-strong)]",
            ].join(" ")}
          >
            <div className="flex items-center justify-between">
              <span className="text-[13px] font-medium text-[var(--pol-light-text-secondary)]">
                در انتظار پذیرش
              </span>
              <span className="text-[20px]">⏳</span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-[28px] font-bold text-[var(--pol-light-text-primary)]">
                {pending.length.toLocaleString("fa-IR")}
              </span>
              <span className="text-[12px] text-[var(--pol-light-text-muted)]">سفارش</span>
            </div>
            <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
              نیازمند اقدام فوری تأیید یا رد
            </p>
          </Card>
        </Link>

        <Link
          href="/vendor/orders?status=ACCEPTED"
          className="group block rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
        >
          <Card className="p-5 transition-all duration-200 group-hover:shadow-[var(--pol-shadow-md)] group-hover:border-[var(--pol-light-border-strong)]">
            <div className="flex items-center justify-between">
              <span className="text-[13px] font-medium text-[var(--pol-light-text-secondary)]">
                در حال پردازش و ارسال
              </span>
              <span className="text-[20px]">🚚</span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-[28px] font-bold text-[var(--pol-light-text-primary)]">
                {fulfilling.length.toLocaleString("fa-IR")}
              </span>
              <span className="text-[12px] text-[var(--pol-light-text-muted)]">سفارش</span>
            </div>
            <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
              از آماده‌سازی تا تحویل به ناوگان
            </p>
          </Card>
        </Link>

        <Link
          href="/vendor/inventory/daily"
          className="group block rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
        >
          <Card className="p-5 transition-all duration-200 group-hover:shadow-[var(--pol-shadow-md)] group-hover:border-[var(--pol-light-border-strong)]">
            <div className="flex items-center justify-between">
              <span className="text-[13px] font-medium text-[var(--pol-light-text-secondary)]">
                تأیید روزانه موجودی
              </span>
              <span className="text-[20px]">📋</span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-[22px] font-bold text-[var(--pol-light-text-primary)]">
                {new Date().toLocaleDateString("fa-IR")}
              </span>
            </div>
            <p className="mt-1 text-[11px] text-[var(--pol-light-brand-primary)] group-hover:underline">
              ثبت موجودی امروز ←
            </p>
          </Card>
        </Link>
      </section>

      {/* Urgent Orders Queue (Needs Action) */}
      <section aria-label="اقدامات فوری" className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
              سفارش‌های نیازمند اقدام فوری
            </h2>
            {pending.length > 0 && (
              <StatusChip tone="warning">{pending.length.toLocaleString("fa-IR")} مورد</StatusChip>
            )}
          </div>
          <Link
            href="/vendor/orders"
            className="text-[13px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
          >
            مشاهده تمام صف سفارش‌ها ←
          </Link>
        </div>

        {pending.length === 0 ? (
          <EmptyState
            title="هیچ سفارشی معطل اقدام شما نیست"
            description="سفارش‌های جدید ثبت‌شده توسط خرده‌فروشان بلافاصله در این بخش ظاهر می‌شوند."
          />
        ) : (
          <div className="grid gap-3">
            {pending.map((o) => (
              <Link
                key={String(o.id)}
                href={`/vendor/orders/${o.id}`}
                className="group block rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
              >
                <Card className="p-4 transition-all duration-200 group-hover:shadow-[var(--pol-shadow-md)] group-hover:border-[var(--pol-light-border-strong)]">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex flex-wrap items-center gap-2.5">
                      <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                        {orderStatusLabel[o.order_status ?? ""] ?? o.order_status ?? "—"}
                      </StatusChip>
                      <StatusChip tone={ageTone(o.created_at, 4, 12)}>
                        {ageLabel(o.created_at)}
                      </StatusChip>
                      <span className="font-mono text-[14px] font-bold text-[var(--pol-light-text-primary)]" dir="ltr">
                        {o.order_number ?? String(o.id)}
                      </span>
                    </div>

                    <div className="flex items-center justify-between border-t border-[var(--pol-light-border-subtle)] pt-2 sm:border-0 sm:pt-0 sm:gap-4">
                      <span className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                        {formatToman(o.total_amount_toman)}
                      </span>
                      <span className="text-[12px] font-medium text-[var(--pol-light-brand-primary)] group-hover:underline">
                        بررسی و پذیرش ←
                      </span>
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Recent Orders Overview */}
      <section aria-label="سفارش‌های اخیر" className="space-y-4">
        <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
          سفارش‌های اخیر
        </h2>

        {orders.length === 0 ? (
          <EmptyState
            title="هنوز سفارشی دریافت نشده است"
            description="به محض تخصیص اولین سفارش توسط سیستم توزیع پُل، در این قسمت ثبت خواهد شد."
          />
        ) : (
          <div className="grid gap-2.5">
            {orders.slice(0, 8).map((o) => (
              <Card
                key={String(o.id)}
                className="p-3.5 transition-all duration-150 hover:border-[var(--pol-light-border-strong)]"
              >
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                      {orderStatusLabel[o.order_status ?? ""] ?? o.order_status ?? "—"}
                    </StatusChip>
                    <Link
                      href={`/vendor/orders/${o.id}`}
                      className="font-mono text-[13px] font-bold text-[var(--pol-light-text-primary)] hover:text-[var(--pol-light-brand-primary)] hover:underline"
                      dir="ltr"
                    >
                      {o.order_number ?? String(o.id)}
                    </Link>
                    {o.dispute_status && o.dispute_status !== "NONE" && (
                      <StatusChip tone="danger">{str(o.dispute_status)}</StatusChip>
                    )}
                  </div>

                  <div className="flex items-center justify-between text-[12px] sm:gap-4">
                    <span className="text-[var(--pol-light-text-muted)]">
                      {formatDateTime(o.created_at)}
                    </span>
                    <span className="font-semibold text-[var(--pol-light-text-primary)]">
                      {formatToman(o.total_amount_toman)}
                    </span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>

      {/* Quick Navigation Cards */}
      <section aria-label="دسته‌بندی‌های عملیاتی" className="space-y-4">
        <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
          دسترسی سریع عملیاتی
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {navLinks.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="group block rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
            >
              <Card className="h-full p-4 transition-all duration-200 group-hover:shadow-[var(--pol-shadow-md)] group-hover:border-[var(--pol-light-border-strong)]">
                <div className="flex items-center gap-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[var(--pol-light-surface-subtle)] text-[18px]">
                    {l.icon}
                  </span>
                  <div>
                    <h3 className="text-[14px] font-bold text-[var(--pol-light-text-primary)] group-hover:text-[var(--pol-light-brand-primary)] transition-colors">
                      {l.title}
                    </h3>
                    <p className="mt-0.5 text-[12px] text-[var(--pol-light-text-secondary)] line-clamp-1">
                      {l.desc}
                    </p>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
