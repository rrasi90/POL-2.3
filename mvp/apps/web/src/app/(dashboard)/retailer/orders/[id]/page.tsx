"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Button,
  EmptyState,
  ErrorState,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  disputeLabel,
  disputeTone,
  formatDateTime,
  formatToman,
  groupStatusLabel,
  groupStatusTone,
  orderStatusTone,
  orderStatusLabel,
} from "../../shared";

interface OrderDetail {
  id: string;
  order_number?: string | null;
  order_status?: string | null;
  dispute_status?: string | null;
  total_amount_toman?: number | null;
  order_group_id?: string | null;
  group_status?: string | null;
  group_total_toman?: number | null;
  group_order_count?: number | null;
  vendor_id?: string | null;
  retailer_id?: string | null;
  basket_id?: string | null;
  allocation_plan_id?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  delivery_address?: string | null;
  address_snapshot?: unknown;
}

interface OrderItem {
  id: string;
  product_id?: string | null;
  product_name_snapshot?: string | null;
  brand_name_snapshot?: string | null;
  vendor_sku_snapshot?: string | null;
  packaging_unit_snapshot?: string | null;
  pack_quantity_snapshot?: number | null;
  ordered_quantity?: number | null;
  accepted_quantity?: number | null;
  delivered_quantity?: number | null;
  unit_price_toman?: number | null;
  total_line_amount_toman?: number | null;
  fulfillment_status?: string | null;
  dispute_reason?: string | null;
}

interface TimelineEvent {
  id: string;
  event_type?: string | null;
  from_status?: string | null;
  to_status?: string | null;
  actor_user_id?: string | null;
  created_at?: string | null;
  event_data?: unknown;
}

type LoadState = "loading" | "error" | "ready";

function asArray<T>(raw: unknown, key?: string): T[] {
  if (Array.isArray(raw)) return raw as T[];
  if (raw && typeof raw === "object") {
    const obj = raw as Record<string, unknown>;
    if (key && Array.isArray(obj[key])) return obj[key] as T[];
    if (Array.isArray(obj.items)) return obj.items as T[];
    if (Array.isArray(obj.events)) return obj.events as T[];
    if (Array.isArray(obj.data)) return obj.data as T[];
  }
  return [];
}

/**
 * R-09B child order detail: GET /orders/{id}, /items, /timeline.
 */
export default function RetailerOrderDetailPage() {
  const params = useParams<{ id: string }>();
  const orderId = params.id;

  const [order, setOrder] = useState<OrderDetail | null>(null);
  const [items, setItems] = useState<OrderItem[]>([]);
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!orderId) return;
    setState("loading");
    setErrorMessage(null);
    try {
      const [o, it, tl] = await Promise.all([
        getApi().get<OrderDetail>(`/api/v1/orders/${orderId}`),
        getApi().get<unknown>(`/api/v1/orders/${orderId}/items`),
        getApi().get<unknown>(`/api/v1/orders/${orderId}/timeline`),
      ]);
      setOrder(o);
      setItems(asArray<OrderItem>(it, "items"));
      setEvents(asArray<TimelineEvent>(tl, "events"));
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت سفارش ناموفق بود");
      setState("error");
    }
  }, [orderId]);

  useEffect(() => {
    void load();
  }, [load]);

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری سفارش">
        <Skeleton className="h-8 w-64" />
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <Skeleton lines={3} />
        </div>
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <Skeleton lines={4} />
        </div>
      </div>
    );
  }

  if (state === "error" || !order) {
    return (
      <ErrorState
        title="دریافت سفارش ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-start gap-3">
        <div>
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            جزئیات سفارش
          </h1>
          <p className="mt-1 flex flex-wrap items-center gap-2">
            <span className="text-[13px] text-[var(--pol-light-text-secondary)]" dir="ltr">
              {order.order_number ?? order.id}
            </span>
            <span className="text-[11px] text-[var(--pol-light-text-muted)]">
              {formatDateTime(order.created_at)}
            </span>
          </p>
        </div>
        <div className="ms-auto flex flex-wrap gap-2">
          <Button variant="ghost" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
        </div>
      </header>

      <section
        aria-label="وضعیت‌ها"
        className="flex flex-wrap items-center gap-2 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
      >
        <StatusChip tone={orderStatusTone[order.order_status ?? ""] ?? "neutral"}>
          {orderStatusLabel[order.order_status ?? ""] ?? order.order_status ?? "—"}
        </StatusChip>
        {order.group_status ? (
          <StatusChip tone={groupStatusTone[order.group_status] ?? "neutral"}>
            گروه: {groupStatusLabel[order.group_status] ?? order.group_status}
          </StatusChip>
        ) : null}
        <StatusChip tone={disputeTone[order.dispute_status ?? "NONE"] ?? "neutral"}>
          {disputeLabel[order.dispute_status ?? "NONE"] ?? order.dispute_status ?? ""}
        </StatusChip>
        <span className="ms-auto text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
          {formatToman(order.total_amount_toman)}
        </span>
      </section>

      <div className="flex flex-wrap gap-2">
        {order.order_group_id ? (
          <Link
            href={`/retailer/orders/group/${order.order_group_id}`}
            className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
          >
            نمایش گروه سفارش
            {order.group_order_count != null
              ? ` (${order.group_order_count.toLocaleString("fa-IR")})`
              : ""}
          </Link>
        ) : null}
        <Link
          href={`/retailer/orders/${order.id}/returns`}
          className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
        >
          بازگشت کالا و اختلاف
        </Link>
        <Link
          href="/retailer/support"
          className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
        >
          پشتیبانی
        </Link>
      </div>

      <section aria-label="اقلام سفارش">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          اقلام
        </h2>
        {items.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="قلمی برای این سفارش ثبت نشده" />
          </div>
        ) : (
          <div className="mt-3 overflow-x-auto rounded-[12px] border border-[var(--pol-light-border-subtle)]">
            <table className="w-full min-w-[640px] border-collapse bg-[var(--pol-light-surface-default)] text-[13px]">
              <thead>
                <tr className="border-b border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] text-[12px] text-[var(--pol-light-text-secondary)]">
                  <th className="px-4 py-2 text-start font-medium">کالا</th>
                  <th className="px-4 py-2 text-start font-medium">سفارش</th>
                  <th className="px-4 py-2 text-start font-medium">پذیرفته</th>
                  <th className="px-4 py-2 text-start font-medium">تحویل</th>
                  <th className="px-4 py-2 text-start font-medium">واحد</th>
                  <th className="px-4 py-2 text-start font-medium">مبلغ</th>
                </tr>
              </thead>
              <tbody>
                {items.map((it) => (
                  <tr
                    key={it.id}
                    className="border-b border-[var(--pol-light-border-subtle)] last:border-b-0"
                  >
                    <td className="px-4 py-3">
                      <span className="text-[var(--pol-light-text-primary)]">
                        {it.product_name_snapshot ?? "—"}
                      </span>
                      {it.brand_name_snapshot ? (
                        <span className="ms-1 text-[11px] text-[var(--pol-light-text-muted)]">
                          {it.brand_name_snapshot}
                        </span>
                      ) : null}
                      {it.fulfillment_status ? (
                        <span className="ms-2">
                          <StatusChip tone="info">{it.fulfillment_status}</StatusChip>
                        </span>
                      ) : null}
                    </td>
                    <td className="px-4 py-3 text-[var(--pol-light-text-primary)]">
                      {Number(it.ordered_quantity ?? 0).toLocaleString("fa-IR")}
                    </td>
                    <td className="px-4 py-3 text-[var(--pol-light-text-secondary)]">
                      {it.accepted_quantity != null
                        ? Number(it.accepted_quantity).toLocaleString("fa-IR")
                        : "—"}
                    </td>
                    <td className="px-4 py-3 text-[var(--pol-light-text-secondary)]">
                      {it.delivered_quantity != null
                        ? Number(it.delivered_quantity).toLocaleString("fa-IR")
                        : "—"}
                    </td>
                    <td className="px-4 py-3 text-[var(--pol-light-text-secondary)]">
                      {it.packaging_unit_snapshot ?? "—"}
                      {it.pack_quantity_snapshot
                        ? ` ×${it.pack_quantity_snapshot.toLocaleString("fa-IR")}`
                        : ""}
                    </td>
                    <td className="px-4 py-3 text-[var(--pol-light-text-primary)]">
                      {formatToman(it.total_line_amount_toman)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section aria-label="خط زمانی سفارش">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          خط زمانی
        </h2>
        {events.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="رویدادی ثبت نشده" description="هنوز رویدادی برای این سفارش وجود ندارد." />
          </div>
        ) : (
          <ol className="mt-3 space-y-0 border-s-2 border-[var(--pol-light-border-subtle)] ps-4">
            {events.map((ev) => (
              <li key={ev.id} className="relative pb-4 last:pb-0">
                <span
                  aria-hidden
                  className="absolute -start-[21px] top-1.5 size-2.5 rounded-full bg-[var(--pol-light-brand-primary)]"
                />
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-[13px] font-medium text-[var(--pol-light-text-primary)]">
                    {ev.event_type ?? "رویداد"}
                  </span>
                  {ev.from_status || ev.to_status ? (
                    <span className="text-[12px] text-[var(--pol-light-text-secondary)]" dir="ltr">
                      {ev.from_status ?? "∅"} → {ev.to_status ?? "∅"}
                    </span>
                  ) : null}
                  <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(ev.created_at)}
                  </span>
                </div>
              </li>
            ))}
          </ol>
        )}
      </section>
    </div>
  );
}
