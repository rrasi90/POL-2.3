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
        <Card className="p-5">
          <Skeleton lines={4} />
        </Card>
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
    <div className="space-y-6 pb-10">
      <header className="flex flex-wrap items-start justify-between gap-4 border-b border-[var(--pol-light-border-subtle)] pb-5">
        <div>
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            بازگشت کالا و حل اختلاف
          </h1>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)] font-mono" dir="ltr">
            سفارش #{orderId}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button size="sm" variant={returnOpen ? "ghost" : "secondary"} onClick={() => setReturnOpen((v) => !v)}>
            {returnOpen ? "بستن فرم مرجوعی" : "+ ثبت درخواست مرجوعی"}
          </Button>
          <Button size="sm" variant={disputeOpen ? "ghost" : "secondary"} onClick={() => setDisputeOpen((v) => !v)}>
            {disputeOpen ? "بستن فرم اختلاف" : "+ ثبت اختلاف رسمی"}
          </Button>
          <Link
            href={`/retailer/orders/${orderId}`}
            className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[12px] font-medium text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)]"
          >
            ← بازگشت به سفارش
          </Link>
        </div>
      </header>

      {/* Return Request Modal/Card */}
      {returnOpen ? (
        <Card className="p-5 shadow-xs border-[var(--pol-light-brand-primary)]/40 space-y-4">
          <div>
            <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
              ثبت درخواست مرجوعی کالا
            </h2>
            <p className="text-[12px] text-[var(--pol-light-text-secondary)]">
              در صورت آسیب‌دیدگی کارتن، انقضای تاریخ مصرف یا مغایرت قلم دریافتی ثبت کنید.
            </p>
          </div>

          {returnError ? (
            <ErrorState title="ثبت مرجوعی ناموفق بود" description={returnError} />
          ) : null}

          <div className="grid gap-3 sm:grid-cols-3">
            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="return-reason"
                className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]"
              >
                علت مرجوعی
              </label>
              <select
                id="return-reason"
                className="h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 text-[14px] text-[var(--pol-light-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)] shadow-2xs"
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
              label="تعداد کارتن یا بسته"
              type="number"
              min={1}
              value={returnForm.quantity}
              onChange={(e) => setReturnForm((f) => ({ ...f, quantity: e.target.value }))}
              required
            />
            <Field
              label="توضیحات تکمیلی"
              value={returnForm.reason}
              onChange={(e) => setReturnForm((f) => ({ ...f, reason: e.target.value }))}
              hint="اختیاری — حداکثر ۵۰۰ نویسه"
              maxLength={500}
              placeholder="توضیح آسیب یا عدم تطابق…"
            />
          </div>

          <div className="flex gap-2 pt-2">
            <Button loading={returning} onClick={() => void createReturn()}>
              ثبت نهایی درخواست مرجوعی
            </Button>
            <Button variant="ghost" onClick={() => setReturnOpen(false)}>
              انصراف
            </Button>
          </div>
        </Card>
      ) : null}

      {/* Dispute Modal/Card */}
      {disputeOpen ? (
        <Card className="p-5 shadow-xs border-[var(--pol-light-semantic-danger)]/40 space-y-4">
          <div>
            <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
              ثبت اختلاف رسمی (Dispute)
            </h2>
            <p className="text-[12px] text-[var(--pol-light-text-secondary)]">
              در صورت عدم توافق با فروشنده یا بروز خطای مالی، موضوع به واحد عملیات پُل ارجاع می‌شود.
            </p>
          </div>

          {disputeError ? (
            <ErrorState title="ثبت اختلاف ناموفق بود" description={disputeError} />
          ) : null}

          <div className="grid gap-3 sm:grid-cols-2">
            <Field
              label="عنوان دلیل اختلاف"
              value={disputeForm.reason}
              onChange={(e) => setDisputeForm((f) => ({ ...f, reason: e.target.value }))}
              required
              maxLength={200}
              placeholder="مثلاً: مغایرت در فاکتور تسویه حساب…"
            />
            <Field
              label="شرح کامل اختلاف"
              value={disputeForm.description}
              onChange={(e) =>
                setDisputeForm((f) => ({ ...f, description: e.target.value }))
              }
              hint="اختیاری — حداکثر ۲۰۰۰ نویسه"
              maxLength={2000}
              placeholder="جزئیات پیگیری و تماس‌های انجام‌شده…"
            />
          </div>

          <div className="flex gap-2 pt-2">
            <Button loading={disputing} onClick={() => void createDispute()}>
              ثبت و ارجاع به بازرسی پُل
            </Button>
            <Button variant="ghost" onClick={() => setDisputeOpen(false)}>
              انصراف
            </Button>
          </div>
        </Card>
      ) : null}

      {/* Returns List */}
      <section aria-label="مرجوعی‌ها" className="space-y-3">
        <h2 className="text-[16px] leading-[24px] font-bold text-[var(--pol-light-text-primary)]">
          درخواست‌های مرجوعی ({returns.length.toLocaleString("fa-IR")})
        </h2>
        {returns.length === 0 ? (
          <Card variant="subtle" className="p-5">
            <EmptyState
              title="مرجوعی ثبت نشده است"
              description="برای این سفارش تاکنون هیچ درخواست مرجوعی ثبت نگردیده است."
            />
          </Card>
        ) : (
          <div className="space-y-3">
            {returns.map((r) => (
              <Card key={String(r.id)} className="p-4 sm:p-5 shadow-xs space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--pol-light-border-subtle)] pb-2.5">
                  <div className="flex items-center gap-2">
                    <StatusChip tone={returnStatusTone[r.status ?? ""] ?? "neutral"}>
                      {returnStatusLabel[r.status ?? ""] ?? r.status ?? "—"}
                    </StatusChip>
                    {r.reason_code ? (
                      <span className="font-mono text-[11px] rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[var(--pol-light-text-secondary)] border border-[var(--pol-light-border-subtle)]" dir="ltr">
                        {r.reason_code}
                      </span>
                    ) : null}
                  </div>
                  <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(r.created_at)}
                  </span>
                </div>

                {r.reason ? (
                  <p className="text-[13px] text-[var(--pol-light-text-secondary)]">
                    علت: {r.reason}
                  </p>
                ) : null}

                <div className="flex flex-wrap items-center justify-between gap-3 text-[13px] pt-1">
                  <div className="flex items-center gap-3">
                    {r.quantity != null ? (
                      <span className="font-medium text-[var(--pol-light-text-primary)]">
                        تعداد مرجوعی: {Number(r.quantity).toLocaleString("fa-IR")}
                      </span>
                    ) : null}
                    {r.requested_amount_toman != null ? (
                      <span className="font-bold text-[var(--pol-light-brand-primary)]">
                        مبلغ: {formatToman(r.requested_amount_toman)}
                      </span>
                    ) : null}
                  </div>

                  {r.resolution_note ? (
                    <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                      نتیجه: {r.resolution_note}
                    </span>
                  ) : null}
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>

      {/* Disputes List */}
      <section aria-label="اختلاف‌ها" className="space-y-3">
        <h2 className="text-[16px] leading-[24px] font-bold text-[var(--pol-light-text-primary)]">
          اختلاف‌های ثبت‌شده ({disputes.length.toLocaleString("fa-IR")})
        </h2>
        {disputes.length === 0 ? (
          <Card variant="subtle" className="p-5">
            <EmptyState
              title="اختلافی برای این سفارش وجود ندارد"
              description="این سفارش روند طبیعی خود را بدون طرح اختلاف رسمی طی کرده است."
            />
          </Card>
        ) : (
          <div className="space-y-3">
            {disputes.map((d) => (
              <Card key={String(d.id)} className="p-4 sm:p-5 shadow-xs space-y-2 border-[var(--pol-light-semantic-danger)]/20">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--pol-light-border-subtle)] pb-2.5">
                  <StatusChip tone={disputeTone[d.status ?? "NONE"] ?? "neutral"}>
                    {disputeLabel[d.status ?? "NONE"] ?? d.status ?? "—"}
                  </StatusChip>
                  <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(d.created_at)}
                  </span>
                </div>

                <p className="text-[14px] font-bold text-[var(--pol-light-text-primary)]">
                  {d.reason ?? "بدون عنوان"}
                </p>

                {d.description ? (
                  <p className="text-[13px] text-[var(--pol-light-text-secondary)]">
                    {d.description}
                  </p>
                ) : null}

                {d.claimed_amount_toman != null ? (
                  <p className="text-[13px] font-semibold text-[var(--pol-light-semantic-danger)]">
                    مبلغ ادعاشده: {formatToman(d.claimed_amount_toman)}
                  </p>
                ) : null}
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
