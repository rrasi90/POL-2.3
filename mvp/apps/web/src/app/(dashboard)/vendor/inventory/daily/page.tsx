"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  Skeleton,
  StatusChip,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  inputCls,
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

  const isConfirmed = payload?.status === "CONFIRMED";

  if (state === "loading") {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری تأیید روزانه">
        <Skeleton className="h-9 w-64" />
        <Card className="p-6">
          <Skeleton lines={5} />
        </Card>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت وضعیت موجودی روزانه ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load(date)}
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
              مراسم روزانه تأیید موجودی
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              V-07 · تعهد زنجیره تأمین
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            تأیید صبحگاهی موجودی اقلام انبار تضمین‌کننده تخصیص بهینه و بدون کنسلی سفارش‌هاست
          </p>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <Link
            href="/vendor/inventory"
            className="rounded-lg border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 py-1.5 text-[13px] text-[var(--pol-light-text-primary)] hover:bg-[var(--pol-light-surface-subtle)] transition-colors"
          >
            مدیریت انبار
          </Link>
          <Button variant="secondary" size="sm" onClick={() => void load(date)}>
            به‌روزرسانی
          </Button>
        </div>
      </header>

      {/* Date & Ritual Status Banner */}
      <Card className="p-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2">
              <label htmlFor="daily-date" className="text-[13px] font-semibold text-[var(--pol-light-text-primary)]">
                تاریخ تقویمی:
              </label>
              <input
                id="daily-date"
                type="date"
                className={[inputCls, "w-auto"].join(" ")}
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </div>
            {isConfirmed ? (
              <StatusChip tone="success">تأیید قطعی ثبت شده است</StatusChip>
            ) : (
              <StatusChip tone="warning">نیازمند تأیید موجودی امروز</StatusChip>
            )}
          </div>

          <div className="flex items-center gap-2 border-t border-[var(--pol-light-border-subtle)] pt-3 sm:border-0 sm:pt-0">
            <Button
              variant="outline"
              disabled={acting !== null || isConfirmed}
              loading={acting === "confirm"}
              onClick={() => void confirmPlain()}
            >
              تأیید کامل بدون تغییر
            </Button>
            <Button
              disabled={acting !== null || (!hasEdits && isConfirmed)}
              loading={acting === "changes"}
              onClick={() => void confirmChanges()}
            >
              تأیید با اعمال تغییرات
            </Button>
          </div>
        </div>
      </Card>

      {done && (
        <div className="rounded-xl border border-emerald-300 bg-emerald-50/50 p-4 text-[13px] font-semibold text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950/30 dark:text-emerald-300">
          ✓ تأیید روزانه با موفقیت در سیستم ثبت گردید و کاتالوگ فروشگاه شما معتبر شناخته شد.
        </div>
      )}

      {actionError && (
        <ErrorState title="خطا در ثبت تأیید موجودی" description={actionError} />
      )}

      {/* Lines Table */}
      <section aria-label="اقلام نیازمند تأیید" className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
            اقلام موجودی روزانه ({lines.length.toLocaleString("fa-IR")} قلم)
          </h2>
          {hasEdits && (
            <span className="text-[12px] font-semibold text-amber-600 dark:text-amber-400">
              تغییرات در تعداد اعمال شده و آماده تأیید است
            </span>
          )}
        </div>

        {lines.length === 0 ? (
          <EmptyState
            title="هیچ کالایی برای تأیید در این تاریخ یافت نشد"
            description="ابتدا اقلام کاتالوگ را در بخش کاتالوگ فروشنده فعال نمایید."
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>شرح کالا</TableHead>
                <TableHead>واحد</TableHead>
                <TableHead>موجودی سیستمی</TableHead>
                <TableHead>موجودی واقعی انبار</TableHead>
                <TableHead>مغایرت (اختلاف)</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {lines.map((line) => {
                const id = str(line.id);
                const exp = line.expected_quantity ?? 0;
                const currentVal = edits[id] ?? String(line.confirmed_quantity ?? exp);
                const numVal = Number(currentVal) || 0;
                const delta = numVal - exp;

                return (
                  <TableRow key={line.id}>
                    <TableCell className="font-bold">
                      {line.product_name ?? id.slice(0, 8)}
                    </TableCell>
                    <TableCell className="text-[var(--pol-light-text-secondary)]">
                      {line.packaging_unit ?? "بسته"}
                    </TableCell>
                    <TableCell className="font-mono text-[var(--pol-light-text-secondary)]">
                      {exp.toLocaleString("fa-IR")}
                    </TableCell>
                    <TableCell>
                      <input
                        type="number"
                        min={0}
                        className={[inputCls, "w-28 text-center font-bold"].join(" ")}
                        value={currentVal}
                        onChange={(e) =>
                          setEdits((prev) => ({ ...prev, [id]: e.target.value }))
                        }
                      />
                    </TableCell>
                    <TableCell>
                      <span
                        className={[
                          "font-mono font-bold text-[13px]",
                          delta === 0
                            ? "text-[var(--pol-light-text-muted)]"
                            : delta > 0
                              ? "text-emerald-600 dark:text-emerald-400"
                              : "text-rose-600 dark:text-rose-400",
                        ].join(" ")}
                        dir="ltr"
                      >
                        {delta > 0 ? `+${delta}` : delta}
                      </span>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </section>
    </div>
  );
}
