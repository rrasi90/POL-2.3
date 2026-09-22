"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Button,
  EmptyState,
  ErrorState,
  Field,
  SearchField,
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
  itemsOf,
  orderStatusLabel,
  orderStatusTone,
  str,
  type LoadState,
} from "../_shared";

interface OrderRow {
  id: string;
  order_number?: string | null;
  order_status?: string | null;
  dispute_status?: string | null;
  created_at?: string | null;
}

interface ReturnRow {
  id: string;
  status?: string | null;
  reason?: string | null;
  created_at?: string | null;
}

interface DisputeRow {
  id: string;
  status?: string | null;
  reason?: string | null;
  created_at?: string | null;
}

export default function OpsRmaPage() {
  const [orders, setOrders] = useState<OrderRow[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [orderId, setOrderId] = useState("");
  const [lookupError, setLookupError] = useState<string | null>(null);
  const [looking, setLooking] = useState(false);
  const [returns, setReturns] = useState<ReturnRow[]>([]);
  const [disputes, setDisputes] = useState<DisputeRow[]>([]);
  const [loadedOrderId, setLoadedOrderId] = useState<string | null>(null);
  const [detailState, setDetailState] = useState<LoadState>("ready");

  const loadOrders = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const data = await getApi().get<unknown>("/api/v1/orders?limit=50&offset=0");
      setOrders(itemsOf<OrderRow>(data, "orders"));
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت سفارش‌ها ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void loadOrders();
  }, [loadOrders]);

  const loadForOrder = useCallback(async (id: string) => {
    setDetailState("loading");
    setLookupError(null);
    try {
      const [r, d] = await Promise.all([
        getApi().get<unknown>(`/api/v1/orders/${id}/returns`),
        getApi().get<unknown>(`/api/v1/orders/${id}/disputes`),
      ]);
      setReturns(itemsOf<ReturnRow>(r, "returns"));
      setDisputes(itemsOf<DisputeRow>(d, "disputes"));
      setLoadedOrderId(id);
      setDetailState("ready");
    } catch (err) {
      setLookupError(err instanceof Error ? err.message : "دریافت مرجوعی/اختلاف ناموفق بود");
      setDetailState("error");
    }
  }, []);

  const filtered = orders.filter((o) => {
    const active =
      (typeof o.dispute_status === "string" &&
        o.dispute_status !== "NONE" &&
        o.dispute_status !== "CLOSED") ||
      (typeof o.order_status === "string" &&
        ["CREATED", "SUBMITTED", "ACCEPTED", "PARTIALLY_ACCEPTED", "PREPARING", "READY", "DISPATCHED"].includes(
          o.order_status,
        ));
    if (!query.trim()) return active || true;
    const q = query.trim().toLowerCase();
    return (
      str(o.order_number, "").toLowerCase().includes(q) || str(o.id, "").toLowerCase().includes(q)
    );
  });

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری RMA">
        <Skeleton className="h-8 w-48" />
        <div className={cardCls}>
          <Skeleton lines={5} />
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت سفارش‌ها ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void loadOrders()}
      />
    );
  }

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          میز RMA / اختلاف
        </h1>
        <StatusChip tone="warning">G-013</StatusChip>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">O-04</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void loadOrders()}>
          به‌روزرسانی
        </Button>
      </header>

      <div className="rounded-[12px] border border-[var(--pol-light-semantic-warning)]/40 bg-[var(--pol-light-surface-default)] p-3">
        <p className="text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          شکاف G-013: لیست سراسری مرجوعی وجود ندارد — فقط{" "}
          <code dir="ltr" className="text-[12px]">
            GET /orders/&#123;order_id&#125;/returns
          </code>{" "}
          و disputes per-order. از فهرست سفارش یا شناسه دستی وارد شوید.
        </p>
      </div>

      <section aria-label="جستجوی شناسه سفارش" className={cardCls}>
        <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
          باز کردن با شناسه سفارش
        </h2>
        <div className="mt-2 flex flex-wrap items-end gap-2">
          <Field
            label="شناسه سفارش"
            value={orderId}
            onChange={(e) => setOrderId(e.target.value)}
            dir="ltr"
            className="max-w-xs flex-1"
          />
          <Button
            size="sm"
            loading={looking}
            disabled={!orderId.trim()}
            onClick={() => {
              if (orderId.trim()) void loadForOrder(orderId.trim());
            }}
          >
            باز کردن
          </Button>
        </div>
        {lookupError ? (
          <div className="mt-3">
            <ErrorState title="دریافت مرجوعی/اختلاف ناموفق بود" description={lookupError} />
          </div>
        ) : null}
      </section>

      <section aria-label="نتیجه بررسی per-order">
        {loadedOrderId ? (
          <div className={cardCls}>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
                سفارش
              </h2>
              <span className="text-[13px] text-[var(--pol-light-text-secondary)]" dir="ltr">
                {loadedOrderId}
              </span>
              <Button
                variant="ghost"
                size="sm"
                className="ms-auto"
                onClick={() => {
                  setLoadedOrderId(null);
                  setReturns([]);
                  setDisputes([]);
                  setLookupError(null);
                }}
              >
                بستن
              </Button>
            </div>

            <div className="mt-3 grid gap-4 sm:grid-cols-2">
              <div>
                <h3 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
                  مرجوعی‌ها
                </h3>
                {detailState === "loading" ? (
                  <div className="mt-2" aria-busy="true">
                    <Skeleton lines={3} />
                  </div>
                ) : returns.length === 0 ? (
                  <p className="mt-2 text-[13px] text-[var(--pol-light-text-secondary)]">
                    مرجوعی ثبت نشده است.
                  </p>
                ) : (
                  <ul role="list" className="mt-2 space-y-2">
                    {returns.map((r) => (
                      <li
                        key={str(r.id)}
                        className="rounded-[8px] border border-[var(--pol-light-border-subtle)] p-3"
                      >
                        <div className="flex flex-wrap items-center gap-2">
                          <StatusChip tone="info">{r.status ?? "—"}</StatusChip>
                          <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                            {formatDateTime(r.created_at)}
                          </span>
                        </div>
                        {r.reason ? (
                          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
                            {r.reason}
                          </p>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div>
                <h3 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
                  اختلاف‌ها
                </h3>
                {detailState === "loading" ? (
                  <div className="mt-2" aria-busy="true">
                    <Skeleton lines={3} />
                  </div>
                ) : disputes.length === 0 ? (
                  <p className="mt-2 text-[13px] text-[var(--pol-light-text-secondary)]">
                    اختلافی ثبت نشده است.
                  </p>
                ) : (
                  <ul role="list" className="mt-2 space-y-2">
                    {disputes.map((d) => (
                      <li
                        key={str(d.id)}
                        className="rounded-[8px] border border-[var(--pol-light-border-subtle)] p-3"
                      >
                        <div className="flex flex-wrap items-center gap-2">
                          <StatusChip tone={disputeStatusTone[d.status ?? ""] ?? "neutral"}>
                            {disputeStatusLabel[d.status ?? ""] ?? d.status ?? "—"}
                          </StatusChip>
                          <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                            {formatDateTime(d.created_at)}
                          </span>
                        </div>
                        {d.reason ? (
                          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
                            {d.reason}
                          </p>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>
        ) : null}
      </section>

      <section aria-label="فهرست سفارش‌ها">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
            سفارش‌ها
          </h2>
          <SearchField
            label="جستجوی سفارش"
            placeholder="شماره سفارش…"
            className="ms-auto w-full max-w-xs"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        {filtered.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="سفارشی یافت نشد"
              description="عبارت جستجو را تغییر دهید."
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {filtered.map((o) => (
              <li key={str(o.id)} className={cardCls}>
                <div className="flex flex-wrap items-center gap-2">
                  <StatusChip tone={orderStatusTone[o.order_status ?? ""] ?? "neutral"}>
                    {orderStatusLabel[o.order_status ?? ""] ?? o.order_status ?? "—"}
                  </StatusChip>
                  <StatusChip tone={disputeStatusTone[o.dispute_status ?? ""] ?? "neutral"}>
                    {disputeStatusLabel[o.dispute_status ?? ""] ?? o.dispute_status ?? "—"}
                  </StatusChip>
                  <StatusChip tone={ageTone(o.created_at)}>{ageLabel(o.created_at)}</StatusChip>
                  <span className="ms-auto flex flex-wrap gap-2">
                    <button
                      type="button"
                      className="text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
                      onClick={() => {
                        setOrderId(str(o.id));
                        void loadForOrder(str(o.id));
                      }}
                    >
                      بررسی مرجوعی/اختلاف
                    </button>
                    <Link
                      href="/ops/queues"
                      className="text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
                    >
                      صفوف
                    </Link>
                  </span>
                </div>
                <p className="mt-1.5 text-[14px] font-semibold text-[var(--pol-light-text-primary)]" dir="ltr">
                  {o.order_number ?? str(o.id)}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
