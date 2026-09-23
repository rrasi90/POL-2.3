import React, { useEffect, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { healthz, isOnline, subscribeOnline } from "../api";
import { colors, spacing } from "../theme";

/** F-05 weak network / offline banner — connection status + retry (MVP boundary). */
export function OfflineBanner(): React.ReactNode {
  const [online, setOnline] = useState(isOnline());
  useEffect(() => subscribeOnline(setOnline), []);
  if (online) return null;
  return (
    <View style={styles.banner} accessibilityRole="alert">
      <Text style={styles.title}>آفلاین — F-05</Text>
      <Text style={styles.body}>اتصال شبکه قطع است. تغییرات هنگام اتصال مجدد همگام‌سازی می‌شوند.</Text>
      <Pressable
        accessibilityRole="button"
        onPress={() => void healthz()}
        style={styles.retry}
      >
        <Text style={styles.retryText}>تلاش مجدد</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
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
  retryText: { color: "#fff", fontSize: 12, fontWeight: "600" },
});
