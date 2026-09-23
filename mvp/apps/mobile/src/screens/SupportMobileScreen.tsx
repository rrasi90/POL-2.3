import React, { useCallback, useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { api } from "../api";
import { Btn, Card, Empty, ErrorBox, Input, Screen, StatusChip, Title } from "../components/ui";
import type { Role } from "../types";
import { colors, spacing } from "../theme";

type CaseRow = {
  id: string;
  case_number?: string | null;
  case_type?: string | null;
  subject?: string | null;
  related_order_id?: string | null;
  priority?: string | null;
  status?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  resolution_note?: string | null;
};
type Message = { id: string; message_text?: string | null; created_at?: string | null; sender_role?: string | null };

function rows<T>(data: unknown): T[] {
  if (Array.isArray(data)) return data as T[];
  if (!data || typeof data !== "object") return [];
  const o = data as Record<string, unknown>;
  for (const k of ["cases", "items", "data", "results"]) {
    if (Array.isArray(o[k])) return o[k] as T[];
  }
  return [];
}

export function SupportMobileScreen(props: { role: Role; onBack?: () => void }): React.ReactNode {
  const [cases, setCases] = useState<CaseRow[]>([]);
  const [selected, setSelected] = useState<CaseRow | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [relatedOrderId, setRelatedOrderId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadCases = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const data = await api.get<unknown>("/api/v1/support/cases");
      setCases(rows<CaseRow>(data));
    } catch (e) { setError(e instanceof Error ? e.message : "دریافت پرونده‌ها ناموفق بود"); }
    finally { setLoading(false); }
  }, []);

  const loadCase = useCallback(async (id: string) => {
    setLoading(true); setError(null);
    try {
      const data = await api.get<CaseRow>("/api/v1/support/cases/" + id);
      setSelected(data);
      setMessages([]);
    } catch (e) { setError(e instanceof Error ? e.message : "دریافت پرونده ناموفق بود"); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { void loadCases(); }, [loadCases]);

  async function createCase(): Promise<void> {
    if (!subject.trim()) { setError("موضوع پرونده الزامی است."); return; }
    setLoading(true); setError(null);
    try {
      const body: Record<string, string> = { subject: subject.trim(), case_type: "GENERAL", priority: "NORMAL" };
      if (relatedOrderId.trim()) body.related_order_id = relatedOrderId.trim();
      const created = await api.post<CaseRow>("/api/v1/support/cases", body);
      setSubject(""); setRelatedOrderId(""); setSelected(created);
      await loadCases();
    } catch (e) { setError(e instanceof Error ? e.message : "ایجاد پرونده ناموفق بود"); }
    finally { setLoading(false); }
  }

  async function sendMessage(): Promise<void> {
    if (!selected || !message.trim()) return;
    setLoading(true); setError(null);
    try {
      const created = await api.post<Message>("/api/v1/support/cases/" + selected.id + "/messages", {
        message_text: message.trim(),
      });
      setMessages((prev) => prev.concat(created));
      setMessage("");
    } catch (e) { setError(e instanceof Error ? e.message : "ارسال پیام ناموفق بود"); }
    finally { setLoading(false); }
  }

  if (selected) {
    return (
      <Screen>
        <ScrollView>
          <Title badge={props.role}>پشتیبانی · جزئیات</Title>
          {props.onBack ? <Btn label="بازگشت" tone="ghost" onPress={() => { setSelected(null); props.onBack?.(); }} /> : null}
          <ErrorBox message={error} />
          <Card>
            <StatusChip label={selected.status || "—"} tone={selected.status === "RESOLVED" ? "ok" : "info"} />
            <Text style={styles.h2}>{selected.subject || "بدون موضوع"}</Text>
            <Text style={styles.meta}>{selected.case_number || selected.id}</Text>
            <Text style={styles.meta}>{selected.priority || "NORMAL"} · {selected.case_type || "GENERAL"}</Text>
            {selected.related_order_id ? <Text style={styles.meta}>Order: {selected.related_order_id}</Text> : null}
          </Card>
          <Card>
            <Text style={styles.h2}>پیام جدید</Text>
            <Input label="متن پیام" value={message} onChangeText={setMessage} multiline numberOfLines={4} maxLength={5000} />
            <Btn label="ارسال پیام" onPress={() => void sendMessage()} loading={loading} disabled={!message.trim() || loading} />
          </Card>
          <Card>
            <Text style={styles.h2}>پیام‌های این نشست</Text>
            {messages.length === 0 ? <Empty title="پیامی در این نشست نیست" description="API فعلی GET برای فهرست پیام‌ها ندارد." /> : messages.map((m) => (
              <View key={m.id} style={styles.message}>
                <Text style={styles.body}>{m.message_text || "—"}</Text>
                <Text style={styles.meta}>{m.sender_role || "—"} · {m.created_at || "—"}</Text>
              </View>
            ))}
          </Card>
        </ScrollView>
      </Screen>
    );
  }

  return (
    <Screen>
      <ScrollView>
        <Title badge={props.role}>پشتیبانی</Title>
        <ErrorBox message={error} />
        <Card>
          <Text style={styles.h2}>پرونده جدید</Text>
          <Input label="موضوع" value={subject} onChangeText={setSubject} maxLength={200} />
          <Input label="شناسه سفارش (اختیاری)" value={relatedOrderId} onChangeText={setRelatedOrderId} />
          <Btn label="ایجاد پرونده" onPress={() => void createCase()} loading={loading} disabled={!subject.trim() || loading} />
        </Card>
        <Card>
          <View style={styles.headerRow}>
            <Text style={styles.h2}>پرونده‌ها</Text>
            <Btn label="تازه‌سازی" tone="ghost" onPress={() => void loadCases()} />
          </View>
          {cases.length === 0 ? <Empty title="پرونده‌ای نیست" /> : cases.map((c) => (
            <View key={c.id} style={styles.caseRow}>
              <View style={styles.grow}>
                <Text style={styles.h2}>{c.subject || "بدون موضوع"}</Text>
                <Text style={styles.meta}>{c.case_number || c.id} · {c.status || "—"}</Text>
              </View>
              <Btn label="باز کردن" tone="ghost" onPress={() => void loadCase(c.id)} />
            </View>
          ))}
        </Card>
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  headerRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  caseRow: { flexDirection: "row", alignItems: "center", gap: spacing.sm, borderTopWidth: 1, borderTopColor: colors.border, paddingTop: spacing.sm, marginTop: spacing.sm },
  message: { borderTopWidth: 1, borderTopColor: colors.border, paddingTop: spacing.sm, marginTop: spacing.sm },
  grow: { flex: 1, minWidth: 0 },
  h2: { color: colors.text, fontSize: 15, fontWeight: "700", marginBottom: 4 },
  body: { color: colors.text, fontSize: 13, lineHeight: 20 },
  meta: { color: colors.textSecondary, fontSize: 11, lineHeight: 18 },
});
