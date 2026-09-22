"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Button,
  EmptyState,
  ErrorState,
  Field,
  SearchField,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  asRecordArray,
  formatDateTime,
  supportPriorityTone,
  supportStatusLabel,
  supportStatusTone,
} from "../shared";

interface CaseRow {
  id: string;
  case_number?: string | null;
  case_type?: string | null;
  subject?: string | null;
  related_order_id?: string | null;
  priority?: string | null;
  status?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  resolution_note?: string | null;
}

interface CaseMessage {
  id: string;
  message_text?: string | null;
  created_at?: string | null;
  sender_role?: string | null;
}

interface CaseDetail extends CaseRow {
  messages?: CaseMessage[];
}

type LoadState = "loading" | "error" | "ready";

const PRIORITY_OPTIONS = ["", "LOW", "NORMAL", "HIGH", "URGENT"] as const;

const PRIORITY_LABEL: Record<string, string> = {
  URGENT: "فوری",
  HIGH: "زیاد",
  NORMAL: "عادی",
  LOW: "کم",
};

/**
 * R-12 retailer support.
 * POST/GET /support/cases, GET /support/cases/{id}, POST messages
 */
export default function RetailerSupportPage() {
  const [cases, setCases] = useState<CaseRow[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<CaseDetail | null>(null);
  const [detailState, setDetailState] = useState<LoadState>("ready");
  const [detailError, setDetailError] = useState<string | null>(null);
  const [sessionMessages, setSessionMessages] = useState<CaseMessage[]>([]);
  const [messageText, setMessageText] = useState("");
  const [messageError, setMessageError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    subject: "",
    case_type: "GENERAL",
    priority: "NORMAL",
    related_order_id: "",
  });
  const [createError, setCreateError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const loadList = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const data = await getApi().get<unknown>("/api/v1/support/cases");
      setCases(asRecordArray(data) as unknown as CaseRow[]);
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت پرونده‌ها ناموفق بود");
      setState("error");
    }
  }, []);

  const loadDetail = useCallback(async (id: string) => {
    setDetailState("loading");
    setDetailError(null);
    setSessionMessages([]);
    setMessageText("");
    setMessageError(null);
    try {
      const data = await getApi().get<CaseDetail>(`/api/v1/support/cases/${id}`);
      setDetail(data);
      setDetailState("ready");
    } catch (err) {
      setDetailError(err instanceof Error ? err.message : "دریافت پرونده ناموفق بود");
      setDetailState("error");
    }
  }, []);

  useEffect(() => {
    void loadList();
  }, [loadList]);

  useEffect(() => {
    if (selectedId) void loadDetail(selectedId);
  }, [selectedId, loadDetail]);

  const filtered = cases.filter((c) => {
    if (!query.trim()) return true;
    const q = query.trim().toLowerCase();
    return (
      (c.subject ?? "").toLowerCase().includes(q) ||
      (c.case_number ?? "").toLowerCase().includes(q) ||
      String(c.id).toLowerCase().includes(q)
    );
  });

  async function sendMessage() {
    if (!selectedId || !messageText.trim()) return;
    setSending(true);
    setMessageError(null);
    try {
      const created = await getApi().post<CaseMessage>(
        `/api/v1/support/cases/${selectedId}/messages`,
        { message_text: messageText.trim() },
      );
      setSessionMessages((prev) => [...prev, created]);
      setMessageText("");
    } catch (err) {
      setMessageError(err instanceof Error ? err.message : "ارسال پیام ناموفق بود");
    } finally {
      setSending(false);
    }
  }

  async function createCase() {
    if (!createForm.subject.trim()) {
      setCreateError("موضوع پرونده الزامی است.");
      return;
    }
    setCreating(true);
    setCreateError(null);
    try {
      const body: Record<string, string> = {
        subject: createForm.subject.trim(),
        case_type: createForm.case_type,
        priority: createForm.priority,
      };
      if (createForm.related_order_id.trim())
        body.related_order_id = createForm.related_order_id.trim();
      const created = await getApi().post<CaseRow>("/api/v1/support/cases", body);
      setCreateOpen(false);
      setCreateForm({
        subject: "",
        case_type: "GENERAL",
        priority: "NORMAL",
        related_order_id: "",
      });
      setCases((prev) => [created, ...prev]);
      setSelectedId(String(created.id));
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : "ایجاد پرونده ناموفق بود");
    } finally {
      setCreating(false);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری پشتیبانی">
        <Skeleton className="h-8 w-48" />
        <div className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4">
          <Skeleton lines={5} />
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت پرونده‌های پشتیبانی ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void loadList()}
      />
    );
  }

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          پشتیبانی
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">R-12</span>
        <Button
          size="sm"
          className="ms-auto"
          onClick={() => setCreateOpen((v) => !v)}
          aria-expanded={createOpen}
        >
          {createOpen ? "بستن فرم" : "پرونده جدید"}
        </Button>
      </header>

      {createOpen ? (
        <section
          aria-label="ایجاد پرونده"
          className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
        >
          <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
            پرونده جدید
          </h2>
          {createError ? (
            <div className="mt-3">
              <ErrorState title="ایجاد پرونده ناموفق بود" description={createError} />
            </div>
          ) : null}
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            <Field
              label="موضوع"
              value={createForm.subject}
              onChange={(e) => setCreateForm((f) => ({ ...f, subject: e.target.value }))}
              required
              maxLength={200}
            />
            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="rs-priority"
                className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]"
              >
                اولویت
              </label>
              <select
                id="rs-priority"
                className="h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 text-[14px] text-[var(--pol-light-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
                value={createForm.priority}
                onChange={(e) => setCreateForm((f) => ({ ...f, priority: e.target.value }))}
              >
                {PRIORITY_OPTIONS.filter(Boolean).map((p) => (
                  <option key={p} value={p}>
                    {PRIORITY_LABEL[p] ?? p}
                  </option>
                ))}
              </select>
            </div>
            <Field
              label="شناسه سفارش مرتبط"
              value={createForm.related_order_id}
              onChange={(e) =>
                setCreateForm((f) => ({ ...f, related_order_id: e.target.value }))
              }
              hint="اختیاری"
              dir="ltr"
            />
          </div>
          <div className="mt-3">
            <Button loading={creating} onClick={() => void createCase()}>
              ایجاد پرونده
            </Button>
          </div>
        </section>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
        <section aria-label="فهرست پرونده‌ها" className="space-y-3">
          <SearchField
            label="جستجوی پرونده"
            placeholder="جستجوی موضوع یا شماره…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          {filtered.length === 0 ? (
            <EmptyState
              title="پرونده‌ای یافت نشد"
              description="پرونده جدید بسازید یا عبارت جستجو را تغییر دهید."
            />
          ) : (
            <ul role="list" className="space-y-2">
              {filtered.map((c) => (
                <li key={String(c.id)}>
                  <button
                    type="button"
                    onClick={() => setSelectedId(String(c.id))}
                    className={[
                      "w-full rounded-[12px] border p-3 text-start transition-colors duration-[160ms]",
                      selectedId === String(c.id)
                        ? "border-[var(--pol-light-brand-primary)] bg-[var(--pol-light-surface-subtle)]"
                        : "border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] hover:bg-[var(--pol-light-surface-subtle)]",
                    ].join(" ")}
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <StatusChip tone={supportStatusTone[c.status ?? ""] ?? "neutral"}>
                        {supportStatusLabel[c.status ?? ""] ?? c.status ?? "—"}
                      </StatusChip>
                      <StatusChip tone={supportPriorityTone[c.priority ?? ""] ?? "neutral"}>
                        {PRIORITY_LABEL[c.priority ?? ""] ?? c.priority ?? "—"}
                      </StatusChip>
                      <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                        {formatDateTime(c.created_at)}
                      </span>
                    </div>
                    <p className="mt-1.5 text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
                      {c.subject ?? "بدون موضوع"}
                    </p>
                    <p className="text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                      {c.case_number ?? String(c.id)}
                    </p>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section
          aria-label="جزئیات پرونده"
          className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4"
        >
          {!selectedId ? (
            <EmptyState
              title="پرونده‌ای انتخاب نشده"
              description="از فهرست کنار، یک پرونده انتخاب کنید."
            />
          ) : detailState === "loading" ? (
            <div aria-busy="true" aria-label="در حال بارگذاری جزئیات">
              <Skeleton lines={5} />
            </div>
          ) : detailState === "error" ? (
            <ErrorState
              title="دریافت جزئیات پرونده ناموفق بود"
              description={detailError ?? undefined}
              onRetry={() => selectedId && void loadDetail(selectedId)}
            />
          ) : detail ? (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center gap-2">
                <StatusChip tone={supportStatusTone[detail.status ?? ""] ?? "neutral"}>
                  {supportStatusLabel[detail.status ?? ""] ?? detail.status ?? "—"}
                </StatusChip>
                <StatusChip tone={supportPriorityTone[detail.priority ?? ""] ?? "neutral"}>
                  {PRIORITY_LABEL[detail.priority ?? ""] ?? detail.priority ?? "—"}
                </StatusChip>
                <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                  {formatDateTime(detail.updated_at)}
                </span>
              </div>
              <div>
                <h2 className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
                  {detail.subject ?? "بدون موضوع"}
                </h2>
                <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                  {detail.case_number ?? String(detail.id)}
                </p>
                {detail.related_order_id ? (
                  <p className="mt-2 text-[13px] text-[var(--pol-light-text-secondary)]" dir="ltr">
                    order: {detail.related_order_id}
                  </p>
                ) : null}
                {detail.resolution_note ? (
                  <p className="mt-2 text-[13px] text-[var(--pol-light-text-secondary)]">
                    {detail.resolution_note}
                  </p>
                ) : null}
              </div>

              <div className="border-t border-[var(--pol-light-border-subtle)] pt-3">
                <h3 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
                  مکالمه
                </h3>
                <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
                  GET messages در بک‌اند وجود ندارد — فقط پیام‌های این نشست نمایش داده می‌شود.
                </p>
                {sessionMessages.length === 0 ? (
                  <p className="mt-2 text-[13px] text-[var(--pol-light-text-secondary)]">
                    پیامی در این نشست ثبت نشده است.
                  </p>
                ) : (
                  <ul role="list" className="mt-2 space-y-2">
                    {sessionMessages.map((m) => (
                      <li
                        key={String(m.id)}
                        className="rounded-[8px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-3"
                      >
                        <p className="text-[13px] text-[var(--pol-light-text-primary)]">
                          {m.message_text}
                        </p>
                        <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
                          {formatDateTime(m.created_at)}
                        </p>
                      </li>
                    ))}
                  </ul>
                )}
                {messageError ? (
                  <div className="mt-2">
                    <ErrorState title="ارسال پیام ناموفق بود" description={messageError} />
                  </div>
                ) : null}
                <div className="mt-2 flex flex-col gap-2">
                  <textarea
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    maxLength={5000}
                    rows={3}
                    placeholder="متن پیام (حداکثر ۵۰۰۰ نویسه)…"
                    className="min-h-[72px] w-full resize-y rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-2 text-[14px] text-[var(--pol-light-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
                  />
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      loading={sending}
                      disabled={!messageText.trim()}
                      onClick={() => void sendMessage()}
                    >
                      ارسال پیام
                    </Button>
                    <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                      {messageText.length.toLocaleString("fa-IR")}/5000
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ) : null}
        </section>
      </div>
    </div>
  );
}
