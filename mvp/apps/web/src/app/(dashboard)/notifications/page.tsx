"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Button, EmptyState, ErrorState, Skeleton, StatusChip, type StatusTone } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import type { NotificationItem } from "@pol/types";

const PAGE_SIZE = 50;

const priorityTone: Record<string, StatusTone> = {
  CRITICAL: "danger",
  HIGH: "warning",
  NORMAL: "info",
  LOW: "neutral",
};

const priorityLabel: Record<string, string> = {
  CRITICAL: "بحرانی",
  HIGH: "زیاد",
  NORMAL: "عادی",
  LOW: "کم",
};

function unreadOf(item: NotificationItem): boolean | null {
  if (typeof item.is_read === "boolean") return !item.is_read;
  if (typeof item.read === "boolean") return !item.read;
  return null;
}

function formatDateTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleString("fa-IR", { dateStyle: "medium", timeStyle: "short" });
}

type LoadState = "loading" | "error" | "ready";

export default function NotificationsPage() {
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const [exhausted, setExhausted] = useState(false);
  const itemsRef = useRef<NotificationItem[]>([]);
  const loadingRef = useRef(false);

  const load = useCallback(async (reset: boolean) => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    if (reset) {
      setState("loading");
      setErrorMessage(null);
      setExhausted(false);
    } else {
      setLoadingMore(true);
    }
    try {
      const offset = reset ? 0 : itemsRef.current.length;
      const data = await getApi().get<NotificationItem[]>(
        `/api/v1/notifications?limit=${PAGE_SIZE}&offset=${offset}`,
      );
      itemsRef.current = reset ? data : [...itemsRef.current, ...data];
      setItems(itemsRef.current);
      if (data.length < PAGE_SIZE) setExhausted(true);
      setState("ready");
    } catch (err) {
      if (reset) {
        setErrorMessage(err instanceof Error ? err.message : "دریافت اعلان‌ها ناموفق بود");
        setState("error");
      } else {
        setExhausted(true);
      }
    } finally {
      loadingRef.current = false;
      setLoadingMore(false);
    }
  }, []);

  useEffect(() => {
    void load(true);
  }, [load]);

  if (state === "loading") {
    return (
      <div className="space-y-3" aria-busy="true" aria-label="در حال بارگذاری اعلان‌ها">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
          >
            <Skeleton className="mb-2 h-4 w-1/3" />
            <Skeleton lines={2} />
          </div>
        ))}
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

  if (items.length === 0) {
    return (
      <div className="space-y-4">
        <PageHeader count={0} />
        <EmptyState
          title="اعلانی وجود ندارد"
          description="وقتی اعلان جدیدی برای شما ثبت شود، اینجا نمایش داده می‌شود."
        />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <PageHeader count={items.length} />
      <ul role="list" className="space-y-2">
        {items.map((item) => {
          const unread = unreadOf(item);
          return (
            <li
              key={item.id}
              className={[
                "rounded-[12px] border bg-[var(--pol-light-surface-default)] p-4",
                "transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]",
                unread
                  ? "border-[var(--pol-light-brand-primary)]"
                  : "border-[var(--pol-light-border-subtle)]",
              ].join(" ")}
            >
              <div className="flex flex-wrap items-center gap-2">
                <StatusChip tone={priorityTone[item.priority] ?? "neutral"}>
                  {priorityLabel[item.priority] ?? item.priority}
                </StatusChip>
                {unread ? <StatusChip tone="info">خوانده‌نشده</StatusChip> : null}
                <span className="ms-auto text-[11px] leading-[16px] text-[var(--pol-light-text-muted)]">
                  {formatDateTime(item.created_at)}
                </span>
              </div>
              <p className="mt-2 text-[14px] leading-[22px] font-semibold text-[var(--pol-light-text-primary)]">
                {item.title}
              </p>
              <p className="mt-1 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
                {item.body}
              </p>
              <p
                className="mt-2 text-[11px] leading-[16px] text-[var(--pol-light-text-muted)]"
                dir="ltr"
              >
                {item.event_name}
              </p>
            </li>
          );
        })}
      </ul>
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

function PageHeader({ count }: { count: number }) {
  return (
    <header className="flex flex-wrap items-baseline gap-3">
      <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
        اعلان‌ها
      </h1>
      {count > 0 ? (
        <span className="text-[12px] leading-[18px] text-[var(--pol-light-text-muted)]">
          {count.toLocaleString("fa-IR")} مورد
        </span>
      ) : null}
    </header>
  );
}
