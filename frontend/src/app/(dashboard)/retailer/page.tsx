"use client";

import { useState, useMemo } from "react";
import { useApi } from "@/lib/hooks/useApi";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState, EmptyProductIcon } from "@/components/ui/EmptyState";
import type { Product } from "@/lib/types";

function formatToman(value: number): string {
  return value.toLocaleString("fa-IR") + " تومان";
}

function ProductSkeleton() {
  return (
    <div className="animate-pulse rounded-xl border border-neutral-200 bg-white p-3">
      <div className="mb-3 aspect-square rounded-lg bg-neutral-200" />
      <div className="mb-2 h-4 w-3/4 rounded bg-neutral-200" />
      <div className="mb-2 h-3 w-1/2 rounded bg-neutral-200" />
      <div className="mb-3 h-3 w-2/3 rounded bg-neutral-200" />
      <div className="flex items-center justify-between">
        <div className="h-5 w-20 rounded bg-neutral-200" />
        <div className="h-8 w-16 rounded bg-neutral-200" />
      </div>
    </div>
  );
}

export default function RetailerCatalogPage() {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedBrand, setSelectedBrand] = useState<string | null>(null);

  const params = useMemo(() => {
    const p: Record<string, string> = {};
    if (search) p.search = search;
    if (selectedCategory) p.category = selectedCategory;
    if (selectedBrand) p.brand = selectedBrand;
    return p;
  }, [search, selectedCategory, selectedBrand]);

  const { data: productsData, isLoading: productsLoading } = useApi<{
    results: Product[];
    count: number;
  }>("/api/v1/catalog/products", params);

  const { data: categoriesData, isLoading: categoriesLoading } = useApi<{
    results: { id: string; name: string }[];
  }>("/api/v1/catalog/categories");

  const { data: brandsData, isLoading: brandsLoading } = useApi<{
    results: { id: string; name: string }[];
  }>("/api/v1/catalog/brands");

  const products = productsData?.results ?? [];
  const categories = categoriesData?.results ?? [];
  const brands = brandsData?.results ?? [];

  return (
    <div className="flex flex-col gap-5 p-4 md:p-6">
      <div>
        <h1 className="text-xl font-bold text-neutral-900">کاتالوگ محصولات</h1>
        <p className="mt-1 text-sm text-neutral-500">مشاهده و افزودن محصولات به سبد خرید</p>
      </div>

      <div className="relative">
        <svg
          className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="جستجوی محصول..."
          className="w-full rounded-xl border border-neutral-300 bg-white py-3 pr-10 pl-4 text-sm text-neutral-900 placeholder-neutral-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        />
      </div>

      {!categoriesLoading && categories.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors ${
              selectedCategory === null
                ? "bg-primary-600 text-white"
                : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
            }`}
          >
            همه دسته‌ها
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(selectedCategory === cat.id ? null : cat.id)}
              className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                selectedCategory === cat.id
                  ? "bg-primary-600 text-white"
                  : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>
      )}

      {!brandsLoading && brands.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          <button
            onClick={() => setSelectedBrand(null)}
            className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors ${
              selectedBrand === null
                ? "bg-primary-600 text-white"
                : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
            }`}
          >
            همه برندها
          </button>
          {brands.map((brand) => (
            <button
              key={brand.id}
              onClick={() => setSelectedBrand(selectedBrand === brand.id ? null : brand.id)}
              className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                selectedBrand === brand.id
                  ? "bg-primary-600 text-white"
                  : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
              }`}
            >
              {brand.name}
            </button>
          ))}
        </div>
      )}

      {productsLoading ? (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 md:gap-4 lg:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <ProductSkeleton key={i} />
          ))}
        </div>
      ) : products.length === 0 ? (
        <EmptyState
          icon={<EmptyProductIcon />}
          title="محصولی یافت نشد"
          description="با تغییر فیلترها یا عبارت جستجو، محصول مورد نظر خود را پیدا کنید."
        />
      ) : (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 md:gap-4 lg:grid-cols-4">
          {products.map((product) => (
            <div
              key={product.id}
              className="flex flex-col rounded-xl border border-neutral-200 bg-white transition-shadow hover:shadow-md"
            >
              <div className="relative aspect-square flex items-center justify-center rounded-t-xl bg-neutral-100">
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="h-full w-full rounded-t-xl object-cover"
                  />
                ) : (
                  <svg
                    className="h-10 w-10 text-neutral-300"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={1.5}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z"
                    />
                  </svg>
                )}
              </div>

              <div className="flex flex-1 flex-col gap-1 p-3">
                <h3 className="text-[14px] font-semibold leading-tight text-neutral-900 line-clamp-2">
                  {product.name}
                </h3>
                <p className="text-xs text-neutral-500">{product.brand}</p>
                {product.vendor_name && (
                  <Badge variant="info" size="sm">
                    {product.vendor_name}
                  </Badge>
                )}
                <p className="mt-auto text-xs text-neutral-400">
                  {product.pack_size} × {product.unit}
                </p>
              </div>

              <div className="flex items-center justify-between border-t border-neutral-100 p-3 pt-2">
                <span className="text-sm font-bold text-neutral-900">
                  {formatToman(product.unit_price_toman)}
                </span>
                <Button variant="primary" size="sm">
                  افزودن به سبد
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
