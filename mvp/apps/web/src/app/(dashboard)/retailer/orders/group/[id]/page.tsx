"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Button, Card, EmptyState, ErrorState, Skeleton, StatusChip } from "@pol/ui";
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
        <Card className="p-5">
          <Skeleton lines={3} />
        </Card>
        <Card className="p-5">
          <Skeleton lines={5} />
        </Card>
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
    <div className="space-y-6 pb-10">
      <header className="flex flex-wrap items-start justify-between gap-4 border-b border-[var(--pol-light-border-subtle)] pb-5">
        <div>
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            جزئیات گروه سفارش
          </h1>
          <p className="mt-1 flex flex-wrap items-center gap-2">
            <span className="font-mono text-[14px] font-bold text-[var(--pol-light-text-primary)]" dir="ltr">
              {group.id}
            </span>
            <span className="text-[12px] text-[var(--pol-light-text-muted)]">
              · ثبت‌شده در {formatDateTime(group.created_at)}
            </span>
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="secondary" size="sm" onClick={() => void load()}>
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

      {/* Group Summary Card */}
      <Card className="p-5 shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <StatusChip tone={groupStatusTone[status] ?? "neutral"}>
              {groupStatusLabel[status] ?? status ?? "—"}
            </StatusChip>
            <span className="text-[13px] font-medium text-[var(--pol-light-text-secondary)]">
              {group.group_order_count != null
                ? `${group.group_order_count.toLocaleString("fa-IR")} سفارش تفکیک‌شده`
                : `${children.length.toLocaleString("fa-IR")} سفارش تفکیک‌شده`}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[13px] text-[var(--pol-light-text-muted)]">مجموع کل گروه:</span>
            <span className="text-[18px] font-bold text-[var(--pol-light-brand-primary)]">
              {formatToman(group.group_total_toman)}
            </span>
          </div>
        </div>

        {group.delivery_address ? (
          <div className="mt-3 pt-3 border-t border-[var(--pol-light-border-subtle)] text-[12px] text-[var(--pol-light-text-secondary)]">
            <span className="font-semibold text-[var(--pol-light-text-primary)]">نشانی تحویل مشترک: </span>
            <span>{group.delivery_address}</span>
          </div>
        ) : null}
      </Card>

      {/* Child Orders */}
      <section aria-label="سفارش‌های گروه" className="space-y-3">
        <h2 className="text-[16px] leading-[24px] font-bold text-[var(--pol-light-text-primary)]">
          سفارش‌های تفکیک‌شده در این گروه ({children.length.toLocaleString("fa-IR")})
        </h2>
        {children.length === 0 ? (
          <Card variant="subtle" className="p-5">
            <EmptyState title="سفارشی در این گروه یافت نشد" />
          </Card>
        ) : (
          <div className="space-y-3">
            {children.map((o) => (
              <Card
                key={String(o.id)}
                variant="interactive"
                className="p-4 sm:p-5 transition-all duration-[160ms] hover:border-[var(--pol-light-brand-primary)]/40 hover:shadow-card"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--pol-light-border-subtle)] pb-3">
                  <div className="flex items-center gap-2">
                    <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                      {orderStatusLabel[o.order_status ?? ""] ?? o.order_status ?? "—"}
                    </StatusChip>
                    {o.dispute_status && o.dispute_status !== "NONE" ? (
                      <StatusChip tone="danger">اختلاف</StatusChip>
                    ) : null}
                    {o.vendor_name ? (
                      <span className="font-bold text-[13px] text-[var(--pol-light-text-primary)]">
                        تأمین‌کننده: {o.vendor_name}
                      </span>
                    ) : null}
                  </div>
                  <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(o.created_at)}
                  </span>
                </div>

                <div className="mt-3 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-[12px] text-[var(--pol-light-text-muted)]">شماره سفارش:</span>
                    <Link
                      href={`/retailer/orders/${o.id}`}
                      className="font-mono text-[14px] font-bold text-[var(--pol-light-brand-primary)] hover:underline"
                      dir="ltr"
                    >
                      {o.order_number ?? String(o.id)}
                    </Link>
                  </div>

                  <span className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                    {formatToman(o.total_amount_toman)}
                  </span>
                </div>

                <div className="mt-3 pt-3 border-t border-[var(--pol-light-border-subtle)] flex justify-end">
                  <Link
                    href={`/retailer/orders/${o.id}`}
                    className="text-[12px] font-semibold text-[var(--pol-light-brand-primary)] hover:underline"
                  >
                    مشاهده جزئیات سفارش تأمین‌کننده ←
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
