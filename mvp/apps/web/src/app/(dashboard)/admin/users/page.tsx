"use client";

import { useCallback, useEffect, useState } from "react";
import { Button, EmptyState, ErrorState, Field, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, itemsOf, type LoadState } from "../../ops/_shared";

interface UserRow {
  id: string; phone_number?: string; full_name?: string; role?: string;
  is_active: boolean; membership_count?: number;
}

export default function AdminUsersPage() {
  const [rows, setRows] = useState<UserRow[]>([]);
  const [query, setQuery] = useState("");
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading"); setError(null);
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

  useEffect(() => { void load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function toggle(row: UserRow) {
    setError(null);
    try {
      await getApi().patch("/api/v1/admin/users/" + row.id + "/status", { is_active: !row.is_active });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "تغییر وضعیت ناموفق بود");
    }
  }

  if (state === "loading") return <div className="space-y-4" aria-busy="true"><Skeleton className="h-8 w-48" /><div className={cardCls}><Skeleton lines={7} /></div></div>;
  if (state === "error") return <ErrorState title="دریافت کاربران ناموفق بود" description={error ?? undefined} onRetry={() => void load()} />;

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] font-bold text-[var(--pol-light-text-primary)]">کاربران</h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">O-10B · {rows.length.toLocaleString("fa-IR")} کاربر</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>به‌روزرسانی</Button>
      </header>
      <section className={cardCls}>
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-[220px] flex-1">
            <Field label="جستجو" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="نام، موبایل یا نقش" />
          </div>
          <Button onClick={() => void load()}>جستجو</Button>
        </div>
      </section>
      {error ? <div className="text-[13px] text-[var(--pol-light-semantic-danger)]">{error}</div> : null}
      {rows.length === 0 ? (
        <EmptyState title="کاربری یافت نشد" description="هیچ کاربری با این معیار پیدا نشد." />
      ) : (
        <ul className="space-y-2">
          {rows.map((r) => (
            <li key={r.id} className={cardCls}>
              <div className="flex flex-wrap items-center gap-2">
                <StatusChip tone={r.is_active ? "success" : "danger"}>{r.is_active ? "فعال" : "غیرفعال"}</StatusChip>
                <span className="font-semibold">{r.full_name ?? "—"}</span>
                <span className="text-[12px] text-[var(--pol-light-text-muted)]">{r.role ?? "—"}</span>
                <span className="ms-auto" dir="ltr">{r.phone_number ?? "—"}</span>
              </div>
              <div className="mt-2 text-[12px] text-[var(--pol-light-text-muted)]">عضویت‌ها: {Number(r.membership_count ?? 0).toLocaleString("fa-IR")}</div>
              <div className="mt-3">
                <Button variant={r.is_active ? "danger" : "success"} size="sm" onClick={() => void toggle(r)}>
                  {r.is_active ? "غیرفعال‌سازی" : "فعال‌سازی"}
                </Button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
