"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  Field,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  formatDateTime,
  formatToman,
  idOf,
  itemsOf,
  str,
  type LoadState,
} from "../_shared";

interface ReferralRow {
  id: string;
  referral_code?: string | null;
  status?: string | null;
  retailer_id?: string | null;
  referred_entity_type?: string | null;
  attributed_orders_count?: number | null;
  attributed_amount_toman?: number | null;
  created_at?: string | null;
  redeemed_at?: string | null;
}

/**
 * V-08 referrals — attribution only (D-016: no reward UI).
 * POST/GET /referrals, GET /referrals/{id}, POST /referrals/{id}/redeem
 */
export default function VendorReferralsPage() {
  const [rows, setRows] = useState<ReferralRow[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    try {
      const data = await getApi().get<unknown>("/api/v1/referrals");
      setRows(itemsOf<ReferralRow>(data, "referrals"));
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت ارجاع‌ها ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function createReferral() {
    setCreating(true);
    setCreateError(null);
    try {
      const body: Record<string, string> = {};
      if (code.trim()) body.referral_code = code.trim();
      const created = await getApi().post<ReferralRow>("/api/v1/referrals", body);
      setRows((prev) => [created, ...prev]);
      setCode("");
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : "ایجاد ارجاع ناموفق بود");
    } finally {
      setCreating(false);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری ارجاع‌ها">
        <Skeleton className="h-9 w-48" />
        <Card className="p-6">
          <Skeleton lines={4} />
        </Card>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت ارجاع‌ها ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
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
              سیستم معرفی و ارجاع
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              V-08 · D-016
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            ثبت و ردیابی کدهای بازاریابی و انتساب حجم خرید سوپرمارکت‌های دعوت‌شده
          </p>
        </div>

        <Button variant="secondary" size="sm" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      {/* Scope Disclaimer */}
      <div className="flex items-start gap-3 rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-4 text-[13px] text-[var(--pol-light-text-secondary)] leading-relaxed">
        <span className="text-base">ℹ️</span>
        <div>
          <strong className="font-semibold text-[var(--pol-light-text-primary)]">قوانین ارجاع:</strong>{" "}
          در نسخه فعلی، پاداش نقدی مستقیم یا کیف پول چندسطحی فعال نیست (D-016). انتساب سفارش‌ها به صورت
          شفاف برای ارائه گزارش عملکرد و تحلیل کانال‌های جذب محاسبه می‌شود.
        </div>
      </div>

      {/* Create Referral Card */}
      <Card className="p-5 space-y-4">
        <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
          تولید کد ارجاع جدید
        </h2>

        {createError && (
          <ErrorState title="ایجاد ارجاع ناموفق بود" description={createError} />
        )}

        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="flex-1">
            <Field
              label="کد ارجاع دلخواه (اختیاری)"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="مثال: REF-TEHRAN-01"
              hint="در صورت خالی بودن، کد رندوم توسط سرور تولید می‌شود"
              dir="ltr"
              maxLength={64}
            />
          </div>
          <Button
            loading={creating}
            onClick={() => void createReferral()}
          >
            تولید و ثبت کد
          </Button>
        </div>
      </Card>

      {/* Referral Codes List */}
      <section aria-label="فهرست ارجاع‌ها" className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
            کدهای فعال و سوابق انتساب
          </h2>
          <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
            {rows.length.toLocaleString("fa-IR")} کد ارجاع
          </span>
        </div>

        {rows.length === 0 ? (
          <EmptyState
            title="کد ارجاعی ثبت نشده است"
            description="اولین کد ارجاع خود را برای جذب سوپرمارکت‌های جدید بسازید."
          />
        ) : (
          <div className="grid gap-3">
            {rows.map((r) => (
              <Card key={idOf(r) || str(r.id)} className="p-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex items-center gap-2.5">
                    <StatusChip tone="info">{r.status ?? "فعال"}</StatusChip>
                    <span className="font-mono text-[15px] font-bold text-[var(--pol-light-text-primary)]" dir="ltr">
                      {r.referral_code ?? str(r.id)}
                    </span>
                  </div>

                  <span className="text-[12px] text-[var(--pol-light-text-muted)]">
                    تاریخ ایجاد: {formatDateTime(r.created_at)}
                  </span>
                </div>

                <div className="mt-3 flex flex-wrap items-center gap-4 border-t border-[var(--pol-light-border-subtle)] pt-3 text-[13px] text-[var(--pol-light-text-secondary)]">
                  {r.attributed_orders_count != null && (
                    <span>
                      سفارش‌های منتسب:{" "}
                      <strong className="text-[var(--pol-light-text-primary)]">
                        {Number(r.attributed_orders_count).toLocaleString("fa-IR")}
                      </strong>
                    </span>
                  )}
                  {r.attributed_amount_toman != null && (
                    <span>
                      مبلغ خرید کل:{" "}
                      <strong className="text-[var(--pol-light-text-primary)]">
                        {formatToman(r.attributed_amount_toman)}
                      </strong>
                    </span>
                  )}
                  {r.redeemed_at && (
                    <span>استفاده شده در: {formatDateTime(r.redeemed_at)}</span>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
