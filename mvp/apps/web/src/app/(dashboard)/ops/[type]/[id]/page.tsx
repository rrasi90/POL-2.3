"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
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
  ageLabel,
  ageTone,
  cardCls,
  disputeStatusLabel,
  disputeStatusTone,
  formatDateTime,
  formatOperationalStatus,
  formatTimelineEventLabel,
  reconStatusLabel,
  returnStatusLabel,
  formatToman,
  idOf,
  itemsOf,
  orderStatusLabel,
  orderStatusTone,
  str,
  supportPriorityLabel,
  supportPriorityTone,
  supportStatusLabel,
  supportStatusTone,
  type LoadState,
} from "../../_shared";

type ObjectType = "orders" | "support" | "reconciliation" | "returns" | "unknown";

const TYPE_LABEL: Record<ObjectType, string> = {
  orders: "سفارش",
  support: "پشتیبانی",
  reconciliation: "تطبیق مالی",
  returns: "مرجوعی",
  unknown: "شیء",
};

const ORDER_STATUSES = new Set([
  "CREATED",
  "SUBMITTED",
  "ACCEPTED",
  "PARTIALLY_ACCEPTED",
  "REJECTED",
  "PREPARING",
  "READY",
  "DISPATCHED",
  "DELIVERED",
  "CANCELLED",
]);

const SUPPORT_STATUSES = new Set([
  "OPEN",
  "IN_PROGRESS",
  "WAITING_ON_USER",
  "RESOLVED",
  "CLOSED",
]);

function asRecord(v: unknown): Record<string, unknown> | null {
  return v && typeof v === "object" && !Array.isArray(v)
    ? (v as Record<string, unknown>)
    : null;
}

function classifyType(raw: string): ObjectType {
  const t = raw.toLowerCase();
  if (t === "order" || t === "orders") return "orders";
  if (t === "support" || t === "case" || t === "cases") return "support";
  if (t === "recon" || t === "reconciliation" || t === "finance") return "reconciliation";
  if (t === "return" || t === "returns" || t === "rma") return "returns";
  return "unknown";
}

function statusOf(type: ObjectType, rec: Record<string, unknown>): string | null {
  if (type === "orders") return typeof rec.order_status === "string" ? rec.order_status : null;
  if (type === "support") return typeof rec.status === "string" ? rec.status : null;
  if (type === "reconciliation") return typeof rec.status === "string" ? rec.status : null;
  if (type === "returns") return typeof rec.status === "string" ? rec.status : null;
  return null;
}

function relatedLinks(type: ObjectType, rec: Record<string, unknown>): Array<{
  href: string;
  label: string;
}> {
  const links: Array<{ href: string; label: string }> = [];
  const orderId = idOf(rec.id);
  const orderGroupId = idOf(rec.order_group_id);
  const relatedOrderId = idOf(rec.related_order_id);
  if (type === "orders" && orderId) {
    links.push({ href: `/ops/orders/${orderId}`, label: "همان سفارش" });
    if (orderGroupId) {
      links.push({
        href: `/retailer/orders/group/${orderGroupId}`,
        label: "گروه سفارش",
      });
    }
    const retailerId = idOf(rec.retailer_id);
    const vendorId = idOf(rec.vendor_id);
    if (retailerId) links.push({ href: `/ops/users/${retailerId}`, label: "خرده‌فروش" });
    if (vendorId) links.push({ href: `/ops/vendors/${vendorId}`, label: "فروشنده" });
  }
  if (type === "support" && relatedOrderId) {
    links.push({ href: `/ops/orders/${relatedOrderId}`, label: "سفارش مرتبط" });
  }
  if (type === "returns" && orderId) {
    links.push({ href: `/ops/orders/${orderId}`, label: "سفارش مرتبط" });
  }
  return links;
}

function allowedActions(
  type: ObjectType,
  rec: Record<string, unknown>,
): Array<{ id: string; label: string; method: string; path: string; body?: unknown }> {
  if (type === "support") {
    const status = typeof rec.status === "string" ? rec.status : "";
    const transitions: Record<string, string[]> = {
      OPEN: ["IN_PROGRESS", "WAITING_ON_USER", "RESOLVED", "CLOSED"],
      IN_PROGRESS: ["WAITING_ON_USER", "RESOLVED", "CLOSED"],
      WAITING_ON_USER: ["IN_PROGRESS", "RESOLVED", "CLOSED"],
      RESOLVED: ["CLOSED", "IN_PROGRESS"],
      CLOSED: [],
    };
    return (transitions[status] ?? []).map((next) => ({
      id: next,
      label: `انتقال به ${next}`,
      method: "PATCH",
      path: `/api/v1/support/cases/${idOf(rec.id)}`,
      body: { target_status: next },
    }));
  }
  if (type === "orders") {
    const status = typeof rec.order_status === "string" ? rec.order_status : "";
    const acts: Array<{ id: string; label: string; method: string; path: string; body?: unknown }> =
      [];
    if (status === "SUBMITTED") {
      acts.push(
        {
          id: "accept",
          label: "پذیرش",
          method: "POST",
          path: `/api/v1/orders/${idOf(rec.id)}/accept`,
          body: {},
        },
        {
          id: "reject",
          label: "رد",
          method: "POST",
          path: `/api/v1/orders/${idOf(rec.id)}/reject`,
          body: {},
        },
      );
    }
    if (status === "CANCELLED" || status === "REJECTED" || status === "DELIVERED") {
      return acts;
    }
    return acts;
  }
  return [];
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

/**
 * O-03 Object detail shell (doc 22): current state, timeline/audit,
 * linked retailer/vendor/order, evidence, allowed actions, assignment.
 * Route `/ops/[type]/[id]` — type is a path string, never invented.
 */
export default function OpsObjectDetailPage() {
  const params = useParams<{ type: string; id: string }>();
  const rawType = params.type ?? "";
  const objectId = params.id ?? "";
  const type = useMemo(() => classifyType(rawType), [rawType]);

  const [record, setRecord] = useState<Record<string, unknown> | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [acting, setActing] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!objectId || type === "unknown") {
      setState("error");
      setErrorMessage(`نوع شیء «${rawType}» پشتیبانی نمی‌شود`);
      setRecord(null);
      setTimeline([]);
      return;
    }
    setState("loading");
    setErrorMessage(null);
    setActionError(null);
    try {
      let detail: unknown;
      if (type === "orders") {
        const [o, tl] = await Promise.all([
          getApi().get<unknown>(`/api/v1/orders/${objectId}`),
          getApi().get<unknown>(`/api/v1/orders/${objectId}/timeline`).catch(() => null),
        ]);
        detail = o;
        setTimeline(itemsOf<TimelineEvent>(tl, "events"));
      } else if (type === "support") {
        detail = await getApi().get<unknown>(`/api/v1/support/cases/${objectId}`);
        setTimeline([]);
      } else if (type === "reconciliation") {
        detail = await getApi().get<unknown>(`/api/v1/finance/reconciliation/${objectId}`);
        setTimeline([]);
      } else {
        detail = await getApi().get<unknown>(`/api/v1/orders/${objectId}/returns`);
        const rows = itemsOf<Record<string, unknown>>(detail);
        detail = rows[0] ?? detail;
        setTimeline([]);
      }
      const rec = asRecord(detail);
      if (!rec) {
        setState("error");
        setErrorMessage("پاسخ سرور قابل پردازش نیست");
        setRecord(null);
        return;
      }
      setRecord(rec);
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت شیء ناموفق بود");
      setState("error");
      setRecord(null);
    }
  }, [objectId, rawType, type]);

  useEffect(() => {
    void load();
  }, [load]);

  async function runAction(act: { id: string; method: string; path: string; body?: unknown }) {
    setActing(act.id);
    setActionError(null);
    try {
      if (act.method === "PATCH") {
        await getApi().patch(act.path, act.body ?? {});
      } else {
        await getApi().post(act.path, act.body ?? {});
      }
      await load();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "عملیات ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری شیء">
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

  if (state === "error" || !record) {
    return (
      <ErrorState
        title="دریافت شیء ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  const status = statusOf(type, record);
  const objectIdStr = idOf(record.id) || objectId;
  const links = relatedLinks(type, record);
  const actions = allowedActions(type, record);
  const assignmentUser = idOf(record.assigned_to_user_id) || idOf(record.assignee_user_id);
  const evidenceKeys = Object.keys(record).filter((k) =>
    /evidence|proof|attachment|media|document/i.test(k),
  );

  return (
    <div className="space-y-5" data-screen="O-03">
      <header className="flex flex-wrap items-baseline justify-between gap-3 border-b border-[var(--pol-light-border-subtle)] pb-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <Link
              href="/ops/queues"
              className="text-[12px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
            >
              ← بازگشت به صف‌ها
            </Link>
            <span className="text-[var(--pol-light-text-disabled)]">/</span>
            <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              {TYPE_LABEL[type]}
            </span>
          </div>
          <h1 className="mt-2 text-[22px] leading-[30px] font-bold text-[var(--pol-light-text-primary)]">
            جزئیات {TYPE_LABEL[type]}
          </h1>
          <p className="mt-1 flex flex-wrap items-center gap-2 text-[12px]">
            <span className="font-mono font-semibold text-[var(--pol-light-text-primary)]" dir="ltr">
              {str(record.order_number ?? record.case_number, objectIdStr)}
            </span>
            <span className="text-[var(--pol-light-text-muted)]">·</span>
            <span className="font-mono text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
              {rawType}/{objectId}
            </span>
            <span className="text-[var(--pol-light-text-muted)]">·</span>
            <span className="text-[var(--pol-light-text-muted)]">
              ثبت: {formatDateTime(record.created_at ?? record.opened_at)}
            </span>
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="secondary" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
          <Link
            href="/ops/queues"
            className="inline-flex h-8 items-center rounded-lg border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 text-[12px] font-medium text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
          >
            صف‌های کاری
          </Link>
        </div>
      </header>

      {/* Current Status Strip */}
      <section
        aria-label="وضعیت فعلی"
        className="flex flex-wrap items-center gap-3 rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4 shadow-xs"
      >
        <div className="flex flex-wrap items-center gap-2">
          {status ? (
            <StatusChip
              tone={
                type === "orders"
                  ? orderStatusTone[status] ?? "neutral"
                  : type === "support"
                    ? supportStatusTone[status] ?? "neutral"
                    : "neutral"
              }
            >
              {type === "orders"
                ? orderStatusLabel[status] ?? status
                : type === "support"
                  ? supportStatusLabel[status] ?? status
                  : status}
            </StatusChip>
          ) : (
            <StatusChip tone="neutral">{TYPE_LABEL[type]}</StatusChip>
          )}

          {type === "orders" && record.dispute_status ? (
            <StatusChip
              tone={disputeStatusTone[String(record.dispute_status)] ?? "neutral"}
            >
              {disputeStatusLabel[String(record.dispute_status)] ??
                String(record.dispute_status)}
            </StatusChip>
          ) : null}

          {type === "support" && record.priority ? (
            <StatusChip tone={supportPriorityTone[String(record.priority)] ?? "neutral"}>
              {supportPriorityLabel[String(record.priority)] ?? String(record.priority)}
            </StatusChip>
          ) : null}
        </div>

        <div className="ms-auto flex flex-wrap items-center gap-3">
          <span className="flex items-center gap-1.5 text-[12px] text-[var(--pol-light-text-secondary)]">
            <span>سن پرونده:</span>
            <span className="font-medium text-[var(--pol-light-text-primary)]">
              {ageLabel(record.created_at ?? record.opened_at)}
            </span>
            <StatusChip tone={ageTone(record.created_at ?? record.opened_at)}>
              سن
            </StatusChip>
          </span>

          {record.total_amount_toman != null ? (
            <span className="border-s border-[var(--pol-light-border-subtle)] ps-3 font-extrabold tabular-nums text-[16px] text-[var(--pol-light-text-primary)]">
              {formatToman(record.total_amount_toman)}
            </span>
          ) : null}
        </div>
      </section>

      {actionError ? (
        <ErrorState title="عملیات ناموفق بود" description={actionError} />
      ) : null}

      {/* Allowed Actions Bar */}
      {actions.length > 0 ? (
        <section aria-label="اقدامات مجاز" className={cardCls}>
          <h2 className="text-[13px] font-bold text-[var(--pol-light-text-primary)]">
            اقدامات مجاز عملیاتی
          </h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {actions.map((a) => (
              <Button
                key={a.id}
                size="sm"
                variant={a.id === "reject" ? "danger" : "primary"}
                loading={acting === a.id}
                disabled={acting !== null}
                onClick={() => void runAction(a)}
              >
                {a.label}
              </Button>
            ))}
          </div>
        </section>
      ) : null}

      {/* Properties DL */}
      <section aria-label="فیلدها" className={cardCls}>
        <h2 className="border-b border-[var(--pol-light-border-subtle)] pb-2.5 text-[14px] font-bold text-[var(--pol-light-text-primary)]">
          مشخصات و صفات موجودیت
        </h2>
        <dl className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(record)
            .filter(([, v]) => v == null || typeof v !== "object")
            .slice(0, 24)
            .map(([k, v]) => (
              <div key={k} className="rounded-lg border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)]/40 p-2.5">
                <dt className="font-mono text-[11px] font-medium text-[var(--pol-light-text-muted)]" dir="ltr">
                  {k}
                </dt>
                <dd className="mt-1 font-mono text-[13px] font-medium text-[var(--pol-light-text-primary)] break-all" dir="auto">
                  {v == null
                    ? "—"
                    : typeof v === "boolean"
                      ? v
                        ? "true"
                        : "false"
                      : String(v)}
                </dd>
              </div>
            ))}
        </dl>
      </section>

      {/* Related Entities Links */}
      <section aria-label="لینک‌های مرتبط" className={cardCls}>
        <h2 className="border-b border-[var(--pol-light-border-subtle)] pb-2.5 text-[14px] font-bold text-[var(--pol-light-text-primary)]">
          طرف‌های مرتبط (خرده‌فروش / تأمین‌کننده / گروه سفارش)
        </h2>
        {links.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="موجودیت مرتبطی یافت نشد" />
          </div>
        ) : (
          <ul className="mt-3 flex flex-wrap gap-2">
            {links.map((l) => (
              <li key={l.href}>
                <Link
                  href={l.href}
                  className="inline-flex h-8 items-center rounded-lg border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 text-[12px] font-medium text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
                >
                  {l.label}
                </Link>
              </li>
            ))}
          </ul>
        )}
        {record.retailer_id || record.vendor_id ? (
          <div className="mt-3 grid gap-2.5 sm:grid-cols-2">
            {record.retailer_id ? (
              <div className="rounded-lg border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)]/40 p-2.5">
                <span className="block text-[11px] text-[var(--pol-light-text-muted)]">شناسه خرده‌فروش (retailer_id)</span>
                <span className="font-mono text-[12px] font-medium text-[var(--pol-light-text-primary)]" dir="ltr">
                  {String(record.retailer_id)}
                </span>
              </div>
            ) : null}
            {record.vendor_id ? (
              <div className="rounded-lg border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)]/40 p-2.5">
                <span className="block text-[11px] text-[var(--pol-light-text-muted)]">شناسه فروشنده (vendor_id)</span>
                <span className="font-mono text-[12px] font-medium text-[var(--pol-light-text-primary)]" dir="ltr">
                  {String(record.vendor_id)}
                </span>
              </div>
            ) : null}
          </div>
        ) : null}
      </section>

      {/* Evidence Section */}
      <section aria-label="شواهد" className={cardCls}>
        <h2 className="border-b border-[var(--pol-light-border-subtle)] pb-2.5 text-[14px] font-bold text-[var(--pol-light-text-primary)]">
          شواهد و ضمائم پیوست
        </h2>
        {evidenceKeys.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="مدرک یا شاهدی پیوست نشده است"
              description="فیلد پیوست یا شواهد در خروجی این رکورد خالی است."
            />
          </div>
        ) : (
          <dl className="mt-3 space-y-2">
            {evidenceKeys.map((k) => (
              <div key={k} className="rounded-lg border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)]/40 p-2.5">
                <dt className="font-mono text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                  {k}
                </dt>
                <dd className="mt-1 font-mono text-[12px] text-[var(--pol-light-text-primary)] break-all">
                  {typeof record[k] === "object"
                    ? JSON.stringify(record[k])
                    : String(record[k])}
                </dd>
              </div>
            ))}
          </dl>
        )}
      </section>

      {/* Assignment Section */}
      <section aria-label="واگذاری" className={cardCls}>
        <h2 className="border-b border-[var(--pol-light-border-subtle)] pb-2.5 text-[14px] font-bold text-[var(--pol-light-text-primary)]">
          ارجاع و مسئول پرونده
        </h2>
        <div className="mt-3 flex flex-wrap items-center gap-2 text-[13px] text-[var(--pol-light-text-secondary)]">
          <span>کاربر مسئول:</span>
          {assignmentUser ? (
            <span className="font-mono font-medium text-[var(--pol-light-text-primary)]" dir="ltr">{assignmentUser}</span>
          ) : (
            <span className="text-[var(--pol-light-text-muted)]">بدون ارجاع مستقیم</span>
          )}
        </div>
        {record.assigned_organization_id ? (
          <p className="mt-1 font-mono text-[12px] text-[var(--pol-light-text-muted)]" dir="ltr">
            سازمان ارجاع: {String(record.assigned_organization_id)}
          </p>
        ) : null}
      </section>

      {/* Timeline Section */}
      <section aria-label="گاه‌شمار / ممیزی" className={cardCls}>
        <h2 className="border-b border-[var(--pol-light-border-subtle)] pb-2.5 text-[14px] font-bold text-[var(--pol-light-text-primary)]">
          گاه‌شمار و لاگ وقایع (Audit Trail)
        </h2>
        {timeline.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="رویداد ثبتی در دسترس نیست"
              description="گاه‌شمار مستقیماً از لاگ رویدادهای سرور واکشی می‌شود."
            />
          </div>
        ) : (
          <ol className="mt-4 border-s-2 border-[var(--pol-light-border-subtle)] ps-4 space-y-4">
            {timeline.map((ev) => (
              <li key={ev.id} className="relative pb-1">
                <span
                  aria-hidden
                  className="absolute -start-[21px] top-1.5 size-2.5 rounded-full bg-[var(--pol-light-brand-primary)] ring-4 ring-[var(--pol-light-surface-default)]"
                />
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-[13px] font-semibold text-[var(--pol-light-text-primary)]">
                      {formatTimelineEventLabel(ev.event_type)}
                    </span>
                    {ev.from_status || ev.to_status ? (
                      <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 font-mono text-[11px] text-[var(--pol-light-text-secondary)]" dir="ltr">
                        {formatOperationalStatus(ev.from_status, "∅")} → {formatOperationalStatus(ev.to_status, "∅")}
                      </span>
                    ) : null}
                  </div>
                  <span className="text-[11px] text-[var(--pol-light-text-muted)]">
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
