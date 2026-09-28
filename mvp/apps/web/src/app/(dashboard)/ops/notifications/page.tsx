"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Button,
  EmptyState,
  ErrorState,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  ageLabel,
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

  const counts = useMemo(() => {
    let critical = 0;
    let high = 0;
    let normal = 0;
    for (const item of items) {
      if (item.priority === "CRITICAL") critical++;
      else if (item.priority === "HIGH") high++;
      else normal++;
    }
    return { total: items.length, critical, high, normal };
  }, [items]);

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری اعلان‌ها">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-3 sm:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className={cardCls}><Skeleton lines={2} /></div>
          ))}
        </div>
        <div className={cardCls}>
          <Skeleton lines={6} />
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
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline justify-between gap-3 border-b border-[var(--pol-light-border-subtle)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] leading-[30px] font-bold text-[var(--pol-light-text-primary)]">
              مرکز اعلان‌های سیستمی
            </h1>
            <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              O-08
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-muted)]">
            مشاهده لاگ رویدادها، خطاهای ارسالی و پیام‌های فوری پلتفرم
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => void load(true)}
          >
            به‌روزرسانی
          </Button>
        </div>
      </header>

      {/* KPI Counters */}
      <section aria-label="خلاصه اولویت‌ها" className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className={cardCls}>
          <p className="text-[12px] font-medium text-[var(--pol-light-text-muted)]">کل اعلان‌های دریافتی</p>
          <p className="mt-1 text-[24px] font-bold text-[var(--pol-light-text-primary)]">{counts.total.toLocaleString("fa-IR")}</p>
        </div>
        <div className={cardCls}>
          <p className="text-[12px] font-medium text-[var(--pol-light-semantic-danger)]">بحرانی (CRITICAL)</p>
          <p className="mt-1 text-[24px] font-bold text-[var(--pol-light-semantic-danger)]">{counts.critical.toLocaleString("fa-IR")}</p>
        </div>
        <div className={cardCls}>
          <p className="text-[12px] font-medium text-[var(--pol-light-semantic-warning)]">اولویت بالا (HIGH)</p>
          <p className="mt-1 text-[24px] font-bold text-[var(--pol-light-semantic-warning)]">{counts.high.toLocaleString("fa-IR")}</p>
        </div>
        <div className={cardCls}>
          <p className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">عادی / کم</p>
          <p className="mt-1 text-[24px] font-bold text-[var(--pol-light-text-primary)]">{counts.normal.toLocaleString("fa-IR")}</p>
        </div>
      </section>

      {/* Architectural Gap Banner */}
      <div className="rounded-xl border border-[var(--pol-light-semantic-warning)]/30 bg-[var(--pol-light-semantic-warning)]/10 p-3.5 text-[12px] leading-[20px] text-[var(--pol-light-text-secondary)]">
        <strong className="font-semibold text-[var(--pol-light-semantic-warning)]">وضعیت ارائه‌دهنده پیامک/اعلان: </strong>
        عملیات Provider اعلان (تنظیمات صف پیامکی و درگاه) در نسخه فعلی MVP بر عهده سرویس پس‌زمینه است. داده‌های زیر مستقیماً از لاگ واقعی رویدادهای سرور واکشی شده‌اند.
      </div>

      {items.length === 0 ? (
        <EmptyState
          title="اعلانی ثبت نشده است"
          description="وقتی پیام یا رویداد سیستمی جدیدی ثبت شود، در این بخش فهرست می‌شود."
        />
      ) : (
        <ul role="list" className="space-y-3">
          {items.map((n) => (
            <li key={n.id} className={cardCls}>
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--pol-light-border-subtle)] pb-2.5">
                <div className="flex items-center gap-2">
                  <StatusChip tone={notificationPriorityTone[n.priority ?? ""] ?? "neutral"}>
                    {notificationPriorityLabel[n.priority ?? ""] ?? n.priority ?? "—"}
                  </StatusChip>
                  {n.event_name ? (
                    <span className="rounded-md border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 font-mono text-[11px] text-[var(--pol-light-text-secondary)]" dir="ltr">
                      {n.event_name}
                    </span>
                  ) : null}
                </div>
                <div className="flex items-center gap-2 text-[11px] text-[var(--pol-light-text-muted)]">
                  <span>{ageLabel(n.created_at)}</span>
                  <span>·</span>
                  <span>{formatDateTime(n.created_at)}</span>
                </div>
              </div>
              <p className="mt-2.5 text-[14px] font-bold text-[var(--pol-light-text-primary)]">
                {n.title ?? "بدون عنوان"}
              </p>
              {n.body ? (
                <p className="mt-1 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
                  {n.body}
                </p>
              ) : null}
              <div className="mt-2.5 text-[11px] font-mono text-[var(--pol-light-text-muted)]" dir="ltr">
                ID: {n.id}
              </div>
            </li>
          ))}
        </ul>
      )}

      {!exhausted && items.length > 0 ? (
        <div className="flex justify-center pt-2">
          <Button variant="secondary" size="sm" loading={loadingMore} onClick={() => void load(false)}>
            بارگذاری ۵۰ مورد بعدی
          </Button>
        </div>
      ) : null}
    </div>
  );
}
