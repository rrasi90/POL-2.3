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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  formatDateTime,
  formatToman,
  inputCls,
  itemsOf,
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
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری قیمت‌ها">
        <Skeleton className="h-9 w-64" />
        <Card className="p-6">
          <Skeleton lines={4} />
        </Card>
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
    <div className="space-y-6">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] md:text-[26px] font-bold text-[var(--pol-light-text-primary)]">
              مدیریت و تاریخچه قیمت کالا
            </h1>
            <span className="font-mono text-[13px] text-[var(--pol-light-text-secondary)]" dir="ltr">
              کد کالا: {vendorProductId?.slice(0, 8)}...
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            تعیین قیمت فعال، زمان‌بندی اعمال نرخ‌های جدید و مشاهده سوابق تغییرات
          </p>
        </div>

        <div className="flex shrink-0 gap-2">
          <Button variant="ghost" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
          <Link
            href="/vendor/catalog"
            className="inline-flex items-center justify-center rounded-lg border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] font-medium text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)] transition-colors"
          >
            کاتالوگ فروشنده
          </Link>
        </div>
      </header>

      {/* Current Active Price Card */}
      <Card className="p-5 bg-[var(--pol-light-surface-subtle)]">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[13px] font-medium text-[var(--pol-light-text-secondary)]">
                قیمت فعال در بازار پُل
              </span>
              <StatusChip tone="success">قیمت رسمی جاری</StatusChip>
            </div>
            <div className="mt-2 text-[26px] font-bold text-[var(--pol-light-text-primary)]">
              {formatToman(current?.price_toman)}
            </div>
          </div>

          <div className="text-[12px] text-[var(--pol-light-text-secondary)]">
            {current?.valid_from && (
              <div>معتبر از: {formatDateTime(current.valid_from)}</div>
            )}
            {current?.valid_to && (
              <div>تا تاریخ: {formatDateTime(current.valid_to)}</div>
            )}
          </div>
        </div>
      </Card>

      {/* Update Price Form */}
      <Card className="p-5 space-y-4">
        <h2 className="text-[16px] font-bold text-[var(--pol-light-text-primary)]">
          تعریف نرخ جدید کالا
        </h2>

        {saveError && (
          <ErrorState title="خطا در ثبت نرخ جدید" description={saveError} />
        )}

        {saved && (
          <div className="rounded-xl border border-emerald-300 bg-emerald-50/50 p-3 text-[13px] font-semibold text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950/30 dark:text-emerald-300">
            ✓ نرخ جدید با موفقیت ثبت و در کاتالوگ فعال گردید.
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-3">
          <Field
            label="قیمت جدید (تومان)"
            type="number"
            min={0}
            value={newPrice}
            onChange={(e) => setNewPrice(e.target.value)}
            required
            hint="قیمت فروش ناخالص به سوپرمارکت"
          />
          <div className="flex flex-col gap-1.5">
            <label htmlFor="valid-from" className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
              آغاز اعتبار (اختیاری)
            </label>
            <input
              id="valid-from"
              type="datetime-local"
              className={inputCls}
              value={validFrom}
              onChange={(e) => setValidFrom(e.target.value)}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="valid-to" className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
              پایان اعتبار (اختیاری)
            </label>
            <input
              id="valid-to"
              type="datetime-local"
              className={inputCls}
              value={validTo}
              onChange={(e) => setValidTo(e.target.value)}
            />
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <Button loading={saving} onClick={() => void savePrice()}>
            ثبت و اعمال قیمت جدید
          </Button>
        </div>
      </Card>

      {/* Price History Table */}
      <section aria-label="تاریخچه قیمت‌ها" className="space-y-3">
        <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
          سوابق تغییرات قیمت ({history.length.toLocaleString("fa-IR")} مورد)
        </h2>

        {history.length === 0 ? (
          <EmptyState title="هیچ سابقه‌ای برای قیمت این کالا ثبت نشده است" />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>مبلغ ثبت‌شده</TableHead>
                <TableHead>وضعیت</TableHead>
                <TableHead>شروع اعتبار</TableHead>
                <TableHead>پایان اعتبار</TableHead>
                <TableHead>تاریخ ثبت</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {history.map((row) => (
                <TableRow key={row.id}>
                  <TableCell className="font-bold">
                    {formatToman(row.price_toman)}
                  </TableCell>
                  <TableCell>
                    {row.is_current ? (
                      <StatusChip tone="success">جاری</StatusChip>
                    ) : (
                      <StatusChip tone="neutral">منقضی</StatusChip>
                    )}
                  </TableCell>
                  <TableCell className="text-[12px] text-[var(--pol-light-text-secondary)]">
                    {formatDateTime(row.valid_from)}
                  </TableCell>
                  <TableCell className="text-[12px] text-[var(--pol-light-text-secondary)]">
                    {formatDateTime(row.valid_to)}
                  </TableCell>
                  <TableCell className="text-[12px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(row.created_at)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </section>
    </div>
  );
}
