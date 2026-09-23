import React, { useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text } from "react-native";
import { api } from "../api";
import { Btn, Card, Empty, ErrorBox, Screen, StatusChip, Title } from "../components/ui";
import type { Role } from "../types";
import { colors, spacing } from "../theme";

type Dash = { delivery_exceptions?: { open_count?: number; escalated_count?: number }; disputes?: { open_disputes?: number }; support_cases?: { open_cases?: number } };
type Order = { id: string; order_number?: string | null; order_status?: string | null; total_amount_toman?: number | string | null };
type Recon = { id: string; status?: string | null; expected_amount_toman?: number | string | null; observed_amount_toman?: number | string | null };
type Audit = { id: string; action?: string | null; resource_type?: string | null; actor_user_id?: string | null; created_at?: string | null };

function list<T>(data: unknown, keys: string[]): T[] {
  if (Array.isArray(data)) return data as T[];
  if (!data || typeof data !== "object") return [];
  const o = data as Record<string, unknown>;
  for (const k of keys) if (Array.isArray(o[k])) return o[k] as T[];
  return [];
}
function money(v: number | string | null | undefined): string { const n = Number(v); return Number.isFinite(n) ? n.toLocaleString("fa-IR") + " تومان" : "—"; }

export function OpsMobileScreen(props: { role: Extract<Role, "OPS_AGENT" | "ADMIN_SUPER"> }): React.ReactNode {
  const [tab, setTab] = useState<"overview" | "recon" | "audit">("overview");
  const [dash, setDash] = useState<Dash | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [recon, setRecon] = useState<Recon[]>([]);
  const [audit, setAudit] = useState<Audit[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadOverview(): Promise<void> {
    const [d, o] = await Promise.all([
      api.get<Dash>("/api/v1/admin/exceptions/dashboard"),
      api.get<unknown>("/api/v1/orders?limit=20&offset=0"),
    ]);
    setDash(d); setOrders(list<Order>(o, ["orders", "items"]));
  }
  async function loadRecon(): Promise<void> {
    const d = await api.get<unknown>("/api/v1/finance/reconciliation?limit=50&offset=0");
    setRecon(list<Recon>(d, ["cases", "items"]));
  }
  async function loadAudit(): Promise<void> {
    const d = await api.get<unknown>("/api/v1/admin/audit-logs");
    setAudit(list<Audit>(d, ["logs", "items"]));
  }
  useEffect(() => {
    setError(null);
    void (tab === "overview" ? loadOverview() : tab === "recon" ? loadRecon() : loadAudit()).catch((e) => setError(e instanceof Error ? e.message : "بارگذاری ناموفق بود"));
  }, [tab]);

  return (
    <Screen>
      <Title badge={props.role}>موبایل عملیات</Title>
      <ScrollView>
        <Text style={styles.note}>این سطح موبایل برای قابلیت‌های عملیاتی موجود API است؛ هیچ business rule در کلاینت اجرا نمی‌شود.</Text>
        <Btn label="نمای کلی" onPress={() => setTab("overview")} tone={tab === "overview" ? "primary" : "ghost"} />
        <Btn label="تطبیق مالی" onPress={() => setTab("recon")} tone={tab === "recon" ? "primary" : "ghost"} />
        {props.role === "ADMIN_SUPER" ? <Btn label="لاگ ممیزی" onPress={() => setTab("audit")} tone={tab === "audit" ? "primary" : "ghost"} /> : null}
        <ErrorBox message={error} />
        {tab === "overview" ? (
          <>
            <Card><Text style={styles.h2}>O-01 استثناها</Text><Text style={styles.metric}>{String(dash?.delivery_exceptions?.open_count ?? 0)}</Text><Text style={styles.meta}>تحویل باز · ارتقا {String(dash?.delivery_exceptions?.escalated_count ?? 0)}</Text><Text style={styles.metric}>{String(dash?.disputes?.open_disputes ?? 0)}</Text><Text style={styles.meta}>اختلاف باز</Text><Text style={styles.metric}>{String(dash?.support_cases?.open_cases ?? 0)}</Text><Text style={styles.meta}>پرونده پشتیبانی باز</Text></Card>
            {orders.length === 0 ? <Empty title="صف سفارش خالی است" /> : orders.slice(0, 10).map((o) => <Card key={o.id}><StatusChip label={o.order_status || "—"} tone="info" /><Text style={styles.h2}>{o.order_number || o.id}</Text><Text style={styles.metric}>{money(o.total_amount_toman)}</Text></Card>)}
          </>
        ) : tab === "recon" ? (
          recon.length === 0 ? <Empty title="مغایرتی نیست" /> : recon.map((r) => <Card key={r.id}><StatusChip label={r.status || "—"} tone={r.status === "MISMATCH" ? "warn" : "info"} /><Text style={styles.metric}>{money(r.expected_amount_toman)}</Text><Text style={styles.meta}>مشاهده: {money(r.observed_amount_toman)}</Text></Card>)
        ) : (
          audit.length === 0 ? <Empty title="لاگ ممیزی نیست" /> : audit.map((a) => <Card key={a.id}><Text style={styles.h2}>{a.action || "—"}</Text><Text style={styles.meta}>{a.resource_type || "—"}</Text><Text style={styles.meta}>{a.actor_user_id || "—"}</Text><Text style={styles.meta}>{a.created_at || "—"}</Text></Card>)
        )}
      </ScrollView>
    </Screen>
  );
}
const styles = StyleSheet.create({
  note: { color: colors.textSecondary, fontSize: 12, lineHeight: 18, marginBottom: spacing.md },
  h2: { color: colors.text, fontSize: 15, fontWeight: "700", marginBottom: 4 },
  meta: { color: colors.textSecondary, fontSize: 11, lineHeight: 18 },
  metric: { color: colors.text, fontSize: 20, fontWeight: "700", marginVertical: spacing.sm },
});
