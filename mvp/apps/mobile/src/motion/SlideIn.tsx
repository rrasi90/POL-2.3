import React, { useEffect, useRef } from "react";
import { Animated, type StyleProp, type ViewStyle } from "react-native";
import { RTL_LAYOUT, motionDrift, motionDuration, motionEasing } from "./motionTokens";
import type { MotionDirection } from "./motionTypes";
import { useReducedMotion } from "./useReducedMotion";

// "forward" is the next step in reading flow (RTL: enters from the left),
// "back" the reverse; "up"/"down" are vertical.
function entryOffset(direction: MotionDirection, distance: number): { x: number; y: number } {
  const sign = RTL_LAYOUT ? -1 : 1;
  switch (direction) {
    case "forward":
      return { x: sign * distance, y: 0 };
    case "back":
      return { x: -sign * distance, y: 0 };
    case "up":
      return { x: 0, y: distance };
    case "down":
      return { x: 0, y: -distance };
  }
}

export function SlideIn(props: {
  children: React.ReactNode;
  direction?: MotionDirection;
  delay?: number;
  distance?: number;
  duration?: number;
  style?: StyleProp<ViewStyle>;
}): React.ReactNode {
  const reduced = useReducedMotion();
  const progress = useRef(new Animated.Value(reduced ? 1 : 0)).current;
  const direction = props.direction ?? "forward";
  const distance = props.distance ?? motionDrift.md;
  const offset = entryOffset(direction, distance);

  useEffect(() => {
    if (reduced) {
      progress.setValue(1);
      return;
    }
    const animation = Animated.timing(progress, {
      toValue: 1,
      delay: props.delay ?? 0,
      duration: props.duration ?? motionDuration.base,
      easing: motionEasing.standard,
      useNativeDriver: true,
    });
    animation.start();
    return () => animation.stop();
  }, [progress, reduced, props.delay, props.duration]);

  return (
    <Animated.View
      style={[
        props.style,
        {
          opacity: progress,
          transform: [
            { translateX: progress.interpolate({ inputRange: [0, 1], outputRange: [offset.x, 0] }) },
            { translateY: progress.interpolate({ inputRange: [0, 1], outputRange: [offset.y, 0] }) },
          ],
        },
      ]}
    >
      {props.children}
    </Animated.View>
  );
}