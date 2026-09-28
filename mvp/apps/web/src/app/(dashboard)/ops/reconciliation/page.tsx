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
  formatToman,
  inputCls,
  itemsOf,
  reconStatusLabel,
  reconStatusTone,
  str,
  type LoadState,
} from "../_shared";

interface ReconCase {
  id: string;
  payment_id?: string | null;
  status?: string | null;
  expected_amount_toman?: number | string | null;
  observed_amount_toman?: number | string | null;
  external_reference?: string | null;
  resolution_reason?: string | null;
  opened_at?: string | null;
  resolved_at?: string | null;
  attempt_count?: number | null;
}

const STATUS_OPTIONS = [
  "",
  "OPEN",
  "MATCHED",
  "PARTIALLY_MATCHED",
  "MISMATCH",
  "RESOLVED",
  "CANCELLED",
] as const;

export default function OpsReconciliationPage() {
  const [items, setItems] = useState<ReconCase[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ReconCase | null>(null);
  const [detailState, setDetailState] = useState<LoadState>("ready");
  const [detailError, setDetailError] = useState<string | null>(null);
  const [resolveNote, setResolveNote] = useState("");
  const [resolving, setResolving] = useState(false);
  const [resolveError, setResolveError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const qs = new URLSearchParams({ limit: "50", offset: "0" });
      if (statusFilter) qs.set("status", statusFilter);
      const data = await getApi().get<unknown>(`/api/v1/finance/reconciliation?${qs}`);
      setItems(itemsOf<ReconCase>(data, "cases"));
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت تطبیق ناموفق بود");
      setState("error");
    }
  }, [statusFilter]);

  const loadDetail = useCallback(async (id: string) => {
    setDetailState("loading");
    setDetailError(null);
    setResolveNote("");
    setResolveError(null);
    try {
      const data = await getApi().get<ReconCase>(`/api/v1/finance/reconciliation/${id}`);
      setDetail(data);
      setDetailState("ready");
    } catch (err) {
      setDetailError(err instanceof Error ? err.message : "دریافت جزئیات ناموفق بود");
      setDetailState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (selectedId) void loadDetail(selectedId);
  }, [selectedId, loadDetail]);

  const filtered = items.filter((it) => {
    if (!query.trim()) return true;
    const q = query.trim().toLowerCase();
    return (
      str(it.id).toLowerCase().includes(q) ||
      str(it.payment_id).toLowerCase().includes(q) ||
      str(it.external_reference).toLowerCase().includes(q)
    );
  });

  async function resolveCase() {
    if (!selectedId) return;
    setResolving(true);
    setResolveError(null);
    try {
      await getApi().post(`/api/v1/finance/reconciliation/${selectedId}/resolve`, {
        resolution_reason: resolveNote.trim() || undefined,
      });
      await loadDetail(selectedId);
      await load();
    } catch (err) {
      setResolveError(err instanceof Error ? err.message : "حل مغایرت ناموفق بود");
    } finally {
      setResolving(false);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری تطبیق مالی">
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
        title="دریافت مغایرت‌های مالی ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-[var(--pol-light-border-subtle)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[20px] md:text-[24px] font-bold text-[var(--pol-light-text-primary)]">
              کنسول انطباق و تطبیق مالی
            </h1>
            <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-bold text-[var(--pol-light-text-secondary)]">
              O-05 · Reconciliation
            </span>
          </div>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
            بررسی مغایرت‌های واریزی درگاه پرداخت، مقادیر انتظاری و دستور تسویه حساب
          </p>
        </div>

        <Button variant="secondary" size="sm" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      {/* Split View */}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1.4fr)]">
        {/* Cases List */}
        <section aria-label="فهرست مغایرت‌ها" className="space-y-3">
          <div className="grid gap-2 sm:grid-cols-2">
            <SearchField
              label="جستجو"
              placeholder="شناسه، پرداخت، مرجع..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <div className="flex flex-col gap-1.5">
              <label htmlFor="recon-status" className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
                وضعیت مغایرت
              </label>
              <select
                id="recon-status"
                className={inputCls}
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="">همه وضعیت‌ها</option>
                {STATUS_OPTIONS.filter(Boolean).map((s) => (
                  <option key={s} value={s}>
                    {reconStatusLabel[s] ?? s}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {filtered.length === 0 ? (
            <EmptyState
              title="موردی یافت نشد"
              description="مغایرت مالی بازی با این مشخصات در سیستم ثبت نشده است."
            />
          ) : (
            <div className="space-y-2">
              {filtered.map((item) => {
                const isSelected = selectedId === item.id;
                return (
                  <Card
                    key={item.id}
                    onClick={() => setSelectedId(item.id)}
                    className={[
                      "cursor-pointer p-3.5 transition-all duration-150 text-start",
                      isSelected
                        ? "border-[var(--pol-light-brand-primary)] bg-[var(--pol-light-surface-subtle)] ring-1 ring-[var(--pol-light-brand-primary)]"
                        : "hover:border-[var(--pol-light-border-strong)] hover:bg-[var(--pol-light-surface-subtle)]",
                    ].join(" ")}
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <StatusChip tone={reconStatusTone[item.status ?? ""] ?? "neutral"}>
                        {reconStatusLabel[item.status ?? ""] ?? item.status ?? "—"}
                      </StatusChip>
                      <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                        {ageLabel(item.opened_at)}
                      </span>
                    </div>

                    <div className="mt-2 flex flex-wrap items-center justify-between text-[12px] text-[var(--pol-light-text-secondary)]">
                      <span>
                        انتظار: <strong>{formatToman(item.expected_amount_toman)}</strong>
                      </span>
                      <span>
                        مشاهده: <strong>{formatToman(item.observed_amount_toman)}</strong>
                      </span>
                    </div>

                    <div className="mt-2 flex items-center justify-between text-[11px] text-[var(--pol-light-text-muted)] border-t border-[var(--pol-light-border-subtle)] pt-2">
                      <span dir="ltr" className="font-mono">
                        ID: {item.id.slice(0, 8)}...
                      </span>
                      {item.payment_id && (
                        <span dir="ltr" className="font-mono">
                          پرداخت: {item.payment_id.slice(0, 8)}...
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
        <section aria-label="جزئیات پرونده مغایرت">
          {!selectedId ? (
            <Card className="flex flex-col items-center justify-center p-12 text-center">
              <span className="text-[32px] mb-2">⚖️</span>
              <h3 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                موردی انتخاب نشده است
              </h3>
              <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
                یک ردیف مغایرت را از ستون کناری جهت بررسی تفصیلی و رفع مغایرت انتخاب کنید.
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
                <StatusChip tone={reconStatusTone[detail.status ?? ""] ?? "neutral"}>
                  {reconStatusLabel[detail.status ?? ""] ?? detail.status ?? "—"}
                </StatusChip>
                <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                  زمان ثبت: {formatDateTime(detail.opened_at)}
                </span>
              </div>

              {/* Amounts Comparison */}
              <div className="grid gap-3 sm:grid-cols-2 rounded-xl bg-[var(--pol-light-surface-subtle)] p-4 border border-[var(--pol-light-border-subtle)]">
                <div>
                  <span className="block text-[11px] text-[var(--pol-light-text-secondary)]">
                    مبلغ انتظاری پُل
                  </span>
                  <span className="text-[18px] font-bold text-[var(--pol-light-text-primary)]">
                    {formatToman(detail.expected_amount_toman)}
                  </span>
                </div>
                <div>
                  <span className="block text-[11px] text-[var(--pol-light-text-secondary)]">
                    مبلغ مشاهده‌شده بانکی
                  </span>
                  <span className="text-[18px] font-bold text-[var(--pol-light-text-primary)]">
                    {formatToman(detail.observed_amount_toman)}
                  </span>
                </div>
              </div>

              {/* Metadata */}
              <div className="space-y-2 text-[12px] text-[var(--pol-light-text-secondary)]">
                <div className="flex justify-between">
                  <span>شناسه پرونده:</span>
                  <span dir="ltr" className="font-mono text-[var(--pol-light-text-primary)]">
                    {detail.id}
                  </span>
                </div>
                {detail.payment_id && (
                  <div className="flex justify-between">
                    <span>شناسه پرداخت:</span>
                    <span dir="ltr" className="font-mono text-[var(--pol-light-text-primary)]">
                      {detail.payment_id}
                    </span>
                  </div>
                )}
                {detail.external_reference && (
                  <div className="flex justify-between">
                    <span>کد پیگیری شاپرک / سداد:</span>
                    <span dir="ltr" className="font-mono text-[var(--pol-light-text-primary)]">
                      {detail.external_reference}
                    </span>
                  </div>
                )}
                {detail.attempt_count != null && (
                  <div className="flex justify-between">
                    <span>تعداد تلاش‌های تطبیق:</span>
                    <span className="text-[var(--pol-light-text-primary)]">
                      {detail.attempt_count.toLocaleString("fa-IR")}
                    </span>
                  </div>
                )}
                {detail.resolution_reason && (
                  <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/30 p-3 text-emerald-800 dark:text-emerald-300">
                    <strong>علت رفع مغایرت:</strong> {detail.resolution_reason}
                  </div>
                )}
              </div>

              {/* Resolve Case Section */}
              {detail.status !== "RESOLVED" && detail.status !== "CANCELLED" && (
                <div className="border-t border-[var(--pol-light-border-subtle)] pt-4 space-y-3">
                  <h3 className="text-[14px] font-bold text-[var(--pol-light-text-primary)]">
                    ثبت اقدام رفع مغایرت مالی
                  </h3>
                  {resolveError && (
                    <ErrorState title="خطا در حل مغایرت" description={resolveError} />
                  )}
                  <Field
                    label="توضیح یا دلیل رفع مغایرت"
                    value={resolveNote}
                    onChange={(e) => setResolveNote(e.target.value)}
                    placeholder="مثال: تراکنش اصلاحی شاپرک بررسی شد و مبلغ لحاظ گردید..."
                  />
                  <div className="flex justify-end">
                    <Button loading={resolving} onClick={() => void resolveCase()}>
                      علامت‌گذاری به عنوان حل‌شده (Resolved)
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          ) : null}
        </section>
      </div>
    </div>
  );
}
