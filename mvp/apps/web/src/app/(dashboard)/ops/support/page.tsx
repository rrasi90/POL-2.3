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
  ageLabel,
  ageTone,
  cardCls,
  formatDateTime,
  idOf,
  inputCls,
  itemsOf,
  str,
  supportPriorityLabel,
  supportPriorityTone,
  supportStatusLabel,
  supportStatusTone,
  supportTransitions,
  supportTypeLabel,
  type LoadState,
} from "../_shared";

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
  resolution_code?: string | null;
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

const TYPE_OPTIONS = [
  "",
  "GENERAL",
  "ORDER_INQUIRY",
  "PAYMENT_ASSISTANCE",
  "DELIVERY_DELAY",
  "ACCOUNT_ISSUE",
  "CATALOG_SUGGESTION",
  "INVOICE_INQUIRY",
] as const;

const PRIORITY_OPTIONS = ["", "LOW", "NORMAL", "HIGH", "URGENT"] as const;

export default function OpsSupportPage() {
  const [cases, setCases] = useState<CaseRow[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<CaseDetail | null>(null);
  const [detailState, setDetailState] = useState<LoadState>("ready");
  const [detailError, setDetailError] = useState<string | null>(null);
  const [sessionMessages, setSessionMessages] = useState<CaseMessage[]>([]);
  const [messageText, setMessageText] = useState("");
  const [messageError, setMessageError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [transitionTo, setTransitionTo] = useState("");
  const [transitionNote, setTransitionNote] = useState("");
  const [transitioning, setTransitioning] = useState(false);
  const [transitionError, setTransitionError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    subject: "",
    case_type: "GENERAL",
    priority: "NORMAL",
    related_order_id: "",
  });
  const [createError, setCreateError] = useState<string | null>(null);

  const loadList = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const data = await getApi().get<unknown>("/api/v1/support/cases");
      setCases(itemsOf<CaseRow>(data, "cases"));
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
    setTransitionTo("");
    setTransitionNote("");
    setTransitionError(null);
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
    if (typeFilter && c.case_type !== typeFilter) return false;
    if (!query.trim()) return true;
    const q = query.trim().toLowerCase();
    return (
      str(c.subject, "").toLowerCase().includes(q) ||
      str(c.case_number, "").toLowerCase().includes(q) ||
      str(c.id, "").toLowerCase().includes(q)
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

  async function transition() {
    if (!selectedId || !transitionTo) return;
    setTransitioning(true);
    setTransitionError(null);
    try {
      const body: Record<string, string> = { target_status: transitionTo };
      if (transitionNote.trim()) body.resolution_note = transitionNote.trim();
      const updated = await getApi().patch<CaseDetail>(
        `/api/v1/support/cases/${selectedId}`,
        body,
      );
      setDetail(updated);
      setTransitionTo("");
      setTransitionNote("");
      await loadList();
    } catch (err) {
      setTransitionError(err instanceof Error ? err.message : "تغییر وضعیت ناموفق بود");
    } finally {
      setTransitioning(false);
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
      setCreateForm({ subject: "", case_type: "GENERAL", priority: "NORMAL", related_order_id: "" });
      setCases((prev) => [created, ...prev]);
      setSelectedId(idOf(created));
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
        <div className={cardCls}>
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

  const currentStatus = str(detail?.status, "");
  const nextStatuses = supportTransitions[currentStatus] ?? [];

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          میز پشتیبانی
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">O-05</span>
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
        <section aria-label="ایجاد پرونده" className={cardCls}>
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
                htmlFor="support-type"
                className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]"
              >
                نوع
              </label>
              <select
                id="support-type"
                className={inputCls}
                value={createForm.case_type}
                onChange={(e) => setCreateForm((f) => ({ ...f, case_type: e.target.value }))}
              >
                {TYPE_OPTIONS.filter(Boolean).map((t) => (
                  <option key={t} value={t}>
                    {supportTypeLabel[t] ?? t}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="support-priority"
                className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]"
              >
                اولویت
              </label>
              <select
                id="support-priority"
                className={inputCls}
                value={createForm.priority}
                onChange={(e) => setCreateForm((f) => ({ ...f, priority: e.target.value }))}
              >
                {PRIORITY_OPTIONS.filter(Boolean).map((p) => (
                  <option key={p} value={p}>
                    {supportPriorityLabel[p] ?? p}
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
          <div className="grid gap-2 sm:grid-cols-[1fr_auto]">
            <SearchField
              label="جستجوی پرونده"
              placeholder="جستجوی موضوع یا شماره…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <select
              aria-label="فیلتر نوع"
              className={inputCls}
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="">همه انواع</option>
              {TYPE_OPTIONS.filter(Boolean).map((t) => (
                <option key={t} value={t}>
                  {supportTypeLabel[t] ?? t}
                </option>
              ))}
            </select>
          </div>

          {filtered.length === 0 ? (
            <EmptyState
              title="پرونده‌ای یافت نشد"
              description="فیلترها را تغییر دهید یا پرونده جدید بسازید."
            />
          ) : (
            <ul role="list" className="space-y-2">
              {filtered.map((c) => (
                <li key={str(c.id)}>
                  <button
                    type="button"
                    onClick={() => setSelectedId(str(c.id))}
                    className={[
                      "w-full rounded-[12px] border p-3 text-start transition-colors duration-[160ms]",
                      selectedId === str(c.id)
                        ? "border-[var(--pol-light-brand-primary)] bg-[var(--pol-light-surface-subtle)]"
                        : "border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] hover:bg-[var(--pol-light-surface-subtle)]",
                    ].join(" ")}
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <StatusChip tone={supportStatusTone[c.status ?? ""] ?? "neutral"}>
                        {supportStatusLabel[c.status ?? ""] ?? c.status ?? "—"}
                      </StatusChip>
                      <StatusChip tone={supportPriorityTone[c.priority ?? ""] ?? "neutral"}>
                        {supportPriorityLabel[c.priority ?? ""] ?? c.priority ?? "—"}
                      </StatusChip>
                      <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                        {ageLabel(c.created_at)}
                      </span>
                    </div>
                    <p className="mt-1.5 text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
                      {c.subject ?? "بدون موضوع"}
                    </p>
                    <p className="text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                      {c.case_number ?? str(c.id)}
                    </p>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section aria-label="جزئیات پرونده" className={cardCls}>
          {!selectedId ? (
            <EmptyState
              title="پرونده‌ای انتخاب نشده"
              description="از فهرست کنار، یک پرونده انتخاب کنید تا جزئیات آن نمایش داده شود."
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
                  {supportPriorityLabel[detail.priority ?? ""] ?? detail.priority ?? "—"}
                </StatusChip>
                <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
                  {supportTypeLabel[str(detail.case_type)] ?? detail.case_type ?? "—"}
                </span>
                <StatusChip tone={ageTone(detail.updated_at, 48, 168)}>
                  {ageLabel(detail.updated_at)}
                </StatusChip>
              </div>

              <div>
                <h2 className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
                  {detail.subject ?? "بدون موضوع"}
                </h2>
                <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                  {detail.case_number ?? str(detail.id)}
                </p>
                <dl className="mt-3 grid gap-3 sm:grid-cols-2">
                  <div>
                    <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
                      ایجاد
                    </dt>
                    <dd className="text-[13px] text-[var(--pol-light-text-primary)]">
                      {formatDateTime(detail.created_at)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
                      سفارش مرتبط
                    </dt>
                    <dd className="text-[13px] text-[var(--pol-light-text-primary)]" dir="ltr">
                      {detail.related_order_id ?? "—"}
                    </dd>
                  </div>
                  {detail.resolution_code ? (
                    <div>
                      <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
                        کد حل
                      </dt>
                      <dd className="text-[13px] text-[var(--pol-light-text-primary)]" dir="ltr">
                        {detail.resolution_code}
                      </dd>
                    </div>
                  ) : null}
                  {detail.resolution_note ? (
                    <div className="sm:col-span-2">
                      <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
                        یادداشت حل
                      </dt>
                      <dd className="text-[13px] text-[var(--pol-light-text-primary)]">
                        {detail.resolution_note}
                      </dd>
                    </div>
                  ) : null}
                </dl>
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
                        key={str(m.id)}
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
                    className={[inputCls, "h-auto min-h-[72px] py-2 resize-y"].join(" ")}
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

              <div className="border-t border-[var(--pol-light-border-subtle)] pt-3">
                <h3 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
                  تغییر وضعیت
                </h3>
                {nextStatuses.length === 0 ? (
                  <p className="mt-2 text-[13px] text-[var(--pol-light-text-secondary)]">
                    وضعیت بسته — انتقال مجازی وجود ندارد (سرور مرجع است).
                  </p>
                ) : (
                  <div className="mt-2 space-y-2">
                    {transitionError ? (
                      <ErrorState
                        title="تغییر وضعیت ناموفق بود"
                        description={transitionError}
                      />
                    ) : null}
                    <div className="flex flex-wrap gap-2">
                      {nextStatuses.map((s) => (
                        <button
                          key={s}
                          type="button"
                          onClick={() => setTransitionTo(s)}
                          className={[
                            "rounded-[8px] border px-3 py-1.5 text-[12px] transition-colors duration-[160ms]",
                            transitionTo === s
                              ? "border-[var(--pol-light-brand-primary)] bg-[var(--pol-light-surface-subtle)] font-semibold"
                              : "border-[var(--pol-light-border-strong)] text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)]",
                          ].join(" ")}
                        >
                          {supportStatusLabel[s] ?? s}
                        </button>
                      ))}
                    </div>
                    <textarea
                      value={transitionNote}
                      onChange={(e) => setTransitionNote(e.target.value)}
                      rows={2}
                      maxLength={2000}
                      placeholder="یادداشت حل (اختیاری)…"
                      className={[inputCls, "h-auto min-h-[56px] py-2 resize-y"].join(" ")}
                    />
                    <Button
                      size="sm"
                      variant="secondary"
                      loading={transitioning}
                      disabled={!transitionTo}
                      onClick={() => void transition()}
                    >
                      اعمال وضعیت
                    </Button>
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </section>
      </div>
    </div>
  );
}
