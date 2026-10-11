"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  QtyStepper,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { useBasketStore, type BasketLine } from "@/lib/basket";

interface BasketCreateResult {
  basket_id: string;
  version: number;
  status: string;
}

interface BasketItemResult {
  basket_id: string;
  version: number;
  status: string;
}

/**
 * R-06 Multi-vendor basket (D-014).
 * Lines live in localStorage (key pol.basket) — G-012 client cache, presentation only.
 * Server basket is created only when the retailer reviews/confirms the basket.
 * Multi-vendor grouping here is a client-side preview of entered lines;
 * the authoritative split comes from allocation-preview on checkout (R-07).
 */
export default function RetailerBasketPage() {
  const router = useRouter();
  const lines = useBasketStore((s) => s.lines);
  const setQuantity = useBasketStore((s) => s.setQuantity);
  const removeLine = useBasketStore((s) => s.removeLine);
  const clear = useBasketStore((s) => s.clear);
  const serverBasketId = useBasketStore((s) => s.serverBasketId);
  const setServerBasket = useBasketStore((s) => s.setServerBasket);

  const [syncing, setSyncing] = useState(false);
  const [syncError, setSyncError] = useState<string | null>(null);
  const [synced, setSynced] = useState(false);

  const groupPreview = useMemo(() => {
    // Presentation-only grouping of entered lines by vendor_hint if present.
    // Real multi-vendor split is returned by POST /baskets/{id}/allocation-preview.
    const byVendor = new Map<string, BasketLine[]>();
    for (const line of lines) {
      const key = (line as BasketLine & { vendor_hint?: string }).vendor_hint ?? "پس از تخصیص";
      const bucket = byVendor.get(key) ?? [];
      bucket.push(line);
      byVendor.set(key, bucket);
    }
    return Array.from(byVendor.entries());
  }, [lines]);

  async function pushToServer(): Promise<boolean> {
    if (lines.length === 0) {
      setSyncError("سبد خرید خالی است.");
      return false;
    }
    setSyncing(true);
    setSyncError(null);
    setSynced(false);
    try {
      const created = await getApi().post<BasketCreateResult>("/api/v1/baskets");
      let version = created.version;
      const basketId = created.basket_id;
      for (const line of lines) {
        const res = await getApi().post<BasketItemResult>(
          `/api/v1/baskets/${basketId}/items`,
          {
            product_id: line.product_id,
            requested_quantity: line.quantity,
            pack_quantity: line.pack_quantity > 0 ? line.pack_quantity : 1,
            expected_version: version,
          },
        );
        version = res.version;
      }
      setServerBasket(basketId);
      setSynced(true);
      return true;
    } catch (err) {
      setSyncError(
        err instanceof Error ? err.message : "همگام‌سازی سبد با سرور ناموفق بود",
      );
      return false;
    } finally {
      setSyncing(false);
    }
  }

  async function reviewAndCheckout() {
    const syncedSuccessfully = await pushToServer();
    if (syncedSuccessfully) router.push("/retailer/checkout");
  }

  if (lines.length === 0) {
    return (
      <div className="space-y-6 pb-10">
        <header className="border-b border-[var(--pol-light-border-subtle)] pb-5">
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            سبد خرید یکپارچه
          </h1>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            اقلام انتخابی از کاتالوگ در این بخش تجمیع و آماده ارسال به تأمین‌کنندگان می‌شوند.
          </p>
        </header>
        <Card variant="subtle" className="p-8">
          <EmptyState
            title="سبد خرید شما خالی است"
            description="برای شروع خرید، اقلام مورد نیاز فروشگاه خود را از کاتالوگ کالاهای FMCG انتخاب کنید."
            actionLabel="مشاهده و جستجوی کاتالوگ"
            onAction={() => router.push("/retailer/catalog")}
          />
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-10">
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-[var(--pol-light-border-subtle)] pb-5">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
              سبد خرید یکپارچه
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[12px] font-medium text-[var(--pol-light-text-secondary)] border border-[var(--pol-light-border-subtle)]">
              {lines.length.toLocaleString("fa-IR")} قلم کالا
            </span>
            {serverBasketId ? (
              <StatusChip tone="success">ثبت‌شده در سرور</StatusChip>
            ) : (
              <StatusChip tone="neutral">پیش‌نویس محلی</StatusChip>
            )}
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            سبد چندفروشنده‌ای پُل کالاها را بهینه تجمیع کرده و پس از تأیید تخصیص بین بهترین تأمین‌کنندگان تقسیم می‌کند.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              clear();
              setServerBasket(null);
            }}
            disabled={syncing}
            className="text-[var(--pol-light-semantic-danger)] hover:bg-[var(--pol-light-semantic-danger)]/10"
          >
            خالی کردن سبد
          </Button>
        </div>
      </header>

      {syncError ? (
        <ErrorState
          title="همگام‌سازی سبد با سرور ناموفق بود"
          description={syncError}
          onRetry={() => void pushToServer()}
        />
      ) : null}

      {synced && serverBasketId ? (
        <div
          role="status"
          className="flex items-center gap-2 rounded-[10px] bg-emerald-500/10 p-4 text-[13px] font-medium text-emerald-800 dark:text-emerald-300 border border-emerald-500/30"
        >
          <svg className="size-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span>سبد خرید در سرور ثبت شد. اکنون می‌توانید پیش‌نمایش تخصیص و تسویه حساب را مشاهده کنید.</span>
        </div>
      ) : null}

      {/* Cart Items List */}
      <section aria-label="اقلام سبد خرید" className="space-y-3">
        <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
          اقلام سفارش
        </h2>

        <div className="space-y-3">
          {lines.map((line) => (
            <Card
              key={line.product_id}
              className="p-4 sm:p-5 transition-all duration-[160ms] hover:border-[var(--pol-light-brand-primary)]/40 shadow-xs"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <Link
                    href={`/retailer/catalog/${line.product_id}`}
                    className="text-[15px] font-bold text-[var(--pol-light-text-primary)] hover:text-[var(--pol-light-brand-primary)] hover:underline leading-[22px]"
                  >
                    {line.name}
                  </Link>
                  <div className="mt-1.5 flex flex-wrap items-center gap-2 text-[12px] text-[var(--pol-light-text-secondary)]">
                    <span className="font-mono text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                      {line.master_sku ?? ""}
                    </span>
                    {line.unit ? (
                      <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 border border-[var(--pol-light-border-subtle)]">
                        واحد: {line.unit}
                        {line.pack_quantity > 1
                          ? ` (بسته ${line.pack_quantity.toLocaleString("fa-IR")} عددی)`
                          : ""}
                      </span>
                    ) : null}
                  </div>
                </div>

                <div className="flex items-center gap-4 self-end sm:self-center">
                  <div className="flex flex-col items-end">
                    <span className="text-[11px] text-[var(--pol-light-text-muted)] mb-1">تعداد بسته:</span>
                    <QtyStepper
                      value={line.quantity}
                      min={1}
                      onChange={(next) => setQuantity(line.product_id, next)}
                      label={`تعداد ${line.name}`}
                    />
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeLine(line.product_id)}
                    aria-label={`حذف ${line.name}`}
                    className="text-[var(--pol-light-semantic-danger)] hover:bg-[var(--pol-light-semantic-danger)]/10"
                  >
                    <svg className="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                    حذف
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Multi-Vendor Grouping Preview */}
      <Card variant="subtle" className="p-5 border-dashed border-[var(--pol-light-border-strong)]">
        <div className="flex items-center gap-2">
          <div className="flex size-8 items-center justify-center rounded-[8px] bg-[var(--pol-light-brand-primary)]/10 text-[var(--pol-light-brand-primary)]">
            <svg className="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <div>
            <h2 className="text-[14px] font-bold text-[var(--pol-light-text-primary)]">
              پیش‌نمایش گروه‌بندی چندتأمین‌کننده‌ای (D-014)
            </h2>
            <p className="text-[11px] text-[var(--pol-light-text-secondary)]">
              تقسیم بهینه و قطعی سفارش بین فروشندگان مختلف پس از بررسی استراتژی تخصیص انجام می‌پذیرد.
            </p>
          </div>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {groupPreview.map(([vendor, groupLines]) => (
            <div
              key={vendor}
              className="rounded-[10px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-3.5 shadow-2xs"
            >
              <div className="flex items-center justify-between border-b border-[var(--pol-light-border-subtle)] pb-2">
                <StatusChip tone="info">{vendor}</StatusChip>
                <span className="text-[11px] font-medium text-[var(--pol-light-text-muted)]">
                  {groupLines.length.toLocaleString("fa-IR")} قلم کالا
                </span>
              </div>
              <ul className="mt-2.5 space-y-1">
                {groupLines.map((l) => (
                  <li
                    key={l.product_id}
                    className="flex justify-between text-[12px] text-[var(--pol-light-text-secondary)]"
                  >
                    <span className="truncate max-w-[200px]">{l.name}</span>
                    <span className="font-semibold text-[var(--pol-light-text-primary)]">
                      {l.quantity.toLocaleString("fa-IR")} بسته
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </Card>

      {/* Action Footer Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-[var(--pol-light-border-subtle)] pt-5">
        <div className="flex flex-wrap items-center gap-2">
          <Button
            onClick={() => void reviewAndCheckout()}
            loading={syncing}
            disabled={syncing}
          >
            بررسی تخصیص و ادامه تسویه حساب ←
          </Button>
          <Button
            variant="secondary"
            onClick={() => void pushToServer()}
            loading={syncing}
            disabled={syncing || lines.length === 0}
          >
            ثبت سبد در سرور
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" onClick={() => router.push("/retailer/catalog")}>
            + افزودن کالای بیشتر
          </Button>
        </div>
      </div>
    </div>
  );
}
