import React, { useCallback, useEffect, useRef, useState } from "react";
import { Animated, type StyleProp, type ViewStyle } from "react-native";
import { motionShake } from "./motionTokens";
import { useReducedMotion } from "./useReducedMotion";

// Trigger by revision counter, not message text — repeating the same error must
// animate again. Screens: const [revision, bumpRevision] = useErrorTrigger();
export function useErrorTrigger(): [number, () => void] {
  const [trigger, setTrigger] = useState(0);
  const bump = useCallback(() => setTrigger((value) => value + 1), []);
  return [trigger, bump];
}

export function ErrorShake(props: {
  trigger: number;
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
}): React.ReactNode {
  const reduced = useReducedMotion();
  const translateX = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (props.trigger <= 0 || reduced) return;
    translateX.setValue(0);
    const a = motionShake.amplitude;
    const s = motionShake.step;
    const animation = Animated.sequence([
      Animated.timing(translateX, { toValue: -a, duration: s, useNativeDriver: true }),
      Animated.timing(translateX, { toValue: a, duration: s * 2, useNativeDriver: true }),
      Animated.timing(translateX, { toValue: -a / 2, duration: s, useNativeDriver: true }),
      Animated.timing(translateX, { toValue: a / 2, duration: s, useNativeDriver: true }),
      Animated.timing(translateX, { toValue: 0, duration: s, useNativeDriver: true }),
    ]);
    animation.start();
    return () => animation.stop();
  }, [props.trigger, reduced, translateX]);

  return (
    <Animated.View style={[props.style, { transform: [{ translateX }] }]}>
      {props.children}
    </Animated.View>
  );
}
