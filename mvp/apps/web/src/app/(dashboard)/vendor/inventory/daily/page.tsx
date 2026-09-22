"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Button,
  EmptyState,
  ErrorState,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  cardCls,
  formatDateTime,
  inputCls,
  itemsOf,
  str,
  type LoadState,
} from "../../_shared";

interface DailyLine {
  id: string;
  product_id?: string | null;
  product_name?: string | null;
  expected_quantity?: number | null;
  confirmed_quantity?: number | null;
  packaging_unit?: string | null;
  delta?: number | null;
}

interface DailyPayload {
  confirmation_date?: string | null;
  status?: string | null;
  lines?: DailyLine[];
}

function todayIsoDate(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

/**
 * V-07 daily inventory confirmation.
 * GET /inventory/daily/{confirmation_date}
 * POST .../confirm  |  POST .../confirm-with-changes
 */
export default function VendorDailyInventoryPage() {
  const [date, setDate] = useState(todayIsoDate());
  const [payload, setPayload] = useState<DailyPayload | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [edits, setEdits] = useState<Record<string, string>>({});
  const [actionError, setActionError] = useState<string | null>(null);
  const [acting, setActing] = useState<"confirm" | "changes" | null>(null);
  const [done, setDone] = useState<string | null>(null);

  const load = useCallback(async (d: string) => {
    if (!d) return;
    setState("loading");
    setErrorMessage(null);
    setDone(null);
    setActionError(null);
    setEdits({});
    try {
      const data = await getApi().get<DailyPayload>(
        `/api/v1/inventory/daily/${d}`,
      );
      setPayload(data);
      const next: Record<string, string> = {};
      for (const line of data?.lines ?? []) {
        const qty =
          line.confirmed_quantity ?? line.expected_quantity ?? 0;
        next[str(line.id)] = String(qty);
      }
      setEdits(next);
      setState("ready");
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : "دریافت موجودی روزانه ناموفق بود",
      );
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load(date);
  }, [date, load]);

  async function confirmPlain() {
    setActing("confirm");
    setActionError(null);
    setDone(null);
    try {
      await getApi().post(`/api/v1/inventory/daily/${date}/confirm`, {});
      setDone("confirm");
      await load(date);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "تأیید ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  async function confirmChanges() {
    const lines = (payload?.lines ?? []).map((line) => {
      const id = str(line.id);
      const qty = Number(edits[id] ?? line.confirmed_quantity ?? line.expected_quantity ?? 0);
      return {
        id,
        product_id: line.product_id,
        confirmed_quantity: Number.isFinite(qty) ? qty : 0,
      };
    });
    setActing("changes");
    setActionError(null);
    setDone(null);
    try {
      await getApi().post(`/api/v1/inventory/daily/${date}/confirm-with-changes`, {
        lines,
      });
      setDone("changes");
      await load(date);
    } catch (err) {
      setActionError(
        err instanceof Error ? err.message : "تأیید با تغییرات ناموفق بود",
      );
    } finally {
      setActing(null);
    }
  }

  const lines = payload?.lines ?? [];
  const hasEdits = lines.some((line) => {
    const id = str(line.id);
    const base = String(line.confirmed_quantity ?? line.expected_quantity ?? 0);
    return edits[id] !== undefined && edits[id] !== base;
  });

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          تأیید روزانه موجودی
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">V-07</span>
        <Link
          href="/vendor/inventory"
          className="text-[13px] text-[var(--pol-light-brand-primary)] hover:underline"
        >
          موجودی
        </Link>
      </header>

      <section aria-label="انتخاب تاریخ" className="flex flex-wrap items-end gap-3">
        <div className="flex flex-col gap-1.5">
          <label
            htmlFor="daily-date"
            className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]"
          >
            تاریخ تأیید
          </label>
          <input
            id="daily-date"
            type="date"
            className={[inputCls, "w-44"].join(" ")}
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </div>
        <Button variant="secondary" size="sm" onClick={() => void load(date)}>
          بارگذاری
        </Button>
        {payload?.status ? (
          <StatusChip tone={payload.status === "CONFIRMED" ? "success" : "warning"}>
            {payload.status}
          </StatusChip>
        ) : null}
        {payload?.confirmation_date ? (
          <span className="text-[12px] text-[var(--pol-light-text-muted)]">
            {payload.confirmation_date}
          </span>
        ) : null}
      </section>

      {state === "loading" ? (
        <div className={cardCls} aria-busy="true" aria-label="در حال بارگذاری">
          <Skeleton lines={5} />
        </div>
      ) : state === "error" ? (
        <ErrorState
          title="دریافت موجودی روزانه ناموفق بود"
          description={errorMessage ?? undefined}
          onRetry={() => void load(date)}
        />
      ) : lines.length === 0 ? (
        <EmptyState
          title="ردیفی برای این تاریخ نیست"
          description="برای روز انتخاب‌شده موجودی روزانه‌ای تعریف نشده است."
        />
      ) : (
        <section aria-label="ردیف‌های موجودی" className={cardCls}>
          <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
            ردیف‌ها
          </h2>
          <ul role="list" className="mt-3 space-y-2">
            {lines.map((line) => {
              const id = str(line.id);
              return (
                <li
                  key={id}
                  className="flex flex-wrap items-center gap-3 rounded-[8px] border border-[var(--pol-light-border-subtle)] p-3"
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-[13px] font-medium text-[var(--pol-light-text-primary)]">
                      {line.product_name ?? id.slice(0, 8)}
                    </p>
                    <p className="text-[12px] text-[var(--pol-light-text-muted)]">
                      مورد انتظار:{" "}
                      {Number(line.expected_quantity ?? 0).toLocaleString("fa-IR")}
                      {line.packaging_unit ? ` ${line.packaging_unit}` : ""}
                    </p>
                  </div>
                  <label className="sr-only" htmlFor={`daily-${id}`}>
                    تعداد تأیید {line.product_name ?? id}
                  </label>
                  <input
                    id={`daily-${id}`}
                    type="number"
                    min={0}
                    className={[inputCls, "w-28"].join(" ")}
                    value={edits[id] ?? ""}
                    onChange={(e) =>
                      setEdits((prev) => ({ ...prev, [id]: e.target.value }))
                    }
                  />
                </li>
              );
            })}
          </ul>

          {actionError ? (
            <div className="mt-3">
              <ErrorState title="تأیید ناموفق بود" description={actionError} />
            </div>
          ) : null}
          {done ? (
            <p className="mt-3 text-[13px] text-[var(--pol-light-semantic-success, #15803d)]">
              {done === "confirm"
                ? "موجودی روزانه تأیید شد."
                : "موجودی با تغییرات تأیید شد."}
            </p>
          ) : null}

          <div className="mt-4 flex flex-wrap gap-2">
            {!hasEdits ? (
              <Button
                loading={acting === "confirm"}
                disabled={acting !== null}
                onClick={() => void confirmPlain()}
              >
                تأیید بدون تغییر
              </Button>
            ) : null}
            <Button
              variant={hasEdits ? "primary" : "secondary"}
              loading={acting === "changes"}
              disabled={acting !== null}
              onClick={() => void confirmChanges()}
            >
              تأیید با تغییرات
            </Button>
          </div>
        </section>
      )}

      <p className="text-[11px] text-[var(--pol-light-text-muted)]">
        آخرین بارگذاری: {formatDateTime(new Date().toISOString())}
      </p>
    </div>
  );
}
