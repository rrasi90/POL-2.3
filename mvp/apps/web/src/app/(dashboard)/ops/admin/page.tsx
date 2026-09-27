"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  SearchField,
  Skeleton,
  StatusChip,
} from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import {
  formatDateTime,
  itemsOf,
  str,
  type LoadState,
} from "../_shared";

interface ExceptionsDashboard {
  delivery_exceptions?: {
    total?: number;
    open_count?: number;
    resolved_count?: number;
    escalated_count?: number;
  };
  disputes?: { total?: number; open_disputes?: number };
  support_cases?: { total?: number; open_cases?: number };
}

interface AuditLog {
  id: string;
  actor_user_id?: string | null;
  actor_name?: string | null;
  action?: string | null;
  target_entity_type?: string | null;
  target_entity_id?: string | null;
  state_before?: string | null;
  state_after?: string | null;
  reason?: string | null;
  correlation_id?: string | null;
  created_at?: string | null;
}

export default function OpsAdminPage() {
  const [dash, setDash] = useState<ExceptionsDashboard | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [exhausted, setExhausted] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);

  const load = useCallback(async () => {
    setState("loading");
    setErrorMessage(null);
    setExhausted(false);
    try {
      const [d, l] = await Promise.all([
        getApi().get<ExceptionsDashboard>("/api/v1/admin/exceptions/dashboard"),
        getApi().get<unknown>("/api/v1/admin/audit-logs?limit=50&offset=0"),
      ]);
      setDash(d);
      const rows = itemsOf<AuditLog>(l, "logs");
      setLogs(rows);
      if (rows.length < 50) setExhausted(true);
      setState("ready");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "دریافت ادمین ناموفق بود");
      setState("error");
    }
  }, []);

  const loadMore = useCallback(async () => {
    if (loadingMore || exhausted) return;
    setLoadingMore(true);
    try {
      const l = await getApi().get<unknown>(
        `/api/v1/admin/audit-logs?limit=50&offset=${logs.length}`,
      );
      const rows = itemsOf<AuditLog>(l, "logs");
      setLogs((prev) => [...prev, ...rows]);
      if (rows.length < 50) setExhausted(true);
    } catch {
      setExhausted(true);
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore, exhausted, logs.length]);

  useEffect(() => {
    void load();
  }, [load]);

  const filtered = logs.filter((log) => {
    if (!query.trim()) return true;
    const q = query.trim().toLowerCase();
    return (
      (log.action ?? "").toLowerCase().includes(q) ||
      (log.actor_name ?? "").toLowerCase().includes(q) ||
      (log.target_entity_type ?? "").toLowerCase().includes(q) ||
      (log.target_entity_id ?? "").toLowerCase().includes(q) ||
      (log.correlation_id ?? "").toLowerCase().includes(q)
    );
  });

  if (state === "loading") {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری لاگ‌های ممیزی">
        <Skeleton className="h-9 w-52" />
        <div className="grid gap-3 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="p-4">
              <Skeleton lines={2} />
            </Card>
          ))}
        </div>
        <Card className="p-5">
          <Skeleton lines={6} />
        </Card>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت اطلاعات ادمین ناموفق بود"
        description={errorMessage ?? undefined}
        onRetry={() => void load()}
      />
    );
  }

  const ex = dash?.delivery_exceptions ?? {};
  const disputes = dash?.disputes ?? {};
  const cases = dash?.support_cases ?? {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-[var(--pol-light-border-subtle)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[20px] md:text-[24px] font-bold text-[var(--pol-light-text-primary)]">
              داشبورد استثناها و لاگ‌های ممیزی (Audit Logs)
            </h1>
            <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-bold text-[var(--pol-light-text-secondary)]">
              O-10 · Audit Trail
            </span>
          </div>
          <p className="mt-1 text-[12px] text-[var(--pol-light-text-secondary)]">
            ثبت غیرقابل تغییر تمامی رویدادها، تغییرات دسترسی، وضعیت سفارش‌ها و تراکنش‌های سیستمی
          </p>
        </div>

        <Button variant="secondary" size="sm" onClick={() => void load()}>
          به‌روزرسانی لاگ‌ها
        </Button>
      </header>

      {/* Exception Metrics */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="p-4">
          <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
            استثناهای باز تحویل
          </span>
          <div className="mt-2 text-[24px] font-bold text-[var(--pol-light-text-primary)]">
            {(ex.open_count ?? 0).toLocaleString("fa-IR")}
          </div>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
            کل: {str(ex.total, "0")} · ارتقا: {str(ex.escalated_count, "0")}
          </p>
        </Card>

        <Card className="p-4">
          <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
            اختلافات باز
          </span>
          <div className="mt-2 text-[24px] font-bold text-[var(--pol-light-text-primary)]">
            {(disputes.open_disputes ?? 0).toLocaleString("fa-IR")}
          </div>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
            کل موارد: {str(disputes.total, "0")}
          </p>
        </Card>

        <Card className="p-4">
          <span className="text-[12px] font-medium text-[var(--pol-light-text-secondary)]">
            تیکت‌های باز
          </span>
          <div className="mt-2 text-[24px] font-bold text-[var(--pol-light-text-primary)]">
            {(cases.open_cases ?? 0).toLocaleString("fa-IR")}
          </div>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
            کل پرونده‌ها: {str(cases.total, "0")}
          </p>
        </Card>
      </div>

      {/* Audit Logs Section */}
      <section aria-label="لاگ‌های ممیزی" className="space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-[16px] font-bold text-[var(--pol-light-text-primary)]">
              لاگ‌های تغییر وضعیت و رویدادهای ممیزی
            </h2>
            <span className="text-[12px] text-[var(--pol-light-text-secondary)]">
              {filtered.length.toLocaleString("fa-IR")} لاگ یافت‌شده
            </span>
          </div>

          <div className="w-full sm:w-72">
            <SearchField
              label="جستجوی لاگ"
              placeholder="اقدام، کاربر، موجودیت یا شناسه..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <EmptyState
            title="هیچ لاگ ممیزی یافت نشد"
            description="با فیلترهای کنونی هیچ رویدادی در سامانه تطابق ندارد."
          />
        ) : (
          <div className="grid gap-2.5">
            {filtered.map((log) => (
              <Card key={log.id} className="p-3.5">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusChip tone="info">{log.action ?? "ACTION"}</StatusChip>
                    <span className="font-semibold text-[13px] text-[var(--pol-light-text-primary)]">
                      {log.actor_name ?? "سیستم خودکار"}
                    </span>
                    <span className="font-mono text-[12px] text-[var(--pol-light-text-secondary)]" dir="ltr">
                      [{log.target_entity_type ?? "ENTITY"}:{log.target_entity_id?.slice(0, 8) ?? "—"}]
                    </span>
                  </div>

                  <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(log.created_at)}
                  </span>
                </div>

                {(log.state_before || log.state_after) && (
                  <div className="mt-2 rounded-lg bg-[var(--pol-light-surface-subtle)] px-3 py-1.5 font-mono text-[11px] text-[var(--pol-light-text-secondary)]" dir="ltr">
                    {log.state_before ?? "∅"} → {log.state_after ?? "∅"}
                  </div>
                )}

                {log.reason && (
                  <p className="mt-2 text-[12px] text-[var(--pol-light-text-secondary)]">
                    علت: {log.reason}
                  </p>
                )}

                {log.correlation_id && (
                  <div className="mt-1 text-[10px] font-mono text-[var(--pol-light-text-muted)]" dir="ltr">
                    corr_id={log.correlation_id}
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}

        {!exhausted && (
          <div className="flex justify-center pt-2">
            <Button
              variant="secondary"
              loading={loadingMore}
              onClick={() => void loadMore()}
            >
              بارگذاری ۵۰ لاگ قدیمی‌تر
            </Button>
          </div>
        )}
      </section>
    </div>
  );
}
