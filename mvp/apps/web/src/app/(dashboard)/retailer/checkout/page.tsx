"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
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
import { useBasketStore } from "@/lib/basket";
import { formatToman, groupStatusLabel, groupStatusTone } from "../shared";

interface AllocatedVendor {
  vendor_id: string;
  business_name: string;
  subtotal_toman: number;
  min_order_value_toman: number;
  mov_satisfied: boolean;
  allocated_items_count: number;
}

interface AllocationSummary {
  total_items_requested: number;
  total_items_allocated: number;
  total_items_unfulfilled: number;
  total_amount_toman: number;
  estimated_delivery_cost_toman: number;
}

interface AllocationPreview {
  allocation_plan_id: string;
  strategy: string;
  vendor_count: number;
  allocated_vendors: AllocatedVendor[];
  summary: AllocationSummary;
  unfulfilled_items: {
    product_id: string;
    requested_quantity: number;
    unit: string;
    reason_code: string;
  }[];
}

interface CheckoutResult {
  order_group_id: string;
  group_status: string;
  total_amount_toman: number;
  child_orders: {
    order_id: string;
    vendor_id: string;
    order_status: string;
    subtotal_toman: number;
  }[];
  idempotent_replay: boolean;
}

const paymentMethods = [
  { value: "CASH_ON_DELIVERY", label: "پرداخت نقدی هنگام تحویل" },
  { value: "POS_DRIVER", label: "کارتخوان راننده" },
  { value: "DIRECT_BANK_TRANSFER", label: "انتقال مستقیم بانکی" },
  { value: "CHEQUE_SAYYAD", label: "چک سایبا" },
  { value: "ONLINE_MOCK", label: "پرداخت آنلایل (آزمایشی)" },
] as const;

type PaymentMethod = (typeof paymentMethods)[number]["value"];

type Phase = "loading" | "error" | "ready" | "success";

/**
 * R-07 allocation review + R-08 checkout/confirmation.
 * POST /baskets/{id}/allocation-preview → summary from API only.
 * POST /orders with confirmed plan id + Idempotency-Key header (UUIDv4).
 */
export default function RetailerCheckoutPage() {
  const router = useRouter();
  const lines = useBasketStore((s) => s.lines);
  const serverBasketId = useBasketStore((s) => s.serverBasketId);
  const clearBasket = useBasketStore((s) => s.clear);

  const [phase, setPhase] = useState<Phase>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [preview, setPreview] = useState<AllocationPreview | null>(null);
  const [address, setAddress] = useState("");
  const [payment, setPayment] = useState<PaymentMethod>("CASH_ON_DELIVERY");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [result, setResult] = useState<CheckoutResult | null>(null);
  const idempotencyKey = useState(() =>
    typeof crypto !== "undefined" && crypto.randomUUID
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(16).slice(2)}`,
  )[0];

  const runPreview = useCallback(async () => {
    if (!serverBasketId) {
      setPhase("error");
      setErrorMessage("سبدی در سرور ثبت نشده است. ابتدا سبد را بررسی کنید.");
      return;
    }
    setPhase("loading");
    setErrorMessage(null);
    setSubmitError(null);
    try {
      const data = await getApi().post<AllocationPreview>(
        `/api/v1/baskets/${serverBasketId}/allocation-preview`,
      );
      setPreview(data);
      setPhase("ready");
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : "بررسی تخصیص ناموفق بود",
      );
      setPhase("error");
    }
  }, [serverBasketId]);

  useEffect(() => {
    if (lines.length === 0 && !serverBasketId) {
      setPhase("error");
      setErrorMessage("سبد خرید خالی است.");
      return;
    }
    void runPreview();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [serverBasketId]);

  async function placeOrder(e: React.FormEvent) {
    e.preventDefault();
    setSubmitError(null);
    if (!preview) return;
    const trimmed = address.trim();
    if (trimmed.length < 5) {
      setSubmitError("آدرس تحویل باید حداقل ۵ نویسه باشد.");
      return;
    }
    setSubmitting(true);
    try {
      const data = await getApi().post<CheckoutResult>(
        "/api/v1/orders",
        {
          allocation_plan_id: preview.allocation_plan_id,
          delivery_address: trimmed,
          preferred_payment_method: payment,
        },
        { headers: { "Idempotency-Key": idempotencyKey } },
      );
      setResult(data);
      clearBasket();
      setPhase("success");
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "ثبت سفارش ناموفق بود");
    } finally {
      setSubmitting(false);
    }
  }

  if (phase === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بررسی تخصیص">
        <Skeleton className="h-8 w-56" />
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <Skeleton lines={5} />
        </div>
      </div>
    );
  }

  if (phase === "error") {
    return (
      <div className="space-y-4">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          تسویه حساب
        </h1>
        <EmptyState
          title="برای تسویه، سبد لازم است"
          description={errorMessage ?? "سبد خرید خالی است."}
          actionLabel="رفتن به سبد"
          onAction={() => router.push("/retailer/basket")}
        />
      </div>
    );
  }

  if (phase === "success" && result) {
    return (
      <div className="space-y-6 pb-10">
        <header className="border-b border-[var(--pol-light-border-subtle)] pb-5">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
              <svg className="size-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
                سفارش شما با موفقیت ثبت شد
              </h1>
              <p className="mt-0.5 text-[13px] text-[var(--pol-light-text-secondary)]">
                {result.idempotent_replay
                  ? "این درخواست قبلاً در سیستم ثبت شده بود (پخش هم‌توانی)."
                  : "سفارش شما به تفکیک تأمین‌کنندگان ارسال گردید."}
              </p>
            </div>
          </div>
        </header>

        <Card className="p-5 shadow-xs space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--pol-light-border-subtle)] pb-4">
            <div className="flex items-center gap-2">
              <span className="text-[13px] text-[var(--pol-light-text-muted)]">وضعیت گروه سفارش:</span>
              <StatusChip tone={groupStatusTone[result.group_status] ?? "neutral"}>
                {groupStatusLabel[result.group_status] ?? result.group_status}
              </StatusChip>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[13px] text-[var(--pol-light-text-muted)]">مبلغ کل گروه:</span>
              <span className="text-[16px] font-bold text-[var(--pol-light-text-primary)]">
                {formatToman(result.total_amount_toman)}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between text-[12px] text-[var(--pol-light-text-secondary)]">
            <span>شماره پیگیری گروه سفارش:</span>
            <span dir="ltr" className="font-mono text-[13px] font-bold text-[var(--pol-light-text-primary)]">
              {result.order_group_id}
            </span>
          </div>

          <div>
            <h3 className="text-[13px] font-bold text-[var(--pol-light-text-primary)] mb-2">
              سفارش‌های تفکیک‌شده به تفکیک فروشنده:
            </h3>
            <div className="space-y-2">
              {result.child_orders.map((c) => (
                <div
                  key={c.order_id}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-[8px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-3 text-[13px]"
                >
                  <div className="flex items-center gap-3">
                    <StatusChip tone={c.order_status === "PENDING" ? "warning" : "info"}>
                      {c.order_status}
                    </StatusChip>
                    <Link
                      href={`/retailer/orders/${c.order_id}`}
                      className="font-mono text-[12px] font-bold text-[var(--pol-light-brand-primary)] hover:underline"
                      dir="ltr"
                    >
                      {c.order_id.slice(0, 8)}…
                    </Link>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-[var(--pol-light-text-primary)]">
                      {formatToman(c.subtotal_toman)}
                    </span>
                    <Link
                      href={`/retailer/orders/${c.order_id}`}
                      className="text-[12px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
                    >
                      مشاهده ←
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>

        <div className="flex flex-wrap gap-3 pt-2">
          <Button onClick={() => router.push(`/retailer/orders/group/${result.order_group_id}`)}>
            مشاهده گروه سفارش
          </Button>
          <Button variant="secondary" onClick={() => router.push("/retailer/orders")}>
            فهرست تمام سفارش‌ها
          </Button>
          <Button variant="ghost" onClick={() => router.push("/retailer/catalog")}>
            بازگشت به کاتالوگ
          </Button>
        </div>
      </div>
    );
  }

  if (!preview) {
    return (
      <ErrorState
        title="بررسی تخصیص در دسترس نیست"
        description={errorMessage ?? undefined}
        onRetry={() => void runPreview()}
      />
    );
  }

  return (
    <div className="space-y-6 pb-10">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--pol-light-border-subtle)] pb-5">
        <div>
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            بررسی تخصیص و تسویه حساب
          </h1>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            پیش‌نمایش تخصیص هوشمند کالاها بین تأمین‌کنندگان بر اساس موجودی، حداقل سفارش (MOV) و بهترین قیمت
          </p>
        </div>
        <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-mono text-[var(--pol-light-text-muted)] border border-[var(--pol-light-border-subtle)]" dir="ltr">
          استراتژی: {preview.strategy}
        </span>
      </header>

      {/* Allocation Summary Metrics */}
      <section aria-label="خلاصه تخصیص" className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-4">
          <Card className="p-4 shadow-2xs">
            <p className="text-[12px] text-[var(--pol-light-text-secondary)]">تعداد تأمین‌کنندگان</p>
            <p className="mt-1 text-[20px] font-bold text-[var(--pol-light-text-primary)]">
              {preview.vendor_count.toLocaleString("fa-IR")}
            </p>
          </Card>
          <Card className="p-4 shadow-2xs">
            <p className="text-[12px] text-[var(--pol-light-text-secondary)]">اقلام تخصیص‌یافته</p>
            <p className="mt-1 text-[20px] font-bold text-[var(--pol-light-semantic-success)]">
              {preview.summary.total_items_allocated.toLocaleString("fa-IR")}
            </p>
          </Card>
          <Card className="p-4 shadow-2xs">
            <p className="text-[12px] text-[var(--pol-light-text-secondary)]">اقلام بدون تأمین‌کننده</p>
            <p className="mt-1 text-[20px] font-bold text-[var(--pol-light-semantic-danger)]">
              {preview.summary.total_items_unfulfilled.toLocaleString("fa-IR")}
            </p>
          </Card>
          <Card className="p-4 shadow-2xs">
            <p className="text-[12px] text-[var(--pol-light-text-secondary)]">مبلغ کل برآوردشده</p>
            <p className="mt-1 text-[18px] font-bold text-[var(--pol-light-brand-primary)]">
              {formatToman(preview.summary.total_amount_toman)}
            </p>
          </Card>
        </div>

        {/* Vendor Allocation Breakdown */}
        <Card className="p-5 shadow-xs">
          <div className="flex items-center justify-between border-b border-[var(--pol-light-border-subtle)] pb-3 mb-3">
            <h2 className="text-[14px] font-bold text-[var(--pol-light-text-primary)]">
              تفکیک تأمین‌کنندگان منتخب
            </h2>
            <Button variant="ghost" size="sm" onClick={() => void runPreview()}>
              به‌روزرسانی تخصیص
            </Button>
          </div>

          <div className="space-y-2">
            {preview.allocated_vendors.map((v) => (
              <div
                key={v.vendor_id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-[8px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-3 text-[13px]"
              >
                <div className="flex items-center gap-2">
                  <div className="size-2 rounded-full bg-[var(--pol-light-brand-primary)]" />
                  <span className="font-bold text-[var(--pol-light-text-primary)]">
                    {v.business_name}
                  </span>
                  <StatusChip tone={v.mov_satisfied ? "success" : "warning"}>
                    {v.mov_satisfied ? "حداقل خرید رعایت شده" : "زیر حداقل خرید (MOV)"}
                  </StatusChip>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                    {v.allocated_items_count.toLocaleString("fa-IR")} قلم
                    {v.min_order_value_toman > 0
                      ? ` (کف سفارش: ${formatToman(v.min_order_value_toman)})`
                      : ""}
                  </span>
                  <span className="font-bold text-[var(--pol-light-text-primary)]">
                    {formatToman(v.subtotal_toman)}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {preview.unfulfilled_items.length > 0 ? (
            <div className="mt-4 rounded-[8px] border border-[var(--pol-light-semantic-danger)]/40 bg-[var(--pol-light-surface-subtle)] p-3">
              <p className="text-[13px] font-bold text-[var(--pol-light-semantic-danger)]">
                اقلام بدون تخصیص
              </p>
              <ul className="mt-1.5 space-y-1">
                {preview.unfulfilled_items.map((u, i) => (
                  <li
                    key={`${u.product_id}-${i}`}
                    className="text-[12px] text-[var(--pol-light-text-secondary)] font-mono"
                    dir="ltr"
                  >
                    {u.product_id.slice(0, 8)}… ×{u.requested_quantity} — {u.reason_code}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </Card>
      </section>

      {/* Checkout Form */}
      <section aria-label="تکمیل سفارش">
        <Card className="p-5 shadow-xs">
          <h2 className="text-[16px] leading-[24px] font-bold text-[var(--pol-light-text-primary)] mb-4">
            اطلاعات تحویل و روش پرداخت
          </h2>
          {submitError ? (
            <div className="mb-4">
              <ErrorState title="ثبت سفارش ناموفق بود" description={submitError} />
            </div>
          ) : null}
          <form onSubmit={placeOrder} className="grid max-w-xl gap-4">
            <Field
              label="آدرس دقیق تحویل سفارش"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              required
              minLength={5}
              maxLength={1000}
              hint="حداقل ۵ نویسه — مثلاً اهواز، خیابان نادری، نبش خیابان سعدی، فروشگاه شایان"
              placeholder="استان، شهر، خیابان، پلاک، واحد…"
            />
            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="checkout-payment"
                className="text-[12px] leading-[18px] font-medium text-[var(--pol-light-text-secondary)]"
              >
                روش پرداخت ترجیحی
              </label>
              <select
                id="checkout-payment"
                value={payment}
                onChange={(e) => setPayment(e.target.value as PaymentMethod)}
                className="h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 text-[14px] text-[var(--pol-light-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)] shadow-2xs"
              >
                {paymentMethods.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <Button type="submit" loading={submitting} disabled={submitting}>
                تأیید نهایی و ثبت قطعی سفارش
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => router.push("/retailer/basket")}
                disabled={submitting}
              >
                بازگشت به سبد خرید
              </Button>
            </div>
            <p className="text-[11px] text-[var(--pol-light-text-muted)] font-mono" dir="ltr">
              idempotency_key: {idempotencyKey}
            </p>
          </form>
        </Card>
      </section>
    </div>
  );
}
