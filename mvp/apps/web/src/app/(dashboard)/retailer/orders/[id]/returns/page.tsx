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
  asRecordArray,
  disputeLabel,
  disputeTone,
  formatDateTime,
  formatToman,
  returnStatusLabel,
  returnStatusTone,
} from "../../../shared";

interface ReturnRow {
  id: string;
  order_id?: string | null;
  status?: string | null;
  reason?: string | null;
  reason_code?: string | null;
  quantity?: number | null;
  requested_amount_toman?: number | null;
  resolution_note?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

interface DisputeRow {
  id: string;
  order_id?: string | null;
  status?: string | null;
  reason?: string | null;
  description?: string | null;
  claimed_amount_toman?: number | null;
  created_at?: string | null;
  updated_at?: string | null;
}

type LoadState = "loading" | "error" | "ready";

const RETURN_REASONS = [
  "DAMAGED",
  "WRONG_ITEM",
  "MISSING_ITEMS",
  "QUALITY",
  "EXPIRED",
  "OTHER",
] as const;

/**
 * R-11 returns / disputes for one order.
 * POST/GET /orders/{id}/returns, POST/GET /orders/{id}/disputes
 */
export default function RetailerOrderReturnsPage() {
  const params = useParams<{ id: string }>();
  const orderId = params.id;

  const [returns, setReturns] = useState<ReturnRow[]>([]);
  const [disputes, setDisputes] = useState<DisputeRow[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [returnOpen, setReturnOpen] = useState(false);
  const [returnForm, setReturnForm] = useState({ reason_code: "DAMAGED", quantity: "1", reason: "" });
  const [returnError, setReturnError] = useState<string | null>(null);
  const [returning, setReturning] = useState(false);

  const [disputeOpen, setDisputeOpen] = useState(false);
  const [disputeForm, setDisputeForm] = useState({ reason: "", description: "" });
  const [disputeError, setDisputeError] = useState<string | null>(null);
  const [disputing, setDisputing] = useState(false);

  const load = useCallback(async () => {
    if (!orderId) return;
    setState("loading");
    setErrorMessage(null);
    try {
      const [r, d] = await Promise.all([
        getApi().get<unknown>(`/api/v1/orders/${orderId}/returns`),
        getApi().get<unknown>(`/api/v1/orders/${orderId}/disputes`),
      ]);
      setReturns(asRecordArray(r) as unknown as ReturnRow[]);
      setDisputes(asRecordArray(d) as unknown as DisputeRow[]);
      setState("ready");
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : "دریافت مرجوعی‌ها ناموفق بود",
      );
      setState("error");
    }
  }, [orderId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function createReturn() {
    if (!orderId) return;
    const qty = Number(returnForm.quantity);
    if (!Number.isFinite(qty) || qty < 1) {
      setReturnError("تعداد باید عددی بزرگ‌تر از صفر باشد.");
      return;
    }
    setReturning(true);
    setReturnError(null);
    try {
      const body: Record<string, unknown> = {
        reason_code: returnForm.reason_code,
        quantity: qty,
      };
      if (returnForm.reason.trim()) body.reason = returnForm.reason.trim();
      await getApi().post(`/api/v1/orders/${orderId}/returns`, body);
      setReturnOpen(false);
      setReturnForm({ reason_code: "DAMAGED", quantity: "1", reason: "" });
      await load();
    } catch (err) {
      setReturnError(err instanceof Error ? err.message : "ثبت مرجوعی ناموفق بود");
    } finally {
      setReturning(false);
    }
  }

  async function createDispute() {
    if (!orderId || !disputeForm.reason.trim()) {
      setDisputeError("دلیل اختلاف الزامی است.");
      return;
    }
    setDisputing(true);
    setDisputeError(null);
    try {
      const body: Record<string, string> = { reason: disputeForm.reason.trim() };
      if (disputeForm.description.trim())
        body.description = disputeForm.description.trim();
      await getApi().post(`/api/v1/orders/${orderId}/disputes`, body);
      setDisputeOpen(false);
      setDisputeForm({ reason: "", description: "" });
      await load();
    } catch (err) {
      setDisputeError(err instanceof Error ? err.message : "ثبت اختلاف ناموفق بود");
    } finally {
      setDisputing(false);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری مرجوعی‌ها">
        <Skeleton className="h-8 w-64" />
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <Skeleton lines={4} />
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت مرجوعی‌ها و اختلاف‌ها ناموفق بود"
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
            بازگشت کالا و اختلاف
          </h1>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]" dir="ltr">
            order {orderId}
          </p>
        </div>
        <div className="ms-auto flex flex-wrap gap-2">
          <Button size="sm" variant="secondary" onClick={() => setReturnOpen((v) => !v)}>
            {returnOpen ? "بستن فرم" : "درخواست مرجوعی"}
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setDisputeOpen((v) => !v)}>
            {disputeOpen ? "بستن فرم" : "ثبت اختلاف"}
          </Button>
          <Link
            href={`/retailer/orders/${orderId}`}
            className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
          >
            بازگشت به سفارش
          </Link>
        </div>
      </header>

      {returnOpen ? (
        <section
          aria-label="درخواست مرجوعی"
          className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
        >
          <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
            درخواست مرجوعی
          </h2>
          {returnError ? (
            <div className="mt-3">
              <ErrorState title="ثبت مرجوعی ناموفق بود" description={returnError} />
            </div>
          ) : null}
          <div className="mt-3 grid gap-3 sm:grid-cols-3">
            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="return-reason"
                className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]"
              >
                دلیل
              </label>
              <select
                id="return-reason"
                className="h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 text-[14px] text-[var(--pol-light-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
                value={returnForm.reason_code}
                onChange={(e) =>
                  setReturnForm((f) => ({ ...f, reason_code: e.target.value }))
                }
              >
                {RETURN_REASONS.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </div>
            <Field
              label="تعداد"
              type="number"
              min={1}
              value={returnForm.quantity}
              onChange={(e) => setReturnForm((f) => ({ ...f, quantity: e.target.value }))}
              required
            />
            <Field
              label="توضیح"
              value={returnForm.reason}
              onChange={(e) => setReturnForm((f) => ({ ...f, reason: e.target.value }))}
              hint="اختیاری"
              maxLength={500}
            />
          </div>
          <div className="mt-3">
            <Button loading={returning} onClick={() => void createReturn()}>
              ثبت مرجوعی
            </Button>
          </div>
        </section>
      ) : null}

      {disputeOpen ? (
        <section
          aria-label="ثبت اختلاف"
          className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
        >
          <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
            ثبت اختلاف
          </h2>
          {disputeError ? (
            <div className="mt-3">
              <ErrorState title="ثبت اختلاف ناموفق بود" description={disputeError} />
            </div>
          ) : null}
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            <Field
              label="دلیل"
              value={disputeForm.reason}
              onChange={(e) => setDisputeForm((f) => ({ ...f, reason: e.target.value }))}
              required
              maxLength={200}
            />
            <Field
              label="شرح"
              value={disputeForm.description}
              onChange={(e) =>
                setDisputeForm((f) => ({ ...f, description: e.target.value }))
              }
              hint="اختیاری"
              maxLength={2000}
            />
          </div>
          <div className="mt-3">
            <Button loading={disputing} onClick={() => void createDispute()}>
              ثبت اختلاف
            </Button>
          </div>
        </section>
      ) : null}

      <section aria-label="مرجوعی‌ها">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          مرجوعی‌ها
        </h2>
        {returns.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="مرجوعی ثبت نشده"
              description="برای این سفارش درخواست مرجوعی وجود ندارد."
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {returns.map((r) => (
              <li
                key={String(r.id)}
                className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <StatusChip tone={returnStatusTone[r.status ?? ""] ?? "neutral"}>
                    {returnStatusLabel[r.status ?? ""] ?? r.status ?? "—"}
                  </StatusChip>
                  {r.reason_code ? (
                    <span className="text-[12px] text-[var(--pol-light-text-secondary)]" dir="ltr">
                      {r.reason_code}
                    </span>
                  ) : null}
                  <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(r.created_at)}
                  </span>
                </div>
                {r.reason ? (
                  <p className="mt-2 text-[13px] text-[var(--pol-light-text-secondary)]">
                    {r.reason}
                  </p>
                ) : null}
                <div className="mt-2 flex flex-wrap gap-3 text-[13px] text-[var(--pol-light-text-primary)]">
                  {r.quantity != null ? (
                    <span>تعداد: {Number(r.quantity).toLocaleString("fa-IR")}</span>
                  ) : null}
                  {r.requested_amount_toman != null ? (
                    <span>{formatToman(r.requested_amount_toman)}</span>
                  ) : null}
                  {r.resolution_note ? (
                    <span className="text-[var(--pol-light-text-secondary)]">
                      {r.resolution_note}
                    </span>
                  ) : null}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section aria-label="اختلاف‌ها">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          اختلاف‌ها
        </h2>
        {disputes.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="اختلافی ثبت نشده"
              description="برای این سفارش اختلافی وجود ندارد."
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {disputes.map((d) => (
              <li
                key={String(d.id)}
                className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <StatusChip tone={disputeTone[d.status ?? "NONE"] ?? "neutral"}>
                    {disputeLabel[d.status ?? "NONE"] ?? d.status ?? "—"}
                  </StatusChip>
                  <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(d.created_at)}
                  </span>
                </div>
                <p className="mt-2 text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
                  {d.reason ?? "بدون دلیل"}
                </p>
                {d.description ? (
                  <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
                    {d.description}
                  </p>
                ) : null}
                {d.claimed_amount_toman != null ? (
                  <p className="mt-1 text-[13px] text-[var(--pol-light-text-primary)]">
                    مبلغ ادعا: {formatToman(d.claimed_amount_toman)}
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
