import React, { useEffect, useRef } from "react";
import { Animated, StyleSheet, View, type StyleProp, type ViewStyle } from "react-native";
import { motionDuration, motionEasing } from "./motionTokens";
import { useTheme } from "../theme";
import { useReducedMotion } from "./useReducedMotion";

// Repeating soft ring for scan lookup and arrival feedback. Decorative only:
// pointerEvents none, opacity/scale driven, hidden entirely under reduced motion.
export function Pulse(props: {
  active: boolean;
  loop?: boolean;
  size?: number;
  style?: StyleProp<ViewStyle>;
  children?: React.ReactNode;
}): React.ReactNode {
  const { colors } = useTheme();
  const reduced = useReducedMotion();
  const progress = useRef(new Animated.Value(0)).current;
  const size = props.size ?? 64;

  useEffect(() => {
    if (!props.active || reduced) {
      progress.setValue(0);
      return;
    }
    const burst = Animated.sequence([
      Animated.timing(progress, { toValue: 1, duration: motionDuration.base, easing: motionEasing.decelerate, useNativeDriver: true }),
      Animated.timing(progress, { toValue: 0, duration: motionDuration.base, easing: motionEasing.accelerate, useNativeDriver: true }),
    ]);
    const animation = props.loop === false ? Animated.sequence([burst, burst, burst]) : Animated.loop(burst);
    animation.start();
    return () => animation.stop();
  }, [progress, props.active, props.loop, reduced]);

  return (
    <View style={props.style}>
      {props.children}
      {props.active && !reduced ? (
        <Animated.View pointerEvents="none" style={StyleSheet.absoluteFill}>
          <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
            <Animated.View
              style={{
                width: size,
                height: size,
                borderRadius: size / 2,
                borderWidth: 2,
                borderColor: colors.brand,
                opacity: progress.interpolate({ inputRange: [0, 1], outputRange: [0.4, 0] }),
                transform: [{ scale: progress.interpolate({ inputRange: [0, 1], outputRange: [1, 1.6] }) }],
              }}
            />
          </View>
        </Animated.View>
      ) : null}
    </View>
  );
}
