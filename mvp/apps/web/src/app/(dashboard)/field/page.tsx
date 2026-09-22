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
  type StatusTone,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  ageLabel,
  ageTone,
  cardCls,
  formatDateTime,
  itemsOf,
  str,
  type LoadState,
} from "../ops/_shared";

const taskStatusTone: Record<string, StatusTone> = {
  PENDING: "warning",
  IN_PROGRESS: "info",
  COMPLETED: "success",
  CANCELLED: "neutral",
  OPEN: "warning",
  DONE: "success",
  CLOSED: "neutral",
};

const taskStatusLabel: Record<string, string> = {
  PENDING: "در انتظار",
  IN_PROGRESS: "در حال انجام",
  COMPLETED: "تکمیل‌شده",
  CANCELLED: "لغوشده",
  OPEN: "باز",
  DONE: "انجام‌شده",
  CLOSED: "بسته",
};

interface FieldTask {
  id: string;
  task_type?: string | null;
  status?: string | null;
  notes?: string | null;
  due_date?: string | null;
  created_at?: string | null;
  completed_at?: string | null;
}

function useOnline(): boolean {
  const [online, setOnline] = useState(true);
  useEffect(() => {
    setOnline(typeof navigator !== "undefined" ? navigator.onLine : true);
    const on = () => setOnline(true);
    const off = () => setOnline(false);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => {
      window.removeEventListener("online", on);
      window.removeEventListener("offline", off);
    };
  }, []);
  return online;
}

export default function FieldTasksPage() {
  const [tasks, setTasks] = useState<FieldTask[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const online = useOnline();

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const data = await getApi().get<unknown>("/api/v1/field/tasks?limit=50&offset=0");
      setTasks(itemsOf<FieldTask>(data, "tasks"));
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت وظایف ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const filtered = tasks.filter((t) => {
    if (!query.trim()) return true;
    const q = query.trim().toLowerCase();
    return (
      str(t.task_type, "").toLowerCase().includes(q) ||
      str(t.notes, "").toLowerCase().includes(q) ||
      str(t.id, "").toLowerCase().includes(q)
    );
  });

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری وظایف میدانی">
        <Skeleton className="h-8 w-48" />
        <div className={cardCls}>
          <Skeleton lines={5} />
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت وظایف میدانی ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          فعال‌سازی میدانی
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">F-01</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      {!online ? (
        <div
          role="status"
          className="rounded-[12px] border border-[var(--pol-light-semantic-warning)]/40 bg-[var(--pol-light-surface-default)] p-3"
        >
          <p className="text-[13px] font-semibold text-[var(--pol-light-semantic-warning)]">
            آفلاین — F-05
          </p>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
            اتصال شبکه قطع است. تغییرات هنگام اتصال مجدد همگام‌سازی می‌شوند.
          </p>
        </div>
      ) : null}

      <section aria-label="دسترسی سریع" className="grid gap-3 sm:grid-cols-2">
        <Link
          href="/retailer/catalog"
          className={`${cardCls} transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]`}
        >
          <p className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
            سفارش کمکی (F-03)
          </p>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
            کاتالوگ خرده‌فروشی برای ثبت سفارش کمکی — جریان‌های retail embedded.
          </p>
        </Link>
        <div className={`${cardCls} border-dashed`}>
          <p className="text-[14px] font-semibold text-[var(--pol-light-text-secondary)]">
            فعال‌سازی خرده‌فروش (F-02)
          </p>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]">
            جزئیات وظیفه و PATCH وضعیت/یادداشت از طریق لیست زیر.
          </p>
        </div>
      </section>

      <section aria-label="فهرست وظایف">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
            وظایف امروز
          </h2>
          <SearchField
            label="جستجوی وظیفه"
            placeholder="جستجو…"
            className="ms-auto w-full max-w-xs"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        {filtered.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="وظیفه‌ای وجود ندارد"
              description="وقتی وظیفه جدیدی واگذار شود، اینجا نمایش داده می‌شود."
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {filtered.map((t) => (
              <li key={str(t.id)}>
                <Link
                  href={`/field/tasks/${t.id}`}
                  className="block rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4 transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusChip tone={taskStatusTone[t.status ?? ""] ?? "neutral"}>
                      {taskStatusLabel[t.status ?? ""] ?? t.status ?? "—"}
                    </StatusChip>
                    <span className="text-[12px] text-[var(--pol-light-text-secondary)]" dir="ltr">
                      {t.task_type ?? "—"}
                    </span>
                    <StatusChip tone={ageTone(t.created_at, 48, 168)}>
                      {ageLabel(t.created_at)}
                    </StatusChip>
                    <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                      {formatDateTime(t.created_at)}
                    </span>
                  </div>
                  {t.notes ? (
                    <p className="mt-2 line-clamp-2 text-[13px] text-[var(--pol-light-text-secondary)]">
                      {t.notes}
                    </p>
                  ) : null}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
