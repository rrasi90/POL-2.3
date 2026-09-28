"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Button,
  EmptyState,
  ErrorState,
  Field,
  Skeleton,
  StatusChip,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  type StatusTone,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, itemsOf, type LoadState } from "../../ops/_shared";

interface Org {
  id: string;
  name: string;
  org_type: string;
  status: string;
  national_id?: string | null;
  membership_count?: number;
}

const statusOptions = ["ACTIVE", "SUSPENDED", "APPROVED", "UNDER_REVIEW", "REJECTED"] as const;

const orgStatusLabel: Record<string, string> = {
  ACTIVE: "فعال",
  SUSPENDED: "معلق",
  APPROVED: "تأییدشده",
  UNDER_REVIEW: "در انتظار بررسی",
  REJECTED: "ردشده",
};

function toneForOrgStatus(status: string): StatusTone {
  if (status === "ACTIVE" || status === "APPROVED") return "success";
  if (status === "SUSPENDED" || status === "REJECTED") return "danger";
  if (status === "UNDER_REVIEW") return "warning";
  return "neutral";
}

export default function AdminOrgsPage() {
  const [rows, setRows] = useState<Org[]>([]);
  const [query, setQuery] = useState("");
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setError(null);
    try {
      const qs = query.trim() ? "?query=" + encodeURIComponent(query.trim()) : "";
      const data = await getApi().get<unknown>("/api/v1/admin/organizations" + qs);
      setRows(itemsOf<Org>(data, "organizations"));
      setState("ready");
    } catch (e) {
      setError(e instanceof Error ? e.message : "دریافت سازمان‌ها ناموفق بود");
      setState("error");
    }
  }, [query]);

  useEffect(() => {
    void load();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function changeStatus(row: Org, status: string) {
    setBusyId(row.id);
    setError(null);
    try {
      await getApi().patch("/api/v1/admin/organizations/" + row.id + "/status", { status });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "تغییر وضعیت ناموفق بود");
    } finally {
      setBusyId(null);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری سازمان‌ها">
        <Skeleton className="h-8 w-48" />
        <div className={cardCls}><Skeleton lines={3} /></div>
        <div className={cardCls}><Skeleton lines={8} /></div>
      </div>
    );
  }

  if (state === "error") {
    return <ErrorState title="دریافت سازمان‌ها ناموفق بود" description={error ?? undefined} onRetry={() => void load()} />;
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline justify-between gap-3 border-b border-[var(--pol-light-border-subtle)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Link
              href="/admin"
              className="text-[12px] font-medium text-[var(--pol-light-brand-primary)] hover:underline"
            >
              ← بازگشت
            </Link>
            <span className="text-[var(--pol-light-text-disabled)]">/</span>
            <h1 className="text-[22px] leading-[30px] font-bold text-[var(--pol-light-text-primary)]">
              مدیریت سازمان‌ها
            </h1>
            <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              O-10B
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-muted)]">
            فهرست بنگاه‌های اقتصادی، اصناف، فروشندگان و خرده‌فروشان ثبت‌نامی در سامانه
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[12px] font-medium text-[var(--pol-light-text-muted)]">
            {rows.length.toLocaleString("fa-IR")} سازمان
          </span>
          <Button variant="secondary" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
        </div>
      </header>

      {/* Search Bar */}
      <section className={cardCls} aria-label="جست‌وجوی سازمان">
        <div className="grid gap-3 sm:grid-cols-[1fr_auto] items-end">
          <Field
            label="جست‌وجوی سازمان"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="نام سازمان، شناسه یا شناسه ملی..."
          />
          <Button size="sm" onClick={() => void load()}>
            جست‌وجو
          </Button>
        </div>
      </section>

      {error ? (
        <div className="rounded-xl border border-[var(--pol-light-semantic-danger)]/30 bg-[var(--pol-light-semantic-danger)]/10 p-3 text-[13px] text-[var(--pol-light-semantic-danger)]">
          {error}
        </div>
      ) : null}

      {rows.length === 0 ? (
        <EmptyState
          title="سازمانی یافت نشد"
          description="سازمانی با مشخصات جست‌وجوشده در پایگاه داده وجود ندارد."
        />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>نام سازمان / شناسه</TableHead>
              <TableHead>نوع سازمان</TableHead>
              <TableHead>شناسه ملی</TableHead>
              <TableHead>وضعیت حساب</TableHead>
              <TableHead>تعداد اعضا</TableHead>
              <TableHead className="text-end">تغییر وضعیت</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((r) => {
              const isBusy = busyId === r.id;
              return (
                <TableRow key={r.id}>
                  <TableCell>
                    <div className="font-bold text-[14px] text-[var(--pol-light-text-primary)]">
                      {r.name}
                    </div>
                    <div className="font-mono text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                      {r.id}
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
                      {r.org_type}
                    </span>
                  </TableCell>
                  <TableCell className="font-mono text-[12px]" dir="ltr">
                    {r.national_id ?? "—"}
                  </TableCell>
                  <TableCell>
                    <StatusChip tone={toneForOrgStatus(r.status)}>
                      {orgStatusLabel[r.status] ?? r.status}
                    </StatusChip>
                  </TableCell>
                  <TableCell className="tabular-nums">
                    {Number(r.membership_count ?? 0).toLocaleString("fa-IR")}
                  </TableCell>
                  <TableCell className="text-end">
                    <div className="flex flex-wrap items-center justify-end gap-1.5">
                      {statusOptions
                        .filter((s) => s !== r.status)
                        .map((s) => (
                          <Button
                            key={s}
                            variant={s === "SUSPENDED" || s === "REJECTED" ? "danger" : "secondary"}
                            size="sm"
                            disabled={isBusy}
                            onClick={() => void changeStatus(r, s)}
                            className="text-[11px] h-7 px-2"
                          >
                            {orgStatusLabel[s] ?? s}
                          </Button>
                        ))}
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
