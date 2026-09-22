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
  cardCls,
  formatDateTime,
  formatToman,
  inputCls,
  itemsOf,
  str,
  type LoadState,
} from "../../../_shared";

interface PriceRow {
  id: string;
  price_toman?: number | null;
  valid_from?: string | null;
  valid_to?: string | null;
  is_current?: boolean | null;
  created_at?: string | null;
}

interface CurrentPrice {
  id?: string;
  price_toman?: number | null;
  valid_from?: string | null;
  valid_to?: string | null;
}

/**
 * V-05 pricing for one vendor product.
 * GET/POST /catalog/vendors/products/{id}/prices
 * GET /catalog/vendors/products/{id}/prices/current
 */
export default function VendorProductPricesPage() {
  const params = useParams<{ id: string }>();
  const vendorProductId = params.id;

  const [history, setHistory] = useState<PriceRow[]>([]);
  const [current, setCurrent] = useState<CurrentPrice | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [newPrice, setNewPrice] = useState("");
  const [validFrom, setValidFrom] = useState("");
  const [validTo, setValidTo] = useState("");
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const load = useCallback(async () => {
    if (!vendorProductId) return;
    setState("loading");
    setErrorMessage(null);
    try {
      const [hist, cur] = await Promise.all([
        getApi().get<unknown>(
          `/api/v1/catalog/vendors/products/${vendorProductId}/prices`,
        ),
        getApi().get<CurrentPrice>(
          `/api/v1/catalog/vendors/products/${vendorProductId}/prices/current`,
        ),
      ]);
      setHistory(itemsOf<PriceRow>(hist, "prices"));
      setCurrent(cur);
      if (cur?.price_toman != null) setNewPrice(String(cur.price_toman));
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت قیمت‌ها ناموفق بود");
      setState("error");
    }
  }, [vendorProductId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function savePrice() {
    if (!vendorProductId) return;
    const n = Number(newPrice);
    if (!Number.isFinite(n) || n < 0) {
      setSaveError("قیمت باید عددی غیرمنفی باشد.");
      return;
    }
    setSaving(true);
    setSaveError(null);
    setSaved(false);
    try {
      const body: Record<string, unknown> = { price_toman: n };
      if (validFrom) body.valid_from = new Date(validFrom).toISOString();
      if (validTo) body.valid_to = new Date(validTo).toISOString();
      await getApi().post(
        `/api/v1/catalog/vendors/products/${vendorProductId}/prices`,
        body,
      );
      setSaved(true);
      await load();
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "ثبت قیمت ناموفق بود");
    } finally {
      setSaving(false);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری قیمت‌ها">
        <Skeleton className="h-8 w-64" />
        <div className={cardCls}>
          <Skeleton lines={4} />
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت قیمت‌ها ناموفق بود"
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
            قیمت کالا
          </h1>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]" dir="ltr">
            V-05 · vendor_product {vendorProductId}
          </p>
        </div>
        <div className="ms-auto flex flex-wrap gap-2">
          <Button variant="ghost" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
          <Link
            href="/vendor/catalog"
            className="rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)]"
          >
            کاتالوگ
          </Link>
        </div>
      </header>

      <section aria-label="قیمت فعلی" className={cardCls}>
        <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
          قیمت فعلی
        </h2>
        <p className="mt-2 text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          {formatToman(current?.price_toman)}
        </p>
        {current?.valid_from || current?.valid_to ? (
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
            از {formatDateTime(current.valid_from)} تا {formatDateTime(current.valid_to)}
          </p>
        ) : (
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]">
            محدوده اعتبار: —
          </p>
        )}
      </section>

      <section aria-label="ثبت قیمت جدید" className={cardCls}>
        <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
          ثبت قیمت جدید
        </h2>
        {saveError ? (
          <div className="mt-3">
            <ErrorState title="ثبت قیمت ناموفق بود" description={saveError} />
          </div>
        ) : null}
        {saved ? (
          <p className="mt-2 text-[13px] text-[var(--pol-light-semantic-success, #15803d)]">
            قیمت ثبت شد.
          </p>
        ) : null}
        <div className="mt-3 grid gap-3 sm:grid-cols-3">
          <Field
            label="قیمت (تومان)"
            type="number"
            min={0}
            value={newPrice}
            onChange={(e) => setNewPrice(e.target.value)}
            required
            dir="ltr"
          />
          <Field
            label="از تاریخ"
            type="datetime-local"
            value={validFrom}
            onChange={(e) => setValidFrom(e.target.value)}
            hint="اختیاری"
          />
          <Field
            label="تا تاریخ"
            type="datetime-local"
            value={validTo}
            onChange={(e) => setValidTo(e.target.value)}
            hint="اختیاری"
          />
        </div>
        <div className="mt-3">
          <Button loading={saving} onClick={() => void savePrice()}>
            ثبت قیمت
          </Button>
        </div>
      </section>

      <section aria-label="تاریخچه قیمت">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          تاریخچه
        </h2>
        {history.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="قیمتی ثبت نشده" description="هنوز رکورد قیمتی وجود ندارد." />
          </div>
        ) : (
          <div className="mt-3 overflow-x-auto rounded-[12px] border border-[var(--pol-light-border-subtle)]">
            <table className="w-full min-w-[480px] border-collapse bg-[var(--pol-light-surface-default)] text-[13px]">
              <thead>
                <tr className="border-b border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] text-[12px] text-[var(--pol-light-text-secondary)]">
                  <th className="px-4 py-2 text-start font-medium">قیمت</th>
                  <th className="px-4 py-2 text-start font-medium">از</th>
                  <th className="px-4 py-2 text-start font-medium">تا</th>
                  <th className="px-4 py-2 text-start font-medium">وضعیت</th>
                </tr>
              </thead>
              <tbody>
                {history.map((row) => (
                  <tr
                    key={String(row.id)}
                    className="border-b border-[var(--pol-light-border-subtle)] last:border-b-0"
                  >
                    <td className="px-4 py-3 text-[var(--pol-light-text-primary)]">
                      {formatToman(row.price_toman)}
                    </td>
                    <td className="px-4 py-3 text-[var(--pol-light-text-secondary)]">
                      {formatDateTime(row.valid_from)}
                    </td>
                    <td className="px-4 py-3 text-[var(--pol-light-text-secondary)]">
                      {formatDateTime(row.valid_to)}
                    </td>
                    <td className="px-4 py-3">
                      {row.is_current ? (
                        <StatusChip tone="success">فعلی</StatusChip>
                      ) : (
                        <StatusChip tone="neutral">قبلی</StatusChip>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
