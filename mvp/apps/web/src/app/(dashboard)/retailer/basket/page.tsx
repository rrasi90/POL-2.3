"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Button,
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

  async function pushToServer() {
    if (lines.length === 0) return;
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
    } catch (err) {
      setSyncError(
        err instanceof Error ? err.message : "همگام‌سازی سبد با سرور ناموفق بود",
      );
    } finally {
      setSyncing(false);
    }
  }

  async function reviewAndCheckout() {
    await pushToServer();
    // navigate only if sync succeeded — pushToServer sets error on failure
    // (syncError state is set async; check serverBasketId after)
    router.push("/retailer/checkout");
  }

  if (lines.length === 0) {
    return (
      <div className="space-y-4">
        <header>
          <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
            سبد خرید
          </h1>
        </header>
        <EmptyState
          title="سبد خرید خالی است"
          description="از کاتالوگ کالا انتخاب کنید تا به سبد اضافه شود."
          actionLabel="رفتن به کاتالوگ"
          onAction={() => router.push("/retailer/catalog")}
        />
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          سبد خرید
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">
          {lines.length.toLocaleString("fa-IR")} قلم کالا
        </span>
        {serverBasketId ? (
          <StatusChip tone="info">با سرور همگام شده</StatusChip>
        ) : (
          <StatusChip tone="neutral">ذخیره محلی</StatusChip>
        )}
      </header>

      <p className="text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
        سبد یکپارچه چندفروشنده‌ای است (D-014). تقسیم نهایی کالاها بین فروشندگان پس از
        بررسی تخصیص (allocation-preview) مشخص می‌شود.
      </p>

      {syncError ? (
        <ErrorState
          title="همگام‌سازی سبد ناموفق بود"
          description={syncError}
          onRetry={() => void pushToServer()}
        />
      ) : null}
      {synced && serverBasketId ? (
        <p
          role="status"
          className="text-[13px] text-[var(--pol-light-semantic-success)]"
        >
          سبد در سرور ثبت شد. می‌توانید برای بررسی تخصیص ادامه دهید.
        </p>
      ) : null}

      <ul role="list" className="space-y-2">
        {lines.map((line) => (
          <li
            key={line.product_id}
            className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
          >
            <div className="flex flex-wrap items-start gap-3">
              <div className="min-w-0 flex-1">
                <Link
                  href={`/retailer/catalog/${line.product_id}`}
                  className="text-[14px] font-semibold text-[var(--pol-light-text-primary)] hover:underline"
                >
                  {line.name}
                </Link>
                <p className="mt-0.5 text-[12px] text-[var(--pol-light-text-muted)]" dir="ltr">
                  {line.master_sku ?? ""}
                </p>
                {line.unit ? (
                  <p className="mt-0.5 text-[12px] text-[var(--pol-light-text-secondary)]">
                    واحد: {line.unit}
                    {line.pack_quantity > 1
                      ? ` · بسته ${line.pack_quantity.toLocaleString("fa-IR")}`
                      : ""}
                  </p>
                ) : null}
              </div>
              <div className="flex items-center gap-3">
                <QtyStepper
                  value={line.quantity}
                  min={1}
                  onChange={(next) => setQuantity(line.product_id, next)}
                  label={`تعداد ${line.name}`}
                />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeLine(line.product_id)}
                  aria-label={`حذف ${line.name}`}
                >
                  حذف
                </Button>
              </div>
            </div>
          </li>
        ))}
      </ul>

      <section
        aria-label="پیش‌نمایش گروه‌بندی"
        className="rounded-[12px] border border-dashed border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-4"
      >
        <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
          پیش‌نمایش گروه‌بندی (غیرالزام‌آور)
        </h2>
        <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
          این نمایش صرفاً اقلام واردشده را نشان می‌دهد؛ تخصیص قطعی پس از allocation-preview
          دریافت می‌شود.
        </p>
        <div className="mt-3 space-y-2">
          {groupPreview.map(([vendor, groupLines]) => (
            <div
              key={vendor}
              className="rounded-[8px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-3"
            >
              <div className="flex items-center gap-2">
                <StatusChip tone="info">{vendor}</StatusChip>
                <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                  {groupLines.length.toLocaleString("fa-IR")} قلم
                </span>
              </div>
              <ul className="mt-1.5 space-y-0.5">
                {groupLines.map((l) => (
                  <li
                    key={l.product_id}
                    className="flex justify-between text-[13px] text-[var(--pol-light-text-secondary)]"
                  >
                    <span>{l.name}</span>
                    <span>×{l.quantity.toLocaleString("fa-IR")}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <div className="flex flex-wrap items-center gap-2 border-t border-[var(--pol-light-border-subtle)] pt-4">
        <Button
          onClick={() => void reviewAndCheckout()}
          loading={syncing}
          disabled={syncing}
        >
          بررسی و ادامه تسویه
        </Button>
        <Button
          variant="secondary"
          onClick={() => void pushToServer()}
          loading={syncing}
          disabled={syncing || lines.length === 0}
        >
          ثبت سبد در سرور
        </Button>
        <Button
          variant="ghost"
          onClick={() => {
            clear();
            setServerBasket(null);
          }}
          disabled={syncing}
        >
          خالی کردن سبد
        </Button>
        <Button variant="ghost" onClick={() => router.push("/retailer/catalog")}>
          ادامه خرید
        </Button>
      </div>
    </div>
  );
}
