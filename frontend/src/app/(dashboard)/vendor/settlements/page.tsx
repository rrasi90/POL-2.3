"use client";

import { useMemo } from "react";
import { useApi } from "@/lib/hooks/useApi";
import { StatusBadge } from "@/components/ui/Badge";
import { EmptyState, EmptyBoxIcon } from "@/components/ui/EmptyState";

interface SettlementBatch {
  id: string;
  batch_number: string;
  date: string;
  gross_amount: number;
  commission: number;
  net_amount: number;
  status: "PENDING" | "PROCESSING" | "SETTLED" | "FAILED";
  settled_date: string | null;
  items_count: number;
}

function formatToman(value: number): string {
  return new Intl.NumberFormat("fa-IR").format(value) + " تومان";
}

function toJalali(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString("fa-IR-u-nu-latn", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function KPISkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
          <div className="mb-3 h-3 w-24 animate-pulse rounded bg-gray-200" />
          <div className="mb-2 h-7 w-20 animate-pulse rounded bg-gray-200" />
        </div>
      ))}
    </div>
  );
}

function BatchSkeleton() {
  return (
    <div className="flex flex-col gap-3">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="animate-pulse rounded-xl border border-gray-200 bg-white p-4">
          <div className="flex items-start justify-between">
            <div className="flex flex-col gap-2">
              <div className="h-4 w-28 rounded bg-gray-200" />
              <div className="h-3 w-36 rounded bg-gray-100" />
            </div>
            <div className="flex flex-col items-end gap-2">
              <div className="h-4 w-32 rounded bg-gray-200" />
              <div className="h-5 w-20 rounded-full bg-gray-200" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
}

function KPICard({ title, value, subtitle }: KPICardProps) {
  return (
    <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
      <p className="mb-3 text-xs text-gray-500">{title}</p>
      <p className="mb-1 text-[28px] font-bold leading-none text-gray-900">{value}</p>
      {subtitle && <p className="text-xs text-gray-400">{subtitle}</p>}
    </div>
  );
}

export default function VendorSettlementsPage() {
  const { data, isLoading } = useApi<{
    results: SettlementBatch[];
    count: number;
  }>("/api/v1/finance/settlements", { ordering: "-date" });

  const batches = data?.results ?? [];

  const kpis = useMemo(() => {
    if (!batches.length) {
      return [
        { title: "درآمد کل", value: "۰ تومان" },
        { title: "کارمزد", value: "۰ تومان" },
        { title: "خالص دریافتی", value: "۰ تومان" },
        { title: "در انتظار تسویه", value: "۰ تومان" },
      ];
    }

    const grossTotal = batches.reduce<number>((sum: number, b: SettlementBatch) => sum + b.gross_amount, 0);
    const commissionTotal = batches.reduce<number>((sum: number, b: SettlementBatch) => sum + b.commission, 0);
    const netTotal = batches.reduce<number>((sum: number, b: SettlementBatch) => sum + b.net_amount, 0);
    const pendingTotal = batches
      .filter((b: SettlementBatch) => b.status === "PENDING" || b.status === "PROCESSING")
      .reduce<number>((sum: number, b: SettlementBatch) => sum + b.net_amount, 0);

    return [
      { title: "درآمد کل", value: formatToman(grossTotal) },
      { title: "کارمزد", value: formatToman(commissionTotal) },
      { title: "خالص دریافتی", value: formatToman(netTotal) },
      { title: "در انتظار تسویه", value: formatToman(pendingTotal) },
    ];
  }, [batches]);

  return (
    <div className="min-h-screen bg-gray-50/50 p-6" dir="rtl">
      <div className="mx-auto max-w-7xl space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">تسویه حساب‌ها</h1>
          <p className="mt-1 text-sm text-gray-500">مشاهده دوره‌های تسویه و جزئیات مالی</p>
        </div>

        {isLoading ? (
          <KPISkeleton />
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {kpis.map((kpi) => (
              <KPICard key={kpi.title} {...kpi} />
            ))}
          </div>
        )}

        <div>
          <h2 className="mb-4 text-lg font-semibold text-gray-900">دوره‌های تسویه</h2>

          {isLoading ? (
            <BatchSkeleton />
          ) : batches.length === 0 ? (
            <EmptyState
              icon={<EmptyBoxIcon />}
              title="تسویه حسابی ثبت نشده"
              description="پس از تسویه دوره‌های مالی، اطلاعات آن‌ها در اینجا نمایش داده می‌شود."
            />
          ) : (
            <div className="flex flex-col gap-3">
              {batches.map((batch) => (
                <div
                  key={batch.id}
                  className="rounded-xl border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex flex-col gap-1">
                      <span className="text-xs text-gray-500">
                        دسته #{batch.batch_number}
                      </span>
                      <span className="text-sm text-gray-500">
                        {toJalali(batch.date)}
                      </span>
                      <span className="text-xs text-gray-400">
                        {batch.items_count} تراکنش
                      </span>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <StatusBadge status={batch.status} />
                    </div>
                  </div>

                  <div className="mt-3 grid grid-cols-3 gap-4 border-t border-gray-100 pt-3">
                    <div>
                      <p className="text-xs text-gray-500">مبلغ ناخالص</p>
                      <p className="text-sm font-semibold text-gray-900">
                        {formatToman(batch.gross_amount)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">کارمزد</p>
                      <p className="text-sm font-semibold text-danger-600">
                        -{formatToman(batch.commission)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">خالص دریافتی</p>
                      <p className="text-sm font-bold text-emerald-600">
                        {formatToman(batch.net_amount)}
                      </p>
                    </div>
                  </div>

                  {batch.settled_date && (
                    <p className="mt-2 text-xs text-gray-400">
                      تسویه شده در {toJalali(batch.settled_date)}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
