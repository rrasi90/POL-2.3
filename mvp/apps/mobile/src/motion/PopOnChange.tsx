import React, { useEffect, useRef } from "react";
import { Animated, type StyleProp, type ViewStyle } from "react-native";
import { motionScale, motionSpring } from "./motionTokens";
import { useReducedMotion } from "./useReducedMotion";

// Pops (scale pulse) when `value` changes. Use for quantity, totals, basket
// badge, KPI numbers — never as a digit-roll. First mount renders without
// popping; repeated identical values do not re-trigger.
export function PopOnChange(props: {
  value: number | string;
  children: React.ReactNode;
  scaleTo?: number;
  style?: StyleProp<ViewStyle>;
}): React.ReactNode {
  const reduced = useReducedMotion();
  const scale = useRef(new Animated.Value(1)).current;
  const previous = useRef(props.value);
  const mounted = useRef(false);

  useEffect(() => {
    if (!mounted.current) {
      mounted.current = true;
      previous.current = props.value;
      return;
    }
    if (previous.current === props.value) return;
    previous.current = props.value;
    if (reduced) return;
    scale.setValue(props.scaleTo ?? motionScale.pop);
    Animated.spring(scale, { toValue: 1, ...motionSpring.bump, useNativeDriver: true }).start();
  }, [props.value, props.scaleTo, reduced, scale]);

  return (
    <Animated.View style={[props.style, { transform: [{ scale }] }]}>
      {props.children}
    </Animated.View>
  );
}
