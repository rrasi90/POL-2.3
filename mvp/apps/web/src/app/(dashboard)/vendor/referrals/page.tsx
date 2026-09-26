"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Button,
  EmptyState,
  ErrorState,
  Field,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  cardCls,
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
 * Redeem endpoint exists in API map; UI does NOT surface reward balance (out of scope).
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
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری ارجاع‌ها">
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
        title="دریافت ارجاع‌ها ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          ارجاع‌ها
        </h1>
        <StatusChip tone="info">D-016 · فقط نسبت‌دهی</StatusChip>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">V-08</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      <section aria-label="محدوده" className="rounded-[12px] border border-dashed border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-subtle)] p-4">
        <p className="text-[13px] text-[var(--pol-light-text-secondary)]">
          پاداش چندلایه و کیف پول ارجاع خارج از MVP است (D-016 / D-021). فقط ثبت و نسبت‌دهی
          ارجاع نمایش داده می‌شود — بدون UI موجودی پاداش.
        </p>
      </section>

      <section aria-label="ایجاد ارجاع" className={cardCls}>
        <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
          ارجاع جدید
        </h2>
        {createError ? (
          <div className="mt-3">
            <ErrorState title="ایجاد ارجاع ناموفق بود" description={createError} />
          </div>
        ) : null}
        <div className="mt-3 flex flex-wrap items-end gap-3">
          <div className="min-w-[200px] flex-1">
            <Field
              label="کد ارجاع (اختیاری)"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              hint="در صورت خالی بودن سرور کد می‌سازد"
              dir="ltr"
              maxLength={64}
            />
          </div>
          <Button loading={creating} onClick={() => void createReferral()}>
            ایجاد
          </Button>
        </div>
      </section>

      <section aria-label="فهرست ارجاع‌ها">
        <h2 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          فهرست
        </h2>
        {rows.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="ارجاعی ثبت نشده"
              description="اولین ارجاع خود را بسازید."
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {rows.map((r) => (
              <li key={idOf(r) || str(r.id)} className={cardCls}>
                <div className="flex flex-wrap items-center gap-2">
                  <StatusChip tone="info">{r.status ?? "—"}</StatusChip>
                  <span className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]" dir="ltr">
                    {r.referral_code ?? str(r.id)}
                  </span>
                  <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(r.created_at)}
                  </span>
                </div>
                <div className="mt-2 flex flex-wrap gap-3 text-[13px] text-[var(--pol-light-text-secondary)]">
                  {r.attributed_orders_count != null ? (
                    <span>
                      سفارش نسبت‌گرفته: {Number(r.attributed_orders_count).toLocaleString("fa-IR")}
                    </span>
                  ) : null}
                  {r.attributed_amount_toman != null ? (
                    <span>مبلغ: {formatToman(r.attributed_amount_toman)}</span>
                  ) : null}
                  {r.redeemed_at ? (
                    <span>بازخرید: {formatDateTime(r.redeemed_at)}</span>
                  ) : null}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
