"use client";

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
  disputeLabel,
  disputeTone,
  formatDateTime,
  formatToman,
  groupStatusLabel,
  groupStatusTone,
  orderStatusTone,
  orderStatusLabel,
} from "../../shared";

interface DeliveryRecord {
  id?: string;
  order_id?: string | null;
  vendor_id?: string | null;
  delivery_status?: string | null;
  driver_name?: string | null;
  vehicle_plate?: string | null;
  driver_phone?: string | null;
  dispatched_at?: string | null;
  delivered_at?: string | null;
  created_at?: string | null;
}

interface DeliveryProof {
  id?: string;
  delivery_id?: string | null;
  accepted_by_name?: string | null;
  accepted_at?: string | null;
  otp_verified?: boolean | null;
  issue_reported_at_delivery?: string | null;
  message?: string | null;
}

interface PartialProposalView {
  proposal_id: string;
  status: string;
  proposed_at?: string | null;
  items: Array<{
    order_item_id: string;
    accepted_quantity?: number | null;
    reason?: string | null;
  }>;
}

const PARTIAL_PROPOSED = "ORDER_PARTIAL_ACCEPTANCE_PROPOSED";
const PARTIAL_DECLINED = "ORDER_PARTIAL_ACCEPTANCE_DECLINED";
const PARTIAL_APPROVED = "ORDER_PARTIAL_ACCEPTANCE_APPROVED";

function asRecord(v: unknown): Record<string, unknown> | null {
  return v && typeof v === "object" && !Array.isArray(v)
    ? (v as Record<string, unknown>)
    : null;
}

function strVal(v: unknown): string | null {
  return typeof v === "string" && v ? v : null;
}

function numVal(v: unknown): number | null {
  if (typeof v === "number" && Number.isFinite(v)) return v;
  if (typeof v === "string" && v.trim() !== "") {
    const n = Number(v);
    if (Number.isFinite(n)) return n;
  }
  return null;
}

/**
 * R-09C: no GET for proposals — derive open proposals from timeline
 * event_data.proposal_id / items on PROPOSED events, closing on
 * later APPROVED/DECLINED for the same proposal_id.
 */
function deriveProposals(events: TimelineEvent[]): PartialProposalView[] {
  const byId = new Map<string, PartialProposalView>();
  for (const ev of events) {
    const data = asRecord(ev.event_data);
    const proposalId = strVal(data?.proposal_id);
    if (!proposalId) continue;
    const t = ev.event_type ?? "";
    if (t === PARTIAL_PROPOSED) {
      const rawItems = Array.isArray(data?.items) ? (data.items as unknown[]) : [];
      const items = rawItems.map((raw) => {
        const row = asRecord(raw) ?? {};
        return {
          order_item_id: strVal(row.order_item_id) ?? strVal(row.item_id) ?? "",
          accepted_quantity: numVal(row.accepted_quantity),
          reason: strVal(row.reason),
        };
      });
      byId.set(proposalId, {
        proposal_id: proposalId,
        status: "PENDING",
        proposed_at: ev.created_at ?? null,
        items,
      });
    } else if (t === PARTIAL_APPROVED) {
      const prev = byId.get(proposalId);
      byId.set(proposalId, {
        proposal_id: proposalId,
        status: "ACCEPTED",
        proposed_at: prev?.proposed_at ?? null,
        items: prev?.items ?? [],
      });
    } else if (t === PARTIAL_DECLINED) {
      const prev = byId.get(proposalId);
      byId.set(proposalId, {
        proposal_id: proposalId,
        status: "DECLINED",
        proposed_at: prev?.proposed_at ?? null,
        items: prev?.items ?? [],
      });
    }
  }
  return [...byId.values()].sort((a, b) =>
    String(b.proposed_at ?? "").localeCompare(String(a.proposed_at ?? "")),
  );
}

const DELIVERY_STATUS_LABEL: Record<string, string> = {
  PENDING: "در انتظار ارسال",
  ASSIGNED: "محول‌شده",
  IN_TRANSIT: "در حال ارسال",
  OUT_FOR_DELIVERY: "خارج‌شده برای تحویل",
  DELIVERED: "تحویل‌شده",
  FAILED: "ناموفق",
  CANCELLED: "لغوشده",
};

const DELIVERY_STATUS_TONE: Record<string, "success" | "warning" | "danger" | "info" | "neutral"> = {
  PENDING: "neutral",
  ASSIGNED: "info",
  IN_TRANSIT: "info",
  OUT_FOR_DELIVERY: "warning",
  DELIVERED: "success",
  FAILED: "danger",
  CANCELLED: "neutral",
};

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
 * R-09C partial acceptance review (approve/decline).
 * R-09D delivery tracking (GET /orders/{id}/delivery).
 * R-09E handoff / receiver confirm (proof + POST /deliver).
 */
export default function RetailerOrderDetailPage() {
  const params = useParams<{ id: string }>();
  const orderId = params.id;

  const [order, setOrder] = useState<OrderDetail | null>(null);
  const [items, setItems] = useState<OrderItem[]>([]);
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [acting, setActing] = useState<string | null>(null);
  const [delivery, setDelivery] = useState<DeliveryRecord | null>(null);
  const [deliveryMissing, setDeliveryMissing] = useState(false);
  const [proof, setProof] = useState<DeliveryProof | null>(null);
  const [proofMissing, setProofMissing] = useState(false);
  const [declineOpen, setDeclineOpen] = useState<string | null>(null);
  const [declineReason, setDeclineReason] = useState("");
  const [recipientName, setRecipientName] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [issueReported, setIssueReported] = useState("");

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
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت سفارش ناموفق بود");
      setState("error");
      return;
    }
    try {
      const d = await getApi().get<DeliveryRecord>(`/api/v1/orders/${orderId}/delivery`);
      if (d && (d.id || d.delivery_status)) {
        setDelivery(d);
        setDeliveryMissing(false);
      } else {
        setDelivery(null);
        setDeliveryMissing(true);
      }
    } catch {
      setDelivery(null);
      setDeliveryMissing(true);
    }
    try {
      const p = await getApi().get<DeliveryProof>(`/api/v1/orders/${orderId}/delivery/proof`);
      if (p && p.id) {
        setProof(p);
        setProofMissing(false);
      } else {
        setProof(null);
        setProofMissing(true);
      }
    } catch {
      setProof(null);
      setProofMissing(true);
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

  async function approveProposal(proposalId: string) {
    await act(
      `/partial-acceptance-proposals/${proposalId}/approve`,
      undefined,
      `approve:${proposalId}`,
    );
  }

  async function declineProposal(proposalId: string) {
    setActing(`decline:${proposalId}`);
    setActionError(null);
    try {
      const reason = declineReason.trim();
      await getApi().post(
        `/api/v1/orders/${orderId}/partial-acceptance-proposals/${proposalId}/decline`,
        reason ? { reason } : undefined,
      );
      setDeclineOpen(null);
      setDeclineReason("");
      await load();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "رد پیشنهاد ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  async function confirmDelivery() {
    if (!orderId) return;
    setActing("deliver");
    setActionError(null);
    try {
      const body: Record<string, string> = {};
      if (recipientName.trim()) body.recipient_name = recipientName.trim();
      if (otpCode.trim()) body.otp_code = otpCode.trim();
      if (issueReported.trim()) body.issue_reported = issueReported.trim();
      await getApi().post(`/api/v1/orders/${orderId}/deliver`, body);
      await load();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "تأیید تحویل ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری سفارش">
        <Skeleton className="h-8 w-64" />
        <Card className="p-5">
          <Skeleton lines={3} />
        </Card>
        <Card className="p-5">
          <Skeleton lines={4} />
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

  return (
    <div className="space-y-6 pb-10">
      <header className="flex flex-wrap items-start justify-between gap-4 border-b border-[var(--pol-light-border-subtle)] pb-5">
        <div>
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            جزئیات سفارش
          </h1>
          <p className="mt-1 flex flex-wrap items-center gap-2">
            <span className="font-mono text-[14px] font-bold text-[var(--pol-light-text-primary)]" dir="ltr">
              {order.order_number ?? order.id}
            </span>
            <span className="text-[12px] text-[var(--pol-light-text-muted)]">
              · ثبت‌شده در {formatDateTime(order.created_at)}
            </span>
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="secondary" size="sm" onClick={() => void load()}>
            <svg className="size-4 me-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            به‌روزرسانی
          </Button>
          <Link
            href="/retailer/orders"
            className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[12px] font-medium text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)]"
          >
            ← تمام سفارش‌ها
          </Link>
        </div>
      </header>

      {/* Primary Status Banner */}
      <Card className="p-4 sm:p-5 shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-2">
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
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[13px] text-[var(--pol-light-text-muted)]">مبلغ کل سفارش:</span>
            <span className="text-[18px] font-bold text-[var(--pol-light-brand-primary)]">
              {formatToman(order.total_amount_toman)}
            </span>
          </div>
        </div>

        {order.delivery_address ? (
          <div className="mt-3 pt-3 border-t border-[var(--pol-light-border-subtle)] text-[12px] text-[var(--pol-light-text-secondary)]">
            <span className="font-semibold text-[var(--pol-light-text-primary)]">نشانی تحویل: </span>
            <span>{order.delivery_address}</span>
          </div>
        ) : null}
      </Card>

      {actionError ? (
        <ErrorState title="عملیات ناموفق بود" description={actionError} />
      ) : null}

      {/* Context Links */}
      <div className="flex flex-wrap gap-2">
        {order.order_group_id ? (
          <Link
            href={`/retailer/orders/group/${order.order_group_id}`}
            className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[12px] font-medium text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
          >
            مشاهده گروه سفارش
            {order.group_order_count != null
              ? ` (${order.group_order_count.toLocaleString("fa-IR")} سفارش)`
              : ""}
          </Link>
        ) : null}
        <Link
          href={`/retailer/orders/${order.id}/returns`}
          className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[12px] font-medium text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
        >
          ثبت درخواست بازگشت کالا و اختلاف
        </Link>
        <Link
          href="/retailer/support"
          className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[12px] font-medium text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
        >
          پشتیبانی سفارش
        </Link>
      </div>

      {/* Order Items Table */}
      <section aria-label="اقلام سفارش" className="space-y-3">
        <h2 className="text-[16px] leading-[24px] font-bold text-[var(--pol-light-text-primary)]">
          اقلام سفارش ({items.length.toLocaleString("fa-IR")} قلم)
        </h2>
        {items.length === 0 ? (
          <Card variant="subtle" className="p-6">
            <EmptyState title="قلمی برای این سفارش ثبت نشده است" />
          </Card>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>نام کالا و مشخصات</TableHead>
                <TableHead>تعداد سفارش</TableHead>
                <TableHead>پذیرفته‌شده</TableHead>
                <TableHead>تحویل‌شده</TableHead>
                <TableHead>بسته‌بندی</TableHead>
                <TableHead>مبلغ کل سطر</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((it) => (
                <TableRow key={it.id}>
                  <TableCell>
                    <div className="font-semibold text-[var(--pol-light-text-primary)]">
                      {it.product_name_snapshot ?? "—"}
                    </div>
                    <div className="mt-0.5 flex flex-wrap items-center gap-1.5">
                      {it.brand_name_snapshot ? (
                        <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                          {it.brand_name_snapshot}
                        </span>
                      ) : null}
                      {it.fulfillment_status ? (
                        <StatusChip tone="info">{it.fulfillment_status}</StatusChip>
                      ) : null}
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
                    {it.delivered_quantity != null
                      ? Number(it.delivered_quantity).toLocaleString("fa-IR")
                      : "—"}
                  </TableCell>
                  <TableCell className="text-[var(--pol-light-text-secondary)]">
                    {it.packaging_unit_snapshot ?? "—"}
                    {it.pack_quantity_snapshot
                      ? ` ×${it.pack_quantity_snapshot.toLocaleString("fa-IR")}`
                      : ""}
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

      {/* Partial Acceptance Review (R-09C) */}
      <section aria-label="پذیرش جزئی" data-screen="R-09C" className="space-y-3">
        <h2 className="text-[16px] leading-[24px] font-bold text-[var(--pol-light-text-primary)]">
          پیشنهادهای پذیرش جزئی تأمین‌کننده
        </h2>
        {(() => {
          const proposals = deriveProposals(events);
          const openOnes = proposals.filter((p) => p.status === "PENDING");
          const canReview =
            openOnes.length > 0 &&
            order.order_status != null &&
            ["SUBMITTED", "ACCEPTED", "PARTIALLY_ACCEPTED"].includes(order.order_status);
          if (proposals.length === 0) {
            return (
              <Card variant="subtle" className="p-5">
                <EmptyState
                  title="پیشنهاد پذیرش جزئی ثبت نشده"
                  description="تأمین‌کننده هنوز کسری موجودی یا تغییر تعدادی برای این سفارش پیشنهاد نداده است."
                />
              </Card>
            );
          }
          return (
            <div className="space-y-3">
              {proposals.map((p) => (
                <Card key={p.proposal_id} className="p-4 sm:p-5 shadow-xs space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--pol-light-border-subtle)] pb-3">
                    <div className="flex items-center gap-2">
                      <StatusChip
                        tone={
                          p.status === "ACCEPTED"
                            ? "success"
                            : p.status === "DECLINED"
                              ? "danger"
                              : "warning"
                        }
                      >
                        {p.status === "ACCEPTED"
                          ? "پذیرفته‌شده توسط شما"
                          : p.status === "DECLINED"
                            ? "ردشده توسط شما"
                            : "در انتظار بررسی و تصمیم شما"}
                      </StatusChip>
                      <span className="font-mono text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                        شناسه: {p.proposal_id.slice(0, 10)}…
                      </span>
                    </div>
                    <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                      {formatDateTime(p.proposed_at)}
                    </span>
                  </div>

                  {p.items.length > 0 ? (
                    <div className="rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-3 border border-[var(--pol-light-border-subtle)] space-y-1.5">
                      {p.items.map((line) => {
                        const item = items.find((i) => i.id === line.order_item_id);
                        return (
                          <div
                            key={line.order_item_id || `${p.proposal_id}-line`}
                            className="flex flex-wrap items-center justify-between text-[13px]"
                          >
                            <span className="font-medium text-[var(--pol-light-text-primary)]">
                              {item?.product_name_snapshot ?? line.order_item_id.slice(0, 8)}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="text-[var(--pol-light-text-secondary)]">
                                پذیرفته:{" "}
                                <strong className="text-[var(--pol-light-text-primary)]">
                                  {line.accepted_quantity != null
                                    ? Number(line.accepted_quantity).toLocaleString("fa-IR")
                                    : "—"}
                                </strong>
                                {item?.ordered_quantity != null
                                  ? ` از ${Number(item.ordered_quantity).toLocaleString("fa-IR")}`
                                  : ""}
                              </span>
                              {line.reason ? (
                                <span className="rounded-md bg-[var(--pol-light-surface-default)] px-2 py-0.5 text-[11px] text-[var(--pol-light-text-muted)] border border-[var(--pol-light-border-subtle)]">
                                  علت: {line.reason}
                                </span>
                              ) : null}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : null}

                  {canReview && p.status === "PENDING" ? (
                    <div className="flex flex-wrap gap-2 pt-2 border-t border-[var(--pol-light-border-subtle)]">
                      <Button
                        size="sm"
                        loading={acting === `approve:${p.proposal_id}`}
                        disabled={acting !== null}
                        onClick={() => void approveProposal(p.proposal_id)}
                      >
                        تأیید پذیرش جزئی
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          setDeclineOpen((cur) => (cur === p.proposal_id ? null : p.proposal_id));
                          setDeclineReason("");
                        }}
                        aria-expanded={declineOpen === p.proposal_id}
                      >
                        رد پیشنهاد تأمین‌کننده
                      </Button>
                    </div>
                  ) : null}

                  {declineOpen === p.proposal_id ? (
                    <div className="mt-3 space-y-3 rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-3 border border-[var(--pol-light-border-subtle)]">
                      <Field
                        label="دلیل رد پیشنهاد"
                        value={declineReason}
                        onChange={(e) => setDeclineReason(e.target.value)}
                        hint="اختیاری — حداکثر ۱۰۰۰ نویسه"
                        maxLength={1000}
                        placeholder="مثلاً: تعداد کمتر برای فروشگاه صرفه اقتصادی ندارد…"
                      />
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          loading={acting === `decline:${p.proposal_id}`}
                          disabled={acting !== null}
                          onClick={() => void declineProposal(p.proposal_id)}
                        >
                          تأیید رد پیشنهاد
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => setDeclineOpen(null)}
                        >
                          انصراف
                        </Button>
                      </div>
                    </div>
                  ) : null}
                </Card>
              ))}
            </div>
          );
        })()}
      </section>

      {/* Delivery Tracking (R-09D) */}
      <section aria-label="پیگیری ارسال" data-screen="R-09D" className="space-y-3">
        <h2 className="text-[16px] leading-[24px] font-bold text-[var(--pol-light-text-primary)]">
          پیگیری و مشخصات ارسال
        </h2>
        {deliveryMissing || !delivery ? (
          <Card variant="subtle" className="p-5">
            <EmptyState
              title="هنوز ارسالی ثبت نشده است"
              description="پس از آماده‌سازی کالا توسط تأمین‌کننده و تخصیص راننده، اطلاعات باربری و خودرو در این بخش نمایش می‌یابد."
            />
          </Card>
        ) : (
          <Card className="p-5 shadow-xs">
            <dl className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
              <div className="rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-3 border border-[var(--pol-light-border-subtle)]">
                <dt className="text-[12px] text-[var(--pol-light-text-muted)]">وضعیت جاری ارسال</dt>
                <dd className="mt-1">
                  <StatusChip
                    tone={
                      DELIVERY_STATUS_TONE[delivery.delivery_status ?? ""] ?? "neutral"
                    }
                  >
                    {DELIVERY_STATUS_LABEL[delivery.delivery_status ?? ""] ??
                      delivery.delivery_status ??
                      "—"}
                  </StatusChip>
                </dd>
              </div>

              <div className="rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-3 border border-[var(--pol-light-border-subtle)]">
                <dt className="text-[12px] text-[var(--pol-light-text-muted)]">نام و پلاک راننده</dt>
                <dd className="mt-1 text-[13px] font-bold text-[var(--pol-light-text-primary)]">
                  {delivery.driver_name ?? "—"}
                  {delivery.vehicle_plate ? (
                    <span className="ms-2 rounded-md bg-[var(--pol-light-surface-default)] px-2 py-0.5 font-mono text-[11px] text-[var(--pol-light-text-secondary)] border border-[var(--pol-light-border-subtle)]" dir="ltr">
                      {delivery.vehicle_plate}
                    </span>
                  ) : null}
                </dd>
              </div>

              <div className="rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-3 border border-[var(--pol-light-border-subtle)]">
                <dt className="text-[12px] text-[var(--pol-light-text-muted)]">شماره تماس راننده</dt>
                <dd className="mt-1 text-[13px] font-bold text-[var(--pol-light-text-primary)] font-mono" dir="ltr">
                  {delivery.driver_phone ?? "—"}
                </dd>
              </div>

              <div className="rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-3 border border-[var(--pol-light-border-subtle)]">
                <dt className="text-[12px] text-[var(--pol-light-text-muted)]">زمان خروج و ارسال</dt>
                <dd className="mt-1 text-[13px] text-[var(--pol-light-text-primary)]">
                  {formatDateTime(delivery.dispatched_at)}
                </dd>
              </div>

              <div className="rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-3 border border-[var(--pol-light-border-subtle)]">
                <dt className="text-[12px] text-[var(--pol-light-text-muted)]">زمان تحویل قطعی</dt>
                <dd className="mt-1 text-[13px] text-[var(--pol-light-text-primary)]">
                  {formatDateTime(delivery.delivered_at)}
                </dd>
              </div>
            </dl>
          </Card>
        )}
      </section>

      {/* Receiver Handoff & Confirmation (R-09E) */}
      <section aria-label="تحویل و رسید" data-screen="R-09E" className="space-y-3">
        <h2 className="text-[16px] leading-[24px] font-bold text-[var(--pol-light-text-primary)]">
          رسید تحویل و تأیید گیرنده (Proof of Delivery)
        </h2>
        {proof && proof.id ? (
          <Card className="p-5 shadow-xs">
            <dl className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
              <div className="rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-3 border border-[var(--pol-light-border-subtle)]">
                <dt className="text-[12px] text-[var(--pol-light-text-muted)]">نام تحویل‌گیرنده</dt>
                <dd className="mt-1 text-[13px] font-bold text-[var(--pol-light-text-primary)]">
                  {proof.accepted_by_name ?? "—"}
                </dd>
              </div>

              <div className="rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-3 border border-[var(--pol-light-border-subtle)]">
                <dt className="text-[12px] text-[var(--pol-light-text-muted)]">زمان ثبت تحویل</dt>
                <dd className="mt-1 text-[13px] text-[var(--pol-light-text-primary)]">
                  {formatDateTime(proof.accepted_at)}
                </dd>
              </div>

              <div className="rounded-[8px] bg-[var(--pol-light-surface-subtle)] p-3 border border-[var(--pol-light-border-subtle)]">
                <dt className="text-[12px] text-[var(--pol-light-text-muted)]">تأییدیه احراز هویت پیامکی (OTP)</dt>
                <dd className="mt-1">
                  <StatusChip tone={proof.otp_verified ? "success" : "neutral"}>
                    {proof.otp_verified ? "تأییدشده با کد OTP" : "ثبت بدون OTP"}
                  </StatusChip>
                </dd>
              </div>

              {proof.issue_reported_at_delivery ? (
                <div className="sm:col-span-2 md:col-span-3 rounded-[8px] bg-[var(--pol-light-warning)]/10 p-3 border border-[var(--pol-light-warning)]/30">
                  <dt className="text-[12px] font-bold text-[var(--pol-light-warning)]">
                    مشکل گزارش‌شده در هنگام تحویل:
                  </dt>
                  <dd className="mt-1 text-[13px] text-[var(--pol-light-text-primary)]">
                    {proof.issue_reported_at_delivery}
                  </dd>
                </div>
              ) : null}
            </dl>
          </Card>
        ) : (
          <Card variant="subtle" className="p-5">
            <EmptyState
              title="رسید قطعی تحویل هنوز ثبت نشده است"
              description={
                proofMissing
                  ? "پس از دریافت بار در مقصد، می‌توانید تحویل را با کد ۴ رقمی پیامک‌شده تأیید نمایید."
                  : undefined
              }
            />
          </Card>
        )}

        {order.order_status === "DISPATCHED" || order.order_status === "DELIVERED" ? (
          <Card className="p-5 shadow-xs border-[var(--pol-light-brand-primary)]/30 space-y-4">
            <div>
              <h3 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                تأیید تحویل سفارش توسط گیرنده
              </h3>
              <p className="mt-0.5 text-[12px] text-[var(--pol-light-text-muted)]">
                کد پیامک‌شده ۴ رقمی ارسال را در کادر زیر وارد کنید و دکمه تأیید تحویل را بفشارید.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <Field
                label="نام شخص تحویل‌گیرنده"
                value={recipientName}
                onChange={(e) => setRecipientName(e.target.value)}
                maxLength={200}
                hint="اختیاری — مثلاً متصدی فروشگاه"
                placeholder="نام و نام خانوادگی…"
              />
              <Field
                label="کد ۴ رقمی OTP"
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ""))}
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={4}
                hint="کد ۴ رقمی ارسال‌شده به تلفن همراه گیرنده"
                placeholder="----"
              />
            </div>

            <Field
              label="شرح مشکل در صورت مغایرت یا آسیب بار"
              value={issueReported}
              onChange={(e) => setIssueReported(e.target.value)}
              maxLength={500}
              hint="اختیاری — در صورت کسری کارتن یا شکستگی کالا شرح دهید"
              placeholder="توضیحات مغایرت در هنگام تحویل…"
            />

            <div className="flex gap-2 pt-1">
              <Button
                loading={acting === "deliver"}
                disabled={acting !== null}
                onClick={() => void confirmDelivery()}
              >
                تأیید و ثبت نهایی تحویل سفارش
              </Button>
            </div>
          </Card>
        ) : null}
      </section>

      {/* Order Events Timeline */}
      <section aria-label="خط زمانی سفارش" className="space-y-3">
        <h2 className="text-[16px] leading-[24px] font-bold text-[var(--pol-light-text-primary)]">
          خط زمانی رویدادهای سفارش ({events.length.toLocaleString("fa-IR")} رویداد)
        </h2>
        {events.length === 0 ? (
          <Card variant="subtle" className="p-5">
            <EmptyState title="رویدادی ثبت نشده است" description="هنوز هیچ تغییر وضعیتی در چرخه این سفارش روی نداده است." />
          </Card>
        ) : (
          <Card className="p-5 shadow-xs">
            <ol className="relative space-y-4 border-s-2 border-[var(--pol-light-border-subtle)] ps-5 ms-2">
              {events.map((ev) => (
                <li key={ev.id} className="relative">
                  <span
                    aria-hidden
                    className="absolute -start-[27px] top-1.5 size-3 rounded-full bg-[var(--pol-light-brand-primary)] ring-4 ring-[var(--pol-light-surface-default)]"
                  />
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-[13px] font-bold text-[var(--pol-light-text-primary)]">
                        {ev.event_type ?? "رویداد"}
                      </span>
                      {ev.from_status || ev.to_status ? (
                        <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-mono text-[var(--pol-light-text-secondary)] border border-[var(--pol-light-border-subtle)]" dir="ltr">
                          {ev.from_status ?? "∅"} → {ev.to_status ?? "∅"}
                        </span>
                      ) : null}
                    </div>
                    <span className="text-[11px] font-medium text-[var(--pol-light-text-muted)]">
                      {formatDateTime(ev.created_at)}
                    </span>
                  </div>
                </li>
              ))}
            </ol>
          </Card>
        )}
      </section>
    </div>
  );
}
