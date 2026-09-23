import React from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
  type TextInputProps,
} from "react-native";
import { colors, spacing } from "../theme";

export function Screen(props: { children: React.ReactNode }): React.ReactNode {
  return <View style={styles.screen}>{props.children}</View>;
}

export function Title(props: { children: React.ReactNode; badge?: string }): React.ReactNode {
  return (
    <View style={styles.titleRow}>
      <Text style={styles.title}>{props.children}</Text>
      {props.badge ? (
        <Text style={styles.badge} accessibilityLabel={props.badge}>
          {props.badge}
        </Text>
      ) : null}
    </View>
  );
}

export function Card(props: { children: React.ReactNode }): React.ReactNode {
  return <View style={styles.card}>{props.children}</View>;
}

export function Btn(props: {
  label: string;
  onPress: () => void;
  disabled?: boolean;
  loading?: boolean;
  tone?: "primary" | "ghost";
}): React.ReactNode {
  const ghost = props.tone === "ghost";
  return (
    <Pressable
      accessibilityRole="button"
      disabled={props.disabled || props.loading}
      onPress={props.onPress}
      style={[styles.btn, ghost && styles.btnGhost, (props.disabled || props.loading) && styles.btnDisabled]}
    >
      {props.loading ? (
        <ActivityIndicator color={ghost ? colors.brand : "#fff"} />
      ) : (
        <Text style={[styles.btnText, ghost && styles.btnTextGhost]}>{props.label}</Text>
      )}
    </Pressable>
  );
}

export function Input(props: TextInputProps & { label: string; hint?: string }): React.ReactNode {
  const { label, hint, ...rest } = props;
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        {...rest}
        style={[styles.input, rest.style]}
        placeholderTextColor={colors.textMuted}
      />
      {hint ? <Text style={styles.hint}>{hint}</Text> : null}
    </View>
  );
}

export function StatusChip(props: { label: string; tone?: "neutral" | "warn" | "ok" | "info" }): React.ReactNode {
  const tone = props.tone ?? "neutral";
  const bg =
    tone === "ok" ? "#ECFDF5" : tone === "warn" ? "#FFFBEB" : tone === "info" ? "#EFF6FF" : "#F1F5F9";
  const fg =
    tone === "ok" ? colors.success : tone === "warn" ? colors.warning : tone === "info" ? colors.brand : colors.textSecondary;
  return (
    <View style={[styles.chip, { backgroundColor: bg }]}>
      <Text style={[styles.chipText, { color: fg }]}>{props.label}</Text>
    </View>
  );
}

export function ErrorBox(props: { message: string | null }): React.ReactNode {
  if (!props.message) return null;
  return (
    <View style={styles.error}>
      <Text style={styles.errorText}>{props.message}</Text>
    </View>
  );
}

export function Empty(props: { title: string; description?: string }): React.ReactNode {
  return (
    <Card>
      <Text style={styles.emptyTitle}>{props.title}</Text>
      {props.description ? <Text style={styles.emptyBody}>{props.description}</Text> : null}
    </Card>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg, padding: spacing.lg },
  titleRow: { flexDirection: "row", alignItems: "center", gap: spacing.sm, marginBottom: spacing.md },
  title: { fontSize: 22, fontWeight: "700", color: colors.text },
  badge: { fontSize: 11, color: colors.textMuted },
  card: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  btn: {
    backgroundColor: colors.brand,
    borderRadius: 10,
    minHeight: 44,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
  },
  btnGhost: { backgroundColor: "transparent", borderWidth: 1, borderColor: colors.border },
  btnDisabled: { opacity: 0.55 },
  btnText: { color: "#fff", fontSize: 14, fontWeight: "600" },
  btnTextGhost: { color: colors.brand },
  field: { marginBottom: spacing.md },
  label: { fontSize: 12, color: colors.textSecondary, marginBottom: 6, fontWeight: "500" },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: spacing.md,
    paddingVertical: 10,
    fontSize: 15,
    color: colors.text,
    backgroundColor: colors.surface,
  },
  hint: { fontSize: 11, color: colors.textMuted, marginTop: 4 },
  chip: { borderRadius: 999, paddingHorizontal: 10, paddingVertical: 4, alignSelf: "flex-start" },
  chipText: { fontSize: 11, fontWeight: "600" },
  error: { backgroundColor: "#FEF2F2", borderColor: "#FECACA", borderWidth: 1, borderRadius: 10, padding: spacing.md, marginBottom: spacing.md },
  errorText: { color: colors.danger, fontSize: 13 },
  emptyTitle: { fontSize: 15, fontWeight: "600", color: colors.text },
  emptyBody: { fontSize: 13, color: colors.textSecondary, marginTop: 6, lineHeight: 20 },
});
