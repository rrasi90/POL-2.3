import React, { useEffect, useRef } from "react";
import { Animated, StyleSheet, Text, View } from "react-native";
import { motionDuration, motionEasing, motionSpring } from "./motionTokens";
import { useThemedStyles, type Palette } from "../theme";
import { useReducedMotion } from "./useReducedMotion";

// PRESENTATION MAPPING ONLY. The single source of truth for order state is the
// backend `order_status` field; these view-model helpers only place the current
// status on a visual axis. They create no business state.
export const ORDER_STAGES = ["ثبت سفارش", "تایید و آماده‌سازی", "آماده ارسال", "تحویل"] as const;

export function stageIndexForOrderStatus(status: string | null | undefined): number {
  if (status === "DELIVERED" || status === "ARRIVED") return 3;
  if (status === "IN_TRANSIT" || status === "DISPATCHED") return 2;
  if (["READY", "PREPARING", "ACCEPTED", "PARTIALLY_ACCEPTED"].includes(status || "")) return 1;
  return 0;
}

// Animated order stepper: dots pop when they become done, the connecting line
// fills toward the current stage. Same visual grammar as the original static
// stepper (LTR row), now driven by one progress value.
export function OrderProgress(props: { status: string | null | undefined }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const reduced = useReducedMotion();
  const last = ORDER_STAGES.length - 1;
  const stage = stageIndexForOrderStatus(props.status);
  const progress = useRef(new Animated.Value(stage / last)).current;

  useEffect(() => {
    if (reduced) {
      progress.setValue(stage / last);
      return;
    }
    const animation = Animated.timing(progress, {
      toValue: stage / last,
      duration: motionDuration.emphasis,
      easing: motionEasing.standard,
      useNativeDriver: true,
    });
    animation.start();
    return () => animation.stop();
  }, [progress, reduced, stage, last]);

  return (
    <View style={styles.stepper}>
      {ORDER_STAGES.map((label, index) => {
        const done = index <= stage;
        return (
          <View key={label} style={styles.step}>
            <StepDot done={done} index={index} />
            <Text style={[styles.stepText, done && styles.stepTextDone]}>{label}</Text>
            {index < last ? (
              <View style={styles.stepLine}>
                <Animated.View
                  style={[
                    styles.stepLineFill,
                    {
                      opacity: progress.interpolate({
                        inputRange: [index / last, Math.min((index + 0.5) / last, 1)],
                        outputRange: [0, 1],
                        extrapolateLeft: "clamp",
                        extrapolateRight: "clamp",
                      }),
                      transform: [{
                        scaleX: progress.interpolate({
                          inputRange: [index / last, (index + 1) / last],
                          outputRange: [0, 1],
                          extrapolateLeft: "clamp",
                          extrapolateRight: "clamp",
                        }),
                      }],
                    },
                  ]}
                />
              </View>
            ) : null}
          </View>
        );
      })}
    </View>
  );
}

function StepDot(props: { done: boolean; index: number }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const reduced = useReducedMotion();
  const scale = useRef(new Animated.Value(1)).current;
  const wasDone = useRef(props.done);

  useEffect(() => {
    const becameDone = props.done && !wasDone.current;
    wasDone.current = props.done;
    scale.stopAnimation();
    scale.setValue(1);
    if (reduced || !becameDone) return;
    scale.setValue(1.3);
    const animation = Animated.spring(scale, { toValue: 1, ...motionSpring.bump, useNativeDriver: true });
    animation.start();
    return () => {
      animation.stop();
      scale.stopAnimation();
      scale.setValue(1);
    };
  }, [props.done, reduced, scale]);

  return (
    <Animated.View style={[styles.stepDot, props.done && styles.stepDotDone, { transform: [{ scale }] }]}>
      <Text style={[styles.stepDotText, props.done && styles.stepDotTextDone]}>{props.done ? "✓" : String(props.index + 1)}</Text>
    </Animated.View>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
    stepper: { flexDirection: "row", alignItems: "flex-start", direction: "ltr" },
    step: { flex: 1, alignItems: "center", position: "relative" },
    stepDot: { width: 30, height: 30, borderRadius: 15, backgroundColor: colors.neutralBg, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center", zIndex: 2 },
    stepDotDone: { backgroundColor: colors.brand, borderColor: colors.brand },
    stepDotText: { color: colors.textMuted, fontSize: 10, fontWeight: "900" },
    stepDotTextDone: { color: "#fff" },
    stepText: { color: colors.textMuted, fontSize: 9, textAlign: "center", marginTop: 5 },
    stepTextDone: { color: colors.text, fontWeight: "800" },
    stepLine: { position: "absolute", top: 14, left: "50%", right: "-50%", height: 2, backgroundColor: colors.border },
    stepLineFill: { position: "absolute", top: 0, right: 0, bottom: 0, left: 0, backgroundColor: colors.brand },
  });
}
