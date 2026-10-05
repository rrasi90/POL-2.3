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
          <Text style={styles.badge}>{props.badge}</Text>
        </View>
      ) : null}
    </View>
  );
}

export function Card(props: { children: React.ReactNode; style?: object }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return <View style={[styles.card, props.style]}>{props.children}</View>;
}

export function Btn(props: {
  label: string;
  onPress: () => void;
  disabled?: boolean;
  loading?: boolean;
  tone?: "primary" | "ghost" | "danger";
  compact?: boolean;
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
        props.compact && styles.btnCompact,
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

export function Input(props: TextInputProps & { label: string; hint?: string; direction?: "rtl" | "ltr" }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const { colors } = useTheme();
  const { label, hint, direction, ...rest } = props;
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <TextInput {...rest} style={[styles.input, direction ? { writingDirection: direction } : null, rest.style]} placeholderTextColor={colors.textMuted} />
      {hint ? <Text style={styles.hint}>{hint}</Text> : null}
    </View>
  );
}

export function StatusChip(props: { label: string; tone?: "neutral" | "warn" | "ok" | "info" | "danger" }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const { colors } = useTheme();
  const tone = props.tone ?? "neutral";
  const bg =
    tone === "ok" ? colors.successBg :
    tone === "warn" ? colors.warningBg :
    tone === "info" ? colors.infoBg :
    tone === "danger" ? colors.dangerBg : colors.neutralBg;
  const fg =
    tone === "ok" ? colors.success :
    tone === "warn" ? colors.warning :
    tone === "info" ? colors.brand :
    tone === "danger" ? colors.danger : colors.textSecondary;
  const bc =
    tone === "ok" ? colors.success + "33" :
    tone === "warn" ? colors.warning + "33" :
    tone === "info" ? colors.brand + "33" :
    tone === "danger" ? colors.danger + "33" : colors.border;
  return <View style={[styles.chip, { backgroundColor: bg, borderColor: bc }]}><Text style={[styles.chipText, { color: fg }]}>{props.label}</Text></View>;
}

export function ErrorBox(props: { message: string | null }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  if (!props.message) return null;
  return <View style={styles.error}><Text style={styles.errorText}>{props.message}</Text></View>;
}

export function Empty(props: { title: string; description?: string }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return <Card><Text style={styles.emptyTitle}>{props.title}</Text>{props.description ? <Text style={styles.emptyBody}>{props.description}</Text> : null}</Card>;
}

export function IconBadge(props: { symbol: string; tone?: "brand" | "success" | "warning" | "danger" | "neutral" }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const { colors } = useTheme();
  const bg =
    props.tone === "success" ? colors.successBg :
    props.tone === "warning" ? colors.warningBg :
    props.tone === "danger" ? colors.dangerBg :
    props.tone === "neutral" ? colors.neutralBg : colors.brandSoft;
  const fg =
    props.tone === "success" ? colors.success :
    props.tone === "warning" ? colors.warning :
    props.tone === "danger" ? colors.danger :
    props.tone === "neutral" ? colors.textSecondary : colors.brand;
  return <View style={[styles.iconBadge, { backgroundColor: bg }]}><Text style={[styles.iconBadgeText, { color: fg }]}>{props.symbol}</Text></View>;
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
    screen: { flex: 1, backgroundColor: colors.bg, paddingHorizontal: spacing.md, paddingTop: spacing.sm, direction: "rtl" },
    titleRow: { flexDirection: "row", alignItems: "center", gap: spacing.sm, marginBottom: spacing.md },
    title: { fontSize: 22, fontWeight: "800", color: colors.text, letterSpacing: -0.4 },
    badgeWrapper: { backgroundColor: colors.neutralBg, borderColor: colors.border, borderWidth: 1, borderRadius: 999, paddingHorizontal: 9, paddingVertical: 3 },
    badge: { fontSize: 10, fontWeight: "700", color: colors.textSecondary },
    card: {
      backgroundColor: colors.surface,
      borderColor: colors.border,
      borderWidth: 1,
      borderRadius: 16,
      padding: spacing.lg,
      marginBottom: spacing.md,
      shadowColor: "#0F172A",
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.04,
      shadowRadius: 8,
      elevation: 1,
    },
    btn: { backgroundColor: colors.brand, borderRadius: 12, minHeight: 48, alignItems: "center", justifyContent: "center", paddingHorizontal: spacing.lg, paddingVertical: spacing.sm },
    btnCompact: { minHeight: 40, paddingHorizontal: spacing.md, borderRadius: 10 },
    btnGhost: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border },
    btnDanger: { backgroundColor: colors.danger },
    btnDisabled: { opacity: 0.5 },
    btnPressed: { opacity: 0.82, transform: [{ scale: 0.985 }] },
    btnText: { color: "#fff", fontSize: 14, fontWeight: "700", textAlign: "center" },
    btnTextGhost: { color: colors.brand },
    btnTextDanger: { color: "#fff" },
    field: { marginBottom: spacing.md },
    label: { fontSize: 12, color: colors.textSecondary, marginBottom: 6, fontWeight: "600", textAlign: "right" },
    input: { borderWidth: 1, borderColor: colors.border, borderRadius: 12, minHeight: 48, paddingHorizontal: spacing.md, paddingVertical: 10, fontSize: 15, color: colors.text, backgroundColor: colors.surface, textAlign: "right" },
    hint: { fontSize: 11, color: colors.textMuted, marginTop: 4, lineHeight: 17, textAlign: "right" },
    chip: { borderWidth: 1, borderRadius: 999, paddingHorizontal: 10, paddingVertical: 5, alignSelf: "flex-start" },
    chipText: { fontSize: 11, fontWeight: "700" },
    error: { backgroundColor: colors.dangerBg, borderColor: colors.danger, borderWidth: 1, borderRadius: 12, padding: spacing.md, marginBottom: spacing.md },
    errorText: { color: colors.danger, fontSize: 13, lineHeight: 19, textAlign: "right" },
    emptyTitle: { fontSize: 15, fontWeight: "700", color: colors.text, textAlign: "right" },
    emptyBody: { fontSize: 13, color: colors.textSecondary, marginTop: 6, lineHeight: 20, textAlign: "right" },
    iconBadge: { width: 44, height: 44, borderRadius: 14, alignItems: "center", justifyContent: "center" },
    iconBadgeText: { fontSize: 21, fontWeight: "800" },
  });
}
