"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Button,
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
      <div className="space-y-5">
        <header>
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            سفارش ثبت شد
          </h1>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            {result.idempotent_replay
              ? "این درخواست قبلاً ثبت شده بود (پخش هم‌توانی)."
              : "سفارش شما با موفقیت ثبت شد."}
          </p>
        </header>

        <section
          aria-label="خلاصه ثبت سفارش"
          className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
        >
          <div className="flex flex-wrap items-center gap-2">
            <StatusChip tone={groupStatusTone[result.group_status] ?? "neutral"}>
              {groupStatusLabel[result.group_status] ?? result.group_status}
            </StatusChip>
            <span className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
              {formatToman(result.total_amount_toman)}
            </span>
          </div>
          <p className="mt-2 text-[13px] text-[var(--pol-light-text-secondary)]">
            شماره گروه سفارش:{" "}
            <span dir="ltr" className="font-mono text-[12px]">
              {result.order_group_id}
            </span>
          </p>
          <ul role="list" className="mt-3 space-y-2">
            {result.child_orders.map((c) => (
              <li
                key={c.order_id}
                className="flex flex-wrap items-center gap-2 rounded-[8px] border border-[var(--pol-light-border-subtle)] px-3 py-2"
              >
                <StatusChip tone={c.order_status === "PENDING" ? "warning" : "info"}>
                  {c.order_status}
                </StatusChip>
                <Link
                  href={`/retailer/orders/${c.order_id}`}
                  className="text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
                >
                  مشاهده سفارش فروشنده
                </Link>
                <span className="ms-auto text-[13px] text-[var(--pol-light-text-primary)]">
                  {formatToman(c.subtotal_toman)}
                </span>
              </li>
            ))}
          </ul>
        </section>

        <div className="flex flex-wrap gap-2">
          <Button onClick={() => router.push(`/retailer/orders/group/${result.order_group_id}`)}>
            مشاهده گروه سفارش
          </Button>
          <Button variant="secondary" onClick={() => router.push("/retailer/orders")}>
            همه سفارش‌ها
          </Button>
          <Button variant="ghost" onClick={() => router.push("/retailer/catalog")}>
            ادامه خرید
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
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          بررسی تخصیص و تسویه
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]" dir="ltr">
          {preview.strategy}
        </span>
      </header>

      <section
        aria-label="خلاصه تخصیص"
        className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
      >
        <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
          خلاصه تخصیص (از سرور)
        </h2>
        <dl className="mt-3 grid gap-3 sm:grid-cols-4">
          <div>
            <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
              تعداد فروشنده
            </dt>
            <dd className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
              {preview.vendor_count.toLocaleString("fa-IR")}
            </dd>
          </div>
          <div>
            <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
              اقلام تخصیص‌یافته
            </dt>
            <dd className="text-[16px] font-semibold text-[var(--pol-light-semantic-success)]">
              {preview.summary.total_items_allocated.toLocaleString("fa-IR")}
            </dd>
          </div>
          <div>
            <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
              اقلام بدون تخصیص
            </dt>
            <dd className="text-[16px] font-semibold text-[var(--pol-light-semantic-danger)]">
              {preview.summary.total_items_unfulfilled.toLocaleString("fa-IR")}
            </dd>
          </div>
          <div>
            <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
              مبلغ کل
            </dt>
            <dd className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
              {formatToman(preview.summary.total_amount_toman)}
            </dd>
          </div>
        </dl>

        <ul role="list" className="mt-4 space-y-2">
          {preview.allocated_vendors.map((v) => (
            <li
              key={v.vendor_id}
              className="flex flex-wrap items-center gap-2 rounded-[8px] border border-[var(--pol-light-border-subtle)] px-3 py-2"
            >
              <span className="text-[13px] font-medium text-[var(--pol-light-text-primary)]">
                {v.business_name}
              </span>
              <StatusChip tone={v.mov_satisfied ? "success" : "warning"}>
                {v.mov_satisfied ? "حداقل خرید رعایت شده" : "زیر حداقل خرید"}
              </StatusChip>
              <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                {v.allocated_items_count.toLocaleString("fa-IR")} قلم
                {v.min_order_value_toman > 0
                  ? ` · MOV ${formatToman(v.min_order_value_toman)}`
                  : ""}
              </span>
              <span className="ms-auto text-[13px] text-[var(--pol-light-text-primary)]">
                {formatToman(v.subtotal_toman)}
              </span>
            </li>
          ))}
        </ul>

        {preview.unfulfilled_items.length > 0 ? (
          <div className="mt-3 rounded-[8px] border border-[var(--pol-light-semantic-danger)]/40 bg-[var(--pol-light-surface-subtle)] p-3">
            <p className="text-[13px] font-medium text-[var(--pol-light-semantic-danger)]">
              اقلام بدون تخصیص
            </p>
            <ul className="mt-1 space-y-0.5">
              {preview.unfulfilled_items.map((u, i) => (
                <li
                  key={`${u.product_id}-${i}`}
                  className="text-[12px] text-[var(--pol-light-text-secondary)]"
                  dir="ltr"
                >
                  {u.product_id.slice(0, 8)}… ×{u.requested_quantity} — {u.reason_code}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        <div className="mt-3">
          <Button variant="secondary" size="sm" onClick={() => void runPreview()}>
            به‌روزرسانی تخصیص
          </Button>
        </div>
      </section>

      <section aria-label="تکمیل سفارش">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          اطلاعات تحویل و پرداخت
        </h2>
        {submitError ? (
          <div className="mt-3">
            <ErrorState title="ثبت سفارش ناموفق بود" description={submitError} />
          </div>
        ) : null}
        <form onSubmit={placeOrder} className="mt-4 grid max-w-xl gap-4">
          <Field
            label="آدرس تحویل"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            required
            minLength={5}
            maxLength={1000}
            hint="至少 ۵ نویسه — مثلاً نشانی فروشگاه در اهواز"
            placeholder="استان، شهر، خیابان، پلاک…"
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
              className="h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 text-[14px] text-[var(--pol-light-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
            >
              {paymentMethods.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button type="submit" loading={submitting} disabled={submitting}>
              تأیید و ثبت سفارش
            </Button>
            <Button
              type="button"
              variant="ghost"
              onClick={() => router.push("/retailer/basket")}
              disabled={submitting}
            >
              بازگشت به سبد
            </Button>
          </div>
          <p className="text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
            idempotency_key: {idempotencyKey}
          </p>
        </form>
      </section>
    </div>
  );
}
