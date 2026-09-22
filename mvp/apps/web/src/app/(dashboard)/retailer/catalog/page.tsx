"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Button,
  EmptyState,
  ErrorState,
  SearchField,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";

interface CatalogCategory {
  id: string;
  name_fa: string;
  slug?: string | null;
  display_order?: number | null;
  subcategories?: { id: string; name_fa: string; slug?: string | null }[];
}

interface CatalogProduct {
  id: string;
  master_sku?: string | null;
  canonical_name_fa: string;
  base_unit?: string | null;
  default_pack_unit?: string | null;
  default_pack_quantity?: number | null;
  brand_name?: string | null;
  category_name?: string | null;
  subcategory_name?: string | null;
}

interface CatalogSearchData {
  items: CatalogProduct[];
  query: string;
}

interface UnifiedSearchData {
  query: string;
  products?: CatalogProduct[];
  vendors?: { id: string; business_name?: string | null; name?: string | null }[];
  categories?: { id: string; name_fa?: string | null; name?: string | null }[];
  page?: number;
  page_size?: number;
}

type LoadState = "idle" | "loading" | "error" | "ready";

const inputCls = [
  "h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3",
  "text-[14px] leading-[22px] text-[var(--pol-light-text-primary)]",
  "placeholder:text-[var(--pol-light-text-muted)]",
  "focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]",
].join(" ");

export default function RetailerCatalogPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [debounced, setDebounced] = useState("");
  const [categoryId, setCategoryId] = useState<string | null>(null);
  const [categories, setCategories] = useState<CatalogCategory[]>([]);
  const [catState, setCatState] = useState<LoadState>("loading");
  const [catError, setCatError] = useState<string | null>(null);
  const [results, setResults] = useState<CatalogProduct[]>([]);
  const [unifiedVendors, setUnifiedVendors] = useState<UnifiedSearchData["vendors"]>([]);
  const [searchState, setSearchState] = useState<LoadState>("idle");
  const [searchError, setSearchError] = useState<string | null>(null);
  const [activeQuery, setActiveQuery] = useState("");

  const loadCategories = useCallback(async () => {
    setCatState("loading");
    setCatError(null);
    try {
      const data = await getApi().get<CatalogCategory[] | { data: CatalogCategory[] }>(
        "/api/v1/catalog/categories",
      );
      const list = Array.isArray(data) ? data : (data?.data ?? []);
      setCategories(list);
      setCatState("ready");
    } catch (err) {
      setCatError(err instanceof Error ? err.message : "دریافت دسته‌بندی‌ها ناموفق بود");
      setCatState("error");
    }
  }, []);

  useEffect(() => {
    void loadCategories();
  }, [loadCategories]);

  useEffect(() => {
    const t = window.setTimeout(() => setDebounced(query.trim()), 350);
    return () => window.clearTimeout(t);
  }, [query]);

  const runSearch = useCallback(
    async (q: string, catId: string | null) => {
      if (!q && !catId) {
        setResults([]);
        setUnifiedVendors([]);
        setActiveQuery("");
        setSearchState("idle");
        return;
      }
      setSearchState("loading");
      setSearchError(null);
      try {
        const params = new URLSearchParams();
        params.set("q", q || " ");
        if (catId) params.set("category_id", catId);
        params.set("limit", "40");

        const catalogPath = q
          ? `/api/v1/catalog/search?${params.toString()}`
          : null;

        if (catalogPath) {
          const data = await getApi().get<CatalogSearchData>(catalogPath);
          setResults(Array.isArray(data?.items) ? data.items : []);
          setActiveQuery(data?.query ?? q);
        } else {
          setResults([]);
          setActiveQuery("");
        }

        // Unified search (vendors/categories) — REAL GET /search; skip blank q (API min_length=1)
        if (q) {
          try {
            const unifiedParams = new URLSearchParams();
            unifiedParams.set("q", q);
            if (catId) unifiedParams.set("type", "product");
            const u = await getApi().get<UnifiedSearchData>(
              `/api/v1/search?${unifiedParams.toString()}`,
            );
            setUnifiedVendors(Array.isArray(u?.vendors) ? u.vendors : []);
          } catch {
            setUnifiedVendors([]);
          }
        } else {
          setUnifiedVendors([]);
        }

        setSearchState("ready");
      } catch (err) {
        setSearchError(err instanceof Error ? err.message : "جستجو ناموفق بود");
        setSearchState("error");
      }
    },
    [],
  );

  useEffect(() => {
    void runSearch(debounced, categoryId);
  }, [debounced, categoryId, runSearch]);

  function chipCls(active: boolean) {
    return [
      "rounded-full border px-3 py-1 text-[12px] leading-[18px] transition-colors duration-[160ms]",
      active
        ? "border-transparent bg-[var(--pol-light-brand-primary)] text-white"
        : "border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)]",
    ].join(" ");
  }

  const hasQuery = debounced.length > 0 || categoryId !== null;

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          کاتالوگ و جستجو
        </h1>
        <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
          جستجوی کالا، انتخاب دسته و مشاهده پیشنهادها
        </p>
      </header>

      <form
        role="search"
        onSubmit={(e) => {
          e.preventDefault();
          void runSearch(query.trim(), categoryId);
        }}
        className="flex gap-2"
      >
        <SearchField
          label="جستجوی کالا"
          placeholder="نام کالا، برند یا SKU…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1"
        />
        <Button type="submit" loading={searchState === "loading"}>
          جستجو
        </Button>
      </form>

      <section aria-label="دسته‌بندی‌ها">
        <h2 className="text-[14px] leading-[22px] font-semibold text-[var(--pol-light-text-primary)]">
          دسته‌بندی‌ها
        </h2>
        {catState === "loading" ? (
          <div className="mt-2 flex flex-wrap gap-2" aria-busy="true">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-8 w-24 rounded-full" />
            ))}
          </div>
        ) : catState === "error" ? (
          <div className="mt-2">
            <ErrorState
              title="دریافت دسته‌بندی‌ها ناموفق بود"
              description={catError ?? undefined}
              onRetry={() => void loadCategories()}
            />
          </div>
        ) : categories.length === 0 ? (
          <p className="mt-2 text-[13px] text-[var(--pol-light-text-muted)]">
            دسته‌بندی‌ای موجود نیست.
          </p>
        ) : (
          <div className="mt-2 flex flex-wrap gap-2">
            <button
              type="button"
              className={chipCls(categoryId === null)}
              onClick={() => setCategoryId(null)}
              aria-pressed={categoryId === null}
            >
              همه
            </button>
            {categories.map((c) => (
              <button
                key={c.id}
                type="button"
                className={chipCls(categoryId === c.id)}
                onClick={() => setCategoryId(categoryId === c.id ? null : c.id)}
                aria-pressed={categoryId === c.id}
              >
                {c.name_fa}
              </button>
            ))}
          </div>
        )}
        {categories.length > 0 && categoryId ? (
          (() => {
            const active = categories.find((c) => c.id === categoryId);
            if (!active?.subcategories?.length) return null;
            return (
              <div className="mt-2 flex flex-wrap gap-2">
                {active.subcategories.map((sc) => (
                  <span
                    key={sc.id}
                    className="rounded-[6px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] text-[var(--pol-light-text-secondary)]"
                  >
                    {sc.name_fa}
                  </span>
                ))}
              </div>
            );
          })()
        ) : null}
      </section>

      <section aria-label="نتایج جستجو" aria-busy={searchState === "loading"}>
        <div className="flex items-center gap-2">
          <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
            نتایج
          </h2>
          {activeQuery ? (
            <span className="text-[12px] text-[var(--pol-light-text-muted)]">
              برای «{activeQuery}»
            </span>
          ) : null}
          {searchState === "ready" ? (
            <span className="ms-auto text-[12px] text-[var(--pol-light-text-muted)]">
              {results.length.toLocaleString("fa-IR")} کالا
            </span>
          ) : null}
        </div>

        {searchState === "loading" ? (
          <div className="mt-3 space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
              >
                <Skeleton className="mb-2 h-4 w-1/3" />
                <Skeleton lines={1} />
              </div>
            ))}
          </div>
        ) : searchState === "error" ? (
          <div className="mt-3">
            <ErrorState
              title="جستجو ناموفق بود"
              description={searchError ?? undefined}
              onRetry={() => void runSearch(debounced, categoryId)}
            />
          </div>
        ) : !hasQuery ? (
          <div className="mt-3">
            <EmptyState
              title="جستجو کنید"
              description="عبارتی وارد کنید یا یک دسته انتخاب کنید تا کالاها نمایش داده شوند."
            />
          </div>
        ) : results.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="کالایی یافت نشد"
              description="عبارت دیگری امتحان کنید یا فیلتر دسته را بردارید."
              actionLabel="پاک کردن فیلتر"
              onAction={() => {
                setQuery("");
                setCategoryId(null);
              }}
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {results.map((p) => (
              <li key={p.id}>
                <Link
                  href={`/retailer/catalog/${p.id}`}
                  className="block rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4 transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[14px] leading-[22px] font-semibold text-[var(--pol-light-text-primary)]">
                      {p.canonical_name_fa}
                    </span>
                    {p.brand_name ? (
                      <StatusChip tone="info">{p.brand_name}</StatusChip>
                    ) : null}
                    <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                      {p.master_sku ?? ""}
                    </span>
                  </div>
                  <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
                    {[p.category_name, p.subcategory_name].filter(Boolean).join(" · ")}
                    {p.default_pack_quantity
                      ? ` — بسته ${p.default_pack_quantity.toLocaleString("fa-IR")} ${p.default_pack_unit ?? p.base_unit ?? ""}`
                      : ""}
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        )}

        {unifiedVendors && unifiedVendors.length > 0 ? (
          <div className="mt-5">
            <h3 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
              تأمین‌کنندگان مرتبط
            </h3>
            <ul role="list" className="mt-2 space-y-2">
              {unifiedVendors.map((v) => (
                <li
                  key={v.id}
                  className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] px-4 py-3 text-[13px] text-[var(--pol-light-text-primary)]"
                >
                  {v.business_name ?? v.name ?? v.id}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </section>

      <div className="flex justify-start border-t border-[var(--pol-light-border-subtle)] pt-4">
        <Button variant="ghost" onClick={() => router.push("/retailer")}>
          بازگشت به خانه
        </Button>
      </div>
    </div>
  );
}
