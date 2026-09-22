"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Button, EmptyState, ErrorState, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  formatDateTime,
  formatToman,
  groupStatusLabel,
  groupStatusTone,
  orderStatusTone,
  orderStatusLabel,
  asRecordArray,
} from "../../../shared";

interface OrderGroupDetail {
  id: string;
  group_status?: string | null;
  group_total_toman?: number | null;
  group_order_count?: number | null;
  retailer_id?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  delivery_address?: string | null;
}

interface ChildOrder {
  id: string;
  order_number?: string | null;
  order_status?: string | null;
  dispute_status?: string | null;
  total_amount_toman?: number | null;
  vendor_id?: string | null;
  vendor_name?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

type LoadState = "loading" | "error" | "ready";

/**
 * R-09 order group detail.
 * GET /orders/group/{id}, GET /orders/group/{id}/orders
 */
export default function RetailerOrderGroupPage() {
  const params = useParams<{ id: string }>();
  const groupId = params.id;

  const [group, setGroup] = useState<OrderGroupDetail | null>(null);
  const [children, setChildren] = useState<ChildOrder[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!groupId) return;
    setState("loading");
    setErrorMessage(null);
    try {
      const [g, list] = await Promise.all([
        getApi().get<OrderGroupDetail>(`/api/v1/orders/group/${groupId}`),
        getApi().get<unknown>(`/api/v1/orders/group/${groupId}/orders`),
      ]);
      setGroup(g);
      setChildren(asRecordArray(list) as unknown as ChildOrder[]);
      setState("ready");
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : "دریافت گروه سفارش ناموفق بود",
      );
      setState("error");
    }
  }, [groupId]);

  useEffect(() => {
    void load();
  }, [load]);

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری گروه سفارش">
        <Skeleton className="h-8 w-64" />
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <Skeleton lines={3} />
        </div>
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <Skeleton lines={5} />
        </div>
      </div>
    );
  }

  if (state === "error" || !group) {
    return (
      <ErrorState
        title="دریافت گروه سفارش ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  const status = group.group_status ?? "";

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-start gap-3">
        <div>
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            گروه سفارش
          </h1>
          <p className="mt-1 flex flex-wrap items-center gap-2">
            <span className="text-[13px] text-[var(--pol-light-text-secondary)]" dir="ltr">
              {group.id}
            </span>
            <span className="text-[11px] text-[var(--pol-light-text-muted)]">
              {formatDateTime(group.created_at)}
            </span>
          </p>
        </div>
        <div className="ms-auto flex flex-wrap gap-2">
          <Button variant="ghost" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
          <Link
            href="/retailer/orders"
            className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
          >
            همه سفارش‌ها
          </Link>
        </div>
      </header>

      <section
        aria-label="خلاصه گروه"
        className="flex flex-wrap items-center gap-2 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
      >
        <StatusChip tone={groupStatusTone[status] ?? "neutral"}>
          {groupStatusLabel[status] ?? status ?? "—"}
        </StatusChip>
        <span className="text-[13px] text-[var(--pol-light-text-secondary)]">
          {group.group_order_count != null
            ? `${group.group_order_count.toLocaleString("fa-IR")} سفارش`
            : `${children.length.toLocaleString("fa-IR")} سفارش`}
        </span>
        <span className="ms-auto text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
          {formatToman(group.group_total_toman)}
        </span>
      </section>

      {group.delivery_address ? (
        <section
          aria-label="آدرس تحویل"
          className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
        >
          <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
            آدرس تحویل
          </h2>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            {group.delivery_address}
          </p>
        </section>
      ) : null}

      <section aria-label="سفارش‌های گروه">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          سفارش‌های این گروه
        </h2>
        {children.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="سفارشی در این گروه یافت نشد" />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {children.map((o) => (
              <li
                key={String(o.id)}
                className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4 transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                    {orderStatusLabel[o.order_status ?? ""] ?? o.order_status ?? "—"}
                  </StatusChip>
                  {o.dispute_status && o.dispute_status !== "NONE" ? (
                    <StatusChip tone="danger">اختلاف</StatusChip>
                  ) : null}
                  <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(o.created_at)}
                  </span>
                </div>
                <div className="mt-2 flex flex-wrap items-center gap-3">
                  <Link
                    href={`/retailer/orders/${o.id}`}
                    className="text-[14px] font-semibold text-[var(--pol-light-text-primary)] hover:underline"
                    dir="ltr"
                  >
                    {o.order_number ?? String(o.id)}
                  </Link>
                  {o.vendor_name ? (
                    <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
                      {o.vendor_name}
                    </span>
                  ) : null}
                  <span className="ms-auto text-[14px] font-medium text-[var(--pol-light-text-primary)]">
                    {formatToman(o.total_amount_toman)}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
