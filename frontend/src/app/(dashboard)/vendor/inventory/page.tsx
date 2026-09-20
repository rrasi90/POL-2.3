"use client";

import { useState, useCallback, useMemo } from "react";
import { useApi } from "@/lib/hooks/useApi";
import { StatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import NavIcon from "@/components/ui/NavIcon";
import { api } from "@/lib/api/client";
import type { InventoryItem } from "@/lib/types";

interface InventoryResponse {
  data: InventoryItem[];
}

interface ConfirmResponse {
  success: boolean;
  message?: string;
}

function toJalali(dateStr: string | null): string {
  if (!dateStr) return "هرگز تایید نشده";
  const d = new Date(dateStr);
  return d.toLocaleDateString("fa-IR-u-nu-latn");
}

function todayJalali(): string {
  return new Date().toLocaleDateString("fa-IR-u-nu-latn", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function TableSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 rounded-xl border border-gray-100 bg-white p-4">
          <div className="h-4 w-40 animate-pulse rounded bg-gray-200" />
          <div className="h-4 w-20 animate-pulse rounded bg-gray-200" />
          <div className="h-4 w-16 animate-pulse rounded bg-gray-200" />
          <div className="h-4 w-32 animate-pulse rounded bg-gray-200" />
          <div className="ml-auto h-8 w-24 animate-pulse rounded bg-gray-200" />
        </div>
      ))}
    </div>
  );
}

export default function VendorInventoryPage() {
  const { data, error, isLoading, mutate } = useApi<InventoryResponse>(
    "/api/v1/vendor/inventory",
  );

  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [confirming, setConfirming] = useState<Record<string, boolean>>({});

  const items = useMemo(() => data?.data ?? [], [data]);

  const getQuantity = useCallback(
    (item: InventoryItem) => {
      return quantities[item.id] ?? item.quantity;
    },
    [quantities],
  );

  const hasChanged = useCallback(
    (item: InventoryItem) => {
      const current = quantities[item.id];
      return current !== undefined && current !== item.quantity;
    },
    [quantities],
  );

  const handleQuantityChange = useCallback((itemId: string, value: string) => {
    const num = parseFloat(value);
    if (!isNaN(num) && num >= 0) {
      setQuantities((prev) => ({ ...prev, [itemId]: num }));
    }
  }, []);

  const handleConfirm = useCallback(
    async (item: InventoryItem) => {
      setConfirming((prev) => ({ ...prev, [item.id]: true }));
      try {
        await api.post<ConfirmResponse>("/api/v1/vendor/inventory/confirm", {
          product_id: item.product_id,
          quantity: getQuantity(item),
        });
        await mutate();
        setQuantities((prev) => {
          const next = { ...prev };
          delete next[item.id];
          return next;
        });
      } catch (err) {
        console.error("Confirm failed:", err);
      } finally {
        setConfirming((prev) => ({ ...prev, [item.id]: false }));
      }
    },
    [getQuantity, mutate],
  );

  const handleConfirmWithChanges = useCallback(
    async (item: InventoryItem) => {
      setConfirming((prev) => ({ ...prev, [item.id]: true }));
      try {
        await api.post<ConfirmResponse>(
          "/api/v1/vendor/inventory/confirm-with-changes",
          {
            product_id: item.product_id,
            quantity: getQuantity(item),
          },
        );
        await mutate();
        setQuantities((prev) => {
          const next = { ...prev };
          delete next[item.id];
          return next;
        });
      } catch (err) {
        console.error("Confirm with changes failed:", err);
      } finally {
        setConfirming((prev) => ({ ...prev, [item.id]: false }));
      }
    },
    [getQuantity, mutate],
  );

  const confirmedCount = items.filter(
    (item) => item.last_confirmed_at !== null,
  ).length;
  const pendingCount = items.length - confirmedCount;

  return (
    <div className="min-h-screen bg-gray-50/50 p-6" dir="rtl">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="flex items-center gap-2 text-2xl font-bold text-gray-900">
              <NavIcon name="clipboard" className="h-6 w-6 text-primary-700" />
              مدیریت انبار
            </h1>
            <p className="mt-1 text-sm text-gray-500">{todayJalali()}</p>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => mutate()}
          >
            <NavIcon name="refresh" className="h-4 w-4" />
            بروزرسانی
          </Button>
        </div>

        {isLoading ? (
          <TableSkeleton />
        ) : error ? (
          <div className="rounded-xl border border-danger-200 bg-danger-50 p-6 text-center">
            <p className="text-sm text-danger-700">
              خطا در بارگذاری اطلاعات انبار. لطفاً دوباره تلاش کنید.
            </p>
            <Button
              variant="secondary"
              size="sm"
              className="mt-3"
              onClick={() => mutate()}
            >
              تلاش مجدد
            </Button>
          </div>
        ) : items.length === 0 ? (
          <div className="rounded-xl border border-gray-100 bg-white p-12 text-center">
            <NavIcon name="package" className="mx-auto mb-4 h-12 w-12 text-gray-300" />
            <p className="text-sm text-gray-500">
              محصولی برای مدیریت انبار یافت نشد.
            </p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto rounded-xl border border-gray-100 bg-white shadow-sm">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100 bg-gray-50/80">
                    <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600">
                      محصول
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600">
                      موجودی فعلی
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600">
                      واحد
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600">
                      آخرین تایید
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600">
                      عملیات
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {items.map((item) => {
                    const currentQty = getQuantity(item);
                    const changed = hasChanged(item);
                    const isConfirming = confirming[item.id];

                    return (
                      <tr
                        key={item.id}
                        className="transition-colors hover:bg-gray-50/50"
                      >
                        <td className="px-4 py-3">
                          <span className="font-medium text-gray-900">
                            {item.product_name}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <input
                            type="number"
                            min={0}
                            value={currentQty}
                            onChange={(e) =>
                              handleQuantityChange(item.id, e.target.value)
                            }
                            className={`w-24 rounded-lg border px-3 py-1.5 text-sm text-gray-900 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                              changed
                                ? "border-warning-300 bg-warning-50 focus:border-warning-400 focus:ring-warning-500"
                                : "border-gray-200 bg-white focus:border-primary-400"
                            }`}
                          />
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {item.unit}
                        </td>
                        <td className="px-4 py-3">
                          {item.last_confirmed_at ? (
                            <span className="text-gray-600">
                              {toJalali(item.last_confirmed_at)}
                            </span>
                          ) : (
                            <StatusBadge status="PENDING" />
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center justify-center gap-2">
                            {changed ? (
                              <Button
                                variant="primary"
                                size="sm"
                                loading={isConfirming}
                                onClick={() => handleConfirmWithChanges(item)}
                              >
                                <NavIcon name="check-circle" className="h-4 w-4" />
                                تایید با تغییرات
                              </Button>
                            ) : (
                              <Button
                                variant="secondary"
                                size="sm"
                                loading={isConfirming}
                                onClick={() => handleConfirm(item)}
                              >
                                <NavIcon name="check-circle" className="h-4 w-4" />
                                تایید
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div className="flex items-center gap-6 rounded-xl border border-gray-100 bg-white px-6 py-4 shadow-sm">
              <div className="flex items-center gap-2">
                <NavIcon name="package" className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-600">
                  کل محصولات:
                </span>
                <span className="text-sm font-bold text-gray-900">
                  {items.length}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <NavIcon name="check-circle" className="h-4 w-4 text-success-500" />
                <span className="text-sm text-gray-600">
                  تایید شده:
                </span>
                <span className="text-sm font-bold text-success-700">
                  {confirmedCount}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <NavIcon name="clock" className="h-4 w-4 text-warning-500" />
                <span className="text-sm text-gray-600">
                  در انتظار تایید:
                </span>
                <span className="text-sm font-bold text-warning-700">
                  {pendingCount}
                </span>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
