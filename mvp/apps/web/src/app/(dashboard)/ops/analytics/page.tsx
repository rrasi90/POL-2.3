"use client";

import { useCallback, useEffect, useState } from "react";
import { Button, EmptyState, ErrorState, Field, Skeleton } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, formatToman, type LoadState } from "../_shared";

interface KPI {
  name: string;
  description: string;
  value: number;
}

const labels: Record<string, string> = {
  gmv: "حجم ناخالص معاملات (GMV)",
  aov: "میانگین ارزش سفارش (AOV)",
  repeat_rate: "نرخ خرید مجدد",
  otif: "تحویل کامل و به‌موقع (OTIF)",
  self_service_rate: "نرخ خودخدمتی",
  churn: "نرخ ریزش مشتریان",
  cost_to_serve: "هزینه به ازای خدمت",
  cac: "هزینه جذب مشتری (CAC)",
  vendor_continuation: "نرخ استمرار فروشنده",
  catalog_coverage: "نرخ پوشش کاتالوگ",
};

function isoDate(d: Date) {
  return d.toISOString().slice(0, 10);
}

export default function OpsAnalyticsPage() {
  const today = new Date();
  const weekAgo = new Date(today);
  weekAgo.setDate(today.getDate() - 6);
  const [start, setStart] = useState(isoDate(weekAgo));
  const [end, setEnd] = useState(isoDate(today));
  const [rows, setRows] = useState<KPI[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setError(null);
    try {
      const data = await getApi().get<{ kpis?: KPI[] }>(
        "/api/v1/ops/analytics?start_date=" +
          encodeURIComponent(start) +
          "&end_date=" +
          encodeURIComponent(end),
      );
      setRows(Array.isArray(data.kpis) ? data.kpis : []);
      setState("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "دریافت شاخص‌ها ناموفق بود");
      setState("error");
    }
  }, [start, end]);

  useEffect(() => {
    void load();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  function setPreset(days: number) {
    const t = new Date();
    const s = new Date(t);
    s.setDate(t.getDate() - days);
    setStart(isoDate(s));
    setEnd(isoDate(t));
  }

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری شاخص‌ها">
        <Skeleton className="h-8 w-48" />
        <div className={cardCls}><Skeleton lines={3} /></div>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className={cardCls}><Skeleton lines={4} /></div>
          ))}
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت شاخص‌ها ناموفق بود"
        description={error ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline justify-between gap-3 border-b border-[var(--pol-light-border-subtle)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] leading-[30px] font-bold text-[var(--pol-light-text-primary)]">
              تحلیل عملکرد و شاخص‌های کلیدی (KPI)
            </h1>
            <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              O-09
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-muted)]">
            پایش ۱۰ سنجه حیاتی پلتفرم پول در ابعاد مالی، عملیاتی، رضایت و رفتار مشتریان
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
        </div>
      </header>

      {/* Date filter & Presets */}
      <section className={cardCls} aria-label="فیلتر بازه زمانی">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--pol-light-border-subtle)] pb-3">
          <span className="text-[13px] font-semibold text-[var(--pol-light-text-primary)]">
            بازه زمانی گزارش
          </span>
          <div className="flex flex-wrap items-center gap-1.5">
            <button
              type="button"
              onClick={() => setPreset(0)}
              className="rounded-md border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] px-2.5 py-1 text-[11px] font-medium text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)]"
            >
              امروز
            </button>
            <button
              type="button"
              onClick={() => setPreset(6)}
              className="rounded-md border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] px-2.5 py-1 text-[11px] font-medium text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)]"
            >
              ۷ روز اخیر
            </button>
            <button
              type="button"
              onClick={() => setPreset(29)}
              className="rounded-md border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] px-2.5 py-1 text-[11px] font-medium text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)]"
            >
              ۳۰ روز اخیر
            </button>
          </div>
        </div>

        <div className="mt-3 grid gap-3 sm:grid-cols-[1fr_1fr_auto] items-end">
          <Field
            label="از تاریخ"
            value={start}
            onChange={(e) => setStart(e.target.value)}
            dir="ltr"
            type="date"
          />
          <Field
            label="تا تاریخ"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
            dir="ltr"
            type="date"
          />
          <Button size="sm" onClick={() => void load()}>
            اعمال بازه
          </Button>
        </div>
      </section>

      {rows.length === 0 ? (
        <EmptyState
          title="داده‌ای برای بازه زمانی انتخابی یافت نشد"
          description="لطفاً بازه تاریخی را تغییر داده و مجدداً تلاش کنید."
        />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {rows.map((kpi) => {
            const percent = [
              "repeat_rate",
              "otif",
              "self_service_rate",
              "churn",
              "vendor_continuation",
              "catalog_coverage",
            ].includes(kpi.name);
            const money = ["gmv", "aov", "cost_to_serve", "cac"].includes(kpi.name);

            return (
              <article
                key={kpi.name}
                className={[
                  cardCls,
                  "transition-all duration-150 hover:border-[var(--pol-light-border-strong)] hover:shadow-sm",
                ].join(" ")}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
                    {labels[kpi.name] ?? kpi.name}
                  </span>
                  <span className="font-mono text-[10px] text-[var(--pol-light-text-muted)]" dir="ltr">
                    {kpi.name}
                  </span>
                </div>

                <div className="mt-2 text-[26px] font-extrabold tracking-tight tabular-nums text-[var(--pol-light-text-primary)]">
                  {percent
                    ? kpi.value.toLocaleString("fa-IR", { maximumFractionDigits: 1 }) + "٪"
                    : money
                      ? formatToman(kpi.value)
                      : kpi.value.toLocaleString("fa-IR", { maximumFractionDigits: 1 })}
                </div>

                <p className="mt-2 border-t border-[var(--pol-light-border-subtle)] pt-2 text-[12px] leading-[18px] text-[var(--pol-light-text-muted)]">
                  {kpi.description}
                </p>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}
