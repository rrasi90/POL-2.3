import React, { useEffect, useRef, useState } from "react";
import { Animated, StyleSheet, Text } from "react-native";
import { motionDrift, motionDuration, motionEasing, motionSpring } from "./motionTokens";
import { spacing, useThemedStyles, type Palette } from "../theme";
import { BrandMark } from "../components/ui";
import { useReducedMotion } from "./useReducedMotion";

// JS-side brand moment (layer B of the two-layer splash policy): the native
// launch splash prevents the white flash; this sequence runs in parallel with
// real boot (fonts + session + healthz) and is cut short the moment boot is
// ready — boot latency is never extended.
export function SplashSequence(props: { ready: boolean; onExited?: () => void }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const reduced = useReducedMotion();
  const mark = useRef(new Animated.Value(0)).current;
  const wordmark = useRef(new Animated.Value(0)).current;
  const tagline = useRef(new Animated.Value(0)).current;
  const exit = useRef(new Animated.Value(1)).current;
  const [exiting, setExiting] = useState(false);
  const exitedCallback = useRef(props.onExited);
  exitedCallback.current = props.onExited;

  useEffect(() => {
    if (reduced) {
      mark.setValue(1);
      wordmark.setValue(1);
      tagline.setValue(1);
      return;
    }
    const animation = Animated.sequence([
      Animated.spring(mark, { toValue: 1, ...motionSpring.pop, useNativeDriver: true }),
      Animated.timing(wordmark, { toValue: 1, duration: motionDuration.base, easing: motionEasing.decelerate, useNativeDriver: true }),
      Animated.timing(tagline, { toValue: 1, duration: motionDuration.base, delay: 60, easing: motionEasing.decelerate, useNativeDriver: true }),
    ]);
    animation.start();
    return () => animation.stop();
  }, [reduced, mark, wordmark, tagline]);

  useEffect(() => {
    if (props.ready) setExiting(true);
  }, [props.ready]);

  useEffect(() => {
    if (!exiting) return;
    mark.setValue(1);
    wordmark.setValue(1);
    tagline.setValue(1);
    if (reduced) {
      exitedCallback.current?.();
      return;
    }
    const animation = Animated.timing(exit, { toValue: 0, duration: motionDuration.base, easing: motionEasing.accelerate, useNativeDriver: true });
    animation.start(({ finished }) => {
      if (finished) exitedCallback.current?.();
    });
    return () => animation.stop();
  }, [exiting, reduced, exit, mark, wordmark, tagline]);

  return (
    <Animated.View style={[styles.host, { opacity: exit }]}>
      <Animated.View style={{ opacity: mark, transform: [{ scale: mark.interpolate({ inputRange: [0, 1], outputRange: [0.7, 1] }) }] }}>
        <BrandMark />
      </Animated.View>
      <Animated.View style={{ opacity: wordmark, transform: [{ translateY: wordmark.interpolate({ inputRange: [0, 1], outputRange: [motionDrift.sm, 0] }) }] }}>
        <Text style={styles.wordmark}>پل</Text>
      </Animated.View>
      <Animated.View style={{ opacity: tagline }}>
        <Text style={styles.tagline}>خرید عمده، ساده‌تر از همیشه</Text>
      </Animated.View>
    </Animated.View>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
    host: { flex: 1, backgroundColor: colors.bg, alignItems: "center", justifyContent: "center" },
    wordmark: { color: colors.text, fontSize: 30, fontWeight: "900", marginTop: spacing.md },
    tagline: { color: colors.textSecondary, fontSize: 12, marginTop: 3 },
  });
}