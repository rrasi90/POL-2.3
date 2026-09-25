"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Button, EmptyState, ErrorState, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, itemsOf, type LoadState } from "../_shared";

interface ExceptionsDashboard {
  delivery_exceptions?: { total?: number; open_count?: number; resolved_count?: number; escalated_count?: number };
  disputes?: { total?: number; open_disputes?: number };
  support_cases?: { total?: number; open_cases?: number };
}

interface ReconCase {
  id: string;
  status?: string | null;
  expected_amount_toman?: number | string | null;
  observed_amount_toman?: number | string | null;
  opened_at?: string | null;
  attempt_count?: number | null;
}

export default function OpsRiskPage() {
  const [dashboard, setDashboard] = useState<ExceptionsDashboard | null>(null);
  const [recon, setRecon] = useState<ReconCase[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setError(null);
    try {
      const [d, r] = await Promise.all([
        getApi().get<ExceptionsDashboard>("/api/v1/admin/exceptions/dashboard"),
        getApi().get<unknown>("/api/v1/finance/reconciliation?status=OPEN&limit=10&offset=0"),
      ]);
      setDashboard(d);
      setRecon(itemsOf<ReconCase>(r, "cases"));
      setState("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "دریافت سیگنال‌های ریسک ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true">
        <Skeleton className="h-8 w-56" />
        <div className="grid gap-3 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className={cardCls}><Skeleton lines={2} /></div>
          ))}
        </div>
        <div className={cardCls}><Skeleton lines={5} /></div>
      </div>
    );
  }

  if (state === "error") {
    return <ErrorState title="دریافت سیگنال‌های ریسک ناموفق بود" description={error ?? undefined} onRetry={() => void load()} />;
  }

  const delivery = dashboard?.delivery_exceptions ?? {};
  const disputes = dashboard?.disputes ?? {};
  const support = dashboard?.support_cases ?? {};

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          ریسک و پایداری عملیاتی
        </h1>
        <StatusChip tone="info">O-07 · سیگنال‌های واقعی</StatusChip>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-3 text-[12px] leading-[20px] text-[var(--pol-light-text-secondary)]">
        این صفحه امتیاز ریسک مصنوعی تولید نمی‌کند. فقط شاخص‌های عملیاتی موجود در backend را
        نمایش می‌دهد؛ مدل امتیازدهی طرف حساب هنوز در قرارداد محصول تعریف نشده است.
      </div>

      <section aria-label="سیگنال‌های عملیاتی" className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className={cardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">استثنای تحویل باز</p>
          <p className="mt-1 text-[24px] font-bold text-[var(--pol-light-text-primary)]">{(delivery.open_count ?? 0).toLocaleString("fa-IR")}</p>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">کل {delivery.total ?? 0} · ارجاع‌شده {delivery.escalated_count ?? 0}</p>
        </div>
        <div className={cardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">اختلاف باز</p>
          <p className="mt-1 text-[24px] font-bold text-[var(--pol-light-text-primary)]">{(disputes.open_disputes ?? 0).toLocaleString("fa-IR")}</p>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">کل {disputes.total ?? 0}</p>
        </div>
        <div className={cardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">پشتیبانی باز</p>
          <p className="mt-1 text-[24px] font-bold text-[var(--pol-light-text-primary)]">{(support.open_cases ?? 0).toLocaleString("fa-IR")}</p>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">کل {support.total ?? 0}</p>
        </div>
        <div className={cardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">تطبیق مالی باز</p>
          <p className="mt-1 text-[24px] font-bold text-[var(--pol-light-text-primary)]">{recon.length.toLocaleString("fa-IR")}</p>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">فهرست زنده از reconciliation</p>
        </div>
      </section>

      <section aria-label="موارد تطبیق باز" className={cardCls}>
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">تطبیق‌های مالی باز</h2>
          <Link href="/ops/reconciliation" className="ms-auto text-[12px] text-[var(--pol-light-brand-primary)]">
            مشاهده همه
          </Link>
        </div>
        {recon.length === 0 ? (
          <div className="mt-3"><EmptyState title="مورد بازی ثبت نشده" description="در حال حاضر مورد OPEN در reconciliation وجود ندارد." /></div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {recon.map((item) => (
              <li key={item.id} className="rounded-[10px] border border-[var(--pol-light-border-subtle)] p-3">
                <div className="flex flex-wrap items-center gap-2">
                  <StatusChip tone="warning">{item.status ?? "OPEN"}</StatusChip>
                  <span className="text-[12px] text-[var(--pol-light-text-muted)]" dir="ltr">{item.id}</span>
                  <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                    تلاش {item.attempt_count ?? 0}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
