"use client";

import { useEffect, useMemo, useState } from "react";
import { Button, EmptyState, ErrorState, Field, Skeleton } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, type LoadState } from "../_shared";

interface PermissionData {
  roles?: Record<string, string[]>;
  source?: string;
}

export default function OpsPermissionsPage() {
  const [data, setData] = useState<PermissionData | null>(null);
  const [query, setQuery] = useState("");
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setState("loading");
    setError(null);
    try {
      const value = await getApi().get<PermissionData>("/api/v1/ops/permissions");
      setData(value);
      setState("ready");
    } catch (e) {
      setError(e instanceof Error ? e.message : "دریافت مجوزها ناموفق بود");
      setState("error");
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const filteredRoles = useMemo(() => {
    if (!data?.roles) return [];
    const entries = Object.entries(data.roles);
    const q = query.trim().toLowerCase();
    if (!q) return entries;
    return entries.filter(
      ([role, perms]) =>
        role.toLowerCase().includes(q) ||
        perms.some((p) => p.toLowerCase().includes(q)),
    );
  }, [data?.roles, query]);

  const totalRoles = data?.roles ? Object.keys(data.roles).length : 0;

  if (state === "loading") {
    return (
      <div className="space-y-4" aria-busy="true" aria-label="در حال بارگذاری مجوزها">
        <Skeleton className="h-8 w-48" />
        <div className={cardCls}><Skeleton lines={10} /></div>
      </div>
    );
  }

  if (state === "error") {
    return <ErrorState title="دریافت مجوزها ناموفق بود" description={error ?? undefined} onRetry={() => void load()} />;
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline justify-between gap-3 border-b border-[var(--pol-light-border-subtle)] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-[22px] leading-[30px] font-bold text-[var(--pol-light-text-primary)]">
              کاتالوگ مجوزهای سامانه
            </h1>
            <span className="rounded-md bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              OP-11
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-muted)]">
            مرجع رسمی ماتریس دسترسی نقش‌های کاربری، اختیارات RBAC و سیاست‌های کانونیکال
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[12px] font-medium text-[var(--pol-light-text-muted)]">
            {totalRoles.toLocaleString("fa-IR")} نقش سیستمی
          </span>
          <Button variant="secondary" size="sm" onClick={() => void load()}>
            به‌روزرسانی
          </Button>
        </div>
      </header>

      {/* Search filter */}
      <section className={cardCls} aria-label="جست‌وجوی مجوزها">
        <Field
          label="جست‌وجو در نقش‌ها و مجوزها"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="جست‌وجوی نقش یا کلید مجوز مانند order:read, rbac:write..."
          dir="ltr"
        />
      </section>

      {filteredRoles.length === 0 ? (
        <EmptyState
          title="نقش یا مجوزی یافت نشد"
          description="با تغییر عبارت جست‌وجو دوباره بررسی کنید."
        />
      ) : (
        <div className="space-y-4">
          {filteredRoles.map(([role, permissions]) => {
            const matches = query.trim()
              ? permissions.filter((p) => p.toLowerCase().includes(query.trim().toLowerCase()))
              : permissions;

            return (
              <section key={role} className={cardCls}>
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[var(--pol-light-border-subtle)] pb-3">
                  <div className="flex items-center gap-2">
                    <span className="size-2 rounded-full bg-[var(--pol-light-brand-primary)]" />
                    <h2 className="font-mono text-[14px] font-bold text-[var(--pol-light-text-primary)]" dir="ltr">
                      {role}
                    </h2>
                  </div>
                  <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
                    {permissions.length.toLocaleString("fa-IR")} مجوز
                  </span>
                </div>

                <div className="mt-3 flex flex-wrap gap-1.5" dir="ltr">
                  {(query.trim() ? matches : permissions).map((p) => (
                    <span
                      key={p}
                      className="rounded-md border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] px-2 py-1 font-mono text-[11px] text-[var(--pol-light-text-secondary)] transition-colors hover:border-[var(--pol-light-border-strong)] hover:text-[var(--pol-light-text-primary)]"
                    >
                      {p}
                    </span>
                  ))}
                </div>
              </section>
            );
          })}
        </div>
      )}

      {data?.source ? (
        <div className="text-[11px] text-[var(--pol-light-text-muted)]" dir="ltr">
          منبع ماتریس: {data.source}
        </div>
      ) : null}
    </div>
  );
}
