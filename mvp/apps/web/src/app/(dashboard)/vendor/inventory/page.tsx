"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  SearchField,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  formatDateTime,
  inputCls,
  itemsOf,
  str,
  type LoadState,
} from "../_shared";

interface InventoryRow {
  id: string;
  vendor_product_id?: string | null;
  product_id?: string | null;
  product_name?: string | null;
  name?: string | null;
  stock_quantity?: number | null;
  reserved_quantity?: number | null;
  available_quantity?: number | null;
  packaging_unit?: string | null;
  updated_at?: string | null;
  is_active?: boolean | null;
}

/**
 * V-06 inventory list + PATCH stock per row.
 * GET /catalog/vendors/products
 * PATCH /catalog/vendors/products/{id}/inventory
 */
export default function VendorInventoryPage() {
  const [rows, setRows] = useState<InventoryRow[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [edits, setEdits] = useState<Record<string, string>>({});
  const [savingId, setSavingId] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [savedId, setSavedId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const data = await getApi().get<unknown>("/api/v1/catalog/vendors/products");
      const products = itemsOf<InventoryRow>(data, "products");
      const invRows = products.map((p) => {
        const vpId = str(p.vendor_product_id ?? p.id, "");
        return {
          id: vpId,
          vendor_product_id: vpId,
          product_id: p.product_id,
          product_name: p.product_name ?? p.name,
          stock_quantity: p.stock_quantity,
          packaging_unit: p.packaging_unit,
          updated_at: p.updated_at,
          is_active: p.is_active,
        } satisfies InventoryRow;
      });
      setRows(invRows);
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت موجودی ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function saveStock(row: InventoryRow) {
    const vpId = str(row.vendor_product_id ?? row.id, "");
    if (!vpId) return;
    const raw = edits[vpId] ?? String(row.stock_quantity ?? 0);
    const n = Number(raw);
    if (!Number.isFinite(n) || n < 0) {
      setSaveError("موجودی باید عددی غیرمنفی باشد.");
      return;
    }
    setSavingId(vpId);
    setSaveError(null);
    setSavedId(null);
    try {
      await getApi().patch(
        `/api/v1/catalog/vendors/products/${vpId}/inventory`,
        { stock_quantity: n },
      );
      setSavedId(vpId);
      await load();
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "به‌روزرسانی موجودی ناموفق بود");
    } finally {
      setSavingId(null);
    }
  }

  const filtered = rows.filter((r) => {
    if (!query.trim()) return true;
    const q = query.trim().toLowerCase();
    return (
      str(r.product_name, "").toLowerCase().includes(q) ||
      str(r.id).toLowerCase().includes(q)
    );
  });

  if (state === "loading") {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری موجودی">
        <Skeleton className="h-9 w-48" />
        <div className="grid gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Card key={i} className="p-5">
              <Skeleton lines={3} />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت موجودی ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] md:text-[26px] font-bold text-[var(--pol-light-text-primary)]">
              مدیریت انبار و موجودی کالاها
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              V-06
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            به‌روزرسانی سریع تعداد موجودی انبار برای هر قلم کالا
          </p>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <Link
            href="/vendor/inventory/daily"
            className="inline-flex items-center justify-center rounded-lg bg-[var(--pol-light-brand-primary)] px-3.5 py-2 text-[13px] font-semibold text-white shadow-sm hover:opacity-95 transition-opacity"
          >
            ⏰ تأیید روزانه موجودی
          </Link>
          <Button variant="secondary" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
        </div>
      </header>

      {/* Search and Alert */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="w-full max-w-md">
          <SearchField
            label="جستجوی کالا"
            placeholder="نام کالا یا شناسه انبار..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
          {filtered.length.toLocaleString("fa-IR")} قلم کالا
        </span>
      </div>

      {saveError && (
        <ErrorState title="خطا در ذخیره‌سازی موجودی" description={saveError} />
      )}

      {/* Inventory Items List */}
      {filtered.length === 0 ? (
        <EmptyState
          title="کالایی یافت نشد"
          description="کالایی در انبار ثبت نشده است یا با عبارت جستجو مطابقت ندارد."
        />
      ) : (
        <div className="grid gap-3">
          {filtered.map((r) => {
            const vpId = str(r.vendor_product_id ?? r.id, "");
            const currentStock = r.stock_quantity ?? 0;
            const editVal = edits[vpId] ?? String(currentStock);
            const isSaving = savingId === vpId;
            const isSaved = savedId === vpId;
            const hasChanged = editVal !== String(currentStock);

            return (
              <Card
                key={vpId}
                className="p-4 transition-all duration-150 hover:border-[var(--pol-light-border-strong)]"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                        {r.product_name ?? "کالای بدون نام"}
                      </h3>
                      {r.is_active === false ? (
                        <StatusChip tone="neutral">غیرفعال</StatusChip>
                      ) : currentStock === 0 ? (
                        <StatusChip tone="danger">ناموجود</StatusChip>
                      ) : currentStock < 10 ? (
                        <StatusChip tone="warning">موجودی اندک</StatusChip>
                      ) : (
                        <StatusChip tone="success">موجود</StatusChip>
                      )}
                    </div>
                    <div className="mt-1 flex flex-wrap items-center gap-2 text-[12px] text-[var(--pol-light-text-secondary)]">
                      <span>واحد: {r.packaging_unit ?? "بسته"}</span>
                      <span>·</span>
                      <span>آخرین به‌روزرسانی: {formatDateTime(r.updated_at)}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between border-t border-[var(--pol-light-border-subtle)] pt-3 sm:border-0 sm:pt-0 sm:gap-4">
                    <div className="flex items-center gap-2">
                      <label htmlFor={`stock-${vpId}`} className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
                        موجودی فعلی:
                      </label>
                      <input
                        id={`stock-${vpId}`}
                        type="number"
                        min={0}
                        className={[inputCls, "w-28 text-center font-bold"].join(" ")}
                        value={editVal}
                        onChange={(e) =>
                          setEdits((prev) => ({ ...prev, [vpId]: e.target.value }))
                        }
                      />
                    </div>

                    <div className="flex items-center gap-2">
                      {isSaved && (
                        <span className="text-[12px] font-bold text-emerald-600 dark:text-emerald-400">
                          ✓ ثبت شد
                        </span>
                      )}
                      <Button
                        size="sm"
                        disabled={!hasChanged || isSaving}
                        loading={isSaving}
                        onClick={() => void saveStock(r)}
                      >
                        ذخیره
                      </Button>
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
