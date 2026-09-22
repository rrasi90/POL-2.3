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
      <header className="flex flex-wrap items-start gap-3">
        <div>
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            {TYPE_LABEL[type]} — جزئیات
          </h1>
          <p className="mt-1 flex flex-wrap items-center gap-2">
            <span className="text-[13px] text-[var(--pol-light-text-secondary)]" dir="ltr">
              {str(record.order_number ?? record.case_number, objectIdStr)}
            </span>
            <span className="text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
              {rawType}/{objectId}
            </span>
            <span className="text-[11px] text-[var(--pol-light-text-muted)]">
              {formatDateTime(record.created_at ?? record.opened_at)}
            </span>
          </p>
        </div>
        <div className="ms-auto flex flex-wrap gap-2">
          <Button variant="ghost" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
          <Link
            href="/ops/queues"
            className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
          >
            صف‌ها
          </Link>
        </div>
      </header>

      <section
        aria-label="وضعیت فعلی"
        className="flex flex-wrap items-center gap-2 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
      >
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
        <span className="ms-auto text-[13px] text-[var(--pol-light-text-secondary)]">
          {ageLabel(record.created_at ?? record.opened_at)}{" "}
          <StatusChip tone={ageTone(record.created_at ?? record.opened_at)}>
            سن
          </StatusChip>
        </span>
        {record.total_amount_toman != null ? (
          <span className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
            {formatToman(record.total_amount_toman)}
          </span>
        ) : null}
      </section>

      {actionError ? (
        <ErrorState title="عملیات ناموفق بود" description={actionError} />
      ) : null}

      <section aria-label="فیلدها" className={cardCls}>
        <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
          وضعیت و اطلاعات
        </h2>
        <dl className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(record)
            .filter(([, v]) => v == null || typeof v !== "object")
            .slice(0, 24)
            .map(([k, v]) => (
              <div key={k}>
                <dt className="text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                  {k}
                </dt>
                <dd className="text-[13px] text-[var(--pol-light-text-primary)]" dir="auto">
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

      <section aria-label="لینک‌های مرتبط" className={cardCls}>
        <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
          خرده‌فروش / فروشنده / سفارش
        </h2>
        {links.length === 0 ? (
          <div className="mt-2">
            <EmptyState title="شیء مرتبط یافت نشد" />
          </div>
        ) : (
          <ul className="mt-2 flex flex-wrap gap-2">
            {links.map((l) => (
              <li key={l.href}>
                <Link
                  href={l.href}
                  className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
                >
                  {l.label}
                </Link>
              </li>
            ))}
          </ul>
        )}
        {record.retailer_id || record.vendor_id ? (
          <dl className="mt-3 grid gap-2 sm:grid-cols-2">
            {record.retailer_id ? (
              <div>
                <dt className="text-[11px] text-[var(--pol-light-text-muted)]">retailer_id</dt>
                <dd className="text-[13px] text-[var(--pol-light-text-primary)]" dir="ltr">
                  {String(record.retailer_id)}
                </dd>
              </div>
            ) : null}
            {record.vendor_id ? (
              <div>
                <dt className="text-[11px] text-[var(--pol-light-text-muted)]">vendor_id</dt>
                <dd className="text-[13px] text-[var(--pol-light-text-primary)]" dir="ltr">
                  {String(record.vendor_id)}
                </dd>
              </div>
            ) : null}
          </dl>
        ) : null}
      </section>

      <section aria-label="شواهد" className={cardCls}>
        <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
          شواهد
        </h2>
        {evidenceKeys.length === 0 ? (
          <div className="mt-2">
            <EmptyState
              title="شواهد پیوست ثبت نشده"
              description="فیلد شواهد/پیوست در پاسخ این شیء وجود ندارد."
            />
          </div>
        ) : (
          <dl className="mt-2 space-y-2">
            {evidenceKeys.map((k) => (
              <div key={k}>
                <dt className="text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                  {k}
                </dt>
                <dd className="text-[13px] text-[var(--pol-light-text-primary)]">
                  {typeof record[k] === "object"
                    ? JSON.stringify(record[k])
                    : String(record[k])}
                </dd>
              </div>
            ))}
          </dl>
        )}
      </section>

      <section aria-label="اقدامات مجاز" className={cardCls}>
        <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
          اقدامات مجاز
        </h2>
        {actions.length === 0 ? (
          <div className="mt-2">
            <EmptyState
              title="اقدام HTTP برای این شیء تعریف نشده"
              description="اقدام فقط از روی قرارداد واقعی؛ بدون ابداع endpoint."
            />
          </div>
        ) : (
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
        )}
      </section>

      <section aria-label="واگذاری" className={cardCls}>
        <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
          واگذاری
        </h2>
        <p className="mt-2 text-[13px] text-[var(--pol-light-text-secondary)]">
          {assignmentUser ? (
            <span dir="ltr">{assignmentUser}</span>
          ) : (
            "کاربر واگذارشده‌ای در پاسخ ثبت نشده است."
          )}
        </p>
        {record.assigned_organization_id ? (
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]" dir="ltr">
            org: {String(record.assigned_organization_id)}
          </p>
        ) : null}
      </section>

      <section aria-label="گاه‌شمار / ممیزی">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          گاه‌شمار / ممیزی
        </h2>
        {timeline.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="رویدادی در دسترس نیست"
              description="برای این نوع شیء timeline از endpoint واقعی خوانده می‌شود؛ در غیر این صورت خالی است."
            />
          </div>
        ) : (
          <ol className="mt-3 border-s-2 border-[var(--pol-light-border-subtle)] ps-4">
            {timeline.map((ev) => (
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
