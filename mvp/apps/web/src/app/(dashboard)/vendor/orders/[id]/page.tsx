"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Button,
  EmptyState,
  ErrorState,
  Field,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  cardCls,
  disputeStatusLabel,
  formatDateTime,
  formatToman,
  fulfillmentLabel,
  idOf,
  inputCls,
  itemsOf,
  orderStatusLabel,
  orderStatusTone,
  str,
  vendorCanAccept,
  vendorCanFulfill,
  type LoadState,
} from "../../_shared";

interface OrderDetail {
  id: string;
  order_number?: string | null;
  order_status?: string | null;
  dispute_status?: string | null;
  total_amount_toman?: number | null;
  retailer_id?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  delivery_address?: string | null;
}

interface OrderItem {
  id: string;
  product_id?: string | null;
  product_name_snapshot?: string | null;
  brand_name_snapshot?: string | null;
  packaging_unit_snapshot?: string | null;
  pack_quantity_snapshot?: number | null;
  ordered_quantity?: number | null;
  accepted_quantity?: number | null;
  delivered_quantity?: number | null;
  unit_price_toman?: number | null;
  total_line_amount_toman?: number | null;
  fulfillment_status?: string | null;
}

interface PartialProposal {
  id: string;
  status?: string | null;
  created_at?: string | null;
}

interface TimelineEvent {
  id: string;
  event_type?: string | null;
  from_status?: string | null;
  to_status?: string | null;
  created_at?: string | null;
}

type LoadState2 = LoadState | "acting";

function asArray<T>(raw: unknown, ...keys: string[]): T[] {
  if (Array.isArray(raw)) return raw as T[];
  if (raw && typeof raw === "object") {
    const obj = raw as Record<string, unknown>;
    for (const key of [...keys, "items", "data", "events", "proposals"]) {
      const hit = obj[key];
      if (Array.isArray(hit)) return hit as T[];
      if (hit && typeof hit === "object" && !Array.isArray(hit)) {
        const nested = hit as Record<string, unknown>;
        for (const k2 of [...keys, "items", "data"]) {
          if (Array.isArray(nested[k2])) return nested[k2] as T[];
        }
        if (Array.isArray(nested.data)) return nested.data as T[];
      }
    }
  }
  return [];
}

/**
 * V-03 order detail + accept / reject / partial / fulfill chain.
 * POST /orders/{id}/accept|reject|preparing|ready|dispatch|deliver
 * POST /orders/{id}/partial-acceptance-proposals
 */
export default function VendorOrderDetailPage() {
  const params = useParams<{ id: string }>();
  const orderId = params.id;

  const [order, setOrder] = useState<OrderDetail | null>(null);
  const [items, setItems] = useState<OrderItem[]>([]);
  const [proposals, setProposals] = useState<PartialProposal[]>([]);
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [state, setState] = useState<LoadState2>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [acting, setActing] = useState<string | null>(null);

  const [rejectOpen, setRejectOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [partialOpen, setPartialOpen] = useState(false);
  const [partialLines, setPartialLines] = useState<Array<{ item_id: string; quantity: string }>>([]);

  const load = useCallback(async () => {
    if (!orderId) return;
    setState("loading");
    setErrorMessage(null);
    setActionError(null);
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
      setPartialLines(
        asArray<OrderItem>(it, "items").map((row) => ({
          item_id: row.id,
          quantity: String(row.ordered_quantity ?? 0),
        })),
      );
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت سفارش ناموفق بود");
      setState("error");
    }
  }, [orderId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function act(path: string, body?: unknown, label = "action") {
    if (!orderId) return;
    setActing(label);
    setActionError(null);
    try {
      await getApi().post(`/api/v1/orders/${orderId}${path}`, body);
      await load();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "عملیات ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  async function submitPartial() {
    if (!orderId) return;
    setActing("partial");
    setActionError(null);
    try {
      const lines = partialLines
        .filter((l) => Number(l.quantity) >= 0 && l.item_id)
        .map((l) => ({ item_id: l.item_id, quantity: Number(l.quantity) }));
      await getApi().post(`/api/v1/orders/${orderId}/partial-acceptance-proposals`, {
        items: lines,
      });
      setPartialOpen(false);
      await load();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "ثبت پذیرش جزئی ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری سفارش">
        <Skeleton className="h-8 w-64" />
        <div className={cardCls}>
          <Skeleton lines={3} />
        </div>
        <div className={cardCls}>
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

  const status = order.order_status ?? "";
  const canAccept = vendorCanAccept(status);
  const canFulfill = vendorCanFulfill(status);
  const nextFulfill = fulfillmentLabel(status);

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-start gap-3">
        <div>
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            جزئیات سفارش فروشنده
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
          <Link
            href="/vendor/orders"
            className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
          >
            صف سفارش‌ها
          </Link>
        </div>
      </header>

      <section
        aria-label="وضعیت"
        className="flex flex-wrap items-center gap-2 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
      >
        <StatusChip tone={orderStatusTone[status] ?? "neutral"}>
          {orderStatusLabel[status] ?? status ?? "—"}
        </StatusChip>
        <StatusChip tone={order.dispute_status && order.dispute_status !== "NONE" ? "danger" : "neutral"}>
          {disputeStatusLabel[order.dispute_status ?? "NONE"] ?? order.dispute_status ?? "—"}
        </StatusChip>
        <span className="ms-auto text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
          {formatToman(order.total_amount_toman)}
        </span>
      </section>

      {actionError ? (
        <ErrorState title="عملیات ناموفق بود" description={actionError} />
      ) : null}

      <section aria-label="اقدامات" className="flex flex-wrap gap-2">
        {canAccept ? (
          <>
            <Button
              loading={acting === "accept"}
              disabled={acting !== null}
              onClick={() => void act("/accept", {}, "accept")}
            >
              پذیرش سفارش
            </Button>
            <Button
              variant="secondary"
              onClick={() => setPartialOpen((v) => !v)}
              aria-expanded={partialOpen}
            >
              پذیرش جزئی
            </Button>
            <Button
              variant="ghost"
              onClick={() => setRejectOpen((v) => !v)}
              aria-expanded={rejectOpen}
            >
              رد سفارش
            </Button>
          </>
        ) : null}
        {canFulfill && nextFulfill ? (
          <Button
            loading={acting === "fulfill"}
            disabled={acting !== null}
            onClick={() => {
              const path =
                status === "ACCEPTED" || status === "PARTIALLY_ACCEPTED"
                  ? "/preparing"
                  : status === "PREPARING"
                    ? "/ready"
                    : status === "READY"
                      ? "/dispatch"
                      : "/deliver";
              void act(path, {}, "fulfill");
            }}
          >
            {nextFulfill}
          </Button>
        ) : null}
      </section>

      {rejectOpen && canAccept ? (
        <section aria-label="رد سفارش" className={cardCls}>
          <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
            رد سفارش
          </h2>
          <div className="mt-3">
            <Field
              label="دلیل"
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              hint="اختیاری — به payload ارسال می‌شود اگر بک‌اند بپذیرد"
              maxLength={500}
            />
          </div>
          <div className="mt-3 flex gap-2">
            <Button
              variant="ghost"
              loading={acting === "reject"}
              disabled={acting !== null}
              onClick={() =>
                void act(
                  "/reject",
                  rejectReason.trim() ? { reason: rejectReason.trim() } : {},
                  "reject",
                ).then(() => setRejectOpen(false))
              }
            >
              تأیید رد
            </Button>
            <Button variant="secondary" onClick={() => setRejectOpen(false)}>
              انصراف
            </Button>
          </div>
        </section>
      ) : null}

      {partialOpen && canAccept ? (
        <section aria-label="پذیرش جزئی" className={cardCls}>
          <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
            پیشنهاد پذیرش جزئی
          </h2>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]">
            تعداد پذیرفته‌شده هر قلم را وارد کنید. مقادیر بیشتر از سفارش توسط سرور رد می‌شود.
          </p>
          <div className="mt-3 space-y-2">
            {partialLines.map((line, idx) => {
              const item = items.find((i) => i.id === line.item_id);
              return (
                <div
                  key={line.item_id}
                  className="flex flex-wrap items-center gap-3 rounded-[8px] border border-[var(--pol-light-border-subtle)] p-3"
                >
                  <span className="text-[13px] text-[var(--pol-light-text-primary)]">
                    {item?.product_name_snapshot ?? line.item_id.slice(0, 8)}
                  </span>
                  <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                    سفارش: {Number(item?.ordered_quantity ?? 0).toLocaleString("fa-IR")}
                  </span>
                  <input
                    type="number"
                    min={0}
                    aria-label={`تعداد پذیرفته‌شده قلم ${idx + 1}`}
                    className={[inputCls, "w-24 ms-auto"].join(" ")}
                    value={line.quantity}
                    onChange={(e) =>
                      setPartialLines((prev) =>
                        prev.map((l, i) =>
                          i === idx ? { ...l, quantity: e.target.value } : l,
                        ),
                      )
                    }
                  />
                </div>
              );
            })}
          </div>
          <div className="mt-3 flex gap-2">
            <Button
              loading={acting === "partial"}
              disabled={acting !== null}
              onClick={() => void submitPartial()}
            >
              ارسال پیشنهاد
            </Button>
            <Button variant="secondary" onClick={() => setPartialOpen(false)}>
              انصراف
            </Button>
          </div>
        </section>
      ) : null}

      <section aria-label="اقلام">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          اقلام
        </h2>
        {items.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="قلمی ثبت نشده" />
          </div>
        ) : (
          <div className="mt-3 overflow-x-auto rounded-[12px] border border-[var(--pol-light-border-subtle)]">
            <table className="w-full min-w-[640px] border-collapse bg-[var(--pol-light-surface-default)] text-[13px]">
              <thead>
                <tr className="border-b border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] text-[12px] text-[var(--pol-light-text-secondary)]">
                  <th className="px-4 py-2 text-start font-medium">کالا</th>
                  <th className="px-4 py-2 text-start font-medium">سفارش</th>
                  <th className="px-4 py-2 text-start font-medium">پذیرفته</th>
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
                    <td className="px-4 py-3 text-[var(--pol-light-text-primary)]">
                      {it.product_name_snapshot ?? "—"}
                      {it.brand_name_snapshot ? (
                        <span className="ms-1 text-[11px] text-[var(--pol-light-text-muted)]">
                          {it.brand_name_snapshot}
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

      <section aria-label="خط زمانی">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          خط زمانی
        </h2>
        {events.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="رویدادی ثبت نشده" />
          </div>
        ) : (
          <ol className="mt-3 border-s-2 border-[var(--pol-light-border-subtle)] ps-4">
            {events.map((ev) => (
              <li key={idOf(ev) || str(ev.id)} className="relative pb-4 last:pb-0">
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

      {proposals.length > 0 ? (
        <section aria-label="پیشنهادهای پذیرش جزئی">
          <h2 className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
            پیشنهادهای پذیرش جزئی
          </h2>
          <ul role="list" className="mt-2 space-y-2">
            {proposals.map((p) => (
              <li key={String(p.id)} className={cardCls}>
                <StatusChip tone="info">{p.status ?? "—"}</StatusChip>
                <span className="ms-2 text-[12px] text-[var(--pol-light-text-muted)]">
                  {formatDateTime(p.created_at)}
                </span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}
