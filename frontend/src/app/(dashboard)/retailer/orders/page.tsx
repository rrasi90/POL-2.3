"use client";

import { useState, useMemo } from "react";
import { useApi } from "@/lib/hooks/useApi";
import { StatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState, EmptyOrderIcon } from "@/components/ui/EmptyState";
import Link from "next/link";
import type { Order, OrderStatus } from "@/lib/types";

const STATUS_TABS: { key: string; label: string }[] = [
  { key: "all", label: "همه" },
  { key: "active", label: "فعال" },
  { key: "completed", label: "تکمیل شده" },
  { key: "cancelled", label: "لغو شده" },
];

const SORT_OPTIONS: { key: string; label: string }[] = [
  { key: "newest", label: "جدیدترین" },
  { key: "oldest", label: "قدیمی‌ترین" },
  { key: "highest", label: "بیشترین مبلغ" },
];

const STATUS_MAP: Record<string, OrderStatus[]> = {
  all: [],
  active: ["CREATED", "SUBMITTED", "ACCEPTED", "PREPARING", "DISPATCHED"],
  completed: ["DELIVERED"],
  cancelled: ["CANCELLED"],
};

const PAGE_SIZE = 8;

function formatToman(amount: number): string {
  return new Intl.NumberFormat("fa-IR").format(amount) + " تومان";
}

function toJalali(dateStr: string): string {
  const d = new Date(dateStr);
  const jd = d.toLocaleDateString("fa-IR-u-nu-latn");
  return jd;
}

export default function RetailerOrdersPage() {
  const [activeTab, setActiveTab] = useState("all");
  const [sort, setSort] = useState("newest");
  const [page, setPage] = useState(1);

  const params = useMemo(() => {
    const p: Record<string, string> = { page: String(page), page_size: String(PAGE_SIZE) };
    if (activeTab !== "all") {
      const statuses = STATUS_MAP[activeTab];
      if (statuses.length) p.status = statuses.join(",");
    }
    if (sort === "oldest") p.ordering = "created_at";
    else if (sort === "highest") p.ordering = "-total_amount";
    else p.ordering = "-created_at";
    return p;
  }, [activeTab, sort, page]);

  const { data, isLoading } = useApi<{
    results: Order[];
    count: number;
  }>("/api/v1/orders", params);

  const orders = data?.results ?? [];
  const totalCount = data?.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  return (
    <div className="flex flex-col gap-6 p-4 md:p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-xl font-bold text-neutral-900">سفارشات</h1>
        <div className="relative">
          <select
            value={sort}
            onChange={(e) => {
              setSort(e.target.value);
              setPage(1);
            }}
            className="appearance-none rounded-lg border border-neutral-300 bg-white px-4 py-2 pl-10 text-sm text-neutral-700 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            {SORT_OPTIONS.map((o) => (
              <option key={o.key} value={o.key}>
                {o.label}
              </option>
            ))}
          </select>
          <svg
            className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      <div className="flex gap-2 overflow-x-auto">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => {
              setActiveTab(tab.key);
              setPage(1);
            }}
            className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? "bg-primary-600 text-white"
                : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex flex-col gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="animate-pulse rounded-xl border border-neutral-200 bg-white p-4">
              <div className="flex items-center justify-between">
                <div className="flex flex-col gap-2">
                  <div className="h-4 w-32 rounded bg-neutral-200" />
                  <div className="h-3 w-48 rounded bg-neutral-200" />
                </div>
                <div className="flex flex-col items-end gap-2">
                  <div className="h-4 w-24 rounded bg-neutral-200" />
                  <div className="h-5 w-20 rounded-full bg-neutral-200" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : orders.length === 0 ? (
        <EmptyState
          icon={<EmptyOrderIcon />}
          title="سفارشی یافت نشد"
          description="هنوز سفارشی ثبت نکرده‌اید."
        />
      ) : (
        <>
          <div className="flex flex-col gap-3">
            {orders.map((order) => (
              <Link key={order.id} href={`/retailer/orders/${order.id}`}>
                <div className="cursor-pointer rounded-xl border border-neutral-200 bg-white p-4 transition-shadow hover:shadow-md">
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-neutral-900">
                          سفارش #{order.order_number}
                        </span>
                      </div>
                      <span className="text-xs text-neutral-500">
                        {toJalali(order.created_at)} · {order.vendor_count} فروشنده
                      </span>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <span className="text-sm font-bold text-neutral-800">
                        {formatToman(order.total_amount_toman)}
                      </span>
                      <StatusBadge status={order.order_status} />
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                قبلی
              </Button>
              <span className="px-3 text-sm text-neutral-600">
                صفحه {page} از {totalPages}
              </span>
              <Button
                variant="secondary"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                بعدی
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
