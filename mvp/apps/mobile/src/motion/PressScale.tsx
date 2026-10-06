import React, { useCallback, useRef } from "react";
import { Animated, Pressable, type AccessibilityRole, type StyleProp, type ViewStyle } from "react-native";
import { motionScale, motionSpring } from "./motionTokens";
import { useReducedMotion } from "./useReducedMotion";

// Shared animated press behaviour. The scale lives on an outer Animated.View so
// the whole surface (background + border) scales, and plain Pressable keeps its
// pressed-state API untouched.
export function usePressScale(options?: { disabled?: boolean; scaleTo?: number }): {
  scale: Animated.Value;
  pressIn: () => void;
  pressOut: () => void;
} {
  const reduced = useReducedMotion();
  const scale = useRef(new Animated.Value(1)).current;
  const disabled = options?.disabled ?? false;
  const scaleTo = options?.scaleTo ?? motionScale.press;

  const pressIn = useCallback(() => {
    if (disabled || reduced) return;
    Animated.spring(scale, { toValue: scaleTo, ...motionSpring.press, useNativeDriver: true }).start();
  }, [scale, disabled, reduced, scaleTo]);

  // Restore unconditionally — it corrects state, it is not itself motion.
  const pressOut = useCallback(() => {
    Animated.spring(scale, { toValue: 1, ...motionSpring.press, useNativeDriver: true }).start();
  }, [scale]);

  return { scale, pressIn, pressOut };
}

export function PressScale(props: {
  children: React.ReactNode;
  onPress?: () => void;
  disabled?: boolean;
  scaleTo?: number;
  style?: StyleProp<ViewStyle>;
  accessibilityLabel?: string;
  accessibilityRole?: AccessibilityRole;
  testID?: string;
}): React.ReactNode {
  const { scale, pressIn, pressOut } = usePressScale({ disabled: props.disabled, scaleTo: props.scaleTo });
  return (
    <Animated.View style={[props.style, { transform: [{ scale }] }]}>
      <Pressable
        accessibilityRole={props.accessibilityRole ?? "button"}
        accessibilityLabel={props.accessibilityLabel}
        accessibilityState={props.disabled ? { disabled: true } : undefined}
        testID={props.testID}
        onPress={props.onPress}
        onPressIn={pressIn}
        onPressOut={pressOut}
        disabled={props.disabled}
      >
        {props.children}
      </Pressable>
    </Animated.View>
  );
}
