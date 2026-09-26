import React, { useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text } from "react-native";
import { api } from "../api";
import { Btn, Card, Empty, ErrorBox, Screen, StatusChip, Title } from "../components/ui";
import type { Role } from "../types";
import { spacing, useThemedStyles, type Palette } from "../theme";
import { SupportMobileScreen } from "./SupportMobileScreen";

type Dash = {
  delivery_exceptions?: { open_count?: number; escalated_count?: number; total?: number };
  disputes?: { open_disputes?: number; total?: number };
  support_cases?: { open_cases?: number; total?: number };
};
type Order = { id: string; order_number?: string | null; order_status?: string | null; total_amount_toman?: number | string | null };
type Recon = { id: string; status?: string | null; expected_amount_toman?: number | string | null; observed_amount_toman?: number | string | null };
type Audit = { id: string; action?: string | null; resource_type?: string | null; actor_user_id?: string | null; created_at?: string | null };
type Candidate = {
  candidate_id: string;
  vendor_name?: string | null;
  proposed_title?: string | null;
  proposed_brand?: string | null;
  barcode?: string | null;
  vendor_sku?: string | null;
  status?: string | null;
  created_at?: string | null;
};
type AdminUser = {
  id: string;
  phone_number?: string | null;
  full_name?: string | null;
  role?: string | null;
  is_active?: boolean;
  membership_count?: number;
};
type AdminOrg = {
  id: string;
  name?: string | null;
  org_type?: string | null;
  status?: string | null;
  membership_count?: number;
};
type Analytics = {
  start_date?: string;
  end_date?: string;
  kpis?: Record<string, unknown>;
};

function list<T>(data: unknown, keys: string[]): T[] {
  if (Array.isArray(data)) return data as T[];
  if (!data || typeof data !== "object") return [];
  const o = data as Record<string, unknown>;
  for (const k of keys) if (Array.isArray(o[k])) return o[k] as T[];
  return [];
}
function money(v: number | string | null | undefined): string {
  const n = Number(v);
  return Number.isFinite(n) ? n.toLocaleString("fa-IR") + " تومان" : "—";
}
function dateKey(date: Date): string {
  return date.toISOString().slice(0, 10);
}
function recentStart(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return dateKey(d);
}
function prettyKpi(key: string): string {
  return key
    .replaceAll("_", " ")
    .replace(/\b\w/g, (x) => x.toUpperCase());
}

export function OpsMobileScreen(props: { role: Extract<Role, "OPS_AGENT" | "ADMIN_SUPER"> }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const [tab, setTab] = useState<
    "overview" | "recon" | "analytics" | "risk" | "candidates" | "users" | "organizations" | "audit" | "support" | "notifications"
  >("overview");
  const [dash, setDash] = useState<Dash | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [recon, setRecon] = useState<Recon[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [organizations, setOrganizations] = useState<AdminOrg[]>([]);
  const [audit, setAudit] = useState<Audit[]>([]);
  const [notifications, setNotifications] = useState<Array<{ id: string; title?: string | null; body?: string | null; priority?: string | null; created_at?: string | null }>>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadOverview(): Promise<void> {
    const [d, o] = await Promise.all([
      api.get<Dash>("/api/v1/admin/exceptions/dashboard"),
      api.get<unknown>("/api/v1/orders?limit=20&offset=0"),
    ]);
    setDash(d);
    setOrders(list<Order>(o, ["orders", "items"]));
  }
  async function loadRecon(): Promise<void> {
    const d = await api.get<unknown>("/api/v1/finance/reconciliation?limit=50&offset=0");
    setRecon(list<Recon>(d, ["cases", "items"]));
  }
  async function loadAnalytics(): Promise<void> {
    const d = await api.get<Analytics>(
      "/api/v1/ops/analytics?start_date=" + recentStart(7) + "&end_date=" + dateKey(new Date()),
    );
    setAnalytics(d);
  }
  async function loadRisk(): Promise<void> {
    const d = await api.get<Dash>("/api/v1/admin/exceptions/dashboard");
    setDash(d);
    const r = await api.get<unknown>("/api/v1/finance/reconciliation?status=OPEN&limit=10&offset=0");
    setRecon(list<Recon>(r, ["cases", "items"]));
  }
  async function loadCandidates(): Promise<void> {
    const d = await api.get<unknown>("/api/v1/admin/product-candidates?status=PENDING_REVIEW&limit=50&offset=0");
    setCandidates(list<Candidate>(d, ["candidates", "items"]));
  }
  async function loadUsers(): Promise<void> {
    const d = await api.get<unknown>("/api/v1/admin/users?limit=50&offset=0");
    setUsers(list<AdminUser>(d, ["users", "items"]));
  }
  async function loadOrganizations(): Promise<void> {
    const d = await api.get<unknown>("/api/v1/admin/organizations?limit=50&offset=0");
    setOrganizations(list<AdminOrg>(d, ["organizations", "items"]));
  }
  async function loadNotifications(): Promise<void> {
    const d = await api.get<unknown>("/api/v1/notifications?limit=50&offset=0");
    setNotifications(list(d, ["items", "notifications", "data", "results"]));
  }
  async function loadAudit(): Promise<void> {
    const d = await api.get<unknown>("/api/v1/admin/audit-logs");
    setAudit(list<Audit>(d, ["logs", "items"]));
  }
  async function reviewCandidate(candidateId: string): Promise<void> {
    try {
      setError(null);
      await api.patch("/api/v1/admin/product-candidates/" + candidateId, {
        action: "REJECT",
        reason: "بررسی و رد از پنل موبایل",
      });
      await loadCandidates();
    } catch (e) {
      setError(e instanceof Error ? e.message : "بازبینی کاندید ناموفق بود");
    }
  }
  async function updateUser(userId: string, isActive: boolean): Promise<void> {
    try {
      setError(null);
      await api.patch("/api/v1/admin/users/" + userId + "/status", { is_active: isActive });
      await loadUsers();
    } catch (e) {
      setError(e instanceof Error ? e.message : "تغییر وضعیت کاربر ناموفق بود");
    }
  }
  async function updateOrganization(organizationId: string, status: "ACTIVE" | "SUSPENDED"): Promise<void> {
    try {
      setError(null);
      await api.patch("/api/v1/admin/organizations/" + organizationId + "/status", { status });
      await loadOrganizations();
    } catch (e) {
      setError(e instanceof Error ? e.message : "تغییر وضعیت سازمان ناموفق بود");
    }
  }

  useEffect(() => {
    setError(null);
    const task =
      tab === "overview"
        ? loadOverview()
        : tab === "recon"
          ? loadRecon()
          : tab === "analytics"
            ? loadAnalytics()
            : tab === "risk"
              ? loadRisk()
              : tab === "candidates"
                ? loadCandidates()
                : tab === "users"
                  ? loadUsers()
                  : tab === "organizations"
                    ? loadOrganizations()
                    : tab === "audit"
                      ? loadAudit()
                      : tab === "notifications"
                        ? loadNotifications()
                        : Promise.resolve();
    void task.catch((e) => setError(e instanceof Error ? e.message : "بارگذاری ناموفق بود"));
  }, [tab]);

  return (
    <Screen>
      <Title badge={props.role}>موبایل عملیات</Title>
      <ScrollView>
        <Text style={styles.note}>
          این سطح موبایل برای قابلیت‌های عملیاتی موجود API است؛ همه business ruleها در backend canonical باقی می‌مانند.
        </Text>
        <Btn label="نمای کلی" onPress={() => setTab("overview")} tone={tab === "overview" ? "primary" : "ghost"} />
        <Btn label="تطبیق مالی" onPress={() => setTab("recon")} tone={tab === "recon" ? "primary" : "ghost"} />
        <Btn label="تحلیل" onPress={() => setTab("analytics")} tone={tab === "analytics" ? "primary" : "ghost"} />
        <Btn label="ریسک" onPress={() => setTab("risk")} tone={tab === "risk" ? "primary" : "ghost"} />
        <Btn label="کاندیدهای کاتالوگ" onPress={() => setTab("candidates")} tone={tab === "candidates" ? "primary" : "ghost"} />
        {props.role === "ADMIN_SUPER" ? (
          <>
            <Btn label="کاربران" onPress={() => setTab("users")} tone={tab === "users" ? "primary" : "ghost"} />
            <Btn label="سازمان‌ها" onPress={() => setTab("organizations")} tone={tab === "organizations" ? "primary" : "ghost"} />
            <Btn label="لاگ ممیزی" onPress={() => setTab("audit")} tone={tab === "audit" ? "primary" : "ghost"} />
          </>
        ) : null}
        <Btn label="پشتیبانی" onPress={() => setTab("support")} tone={tab === "support" ? "primary" : "ghost"} />
        <Btn label="اعلان‌ها" onPress={() => setTab("notifications")} tone={tab === "notifications" ? "primary" : "ghost"} />
        <ErrorBox message={error} />

        {tab === "support" ? (
          <SupportMobileScreen role={props.role} />
        ) : tab === "notifications" ? (
          <ScrollView>
            {notifications.length === 0 ? (
              <Empty title="اعلانی نیست" />
            ) : (
              notifications.map((n) => (
                <Card key={n.id}>
                  <StatusChip label={n.priority || "NORMAL"} tone="info" />
                  <Text style={styles.h2}>{n.title || "اعلان"}</Text>
                  <Text style={styles.meta}>{n.body || "—"}</Text>
                  <Text style={styles.meta}>{n.created_at || "—"}</Text>
                </Card>
              ))
            )}
          </ScrollView>
        ) : tab === "overview" ? (
          <>
            <Card>
              <Text style={styles.h2}>O-01 استثناها</Text>
              <Text style={styles.metric}>{String(dash?.delivery_exceptions?.open_count ?? 0)}</Text>
              <Text style={styles.meta}>تحویل باز · ارتقا {String(dash?.delivery_exceptions?.escalated_count ?? 0)}</Text>
              <Text style={styles.metric}>{String(dash?.disputes?.open_disputes ?? 0)}</Text>
              <Text style={styles.meta}>اختلاف باز</Text>
              <Text style={styles.metric}>{String(dash?.support_cases?.open_cases ?? 0)}</Text>
              <Text style={styles.meta}>پرونده پشتیبانی باز</Text>
            </Card>
            {orders.length === 0 ? (
              <Empty title="صف سفارش خالی است" />
            ) : (
              orders.slice(0, 10).map((o) => (
                <Card key={o.id}>
                  <StatusChip label={o.order_status || "—"} tone="info" />
                  <Text style={styles.h2}>{o.order_number || o.id}</Text>
                  <Text style={styles.metric}>{money(o.total_amount_toman)}</Text>
                </Card>
              ))
            )}
          </>
        ) : tab === "recon" || tab === "risk" ? (
          <>
            {tab === "risk" ? (
              <Card>
                <Text style={styles.h2}>سیگنال‌های ریسک واقعی</Text>
                <Text style={styles.meta}>
                  تحویل باز: {String(dash?.delivery_exceptions?.open_count ?? 0)} · ارتقا: {String(dash?.delivery_exceptions?.escalated_count ?? 0)}
                </Text>
                <Text style={styles.meta}>اختلاف باز: {String(dash?.disputes?.open_disputes ?? 0)}</Text>
                <Text style={styles.meta}>پشتیبانی باز: {String(dash?.support_cases?.open_cases ?? 0)}</Text>
              </Card>
            ) : null}
            {recon.length === 0 ? (
              <Empty title={tab === "risk" ? "مورد باز شناسایی نشد" : "مغایرتی نیست"} />
            ) : (
              recon.map((r) => (
                <Card key={r.id}>
                  <StatusChip label={r.status || "OPEN"} tone={r.status === "MISMATCH" ? "warn" : "info"} />
                  <Text style={styles.metric}>{money(r.expected_amount_toman)}</Text>
                  <Text style={styles.meta}>مشاهده: {money(r.observed_amount_toman)}</Text>
                </Card>
              ))
            )}
          </>
        ) : tab === "analytics" ? (
          <Card>
            <Text style={styles.h2}>تحلیل ۷ روز اخیر</Text>
            <Text style={styles.meta}>
              {analytics?.start_date || recentStart(7)} تا {analytics?.end_date || dateKey(new Date())}
            </Text>
            {analytics?.kpis && Object.keys(analytics.kpis).length > 0 ? (
              Object.entries(analytics.kpis).map(([key, value]) => (
                <Card key={key}>
                  <Text style={styles.h2}>{prettyKpi(key)}</Text>
                  <Text style={styles.metric}>{String(value ?? "—")}</Text>
                </Card>
              ))
            ) : (
              <Empty title="شاخصی برنگشت" description="بازه فعلی داده عملیاتی قابل‌محاسبه‌ای ندارد." />
            )}
          </Card>
        ) : tab === "candidates" ? (
          candidates.length === 0 ? (
            <Empty title="کاندید معلقی نیست" />
          ) : (
            candidates.map((c) => (
              <Card key={c.candidate_id}>
                <StatusChip label={c.status || "PENDING_REVIEW"} tone="warn" />
                <Text style={styles.h2}>{c.proposed_title || "بدون عنوان"}</Text>
                <Text style={styles.meta}>فروشنده: {c.vendor_name || "—"}</Text>
                <Text style={styles.meta}>SKU: {c.vendor_sku || "—"} · بارکد: {c.barcode || "—"}</Text>
                <Text style={styles.meta}>ایجاد: {c.created_at || "—"}</Text>
                <Btn label="رد کاندید" tone="ghost" onPress={() => void reviewCandidate(c.candidate_id)} />
              </Card>
            ))
          )
        ) : tab === "users" ? (
          users.length === 0 ? (
            <Empty title="کاربری نیست" />
          ) : (
            users.map((u) => (
              <Card key={u.id}>
                <StatusChip label={u.is_active ? "ACTIVE" : "INACTIVE"} tone={u.is_active ? "ok" : "warn"} />
                <Text style={styles.h2}>{u.full_name || u.phone_number || u.id}</Text>
                <Text style={styles.meta}>نقش: {u.role || "—"} · عضویت‌ها: {String(u.membership_count ?? 0)}</Text>
                <Btn
                  label={u.is_active ? "غیرفعال کردن" : "فعال کردن"}
                  tone="ghost"
                  onPress={() => void updateUser(u.id, !u.is_active)}
                />
              </Card>
            ))
          )
        ) : tab === "organizations" ? (
          organizations.length === 0 ? (
            <Empty title="سازمانی نیست" />
          ) : (
            organizations.map((o) => (
              <Card key={o.id}>
                <StatusChip label={o.status || "—"} tone={o.status === "ACTIVE" ? "ok" : "info"} />
                <Text style={styles.h2}>{o.name || o.id}</Text>
                <Text style={styles.meta}>نوع: {o.org_type || "—"} · عضویت‌ها: {String(o.membership_count ?? 0)}</Text>
                <Btn
                  label={o.status === "ACTIVE" ? "تعلیق سازمان" : "فعال‌سازی سازمان"}
                  tone="ghost"
                  onPress={() => void updateOrganization(o.id, o.status === "ACTIVE" ? "SUSPENDED" : "ACTIVE")}
                />
              </Card>
            ))
          )
        ) : (
          audit.length === 0 ? (
            <Empty title="لاگ ممیزی نیست" />
          ) : (
            audit.map((a) => (
              <Card key={a.id}>
                <Text style={styles.h2}>{a.action || "—"}</Text>
                <Text style={styles.meta}>{a.resource_type || "—"}</Text>
                <Text style={styles.meta}>{a.actor_user_id || "—"}</Text>
                <Text style={styles.meta}>{a.created_at || "—"}</Text>
              </Card>
            ))
          )
        )}
      </ScrollView>
    </Screen>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
    note: { color: colors.textSecondary, fontSize: 12, lineHeight: 18, marginBottom: spacing.md },
    h2: { color: colors.text, fontSize: 15, fontWeight: "700", marginBottom: 4 },
    meta: { color: colors.textSecondary, fontSize: 11, lineHeight: 18 },
    metric: { color: colors.text, fontSize: 20, fontWeight: "700", marginVertical: spacing.sm },
  });
}
