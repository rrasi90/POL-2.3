"use client";

import { useApi } from "@/lib/hooks/useApi";
import { StatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import NavIcon from "@/components/ui/NavIcon";
import type { SupportCase, FieldTask } from "@/lib/types";

const SUPPORT_STATUS_MAP: Record<string, string> = {
  OPEN: "باز",
  IN_PROGRESS: "در حال بررسی",
  WAITING_ON_VENDOR: "در انتظار فروشنده",
  WAITING_ON_USER: "در انتظار کاربر",
  RESOLVED: "حل شده",
  CLOSED: "بسته شده",
};

const SUPPORT_STATUS_VARIANT: Record<string, "warning" | "info" | "success" | "error"> = {
  OPEN: "error",
  IN_PROGRESS: "warning",
  WAITING_ON_VENDOR: "info",
  WAITING_ON_USER: "info",
  RESOLVED: "success",
  CLOSED: "success",
};

const FIELD_STATUS_MAP: Record<string, string> = {
  ASSIGNED: "تخصیص داده شده",
  IN_PROGRESS: "در حال انجام",
  COMPLETED: "تکمیل شده",
  FAILED: "ناموفق",
  CANCELLED: "لغو شده",
};

const FIELD_STATUS_VARIANT: Record<string, "warning" | "info" | "success" | "error"> = {
  ASSIGNED: "info",
  IN_PROGRESS: "warning",
  COMPLETED: "success",
  FAILED: "error",
  CANCELLED: "error",
};

function KPISkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
          <div className="mb-3 h-3 w-24 animate-pulse rounded bg-gray-200" />
          <div className="mb-2 h-7 w-20 animate-pulse rounded bg-gray-200" />
          <div className="h-3 w-16 animate-pulse rounded bg-gray-100" />
        </div>
      ))}
    </div>
  );
}

interface KPICardProps {
  title: string;
  value: string | number;
  trend?: string;
  trendUp?: boolean;
}

function KPICard({ title, value, trend, trendUp }: KPICardProps) {
  return (
    <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
      <p className="mb-3 text-xs text-gray-500">{title}</p>
      <p className="mb-1 text-[28px] font-bold leading-none text-gray-900">{value}</p>
      {trend && (
        <p className={`text-xs font-medium ${trendUp ? "text-emerald-600" : "text-red-500"}`}>
          {trendUp ? "↑" : "↓"} {trend}
        </p>
      )}
    </div>
  );
}

function ListSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
          <div className="h-10 w-10 animate-pulse rounded-full bg-gray-200" />
          <div className="flex-1 space-y-2">
            <div className="h-4 w-40 animate-pulse rounded bg-gray-200" />
            <div className="h-3 w-24 animate-pulse rounded bg-gray-100" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function OpsDashboardPage() {
  const { data: casesData, isLoading: casesLoading } = useApi<{ data: SupportCase[] }>(
    "/api/v1/ops/support-cases"
  );
  const { data: tasksData, isLoading: tasksLoading } = useApi<{ data: FieldTask[] }>(
    "/api/v1/ops/field-tasks"
  );

  const cases = casesData?.data ?? [];
  const tasks = tasksData?.data ?? [];

  const openCases = cases.filter((c) => c.status === "OPEN" || c.status === "IN_PROGRESS").length;
  const activeTasks = tasks.filter((t) => t.status === "ASSIGNED" || t.status === "IN_PROGRESS").length;
  const pendingPayments = 12;
  const disputes = cases.filter((c) => c.priority === "CRITICAL").length;

  const kpis = [
    { title: "پرونده‌های باز", value: casesLoading ? "..." : openCases, trend: "۳ مورد جدید", trendUp: false },
    { title: "تسک‌های فعال", value: tasksLoading ? "..." : activeTasks, trend: "۲ تسک جدید", trendUp: true },
    { title: "پرداخت‌های در انتظار", value: pendingPayments, trend: "۵ مورد تأیید شده", trendUp: true },
    { title: "اختلافات", value: disputes, trend: "۱ مورد بحرانی", trendUp: false },
  ];

  return (
    <div className="min-h-screen bg-gray-50/50 p-6" dir="rtl">
      <div className="mx-auto max-w-7xl space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">داشبورد عملیات</h1>
          <p className="mt-1 text-sm text-gray-500">مدیریت پشتیبانی، تسک‌های میدانی و پرداخت‌ها</p>
        </div>

        {casesLoading || tasksLoading ? (
          <KPISkeleton />
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {kpis.map((kpi) => (
              <KPICard key={kpi.title} {...kpi} />
            ))}
          </div>
        )}

        <div className="flex flex-wrap gap-3">
          <Button variant="secondary" size="sm">
            <NavIcon name="headphones" className="ml-2 h-4 w-4" />
            پشتیبانی
          </Button>
          <Button variant="secondary" size="sm">
            <NavIcon name="map-pin" className="ml-2 h-4 w-4" />
            تسک‌های میدانی
          </Button>
          <Button variant="secondary" size="sm">
            <NavIcon name="credit-card" className="ml-2 h-4 w-4" />
            پرداخت‌ها
          </Button>
          <Button variant="secondary" size="sm">
            <NavIcon name="alert-triangle" className="ml-2 h-4 w-4" />
            اختلافات
          </Button>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div>
            <h2 className="mb-4 text-lg font-semibold text-gray-900">پرونده‌های پشتیبانی اخیر</h2>
            {casesLoading ? (
              <ListSkeleton />
            ) : cases.length === 0 ? (
              <div className="rounded-xl border border-gray-100 bg-white p-8 text-center text-sm text-gray-400 shadow-sm">
                پرونده‌ای یافت نشد
              </div>
            ) : (
              <div className="space-y-3">
                {cases.slice(0, 5).map((sc) => (
                  <div
                    key={sc.id}
                    className="flex items-center justify-between rounded-xl border border-gray-100 bg-white p-4 shadow-sm"
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-50 text-sm font-bold text-red-600">
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                        </svg>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{sc.subject}</p>
                        <p className="text-xs text-gray-500">{sc.priority === "CRITICAL" ? "بحرانی" : sc.priority === "HIGH" ? "بالا" : "عادی"}</p>
                      </div>
                    </div>
                    <StatusBadge
                      status={SUPPORT_STATUS_MAP[sc.status] ?? sc.status}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>

          <div>
            <h2 className="mb-4 text-lg font-semibold text-gray-900">تسک‌های میدانی اخیر</h2>
            {tasksLoading ? (
              <ListSkeleton />
            ) : tasks.length === 0 ? (
              <div className="rounded-xl border border-gray-100 bg-white p-8 text-center text-sm text-gray-400 shadow-sm">
                تسکی یافت نشد
              </div>
            ) : (
              <div className="space-y-3">
                {tasks.slice(0, 5).map((task) => (
                  <div
                    key={task.id}
                    className="flex items-center justify-between rounded-xl border border-gray-100 bg-white p-4 shadow-sm"
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-50 text-sm font-bold text-blue-600">
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
                        </svg>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{task.retailer_name ?? task.vendor_name ?? task.task_type}</p>
                        <p className="text-xs text-gray-500">{task.location ?? "—"}</p>
                      </div>
                    </div>
                    <StatusBadge
                      status={FIELD_STATUS_MAP[task.status] ?? task.status}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
