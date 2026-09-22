"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Button,
  EmptyState,
  ErrorState,
  SearchField,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  cardCls,
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
 * GET /catalog/vendors/products/{id}/inventory (via list payload or per-product)
 * Current backend exposes inventory under vendor products; when list shape lacks
 * inventory, fetch products and PATCH inventory path per REAL route.
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
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری موجودی">
        <Skeleton className="h-8 w-48" />
        <div className={cardCls}>
          <Skeleton lines={6} />
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
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          موجودی
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">V-06</span>
        <Link
          href="/vendor/inventory/daily"
          className="text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
        >
          تأیید روزانه
        </Link>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      {saveError ? (
        <ErrorState title="به‌روزرسانی موجودی ناموفق بود" description={saveError} />
      ) : null}
      {savedId ? (
        <p className="text-[13px] text-[var(--pol-light-semantic-success, #15803d)]">
          موجودی به‌روزرسانی شد.
        </p>
      ) : null}

      <SearchField
        label="جستجوی کالا"
        placeholder="نام کالا…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      {filtered.length === 0 ? (
        <EmptyState title="کالایی یافت نشد" description="کاتالوگ شما خالی است." />
      ) : (
        <ul role="list" className="space-y-2">
          {filtered.map((row) => {
            const vpId = str(row.vendor_product_id ?? row.id, "");
            const value = edits[vpId] ?? String(row.stock_quantity ?? 0);
            return (
              <li
                key={vpId}
                className="flex flex-wrap items-center gap-3 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
              >
                <div className="min-w-0 flex-1">
                  <p className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
                    {row.product_name ?? "—"}
                  </p>
                  <p className="mt-0.5 text-[12px] text-[var(--pol-light-text-secondary)]">
                    {row.packaging_unit ?? "واحد"}
                    {row.available_quantity != null
                      ? ` · در دسترس ${row.available_quantity.toLocaleString("fa-IR")}`
                      : ""}
                    {row.reserved_quantity
                      ? ` · رزرو ${row.reserved_quantity.toLocaleString("fa-IR")}`
                      : ""}
                  </p>
                </div>
                {row.is_active === false ? (
                  <StatusChip tone="neutral">غیرفعال</StatusChip>
                ) : (
                  <StatusChip tone="success">فعال</StatusChip>
                )}
                <label className="sr-only" htmlFor={`stock-${vpId}`}>
                  موجودی {row.product_name ?? vpId}
                </label>
                <input
                  id={`stock-${vpId}`}
                  type="number"
                  min={0}
                  className={[inputCls, "w-28"].join(" ")}
                  value={value}
                  onChange={(e) => setEdits((prev) => ({ ...prev, [vpId]: e.target.value }))}
                />
                <Button
                  size="sm"
                  loading={savingId === vpId}
                  disabled={savingId !== null}
                  onClick={() => void saveStock(row)}
                >
                  ذخیره
                </Button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
