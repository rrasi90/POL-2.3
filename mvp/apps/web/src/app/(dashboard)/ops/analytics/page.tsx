"use client";

import { useCallback, useEffect, useState } from "react";
import { Button, ErrorState, Field, Skeleton } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, formatToman, type LoadState } from "../_shared";

interface KPI { name: string; description: string; value: number; }

const labels: Record<string,string> = {
  gmv:"GMV", aov:"AOV", repeat_rate:"نرخ خرید مجدد", otif:"OTIF",
  self_service_rate:"خودخدمتی", churn:"ریزش", cost_to_serve:"هزینه خدمت",
  cac:"CAC", vendor_continuation:"ادامه فروشنده", catalog_coverage:"پوشش کاتالوگ",
};

function isoDate(d: Date) { return d.toISOString().slice(0,10); }

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
        "/api/v1/ops/analytics?start_date=" + encodeURIComponent(start) +
        "&end_date=" + encodeURIComponent(end)
      );
      setRows(Array.isArray(data.kpis) ? data.kpis : []);
      setState("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "دریافت شاخص‌ها ناموفق بود");
      setState("error");
    }
  }, [start, end]);

  useEffect(() => { void load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  if (state === "loading") return <div className="space-y-4" aria-busy="true"><Skeleton className="h-8 w-48" /><div className={cardCls}><Skeleton lines={8} /></div></div>;
  if (state === "error") return <ErrorState title="دریافت شاخص‌ها ناموفق بود" description={error ?? undefined} onRetry={() => void load()} />;

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">تحلیل و KPI</h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">O-09 · ده شاخص</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>به‌روزرسانی</Button>
      </header>

      <section className={cardCls}>
        <div className="grid gap-3 md:grid-cols-2">
          <Field label="از تاریخ" value={start} onChange={(e) => setStart(e.target.value)} dir="ltr" type="date" />
          <Field label="تا تاریخ" value={end} onChange={(e) => setEnd(e.target.value)} dir="ltr" type="date" />
        </div>
        <div className="mt-3"><Button onClick={() => void load()}>اعمال بازه</Button></div>
      </section>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {rows.map((kpi) => {
          const percent = ["repeat_rate","otif","self_service_rate","churn","vendor_continuation","catalog_coverage"].includes(kpi.name);
          const money = ["gmv","aov","cost_to_serve","cac"].includes(kpi.name);
          return (
            <article key={kpi.name} className={cardCls}>
              <div className="text-[12px] text-[var(--pol-light-text-muted)]">{labels[kpi.name] ?? kpi.name}</div>
              <div className="mt-2 text-[24px] font-bold text-[var(--pol-light-text-primary)]">
                {percent
                  ? kpi.value.toLocaleString("fa-IR", { maximumFractionDigits: 1 }) + "%"
                  : money
                    ? formatToman(kpi.value)
                    : kpi.value.toLocaleString("fa-IR", { maximumFractionDigits: 1 })}
              </div>
              <p className="mt-2 text-[12px] leading-[18px] text-[var(--pol-light-text-secondary)]">{kpi.description}</p>
            </article>
          );
        })}
      </div>
    </div>
  );
}
