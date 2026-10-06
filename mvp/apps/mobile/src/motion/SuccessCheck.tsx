import React, { useEffect, useRef } from "react";
import { Animated, View } from "react-native";
import { motionDuration, motionEasing, motionSpring } from "./motionTokens";
import { useTheme } from "../theme";
import { useReducedMotion } from "./useReducedMotion";

// Ring + check built from a rotated bordered square — no SVG dependency.
// Whole sequence stays inside the canonical ≤400ms complex-sequence band.
export function SuccessCheck(props: { size?: number; delay?: number }): React.ReactNode {
  const { colors } = useTheme();
  const reduced = useReducedMotion();
  const size = props.size ?? 72;
  const stroke = Math.max(3, Math.round(size * 0.055));
  const ring = useRef(new Animated.Value(0)).current;
  const check = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (reduced) {
      ring.setValue(1);
      check.setValue(1);
      return;
    }
    const animation = Animated.parallel([
      Animated.spring(ring, { toValue: 1, delay: props.delay ?? 0, ...motionSpring.pop, useNativeDriver: true }),
      Animated.timing(check, {
        toValue: 1,
        delay: (props.delay ?? 0) + motionDuration.micro,
        duration: motionDuration.emphasis,
        easing: motionEasing.standard,
        useNativeDriver: true,
      }),
    ]);
    animation.start();
    return () => animation.stop();
  }, [reduced, ring, check, props.delay]);

  const checkHeight = size * 0.42;
  return (
    <View style={{ width: size, height: size, alignItems: "center", justifyContent: "center" }}>
      <Animated.View
        style={{
          position: "absolute",
          width: size,
          height: size,
          borderRadius: size / 2,
          borderWidth: stroke,
          borderColor: colors.success,
          opacity: ring,
          transform: [{ scale: ring.interpolate({ inputRange: [0, 1], outputRange: [0.6, 1] }) }],
        }}
      />
      <Animated.View
        style={{
          width: checkHeight * 0.55,
          height: checkHeight,
          borderRightWidth: stroke,
          borderBottomWidth: stroke,
          borderColor: colors.success,
          borderRadius: 2,
          opacity: check,
          transform: [
            { translateY: -size * 0.03 },
            { rotate: "45deg" },
            { scale: check.interpolate({ inputRange: [0, 1], outputRange: [0.5, 1] }) },
          ],
        }}
      />
    </View>
  );
}
