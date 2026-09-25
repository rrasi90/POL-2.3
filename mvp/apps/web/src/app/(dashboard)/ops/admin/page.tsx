"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
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
      str(log.action, "").toLowerCase().includes(q) ||
      str(log.actor_name, "").toLowerCase().includes(q) ||
      str(log.target_entity_type, "").toLowerCase().includes(q) ||
      str(log.target_entity_id, "").toLowerCase().includes(q)
    );
  });

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری ادمین">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-3 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className={cardCls}>
              <Skeleton lines={2} />
            </div>
          ))}
        </div>
        <div className={cardCls}>
          <Skeleton lines={6} />
        </div>
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

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">
          ادمین / Context
        </h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">O-10</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      <section aria-label="داشبورد استثناها" className="grid gap-3 sm:grid-cols-3">
        <div className={cardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">
            استثنای تحویل باز
          </p>
          <p className="mt-1 text-[24px] font-bold text-[var(--pol-light-text-primary)]">
            {(ex.open_count ?? 0).toLocaleString("fa-IR")}
          </p>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
            کل {str(ex.total, "0")} · حل‌شده {str(ex.resolved_count, "0")} · ارتقا{" "}
            {str(ex.escalated_count, "0")}
          </p>
        </div>
        <div className={cardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">اختلاف باز</p>
          <p className="mt-1 text-[24px] font-bold text-[var(--pol-light-text-primary)]">
            {(dash?.disputes?.open_disputes ?? 0).toLocaleString("fa-IR")}
          </p>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
            کل {str(dash?.disputes?.total, "0")}
          </p>
        </div>
        <div className={cardCls}>
          <p className="text-[12px] text-[var(--pol-light-text-secondary)]">
            پرونده پشتیبانی باز
          </p>
          <p className="mt-1 text-[24px] font-bold text-[var(--pol-light-text-primary)]">
            {(dash?.support_cases?.open_cases ?? 0).toLocaleString("fa-IR")}
          </p>
          <p className="mt-1 text-[11px] text-[var(--pol-light-text-muted)]">
            کل {str(dash?.support_cases?.total, "0")}
          </p>
        </div>
      </section>

      <section aria-label="کاربران و سازمان‌ها" className={cardCls}>
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
            کاربران و سازمان‌ها
          </h2>
          <StatusChip tone="success">G-007 resolved</StatusChip>
        </div>
        <p className="mt-2 text-[13px] text-[var(--pol-light-text-secondary)]">
          مدیریت کاربران و سازمان‌ها اکنون به endpointهای واقعی متصل است؛ این صفحه فقط نمای جمع‌بندی است و
          CRUD اصلی در مسیرهای تخصصی انجام می‌شود.
        </p>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <Link
            href="/admin/users"
            className="rounded-[8px] border border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] p-4 text-[14px] font-semibold text-[var(--pol-light-text-secondary)] transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-default)]"
          >
            مدیریت کاربران
          </Link>
          <Link
            href="/admin/orgs"
            className="rounded-[8px] border border-dashed border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-subtle)] p-4 text-[14px] font-semibold text-[var(--pol-light-text-secondary)] transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-default)]"
          >
            مدیریت سازمان‌ها
          </Link>
        </div>
      </section>

      <section aria-label="لاگ ممیزی">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-[16px] font-semibold text-[var(--pol-light-text-primary)]">
            Audit Logs
          </h2>
          <SearchField
            label="جستجوی لاگ"
            placeholder="action / actor / entity…"
            className="ms-auto w-full max-w-xs"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        {filtered.length === 0 ? (
          <div className="mt-3">
            <EmptyState
              title="لاگی یافت نشد"
              description="فیلتر جستجو را پاک کنید یا منتظر رویداد جدید بمانید."
            />
          </div>
        ) : (
          <ul role="list" className="mt-3 space-y-2">
            {filtered.map((log) => (
              <li key={str(log.id)} className={cardCls}>
                <div className="flex flex-wrap items-center gap-2">
                  <StatusChip tone="info">{log.action ?? "—"}</StatusChip>
                  <span className="text-[13px] font-semibold text-[var(--pol-light-text-primary)]">
                    {log.actor_name ?? log.actor_user_id ?? "—"}
                  </span>
                  <span className="text-[12px] text-[var(--pol-light-text-secondary)]" dir="ltr">
                    {log.target_entity_type ?? "—"}
                    {log.target_entity_id ? ` / ${log.target_entity_id}` : ""}
                  </span>
                  <StatusChip tone={ageTone(log.created_at, 168, 720)}>
                    {ageLabel(log.created_at)}
                  </StatusChip>
                  <span className="ms-auto text-[11px] text-[var(--pol-light-text-muted)]">
                    {formatDateTime(log.created_at)}
                  </span>
                </div>
                {log.state_before || log.state_after || log.reason ? (
                  <p className="mt-1.5 text-[12px] text-[var(--pol-light-text-secondary)]">
                    {log.state_before ? `قبل: ${log.state_before} → ` : ""}
                    {log.state_after ? `بعد: ${log.state_after}` : ""}
                    {log.reason ? ` · ${log.reason}` : ""}
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        )}
        {!exhausted ? (
          <div className="mt-3 flex justify-center">
            <Button variant="secondary" size="sm" loading={loadingMore} onClick={() => void loadMore()}>
              بارگذاری موارد بیشتر
            </Button>
          </div>
        ) : null}
      </section>
    </div>
  );
}
