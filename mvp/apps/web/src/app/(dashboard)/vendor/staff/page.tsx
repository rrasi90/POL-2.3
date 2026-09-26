"use client";

import { useCallback, useEffect, useState } from "react";
import { Button, ErrorState, Field, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { cardCls, itemsOf, type LoadState } from "../_shared";

interface Member {
  membership_id: string;
  user_id: string;
  phone_number?: string | null;
  full_name?: string | null;
  role: "VENDOR_OWNER" | "VENDOR_STAFF";
  status: "INVITED" | "ACTIVE" | "SUSPENDED" | "REVOKED";
  is_primary?: boolean;
}

interface PermissionGrant {
  id: string;
  permission_key: string;
  status: "GRANTED" | "REVOKED";
  granted_at?: string | null;
  revoked_at?: string | null;
}

interface PermissionDetail {
  membership_id: string;
  full_name?: string | null;
  phone_number?: string | null;
  role: string;
  delegatable_permissions: string[];
  grantable_permissions: string[];
  delegated_grants: PermissionGrant[];
  effective_permissions: string[];
}

export default function VendorStaffPage() {
  const [rows, setRows] = useState<Member[]>([]);
  const [phone, setPhone] = useState("");
  const [fullName, setFullName] = useState("");
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const [permissionState, setPermissionState] = useState<LoadState>("ready");
  const [permissionDetail, setPermissionDetail] = useState<PermissionDetail | null>(null);
  const [permissionKey, setPermissionKey] = useState("");
  const [permissionReason, setPermissionReason] = useState("");

  const load = useCallback(async () => {
    setState("loading"); setError(null);
    try {
      const data = await getApi().get<unknown>("/api/v1/vendors/staff");
      setRows(itemsOf<Member>(data, "members"));
      setState("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "دریافت کارکنان ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  async function invite() {
    setBusy(true); setError(null);
    try {
      await getApi().post("/api/v1/vendors/staff/invite", { phone_number: phone.trim(), full_name: fullName.trim() });
      setPhone(""); setFullName(""); await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "دعوت کارمند ناموفق بود");
    } finally { setBusy(false); }
  }

  async function update(member: Member, action: "activate" | "suspend" | "revoke") {
    setBusy(true); setError(null);
    const status = action === "activate" ? "ACTIVE" : action === "suspend" ? "SUSPENDED" : "REVOKED";
    try {
      await getApi().patch(`/api/v1/vendors/staff/${member.membership_id}`, { status });
      await load();
      if (selected === member.membership_id && status !== "ACTIVE") {
        setPermissionDetail(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "تغییر دسترسی ناموفق بود");
    } finally { setBusy(false); }
  }

  async function loadPermissions(membershipId: string) {
    setSelected(membershipId);
    setPermissionState("loading");
    setError(null);
    try {
      const data = await getApi().get<PermissionDetail>(`/api/v1/vendors/staff/${membershipId}/permissions`);
      setPermissionDetail(data);
      setPermissionKey(data.grantable_permissions[0] ?? "");
      setPermissionState("ready");
    } catch (err) {
      setPermissionDetail(null);
      setPermissionState("error");
      setError(err instanceof Error ? err.message : "دریافت مجوزهای تفویضی ناموفق بود");
    }
  }

  async function grant() {
    if (!selected || !permissionKey.trim() || !permissionReason.trim()) return;
    setBusy(true); setError(null);
    try {
      await getApi().post(`/api/v1/vendors/staff/${selected}/permissions`, {
        permission_key: permissionKey,
        reason: permissionReason.trim(),
        client: "WEB",
      });
      setPermissionReason("");
      await loadPermissions(selected);
    } catch (err) {
      setError(err instanceof Error ? err.message : "اعطای مجوز ناموفق بود");
    } finally { setBusy(false); }
  }

  async function revoke(permission: string) {
    if (!selected || !permissionReason.trim()) return;
    setBusy(true); setError(null);
    try {
      await getApi().post(`/api/v1/vendors/staff/${selected}/permissions/${encodeURIComponent(permission)}/revoke`, {
        reason: permissionReason.trim(),
        client: "WEB",
      });
      setPermissionReason("");
      await loadPermissions(selected);
    } catch (err) {
      setError(err instanceof Error ? err.message : "لغو مجوز ناموفق بود");
    } finally { setBusy(false); }
  }

  if (state === "loading") return <div className="space-y-4" aria-busy="true"><Skeleton className="h-8 w-48" /><div className={cardCls}><Skeleton lines={6} /></div></div>;
  if (state === "error") return <ErrorState title="دریافت کارکنان ناموفق بود" description={error ?? undefined} onRetry={() => void load()} />;

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-baseline gap-3">
        <h1 className="text-[24px] leading-[32px] font-bold text-[var(--pol-light-text-primary)]">کارکنان و دسترسی</h1>
        <span className="text-[12px] text-[var(--pol-light-text-muted)]">V-11 · {rows.length.toLocaleString("fa-IR")} عضو</span>
        <Button variant="secondary" size="sm" className="ms-auto" onClick={() => void load()}>به‌روزرسانی</Button>
      </header>

      {error ? <div className="rounded-[12px] border border-[var(--pol-light-semantic-danger)]/40 bg-[var(--pol-light-surface-default)] p-3 text-[13px] text-[var(--pol-light-semantic-danger)]">{error}</div> : null}

      <section className={cardCls} aria-label="دعوت کارمند">
        <h2 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">دعوت کارمند</h2>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <Field label="شماره موبایل" value={phone} onChange={(e) => setPhone(e.target.value)} dir="ltr" placeholder="+9891..." />
          <Field label="نام و نام خانوادگی" value={fullName} onChange={(e) => setFullName(e.target.value)} />
        </div>
        <div className="mt-3"><Button loading={busy} disabled={!phone.trim() || !fullName.trim()} onClick={() => void invite()}>دعوت</Button></div>
      </section>

      <ul role="list" className="space-y-2">
        {rows.map((member) => (
          <li key={member.membership_id} className={cardCls}>
            <div className="flex flex-wrap items-center gap-2">
              <StatusChip tone={member.status === "ACTIVE" ? "success" : member.status === "SUSPENDED" ? "warning" : "neutral"}>{member.status}</StatusChip>
              <span className="font-semibold text-[var(--pol-light-text-primary)]">{member.full_name ?? "—"}</span>
              <span className="text-[12px] text-[var(--pol-light-text-muted)]">{member.role}</span>
              <span className="ms-auto text-[12px] text-[var(--pol-light-text-muted)]" dir="ltr">{member.phone_number ?? "—"}</span>
            </div>
            {member.role !== "VENDOR_OWNER" ? (
              <div className="mt-3 flex flex-wrap gap-2">
                {member.status !== "ACTIVE" ? <Button variant="secondary" size="sm" loading={busy} onClick={() => void update(member, "activate")}>فعال‌سازی</Button> : null}
                {member.status === "ACTIVE" ? <Button variant="secondary" size="sm" loading={busy} onClick={() => void update(member, "suspend")}>تعلیق</Button> : null}
                {member.status !== "REVOKED" ? <Button variant="danger" size="sm" loading={busy} onClick={() => void update(member, "revoke")}>لغو دسترسی</Button> : null}
                {member.status === "ACTIVE" ? <Button variant="secondary" size="sm" onClick={() => void loadPermissions(member.membership_id)}>مجوزهای تفویضی</Button> : null}
              </div>
            ) : null}

            {selected === member.membership_id && member.status === "ACTIVE" && permissionState !== "loading" ? (
              <section className="mt-4 border-t border-[var(--pol-light-border-subtle)] pt-4" aria-label="مجوزهای تفویضی">
                {permissionState === "error" ? (
                  <p className="text-[12px] text-[var(--pol-light-semantic-danger)]">دسترسی به Permission Editor برای نقش فعلی مجاز نیست.</p>
                ) : permissionDetail ? (
                  <>
                    <div className="mb-3 flex flex-wrap items-baseline gap-2">
                      <h3 className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">Effective Access</h3>
                      <span className="text-[11px] text-[var(--pol-light-text-muted)]">{permissionDetail.effective_permissions.length.toLocaleString("fa-IR")} مجوز مؤثر</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {permissionDetail.effective_permissions.map((permission) => (
                        <span key={permission} className="rounded-full border border-[var(--pol-light-border-subtle)] px-2.5 py-1 text-[11px] text-[var(--pol-light-text-secondary)]">{permission}</span>
                      ))}
                    </div>

                    <div className="mt-4 grid gap-3 md:grid-cols-[minmax(0,1fr)_minmax(0,2fr)_auto]">
                      <select
                        value={permissionKey}
                        onChange={(e) => setPermissionKey(e.target.value)}
                        className="rounded-[10px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] px-3 py-2 text-[12px]"
                        aria-label="مجوز قابل اعطا"
                      >
                        {permissionDetail.grantable_permissions
                          .filter((permission) => !permissionDetail.delegated_grants.some((g) => g.permission_key === permission && g.status === "GRANTED"))
                          .map((permission) => <option key={permission} value={permission}>{permission}</option>)}
                      </select>
                      <Field label="دلیل" value={permissionReason} onChange={(e) => setPermissionReason(e.target.value)} />
                      <Button loading={busy} disabled={!permissionKey || !permissionReason.trim()} onClick={() => void grant()}>اعطای مجوز</Button>
                    </div>

                    <div className="mt-4 space-y-2">
                      {permissionDetail.delegated_grants.map((grant) => (
                        <div key={grant.id} className="flex flex-wrap items-center gap-2 rounded-[10px] border border-[var(--pol-light-border-subtle)] px-3 py-2">
                          <StatusChip tone={grant.status === "GRANTED" ? "success" : "neutral"}>{grant.status}</StatusChip>
                          <span className="text-[12px] text-[var(--pol-light-text-primary)]">{grant.permission_key}</span>
                          {grant.status === "GRANTED" ? (
                            <Button variant="danger" size="sm" className="ms-auto" loading={busy} disabled={!permissionReason.trim()} onClick={() => void revoke(grant.permission_key)}>لغو</Button>
                          ) : null}
                        </div>
                      ))}
                    </div>
                  </>
                ) : null}
              </section>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  );
}
