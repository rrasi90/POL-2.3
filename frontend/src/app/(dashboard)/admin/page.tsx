"use client";

import { useApi } from "@/lib/hooks/useApi";
import { StatusBadge } from "@/components/ui/Badge";
import type { User, UserRole, Organization } from "@/lib/types";

function formatToman(value: number): string {
  return new Intl.NumberFormat("fa-IR").format(value) + " تومان";
}

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

const ROLE_LABELS: Record<UserRole, string> = {
  ADMIN_SUPER: "مدیر ارشد",
  OPS_AGENT: "کارشناس عملیات",
  FIELD_ACTIVATOR: "فعال‌ساز میدانی",
  VENDOR_OWNER: "مالک فروشنده",
  VENDOR_STAFF: "کارمند فروشنده",
  RETAILER_OWNER: "مالک خرده‌فروش",
  RETAILER_STAFF: "کارمند خرده‌فروش",
};

function UserSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
          <div className="h-10 w-10 animate-pulse rounded-full bg-gray-200" />
          <div className="flex-1 space-y-2">
            <div className="h-4 w-32 animate-pulse rounded bg-gray-200" />
            <div className="h-3 w-24 animate-pulse rounded bg-gray-100" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function AdminDashboardPage() {
  const { data: usersData, isLoading: usersLoading } = useApi<{ data: User[] }>(
    "/api/v1/admin/users"
  );
  const { data: orgsData, isLoading: orgsLoading } = useApi<{ data: Organization[] }>(
    "/api/v1/admin/organizations"
  );

  const users = usersData?.data ?? [];
  const orgs = orgsData?.data ?? [];

  const kpis = [
    { title: "کل کاربران", value: usersLoading ? "..." : users.length, trend: "۵ کاربر جدید", trendUp: true },
    { title: "کل سازمان‌ها", value: orgsLoading ? "..." : orgs.length, trend: "۲ سازمان جدید", trendUp: true },
    { title: "سفارشات امروز", value: 47, trend: "۱۲٪ نسبت به دیروز", trendUp: true },
    { title: "درآمد کل", value: formatToman(2_580_000_000), trend: "۸٪ نسبت به دیروز", trendUp: true },
  ];

  return (
    <div className="min-h-screen bg-gray-50/50 p-6" dir="rtl">
      <div className="mx-auto max-w-7xl space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">داشبورد مدیریت</h1>
          <p className="mt-1 text-sm text-gray-500">نمای کلی عملکرد پلتفرم و مدیریت منابع</p>
        </div>

        {usersLoading || orgsLoading ? (
          <KPISkeleton />
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {kpis.map((kpi) => (
              <KPICard key={kpi.title} {...kpi} />
            ))}
          </div>
        )}

        <div>
          <h2 className="mb-4 text-lg font-semibold text-gray-900">کاربران اخیر</h2>
          {usersLoading ? (
            <UserSkeleton />
          ) : (
            <div className="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
              <table className="w-full text-right text-sm">
                <thead>
                  <tr className="border-b border-gray-100 bg-gray-50/50">
                    <th className="px-4 py-3 font-medium text-gray-500">نام</th>
                    <th className="px-4 py-3 font-medium text-gray-500">نقش</th>
                    <th className="px-4 py-3 font-medium text-gray-500">سازمان</th>
                    <th className="px-4 py-3 font-medium text-gray-500">وضعیت</th>
                    <th className="px-4 py-3 font-medium text-gray-500">آخرین ورود</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {users.slice(0, 10).map((user) => (
                    <tr key={user.id} className="transition-colors hover:bg-gray-50/50">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-xs font-bold text-primary-700">
                            {user.full_name?.charAt(0) ?? "?"}
                          </div>
                          <span className="font-medium text-gray-900">{user.full_name ?? "—"}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-gray-600">{ROLE_LABELS[user.role]}</td>
                      <td className="px-4 py-3 text-gray-600">—</td>
                      <td className="px-4 py-3">
                        <StatusBadge
                          status={user.is_active ? "فعال" : "غیرفعال"}
                        />
                      </td>
                      <td className="px-4 py-3 text-gray-500">—</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
