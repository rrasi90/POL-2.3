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
import { spacing, useTheme, useThemedStyles, type Palette } from "../theme";

export function Screen(props: { children: React.ReactNode }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return <View style={styles.screen}>{props.children}</View>;
}

export function Title(props: { children: React.ReactNode; badge?: string }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <View style={styles.titleRow}>
      <Text style={styles.title}>{props.children}</Text>
      {props.badge ? (
        <View style={styles.badgeWrapper}>
          <Text style={styles.badge} accessibilityLabel={props.badge}>
            {props.badge}
          </Text>
        </View>
      ) : null}
    </View>
  );
}

export function Card(props: { children: React.ReactNode }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return <View style={styles.card}>{props.children}</View>;
}

export function Btn(props: {
  label: string;
  onPress: () => void;
  disabled?: boolean;
  loading?: boolean;
  tone?: "primary" | "ghost" | "danger";
}): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const { colors } = useTheme();
  const ghost = props.tone === "ghost";
  const danger = props.tone === "danger";
  return (
    <Pressable
      accessibilityRole="button"
      disabled={props.disabled || props.loading}
      onPress={props.onPress}
      style={({ pressed }) => [
        styles.btn,
        ghost && styles.btnGhost,
        danger && styles.btnDanger,
        (props.disabled || props.loading) && styles.btnDisabled,
        pressed && !props.disabled && !props.loading && styles.btnPressed,
      ]}
    >
      {props.loading ? (
        <ActivityIndicator color={ghost ? colors.brand : "#fff"} />
      ) : (
        <Text style={[styles.btnText, ghost && styles.btnTextGhost, danger && styles.btnTextDanger]}>{props.label}</Text>
      )}
    </Pressable>
  );
}

export function Input(props: TextInputProps & { label: string; hint?: string }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const { colors } = useTheme();
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

export function StatusChip(props: { label: string; tone?: "neutral" | "warn" | "ok" | "info" | "danger" }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const { colors } = useTheme();
  const tone = props.tone ?? "neutral";
  const bg =
    tone === "ok"
      ? colors.successBg
      : tone === "warn"
      ? colors.warningBg
      : tone === "info"
      ? colors.infoBg
      : tone === "danger"
      ? colors.dangerBg
      : colors.neutralBg;
  const fg =
    tone === "ok"
      ? colors.success
      : tone === "warn"
      ? colors.warning
      : tone === "info"
      ? colors.brand
      : tone === "danger"
      ? colors.danger
      : colors.textSecondary;
  const bc =
    tone === "ok"
      ? colors.success + "33"
      : tone === "warn"
      ? colors.warning + "33"
      : tone === "info"
      ? colors.brand + "33"
      : tone === "danger"
      ? colors.danger + "33"
      : colors.border;
  return (
    <View style={[styles.chip, { backgroundColor: bg, borderColor: bc }]}>
      <Text style={[styles.chipText, { color: fg }]}>{props.label}</Text>
    </View>
  );
}

export function ErrorBox(props: { message: string | null }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  if (!props.message) return null;
  return (
    <View style={styles.error}>
      <Text style={styles.errorText}>{props.message}</Text>
    </View>
  );
}

export function Empty(props: { title: string; description?: string }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <Card>
      <Text style={styles.emptyTitle}>{props.title}</Text>
      {props.description ? <Text style={styles.emptyBody}>{props.description}</Text> : null}
    </Card>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
    screen: { flex: 1, backgroundColor: colors.bg, padding: spacing.lg },
    titleRow: { flexDirection: "row", alignItems: "center", gap: spacing.sm, marginBottom: spacing.md },
    title: { fontSize: 20, fontWeight: "700", color: colors.text, letterSpacing: -0.3 },
    badgeWrapper: {
      backgroundColor: colors.neutralBg,
      borderColor: colors.border,
      borderWidth: 1,
      borderRadius: 6,
      paddingHorizontal: 8,
      paddingVertical: 2,
    },
    badge: { fontSize: 11, fontWeight: "600", color: colors.textSecondary },
    card: {
      backgroundColor: colors.surface,
      borderColor: colors.border,
      borderWidth: 1,
      borderRadius: 12,
      padding: spacing.lg,
      marginBottom: spacing.md,
      shadowColor: "#0F172A",
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.04,
      shadowRadius: 3,
      elevation: 1,
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
    btnDanger: { backgroundColor: colors.danger },
    btnDisabled: { opacity: 0.5 },
    btnPressed: { opacity: 0.8 },
    btnText: { color: "#fff", fontSize: 14, fontWeight: "600" },
    btnTextGhost: { color: colors.brand },
    btnTextDanger: { color: "#fff" },
    field: { marginBottom: spacing.md },
    label: { fontSize: 12, color: colors.textSecondary, marginBottom: 6, fontWeight: "500" },
    input: {
      borderWidth: 1,
      borderColor: colors.border,
      borderRadius: 10,
      minHeight: 44,
      paddingHorizontal: spacing.md,
      paddingVertical: 10,
      fontSize: 15,
      color: colors.text,
      backgroundColor: colors.surface,
    },
    hint: { fontSize: 11, color: colors.textMuted, marginTop: 4 },
    chip: {
      borderWidth: 1,
      borderRadius: 6,
      paddingHorizontal: 8,
      paddingVertical: 3,
      alignSelf: "flex-start",
    },
    chipText: { fontSize: 11, fontWeight: "600" },
    error: {
      backgroundColor: colors.dangerBg,
      borderColor: colors.danger,
      borderWidth: 1,
      borderRadius: 10,
      padding: spacing.md,
      marginBottom: spacing.md,
    },
    errorText: { color: colors.danger, fontSize: 13, lineHeight: 18 },
    emptyTitle: { fontSize: 15, fontWeight: "600", color: colors.text },
    emptyBody: { fontSize: 13, color: colors.textSecondary, marginTop: 6, lineHeight: 20 },
  });
}
