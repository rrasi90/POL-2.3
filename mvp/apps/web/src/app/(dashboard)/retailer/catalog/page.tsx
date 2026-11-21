"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
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

const PLACEHOLDER_CATEGORY_NAMES = new Set([
  "fulfillment category",
  "proof category",
  "seed cat",
]);

function getDisplayableCategories(input: CatalogCategory[]): CatalogCategory[] {
  const seen = new Set<string>();
  return input.filter((category) => {
    const name = typeof category.name_fa === "string" ? category.name_fa.trim().replace(/\s+/g, " ") : "";
    if (!name) return false;
    const key = name.normalize("NFKC").toLocaleLowerCase("en-US");
    if (PLACEHOLDER_CATEGORY_NAMES.has(key) || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

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

  const visibleCategories = getDisplayableCategories(categories);

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
    <div className="space-y-6 pb-10">
      <header className="border-b border-[var(--pol-light-border-subtle)] pb-5">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          کاتالوگ و جستجوی کالا
        </h1>
        <p className="mt-1 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          جستجوی کالاهای مصرفی روزمره، بررسی برندها، استعلام قیمت و مقایسه موجودی تأمین‌کنندگان
        </p>
      </header>

      {/* Search Bar Form */}
      <Card className="p-4 sm:p-5 shadow-xs">
        <form
          role="search"
          onSubmit={(e) => {
            e.preventDefault();
            void runSearch(query.trim(), categoryId);
          }}
          className="flex flex-col sm:flex-row gap-3"
        >
          <SearchField
            label="جستجوی کالا"
            placeholder="نام کالا، برند یا کد کالا (حداقل ۲ نویسه)…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1"
          />
          <Button type="submit" loading={searchState === "loading"} className="sm:self-end">
            <svg
              className="size-4 me-1.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            جستجو
          </Button>
        </form>
      </Card>

      {/* Category Pills */}
      <section aria-label="دسته‌بندی‌ها" className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-[14px] leading-[22px] font-bold text-[var(--pol-light-text-primary)]">
            دسته‌بندی‌های کالا
          </h2>
          {categoryId ? (
            <button
              type="button"
              onClick={() => setCategoryId(null)}
              className="text-[12px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
            >
              پاک کردن فیلتر دسته
            </button>
          ) : null}
        </div>

        {catState === "loading" ? (
          <div className="flex flex-wrap gap-2" aria-busy="true">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-8 w-24 rounded-full" />
            ))}
          </div>
        ) : catState === "error" ? (
          <ErrorState
            title="دریافت دسته‌بندی‌ها ناموفق بود"
            description={catError ?? undefined}
            onRetry={() => void loadCategories()}
          />
        ) : visibleCategories.length === 0 ? (
          <p className="text-[13px] text-[var(--pol-light-text-muted)]">
            {categories.length === 0 ? "دسته‌بندی‌ای موجود نیست." : "دسته‌بندی معتبری برای نمایش پیدا نشد."}
          </p>
        ) : (
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className={chipCls(categoryId === null)}
              onClick={() => setCategoryId(null)}
              aria-pressed={categoryId === null}
            >
              همه کالاها
            </button>
            {visibleCategories.map((c) => (
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

        {visibleCategories.length > 0 && categoryId ? (
          (() => {
            const active = visibleCategories.find((c) => c.id === categoryId);
            if (!active?.subcategories?.length) return null;
            return (
              <div className="flex flex-wrap items-center gap-1.5 rounded-[10px] bg-[var(--pol-light-surface-subtle)] p-2.5 border border-[var(--pol-light-border-subtle)]">
                <span className="text-[11px] font-medium text-[var(--pol-light-text-muted)] me-1">
                  زیردسته‌ها:
                </span>
                {active.subcategories.map((sc) => (
                  <span
                    key={sc.id}
                    className="rounded-[6px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] px-2.5 py-1 text-[11px] font-medium text-[var(--pol-light-text-secondary)] shadow-2xs"
                  >
                    {sc.name_fa}
                  </span>
                ))}
              </div>
            );
          })()
        ) : null}
      </section>

      {/* Results Section */}
      <section aria-label="نتایج جستجو" aria-busy={searchState === "loading"} className="space-y-4">
        <div className="flex items-center justify-between border-b border-[var(--pol-light-border-subtle)] pb-3">
          <div className="flex items-center gap-2">
            <h2 className="text-[16px] leading-[24px] font-bold text-[var(--pol-light-text-primary)]">
              نتایج کاتالوگ
            </h2>
            {activeQuery ? (
              <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[12px] text-[var(--pol-light-text-secondary)] border border-[var(--pol-light-border-subtle)]">
                «{activeQuery}»
              </span>
            ) : null}
          </div>
          {searchState === "ready" ? (
            <span className="text-[12px] font-medium text-[var(--pol-light-text-muted)]">
              {results.length.toLocaleString("fa-IR")} قلم کالا
            </span>
          ) : null}
        </div>

        {searchState === "loading" ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <Card key={i} className="p-4">
                <Skeleton className="mb-2 h-5 w-2/3" />
                <Skeleton className="mb-3 h-4 w-1/3" />
                <Skeleton lines={2} />
              </Card>
            ))}
          </div>
        ) : searchState === "error" ? (
          <ErrorState
            title="جستجو ناموفق بود"
            description={searchError ?? undefined}
            onRetry={() => void runSearch(debounced, categoryId)}
          />
        ) : categoryId && !debounced ? (
          <Card variant="subtle" className="p-6">
            <EmptyState
              title="برای فیلتر دسته‌بندی، یک عبارت جست‌وجو وارد کنید"
              description="فیلتر دسته‌بندی همراه با نام کالا، برند یا کد کالا اعمال می‌شود. ابتدا عبارت جست‌وجو را وارد کنید."
              actionLabel="پاک کردن فیلتر دسته"
              onAction={() => setCategoryId(null)}
            />
          </Card>
        ) : !hasQuery ? (
          <Card variant="subtle" className="p-6">
            <EmptyState
              title="جستجوی کالا"
              description="نام کالا یا برند را جستجو کنید یا یکی از دسته‌بندی‌های بالا را انتخاب نمایید."
            />
          </Card>
        ) : results.length === 0 ? (
          <Card variant="subtle" className="p-6">
            <EmptyState
              title="کالایی یافت نشد"
              description="کالایی با مشخصات جستجوشده در کاتالوگ موجود نیست. عبارت دیگری امتحان کنید یا فیلتر دسته‌بندی را حذف نمایید."
              actionLabel="پاک کردن جستجو"
              onAction={() => {
                setQuery("");
                setCategoryId(null);
              }}
            />
          </Card>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {results.map((p) => (
              <Link key={p.id} href={`/retailer/catalog/${p.id}`} className="group block">
                <Card
                  variant="interactive"
                  className="h-full p-4 transition-all duration-[160ms] group-hover:border-[var(--pol-light-brand-primary)] group-hover:shadow-card"
                >
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <h3 className="text-[15px] font-bold text-[var(--pol-light-text-primary)] group-hover:text-[var(--pol-light-brand-primary)] leading-[22px]">
                      {p.canonical_name_fa}
                    </h3>
                    <span className="font-mono text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                      {p.master_sku ?? ""}
                    </span>
                  </div>

                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    {p.brand_name ? (
                      <StatusChip tone="info">{p.brand_name}</StatusChip>
                    ) : null}
                    <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
                      {[p.category_name, p.subcategory_name].filter(Boolean).join(" · ")}
                    </span>
                  </div>

                  {p.default_pack_quantity ? (
                    <div className="mt-3 inline-flex items-center gap-1 rounded-[6px] bg-[var(--pol-light-surface-subtle)] px-2 py-1 text-[11px] text-[var(--pol-light-text-secondary)] border border-[var(--pol-light-border-subtle)]">
                      <span>بسته‌بندی:</span>
                      <span className="font-semibold">
                        {p.default_pack_quantity.toLocaleString("fa-IR")} {p.default_pack_unit ?? p.base_unit ?? ""}
                      </span>
                    </div>
                  ) : null}

                  <div className="mt-4 pt-3 border-t border-[var(--pol-light-border-subtle)] flex items-center justify-between text-[12px]">
                    <span className="text-[var(--pol-light-text-muted)]">مشاهده تأمین‌کنندگان</span>
                    <span className="font-semibold text-[var(--pol-light-brand-primary)] group-hover:translate-x-[-2px] transition-transform">
                      انتخاب کالا ←
                    </span>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}

        {/* Unified Vendors matching search */}
        {unifiedVendors && unifiedVendors.length > 0 ? (
          <div className="mt-6 space-y-3">
            <h3 className="text-[14px] font-bold text-[var(--pol-light-text-primary)]">
              تأمین‌کنندگان منطبق
            </h3>
            <div className="grid gap-2 sm:grid-cols-3">
              {unifiedVendors.map((v) => (
                <Card key={v.id} className="p-3 text-[13px] font-medium text-[var(--pol-light-text-primary)]">
                  <div className="flex items-center gap-2">
                    <div className="size-2 rounded-full bg-[var(--pol-light-brand-primary)]" />
                    <span>{v.business_name ?? v.name ?? v.id}</span>
                  </div>
                </Card>
              ))}
            </div>
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
