import { StatusBar } from "expo-status-bar";
import React, { useCallback, useEffect, useState } from "react";
import { Pressable, SafeAreaView, StyleSheet, Text } from "react-native";
import { getToken, healthz } from "./src/api";
import { AccountMobileScreen } from "./src/screens/AccountMobileScreen";
import { AssistedOrderScreen } from "./src/screens/AssistedOrderScreen";
import { FieldTaskDetailScreen } from "./src/screens/FieldTaskDetailScreen";
import { FieldTaskListScreen } from "./src/screens/FieldTaskListScreen";
import { LoginScreen } from "./src/screens/LoginScreen";
import { OpsMobileScreen } from "./src/screens/OpsMobileScreen";
import { OrderDetailMobileScreen } from "./src/screens/OrderDetailMobileScreen";
import { RetailerMobileScreen } from "./src/screens/RetailerMobileScreen";
import { VendorMobileScreen } from "./src/screens/VendorMobileScreen";
import { colors } from "./src/theme";
import type { Role, Route } from "./src/types";

export default function App(): React.ReactNode {
  const [route, setRoute] = useState<Route>({ name: "login" });
  const [role, setRole] = useState<Role | null>(null);
  const [booted, setBooted] = useState(false);

  const refresh = useCallback(() => {
    void healthz().finally(() => setBooted(true));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

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

  const currentRole =
    route.name === "workspace" || route.name === "order-detail" || route.name === "account" ? route.role : role;

  return (
    <SafeAreaView style={styles.root}>
      {currentRole && route.name !== "account" && route.name !== "order-detail" ? (
        <SafeAreaView style={styles.accountBar}>
          <Pressable accessibilityRole="button" onPress={() => setRoute({ name: "account", role: currentRole })} style={styles.accountButton}>
            <Text style={styles.accountText}>حساب / اعلان‌ها</Text>
          </Pressable>
        </SafeAreaView>
      ) : null}
      {route.name === "account" ? (
        <AccountMobileScreen
          role={route.role}
          onBack={() =>
            setRoute(route.role === "FIELD_ACTIVATOR"
              ? { name: "field" }
              : { name: "workspace", role: route.role })
          }
        />
      ) : route.name === "field" ? (
        <FieldTaskListScreen
          onOpenTask={(taskId) => setRoute({ name: "task", taskId })}
          onAssistedOrder={() => setRoute({ name: "assisted" })}
        />
      ) : route.name === "task" ? (
        <FieldTaskDetailScreen taskId={route.taskId} onBack={() => setRoute({ name: "field" })} />
      ) : route.name === "assisted" ? (
        <AssistedOrderScreen onBack={() => setRoute({ name: "field" })} />
      ) : route.name === "order-detail" ? (
        <OrderDetailMobileScreen
          mode={route.role === "VENDOR_OWNER" || route.role === "VENDOR_STAFF" ? "vendor" : "retailer"}
          role={route.role}
          orderId={route.orderId}
          onBack={() => setRoute({ name: "workspace", role: route.role })}
        />
      ) : currentRole === "RETAILER_OWNER" || currentRole === "RETAILER_STAFF" ? (
        <RetailerMobileScreen
          role={currentRole}
          onOpenOrder={(orderId) => setRoute({ name: "order-detail", orderId, role: currentRole })}
        />
      ) : currentRole === "VENDOR_OWNER" || currentRole === "VENDOR_STAFF" ? (
        <VendorMobileScreen
          role={currentRole}
          onOpenOrder={(orderId) => setRoute({ name: "order-detail", orderId, role: currentRole })}
        />
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
  accountBar: { backgroundColor: colors.bg, paddingHorizontal: 12, paddingTop: 6 },
  accountButton: { alignSelf: "flex-start", borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, borderRadius: 999, paddingHorizontal: 12, paddingVertical: 6 },
  accountText: { color: colors.text, fontSize: 11, fontWeight: "600" },
});
