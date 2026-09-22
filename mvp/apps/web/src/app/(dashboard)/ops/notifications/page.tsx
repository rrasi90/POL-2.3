"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Button,
  EmptyState,
  ErrorState,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  cardCls,
  formatDateTime,
  itemsOf,
  notificationPriorityLabel,
  notificationPriorityTone,
  type LoadState,
} from "../_shared";

const PAGE_SIZE = 50;

interface NotificationRow {
  id: string;
  event_name?: string | null;
  title?: string | null;
  body?: string | null;
  priority?: string | null;
  created_at?: string | null;
}

export default function OpsNotificationsPage() {
  const [items, setItems] = useState<NotificationRow[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [exhausted, setExhausted] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);

  const load = useCallback(async (reset: boolean) => {
    if (reset) {
      setState("loading");
      setErrorMessage(null);
      setExhausted(false);
    } else {
      setLoadingMore(true);
    }
    try {
      const offset = reset ? 0 : items.length;
      const data = await getApi().get<unknown>(
        `/api/v1/notifications?limit=${PAGE_SIZE}&offset=${offset}`,
      );
      const rows = itemsOf<NotificationRow>(data);
      setItems((prev) => (reset ? rows : [...prev, ...rows]));
      if (rows.length < PAGE_SIZE) setExhausted(true);
      setState("ready");
    } catch (err) {
      if (reset) {
        setErrorMessage(err instanceof Error ? err.message : "دریافت اعلان‌ها ناموفق بود");
        setState("error");
      } else {
        setExhausted(true);
      }
    } finally {
      setLoadingMore(false);
    }
  }, [items.length]);

  useEffect(() => {
    void load(true);
  }, []);

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری اعلان‌ها">
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
        title="دریافت اعلان‌ها ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load(true)}
      />
    );
  }

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          عملیات اعلان
        </h1>
        <StatusChip tone="warning">Provider GAP</StatusChip>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">O-08</span>
        <Button
          variant="secondary"
          size="sm"
          className="ms-auto"
          onClick={() => void load(true)}
        >
          به‌روزرسانی
        </Button>
      </header>

      <div className="rounded-[12px] border border-dashed border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-subtle)] p-3">
        <p className="text-[13px] text-[var(--pol-light-text-secondary)]">
          شکاف: هیچ API برای عملیات Provider اعلان (ارسال مجدد، صف، تنظیمات ارائه‌دهنده) وجود
          ندارد — فقط فهرست واقعی GET /notifications در دسترس است.
        </p>
      </div>

      {items.length === 0 ? (
        <EmptyState
          title="اعلانی وجود ندارد"
          description="وقتی اعلان جدیدی ثبت شود، اینجا نمایش داده می‌شود."
        />
      ) : (
        <ul role="list" className="space-y-2">
          {items.map((n) => (
            <li key={n.id} className={cardCls}>
              <div className="flex flex-wrap items-center gap-2">
                <StatusChip tone={notificationPriorityTone[n.priority ?? ""] ?? "neutral"}>
                  {notificationPriorityLabel[n.priority ?? ""] ?? n.priority ?? "—"}
                </StatusChip>
                <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                  {formatDateTime(n.created_at)}
                </span>
              </div>
              <p className="mt-2 text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
                {n.title}
              </p>
              <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">{n.body}</p>
              <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                {n.event_name}
              </p>
            </li>
          ))}
        </ul>
      )}

      {!exhausted ? (
        <div className="flex justify-center pt-2">
          <Button variant="secondary" loading={loadingMore} onClick={() => void load(false)}>
            بارگذاری موارد بیشتر
          </Button>
        </div>
      ) : null}
    </div>
  );
}
