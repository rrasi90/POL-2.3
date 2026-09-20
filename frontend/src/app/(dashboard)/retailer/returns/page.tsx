"use client";

import { useState, useEffect, useCallback } from "react";
import { useApi } from "@/lib/hooks/useApi";
import { api } from "@/lib/api/client";
import { StatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState, EmptyOrderIcon } from "@/components/ui/EmptyState";

interface ReturnItem {
  id: string;
  product_name: string;
  quantity: number;
  max_quantity: number;
  unit_price_toman: number;
  unit: string;
}

interface ReturnRequest {
  id: string;
  order_id: string;
  order_number: string;
  items: ReturnItem[];
  reason: string;
  status: "PENDING" | "APPROVED" | "REJECTED" | "COMPLETED";
  created_at: string;
}

interface DeliveredOrder {
  id: string;
  order_number: string;
  items: { id: string; product_name: string; quantity: number; unit_price_toman: number; unit: string }[];
  total_amount_toman: number;
  created_at: string;
}

const RETURN_STATUS_LABELS: Record<string, string> = {
  PENDING: "در انتظار بررسی",
  APPROVED: "تایید شده",
  REJECTED: "رد شده",
  COMPLETED: "تکمیل شده",
};

const PAGE_SIZE = 8;

function formatToman(amount: number): string {
  return new Intl.NumberFormat("fa-IR").format(amount) + " تومان";
}

function toJalali(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString("fa-IR-u-nu-latn");
}

export default function RetailerReturnsPage() {
  const [page, setPage] = useState(1);
  const [showModal, setShowModal] = useState(false);

  const { data, isLoading, mutate } = useApi<{
    results: ReturnRequest[];
    count: number;
  }>("/api/v1/returns", { page: String(page), page_size: String(PAGE_SIZE) });

  const returns = data?.results ?? [];
  const totalCount = data?.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  return (
    <div className="flex flex-col gap-6 p-4 md:p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-neutral-900">درخواست بازگشت</h1>
        <Button onClick={() => setShowModal(true)}>ایجاد درخواست بازگشت جدید</Button>
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
      ) : returns.length === 0 ? (
        <EmptyState
          icon={<EmptyOrderIcon />}
          title="درخواست بازگشتی یافت نشد"
          description="هنوز درخواست بازگشتی ثبت نکرده‌اید."
        />
      ) : (
        <>
          <div className="flex flex-col gap-3">
            {returns.map((ret: ReturnRequest) => (
              <div key={ret.id} className="rounded-xl border border-neutral-200 bg-white p-4">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex flex-col gap-1">
                    <span className="text-sm font-semibold text-neutral-900">
                      سفارش #{ret.order_number}
                    </span>
                    <span className="text-xs text-neutral-500">
                      {ret.items.length} کالا · {toJalali(ret.created_at)}
                    </span>
                    <span className="text-xs text-neutral-500 line-clamp-1">{ret.reason}</span>
                  </div>
                  <StatusBadge status={ret.status} />
                </div>
              </div>
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

      {showModal && (
        <CreateReturnModal
          onClose={() => setShowModal(false)}
          onCreated={() => {
            setShowModal(false);
            mutate();
          }}
        />
      )}
    </div>
  );
}

function CreateReturnModal({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: () => void;
}) {
  const [orders, setOrders] = useState<DeliveredOrder[]>([]);
  const [loadingOrders, setLoadingOrders] = useState(true);
  const [selectedOrderId, setSelectedOrderId] = useState("");
  const [selectedItems, setSelectedItems] = useState<Record<string, number>>({});
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoadingOrders(true);
    api
      .get<{ results: DeliveredOrder[] }>("/api/v1/orders", {
        status: "DELIVERED",
        page_size: "50",
      })
      .then((res) => setOrders(res.results ?? []))
      .catch(() => {})
      .finally(() => setLoadingOrders(false));
  }, []);

  const selectedOrder = orders.find((o) => o.id === selectedOrderId);

  const toggleItem = useCallback(
    (itemId: string, maxQty: number) => {
      setSelectedItems((prev) => {
        const next = { ...prev };
        if (next[itemId] !== undefined) {
          delete next[itemId];
        } else {
          next[itemId] = maxQty;
        }
        return next;
      });
    },
    [],
  );

  const updateQuantity = useCallback((itemId: string, qty: number, max: number) => {
    const clamped = Math.max(1, Math.min(qty, max));
    setSelectedItems((prev) => ({ ...prev, [itemId]: clamped }));
  }, []);

  const handleSubmit = async () => {
    if (!selectedOrderId || Object.keys(selectedItems).length === 0 || !reason.trim()) {
      setError("لطفاً تمام فیلدها را پر کنید.");
      return;
    }

    setSubmitting(true);
    setError("");

    const items = Object.entries(selectedItems).map(([item_id, quantity]) => ({
      item_id,
      quantity,
    }));

    try {
      await api.post(`/api/v1/orders/${selectedOrderId}/returns`, {
        items,
        reason: reason.trim(),
      });
      onCreated();
    } catch (err: any) {
      setError(err.message || "خطا در ارسال درخواست.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" dir="rtl">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl max-h-[90vh] overflow-y-auto">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-neutral-900">ایجاد درخواست بازگشت</h2>
          <button onClick={onClose} className="text-neutral-400 hover:text-neutral-600">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex flex-col gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-neutral-700">انتخاب سفارش</label>
            {loadingOrders ? (
              <div className="h-10 animate-pulse rounded-lg bg-neutral-100" />
            ) : (
              <select
                value={selectedOrderId}
                onChange={(e) => {
                  setSelectedOrderId(e.target.value);
                  setSelectedItems({});
                }}
                className="w-full rounded-lg border border-neutral-300 bg-white px-3 py-2 text-sm text-neutral-700 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              >
                <option value="">-- انتخاب سفارش --</option>
                {orders.map((o) => (
                  <option key={o.id} value={o.id}>
                    سفارش #{o.order_number} — {formatToman(o.total_amount_toman)}
                  </option>
                ))}
              </select>
            )}
          </div>

          {selectedOrder && (
            <div>
              <label className="mb-1 block text-sm font-medium text-neutral-700">انتخاب کالاها</label>
              <div className="flex flex-col gap-2 rounded-lg border border-neutral-200 p-3">
                {selectedOrder.items.map((item) => {
                  const checked = selectedItems[item.id] !== undefined;
                  return (
                    <div key={item.id} className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleItem(item.id, item.quantity)}
                        className="h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                      />
                      <div className="flex-1">
                        <span className="text-sm text-neutral-800">{item.product_name}</span>
                        <span className="mr-2 text-xs text-neutral-400">
                          (حداکثر {item.quantity} {item.unit})
                        </span>
                      </div>
                      {checked && (
                        <input
                          type="number"
                          min={1}
                          max={item.quantity}
                          value={selectedItems[item.id]}
                          onChange={(e) =>
                            updateQuantity(item.id, parseInt(e.target.value) || 1, item.quantity)
                          }
                          className="w-16 rounded border border-neutral-300 px-2 py-1 text-center text-sm focus:border-primary-500 focus:outline-none"
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <div>
            <label className="mb-1 block text-sm font-medium text-neutral-700">دلیل بازگشت</label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              placeholder="دلیل بازگشت کالاها را توضیح دهید..."
              className="w-full rounded-lg border border-neutral-300 bg-white px-3 py-2 text-sm text-neutral-700 placeholder:text-neutral-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>

          {error && <p className="text-sm text-danger-600">{error}</p>}

          <div className="flex gap-3 pt-2">
            <Button variant="secondary" onClick={onClose} className="flex-1">
              انصراف
            </Button>
            <Button
              onClick={handleSubmit}
              loading={submitting}
              disabled={!selectedOrderId || Object.keys(selectedItems).length === 0 || !reason.trim()}
              className="flex-1"
            >
              ارسال درخواست
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
