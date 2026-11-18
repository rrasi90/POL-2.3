"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Button } from "@pol/ui";
import { getLastCorrelationId } from "@pol/api-client";

export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const correlationId = getLastCorrelationId();

  useEffect(() => {
    console.error("unhandled-render-error", error.digest ?? "no-digest");
  }, [error]);

  return (
    <main
      dir="rtl"
      className="flex min-h-screen flex-col items-center justify-center gap-6 bg-[var(--pol-light-bg-canvas)] px-6 text-center text-[var(--pol-light-text-primary)]"
    >
      <div className="max-w-md space-y-3">
        <h1 className="text-2xl font-black">مشکلی در نمایش این صفحه پیش آمد</h1>
        <p className="text-sm leading-7 text-[var(--pol-light-text-secondary)]">
          بارگذاری صفحه ناموفق بود. برای اطمینان از تکرار نشدن عملیات، وضعیت سفارش یا پرداخت را
          پیش از ثبت دوباره بررسی کنید.
        </p>
        {correlationId || error.digest ? (
          <p className="text-xs text-[var(--pol-light-text-secondary)]">
            کد پیگیری: <span className="font-mono">{correlationId ?? error.digest}</span>
          </p>
        ) : null}
      </div>
      <div className="flex flex-wrap items-center justify-center gap-3">
        <Button onClick={() => reset()}>تلاش دوباره</Button>
        <Link
          href="/"
          className="rounded-xl border border-[var(--pol-light-border-subtle)] px-4 py-2 text-sm font-semibold"
        >
          بازگشت به صفحهٔ اصلی
        </Link>
      </div>
    </main>
  );
}
