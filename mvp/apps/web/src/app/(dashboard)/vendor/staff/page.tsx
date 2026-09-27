"use client";

import { useCallback, useEffect, useState } from "react";
import { Button, Card, ErrorState, Field, Skeleton, StatusChip } from "@pol/ui";
import { getApi } from "@/lib/auth/api";
import { inputCls, itemsOf, type LoadState } from "../_shared";

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
    setState("loading");
    setError(null);
    try {
      const data = await getApi().get<unknown>("/api/v1/vendors/staff");
      setRows(itemsOf<Member>(data, "members"));
      setState("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "دریافت کارکنان ناموفق بود");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function invite() {
    setBusy(true);
    setError(null);
    try {
      await getApi().post("/api/v1/vendors/staff/invite", {
        phone_number: phone.trim(),
        full_name: fullName.trim(),
      });
      setPhone("");
      setFullName("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "دعوت کارمند ناموفق بود");
    } finally {
      setBusy(false);
    }
  }

  async function update(member: Member, action: "activate" | "suspend" | "revoke") {
    setBusy(true);
    setError(null);
    const status = action === "activate" ? "ACTIVE" : action === "suspend" ? "SUSPENDED" : "REVOKED";
    try {
      await getApi().patch(`/api/v1/vendors/staff/${member.membership_id}`, { status });
      await load();
      if (selected === member.membership_id && status !== "ACTIVE") {
        setPermissionDetail(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "تغییر دسترسی ناموفق بود");
    } finally {
      setBusy(false);
    }
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
    setBusy(true);
    setError(null);
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
    } finally {
      setBusy(false);
    }
  }

  async function revoke(permission: string) {
    if (!selected || !permissionReason.trim()) return;
    setBusy(true);
    setError(null);
    try {
      await getApi().post(
        `/api/v1/vendors/staff/${selected}/permissions/${encodeURIComponent(permission)}/revoke`,
        {
          reason: permissionReason.trim(),
          client: "WEB",
        },
      );
      setPermissionReason("");
      await loadPermissions(selected);
    } catch (err) {
      setError(err instanceof Error ? err.message : "لغو مجوز ناموفق بود");
    } finally {
      setBusy(false);
    }
  }

  if (state === "loading") {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="در حال بارگذاری کارکنان">
        <Skeleton className="h-9 w-48" />
        <Card className="p-6">
          <Skeleton lines={4} />
        </Card>
      </div>
    );
  }

  if (state === "error") {
    return (
      <ErrorState
        title="دریافت کارکنان ناموفق بود"
        description={error ?? undefined}
        onRetry={() => void load()}
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
              مدیریت پرسنل و دسترسی‌ها
            </h1>
            <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2.5 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
              V-11 · {rows.length.toLocaleString("fa-IR")} همکار
            </span>
          </div>
          <p className="mt-1 text-[13px] text-[var(--pol-light-text-secondary)]">
            تعریف دسترسی برای متصدیان فروش و اپراتورهای انبار بنکداری
          </p>
        </div>

        <Button variant="secondary" size="sm" onClick={() => void load()}>
          به‌روزرسانی
        </Button>
      </header>

      {error && (
        <ErrorState title="خطا در عملیات پرسنل" description={error} />
      )}

      {/* Invite Member Card */}
      <Card className="p-5">
        <h2 className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
          دعوت و ثبت دسترسی همکار جدید
        </h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <Field
            label="شماره تلفن همراه"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            dir="ltr"
            placeholder="0912..."
            hint="پیامک دعوت به این شماره ارسال خواهد شد"
          />
          <Field
            label="نام و نام خانوادگی"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="نام کارمند یا متصدی"
          />
        </div>
        <div className="mt-4 flex justify-end">
          <Button
            loading={busy}
            disabled={!phone.trim() || !fullName.trim()}
            onClick={() => void invite()}
          >
            ارسال دعوت‌نامه عضویت
          </Button>
        </div>
      </Card>

      {/* Staff Members List */}
      <div className="space-y-3">
        <h2 className="text-[17px] font-bold text-[var(--pol-light-text-primary)]">
          فهرست پرسنل بنکداری
        </h2>

        <div className="grid gap-3">
          {rows.map((member) => (
            <Card key={member.membership_id} className="p-5">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex flex-wrap items-center gap-2.5">
                  <StatusChip
                    tone={
                      member.status === "ACTIVE"
                        ? "success"
                        : member.status === "SUSPENDED"
                          ? "warning"
                          : "neutral"
                    }
                  >
                    {member.status === "ACTIVE"
                      ? "فعال"
                      : member.status === "SUSPENDED"
                        ? "معلق"
                        : member.status === "INVITED"
                          ? "دعوت‌شده"
                          : "لغوشده"}
                  </StatusChip>
                  <span className="text-[15px] font-bold text-[var(--pol-light-text-primary)]">
                    {member.full_name ?? "همکار بدون نام"}
                  </span>
                  <span className="rounded-full bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 text-[11px] font-medium text-[var(--pol-light-text-secondary)]">
                    {member.role === "VENDOR_OWNER" ? "مدیر ارشد (Owner)" : "کارمند فروشگاه (Staff)"}
                  </span>
                </div>

                <div className="flex items-center gap-3 text-[13px] font-mono text-[var(--pol-light-text-secondary)]" dir="ltr">
                  {member.phone_number ?? "—"}
                </div>
              </div>

              {member.role !== "VENDOR_OWNER" && (
                <div className="mt-4 flex flex-wrap gap-2 border-t border-[var(--pol-light-border-subtle)] pt-3">
                  {member.status !== "ACTIVE" && (
                    <Button variant="secondary" size="sm" loading={busy} onClick={() => void update(member, "activate")}>
                      فعال‌سازی
                    </Button>
                  )}
                  {member.status === "ACTIVE" && (
                    <Button variant="secondary" size="sm" loading={busy} onClick={() => void update(member, "suspend")}>
                      تعلیق موقت
                    </Button>
                  )}
                  {member.status !== "REVOKED" && (
                    <Button variant="outline" size="sm" loading={busy} onClick={() => void update(member, "revoke")}>
                      لغو دسترسی
                    </Button>
                  )}
                  {member.status === "ACTIVE" && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => void loadPermissions(member.membership_id)}
                    >
                      {selected === member.membership_id ? "بستن مجوزها" : "تنظیم مجوزهای تفویضی"}
                    </Button>
                  )}
                </div>
              )}

              {/* Permissions Section */}
              {selected === member.membership_id && member.status === "ACTIVE" && (
                <section className="mt-4 border-t border-[var(--pol-light-border-subtle)] pt-4 space-y-4" aria-label="مجوزهای تفویضی">
                  {permissionState === "loading" ? (
                    <Skeleton lines={3} />
                  ) : permissionState === "error" ? (
                    <p className="text-[12px] text-rose-600 dark:text-rose-400">
                      دسترسی به بخش مدیریت مجوزها برای نقش فعلی شما مجاز نیست.
                    </p>
                  ) : permissionDetail ? (
                    <>
                      <div>
                        <div className="flex items-center justify-between">
                          <h3 className="text-[14px] font-bold text-[var(--pol-light-text-primary)]">
                            دسترسی‌های مؤثر (Effective Access)
                          </h3>
                          <span className="text-[11px] text-[var(--pol-light-text-muted)]">
                            {permissionDetail.effective_permissions.length.toLocaleString("fa-IR")} مجوز
                          </span>
                        </div>
                        <div className="mt-2 flex flex-wrap gap-1.5">
                          {permissionDetail.effective_permissions.map((p) => (
                            <span
                              key={p}
                              className="rounded-md border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] px-2 py-0.5 font-mono text-[11px] text-[var(--pol-light-text-secondary)]"
                            >
                              {p}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Grant Form */}
                      <div className="rounded-xl border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-3.5 space-y-3">
                        <h4 className="text-[13px] font-bold text-[var(--pol-light-text-primary)]">
                          اعطای دسترسی جدید
                        </h4>
                        <div className="grid gap-3 md:grid-cols-[minmax(0,1.2fr)_minmax(0,2fr)_auto]">
                          <select
                            value={permissionKey}
                            onChange={(e) => setPermissionKey(e.target.value)}
                            className="h-10 rounded-lg border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] px-3 text-[12px] text-[var(--pol-light-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]"
                            aria-label="مجوز قابل اعطا"
                          >
                            {permissionDetail.grantable_permissions
                              .filter((p) => !permissionDetail.delegated_grants.some((g) => g.permission_key === p && g.status === "GRANTED"))
                              .map((p) => (
                                <option key={p} value={p}>
                                  {p}
                                </option>
                              ))}
                          </select>
                          <Field
                            label="دلیل اعطا"
                            value={permissionReason}
                            onChange={(e) => setPermissionReason(e.target.value)}
                            placeholder="علت تفویض مجوز..."
                          />
                          <div className="flex items-end">
                            <Button
                              loading={busy}
                              disabled={!permissionKey || !permissionReason.trim()}
                              onClick={() => void grant()}
                            >
                              اعطای مجوز
                            </Button>
                          </div>
                        </div>
                      </div>

                      {/* Delegated Grants */}
                      {permissionDetail.delegated_grants.length > 0 && (
                        <div className="space-y-2">
                          <h4 className="text-[13px] font-bold text-[var(--pol-light-text-primary)]">
                            مجوزهای تفویض‌شده مستقیم
                          </h4>
                          <div className="space-y-1.5">
                            {permissionDetail.delegated_grants.map((grant) => (
                              <div
                                key={grant.id}
                                className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] px-3 py-2"
                              >
                                <div className="flex items-center gap-2">
                                  <StatusChip tone={grant.status === "GRANTED" ? "success" : "neutral"}>
                                    {grant.status}
                                  </StatusChip>
                                  <span className="font-mono text-[12px] text-[var(--pol-light-text-primary)]">
                                    {grant.permission_key}
                                  </span>
                                </div>
                                {grant.status === "GRANTED" && (
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    loading={busy}
                                    disabled={!permissionReason.trim()}
                                    onClick={() => void revoke(grant.permission_key)}
                                  >
                                    لغو مجوز
                                  </Button>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : null}
                </section>
              )}
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
