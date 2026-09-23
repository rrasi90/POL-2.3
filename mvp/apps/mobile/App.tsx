import { StatusBar } from "expo-status-bar";
import React, { useCallback, useEffect, useState } from "react";
import { SafeAreaView, StyleSheet } from "react-native";
import { getToken, healthz, setToken } from "./src/api";
import { AssistedOrderScreen } from "./src/screens/AssistedOrderScreen";
import { FieldTaskDetailScreen } from "./src/screens/FieldTaskDetailScreen";
import { FieldTaskListScreen } from "./src/screens/FieldTaskListScreen";
import { LoginScreen } from "./src/screens/LoginScreen";
import { colors } from "./src/theme";
import type { Route } from "./src/types";

/**
 * Phase 3 Field-first Expo shell.
 * Screens: F-01 list, F-02/F-04 task detail, F-03 assisted order, F-05 offline banner.
 * No Driver App (D-023). Barcode = D-028 where inventory.scan (not Field MVP).
 */
export default function App(): React.ReactNode {
  const [route, setRoute] = useState<Route>({ name: "login" });
  const [booted, setBooted] = useState(false);

  const refresh = useCallback(() => {
    void healthz().finally(() => setBooted(true));
  }, []);

  useEffect(() => {
    refresh();
    if (getToken()) setRoute({ name: "field" });
  }, [refresh]);

  if (!booted) {
    return <SafeAreaView style={styles.root} />;
  }

  if (!getToken() && route.name !== "login") {
    return (
      <SafeAreaView style={styles.root}>
        <LoginScreen
          onAuthed={() => {
            setRoute({ name: "field" });
            refresh();
          }}
        />
        <StatusBar style="dark" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.root}>
      {route.name === "login" ? (
        <LoginScreen
          onAuthed={() => {
            setRoute({ name: "field" });
            refresh();
          }}
        />
      ) : route.name === "field" ? (
        <FieldTaskListScreen
          onOpenTask={(taskId) => setRoute({ name: "task", taskId })}
          onAssistedOrder={() => setRoute({ name: "assisted" })}
        />
      ) : route.name === "task" ? (
        <FieldTaskDetailScreen taskId={route.taskId} onBack={() => setRoute({ name: "field" })} />
      ) : (
        <AssistedOrderScreen onBack={() => setRoute({ name: "field" })} />
      )}
      <StatusBar style="dark" />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.bg },
});
