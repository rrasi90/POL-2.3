"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
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
  itemsOf,
  type LoadState,
} from "../_shared";

interface ReturnRow {
  return_id: string;
  order_id: string;
  order_number?: string;
  status?: string;
  reason?: string;
  claimed_refund_amount_toman?: number | string | null;
  approved_refund_amount_toman?: number | string | null;
  retailer_name?: string;
  vendor_name?: string;
  created_at?: string;
}

export default function OpsRmaPage() {
  const [rows, setRows] = useState<ReturnRow[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setError(null);
    try {
      const data = await getApi().get<unknown>("/api/v1/ops/returns?limit=50&offset=0");
      setRows(itemsOf<ReturnRow>(data, "returns"));
      setState("ready");
    } catch (e) {
      setError(e instanceof Error ? e.message : "دریافت پرونده‌های RMA ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (state === "loading") {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری مرجوعی‌ها">
        <Skeleton className="h-9 w-48" />
        <div className="grid gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="p-5">
              <Skeleton lines={4} />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت پرونده‌های RMA ناموفق بود"
        description={error ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-[var(--pol-light-border-subtle)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[20px] md:text-[24px] font-bold text-[var(--pol-light-text-primary)]">
              مدیریت مرجوعی و استرداد کالا (RMA)
            </h1>
            <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-bold text-[var(--pol-light-text-secondary)]">
              O-04 · {rows.length.toLocaleString("fa-IR")} پرونده
            </span>
          </div>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
            بررسی علل مرجوعی اقلام معیوب یا تاریخ‌گذشته، حل اختلافات و تأیید مبالغ بازگشت وجه
          </p>
        </div>

        <Button variant="secondary" size="sm" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      {/* Scope Disclaimer */}
      <div className="flex items-start gap-3 rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-4 text-[13px] text-[var(--pol-light-text-secondary)] leading-relaxed">
        <span className="text-base">ℹ️</span>
        <div>
          <strong className="font-semibold text-[var(--pol-light-text-primary)]">فرآیند RMA:</strong>{" "}
          مرجوعی کالا در سامانه پُل مستلزم تأیید فیزیکی بازگشت کالا به انبار بنکدار و ثبت گواهی عدم
          تطابق است. تسویه استرداد وجه به صورت خودکار در دوره تسویه بعدی اعمال خواهد شد.
        </div>
      </div>

      {/* RMA Cases List */}
      {rows.length === 0 ? (
        <EmptyState
          title="هیچ پرونده مرجوعی فعالی وجود ندارد"
          description="درخواست‌های عودت کالا ثبت‌شده توسط خرده‌فروشان پس از ارجاع در این بخش نمایش داده می‌شوند."
        />
      ) : (
        <div className="grid gap-3">
          {rows.map((r) => {
            const isApproved = r.status === "APPROVED";
            const isRejected = r.status === "REJECTED";
            const tone = isApproved ? "success" : isRejected ? "danger" : "warning";

            return (
              <Card
                key={r.return_id}
                className="p-5 transition-all duration-150 hover:shadow-[var(--pol-shadow-md)] hover:border-[var(--pol-light-border-strong)]"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <StatusChip tone={tone}>
                      {r.status === "APPROVED"
                        ? "تأییدشده"
                        : r.status === "REJECTED"
                          ? "ردشده"
                          : r.status ?? "در انتظار بررسی"}
                    </StatusChip>
                    <span className="font-mono text-[14px] font-bold text-[var(--pol-light-text-primary)]" dir="ltr">
                      سفارش: {r.order_number ?? r.order_id}
                    </span>
                    <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
                      {r.retailer_name ?? "خرده‌فروش"} ← {r.vendor_name ?? "بنکدار"}
                    </span>
                  </div>

                  <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(r.created_at)}
                  </span>
                </div>

                {r.reason && (
                  <p className="mt-3 rounded-lg bg-[var(--pol-light-surface-subtle)] p-3 text-[13px] text-[var(--pol-light-text-secondary)] leading-relaxed">
                    <strong className="text-[var(--pol-light-text-primary)]">علت عودت:</strong> {r.reason}
                  </p>
                )}

                <div className="mt-4 flex flex-wrap items-center justify-between border-t border-[var(--pol-light-border-subtle)] pt-3 text-[13px]">
                  <div className="flex flex-wrap items-center gap-4 text-[12px]">
                    <span>
                      مبلغ درخواستی:{" "}
                      <strong className="text-[var(--pol-light-text-primary)]">
                        {formatToman(r.claimed_refund_amount_toman)}
                      </strong>
                    </span>
                    {r.approved_refund_amount_toman != null && (
                      <span>
                        مبلغ تأییدشده:{" "}
                        <strong className="text-emerald-600 dark:text-emerald-400">
                          {formatToman(r.approved_refund_amount_toman)}
                        </strong>
                      </span>
                    )}
                  </div>

                  <Link
                    href={`/ops/orders/${r.order_id}`}
                    className="text-[12px] font-semibold text-[var(--pol-light-brand-primary)] hover:underline"
                  >
                    مشاهده جزئیات سفارش ←
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
