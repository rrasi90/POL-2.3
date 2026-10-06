import React, { useEffect, useRef } from "react";
import { Animated, type StyleProp, type ViewStyle } from "react-native";
import { motionDrift, motionDuration, motionEasing } from "./motionTokens";
import { useReducedMotion } from "./useReducedMotion";

// Enter-only transition for route/tab switches, keyed by semantic identity.
// Progress is adjusted during render (not in an effect) so the incoming
// surface never paints a frame at the stale opacity. Exit choreography is
// deliberately out of scope — no unmount animations.
export function ScreenTransition(props: {
  transitionKey: string;
  children: React.ReactNode;
  duration?: number;
  style?: StyleProp<ViewStyle>;
}): React.ReactNode {
  const reduced = useReducedMotion();
  const progress = useRef(new Animated.Value(0)).current;
  const lastKey = useRef(props.transitionKey);
  if (lastKey.current !== props.transitionKey) {
    lastKey.current = props.transitionKey;
    progress.setValue(reduced ? 1 : 0);
  }

  useEffect(() => {
    if (reduced) {
      progress.setValue(1);
      return;
    }
    const animation = Animated.timing(progress, {
      toValue: 1,
      duration: props.duration ?? motionDuration.base,
      easing: motionEasing.standard,
      useNativeDriver: true,
    });
    animation.start();
    return () => animation.stop();
  }, [progress, reduced, props.transitionKey, props.duration]);

  return (
    <Animated.View
      style={[
        props.style,
        {
          opacity: progress,
          transform: [{ translateY: progress.interpolate({ inputRange: [0, 1], outputRange: [motionDrift.sm, 0] }) }],
        },
      ]}
    >
      {props.children}
    </Animated.View>
  );
}
