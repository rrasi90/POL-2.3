"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Button, ErrorState, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  ageLabel,
  ageTone,
  cardCls,
  formatDateTime,
  itemsOf,
  linkCardCls,
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
  { href: "/ops/queues", title: "صفوف یکپارچه", desc: "سفارش، پشتیبانی، تطبیق و RMA" },
  { href: "/ops/support", title: "میز پشتیبانی", desc: "پرونده‌ها، پیام و تغییر وضعیت" },
  { href: "/ops/reconciliation", title: "تطبیق مالی", desc: "مغایرت‌های پرداخت و تسویه" },
  { href: "/ops/rma", title: "مرجوعی و اختلاف", desc: "بررسی per-order + شکاف G-013" },
  { href: "/ops/admin", title: "ادمین / لاگ ممیزی", desc: "داشبورد استثناها + Audit Logs" },
  { href: "/ops/notifications", title: "عملیات اعلان", desc: "فهرست اعلان‌ها + شکاف Provider" },
  { href: "/ops/analytics", title: "تحلیل پایلوت", desc: "G-008 — بدون API" },
  { href: "/ops/risk", title: "ریسک و پایداری", desc: "API محدود → GAP" },
  { href: "/admin", title: "مدیریت کاربران و سازمان", desc: "G-007 — بدون CRUD" },
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
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری عملیات">
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
        title="دریافت داشبورد عملیات ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  const ex = dash?.delivery_exceptions ?? {};
  const disputes = dash?.disputes ?? {};
  const cases = dash?.support_cases ?? {};

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          عملیات
        </h1>
        <span className="text-[12px] leading-[18px] text-[var(--pol-light-text-muted)]">
          صف‌محور — O-01
        </span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      <section aria-label="خلاصه استثناها" className="grid gap-3 sm:grid-cols-3">
        <div className={cardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">
            استثنای تحویل (باز)
          </p>
          <p className="mt-1 text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            {(ex.open_count ?? 0).toLocaleString("fa-IR")}
          </p>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
            کل {str(ex.total, "0")} · ارتقا {str(ex.escalated_count, "0")}
          </p>
        </div>
        <div className={cardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">اختلافات باز</p>
          <p className="mt-1 text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            {(disputes.open_disputes ?? 0).toLocaleString("fa-IR")}
          </p>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
            کل {str(disputes.total, "0")}
          </p>
        </div>
        <div className={cardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">
            پرونده‌های پشتیبانی باز
          </p>
          <p className="mt-1 text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            {(cases.open_cases ?? 0).toLocaleString("fa-IR")}
          </p>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
            کل {str(cases.total, "0")}
          </p>
        </div>
      </section>

      <section aria-label="پیش‌نمایش صف سفارش‌ها">
        <div className="flex items-center gap-2">
          <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
            سفارش‌های اخیر
          </h2>
          <Link
            href="/ops/queues"
            className="ms-auto text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
          >
            همه صف‌ها
          </Link>
        </div>
        {orders.length === 0 ? (
          <div className="mt-3">
            <ErrorState
              title="سفارشی برای نمایش نیست"
              description="فهرست سفارش‌ها خالی است یا در دسترس نیست."
              onRetry={() => void load()}
              retryLabel="تلاش مجدد"
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {orders.map((o) => (
              <li
                key={o.id}
                className="flex flex-wrap items-center gap-2 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-3"
              >
                <StatusChip tone="info">{o.subtitle}</StatusChip>
                <span className="text-[13px] text-[var(--pol-light-text-primary)]" dir="ltr">
                  {o.title}
                </span>
                <StatusChip tone={ageTone(o.created_at)}>{ageLabel(o.created_at)}</StatusChip>
                <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                  {formatDateTime(o.created_at)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="مقصد عملیات">
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
