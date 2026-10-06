import React, { useEffect, useRef } from "react";
import { Animated, type StyleProp, type ViewStyle } from "react-native";
import { motionDrift, motionDuration, motionEasing } from "./motionTokens";
import { useReducedMotion } from "./useReducedMotion";

// General entrance: fade + small vertical drift. `delay` is the stagger hook —
// pair with staggerDelay(index) for list entrances (cap 8 items).
export function FadeIn(props: {
  children: React.ReactNode;
  delay?: number;
  offsetY?: number;
  duration?: number;
  style?: StyleProp<ViewStyle>;
}): React.ReactNode {
  const reduced = useReducedMotion();
  const progress = useRef(new Animated.Value(reduced ? 1 : 0)).current;

  useEffect(() => {
    if (reduced) {
      progress.setValue(1);
      return;
    }
    const animation = Animated.timing(progress, {
      toValue: 1,
      delay: props.delay ?? 0,
      duration: props.duration ?? motionDuration.base,
      easing: motionEasing.decelerate,
      useNativeDriver: true,
    });
    animation.start();
    return () => animation.stop();
  }, [progress, reduced, props.delay, props.duration]);

  const offsetY = props.offsetY ?? motionDrift.sm;
  return (
    <Animated.View
      style={[
        props.style,
        {
          opacity: progress,
          transform: [{ translateY: progress.interpolate({ inputRange: [0, 1], outputRange: [offsetY, 0] }) }],
        },
      ]}
    >
      {props.children}
    </Animated.View>
  );
}
