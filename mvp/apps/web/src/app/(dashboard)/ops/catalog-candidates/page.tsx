"use client";

import { useCallback, useEffect, useState } from "react";
import { Button, ErrorState, Field, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, itemsOf, type LoadState } from "../../_shared";

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

function toneForStatus(status: Candidate["status"]): "success" | "warning" | "danger" | "neutral" {
  if (status === "APPROVED_CANONICAL") return "success";
  if (status === "MERGED_EXISTING") return "success";
  if (status === "REJECTED") return "danger";
  return "warning";
}

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
      <div className="space-y-4" aria-busy="true">
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
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          بازبینی کاندیداهای کاتالوگ
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">OP-13 · {rows.length.toLocaleString("fa-IR")} مورد</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>به‌روزرسانی</Button>
      </header>

      <section className={cardCls} aria-label="فیلتر کاندیداها">
        <div className="grid gap-3 md:grid-cols-[180px_1fr]">
          <label className="text-[12px] text-[var(--pol-light-text-secondary)]">
            وضعیت
            <select
              className="mt-1 w-full rounded-[10px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] px-3 py-2 text-[13px]"
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
            >
              <option value="PENDING_REVIEW">در انتظار بررسی</option>
              <option value="APPROVED_CANONICAL">تأیید کانونیکال</option>
              <option value="MERGED_EXISTING">ادغام‌شده</option>
              <option value="REJECTED">ردشده</option>
              <option value="">همه</option>
            </select>
          </label>
          <Field
            label="جست‌وجو"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="نام، برند، بارکد یا SKU"
          />
        </div>
      </section>

      {error ? (
        <div className="rounded-[12px] border border-[var(--pol-light-semantic-danger)]/40 bg-[var(--pol-light-surface-default)] p-3 text-[13px] text-[var(--pol-light-semantic-danger)]">
          {error}
        </div>
      ) : null}

      {rows.length === 0 ? (
        <div className={cardCls}>
          <p className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">کاندیدایی برای نمایش وجود ندارد.</p>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-muted)]">فیلترها را تغییر دهید یا بعداً دوباره بررسی کنید.</p>
        </div>
      ) : (
        <ul role="list" className="space-y-3">
          {rows.map((candidate) => {
            const form = forms[candidate.candidate_id] ?? emptyForm();
            const pending = candidate.status === "PENDING_REVIEW";
            return (
              <li key={candidate.candidate_id} className={cardCls}>
                <div className="flex flex-wrap items-center gap-2">
                  <StatusChip tone={toneForStatus(candidate.status)}>{candidate.status}</StatusChip>
                  <span className="font-semibold text-[var(--pol-light-text-primary)]">{candidate.proposed_title}</span>
                  <span className="text-[12px] text-[var(--pol-light-text-muted)]">{candidate.vendor_name ?? candidate.vendor_id}</span>
                </div>

                <div className="mt-3 grid gap-2 text-[12px] text-[var(--pol-light-text-secondary)] md:grid-cols-3">
                  <div>برند پیشنهادی: <span className="font-medium">{candidate.proposed_brand ?? "—"}</span></div>
                  <div dir="ltr">بارکد: <span className="font-medium">{candidate.barcode ?? "—"}</span></div>
                  <div dir="ltr">SKU: <span className="font-medium">{candidate.vendor_sku ?? "—"}</span></div>
                  <div dir="ltr">Candidate ID: {candidate.candidate_id}</div>
                  <div dir="ltr">Created: {candidate.created_at ?? "—"}</div>
                  <div dir="ltr">Resolved: {candidate.resolved_at ?? "—"}</div>
                </div>

                {candidate.review_notes ? (
                  <div className="mt-3 rounded-[10px] bg-[var(--pol-light-surface-subtle)] p-3 text-[12px] text-[var(--pol-light-text-secondary)]">
                    دلیل ثبت‌شده: {candidate.review_notes}
                  </div>
                ) : null}

                {pending ? (
                  <div className="mt-4 border-t border-[var(--pol-light-border-subtle)] pt-4">
                    <div className="grid gap-3 md:grid-cols-2">
                      <label className="text-[12px] text-[var(--pol-light-text-secondary)]">
                        تصمیم
                        <select
                          className="mt-1 w-full rounded-[10px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] px-3 py-2 text-[13px]"
                          value={form.action}
                          onChange={(event) => updateForm(candidate.candidate_id, { action: event.target.value as ReviewAction })}
                        >
                          <option value="REJECT">رد</option>
                          <option value="MERGE_EXISTING">ادغام با کالای موجود</option>
                          <option value="APPROVE_CANONICAL">ساخت کالای کانونیکال</option>
                        </select>
                      </label>
                      <Field
                        label="دلیل"
                        value={form.reason}
                        onChange={(event) => updateForm(candidate.candidate_id, { reason: event.target.value })}
                        placeholder="دلیل تصمیم"
                      />
                    </div>

                    {form.action === "MERGE_EXISTING" ? (
                      <div className="mt-3">
                        <Field
                          label="Target Product ID"
                          value={form.target_product_id}
                          onChange={(event) => updateForm(candidate.candidate_id, { target_product_id: event.target.value })}
                          dir="ltr"
                          placeholder="UUID"
                        />
                      </div>
                    ) : null}

                    {form.action === "APPROVE_CANONICAL" ? (
                      <div className="mt-3 grid gap-3 md:grid-cols-2">
                        <Field label="Brand ID" value={form.brand_id} onChange={(event) => updateForm(candidate.candidate_id, { brand_id: event.target.value })} dir="ltr" placeholder="UUID" />
                        <Field label="Category ID" value={form.category_id} onChange={(event) => updateForm(candidate.candidate_id, { category_id: event.target.value })} dir="ltr" placeholder="UUID" />
                        <Field label="Subcategory ID" value={form.subcategory_id} onChange={(event) => updateForm(candidate.candidate_id, { subcategory_id: event.target.value })} dir="ltr" placeholder="UUID" />
                        <Field label="نام کانونیکال (اختیاری)" value={form.canonical_name_fa} onChange={(event) => updateForm(candidate.candidate_id, { canonical_name_fa: event.target.value })} />
                      </div>
                    ) : null}

                    <div className="mt-3">
                      <Button loading={busyId === candidate.candidate_id} disabled={busyId !== null} onClick={() => void review(candidate)}>
                        ثبت تصمیم
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
