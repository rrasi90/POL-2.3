"use client";

import { useState, useMemo, useCallback } from "react";
import { useApi } from "@/lib/hooks/useApi";
import { StatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState, EmptyOrderIcon } from "@/components/ui/EmptyState";
import { api } from "@/lib/api/client";
import type { VendorOrder } from "@/lib/types";

type FilterTab = "new" | "processing" | "completed" | "all";

const STATUS_TABS: { key: FilterTab; label: string }[] = [
  { key: "new", label: "جدید" },
  { key: "processing", label: "در حال پردازش" },
  { key: "completed", label: "تکمیل شده" },
  { key: "all", label: "همه" },
];

const FILTER_STATUS_MAP: Record<FilterTab, string[]> = {
  new: ["SUBMITTED"],
  processing: ["ACCEPTED", "PARTIALLY_ACCEPTED", "PREPARING"],
  completed: ["DELIVERED"],
  all: [],
};

function formatToman(amount: number): string {
  return new Intl.NumberFormat("fa-IR").format(amount) + " تومان";
}

function toJalali(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString("fa-IR-u-nu-latn", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function SkeletonCard() {
  return (
    <div className="animate-pulse rounded-xl border border-gray-200 bg-white p-4">
      <div className="flex items-start justify-between">
        <div className="flex flex-col gap-2">
          <div className="h-4 w-28 rounded bg-gray-200" />
          <div className="h-5 w-40 rounded bg-gray-200" />
          <div className="h-3 w-24 rounded bg-gray-100" />
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className="h-4 w-32 rounded bg-gray-200" />
          <div className="h-5 w-20 rounded-full bg-gray-200" />
        </div>
      </div>
      <div className="mt-3 flex gap-2">
        <div className="h-8 w-20 rounded bg-gray-100" />
        <div className="h-8 w-20 rounded bg-gray-100" />
      </div>
    </div>
  );
}

export default function VendorOrdersPage() {
  const [activeTab, setActiveTab] = useState<FilterTab>("new");
  const [rejectingOrder, setRejectingOrder] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState("");
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const params = useMemo(() => {
    const p: Record<string, string> = { ordering: "-created_at" };
    const statuses = FILTER_STATUS_MAP[activeTab];
    if (statuses.length) p.status = statuses.join(",");
    return p;
  }, [activeTab]);

  const { data, isLoading, mutate } = useApi<{
    results: VendorOrder[];
    count: number;
  }>("/api/v1/vendor/orders", params);

  const orders = data?.results ?? [];

  const handleAccept = useCallback(async (orderId: string) => {
    setActionLoading(orderId);
    try {
      await api.post(`/api/v1/orders/${orderId}/accept`);
      mutate();
    } catch {
      // toast or error state
    } finally {
      setActionLoading(null);
    }
  }, [mutate]);

  const handleReject = useCallback(async () => {
    if (!rejectingOrder) return;
    setActionLoading(rejectingOrder);
    try {
      await api.post(`/api/v1/orders/${rejectingOrder}/reject`, {
        reason: rejectReason,
      });
      setRejectingOrder(null);
      setRejectReason("");
      mutate();
    } catch {
      // toast or error state
    } finally {
      setActionLoading(null);
    }
  }, [rejectingOrder, rejectReason, mutate]);

  const handlePartialAccept = useCallback(async (orderId: string) => {
    setActionLoading(orderId);
    try {
      await api.post(`/api/v1/orders/${orderId}/partial_accept`);
      mutate();
    } catch {
      // toast or error state
    } finally {
      setActionLoading(null);
    }
  }, [mutate]);

  return (
    <div className="flex flex-col gap-6 p-4 md:p-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900">صفحه سفارشات</h1>
        <p className="mt-1 text-sm text-gray-500">مدیریت سفارشات دریافتی از خرده‌فروشان</p>
      </div>

      <div className="flex gap-2 overflow-x-auto">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? "bg-primary-800 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex flex-col gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : orders.length === 0 ? (
        <EmptyState
          icon={<EmptyOrderIcon />}
          title="سفارش جدیدی وجود ندارد"
        />
      ) : (
        <div className="flex flex-col gap-3">
          {orders.map((order) => (
            <div
              key={order.id}
              className="rounded-xl border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex flex-col gap-1">
                  <span className="text-xs text-gray-500">
                    سفارش #{order.order_number}
                  </span>
                  <span className="text-sm font-bold text-gray-900">
                    {order.retailer_name}
                  </span>
                  <span className="text-xs text-gray-500">
                    {order.items_count} کالا · {toJalali(order.created_at)}
                  </span>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span className="text-sm font-bold text-gray-800">
                    {formatToman(order.total_amount_toman)}
                  </span>
                  <StatusBadge status={order.order_status} />
                </div>
              </div>

              {order.order_status === "SUBMITTED" && (
                <div className="mt-3 flex flex-wrap gap-2 border-t border-gray-100 pt-3">
                  <Button
                    variant="primary"
                    size="sm"
                    loading={actionLoading === order.id}
                    onClick={() => handleAccept(order.id)}
                    className="bg-emerald-600 text-white hover:bg-emerald-700"
                  >
                    پذیرش
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    loading={actionLoading === order.id}
                    onClick={() => setRejectingOrder(order.id)}
                  >
                    رد
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    loading={actionLoading === order.id}
                    onClick={() => handlePartialAccept(order.id)}
                  >
                    پذیرش جزئی
                  </Button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {rejectingOrder && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="mx-4 w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
            <h2 className="mb-2 text-lg font-bold text-gray-900">رد سفارش</h2>
            <p className="mb-4 text-sm text-gray-500">
              لطفاً دلیل رد سفارش را وارد کنید.
            </p>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              rows={3}
              placeholder="دلیل رد..."
              className="mb-4 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
            <div className="flex justify-end gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  setRejectingOrder(null);
                  setRejectReason("");
                }}
              >
                انصراف
              </Button>
              <Button
                variant="danger"
                size="sm"
                loading={actionLoading === rejectingOrder}
                onClick={handleReject}
              >
                تایید رد
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
