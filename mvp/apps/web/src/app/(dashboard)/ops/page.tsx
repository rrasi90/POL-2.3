"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Button, Card, ErrorState, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  ageLabel,
  ageTone,
  formatDateTime,
  itemsOf,
  str,
  type LoadState,
} from "./_shared";

interface ExceptionsDashboard {
  delivery_exceptions?: {
    total?: number;
    open_count?: number;
    resolved_count?: number;
    escalated_count?: number;
  };
  disputes?: {
    total?: number;
    open_disputes?: number;
  };
  support_cases?: {
    total?: number;
    open_cases?: number;
  };
}

interface QueuePreviewItem {
  id: string;
  kind: "order" | "support" | "recon";
  title: string;
  subtitle: string;
  created_at?: string | null;
}

const navLinks = [
  { href: "/ops/queues", title: "صفوف یکپارچه عملیات", desc: "سفارش‌ها، تیکت‌ها، مغایرت‌ها و RMA", icon: "📋" },
  { href: "/ops/support", title: "میز پاسخگویی پشتیبانی", desc: "مدیریت تیکت‌ها و مکالمات طرفین", icon: "💬" },
  { href: "/ops/reconciliation", title: "تطبیق و انطباق مالی", desc: "بررسی عدم تطابق‌های پرداخت و تسویه", icon: "⚖️" },
  { href: "/ops/rma", title: "مرجوعی‌ها و استرداد کالا", desc: "بررسی شکایات و عودت وجه", icon: "🔄" },
  { href: "/ops/admin", title: "استثناها و لاگ‌های ممیزی", desc: "داشبورد وقایع سیستمی و Audit Logs", icon: "🛡️" },
  { href: "/ops/permissions", title: "ماتریس دسترسی و مجوزها", desc: "مدیریت دسترسی‌های سیستمی و اعطای نقش‌ها", icon: "🔑" },
  { href: "/ops/catalog-candidates", title: "تأیید کالاهای کاتالوگ", desc: "بررسی بارکدها و پیشنهادهای بنکداران", icon: "🏷️" },
  { href: "/ops/notifications", title: "مرکز اعلان‌ها و پیامک", desc: "لاگ پیام‌های سیستمی و تحویل پیامک", icon: "🔔" },
  { href: "/ops/analytics", title: "داشبورد شاخص‌های کلیدی", desc: "تحلیل شاخص‌های ده‌گانه پایلوت FMCG", icon: "📈" },
  { href: "/ops/risk", title: "سیگنال‌های ریسک و پایداری", desc: "پایش مغایرت‌های بحرانی و نرخ لغو", icon: "⚠️" },
  { href: "/admin", title: "مدیریت سازمان‌ها و کاربران", desc: "تنظیمات سیستمی و دسترسی‌های کلان", icon: "⚙️" },
];

export default function OpsOverviewPage() {
  const [dash, setDash] = useState<ExceptionsDashboard | null>(null);
  const [orders, setOrders] = useState<QueuePreviewItem[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const [d, o] = await Promise.all([
        getApi().get<ExceptionsDashboard>("/api/v1/admin/exceptions/dashboard"),
        getApi().get<unknown>("/api/v1/orders?limit=10&offset=0"),
      ]);
      setDash(d);
      const orderItems = itemsOf<Record<string, unknown>>(o, "orders");
      setOrders(
        orderItems.slice(0, 5).map((item) => ({
          id: str(item.id, ""),
          kind: "order" as const,
          title: str(item.order_number ?? item.id),
          subtitle: str(item.order_status),
          created_at: typeof item.created_at === "string" ? item.created_at : null,
        })),
      );
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت داشبورد عملیات ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (state === "loading") {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری عملیات">
        <Skeleton className="h-9 w-52" />
        <div className="grid gap-3 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="p-4">
              <Skeleton lines={2} />
            </Card>
          ))}
        </div>
        <Card className="p-5">
          <Skeleton lines={5} />
        </Card>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت داشبورد عملیات ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  const ex = dash?.delivery_exceptions ?? {};
  const disputes = dash?.disputes ?? {};
  const cases = dash?.support_cases ?? {};

  const openExCount = ex.open_count ?? 0;
  const openDispCount = disputes.open_disputes ?? 0;
  const openCasesCount = cases.open_cases ?? 0;

  return (
    <div className="space-y-6">
      {/* Dense Command Header */}
      <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-[var(--pol-light-border-subtle)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[20px] md:text-[24px] font-bold text-[var(--pol-light-text-primary)]">
              اتاق فرمان عملیات مرکزی پُل
            </h1>
            <span className="rounded-md bg-rose-100 dark:bg-rose-950/40 px-2 py-0.5 text-[11px] font-bold text-rose-700 dark:text-rose-400">
              O-01 · Dense Command
            </span>
          </div>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
            پایش بلادرنگ صفوف استثناها، اختلافات طرفین، تیکت‌های باز و سلامت توزیع کالا
          </p>
        </div>

        <Button variant="secondary" size="sm" onClick={() => void load()}>
          به‌روزرسانی داده‌ها
        </Button>
      </header>

      {/* Primary Exception Counters */}
      <section aria-label="خلاصه استثناها" className="grid gap-4 sm:grid-cols-3">
        <Link
          href="/ops/queues?tab=orders"
          className="group block rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
        >
          <Card
            className={[
              "p-4 transition-all duration-150 group-hover:shadow-[var(--pol-shadow-md)]",
              openExCount > 0
                ? "border-rose-300 bg-rose-50/20 dark:border-rose-900/50 dark:bg-rose-950/20"
                : "",
            ].join(" ")}
          >
            <div className="flex items-center justify-between">
              <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
                استثناهای باز تحویل
              </span>
              <StatusChip tone={openExCount > 0 ? "danger" : "neutral"}>
                {openExCount > 0 ? "نیازمند مداخله" : "عادی"}
              </StatusChip>
            </div>
            <div className="mt-2 text-[26px] font-bold text-[var(--pol-light-text-primary)]">
              {openExCount.toLocaleString("fa-IR")}
            </div>
            <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
              کل: {str(ex.total, "0")} · موارد ارتقایافته: {str(ex.escalated_count, "0")}
            </p>
          </Card>
        </Link>

        <Link
          href="/ops/queues?tab=rma"
          className="group block rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
        >
          <Card
            className={[
              "p-4 transition-all duration-150 group-hover:shadow-[var(--pol-shadow-md)]",
              openDispCount > 0
                ? "border-amber-300 bg-amber-50/20 dark:border-amber-900/50 dark:bg-amber-950/20"
                : "",
            ].join(" ")}
          >
            <div className="flex items-center justify-between">
              <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
                اختلافات باز سفارش‌ها
              </span>
              <StatusChip tone={openDispCount > 0 ? "warning" : "neutral"}>
                {openDispCount > 0 ? "در حال رسیدگی" : "بدون اختلاف"}
              </StatusChip>
            </div>
            <div className="mt-2 text-[26px] font-bold text-[var(--pol-light-text-primary)]">
              {openDispCount.toLocaleString("fa-IR")}
            </div>
            <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
              از مجموع {str(disputes.total, "0")} مورد ثبت‌شده
            </p>
          </Card>
        </Link>

        <Link
          href="/ops/support"
          className="group block rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
        >
          <Card
            className={[
              "p-4 transition-all duration-150 group-hover:shadow-[var(--pol-shadow-md)]",
              openCasesCount > 0
                ? "border-sky-300 bg-sky-50/20 dark:border-sky-900/50 dark:bg-sky-950/20"
                : "",
            ].join(" ")}
          >
            <div className="flex items-center justify-between">
              <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
                تیکت‌های باز پشتیبانی
              </span>
              <StatusChip tone={openCasesCount > 0 ? "info" : "neutral"}>
                {openCasesCount > 0 ? "نیازمند پاسخ" : "پاسخ داده‌شده"}
              </StatusChip>
            </div>
            <div className="mt-2 text-[26px] font-bold text-[var(--pol-light-text-primary)]">
              {openCasesCount.toLocaleString("fa-IR")}
            </div>
            <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
              کل پرونده‌های ثبت‌شده: {str(cases.total, "0")}
            </p>
          </Card>
        </Link>
      </section>

      {/* Orders Quick Preview Queue */}
      <section aria-label="پیش‌نمایش صفوف" className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
            آخرین سفارش‌های ورودی به صف عملیات
          </h2>
          <Link
            href="/ops/queues"
            className="text-[12px] font-semibold text-[var(--pol-light-brand-primary)] hover:underline"
          >
            مشاهده کامل صفوف یکپارچه ←
          </Link>
        </div>

        <Card className="divide-y divide-[var(--pol-light-border-subtle)] p-0 overflow-hidden">
          {orders.map((o) => (
            <div
              key={o.id}
              className="flex flex-col gap-2 p-3 sm:flex-row sm:items-center sm:justify-between hover:bg-[var(--pol-light-surface-subtle)] transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="font-mono text-[13px] font-bold text-[var(--pol-light-text-primary)]" dir="ltr">
                  {o.title}
                </span>
                <StatusChip tone="info">{o.subtitle}</StatusChip>
              </div>

              <div className="flex items-center justify-between gap-4 text-[12px]">
                <span className="text-[var(--pol-light-text-muted)]">
                  {formatDateTime(o.created_at)}
                </span>
                <Link
                  href={`/ops/orders/${o.id}`}
                  className="font-medium text-[var(--pol-light-brand-primary)] hover:underline"
                >
                  بازرسی پرونده ←
                </Link>
              </div>
            </div>
          ))}
        </Card>
      </section>

      {/* Operational Modules Navigation Grid */}
      <section aria-label="ماژول‌های عملیاتی" className="space-y-3">
        <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
          کنسول‌های مدیریت عملیاتی
        </h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {navLinks.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="group block rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
            >
              <Card className="h-full p-4 transition-all duration-150 group-hover:shadow-[var(--pol-shadow-md)] group-hover:border-[var(--pol-light-border-strong)]">
                <div className="flex items-start gap-3">
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[var(--pol-light-surface-subtle)] text-[16px]">
                    {l.icon}
                  </span>
                  <div>
                    <h3 className="text-[13px] font-bold text-[var(--pol-light-text-primary)] group-hover:text-[var(--pol-light-brand-primary)] transition-colors">
                      {l.title}
                    </h3>
                    <p className="mt-0.5 text-[11px] text-[var(--pol-light-text-secondary)] line-clamp-1">
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
