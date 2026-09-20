"use client";

import { useState } from "react";
import { useApi } from "@/lib/hooks/useApi";
import { StatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { api } from "@/lib/api/client";
import type { Product } from "@/lib/types";

type FilterTab = "all" | "active" | "inactive" | "out_of_stock";

const FILTER_TABS: { key: FilterTab; label: string }[] = [
  { key: "all", label: "همه" },
  { key: "active", label: "فعال" },
  { key: "inactive", label: "غیرفعال" },
  { key: "out_of_stock", label: "ناموجود" },
];

function formatToman(value: number): string {
  return new Intl.NumberFormat("fa-IR").format(value) + " تومان";
}

function getProductStatus(product: Product): string {
  if (!product.stock_quantity || product.stock_quantity <= 0) return "OUT_OF_STOCK";
  if (product.vendor_id) return "ACTIVE";
  return "INACTIVE";
}

function SkeletonRow() {
  return (
    <tr className="border-b border-gray-100">
      <td className="px-4 py-3"><div className="h-4 w-32 animate-pulse rounded bg-gray-200" /></td>
      <td className="px-4 py-3"><div className="h-4 w-20 animate-pulse rounded bg-gray-200" /></td>
      <td className="px-4 py-3"><div className="h-4 w-28 animate-pulse rounded bg-gray-200" /></td>
      <td className="px-4 py-3"><div className="h-4 w-12 animate-pulse rounded bg-gray-200" /></td>
      <td className="px-4 py-3"><div className="h-5 w-16 animate-pulse rounded-full bg-gray-200" /></td>
      <td className="px-4 py-3">
        <div className="flex gap-2">
          <div className="h-8 w-16 animate-pulse rounded bg-gray-200" />
          <div className="h-8 w-20 animate-pulse rounded bg-gray-200" />
        </div>
      </td>
    </tr>
  );
}

function MobileSkeletonCard() {
  return (
    <div className="rounded-xl border border-gray-100 bg-white p-4 shadow-sm space-y-3">
      <div className="flex items-start justify-between">
        <div className="h-5 w-40 animate-pulse rounded bg-gray-200" />
        <div className="h-5 w-16 animate-pulse rounded-full bg-gray-200" />
      </div>
      <div className="space-y-2">
        <div className="h-4 w-24 animate-pulse rounded bg-gray-100" />
        <div className="h-4 w-32 animate-pulse rounded bg-gray-100" />
        <div className="h-4 w-16 animate-pulse rounded bg-gray-100" />
      </div>
      <div className="flex gap-2 pt-1">
        <div className="h-8 flex-1 animate-pulse rounded bg-gray-200" />
        <div className="h-8 flex-1 animate-pulse rounded bg-gray-200" />
      </div>
    </div>
  );
}

function MobileProductCard({
  product,
  onToggleStatus,
}: {
  product: Product;
  onToggleStatus: (p: Product) => void;
}) {
  const status = getProductStatus(product);
  return (
    <div className="rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-900">{product.name}</h3>
        <StatusBadge status={status} />
      </div>
      <div className="space-y-1.5 text-sm text-gray-500 mb-3">
        <p>برند: <span className="font-medium text-gray-700">{product.brand || "—"}</span></p>
        <p>قیمت: <span className="font-medium text-gray-700">{formatToman(product.unit_price_toman)}</span></p>
        <p>موجودی: <span className="font-medium text-gray-700">{product.stock_quantity ?? 0} {product.unit}</span></p>
      </div>
      <div className="flex gap-2">
        <Button variant="secondary" size="sm" className="flex-1">
          ویرایش
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="flex-1"
          onClick={() => onToggleStatus(product)}
        >
          غیرفعال کردن
        </Button>
      </div>
    </div>
  );
}

export default function VendorCatalogPage() {
  const { data: catalogData, isLoading: loading } = useApi<{ data: Product[] }>("/api/v1/vendor/catalog");
  const [search, setSearch] = useState("");
  const [activeTab, setActiveTab] = useState<FilterTab>("all");

  const products = catalogData?.data ?? [];

  const filtered = products.filter((p) => {
    const matchesSearch =
      !search ||
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      (p.brand && p.brand.toLowerCase().includes(search.toLowerCase()));

    const status = getProductStatus(p);
    const matchesTab =
      activeTab === "all" ||
      (activeTab === "active" && status === "ACTIVE") ||
      (activeTab === "inactive" && status === "INACTIVE") ||
      (activeTab === "out_of_stock" && status === "OUT_OF_STOCK");

    return matchesSearch && matchesTab;
  });

  const handleToggleStatus = async (product: Product) => {
    try {
      await api.patch(`/api/v1/vendor/catalog/${product.id}`, {
        is_active: getProductStatus(product) !== "ACTIVE",
      });
    } catch {
      // silently fail
    }
  };

  return (
    <div className="min-h-screen bg-gray-50/50 p-6" dir="rtl">
      <div className="mx-auto max-w-7xl space-y-6">
        {/* Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-2xl font-bold text-gray-900">کاتالوگ محصولات</h1>
          <Button variant="primary" size="md">
            افزودن محصول جدید
          </Button>
        </div>

        {/* Search + Filters */}
        <div className="space-y-4">
          <input
            type="text"
            placeholder="جستجوی نام محصول یا برند..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
          <div className="flex gap-2 overflow-x-auto">
            {FILTER_TABS.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`whitespace-nowrap rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                  activeTab === tab.key
                    ? "bg-primary-800 text-white"
                    : "bg-white text-gray-600 hover:bg-gray-100"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Loading State */}
        {loading ? (
          <>
            <div className="hidden overflow-x-auto rounded-xl border border-gray-100 bg-white shadow-sm md:block">
              <table className="w-full text-right text-sm">
                <thead className="border-b border-gray-100 bg-gray-50/80">
                  <tr>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500">نام محصول</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500">برند</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500">قیمت (تومان)</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500">موجودی</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500">وضعیت</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500">عملیات</th>
                  </tr>
                </thead>
                <tbody>
                  {Array.from({ length: 5 }).map((_, i) => (
                    <SkeletonRow key={i} />
                  ))}
                </tbody>
              </table>
            </div>
            <div className="space-y-3 md:hidden">
              {Array.from({ length: 3 }).map((_, i) => (
                <MobileSkeletonCard key={i} />
              ))}
            </div>
          </>
        ) : filtered.length === 0 ? (
          <EmptyState
            title="هنوز محصولی اضافه نکرده‌اید"
            description="محصولات خود را به کاتالوگ اضافه کنید تا خریداران بتوانند آن‌ها را مشاهده کنند."
            action={
              <Button variant="primary" size="md" className="mt-2">
                افزودن محصول جدید
              </Button>
            }
          />
        ) : (
          <>
            {/* Desktop Table */}
            <div className="hidden overflow-x-auto rounded-xl border border-gray-100 bg-white shadow-sm md:block">
              <table className="w-full text-right text-sm">
                <thead className="border-b border-gray-100 bg-gray-50/80">
                  <tr>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500">نام محصول</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500">برند</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500">قیمت (تومان)</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500">موجودی</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500">وضعیت</th>
                    <th className="px-4 py-3 text-xs font-medium text-gray-500">عملیات</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((product) => {
                    const status = getProductStatus(product);
                    return (
                      <tr
                        key={product.id}
                        className="border-b border-gray-50 transition-colors hover:bg-gray-50/50"
                      >
                        <td className="px-4 py-3 font-medium text-gray-900">{product.name}</td>
                        <td className="px-4 py-3 text-gray-600">{product.brand || "—"}</td>
                        <td className="px-4 py-3 text-gray-600">{formatToman(product.unit_price_toman)}</td>
                        <td className="px-4 py-3 text-gray-600">
                          {product.stock_quantity ?? 0} {product.unit}
                        </td>
                        <td className="px-4 py-3">
                          <StatusBadge status={status} />
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex gap-2">
                            <Button variant="secondary" size="sm">
                              ویرایش
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleToggleStatus(product)}
                            >
                              غیرفعال کردن
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Mobile Cards */}
            <div className="space-y-3 md:hidden">
              {filtered.map((product) => (
                <MobileProductCard
                  key={product.id}
                  product={product}
                  onToggleStatus={handleToggleStatus}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
