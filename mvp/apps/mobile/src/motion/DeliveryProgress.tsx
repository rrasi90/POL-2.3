import React, { useEffect, useRef, useState } from "react";
import { Animated, StyleSheet, Text, View } from "react-native";
import { RTL_LAYOUT, motionDuration, motionEasing } from "./motionTokens";
import { spacing, useTheme, useThemedStyles, type Palette } from "../theme";
import { useReducedMotion } from "./useReducedMotion";

// PRESENTATION MAPPING ONLY. The single source of truth for delivery state is
// the backend `delivery_status` field (and `order_status` for handover); these
// view-model helpers only place the current status on the delivery axis. They
// create no business state. Order lifecycle and delivery lifecycle are
// independent axes — e.g. order DISPATCHED can coexist with delivery
// PICKED_UP or IN_TRANSIT.
export const DELIVERY_STAGES = ["تحویل به پیک", "جمع‌آوری شد", "در مسیر", "رسید", "تحویل شد"] as const;

export type DeliveryStage = "PENDING" | "PICKED_UP" | "IN_TRANSIT" | "ARRIVED" | "DELIVERED" | "FAILED";

const STAGE_INDEX: Record<DeliveryStage, number> = { PENDING: 0, PICKED_UP: 1, IN_TRANSIT: 2, ARRIVED: 3, DELIVERED: 4, FAILED: 0 };

export function stageForDeliveryStatus(deliveryStatus: string | null | undefined, orderStatus?: string | null): DeliveryStage {
  const raw = (deliveryStatus || "").toUpperCase().replace(/-/g, "_");
  if (raw === "DELIVERED") return "DELIVERED";
  if (raw === "ARRIVED") return "ARRIVED";
  if (raw === "IN_TRANSIT") return "IN_TRANSIT";
  if (raw === "PICKED_UP") return "PICKED_UP";
  if (raw === "FAILED") return "FAILED";
  return "PENDING";
}

// Route line + shipment marker in the Precision Commerce visual language —
// deliberately not a literal truck animation. In RTL the shipment travels
// right → left. The marker shuttles while IN_TRANSIT and pulses on arrival.
export function DeliveryProgress(props: { deliveryStatus?: string | null; orderStatus?: string | null }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const { colors } = useTheme();
  const reduced = useReducedMotion();
  const stage = stageForDeliveryStatus(props.deliveryStatus, props.orderStatus);
  const index = STAGE_INDEX[stage];
  const [trackWidth, setTrackWidth] = useState(0);
  const progress = useRef(new Animated.Value(index / (DELIVERY_STAGES.length - 1))).current;
  const wiggle = useRef(new Animated.Value(0)).current;
  const markerScale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    const target = index / (DELIVERY_STAGES.length - 1);
    if (reduced) {
      progress.setValue(target);
      return;
    }
    const animation = Animated.timing(progress, {
      toValue: target,
      duration: motionDuration.emphasis,
      easing: motionEasing.standard,
      useNativeDriver: true,
    });
    animation.start();
    return () => animation.stop();
  }, [progress, reduced, index]);

  useEffect(() => {
    if (reduced) {
      wiggle.setValue(0);
      markerScale.setValue(1);
      return;
    }
    if (stage === "IN_TRANSIT") {
      const loop = Animated.loop(
        Animated.sequence([
          Animated.timing(wiggle, { toValue: 1, duration: motionDuration.emphasis, easing: motionEasing.ambient, useNativeDriver: true }),
          Animated.timing(wiggle, { toValue: 0, duration: motionDuration.emphasis, easing: motionEasing.ambient, useNativeDriver: true }),
        ]),
      );
      loop.start();
      return () => loop.stop();
    }
    if (stage === "ARRIVED") {
      const burst = Animated.sequence([
        Animated.timing(markerScale, { toValue: 1.35, duration: motionDuration.base, easing: motionEasing.decelerate, useNativeDriver: true }),
        Animated.timing(markerScale, { toValue: 1, duration: motionDuration.base, easing: motionEasing.accelerate, useNativeDriver: true }),
      ]);
      const animation = Animated.sequence([burst, burst, burst]);
      animation.start();
      return () => animation.stop();
    }
    wiggle.setValue(0);
    markerScale.setValue(1);
  }, [stage, reduced, wiggle, markerScale]);

  if (stage === "FAILED") {
    return (
      <View style={styles.failedStrip}>
        <Text style={styles.failedText}>ارسال ناموفق برای این سفارش ثبت شده است.</Text>
      </View>
    );
  }

  const last = DELIVERY_STAGES.length - 1;
  const startSign = RTL_LAYOUT ? 1 : -1;
  // Keep the fill anchored at the route origin while scaleX grows.
  const fillShift = progress.interpolate({ inputRange: [0, 1], outputRange: [(startSign * trackWidth) / 2, 0] });
  const markerShift = Animated.add(
    progress.interpolate({ inputRange: [0, 1], outputRange: [0, -startSign * trackWidth] }),
    wiggle.interpolate({ inputRange: [0, 1], outputRange: [0, -startSign * 6] }),
  );
  const done = stage === "DELIVERED";
  const activeColor = done ? colors.success : colors.brand;

  return (
    <View>
      <View style={styles.track} onLayout={(event) => setTrackWidth(event.nativeEvent.layout.width)}>
        <Animated.View
          style={[
            styles.fill,
            { backgroundColor: activeColor },
            { transform: [{ translateX: fillShift }, { scaleX: progress }] },
          ]}
        />
        <Animated.View
          style={[
            styles.marker,
            { backgroundColor: activeColor },
            { transform: [{ translateX: markerShift }, { scale: markerScale }] },
          ]}
        />
      </View>
      <View style={styles.labels}>
        {DELIVERY_STAGES.map((label, i) => (
          <Text key={label} style={[styles.label, i <= index && styles.labelDone]}>{label}</Text>
        ))}
      </View>
    </View>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
    track: { height: 4, borderRadius: 2, backgroundColor: colors.neutralBg, marginVertical: spacing.lg, overflow: "visible" },
    fill: { position: "absolute", top: 0, right: 0, bottom: 0, left: 0, borderRadius: 2 },
    marker: { position: "absolute", top: -6, right: -8, width: 16, height: 16, borderRadius: 8, borderWidth: 2, borderColor: colors.surface },
    labels: { flexDirection: "row", direction: "rtl" },
    label: { flex: 1, textAlign: "center", fontSize: 9, color: colors.textMuted },
    labelDone: { color: colors.brand, fontWeight: "800" },
    failedStrip: { backgroundColor: colors.dangerBg, borderColor: colors.danger, borderWidth: 1, borderRadius: 12, padding: spacing.md },
    failedText: { color: colors.danger, fontSize: 12, textAlign: "right" },
  });
}
