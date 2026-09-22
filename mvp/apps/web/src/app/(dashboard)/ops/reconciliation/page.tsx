"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Button,
  EmptyState,
  ErrorState,
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
  formatToman,
  idOf,
  itemsOf,
  str,
  reconStatusLabel,
  reconStatusTone,
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

  async function resolveCase() {
    if (!selectedId) return;
    setResolving(true);
    setResolveError(null);
    try {
      const body = resolveNote.trim() ? { resolution_note: resolveNote.trim() } : {};
      const updated = await getApi().patch<ReconCase>(
        `/api/v1/finance/reconciliation/${selectedId}/resolve`,
        body,
      );
      setDetail(updated);
      setResolveNote("");
      await load();
    } catch (err) {
      setResolveError(err instanceof Error ? err.message : "تسویه ناموفق بود");
    } finally {
      setResolving(false);
    }
  }

  const filtered = items.filter((c) => {
    if (!query.trim()) return true;
    const q = query.trim().toLowerCase();
    return (
      str(c.payment_id, "").toLowerCase().includes(q) ||
      str(c.external_reference, "").toLowerCase().includes(q) ||
      str(c.id, "").toLowerCase().includes(q)
    );
  });

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری تطبیق">
        <Skeleton className="h-8 w-48" />
        <div className={cardCls}>
          <Skeleton lines={6} />
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت تطبیق مالی ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  const canResolve =
    detail && detail.status !== "RESOLVED" && detail.status !== "CANCELLED";

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          تطبیق مالی
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">O-06</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      <div className="grid gap-2 sm:grid-cols-[1fr_auto_auto]">
        <SearchField
          label="جستجو"
          placeholder="payment / reference…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select
          aria-label="فیلتر وضعیت"
          className="h-10 rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 text-[14px] text-[var(--pol-light-text-primary)]"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s || "all"} value={s}>
              {s ? (reconStatusLabel[s] ?? s) : "همه وضعیت‌ها"}
            </option>
          ))}
        </select>
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <section aria-label="فهرست موارد">
          {filtered.length === 0 ? (
            <EmptyState
              title="مورد تطبیقی یافت نشد"
              description="فیلترها را تغییر دهید یا منتظر مغایرت جدید بمانید."
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
                      <StatusChip tone={reconStatusTone[c.status ?? ""] ?? "neutral"}>
                        {reconStatusLabel[c.status ?? ""] ?? c.status ?? "—"}
                      </StatusChip>
                      <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                        {ageLabel(c.opened_at)}
                      </span>
                    </div>
                    <div className="mt-1.5 flex flex-wrap gap-3 text-[13px]">
                      <span className="text-[var(--pol-light-text-primary)]" dir="ltr">
                        {c.payment_id ?? str(c.id)}
                      </span>
                      <span className="text-[var(--pol-light-text-secondary)]">
                        انتظار {formatToman(c.expected_amount_toman)} · مشاهده{" "}
                        {formatToman(c.observed_amount_toman)}
                      </span>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section aria-label="جزئیات مورد" className={cardCls}>
          {!selectedId ? (
            <EmptyState
              title="موردی انتخاب نشده"
              description="از فهرست کنار، یک مورد تطبیق انتخاب کنید."
            />
          ) : detailState === "loading" ? (
            <div aria-busy="true">
              <Skeleton lines={5} />
            </div>
          ) : detailState === "error" ? (
            <ErrorState
              title="دریافت جزئیات ناموفق بود"
              description={detailError ?? undefined}
              onRetry={() => selectedId && void loadDetail(selectedId)}
            />
          ) : detail ? (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center gap-2">
                <StatusChip tone={reconStatusTone[detail.status ?? ""] ?? "neutral"}>
                  {reconStatusLabel[detail.status ?? ""] ?? detail.status ?? "—"}
                </StatusChip>
                <StatusChip tone={ageTone(detail.opened_at, 24, 120)}>
                  {ageLabel(detail.opened_at)}
                </StatusChip>
              </div>

              <dl className="grid gap-3 sm:grid-cols-2">
                <div>
                  <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
                    شناسه
                  </dt>
                  <dd className="text-[13px] text-[var(--pol-light-text-primary)]" dir="ltr">
                    {detail.id}
                  </dd>
                </div>
                <div>
                  <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">پرداخت</dt>
                  <dd className="text-[13px] text-[var(--pol-light-text-primary)]" dir="ltr">
                    {detail.payment_id ?? "—"}
                  </dd>
                </div>
                <div>
                  <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
                    مبلغ انتظار
                  </dt>
                  <dd className="text-[13px] text-[var(--pol-light-text-primary)]">
                    {formatToman(detail.expected_amount_toman)}
                  </dd>
                </div>
                <div>
                  <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
                    مبلغ مشاهده
                  </dt>
                  <dd className="text-[13px] text-[var(--pol-light-text-primary)]">
                    {formatToman(detail.observed_amount_toman)}
                  </dd>
                </div>
                <div>
                  <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
                    مرجع خارجی
                  </dt>
                  <dd className="text-[13px] text-[var(--pol-light-text-primary)]" dir="ltr">
                    {detail.external_reference ?? "—"}
                  </dd>
                </div>
                <div>
                  <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
                    تعداد تلاش
                  </dt>
                  <dd className="text-[13px] text-[var(--pol-light-text-primary)]">
                    {(detail.attempt_count ?? 0).toLocaleString("fa-IR")}
                  </dd>
                </div>
                <div>
                  <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
                    باز شده
                  </dt>
                  <dd className="text-[13px] text-[var(--pol-light-text-primary)]">
                    {formatDateTime(detail.opened_at)}
                  </dd>
                </div>
                <div>
                  <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
                    تسویه
                  </dt>
                  <dd className="text-[13px] text-[var(--pol-light-text-primary)]">
                    {formatDateTime(detail.resolved_at)}
                  </dd>
                </div>
                {detail.resolution_reason ? (
                  <div className="sm:col-span-2">
                    <dt className="text-[12px] text-[var(--pol-light-text-secondary)]">
                      دلیل تسویه
                    </dt>
                    <dd className="text-[13px] text-[var(--pol-light-text-primary)]">
                      {detail.resolution_reason}
                    </dd>
                  </div>
                ) : null}
              </dl>

              {canResolve ? (
                <div className="border-t border-[var(--pol-light-border-subtle)] pt-3">
                  <h3 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
                    تسویه مورد
                  </h3>
                  {resolveError ? (
                    <div className="mt-2">
                      <ErrorState title="تسویه ناموفق بود" description={resolveError} />
                    </div>
                  ) : null}
                  <textarea
                    value={resolveNote}
                    onChange={(e) => setResolveNote(e.target.value)}
                    rows={2}
                    maxLength={2000}
                    placeholder="یادداشت تسویه (اختیاری)…"
                    className="mt-2 h-auto min-h-[56px] w-full rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-2 text-[14px] text-[var(--pol-light-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
                  />
                  <div className="mt-2">
                    <Button
                      size="sm"
                      variant="success"
                      loading={resolving}
                      onClick={() => void resolveCase()}
                    >
                      تسویه
                    </Button>
                  </div>
                </div>
              ) : null}
            </div>
          ) : null}
        </section>
      </div>
    </div>
  );
}
