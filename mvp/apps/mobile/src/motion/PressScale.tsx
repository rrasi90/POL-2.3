import React, { useCallback, useEffect, useRef } from "react";
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
    scale.stopAnimation();
    if (disabled || reduced) {
      scale.setValue(1);
      return;
    }
    Animated.spring(scale, { toValue: scaleTo, ...motionSpring.press, useNativeDriver: true }).start();
  }, [scale, disabled, reduced, scaleTo]);

  const pressOut = useCallback(() => {
    scale.stopAnimation();
    if (reduced) {
      scale.setValue(1);
      return;
    }
    Animated.spring(scale, { toValue: 1, ...motionSpring.press, useNativeDriver: true }).start();
  }, [scale, reduced]);

  useEffect(() => () => {
    scale.stopAnimation();
    scale.setValue(1);
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