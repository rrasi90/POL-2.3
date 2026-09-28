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
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, itemsOf, type LoadState } from "../../ops/_shared";

interface UserRow {
  id: string;
  phone_number?: string;
  full_name?: string;
  role?: string;
  is_active: boolean;
  membership_count?: number;
}

export default function AdminUsersPage() {
  const [rows, setRows] = useState<UserRow[]>([]);
  const [query, setQuery] = useState("");
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setError(null);
    try {
      const qs = query.trim() ? "?query=" + encodeURIComponent(query.trim()) : "";
      const data = await getApi().get<unknown>("/api/v1/admin/users" + qs);
      setRows(itemsOf<UserRow>(data, "users"));
      setState("ready");
    } catch (e) {
      setError(e instanceof Error ? e.message : "دریافت کاربران ناموفق بود");
      setState("error");
    }
  }, [query]);

  useEffect(() => {
    void load();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function toggle(row: UserRow) {
    setBusyId(row.id);
    setError(null);
    try {
      await getApi().patch("/api/v1/admin/users/" + row.id + "/status", { is_active: !row.is_active });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "تغییر وضعیت ناموفق بود");
    } finally {
      setBusyId(null);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری کاربران">
        <Skeleton className="h-8 w-48" />
        <div className={cardCls}><Skeleton lines={3} /></div>
        <div className={cardCls}><Skeleton lines={8} /></div>
      </div>
    );
  }

  if (state === "error") {
    return <ErrorState title="دریافت کاربران ناموفق بود" description={error ?? undefined} onRetry={() => void load()} />;
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
              مدیریت کاربران سامانه
            </h1>
            <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              O-10B
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-muted)]">
            فهرست حساب‌های کاربری فعال در نقش‌های خرده‌فروش، تأمین‌کننده، پشتیبان و مدیر سیستم
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[12px] font-medium text-[var(--pol-light-text-muted)]">
            {rows.length.toLocaleString("fa-IR")} کاربر
          </span>
          <Button variant="secondary" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
        </div>
      </header>

      {/* Search Bar */}
      <section className={cardCls} aria-label="جست‌وجوی کاربران">
        <div className="grid gap-3 sm:grid-cols-[1fr_auto] items-end">
          <Field
            label="جست‌وجوی کاربر"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="نام کاربر، شماره موبایل یا عنوان نقش..."
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
          title="کاربری یافت نشد"
          description="کاربری با معیارهای جست‌وجو در پایگاه داده ثبت نشده است."
        />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>نام کاربر / شناسه</TableHead>
              <TableHead>شماره همراه</TableHead>
              <TableHead>نقش</TableHead>
              <TableHead>وضعیت حساب</TableHead>
              <TableHead>عضویت‌ها</TableHead>
              <TableHead className="text-end">اقدام</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((r) => {
              const isBusy = busyId === r.id;
              return (
                <TableRow key={r.id}>
                  <TableCell>
                    <div className="font-bold text-[14px] text-[var(--pol-light-text-primary)]">
                      {r.full_name ?? "بدون نام"}
                    </div>
                    <div className="font-mono text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
                      {r.id}
                    </div>
                  </TableCell>
                  <TableCell className="font-mono text-[13px]" dir="ltr">
                    {r.phone_number ?? "—"}
                  </TableCell>
                  <TableCell>
                    <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 font-mono text-[11px] font-medium text-[var(--pol-light-text-secondary)]" dir="ltr">
                      {r.role ?? "—"}
                    </span>
                  </TableCell>
                  <TableCell>
                    <StatusChip tone={r.is_active ? "success" : "danger"}>
                      {r.is_active ? "فعال" : "غیرفعال"}
                    </StatusChip>
                  </TableCell>
                  <TableCell className="tabular-nums">
                    {Number(r.membership_count ?? 0).toLocaleString("fa-IR")}
                  </TableCell>
                  <TableCell className="text-end">
                    <Button
                      variant={r.is_active ? "danger" : "success"}
                      size="sm"
                      disabled={isBusy}
                      loading={isBusy}
                      onClick={() => void toggle(r)}
                      className="text-[11px] h-7 px-2.5"
                    >
                      {r.is_active ? "غیرفعال‌سازی" : "فعال‌سازی حساب"}
                    </Button>
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
