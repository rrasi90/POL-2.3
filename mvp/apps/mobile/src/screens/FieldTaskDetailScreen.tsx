import React, { useCallback, useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text } from "react-native";
import { api } from "../api";
import { OfflineBanner } from "../components/OfflineBanner";
import { Btn, Card, ErrorBox, Input, Screen, StatusChip, Title } from "../components/ui";
import { spacing, useThemedStyles, type Palette } from "../theme";
import type { FieldTask } from "../types";

const statusLabel: Record<string, string> = {
  PENDING: "در انتظار",
  IN_PROGRESS: "در حال انجام",
  ASSIGNED: "واگذارشده",
  COMPLETED: "تکمیل‌شده",
  CANCELLED: "لغوشده",
  OPEN: "باز",
  DONE: "انجام‌شده",
  CLOSED: "بسته",
};

const statusOptions = ["", "PENDING", "IN_PROGRESS", "ASSIGNED", "COMPLETED", "CANCELLED"];

/** F-02 activation detail + F-04 follow-up notes/status PATCH. */
export function FieldTaskDetailScreen(props: { taskId: string; onBack: () => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const [task, setTask] = useState<FieldTask | null>(null);
  const [status, setStatus] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<FieldTask>(`/api/v1/field/tasks/${props.taskId}`);
      setTask(data);
      setStatus(data.status ?? "");
      setNotes(data.notes ?? "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "دریافت وظیفه ناموفق بود");
    } finally {
      setLoading(false);
    }
  }, [props.taskId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function save(): Promise<void> {
    setSaving(true);
    setSaveError(null);
    setSaved(false);
    try {
      const body: Record<string, string> = {};
      if (status && status !== (task?.status ?? "")) body.status = status;
      if (notes !== (task?.notes ?? "")) body.notes = notes;
      if (Object.keys(body).length === 0) {
        setSaved(true);
        return;
      }
      const updated = await api.patch<FieldTask>(`/api/v1/field/tasks/${props.taskId}`, body);
      setTask(updated);
      setStatus(updated.status ?? "");
      setNotes(updated.notes ?? "");
      setSaved(true);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "ذخیره وظیفه ناموفق بود");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Screen>
      <OfflineBanner />
      <Title badge="F-02 / F-04">جزئیات وظیفه</Title>
      <Btn label="بازگشت به لیست" tone="ghost" onPress={props.onBack} disabled={saving || loading} />
      <ErrorBox message={error} />
      <ErrorBox message={saveError} />
      {saved ? <Text style={styles.saved}>تغییرات ذخیره شد.</Text> : null}

      <Card>
        <StatusChip label={statusLabel[task?.status ?? ""] ?? task?.status ?? "—"} />
        <Text style={styles.type}>{task?.task_type ?? "—"}</Text>
        <Text style={styles.meta} numberOfLines={1}>
          {task?.id}
        </Text>
        <Text style={styles.meta}>سازمان هدف: {task?.target_organization_id ?? "—"}</Text>
        <Text style={styles.meta}>ایجاد: {task?.created_at ?? "—"}</Text>
        <Text style={styles.meta}>مهلت: {task?.due_date ?? "—"}</Text>
        <Text style={styles.meta}>تکمیل: {task?.completed_at ?? "—"}</Text>
      </Card>

      <Card>
        <Text style={styles.h2}>به‌روزرسانی (F-04)</Text>
        <Text style={styles.hint}>PATCH /field/tasks/{"{id}"} — status ≤20، notes ≤2000</Text>
        <Input
          label="وضعیت"
          value={status}
          onChangeText={setStatus}
          maxLength={20}
          hint={statusOptions.filter(Boolean).join(" · ")}
          autoCapitalize="characters"
        />
        <Input
          label="یادداشت"
          value={notes}
          onChangeText={setNotes}
          maxLength={2000}
          multiline
          numberOfLines={4}
          hint={`${notes.length}/2000`}
          style={styles.textarea}
        />
        <Btn label="ذخیره تغییرات" onPress={() => void save()} loading={saving} />
        <Btn label="تازه‌سازی" tone="ghost" onPress={() => void load()} disabled={saving} loading={loading} />
      </Card>
    </Screen>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
  saved: { color: colors.success, fontSize: 13, marginBottom: spacing.sm },
  type: { fontSize: 14, color: colors.text, marginTop: spacing.sm, fontWeight: "600" },
  meta: { fontSize: 12, color: colors.textSecondary, marginTop: 4 },
  h2: { fontSize: 15, fontWeight: "600", color: colors.text },
  hint: { fontSize: 11, color: colors.textMuted, marginTop: 4, marginBottom: spacing.md },
  textarea: { minHeight: 96, textAlignVertical: "top" },
  });
}
