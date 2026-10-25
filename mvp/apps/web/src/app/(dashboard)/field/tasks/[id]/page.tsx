"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Button, ErrorState, Skeleton, StatusChip, type StatusTone } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, formatDateTime, inputCls, str, type LoadState } from "../../../ops/_shared";

const fieldTaskTypeLabel: Record<string, string> = {
  VENDOR_ONBOARDING: "فعال‌سازی بنکدار",
  RETAILER_ONBOARDING: "فعال‌سازی خرده‌فروش",
  STORE_VISIT: "بازدید فروشگاه",
  TRAINING: "آموزش",
  CATALOG_REVIEW: "بررسی کاتالوگ",
  INVENTORY_CHECK: "بررسی موجودی",
  ORDER_FOLLOW_UP: "پیگیری سفارش",
  DELIVERY_FOLLOW_UP: "پیگیری تحویل",
  SUPPORT_FOLLOW_UP: "پیگیری پشتیبانی",
  GENERAL: "وظیفه عمومی",
};

const taskStatusTone: Record<string, StatusTone> = {
  PENDING: "warning",
  IN_PROGRESS: "info",
  COMPLETED: "success",
  CANCELLED: "neutral",
  FAILED: "danger",
  OPEN: "warning",
  DONE: "success",
  CLOSED: "neutral",
};

const taskStatusLabel: Record<string, string> = {
  PENDING: "در انتظار",
  IN_PROGRESS: "در حال انجام",
  COMPLETED: "تکمیل‌شده",
  CANCELLED: "لغوشده",
  FAILED: "ناموفق",
  OPEN: "باز",
  DONE: "انجام‌شده",
  CLOSED: "بسته",
};

interface FieldTask {
  id: string;
  task_type?: string | null;
  assigned_to_user_id?: string | null;
  target_organization_id?: string | null;
  status?: string | null;
  notes?: string | null;
  due_date?: string | null;
  completed_at?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export default function FieldTaskDetailPage() {
  const params = useParams<{ id: string }>();
  const taskId = str(params?.id, "");
  const [task, setTask] = useState<FieldTask | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [status, setStatus] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const load = useCallback(async () => {
    if (!taskId) {
      setState("error");
      setErrorMessage("شناسه وظیفه نامعتبر است.");
      return;
    }
    setState("loading");
    setErrorMessage(null);
    try {
      const data = await getApi().get<FieldTask>(`/api/v1/field/tasks/${taskId}`);
      setTask(data);
      setStatus(str(data.status, ""));
      setNotes(str(data.notes, ""));
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت وظیفه ناموفق بود");
      setState("error");
    }
  }, [taskId]);

  useEffect(() => {
    void load();
  }, [load]);

  const allowedNextStatuses: Record<string, string[]> = {
    ASSIGNED: ["IN_PROGRESS", "FAILED", "CANCELLED"],
    IN_PROGRESS: ["COMPLETED", "FAILED", "CANCELLED"],
    FAILED: ["IN_PROGRESS", "CANCELLED"],
    COMPLETED: [],
    CANCELLED: [],
  };

  async function save() {
    if (!taskId) return;
    setSaving(true);
    setSaveError(null);
    setSaved(false);
    try {
      const body: Record<string, string> = {};
      if (status && status !== str(task?.status, "")) body.status = status;
      if (notes !== str(task?.notes, "")) body.notes = notes;
      if (Object.keys(body).length === 0) {
        setSaved(true);
        setSaving(false);
        return;
      }
      const updated = await getApi().patch<FieldTask>(`/api/v1/field/tasks/${taskId}`, body);
      setTask(updated);
      setStatus(str(updated.status, ""));
      setNotes(str(updated.notes, ""));
      setSaved(true);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "ذخیره وظیفه ناموفق بود");
    } finally {
      setSaving(false);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری وظیفه">
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
        title="دریافت وظیفه ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          جزئیات وظیفه
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">F-02 / F-04</span>
        <Link
          href="/field"
          className="ms-auto text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
        >
          بازگشت به لیست
        </Link>
      </header>

      <section className={cardCls}>
        <div className="flex flex-wrap items-center gap-2">
          <StatusChip tone={taskStatusTone[task?.status ?? ""] ?? "neutral"}>
            {taskStatusLabel[task?.status ?? ""] ?? "وضعیت نامشخص"}
          </StatusChip>
          <span className="text-[13px] text-[var(--pol-light-text-secondary)]" dir="ltr">
            {task?.task_type ? fieldTaskTypeLabel[task.task_type] ?? "نوع وظیفه دیگر" : "—"}
          </span>
          <span className="text-[12px] text-[var(--pol-light-text-muted)]" dir="ltr">
            {task?.id}
          </span>
        </div>

        <dl className="mt-3 grid gap-3 sm:grid-cols-2">
          <div>
            <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">محول‌شده به</dt>
            <dd className="text-[13px] text-[var(--pol-light-text-primary)]" dir="ltr">
              {task?.assigned_to_user_id ?? "—"}
            </dd>
          </div>
          <div>
            <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">سازمان هدف</dt>
            <dd className="text-[13px] text-[var(--pol-light-text-primary)]" dir="ltr">
              {task?.target_organization_id ?? "—"}
            </dd>
          </div>
          <div>
            <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">ایجاد</dt>
            <dd className="text-[13px] text-[var(--pol-light-text-primary)]">
              {formatDateTime(task?.created_at)}
            </dd>
          </div>
          <div>
            <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">مهلت</dt>
            <dd className="text-[13px] text-[var(--pol-light-text-primary)]">
              {formatDateTime(task?.due_date)}
            </dd>
          </div>
          <div>
            <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">تکمیل</dt>
            <dd className="text-[13px] text-[var(--pol-light-text-primary)]">
              {formatDateTime(task?.completed_at)}
            </dd>
          </div>
          <div>
            <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">به‌روزرسانی</dt>
            <dd className="text-[13px] text-[var(--pol-light-text-primary)]">
              {formatDateTime(task?.updated_at)}
            </dd>
          </div>
        </dl>
      </section>

      <section aria-label="ویرایش وضعیت و یادداشت" className={cardCls}>
        <h2 className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
          به‌روزرسانی (F-04)
        </h2>
        <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]">
          PATCH /field/tasks/&#123;id&#125; — status حداکثر ۲۰ نویسه، notes حداکثر ۲۰۰۰ نویسه.
        </p>

        {saveError ? (
          <div className="mt-3">
            <ErrorState title="ذخیره ناموفق بود" description={saveError} />
          </div>
        ) : null}
        {saved ? (
          <p role="status" className="mt-3 text-[13px] text-[var(--pol-light-semantic-success)]">
            تغییرات ذخیره شد.
          </p>
        ) : null}

        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="task-status"
              className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]"
            >
              وضعیت
            </label>
            <select
              id="task-status"
              className={inputCls}
              value={status}
              onChange={(e) => {
                setStatus(e.target.value);
                setSaved(false);
              }}
            >
              <option value="">(بدون تغییر)</option>
              {(task?.status && allowedNextStatuses[task.status] ? allowedNextStatuses[task.status] : []).map((s) => (
                <option key={s} value={s}>
                  {taskStatusLabel[s]}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1.5 sm:col-span-2">
            <label
              htmlFor="task-notes"
              className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]"
            >
              یادداشت
            </label>
            <textarea
              id="task-notes"
              value={notes}
              maxLength={2000}
              rows={4}
              onChange={(e) => {
                setNotes(e.target.value);
                setSaved(false);
              }}
              className={[inputCls, "h-auto min-h-[96px] py-2 resize-y"].join(" ")}
            />
            <p className="text-[11px] text-[var(--pol-light-text-muted)]">
              {notes.length.toLocaleString("fa-IR")}/2000
            </p>
          </div>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          <Button loading={saving} onClick={() => void save()}>
            ذخیره تغییرات
          </Button>
          <Button variant="ghost" disabled={saving} onClick={() => void load()}>
            انصراف
          </Button>
        </div>
      </section>
    </div>
  );
}
