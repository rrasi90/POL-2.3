import React, { useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Animated,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
  type TextInputProps,
} from "react-native";
import { spacing, useTheme, useThemedStyles, type Palette } from "../theme";
import { motionCrossfade, motionDuration, motionEasing } from "../motion/motionTokens";
import { usePressScale } from "../motion/PressScale";
import { FadeIn } from "../motion/FadeIn";
import { ErrorShake, useErrorTrigger } from "../motion/ErrorShake";

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
  const { scale, pressIn, pressOut } = usePressScale({ disabled: props.disabled || props.loading });
  const [shown, setShown] = useState(props.loading ?? false);
  const contentOpacity = useRef(new Animated.Value(1)).current;

  // Label ↔ spinner crossfade; the swap happens at full transparency.
  useEffect(() => {
    if (props.loading === shown) return;
    let cancelled = false;
    Animated.timing(contentOpacity, { toValue: 0, duration: motionCrossfade.out, easing: motionEasing.accelerate, useNativeDriver: true }).start(() => {
      if (cancelled) return;
      setShown(props.loading ?? false);
      Animated.timing(contentOpacity, { toValue: 1, duration: motionCrossfade.in, easing: motionEasing.decelerate, useNativeDriver: true }).start();
    });
    return () => {
      cancelled = true;
    };
  }, [props.loading, shown, contentOpacity]);

  return (
    <Animated.View style={{ transform: [{ scale }] }}>
      <Pressable
        accessibilityRole="button"
        accessibilityState={{ busy: props.loading ?? false, disabled: !!(props.disabled || props.loading) }}
        disabled={props.disabled || props.loading}
        onPress={props.onPress}
        onPressIn={pressIn}
        onPressOut={pressOut}
        style={({ pressed }) => [
          styles.btn,
          props.compact && styles.btnCompact,
          ghost && styles.btnGhost,
          danger && styles.btnDanger,
          (props.disabled || props.loading) && styles.btnDisabled,
          pressed && !props.disabled && !props.loading && styles.btnPressed,
        ]}
      >
        <Animated.View style={[styles.btnContent, { opacity: contentOpacity }]}>
          {shown ? (
            <ActivityIndicator color={ghost ? colors.brand : "#fff"} />
          ) : (
            <Text style={[styles.btnText, ghost && styles.btnTextGhost, danger && styles.btnTextDanger]}>{props.label}</Text>
          )}
        </Animated.View>
      </Pressable>
    </Animated.View>
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
  return (
    <View style={[styles.chip, { backgroundColor: bg, borderColor: bc }]}>
      <FadeIn key={props.label} duration={motionDuration.micro} offsetY={0}>
        <Text style={[styles.chipText, { color: fg }]}>{props.label}</Text>
      </FadeIn>
    </View>
  );
}

export function ErrorBox(props: { message: string | null; revision?: number }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const [messageTrigger, bumpMessageTrigger] = useErrorTrigger();
  // Signature: explicit revision when provided (repeating the same message
  // animates again), otherwise the message text itself.
  const signature = props.revision !== undefined ? props.revision : props.message;
  const lastSignature = useRef(signature);
  useEffect(() => {
    if (props.message && signature !== lastSignature.current) bumpMessageTrigger();
    lastSignature.current = signature;
  }, [signature, props.message, bumpMessageTrigger]);
  if (!props.message) return null;
  return (
    <ErrorShake trigger={messageTrigger}>
      <View style={styles.error}>
        <Text style={styles.errorText}>{props.message}</Text>
      </View>
    </ErrorShake>
  );
}

export function Empty(props: { title: string; description?: string }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <FadeIn>
      <Card>
        <Text style={styles.emptyTitle}>{props.title}</Text>
        {props.description ? <Text style={styles.emptyBody}>{props.description}</Text> : null}
      </Card>
    </FadeIn>
  );
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

// Shared brand mark (brand square + "پل" glyph) used by splash and login so
// both variants render one identical mark.
export function BrandMark(props: { size?: number }): React.ReactNode {
  const { colors } = useTheme();
  const size = props.size ?? 82;
  return (
    <View
      style={{
        width: size,
        height: size,
        borderRadius: Math.round(size * 0.317),
        backgroundColor: colors.brand,
        alignItems: "center",
        justifyContent: "center",
        shadowColor: colors.brand,
        shadowOpacity: 0.22,
        shadowRadius: 14,
        elevation: 4,
      }}
    >
      <Text style={{ color: "#fff", fontSize: Math.round(size * 0.488), fontWeight: "900" }}>پل</Text>
    </View>
  );
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
    btnPressed: { opacity: 0.82 },
    btnContent: { alignItems: "center", justifyContent: "center" },
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
