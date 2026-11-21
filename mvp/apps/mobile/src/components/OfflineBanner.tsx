import React, { useEffect, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { healthz, isOnline, subscribeOnline } from "../api";
import { spacing, useThemedStyles, type Palette } from "../theme";
import { SlideIn } from "../motion/SlideIn";

export function OfflineBanner(): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const [online, setOnline] = useState(isOnline());

  useEffect(() => {
    const unsubscribe = subscribeOnline(setOnline);
    // Capture a state transition that may occur before the subscription effect runs.
    setOnline(isOnline());
    return unsubscribe;
  }, []);

  if (online) return null;

  return (
    <SlideIn direction="down">
      <View style={styles.banner} accessibilityRole="alert">
        <Text style={styles.title}>اتصال شبکه در دسترس نیست</Text>
        <Text style={styles.body}>
          درخواست ناموفق بوده است. اتصال را بررسی کنید و دوباره تلاش کنید.
        </Text>
        <Pressable accessibilityRole="button" onPress={() => void healthz()} style={styles.retry}>
          <Text style={styles.retryText}>تلاش مجدد</Text>
        </Pressable>
      </View>
    </SlideIn>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
  banner: {
    backgroundColor: colors.warningBg,
    borderColor: colors.warning,
    borderWidth: 1,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  title: { color: colors.warning, fontWeight: "700", fontSize: 14 },
  body: { color: colors.textSecondary, fontSize: 12, marginTop: 4, lineHeight: 18 },
  retry: {
    marginTop: spacing.sm,
    alignSelf: "flex-start",
    backgroundColor: colors.warning,
    borderRadius: 8,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs + 2,
  },
  retryText: { color: colors.warning, fontSize: 12, fontWeight: "600", fontFamily: "Vazirmatn-SemiBold" },
  });
}
