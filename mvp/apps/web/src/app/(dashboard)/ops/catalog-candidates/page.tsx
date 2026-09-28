"use client";

import { useCallback, useEffect, useState } from "react";
import { Button, EmptyState, ErrorState, Field, Skeleton, StatusChip, type StatusTone } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, inputCls, itemsOf, type LoadState } from "../_shared";

type ReviewAction = "APPROVE_CANONICAL" | "MERGE_EXISTING" | "REJECT";

interface Candidate {
  candidate_id: string;
  vendor_id: string;
  vendor_name?: string | null;
  proposed_title: string;
  proposed_brand?: string | null;
  barcode?: string | null;
  vendor_sku?: string | null;
  photo_asset_id?: string | null;
  status: "PENDING_REVIEW" | "APPROVED_CANONICAL" | "MERGED_EXISTING" | "REJECTED";
  resolved_product_id?: string | null;
  reviewed_by_user_id?: string | null;
  review_notes?: string | null;
  created_at?: string | null;
  resolved_at?: string | null;
}

interface CandidateForm {
  action: ReviewAction;
  reason: string;
  target_product_id: string;
  brand_id: string;
  category_id: string;
  subcategory_id: string;
  canonical_name_fa: string;
}

const emptyForm = (): CandidateForm => ({
  action: "REJECT",
  reason: "",
  target_product_id: "",
  brand_id: "",
  category_id: "",
  subcategory_id: "",
  canonical_name_fa: "",
});

function toneForStatus(status: Candidate["status"]): StatusTone {
  if (status === "APPROVED_CANONICAL") return "success";
  if (status === "MERGED_EXISTING") return "info";
  if (status === "REJECTED") return "danger";
  return "warning";
}

const statusLabel: Record<string, string> = {
  PENDING_REVIEW: "در انتظار بررسی",
  APPROVED_CANONICAL: "تأیید کانونیکال",
  MERGED_EXISTING: "ادغام‌شده",
  REJECTED: "ردشده",
};

export default function OpsCatalogCandidatesPage() {
  const [rows, setRows] = useState<Candidate[]>([]);
  const [statusFilter, setStatusFilter] = useState("PENDING_REVIEW");
  const [query, setQuery] = useState("");
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [forms, setForms] = useState<Record<string, CandidateForm>>({});

  const load = useCallback(async () => {
    setState("loading");
    setError(null);
    try {
      const suffix = new URLSearchParams();
      if (statusFilter) suffix.set("status", statusFilter);
      if (query.trim()) suffix.set("query", query.trim());
      suffix.set("limit", "50");
      const data = await getApi().get<unknown>(`/api/v1/admin/product-candidates?${suffix.toString()}`);
      const candidates = itemsOf<Candidate>(data, "candidates");
      setRows(candidates);
      setForms((previous) => {
        const next = { ...previous };
        for (const candidate of candidates) {
          if (!next[candidate.candidate_id]) next[candidate.candidate_id] = emptyForm();
        }
        return next;
      });
      setState("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "دریافت کاندیداهای کاتالوگ ناموفق بود");
      setState("error");
    }
  }, [query, statusFilter]);

  useEffect(() => {
    void load();
  }, [load]);

  function updateForm(id: string, patch: Partial<CandidateForm>) {
    setForms((previous) => ({
      ...previous,
      [id]: { ...(previous[id] ?? emptyForm()), ...patch },
    }));
  }

  async function review(candidate: Candidate) {
    const form = forms[candidate.candidate_id] ?? emptyForm();
    if (!form.reason.trim()) {
      setError("برای ثبت تصمیم بازبینی، درج دلیل الزامی است.");
      return;
    }
    setBusyId(candidate.candidate_id);
    setError(null);
    try {
      const body: Record<string, unknown> = {
        action: form.action,
        reason: form.reason.trim(),
      };
      if (form.action === "MERGE_EXISTING") {
        body.target_product_id = form.target_product_id.trim();
      }
      if (form.action === "APPROVE_CANONICAL") {
        body.brand_id = form.brand_id.trim();
        body.category_id = form.category_id.trim();
        body.subcategory_id = form.subcategory_id.trim();
        if (form.canonical_name_fa.trim()) body.canonical_name_fa = form.canonical_name_fa.trim();
      }
      await getApi().patch(`/api/v1/admin/product-candidates/${candidate.candidate_id}`, body);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "ثبت تصمیم بازبینی ناموفق بود");
    } finally {
      setBusyId(null);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری کاندیداها">
        <Skeleton className="h-8 w-64" />
        <div className={cardCls}><Skeleton lines={8} /></div>
      </div>
    );
  }

  if (state === "error") {
    return <ErrorState title="دریافت کاندیداهای کاتالوگ ناموفق بود" description={error ?? undefined} onRetry={() => void load()} />;
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline justify-between gap-3 border-b border-[var(--pol-light-border-subtle)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] leading-[30px] font-bold text-[var(--pol-light-text-primary)]">
              بازبینی کاندیداهای کاتالوگ
            </h1>
            <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              OP-13
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-muted)]">
            بررسی و اعتبارسنجی اقلام کاتالوگ پیشنهادی تأمین‌کنندگان جهت اتصال به محصولات کانونیکال
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[12px] font-medium text-[var(--pol-light-text-muted)]">
            {rows.length.toLocaleString("fa-IR")} مورد
          </span>
          <Button variant="secondary" size="sm" onClick={() => void load()}>به‌روزرسانی</Button>
        </div>
      </header>

      {/* Filter bar */}
      <section className={cardCls} aria-label="فیلتر کاندیداها">
        <div className="grid gap-3 sm:grid-cols-[200px_1fr]">
          <div>
            <label className="mb-1 block text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
              وضعیت بررسی
            </label>
            <select
              className={inputCls}
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
            >
              <option value="PENDING_REVIEW">در انتظار بررسی</option>
              <option value="APPROVED_CANONICAL">تأیید کانونیکال</option>
              <option value="MERGED_EXISTING">ادغام‌شده</option>
              <option value="REJECTED">ردشده</option>
              <option value="">همه موارد</option>
            </select>
          </div>
          <Field
            label="جست‌وجو"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="نام کالا، برند، بارکد یا شناسه SKU..."
          />
        </div>
      </section>

      {error ? (
        <div className="rounded-xl border border-[var(--pol-light-semantic-danger)]/30 bg-[var(--pol-light-semantic-danger)]/10 p-3 text-[13px] text-[var(--pol-light-semantic-danger)]">
          {error}
        </div>
      ) : null}

      {rows.length === 0 ? (
        <EmptyState
          title="کاندیدایی برای نمایش وجود ندارد"
          description="با تغییر فیلتر وضعیت یا کلیدواژه جست‌وجو دوباره تلاش کنید."
        />
      ) : (
        <ul role="list" className="space-y-3">
          {rows.map((candidate) => {
            const form = forms[candidate.candidate_id] ?? emptyForm();
            const pending = candidate.status === "PENDING_REVIEW";
            return (
              <li key={candidate.candidate_id} className={cardCls}>
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--pol-light-border-subtle)] pb-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusChip tone={toneForStatus(candidate.status)}>
                      {statusLabel[candidate.status] ?? candidate.status}
                    </StatusChip>
                    <span className="font-bold text-[14px] text-[var(--pol-light-text-primary)]">
                      {candidate.proposed_title}
                    </span>
                  </div>
                  <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                    فروشنده: <strong className="font-medium text-[var(--pol-light-text-secondary)]">{candidate.vendor_name ?? candidate.vendor_id}</strong>
                  </span>
                </div>

                <div className="mt-3 grid gap-2.5 text-[12px] text-[var(--pol-light-text-secondary)] sm:grid-cols-2 lg:grid-cols-3">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[var(--pol-light-text-muted)]">برند پیشنهادی:</span>
                    <span className="font-medium text-[var(--pol-light-text-primary)]">{candidate.proposed_brand ?? "—"}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[var(--pol-light-text-muted)]">بارکد:</span>
                    <span className="font-mono text-[var(--pol-light-text-primary)]" dir="ltr">{candidate.barcode ?? "—"}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[var(--pol-light-text-muted)]">شناسه SKU:</span>
                    <span className="font-mono text-[var(--pol-light-text-primary)]" dir="ltr">{candidate.vendor_sku ?? "—"}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[var(--pol-light-text-muted)]">شناسه کاندیدا:</span>
                    <span className="font-mono text-[11px]" dir="ltr">{candidate.candidate_id}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[var(--pol-light-text-muted)]">زمان ایجاد:</span>
                    <span className="font-mono text-[11px]" dir="ltr">{candidate.created_at ?? "—"}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[var(--pol-light-text-muted)]">زمان تعیین تکلیف:</span>
                    <span className="font-mono text-[11px]" dir="ltr">{candidate.resolved_at ?? "—"}</span>
                  </div>
                </div>

                {candidate.review_notes ? (
                  <div className="mt-3 rounded-lg border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-2.5 text-[12px] text-[var(--pol-light-text-secondary)]">
                    <span className="font-medium text-[var(--pol-light-text-primary)]">توضیحات بازبینی: </span>
                    {candidate.review_notes}
                  </div>
                ) : null}

                {pending ? (
                  <div className="mt-4 rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)]/50 p-3.5">
                    <h3 className="mb-3 text-[13px] font-bold text-[var(--pol-light-text-primary)]">
                      اقدام بازبینی کاندیدا
                    </h3>
                    <div className="grid gap-3 sm:grid-cols-2">
                      <div>
                        <label className="mb-1 block text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
                          نوع تصمیم
                        </label>
                        <select
                          className={inputCls}
                          value={form.action}
                          onChange={(event) => updateForm(candidate.candidate_id, { action: event.target.value as ReviewAction })}
                        >
                          <option value="REJECT">رد پیشنهاد</option>
                          <option value="MERGE_EXISTING">ادغام با کالای کانونیکال موجود</option>
                          <option value="APPROVE_CANONICAL">ایجاد کالای کانونیکال جدید</option>
                        </select>
                      </div>
                      <Field
                        label="علت / مستندات تصمیم"
                        value={form.reason}
                        onChange={(event) => updateForm(candidate.candidate_id, { reason: event.target.value })}
                        placeholder="علت رد یا شماره رفرنس..."
                      />
                    </div>

                    {form.action === "MERGE_EXISTING" ? (
                      <div className="mt-3">
                        <Field
                          label="Target Product ID (شناسه کالای هدف)"
                          value={form.target_product_id}
                          onChange={(event) => updateForm(candidate.candidate_id, { target_product_id: event.target.value })}
                          dir="ltr"
                          placeholder="UUID کالای کانونیکال"
                        />
                      </div>
                    ) : null}

                    {form.action === "APPROVE_CANONICAL" ? (
                      <div className="mt-3 grid gap-3 sm:grid-cols-2">
                        <Field label="Brand ID" value={form.brand_id} onChange={(event) => updateForm(candidate.candidate_id, { brand_id: event.target.value })} dir="ltr" placeholder="UUID برند" />
                        <Field label="Category ID" value={form.category_id} onChange={(event) => updateForm(candidate.candidate_id, { category_id: event.target.value })} dir="ltr" placeholder="UUID دسته‌بندی اصلی" />
                        <Field label="Subcategory ID" value={form.subcategory_id} onChange={(event) => updateForm(candidate.candidate_id, { subcategory_id: event.target.value })} dir="ltr" placeholder="UUID زیردسته" />
                        <Field label="نام کانونیکال فارسی (اختیاری)" value={form.canonical_name_fa} onChange={(event) => updateForm(candidate.candidate_id, { canonical_name_fa: event.target.value })} placeholder="عنوان استاندارد کانونیکال" />
                      </div>
                    ) : null}

                    <div className="mt-3.5 flex justify-end">
                      <Button
                        size="sm"
                        variant={form.action === "REJECT" ? "danger" : "primary"}
                        loading={busyId === candidate.candidate_id}
                        disabled={busyId !== null}
                        onClick={() => void review(candidate)}
                      >
                        ثبت تصمیم نهایی
                      </Button>
                    </div>
                  </div>
                ) : null}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
