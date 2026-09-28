import { StatusBar } from "expo-status-bar";
import React, { useCallback, useEffect, useState } from "react";
import { Pressable, SafeAreaView, StyleSheet, Text } from "react-native";
import { clearSession, getToken, healthz, restoreSession } from "./src/api";
import { AccountMobileScreen } from "./src/screens/AccountMobileScreen";
import { AssistedOrderScreen } from "./src/screens/AssistedOrderScreen";
import { FieldTaskDetailScreen } from "./src/screens/FieldTaskDetailScreen";
import { FieldTaskListScreen } from "./src/screens/FieldTaskListScreen";
import { LoginScreen } from "./src/screens/LoginScreen";
import { OpsMobileScreen } from "./src/screens/OpsMobileScreen";
import { OrderDetailMobileScreen } from "./src/screens/OrderDetailMobileScreen";
import { RetailerMobileScreen } from "./src/screens/RetailerMobileScreen";
import { VendorMobileScreen } from "./src/screens/VendorMobileScreen";
import { APP_NAME, APP_VARIANT, isAllowedRole } from "./src/appVariant";
import { ThemeProvider, useTheme, useThemedStyles } from "./src/theme";
import type { Role, Route } from "./src/types";

export default function App(): React.ReactNode {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

function AppContent(): React.ReactNode {
  const { mode } = useTheme();
  const styles = useThemedStyles(makeStyles);
  const [route, setRoute] = useState<Route>({ name: "login" });
  const [role, setRole] = useState<Role | null>(null);
  const [booted, setBooted] = useState(false);

  const refresh = useCallback(async () => {
    const restored = await restoreSession();
    if (restored.restored && restored.role && isAllowedRole(restored.role)) {
      const restoredRole = restored.role as Role;
      setRole(restoredRole);
      setRoute({ name: "workspace", role: restoredRole });
    } else if (restored.restored) {
      await clearSession();
      setRole(null);
      setRoute({ name: "login" });
      setBooted(true);
      return;
    } else {
      await healthz();
    }
    setBooted(true);
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  function onLogout(): void {
    void clearSession();
    setRole(null);
    setRoute({ name: "login" });
  }

  function onAuthed(nextRole: Role): void {
    if (!isAllowedRole(nextRole)) {
      void clearSession();
      setRole(null);
      setRoute({ name: "login" });
      return;
    }
    setRole(nextRole);
    setRoute({ name: "workspace", role: nextRole });
  }

  if (!booted) return <SafeAreaView style={styles.root} />;

  if (!getToken()) {
    return (
      <SafeAreaView style={styles.root}>
        <LoginScreen onAuthed={onAuthed} allowedRoles={APP_VARIANT === "vendor" ? ["VENDOR_OWNER", "VENDOR_STAFF"] : ["RETAILER_OWNER", "RETAILER_STAFF"]} appName={APP_NAME} />
        <StatusBar style={mode === "night" ? "light" : "dark"} />
      </SafeAreaView>
    );
  }

  const currentRole =
    route.name === "workspace" || route.name === "order-detail" || route.name === "account"
      ? route.role
      : role;

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
          onLogout={onLogout}
          onBack={() => setRoute({ name: "workspace", role: route.role })}
        />
      ) : route.name === "order-detail" ? (
        <OrderDetailMobileScreen
          mode={route.role === "VENDOR_OWNER" || route.role === "VENDOR_STAFF" ? "vendor" : "retailer"}
          role={route.role}
          orderId={route.orderId}
          onBack={() => setRoute({ name: "workspace", role: route.role })}
        />
      ) : APP_VARIANT === "retailer" && (currentRole === "RETAILER_OWNER" || currentRole === "RETAILER_STAFF") ? (
        <RetailerMobileScreen
          role={currentRole}
          onOpenOrder={(orderId) => setRoute({ name: "order-detail", orderId, role: currentRole })}
        />
      ) : APP_VARIANT === "vendor" && (currentRole === "VENDOR_OWNER" || currentRole === "VENDOR_STAFF") ? (
        <VendorMobileScreen
          role={currentRole}
          onOpenOrder={(orderId) => setRoute({ name: "order-detail", orderId, role: currentRole })}
        />
      ) : (
        <LoginScreen onAuthed={onAuthed} allowedRoles={APP_VARIANT === "vendor" ? ["VENDOR_OWNER", "VENDOR_STAFF"] : ["RETAILER_OWNER", "RETAILER_STAFF"]} appName={APP_NAME} />
      )}
      <StatusBar style={mode === "night" ? "light" : "dark"} />
    </SafeAreaView>
  );
}

function makeStyles(colors: { bg: string; surface: string; border: string; text: string }) {
  return StyleSheet.create({
    root: { flex: 1, backgroundColor: colors.bg },
    accountBar: { backgroundColor: colors.bg, paddingHorizontal: 12, paddingTop: 6 },
    accountButton: { alignSelf: "flex-start", borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, borderRadius: 999, paddingHorizontal: 12, paddingVertical: 6 },
    accountText: { color: colors.text, fontSize: 11, fontWeight: "600" },
  });
}
