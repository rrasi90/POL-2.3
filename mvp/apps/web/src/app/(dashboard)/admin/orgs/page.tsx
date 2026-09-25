"use client";

import { useCallback, useEffect, useState } from "react";
import { Button, EmptyState, ErrorState, Field, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, itemsOf, type LoadState } from "../../_shared";

interface Org {
  id: string; name: string; org_type: string; status: string;
  national_id?: string | null; membership_count?: number;
}
const statusOptions = ["ACTIVE", "SUSPENDED", "APPROVED", "UNDER_REVIEW", "REJECTED"] as const;

export default function AdminOrgsPage() {
  const [rows, setRows] = useState<Org[]>([]);
  const [query, setQuery] = useState("");
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading"); setError(null);
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

  useEffect(() => { void load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function changeStatus(row: Org, status: string) {
    setError(null);
    try {
      await getApi().patch("/api/v1/admin/organizations/" + row.id + "/status", { status });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "تغییر وضعیت ناموفق بود");
    }
  }

  if (state === "loading") return <div className="space-y-4" aria-busy="true"><Skeleton className="h-8 w-48" /><div className={cardCls}><Skeleton lines={7} /></div></div>;
  if (state === "error") return <ErrorState title="دریافت سازمان‌ها ناموفق بود" description={error ?? undefined} onRetry={() => void load()} />;

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] font-bold text-[var(--pol-light-text-primary)]">سازمان‌ها</h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">O-10B · {rows.length.toLocaleString("fa-IR")} سازمان</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>به‌روزرسانی</Button>
      </header>
      <section className={cardCls}>
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-[220px] flex-1"><Field label="جستجو" value={query} onChange={(e) => setQuery(e.target.value)} /></div>
          <Button onClick={() => void load()}>جستجو</Button>
        </div>
      </section>
      {error ? <div className="text-[13px] text-[var(--pol-light-semantic-danger)]">{error}</div> : null}
      {rows.length === 0 ? (
        <EmptyState title="سازمانی یافت نشد" description="هیچ سازمانی با این معیار پیدا نشد." />
      ) : (
        <ul className="space-y-2">
          {rows.map((r) => (
            <li key={r.id} className={cardCls}>
              <div className="flex flex-wrap items-center gap-2">
                <StatusChip tone={r.status === "ACTIVE" ? "success" : r.status === "SUSPENDED" ? "danger" : "warning"}>{r.status}</StatusChip>
                <span className="font-semibold">{r.name}</span>
                <span className="text-[12px] text-[var(--pol-light-text-muted)]">{r.org_type}</span>
                <span className="ms-auto text-[12px]">عضویت: {Number(r.membership_count ?? 0).toLocaleString("fa-IR")}</span>
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                {statusOptions.filter((s) => s !== r.status).map((s) => (
                  <Button key={s} variant="secondary" size="sm" onClick={() => void changeStatus(r, s)}>{s}</Button>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
