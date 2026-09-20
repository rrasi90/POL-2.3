"use client";

import { useApi } from "@/lib/hooks/useApi";
import { StatusBadge, Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import NavIcon from "@/components/ui/NavIcon";
import { Product } from "@/lib/types";

const MOCK_ORDERS = [
  { id: "1", retailer: "فروشگاه زنجیره‌ای رفاه", total: 12_500_000, status: "pending" as const, timeAgo: "۱۰ دقیقه پیش" },
  { id: "2", retailer: "سوپرمارکت پردیس", total: 8_200_000, status: "confirmed" as const, timeAgo: "۲۵ دقیقه پیش" },
  { id: "3", retailer: "هایپرمارکت افق کوروش", total: 45_000_000, status: "shipped" as const, timeAgo: "۱ ساعت پیش" },
  { id: "4", retailer: "فروشگاه خوشه", total: 3_750_000, status: "pending" as const, timeAgo: "۲ ساعت پیش" },
  { id: "5", retailer: "سوپرمارکت جانبو", total: 21_000_000, status: "confirmed" as const, timeAgo: "۳ ساعت پیش" },
];

const STATUS_MAP: Record<string, string> = {
  pending: "در انتظار",
  confirmed: "تأیید شده",
  shipped: "ارسال شده",
  delivered: "تحویل شده",
};

const STATUS_VARIANT: Record<string, "warning" | "info" | "success" | "error"> = {
  pending: "warning",
  confirmed: "info",
  shipped: "success",
  delivered: "success",
};

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

export default function VendorDashboardPage() {
  const { data: catalogData, isLoading: catalogLoading } = useApi<{ data: Product[] }>(
    "/api/v1/vendor/catalog"
  );

  const productCount = catalogData?.data?.length ?? 0;

  const kpis = [
    { title: "سفارشات جدید", value: MOCK_ORDERS.filter((o) => o.status === "pending").length, trend: "۱۲٪ نسبت به دیروز", trendUp: true },
    { title: "درآمد امروز", value: formatToman(MOCK_ORDERS.reduce((s, o) => s + o.total, 0)), trend: "۸٪ نسبت به دیروز", trendUp: true },
    { title: "محصولات فعال", value: catalogLoading ? "..." : productCount, trend: "۳ محصول جدید", trendUp: true },
    { title: "ارسال‌های در انتظار", value: MOCK_ORDERS.filter((o) => o.status === "confirmed").length, trend: "۲ مورد جدید", trendUp: false },
  ];

  return (
    <div className="min-h-screen bg-gray-50/50 p-6" dir="rtl">
      <div className="mx-auto max-w-7xl space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">داشبورد فروشنده</h1>
          <p className="mt-1 text-sm text-gray-500">نمای کلی عملکرد و سفارشات</p>
        </div>

        {catalogLoading ? (
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
            <NavIcon name="package" className="ml-2 h-4 w-4" />
            مدیریت کاتالوگ
          </Button>
          <Button variant="secondary" size="sm">
            <NavIcon name="shopping-cart" className="ml-2 h-4 w-4" />
            مشاهده سفارشات
          </Button>
          <Button variant="secondary" size="sm">
            <NavIcon name="warehouse" className="ml-2 h-4 w-4" />
            مدیریت انبار
          </Button>
        </div>

        <div>
          <h2 className="mb-4 text-lg font-semibold text-gray-900">سفارشات اخیر</h2>
          <div className="space-y-3">
            {MOCK_ORDERS.map((order) => (
              <div
                key={order.id}
                className="flex items-center justify-between rounded-xl border border-gray-100 bg-white p-4 shadow-sm"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 text-sm font-bold text-gray-600">
                    {order.retailer.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{order.retailer}</p>
                    <p className="text-xs text-gray-500">{order.timeAgo}</p>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <span className="text-sm font-bold text-gray-900">
                    {formatToman(order.total)}
                  </span>
                  <StatusBadge status={STATUS_MAP[order.status] ?? order.status} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
