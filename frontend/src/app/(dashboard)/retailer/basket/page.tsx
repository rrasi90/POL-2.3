"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState, EmptyBoxIcon } from "@/components/ui/EmptyState";

interface BasketItem {
  id: string;
  product_id: string;
  name: string;
  vendor_name: string;
  unit_price: number;
  quantity: number;
  pack_size?: string;
  unit?: string;
}

const STORAGE_KEY = "pol_basket";

function loadBasket(): BasketItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveBasket(items: BasketItem[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  } catch {
    // storage full or unavailable
  }
}

function formatToman(value: number): string {
  return new Intl.NumberFormat("fa-IR").format(value) + " تومان";
}

function BasketSkeleton() {
  return (
    <div className="flex flex-col gap-4">
      {Array.from({ length: 2 }).map((_, i) => (
        <div key={i} className="animate-pulse rounded-xl border border-gray-200 bg-white p-4">
          <div className="mb-3 h-4 w-32 rounded bg-gray-200" />
          <div className="flex flex-col gap-3">
            {Array.from({ length: 2 }).map((_, j) => (
              <div key={j} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="h-4 w-40 rounded bg-gray-200" />
                  <div className="h-3 w-20 rounded bg-gray-100" />
                </div>
                <div className="h-4 w-24 rounded bg-gray-200" />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function BasketPage() {
  const [basketItems, setBasketItems] = useState<BasketItem[]>([]);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setBasketItems(loadBasket());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated) {
      saveBasket(basketItems);
    }
  }, [basketItems, hydrated]);

  const updateQuantity = useCallback((itemId: string, delta: number) => {
    setBasketItems((prev) =>
      prev
        .map((item) =>
          item.id === itemId
            ? { ...item, quantity: Math.max(1, item.quantity + delta) }
            : item
        )
    );
  }, []);

  const removeItem = useCallback((itemId: string) => {
    setBasketItems((prev) => prev.filter((item) => item.id !== itemId));
  }, []);

  const groupedByVendor = useMemo(() => {
    const groups: Record<string, BasketItem[]> = {};
    for (const item of basketItems) {
      const key = item.vendor_name;
      if (!groups[key]) groups[key] = [];
      groups[key].push(item);
    }
    return groups;
  }, [basketItems]);

  const grandTotal = useMemo(
    () => basketItems.reduce((sum, item) => sum + item.unit_price * item.quantity, 0),
    [basketItems]
  );

  if (!hydrated) {
    return (
      <div className="min-h-screen bg-gray-50/50 p-6" dir="rtl">
        <div className="mx-auto max-w-3xl space-y-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">سبد خرید</h1>
          </div>
          <BasketSkeleton />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50/50 p-6" dir="rtl">
      <div className="mx-auto max-w-3xl space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">سبد خرید</h1>
          <p className="mt-1 text-sm text-gray-500">
            {basketItems.length > 0
              ? `${basketItems.length} کالا از ${Object.keys(groupedByVendor).length} فروشنده`
              : "محصولات انتخابی شما"}
          </p>
        </div>

        {basketItems.length === 0 ? (
          <EmptyState
            icon={<EmptyBoxIcon />}
            title="سبد خرید شما خالی است"
            description="محصولات مورد نظر خود را از کاتالوگ اضافه کنید."
            action={
              <Link href="/retailer">
                <Button variant="primary">مشاهده کاتالوگ</Button>
              </Link>
            }
          />
        ) : (
          <>
            <div className="flex flex-col gap-4">
              {Object.entries(groupedByVendor).map(([vendorName, items]) => {
                const vendorSubtotal = items.reduce(
                  (sum, item) => sum + item.unit_price * item.quantity,
                  0
                );

                return (
                  <div
                    key={vendorName}
                    className="rounded-xl border border-gray-200 bg-white"
                  >
                    <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-xs font-bold text-primary-700">
                          {vendorName.charAt(0)}
                        </div>
                        <span className="text-sm font-semibold text-gray-900">
                          {vendorName}
                        </span>
                        <Badge variant="info" size="sm">
                          {items.length} کالا
                        </Badge>
                      </div>
                      <span className="text-xs text-gray-500">
                        جمع: {formatToman(vendorSubtotal)}
                      </span>
                    </div>

                    <div className="divide-y divide-gray-50">
                      {items.map((item) => (
                        <div
                          key={item.id}
                          className="flex items-center justify-between gap-3 px-4 py-3"
                        >
                          <div className="flex flex-col gap-0.5">
                            <span className="text-sm font-medium text-gray-900">
                              {item.name}
                            </span>
                            <span className="text-xs text-gray-400">
                              {formatToman(item.unit_price)} / واحد
                              {item.pack_size && ` · ${item.pack_size}`}
                            </span>
                          </div>

                          <div className="flex items-center gap-3">
                            <div className="flex items-center gap-1 rounded-lg border border-gray-200">
                              <button
                                onClick={() => updateQuantity(item.id, -1)}
                                disabled={item.quantity <= 1}
                                className="flex h-8 w-8 items-center justify-center text-gray-500 transition-colors hover:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-300"
                              >
                                −
                              </button>
                              <span className="min-w-[2rem] text-center text-sm font-medium text-gray-900">
                                {item.quantity}
                              </span>
                              <button
                                onClick={() => updateQuantity(item.id, 1)}
                                className="flex h-8 w-8 items-center justify-center text-gray-500 transition-colors hover:bg-gray-100"
                              >
                                +
                              </button>
                            </div>

                            <span className="min-w-[100px] text-left text-sm font-bold text-gray-900">
                              {formatToman(item.unit_price * item.quantity)}
                            </span>

                            <button
                              onClick={() => removeItem(item.id)}
                              className="flex h-8 w-8 items-center justify-center rounded-md text-gray-400 transition-colors hover:bg-red-50 hover:text-red-500"
                              title="حذف"
                            >
                              <svg
                                className="h-4 w-4"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                strokeWidth={2}
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  d="M6 18L18 6M6 6l12 12"
                                />
                              </svg>
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="rounded-xl border border-gray-200 bg-white p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">جمع کل</span>
                <span className="text-xl font-bold text-gray-900">
                  {formatToman(grandTotal)}
                </span>
              </div>
            </div>

            <div className="flex gap-3">
              <Link href="/retailer" className="flex-1">
                <Button variant="secondary" className="w-full">
                  ادامه خرید
                </Button>
              </Link>
              <Link href="/retailer/checkout" className="flex-1">
                <Button variant="primary" className="w-full">
                  رفتن به تسویه حساب
                </Button>
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
