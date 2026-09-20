"use client";

import { use } from "react";
import { useApi } from "@/lib/hooks/useApi";
import { StatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import NavIcon from "@/components/ui/NavIcon";
import Link from "next/link";
import type { Order, OrderItem, OrderEvent } from "@/lib/types";

const STEPS = [
  { key: "CREATED", label: "ایجاد شده" },
  { key: "SUBMITTED", label: "ارسال شده" },
  { key: "ACCEPTED", label: "تایید شده" },
  { key: "PREPARING", label: "آماده‌سازی" },
  { key: "DISPATCHED", label: "ارسال شده" },
  { key: "DELIVERED", label: "تحویل شده" },
] as const;

const STEP_ORDER = STEPS.map((s) => s.key);

const ACTIONABLE_STATUSES: Record<string, { label: string; variant: "danger" | "secondary" | "ghost" }[]> = {
  CREATED: [{ label: "لغو سفارش", variant: "danger" }],
  SUBMITTED: [
    { label: "لغو سفارش", variant: "danger" },
    { label: "درخواست بازگشت", variant: "secondary" },
  ],
  ACCEPTED: [
    { label: "لغو سفارش", variant: "danger" },
    { label: "درخواست بازگشت", variant: "secondary" },
  ],
  PREPARING: [
    { label: "درخواست بازگشت", variant: "secondary" },
    { label: "اعتراض", variant: "ghost" },
  ],
  DISPATCHED: [
    { label: "درخواست بازگشت", variant: "secondary" },
    { label: "اعتراض", variant: "ghost" },
  ],
  DELIVERED: [{ label: "درخواست بازگشت", variant: "secondary" }],
};

function formatToman(amount: number): string {
  return new Intl.NumberFormat("fa-IR").format(amount) + " تومان";
}

function toJalaliFull(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString("fa-IR-u-nu-latn", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getStepIndex(status: string): number {
  const idx = STEP_ORDER.indexOf(status as (typeof STEP_ORDER)[number]);
  return idx >= 0 ? idx : 0;
}

function Stepper({ currentStatus }: { currentStatus: string }) {
  const currentIdx = getStepIndex(currentStatus);

  return (
    <div className="flex flex-col gap-0 sm:flex-row sm:items-center">
      {STEPS.map((step, i) => {
        const isPast = i < currentIdx;
        const isCurrent = i === currentIdx;
        const isFuture = i > currentIdx;

        return (
          <div key={step.key} className="flex items-center sm:flex-col">
            <div className="flex items-center gap-2 sm:flex-col sm:gap-1">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold transition-colors ${
                  isPast
                    ? "bg-primary-600 text-white"
                    : isCurrent
                      ? "bg-primary-800 text-white ring-4 ring-primary-200"
                      : "bg-neutral-200 text-neutral-500"
                }`}
              >
                {isPast ? (
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  i + 1
                )}
              </div>
              <span
                className={`text-xs font-medium ${
                  isFuture ? "text-neutral-400" : "text-neutral-700"
                }`}
              >
                {step.label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div
                className={`mx-1 h-0.5 w-6 sm:mx-0 sm:my-1 sm:h-0.5 sm:w-0.5 sm:flex-1 ${
                  isPast ? "bg-primary-600" : "bg-neutral-200"
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

function VendorSection({ vendorName, items }: { vendorName: string; items: OrderItem[] }) {
  const vendorTotal = items.reduce((sum, item) => sum + item.unit_price_toman * item.quantity, 0);

  return (
    <div className="rounded-xl border border-neutral-200 bg-white">
      <div className="flex items-center justify-between border-b border-neutral-100 px-4 py-3">
        <span className="text-sm font-semibold text-neutral-800">{vendorName}</span>
        <span className="text-xs text-neutral-500">{items.length} کالا</span>
      </div>
      <div className="divide-y divide-neutral-100">
        {items.map((item) => (
          <div key={item.id} className="flex items-center justify-between px-4 py-3">
            <div className="flex flex-col gap-0.5">
              <span className="text-sm font-medium text-neutral-800">{item.product_name}</span>
              <span className="text-xs text-neutral-500">
                {new Intl.NumberFormat("fa-IR").format(item.quantity)} ×{" "}
                {formatToman(item.unit_price_toman)}
              </span>
            </div>
            <span className="text-sm font-semibold text-neutral-700">
              {formatToman(item.unit_price_toman * item.quantity)}
            </span>
          </div>
        ))}
      </div>
      <div className="flex items-center justify-between border-t border-neutral-100 bg-neutral-50 px-4 py-2.5">
        <span className="text-xs text-neutral-500">جمع فروشنده</span>
        <span className="text-sm font-bold text-neutral-800">{formatToman(vendorTotal)}</span>
      </div>
    </div>
  );
}

function Timeline({ events }: { events: OrderEvent[] }) {
  if (!events.length) return null;

  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-bold text-neutral-900">سابقه سفارش</h3>
      <div className="flex flex-col gap-0">
        {events.map((event, i) => (
          <div key={event.id} className="flex gap-3">
            <div className="flex flex-col items-center">
              <div className="h-2.5 w-2.5 rounded-full bg-primary-500" />
              {i < events.length - 1 && <div className="w-px flex-1 bg-neutral-200" />}
            </div>
            <div className="flex flex-col gap-0.5 pb-4">
              <span className="text-xs text-neutral-500">{toJalaliFull(event.created_at)}</span>
              <span className="text-sm text-neutral-700">{event.description}</span>
              {event.actor_name && (
                <span className="text-xs text-neutral-400">{event.actor_name}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function OrderDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: order, isLoading } = useApi<Order>(`/api/v1/orders/${id}`);

  if (isLoading) {
    return (
      <div className="flex flex-col gap-4 p-4 md:p-6">
        <div className="animate-pulse">
          <div className="mb-4 h-4 w-40 rounded bg-neutral-200" />
          <div className="mb-6 h-8 w-64 rounded bg-neutral-200" />
          <div className="mb-6 flex gap-2">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="flex flex-col items-center gap-1">
                <div className="h-8 w-8 rounded-full bg-neutral-200" />
                <div className="h-3 w-12 rounded bg-neutral-200" />
              </div>
            ))}
          </div>
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="mb-4 h-40 rounded-xl bg-neutral-100" />
          ))}
        </div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-neutral-500">
        سفارش یافت نشد
      </div>
    );
  }

  const vendorGroups = (order.items ?? []).reduce<Record<string, OrderItem[]>>((acc, item) => {
    const key = item.vendor_name || "نامشخص";
    if (!acc[key]) acc[key] = [];
    acc[key].push(item);
    return acc;
  }, {});

  const actions = ACTIONABLE_STATUSES[order.order_status] || [];

  return (
    <div className="flex flex-col gap-6 p-4 md:p-6">
      <Link
        href="/retailer/orders"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-primary-600 hover:text-primary-700"
      >
        <NavIcon name="arrow-right" className="h-4 w-4" />
        بازگشت به سفارشات
      </Link>

      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold text-neutral-900">سفارش #{order.order_number}</h1>
          <p className="text-sm text-neutral-500">{toJalaliFull(order.created_at)}</p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status={order.order_status} />
          <span className="text-lg font-bold text-neutral-800">{formatToman(order.total_amount_toman)}</span>
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-neutral-200 bg-white p-4">
        <Stepper currentStatus={order.order_status} />
      </div>

      <div className="flex flex-col gap-4">
        {Object.entries(vendorGroups).map(([vendorName, items]) => (
          <VendorSection key={vendorName} vendorName={vendorName} items={items} />
        ))}
      </div>

      {order.timeline && order.timeline.length > 0 && (
        <Timeline events={order.timeline} />
      )}

      {actions.length > 0 && (
        <div className="flex flex-wrap gap-3 border-t border-neutral-200 pt-4">
          {actions.map((action) => (
            <Button
              key={action.label}
              variant={action.variant as "danger" | "secondary" | "ghost"}
            >
              {action.label}
            </Button>
          ))}
        </div>
      )}
    </div>
  );
}
