"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Button,
  Card,
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
  formatDateTime,
  inputCls,
  itemsOf,
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
      (c.subject ?? "").toLowerCase().includes(q) ||
      (c.case_number ?? "").toLowerCase().includes(q) ||
      String(c.id).toLowerCase().includes(q) ||
      (c.related_order_id ?? "").toLowerCase().includes(q)
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

  async function changeStatus() {
    if (!selectedId || !transitionTo) return;
    setTransitioning(true);
    setTransitionError(null);
    try {
      const body: Record<string, string> = { status: transitionTo };
      if (transitionNote.trim()) body.resolution_note = transitionNote.trim();
      await getApi().patch(`/api/v1/support/cases/${selectedId}/status`, body);
      await loadDetail(selectedId);
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
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری میز پشتیبانی">
        <Skeleton className="h-9 w-48" />
        <div className="grid gap-4 lg:grid-cols-2">
          <Card className="p-5">
            <Skeleton lines={6} />
          </Card>
          <Card className="p-5">
            <Skeleton lines={6} />
          </Card>
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

  const allowedTransitions = detail?.status ? supportTransitions[detail.status] ?? [] : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-[var(--pol-light-border-subtle)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[20px] md:text-[24px] font-bold text-[var(--pol-light-text-primary)]">
              میز عملیات پشتیبانی
            </h1>
            <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-bold text-[var(--pol-light-text-secondary)]">
              O-03 · Triage Desk
            </span>
          </div>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
            رسیدگی به تیکت‌های کاربران، تغییر وضعیت پرونده‌ها و ارسال پاسخ‌های رسمی
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            onClick={() => setCreateOpen((v) => !v)}
            aria-expanded={createOpen}
          >
            {createOpen ? "بستن فرم" : "+ پرونده جدید"}
          </Button>
          <Button variant="secondary" size="sm" onClick={() => void loadList()}>
            به‌روزرسانی
          </Button>
        </div>
      </header>

      {/* New Case Creation Form */}
      {createOpen && (
        <Card className="p-5 border-[var(--pol-light-brand-primary)] bg-[var(--pol-light-surface-subtle)]">
          <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
            ثبت پرونده پشتیبانی جدید
          </h2>
          {createError && (
            <div className="mt-3">
              <ErrorState title="ایجاد پرونده ناموفق بود" description={createError} />
            </div>
          )}
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <Field
              label="موضوع پرونده"
              value={createForm.subject}
              onChange={(e) => setCreateForm((f) => ({ ...f, subject: e.target.value }))}
              placeholder="شرح کوتاه مسئله..."
              required
              maxLength={200}
            />
            <div className="flex flex-col gap-1.5">
              <label htmlFor="ops-priority" className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
                اولویت
              </label>
              <select
                id="ops-priority"
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
            <div className="flex flex-col gap-1.5">
              <label htmlFor="ops-type" className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
                دسته‌بندی موضوعی
              </label>
              <select
                id="ops-type"
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

          <div className="mt-4 flex justify-end gap-2">
            <Button variant="secondary" size="sm" onClick={() => setCreateOpen(false)}>
              انصراف
            </Button>
            <Button size="sm" loading={creating} onClick={() => void createCase()}>
              ایجاد پرونده
            </Button>
          </div>
        </Card>
      )}

      {/* Split Triage View */}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1.4fr)]">
        {/* Cases List Pane */}
        <section aria-label="فهرست پرونده‌ها" className="space-y-3">
          <div className="grid gap-2 sm:grid-cols-2">
            <SearchField
              label="جستجو"
              placeholder="موضوع، شماره یا سفارش..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <div className="flex flex-col gap-1.5">
              <label htmlFor="type-filter" className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
                دسته‌بندی موضوعی
              </label>
              <select
                id="type-filter"
                className={inputCls}
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
              >
                <option value="">همه دسته‌بندی‌ها</option>
                {TYPE_OPTIONS.filter(Boolean).map((t) => (
                  <option key={t} value={t}>
                    {supportTypeLabel[t] ?? t}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {filtered.length === 0 ? (
            <EmptyState
              title="پرونده‌ای یافت نشد"
              description="فیلترها را تغییر دهید یا پرونده جدید ایجاد نمایید."
            />
          ) : (
            <div className="space-y-2">
              {filtered.map((c) => {
                const isSelected = selectedId === String(c.id);
                return (
                  <Card
                    key={String(c.id)}
                    onClick={() => setSelectedId(String(c.id))}
                    className={[
                      "cursor-pointer p-3.5 transition-all duration-150 text-start",
                      isSelected
                        ? "border-[var(--pol-light-brand-primary)] bg-[var(--pol-light-surface-subtle)] ring-1 ring-[var(--pol-light-brand-primary)]"
                        : "hover:border-[var(--pol-light-border-strong)] hover:bg-[var(--pol-light-surface-subtle)]",
                    ].join(" ")}
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <StatusChip tone={supportStatusTone[c.status ?? ""] ?? "neutral"}>
                        {supportStatusLabel[c.status ?? ""] ?? "وضعیت نامشخص"}
                      </StatusChip>
                      <StatusChip tone={supportPriorityTone[c.priority ?? ""] ?? "neutral"}>
                        {supportPriorityLabel[c.priority ?? ""] ?? c.priority ?? "—"}
                      </StatusChip>
                      <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                        {ageLabel(c.created_at)}
                      </span>
                    </div>

                    <p className="mt-2 text-[14px] font-semibold text-[var(--pol-light-text-primary)] line-clamp-1">
                      {c.subject ?? "بدون موضوع"}
                    </p>

                    <div className="mt-1 flex items-center justify-between text-[11px] text-[var(--pol-light-text-muted)]">
                      <span dir="ltr" className="font-mono">
                        {c.case_number ?? String(c.id).slice(0, 8)}
                      </span>
                      {c.case_type && (
                        <span>{supportTypeLabel[c.case_type] ?? c.case_type}</span>
                      )}
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </section>

        {/* Selected Case Triage & Action Pane */}
        <section aria-label="رسیدگی به پرونده">
          {!selectedId ? (
            <Card className="flex flex-col items-center justify-center p-12 text-center">
              <span className="text-[32px] mb-2">📋</span>
              <h3 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                پرونده‌ای انتخاب نشده است
              </h3>
              <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
                یک تیکت را برای مشاهده جزئیات، تغییر وضعیت و پاسخگویی انتخاب فرمایید.
              </p>
            </Card>
          ) : detailState === "loading" ? (
            <Card className="p-5">
              <Skeleton lines={6} />
            </Card>
          ) : detailState === "error" ? (
            <ErrorState
              title="دریافت جزئیات پرونده ناموفق بود"
              description={detailError ?? undefined}
              onRetry={() => selectedId && void loadDetail(selectedId)}
            />
          ) : detail ? (
            <Card className="p-5 space-y-5">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--pol-light-border-subtle)] pb-3">
                <div className="flex flex-wrap items-center gap-2">
                  <StatusChip tone={supportStatusTone[detail.status ?? ""] ?? "neutral"}>
                    {supportStatusLabel[detail.status ?? ""] ?? "وضعیت نامشخص"}
                  </StatusChip>
                  <StatusChip tone={supportPriorityTone[detail.priority ?? ""] ?? "neutral"}>
                    {supportPriorityLabel[detail.priority ?? ""] ?? detail.priority ?? "—"}
                  </StatusChip>
                </div>
                <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                  به‌روزرسانی: {formatDateTime(detail.updated_at)}
                </span>
              </div>

              <div>
                <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
                  {detail.subject ?? "بدون موضوع"}
                </h2>
                <div className="mt-2 flex flex-wrap gap-4 text-[12px] text-[var(--pol-light-text-secondary)]">
                  <span dir="ltr" className="font-mono">
                    شماره پرونده: {detail.case_number ?? detail.id}
                  </span>
                  {detail.related_order_id && (
                    <span dir="ltr" className="font-mono">
                      سفارش: {detail.related_order_id}
                    </span>
                  )}
                </div>
              </div>

              {/* Status Transition Control */}
              {allowedTransitions.length > 0 && (
                <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-4 space-y-3">
                  <h3 className="text-[13px] font-bold text-[var(--pol-light-text-primary)]">
                    تغییر وضعیت پرونده
                  </h3>
                  {transitionError && (
                    <ErrorState title="تغییر وضعیت ناموفق بود" description={transitionError} />
                  )}
                  <div className="grid gap-3 sm:grid-cols-[minmax(0,1.2fr)_minmax(0,2fr)_auto]">
                    <select
                      className={inputCls}
                      value={transitionTo}
                      onChange={(e) => setTransitionTo(e.target.value)}
                    >
                      <option value="">انتخاب وضعیت جدید...</option>
                      {allowedTransitions.map((t) => (
                        <option key={t} value={t}>
                          {supportStatusLabel[t] ?? "وضعیت نامشخص"}
                        </option>
                      ))}
                    </select>
                    <Field
                      label="یادداشت رفع یا تغییر (اختیاری)"
                      value={transitionNote}
                      onChange={(e) => setTransitionNote(e.target.value)}
                      placeholder="علت یا اقدام انجام‌شده..."
                    />
                    <div className="flex items-end">
                      <Button
                        size="sm"
                        disabled={!transitionTo || transitioning}
                        loading={transitioning}
                        onClick={() => void changeStatus()}
                      >
                        ثبت تغییر وضعیت
                      </Button>
                    </div>
                  </div>
                </div>
              )}

              {/* Session Messages Discussion */}
              <div className="border-t border-[var(--pol-light-border-subtle)] pt-4 space-y-4">
                <h3 className="text-[14px] font-bold text-[var(--pol-light-text-primary)]">
                  پیام‌های نشست عملیاتی
                </h3>

                {sessionMessages.length === 0 ? (
                  <p className="text-[12px] text-[var(--pol-light-text-muted)]">
                    پیامی در این نشست ثبت نشده است. پاسخ جدید به کاربر را وارد نمایید.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {sessionMessages.map((m) => (
                      <div
                        key={String(m.id)}
                        className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-3 text-[13px]"
                      >
                        <p className="text-[var(--pol-light-text-primary)]">{m.message_text}</p>
                        <span className="mt-1 block text-end text-[10px] text-[var(--pol-light-text-muted)]">
                          {formatDateTime(m.created_at)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {messageError && (
                  <ErrorState title="ارسال پیام ناموفق بود" description={messageError} />
                )}

                <div className="space-y-2">
                  <textarea
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    maxLength={5000}
                    rows={3}
                    placeholder="متن پیام رسمی پشتیبانی به کاربر..."
                    className="min-h-[72px] w-full resize-y rounded-xl border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] p-3 text-[14px] text-[var(--pol-light-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
                  />
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                      {messageText.length.toLocaleString("fa-IR")}/5000
                    </span>
                    <Button
                      size="sm"
                      loading={sending}
                      disabled={!messageText.trim()}
                      onClick={() => void sendMessage()}
                    >
                      ارسال پاسخ رسمی
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ) : null}
        </section>
      </div>
    </div>
  );
}
