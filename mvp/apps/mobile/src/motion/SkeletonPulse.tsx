import React, { useEffect, useRef } from "react";
import { Animated, StyleSheet, View, type StyleProp, type ViewStyle } from "react-native";
import { motionEasing, motionLoop } from "./motionTokens";
import { spacing, useTheme, useThemedStyles, type Palette } from "../theme";
import { useReducedMotion } from "./useReducedMotion";

// Ambient opacity pulse shared by every skeleton surface.
function useSkeletonPulse(): { value: Animated.Value; reduced: boolean } {
  const reduced = useReducedMotion();
  const value = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    if (reduced) return;
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(value, { toValue: 1, duration: motionLoop.period / 2, easing: motionEasing.ambient, useNativeDriver: true }),
        Animated.timing(value, { toValue: 0, duration: motionLoop.period / 2, easing: motionEasing.ambient, useNativeDriver: true }),
      ]),
    );
    loop.start();
    return () => loop.stop();
  }, [value, reduced]);
  return { value, reduced };
}

export function SkeletonBlock(props: {
  width?: number | `${number}%`;
  height: number;
  radius?: number;
  style?: StyleProp<ViewStyle>;
}): React.ReactNode {
  const { colors } = useTheme();
  const pulse = useSkeletonPulse();
  return (
    <Animated.View
      style={[
        { width: props.width ?? "100%", height: props.height, borderRadius: props.radius ?? 8, backgroundColor: colors.neutralBg },
        { opacity: pulse.reduced ? 0.7 : pulse.value.interpolate({ inputRange: [0, 1], outputRange: [1, 0.45] }) },
        props.style,
      ]}
    />
  );
}

// Composed skeletons mirror the real surface geometry so layout does not shift
// when data lands. One shell, four surfaces (catalog / retailer orders /
// vendor orders / vendor inventory).
function SkeletonCard(props: { children: React.ReactNode; style?: StyleProp<ViewStyle> }): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return <View style={[styles.skeletonCard, props.style]}>{props.children}</View>;
}

export function RetailerCatalogSkeleton(): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <View>
      <SkeletonBlock height={48} radius={14} style={styles.gap} />
      {[0, 1].map((index) => (
        <SkeletonCard key={index}>
          <View style={styles.row}>
            <SkeletonBlock width={56} height={56} radius={14} />
            <View style={styles.fill}>
              <SkeletonBlock width={"70%"} height={14} />
              <SkeletonBlock width={"40%"} height={11} style={styles.gapSm} />
            </View>
          </View>
        </SkeletonCard>
      ))}
    </View>
  );
}

export function RetailerOrderSkeleton(): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <View>
      {[0, 1, 2].map((index) => (
        <SkeletonCard key={index}>
          <SkeletonBlock width={72} height={24} radius={999} />
          <SkeletonBlock width={"55%"} height={14} style={styles.gapSm} />
          <SkeletonBlock width={"35%"} height={11} />
        </SkeletonCard>
      ))}
    </View>
  );
}

export function VendorOrderSkeleton(): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <View>
      <View style={styles.grid2}>
        {[0, 1, 2, 3].map((index) => (
          <SkeletonBlock key={index} height={76} radius={16} style={styles.gridCell} />
        ))}
      </View>
      {[0, 1].map((index) => (
        <SkeletonCard key={index}>
          <SkeletonBlock width={80} height={24} radius={999} />
          <SkeletonBlock width={"60%"} height={14} style={styles.gapSm} />
          <SkeletonBlock width={120} height={40} radius={12} />
        </SkeletonCard>
      ))}
    </View>
  );
}

export function VendorInventorySkeleton(): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  return (
    <View>
      {[0, 1, 2].map((index) => (
        <SkeletonCard key={index}>
          <View style={styles.row}>
            <SkeletonBlock width={48} height={48} radius={14} />
            <View style={styles.fill}>
              <SkeletonBlock width={"50%"} height={14} />
              <SkeletonBlock width={"30%"} height={11} style={styles.gapSm} />
            </View>
            <SkeletonBlock width={64} height={40} radius={10} />
          </View>
        </SkeletonCard>
      ))}
    </View>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
    skeletonCard: { backgroundColor: colors.surface, borderColor: colors.border, borderWidth: 1, borderRadius: 16, padding: spacing.lg, marginBottom: spacing.md },
    row: { flexDirection: "row", alignItems: "center", gap: spacing.md },
    fill: { flex: 1 },
    grid2: { flexDirection: "row", flexWrap: "wrap", gap: spacing.md, marginBottom: spacing.md },
    gridCell: { flexGrow: 1, flexBasis: "45%" },
    gap: { marginBottom: spacing.md },
    gapSm: { marginTop: spacing.sm },
  });
}
