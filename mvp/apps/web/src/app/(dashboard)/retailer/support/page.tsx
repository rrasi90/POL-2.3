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
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری پشتیبانی">
        <Skeleton className="h-9 w-48" />
        <div className="grid gap-4 lg:grid-cols-2">
          <Card className="p-6">
            <Skeleton lines={6} />
          </Card>
          <Card className="p-6">
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] md:text-[26px] font-bold text-[var(--pol-light-text-primary)]">
              مرکز پشتیبانی و تیکت‌ها
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              R-12
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            ارتباط مستقیم با تیم عملیات پُل برای حل مشکلات سفارش و هماهنگی‌ها
          </p>
        </div>
        <Button
          size="sm"
          onClick={() => setCreateOpen((v) => !v)}
          aria-expanded={createOpen}
        >
          {createOpen ? "انصراف و بستن" : "+ ثبت تیکت جدید"}
        </Button>
      </header>

      {/* Create Ticket Modal / Accordion */}
      {createOpen && (
        <Card className="p-5 border-[var(--pol-light-brand-primary)] bg-[var(--pol-light-surface-subtle)] shadow-[var(--pol-shadow-md)]">
          <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
            ثبت پرونده پشتیبانی جدید
          </h2>
          <p className="mt-0.5 text-[12px] text-[var(--pol-light-text-secondary)]">
            اطلاعات مورد نیاز را وارد کنید تا کارشناسان پشتیبانی پُل سریع‌تر پاسخگو باشند.
          </p>

          {createError && (
            <div className="mt-3">
              <ErrorState title="ایجاد پرونده ناموفق بود" description={createError} />
            </div>
          )}

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <Field
              label="موضوع تیکت"
              value={createForm.subject}
              onChange={(e) => setCreateForm((f) => ({ ...f, subject: e.target.value }))}
              placeholder="مثال: مغایرت در تعداد اقلام تحویلی..."
              required
              maxLength={200}
            />
            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="rs-priority"
                className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]"
              >
                میزان اولویت
              </label>
              <select
                id="rs-priority"
                className="h-10 w-full rounded-lg border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 text-[14px] text-[var(--pol-light-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
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
              hint="اختیاری — جهت بررسی سریع‌تر"
              placeholder="مثال: ORD-12345"
              dir="ltr"
            />
          </div>

          <div className="mt-4 flex justify-end gap-2">
            <Button variant="secondary" size="sm" onClick={() => setCreateOpen(false)}>
              انصراف
            </Button>
            <Button size="sm" loading={creating} onClick={() => void createCase()}>
              ثبت و ارسال پرونده
            </Button>
          </div>
        </Card>
      )}

      {/* Split View */}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1.4fr)]">
        {/* Cases List */}
        <section aria-label="فهرست پرونده‌ها" className="space-y-3">
          <SearchField
            label="جستجوی پرونده"
            placeholder="جستجوی موضوع یا شماره تیکت..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />

          {filtered.length === 0 ? (
            <EmptyState
              title="پرونده‌ای یافت نشد"
              description="تیکت جدیدی ثبت کنید یا عبارت جستجو را تغییر دهید."
            />
          ) : (
            <div className="space-y-2.5">
              {filtered.map((c) => {
                const isSelected = selectedId === String(c.id);
                return (
                  <Card
                    key={String(c.id)}
                    onClick={() => setSelectedId(String(c.id))}
                    className={[
                      "cursor-pointer p-4 transition-all duration-150 text-start",
                      isSelected
                        ? "border-[var(--pol-light-brand-primary)] bg-[var(--pol-light-surface-subtle)] ring-1 ring-[var(--pol-light-brand-primary)] shadow-[var(--pol-shadow-sm)]"
                        : "hover:border-[var(--pol-light-border-strong)] hover:bg-[var(--pol-light-surface-subtle)]",
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

                    <p className="mt-2 text-[14px] font-semibold text-[var(--pol-light-text-primary)] line-clamp-1">
                      {c.subject ?? "بدون موضوع"}
                    </p>

                    <div className="mt-1 flex items-center justify-between text-[11px] text-[var(--pol-light-text-muted)]">
                      <span dir="ltr" className="font-mono">
                        {c.case_number ?? `CASE-${String(c.id).slice(0, 8)}`}
                      </span>
                      {c.related_order_id && (
                        <span dir="ltr" className="font-mono">
                          سفارش: {c.related_order_id.slice(0, 8)}...
                        </span>
                      )}
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </section>

        {/* Selected Case Detail */}
        <section aria-label="جزئیات پرونده">
          {!selectedId ? (
            <Card className="flex flex-col items-center justify-center p-12 text-center">
              <span className="text-[36px] mb-2">💬</span>
              <h3 className="text-[15px] font-semibold text-[var(--pol-light-text-primary)]">
                پرونده‌ای انتخاب نشده است
              </h3>
              <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
                یک تیکت را از ستون کناری برای مشاهده جزئیات و گفتگو انتخاب نمایید.
              </p>
            </Card>
          ) : detailState === "loading" ? (
            <Card className="p-6">
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
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--pol-light-border-subtle)] pb-4">
                <div className="flex flex-wrap items-center gap-2">
                  <StatusChip tone={supportStatusTone[detail.status ?? ""] ?? "neutral"}>
                    {supportStatusLabel[detail.status ?? ""] ?? detail.status ?? "—"}
                  </StatusChip>
                  <StatusChip tone={supportPriorityTone[detail.priority ?? ""] ?? "neutral"}>
                    {PRIORITY_LABEL[detail.priority ?? ""] ?? detail.priority ?? "—"}
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
                    کد پیگیری: {detail.case_number ?? String(detail.id)}
                  </span>
                  {detail.related_order_id && (
                    <span dir="ltr" className="font-mono">
                      سفارش مرتبط: {detail.related_order_id}
                    </span>
                  )}
                </div>
                {detail.resolution_note && (
                  <div className="mt-3 rounded-lg border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-3 text-[13px] text-[var(--pol-light-text-secondary)] leading-relaxed">
                    <strong className="block text-[var(--pol-light-text-primary)] mb-1">
                      یادداشت رفع مشکل:
                    </strong>
                    {detail.resolution_note}
                  </div>
                )}
              </div>

              {/* Messages / Discussion */}
              <div className="border-t border-[var(--pol-light-border-subtle)] pt-4 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-[14px] font-bold text-[var(--pol-light-text-primary)]">
                    پیام‌های نشست
                  </h3>
                  <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                    ارسال زنده به تیم عملیات
                  </span>
                </div>

                {sessionMessages.length === 0 ? (
                  <div className="rounded-lg border border-dashed border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-4 text-center text-[12px] text-[var(--pol-light-text-secondary)]">
                    پیام جدیدی در این نشست ثبت نشده است. پاسخ‌های قبلی از طریق پیامک یا بخش وضعیت
                    اطلاع‌رسانی می‌شوند.
                  </div>
                ) : (
                  <div className="space-y-2.5">
                    {sessionMessages.map((m) => (
                      <div
                        key={String(m.id)}
                        className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-3.5 space-y-1"
                      >
                        <p className="text-[13px] leading-relaxed text-[var(--pol-light-text-primary)]">
                          {m.message_text}
                        </p>
                        <div className="flex justify-end text-[10px] text-[var(--pol-light-text-muted)]">
                          {formatDateTime(m.created_at)}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {messageError && (
                  <ErrorState title="ارسال پیام ناموفق بود" description={messageError} />
                )}

                {/* Input box */}
                <div className="space-y-2">
                  <textarea
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    maxLength={5000}
                    rows={3}
                    placeholder="پیام یا توضیحات خود را بنویسید..."
                    className="min-h-[80px] w-full resize-y rounded-xl border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] p-3 text-[14px] text-[var(--pol-light-text-primary)] placeholder:text-[var(--pol-light-text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
                  />
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                      {messageText.length.toLocaleString("fa-IR")} از ۵,۰۰۰ نویسه
                    </span>
                    <Button
                      size="sm"
                      loading={sending}
                      disabled={!messageText.trim()}
                      onClick={() => void sendMessage()}
                    >
                      ارسال پیام
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
