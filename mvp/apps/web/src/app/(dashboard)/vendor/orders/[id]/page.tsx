"use client";

import { formatPackagingUnit } from "@/lib/format-labels";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  Field,
  Skeleton,
  StatusChip,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  disputeStatusLabel,
  formatDateTime,
  formatOperationalStatus,
  formatDeliveryStatus,
  formatTimelineEventLabel,
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
 * POST /orders/{id}/accept|reject|preparing|ready|dispatch
 * POST /orders/{id}/delivery/picked-up|in-transit|arrived
 * POST /orders/{id}/partial-acceptance-proposals
 * POST /orders/{id}/deliver is retailer-only (recipient + OTP) and is never
 * offered here; the vendor advances the delivery record up to ARRIVED.
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
  const [deliveryStatus, setDeliveryStatus] = useState<string | null>(null);
  const [driverName, setDriverName] = useState("");
  const [driverPlate, setDriverPlate] = useState("");
  const [driverPhone, setDriverPhone] = useState("");

  const load = useCallback(async () => {
    if (!orderId) return;
    setState("loading");
    setErrorMessage(null);
    setActionError(null);
    try {
      const [o, it, tl, delivery] = await Promise.all([
        getApi().get<OrderDetail>(`/api/v1/orders/${orderId}`),
        getApi().get<unknown>(`/api/v1/orders/${orderId}/items`),
        getApi().get<unknown>(`/api/v1/orders/${orderId}/timeline`),
        getApi()
          .get<{ delivery_status?: string | null }>(`/api/v1/orders/${orderId}/delivery`)
          .catch(() => null),
      ]);
      setOrder(o);
      setItems(asArray<OrderItem>(it, "items"));
      setEvents(asArray<TimelineEvent>(tl, "events"));
      setDeliveryStatus(delivery?.delivery_status ?? null);
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

  async function submitDispatch() {
    if (!orderId) return;
    if (!driverName.trim() || !driverPlate.trim() || !driverPhone.trim()) {
      setActionError("نام راننده، پلاک و تلفن راننده الزامی است.");
      return;
    }
    setActing("dispatch");
    setActionError(null);
    try {
      await getApi().post(`/api/v1/orders/${orderId}/dispatch`, {
        driver_name: driverName.trim(),
        vehicle_plate: driverPlate.trim(),
        driver_phone: driverPhone.trim(),
      });
      await load();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "ثبت ارسال ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  async function submitDeliveryStage(target: "picked-up" | "in-transit" | "arrived") {
    if (!orderId) return;
    setActing(target);
    setActionError(null);
    try {
      await getApi().post(`/api/v1/orders/${orderId}/delivery/${target}`, {});
      await load();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "تغییر وضعیت تحویل ناموفق بود");
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
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری سفارش">
        <Skeleton className="h-9 w-64" />
        <Card className="p-6">
          <Skeleton lines={4} />
        </Card>
        <Card className="p-6">
          <Skeleton lines={6} />
        </Card>
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
    <div className="space-y-6">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] md:text-[26px] font-bold text-[var(--pol-light-text-primary)]">
              مدیریت و پردازش سفارش
            </h1>
            <span className="font-mono text-[14px] font-bold text-[var(--pol-light-text-secondary)]" dir="ltr">
              {order.order_number ?? order.id}
            </span>
          </div>
          <p className="mt-1 flex flex-wrap items-center gap-2 text-[12px] text-[var(--pol-light-text-secondary)]">
            <span>تاریخ ثبت: {formatDateTime(order.created_at)}</span>
            {order.retailer_id && (
              <>
                <span>·</span>
                <span dir="ltr">شناسه خریدار: {order.retailer_id.slice(0, 8)}...</span>
              </>
            )}
          </p>
        </div>

        <div className="flex shrink-0 gap-2">
          <Button variant="ghost" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
          <Link
            href="/vendor/orders"
            className="inline-flex items-center justify-center rounded-lg border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] font-medium text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)] transition-colors"
          >
            صف سفارش‌ها
          </Link>
        </div>
      </header>

      {/* Status & Amount Banner */}
      <Card className="p-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-2.5">
            <StatusChip tone={orderStatusTone[status] ?? "neutral"}>
              {orderStatusLabel[status] ?? "وضعیت نامشخص"}
            </StatusChip>
            {order.dispute_status && order.dispute_status !== "NONE" && (
              <StatusChip tone="danger">
                {disputeStatusLabel[order.dispute_status ?? ""] ?? "وضعیت نامشخص"}
              </StatusChip>
            )}
            {order.delivery_address && (
              <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
                📍 نشانی تحویل: {order.delivery_address}
              </span>
            )}
          </div>

          <div className="border-t border-[var(--pol-light-border-subtle)] pt-3 sm:border-0 sm:pt-0 text-start sm:text-end">
            <span className="block text-[11px] text-[var(--pol-light-text-secondary)]">
              مبلغ کل فاکتور
            </span>
            <span className="text-[20px] font-bold text-[var(--pol-light-text-primary)]">
              {formatToman(order.total_amount_toman)}
            </span>
          </div>
        </div>
      </Card>

      {actionError && (
        <ErrorState title="عملیات ناموفق بود" description={actionError} />
      )}

      {/* Dispatch driver details (parity with the mobile fulfillment form) */}
      {status === "READY" ? (
        <Card className="p-5 shadow-xs space-y-4">
          <div>
            <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
              مشخصات راننده و خودروی ارسال
            </h2>
            <p className="mt-0.5 text-[12px] text-[var(--pol-light-text-secondary)]">
              برای ثبت ارسال، نام راننده، پلاک و تلفن راننده الزامی است.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <Field
              label="نام راننده"
              value={driverName}
              onChange={(e) => setDriverName(e.target.value)}
              maxLength={100}
              placeholder="مثلاً علی رضایی"
            />
            <Field
              label="پلاک خودرو"
              value={driverPlate}
              onChange={(e) => setDriverPlate(e.target.value)}
              maxLength={20}
              placeholder="12-A-345"
              dir="ltr"
            />
            <Field
              label="تلفن راننده"
              value={driverPhone}
              onChange={(e) => setDriverPhone(e.target.value)}
              maxLength={32}
              placeholder="09121234567"
              inputMode="tel"
              dir="ltr"
            />
          </div>
        </Card>
      ) : null}

      {/* Action Controls Bar */}
      {(canAccept || (canFulfill && nextFulfill)) && (
        <Card className="p-4 bg-[var(--pol-light-surface-subtle)] border-[var(--pol-light-brand-primary)]">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-[14px] font-bold text-[var(--pol-light-text-primary)]">
                اقدامات در گردش کار سفارش
              </h2>
              <p className="text-[12px] text-[var(--pol-light-text-secondary)]">
                {canAccept
                  ? "سفارش جدید دریافت شده است. تأیید موجودی یا پیشنهاد پذیرش جزئی را ثبت کنید."
                  : "سفارش در مرحله آماده‌سازی و ارسال است. با تکمیل هر گام، وضعیت را به‌روزرسانی کنید."}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              {canAccept && (
                <>
                  <Button
                    loading={acting === "accept"}
                    disabled={acting !== null}
                    onClick={() => void act("/accept", {}, "accept")}
                  >
                    تأیید و پذیرش کامل
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={() => {
                      setPartialOpen((v) => !v);
                      setRejectOpen(false);
                    }}
                    aria-expanded={partialOpen}
                  >
                    پیشنهاد پذیرش جزئی
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setRejectOpen((v) => !v);
                      setPartialOpen(false);
                    }}
                    aria-expanded={rejectOpen}
                  >
                    رد سفارش
                  </Button>
                </>
              )}

              {canFulfill && status !== "DISPATCHED" && nextFulfill ? (
                status === "READY" ? (
                  <Button
                    loading={acting === "dispatch"}
                    disabled={acting !== null}
                    onClick={() => void submitDispatch()}
                  >
                    {nextFulfill}
                  </Button>
                ) : (
                  <Button
                    loading={acting === "fulfill"}
                    disabled={acting !== null}
                    onClick={() =>
                      void act(
                        status === "ACCEPTED" || status === "PARTIALLY_ACCEPTED"
                          ? "/preparing"
                          : "/ready",
                        {},
                        "fulfill",
                      )
                    }
                  >
                    {nextFulfill}
                  </Button>
                )
              ) : null}

              {status === "DISPATCHED" ? (
                <div className="flex flex-wrap items-center gap-2">
                  <StatusChip tone="info">
                    وضعیت تحویل: {formatDeliveryStatus(deliveryStatus)}
                  </StatusChip>
                  {deliveryStatus === "ASSIGNED" ? (
                    <Button
                      loading={acting === "picked-up"}
                      disabled={acting !== null}
                      onClick={() => void submitDeliveryStage("picked-up")}
                    >
                      جمع‌آوری شد
                    </Button>
                  ) : null}
                  {deliveryStatus === "PICKED_UP" ? (
                    <Button
                      loading={acting === "in-transit"}
                      disabled={acting !== null}
                      onClick={() => void submitDeliveryStage("in-transit")}
                    >
                      در مسیر
                    </Button>
                  ) : null}
                  {deliveryStatus === "IN_TRANSIT" ? (
                    <Button
                      loading={acting === "arrived"}
                      disabled={acting !== null}
                      onClick={() => void submitDeliveryStage("arrived")}
                    >
                      رسید
                    </Button>
                  ) : null}
                  {deliveryStatus === "FAILED" ? (
                    <p className="text-[12px] font-medium text-[var(--pol-light-semantic-danger)]">
                      ارسال ناموفق شده است؛ برای ادامه به رسیدگی عملیاتی نیاز دارد.
                    </p>
                  ) : null}
                </div>
              ) : null}
            </div>
          </div>
        </Card>
      )}

      {/* Reject Order Section */}
      {rejectOpen && canAccept && (
        <Card className="p-5 border-rose-300 bg-rose-50/20 dark:border-rose-800 dark:bg-rose-950/20">
          <h2 className="text-[15px] font-bold text-rose-600 dark:text-rose-400">
            رد کردن سفارش
          </h2>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
            لطفاً دلیل عدم امکان تأمین اقلام را مشخص کنید تا به خرده‌فروش اطلاع داده شود.
          </p>
          <div className="mt-4">
            <Field
              label="دلیل رد سفارش"
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="مثال: عدم موجودی در انبار مرکزی، افزایش قیمت رسمی..."
              maxLength={500}
            />
          </div>
          <div className="mt-4 flex gap-2">
            <Button
              variant="outline"
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
              تأیید نهایی رد سفارش
            </Button>
            <Button variant="secondary" onClick={() => setRejectOpen(false)}>
              انصراف
            </Button>
          </div>
        </Card>
      )}

      {/* Partial Acceptance Proposal Form */}
      {partialOpen && canAccept && (
        <Card className="p-5 border-amber-300 bg-amber-50/20 dark:border-amber-800 dark:bg-amber-950/20">
          <h2 className="text-[15px] font-bold text-amber-700 dark:text-amber-400">
            ثبت پیشنهاد پذیرش جزئی اقلام
          </h2>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
            تعداد قابل تحویل برای هر قلم کالا را وارد فرمایید. پیشنهاد برای تأیید نهایی به خرده‌فروش
            ارسال می‌شود.
          </p>

          <div className="mt-4 space-y-3">
            {partialLines.map((line, idx) => {
              const item = items.find((i) => i.id === line.item_id);
              return (
                <div
                  key={line.item_id}
                  className="flex flex-col gap-2 rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-3.5 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div>
                    <span className="text-[14px] font-bold text-[var(--pol-light-text-primary)]">
                      {item?.product_name_snapshot ?? line.item_id.slice(0, 8)}
                    </span>
                    <span className="block text-[12px] text-[var(--pol-light-text-muted)]">
                      سفارش اولیه: {Number(item?.ordered_quantity ?? 0).toLocaleString("fa-IR")}{" "}
                      {formatPackagingUnit(item?.packaging_unit_snapshot)}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <label htmlFor={`partial-qty-${idx}`} className="text-[12px] text-[var(--pol-light-text-secondary)]">
                      تعداد قابل تأمین:
                    </label>
                    <input
                      id={`partial-qty-${idx}`}
                      type="number"
                      min={0}
                      className={[inputCls, "w-28 text-center font-bold"].join(" ")}
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
                </div>
              );
            })}
          </div>

          <div className="mt-4 flex gap-2">
            <Button
              loading={acting === "partial"}
              disabled={acting !== null}
              onClick={() => void submitPartial()}
            >
              ارسال پیشنهاد پذیرش جزئی
            </Button>
            <Button variant="secondary" onClick={() => setPartialOpen(false)}>
              انصراف
            </Button>
          </div>
        </Card>
      )}

      {/* Items Table */}
      <section aria-label="اقلام سفارش" className="space-y-3">
        <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
          اقلام سفارش ({items.length.toLocaleString("fa-IR")} قلم)
        </h2>

        {items.length === 0 ? (
          <EmptyState title="هیچ قلم کالایی در این سفارش ثبت نشده است" />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>شرح کالا و برند</TableHead>
                <TableHead>تعداد درخواستی</TableHead>
                <TableHead>تعداد پذیرفته</TableHead>
                <TableHead>واحد بسته‌بندی</TableHead>
                <TableHead>مبلغ کل</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((it) => (
                <TableRow key={it.id}>
                  <TableCell>
                    <div className="py-1">
                      <span className="font-bold text-[var(--pol-light-text-primary)]">
                        {it.product_name_snapshot ?? "—"}
                      </span>
                      {it.brand_name_snapshot && (
                        <span className="block text-[11px] text-[var(--pol-light-text-muted)]">
                          برند: {it.brand_name_snapshot}
                        </span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="font-bold text-[var(--pol-light-text-primary)]">
                    {Number(it.ordered_quantity ?? 0).toLocaleString("fa-IR")}
                  </TableCell>
                  <TableCell className="text-[var(--pol-light-text-secondary)]">
                    {it.accepted_quantity != null
                      ? Number(it.accepted_quantity).toLocaleString("fa-IR")
                      : "—"}
                  </TableCell>
                  <TableCell className="text-[var(--pol-light-text-secondary)]">
                    {formatPackagingUnit(it.packaging_unit_snapshot)}
                    {it.pack_quantity_snapshot ? ` ×${it.pack_quantity_snapshot.toLocaleString("fa-IR")}` : ""}
                  </TableCell>
                  <TableCell className="font-bold text-[var(--pol-light-text-primary)]">
                    {formatToman(it.total_line_amount_toman)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </section>

      {/* Timeline Stepper */}
      <section aria-label="خط زمانی گردش کار" className="space-y-3">
        <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
          خط زمانی گردش کار سفارش
        </h2>

        {events.length === 0 ? (
          <EmptyState title="هیچ رویدادی برای این سفارش ثبت نشده است" />
        ) : (
          <Card className="p-5">
            <ol className="relative border-s-2 border-[var(--pol-light-border-subtle)] ps-5 space-y-4">
              {events.map((ev) => (
                <li key={idOf(ev) || str(ev.id)} className="relative">
                  <span
                    aria-hidden
                    className="absolute -start-[27px] top-1.5 size-3 rounded-full border-2 border-[var(--pol-light-surface-default)] bg-[var(--pol-light-brand-primary)]"
                  />
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-[13px] font-bold text-[var(--pol-light-text-primary)]">
                      {formatTimelineEventLabel(ev.event_type)}
                    </span>
                    <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                      {formatDateTime(ev.created_at)}
                    </span>
                  </div>
                  {ev.from_status || ev.to_status ? (
                    <div className="mt-1 text-[12px] font-mono text-[var(--pol-light-text-secondary)]" dir="ltr">
                      {formatOperationalStatus(ev.from_status, "شروع")} → {formatOperationalStatus(ev.to_status, "پایان")}
                    </div>
                  ) : null}
                </li>
              ))}
            </ol>
          </Card>
        )}
      </section>

      {/* Historical Partial Proposals */}
      {proposals.length > 0 && (
        <section aria-label="پیشنهادهای پذیرش جزئی پیشین" className="space-y-3">
          <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
            پیشنهادهای پذیرش جزئی ثبت‌شده
          </h2>
          <div className="grid gap-2.5">
            {proposals.map((p) => (
              <Card key={String(p.id)} className="p-4">
                <div className="flex items-center justify-between">
                  <StatusChip tone="info">{formatOperationalStatus(p.status)}</StatusChip>
                  <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(p.created_at)}
                  </span>
                </div>
              </Card>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
