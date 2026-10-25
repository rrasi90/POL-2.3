"use client";

import { useCallback, useEffect, useState } from "react";
import { Button, EmptyState, ErrorState, Skeleton } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import type { NotificationPreference, NotificationPreferenceUpdate } from "@pol/types";

type Channel = "PUSH" | "SMS";

const channelLabel: Record<Channel, string> = {
  PUSH: "اعلان برنامه",
  SMS: "پیامک",
};

const notificationCategoryLabels: Readonly<Record<string, string>> = {
  ORDER_STATUS_CHANGED: "تغییر وضعیت سفارش",
  DELIVERY_STATUS_CHANGED: "تغییر وضعیت تحویل",
  RETURN_STATUS_CHANGED: "وضعیت مرجوعی",
  PAYMENT_STATUS_CHANGED: "تغییر وضعیت پرداخت",
  SETTLEMENT_UPDATED: "به‌روزرسانی تسویه",
  SUPPORT_CASE_UPDATED: "به‌روزرسانی درخواست پشتیبانی",
  LOW_STOCK_ALERT: "هشدار کاهش موجودی",
  REFERRAL_REDEEMED: "استفاده از معرفی بنکدار",
};

function formatNotificationCategory(category: string): string {
  return notificationCategoryLabels[category] ?? "سایر اعلان‌ها";
}

type LoadState = "loading" | "error" | "ready";

function ToggleSwitch({
  checked,
  disabled,
  label,
  onToggle,
}: {
  checked: boolean;
  disabled?: boolean;
  label: string;
  onToggle: (next: boolean) => void;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      aria-busy={disabled || undefined}
      disabled={disabled}
      onClick={() => onToggle(!checked)}
      className={[
        "inline-flex h-6 w-11 items-center rounded-full p-0.5",
        "transition-colors duration-[160ms] ease-out",
        "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--pol-light-focus-ring)]",
        "disabled:pointer-events-none disabled:opacity-50",
        checked
          ? "bg-[var(--pol-light-brand-primary)]"
          : "bg-[var(--pol-light-border-strong)] hover:bg-[var(--pol-light-text-muted)]",
      ].join(" ")}
    >
      <span
        aria-hidden
        className={[
          "inline-block size-5 rounded-full bg-white shadow-sm",
          "transition-transform duration-[160ms] ease-out",
          checked ? "translate-x-[-20px]" : "translate-x-0",
        ].join(" ")}
      />
    </button>
  );
}

export default function NotificationPreferencesPage() {
  const [prefs, setPrefs] = useState<NotificationPreference[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [pendingKey, setPendingKey] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const data = await getApi().get<NotificationPreference[]>(
        "/api/v1/notifications/preferences",
      );
      setPrefs(data);
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت ترجیح‌ها ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function toggle(pref: NotificationPreference, channel: Channel, next: boolean) {
    const key = `${pref.category}:${channel}`;
    const snapshot = prefs;
    setPendingKey(key);
    setSaveError(null);
    setPrefs((prev) =>
      prev.map((p) =>
        p.category === pref.category
          ? channel === "PUSH"
            ? { ...p, push_enabled: next }
            : { ...p, sms_enabled: next }
          : p,
      ),
    );
    try {
      await getApi().put<NotificationPreferenceUpdate>("/api/v1/notifications/preferences", {
        event_name: pref.category,
        channel,
        is_enabled: next,
      });
    } catch (err) {
      setPrefs(snapshot);
      setSaveError(err instanceof Error ? err.message : "ذخیره ترجیح ناموفق بود");
    } finally {
      setPendingKey(null);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-3" aria-busy="true" aria-label="در حال بارگذاری ترجیح‌ها">
        <Skeleton className="h-8 w-56" />
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="flex items-center justify-between rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
          >
            <Skeleton className="h-4 w-32" />
            <div className="flex gap-6">
              <Skeleton className="h-6 w-11" />
              <Skeleton className="h-6 w-11" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت ترجیح‌های اعلان ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-4">
      <header>
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          ترجیح‌های اعلان
        </h1>
        <p className="mt-1 text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          کانال‌های دریافت اعلان را برای هر دسته تنظیم کنید.
        </p>
      </header>

      {saveError ? (
        <ErrorState
          title="ذخیره ترجیح ناموفق بود"
          description={saveError}
          onRetry={() => {
            setSaveError(null);
            void load();
          }}
        />
      ) : null}

      {prefs.length === 0 ? (
        <EmptyState
          title="ترجیحی ثبت نشده است"
          description="هنوز ردیف ترجیحی برای حساب شما وجود ندارد."
        />
      ) : (
        <div
          className="overflow-hidden rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)]"
          role="group"
          aria-label="ترجیح‌های اعلان"
        >
          <div className="hidden grid-cols-[1fr_auto_auto] gap-6 border-b border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] px-4 py-2 text-[12px] leading-[18px] font-medium text-[var(--pol-light-text-secondary)] sm:grid">
            <span>دسته</span>
            <span className="w-11 text-center">{channelLabel.PUSH}</span>
            <span className="w-11 text-center">{channelLabel.SMS}</span>
          </div>
          <ul role="list">
            {prefs.map((pref) => (
              <li
                key={pref.category}
                className="grid grid-cols-[1fr_auto_auto] items-center gap-6 border-b border-[var(--pol-light-border-subtle)] px-4 py-3 transition-colors duration-[160ms] last:border-b-0 hover:bg-[var(--pol-light-surface-subtle)] sm:grid"
              >
                <span className="truncate text-[14px] leading-[22px] text-[var(--pol-light-text-primary)]">
                  {pref.category}
                </span>
                <div className="flex w-11 justify-center">
                  <ToggleSwitch
                    checked={pref.push_enabled}
                    disabled={pendingKey === `${pref.category}:PUSH`}
                    label={`${formatNotificationCategory(pref.category)} — ${channelLabel.PUSH}`}
                    onToggle={(next) => void toggle(pref, "PUSH", next)}
                  />
                </div>
                <div className="flex w-11 justify-center">
                  <ToggleSwitch
                    checked={pref.sms_enabled}
                    disabled={pendingKey === `${pref.category}:SMS`}
                    label={`${formatNotificationCategory(pref.category)} — ${channelLabel.SMS}`}
                    onToggle={(next) => void toggle(pref, "SMS", next)}
                  />
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex justify-start">
        <Button variant="ghost" size="sm" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </div>
    </div>
  );
}
