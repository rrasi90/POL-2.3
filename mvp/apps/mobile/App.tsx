import { StatusBar } from "expo-status-bar";
import React, { useCallback, useEffect, useState } from "react";
import { Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";
import { getToken, healthz } from "./src/api";
import { AssistedOrderScreen } from "./src/screens/AssistedOrderScreen";
import { FieldTaskDetailScreen } from "./src/screens/FieldTaskDetailScreen";
import { FieldTaskListScreen } from "./src/screens/FieldTaskListScreen";
import { LoginScreen } from "./src/screens/LoginScreen";
import { OpsMobileScreen } from "./src/screens/OpsMobileScreen";
import { RetailerMobileScreen } from "./src/screens/RetailerMobileScreen";
import { VendorMobileScreen } from "./src/screens/VendorMobileScreen";
import { colors, getThemeMode, setThemeMode, type ThemeMode } from "./src/theme";
import type { Role, Route } from "./src/types";

export default function App(): React.ReactNode {
  const [route, setRoute] = useState<Route>({ name: "login" });
  const [role, setRole] = useState<Role | null>(null);
  const [booted, setBooted] = useState(false);
  const [themeMode, setThemeModeState] = useState<ThemeMode>(getThemeMode());

  const refresh = useCallback(() => {
    void healthz().finally(() => setBooted(true));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  function toggleTheme(): void {
    const next = themeMode === "light" ? "night" : "light";
    setThemeMode(next);
    setThemeModeState(next);
  }

  function onAuthed(nextRole: Role): void {
    setRole(nextRole);
    setRoute(
      nextRole === "FIELD_ACTIVATOR"
        ? { name: "field" }
        : { name: "workspace", role: nextRole },
    );
    refresh();
  }

  if (!booted) return <SafeAreaView style={styles.root} />;

  if (!getToken()) {
    return (
      <SafeAreaView style={styles.root}>
        <LoginScreen onAuthed={onAuthed} />
        <StatusBar style="dark" />
      </SafeAreaView>
    );
  }

  const currentRole = route.name === "workspace" ? route.role : role;

  return (
    <SafeAreaView style={styles.root}>
      <View style={styles.themeBar}>
        <Pressable accessibilityRole="button" onPress={toggleTheme} style={styles.themeButton}>
          <Text style={styles.themeText}>{themeMode === "light" ? "حالت شب" : "حالت روز"}</Text>
        </Pressable>
      </View>
      {route.name === "field" ? (
        <FieldTaskListScreen
          onOpenTask={(taskId) => setRoute({ name: "task", taskId })}
          onAssistedOrder={() => setRoute({ name: "assisted" })}
        />
      ) : route.name === "task" ? (
        <FieldTaskDetailScreen taskId={route.taskId} onBack={() => setRoute({ name: "field" })} />
      ) : route.name === "assisted" ? (
        <AssistedOrderScreen onBack={() => setRoute({ name: "field" })} />
      ) : currentRole === "RETAILER_OWNER" || currentRole === "RETAILER_STAFF" ? (
        <RetailerMobileScreen role={currentRole} />
      ) : currentRole === "VENDOR_OWNER" || currentRole === "VENDOR_STAFF" ? (
        <VendorMobileScreen role={currentRole} />
      ) : currentRole === "OPS_AGENT" || currentRole === "ADMIN_SUPER" ? (
        <OpsMobileScreen role={currentRole} />
      ) : (
        <LoginScreen onAuthed={onAuthed} />
      )}
      <StatusBar style="dark" />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.bg },
  themeBar: { alignItems: "flex-start", paddingHorizontal: 12, paddingTop: 8 },
  themeButton: { borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, borderRadius: 999, paddingHorizontal: 12, paddingVertical: 6 },
  themeText: { color: colors.text, fontSize: 11, fontWeight: "600" },
});
