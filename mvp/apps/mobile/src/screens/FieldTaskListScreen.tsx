import React, { useCallback, useEffect, useState } from "react";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import { api } from "../api";
import { OfflineBanner } from "../components/OfflineBanner";
import { Btn, Card, Empty, ErrorBox, Input, Screen, StatusChip, Title } from "../components/ui";
import { spacing, useThemedStyles, type Palette } from "../theme";
import type { FieldTask } from "../types";
import { formatFieldTaskStatus, formatFieldTaskType } from "../utils/statusLabels";
import { formatTehranDateTime } from "../i18n/fa";

function statusTone(status?: string | null): "neutral" | "warn" | "ok" | "info" {
  if (status === "COMPLETED" || status === "DONE") return "ok";
  if (status === "PENDING" || status === "OPEN" || status === "ASSIGNED") return "warn";
  if (status === "IN_PROGRESS") return "info";
  return "neutral";
}

function itemsOf(data: unknown): FieldTask[] {
  if (Array.isArray(data)) return data as FieldTask[];
  if (data && typeof data === "object") {
    const rec = data as Record<string, unknown>;
    if (Array.isArray(rec.tasks)) return rec.tasks as FieldTask[];
    if (Array.isArray(rec.items)) return rec.items as FieldTask[];
    if (Array.isArray(rec.results)) return rec.results as FieldTask[];
  }
  return [];
}

/** F-01 today/task list + F-03 assisted-order entry + F-05 offline banner. */
export function FieldTaskListScreen(props: {
  onOpenTask: (id: string) => void;
  onAssistedOrder: () => void;
}): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const [tasks, setTasks] = useState<FieldTask[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<unknown>("/api/v1/field/tasks?limit=50&offset=0");
      setTasks(itemsOf(data));
    } catch (err) {
      setError(err instanceof Error ? err.message : "دریافت وظایف ناموفق بود");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const q = query.trim().toLowerCase();
  const filtered = tasks.filter(
    (t) =>
      !q ||
      (t.task_type ?? "").toLowerCase().includes(q) ||
      (t.notes ?? "").toLowerCase().includes(q) ||
      (t.id ?? "").toLowerCase().includes(q),
  );

  return (
    <Screen>
      <OfflineBanner />
      <Title badge="وظایف میدانی">فعال‌سازی میدانی</Title>
      <ErrorBox message={error} />
      <View style={styles.actions}>
        <Btn label="به‌روزرسانی" tone="ghost" onPress={() => void load()} loading={loading} />
        <Btn label="ثبت سفارش به کمک کارشناس" onPress={props.onAssistedOrder} />
      </View>
      <Input
        label="جستجوی وظیفه"
        placeholder="جستجو…"
        value={query}
        onChangeText={setQuery}
        autoCapitalize="none"
      />
      <Text style={styles.section}>وظایف امروز</Text>
      {filtered.length === 0 ? (
        <Empty
          title="وظیفه‌ای وجود ندارد"
          description="وقتی وظیفه جدید واگذار شود، اینجا نمایش داده می‌شود."
        />
      ) : (
        <FlatList
          data={filtered}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <Pressable accessibilityRole="button" onPress={() => props.onOpenTask(item.id)}>
              <Card>
                <View style={styles.row}>
                  <StatusChip label={formatFieldTaskStatus(item.status)} tone={statusTone(item.status)} />
                  <Text style={styles.type} numberOfLines={1}>
                    {formatFieldTaskType(item.task_type)}
                  </Text>
                </View>
                {item.notes ? (
                  <Text style={styles.notes} numberOfLines={2}>
                    {item.notes}
                  </Text>
                ) : null}
                <Text style={styles.meta}>{formatTehranDateTime(item.created_at)}</Text>
              </Card>
            </Pressable>
          )}
        />
      )}
    </Screen>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
  actions: { flexDirection: "row", gap: spacing.sm, marginBottom: spacing.md, flexWrap: "wrap" },
  section: { fontSize: 15, fontWeight: "600", color: colors.text, marginBottom: spacing.sm },
  row: { flexDirection: "row", alignItems: "center", gap: spacing.sm, flexWrap: "wrap" },
  type: { fontSize: 13, color: colors.textSecondary, flexShrink: 1 },
  notes: { fontSize: 13, color: colors.textSecondary, marginTop: spacing.sm, lineHeight: 20 },
  meta: { fontSize: 11, color: colors.textMuted, marginTop: spacing.xs },
  });
}
