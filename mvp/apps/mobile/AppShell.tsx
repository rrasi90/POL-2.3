import { StatusBar } from "expo-status-bar";
import { useFonts } from "expo-font";
import React, { useCallback, useEffect, useState } from "react";
import { Pressable, SafeAreaView, StyleSheet, Text } from "react-native";
import { clearSession, getToken, healthz, restoreSession } from "./src/api";
import { AccountMobileScreen } from "./src/screens/AccountMobileScreen";
import { OfflineBanner } from "./src/components/OfflineBanner";
import { LoginScreen } from "./src/screens/LoginScreen";
import { OrderDetailMobileScreen } from "./src/screens/OrderDetailMobileScreen";
import { ScreenTransition } from "./src/motion/ScreenTransition";
import { SplashSequence } from "./src/motion/SplashSequence";
import { ThemeProvider, useTheme, useThemedStyles } from "./src/theme";
import type { Role } from "./src/types";

export type WorkspaceProps<R extends Role> = { role: R; onOpenOrder: (orderId: string) => void; onOpenAccount: () => void };

type AppShellProps<R extends Role> = {
  appName: string;
  allowedRoles: readonly R[];
  workspace: (props: WorkspaceProps<R>) => React.ReactNode;
  orderMode: "retailer" | "vendor";
};

export function AppShell<R extends Role>(props: AppShellProps<R>): React.ReactNode {
  return <ThemeProvider><AppContent {...props} /></ThemeProvider>;
}

function AppContent<R extends Role>(props: AppShellProps<R>): React.ReactNode {
  const { mode } = useTheme();
  const styles = useThemedStyles(makeStyles);
  const [fontsLoaded] = useFonts({
    "Vazirmatn-Regular": require("./assets/fonts/Vazirmatn-Regular.ttf"),
    "Vazirmatn-SemiBold": require("./assets/fonts/Vazirmatn-SemiBold.ttf"),
    "Vazirmatn-Bold": require("./assets/fonts/Vazirmatn-Bold.ttf"),
  });
  const [route, setRoute] = useState<
    { name: "login" } | { name: "workspace"; role: R } |
    { name: "order-detail"; orderId: string; role: R } | { name: "account"; role: R }
  >({ name: "login" });
  const [role, setRole] = useState<R | null>(null);
  const [booted, setBooted] = useState(false);
  const [splashExited, setSplashExited] = useState(false);

  const refresh = useCallback(async () => {
    const restored = await restoreSession();
    if (restored.restored && restored.role && props.allowedRoles.includes(restored.role as R)) {
      const restoredRole = restored.role as R;
      setRole(restoredRole);
      setRoute({ name: "workspace", role: restoredRole });
    } else if (restored.restored) {
      await clearSession();
      setRole(null);
      setRoute({ name: "login" });
    } else {
      await healthz();
    }
    setBooted(true);
  }, [props.allowedRoles]);

  useEffect(() => { void refresh(); }, [refresh]);

  function onLogout(): void {
    void clearSession();
    setRole(null);
    setRoute({ name: "login" });
  }

  function onAuthed(nextRole: Role): void {
    if (!props.allowedRoles.includes(nextRole as R)) {
      void clearSession();
      setRole(null);
      setRoute({ name: "login" });
      return;
    }
    const scopedRole = nextRole as R;
    setRole(scopedRole);
    setRoute({ name: "workspace", role: scopedRole });
  }

  if (!fontsLoaded || !booted || !splashExited) {
    return (
      <SafeAreaView style={styles.root}>
        <SplashSequence ready={fontsLoaded && booted} onExited={() => setSplashExited(true)} />
        <StatusBar style={mode === "night" ? "light" : "dark"} />
      </SafeAreaView>
    );
  }
  if (!getToken()) return (
    <SafeAreaView style={styles.root}>
      <ScreenTransition transitionKey="login" style={styles.routeHost}>
        <LoginScreen onAuthed={onAuthed} allowedRoles={props.allowedRoles} appName={props.appName} />
      </ScreenTransition>
      <StatusBar style={mode === "night" ? "light" : "dark"} />
    </SafeAreaView>
  );

  const currentRole = route.name === "login" ? role : route.role;
  const routeKey = route.name === "order-detail" ? `order-detail:${route.orderId}` : route.name;
  return (
    <SafeAreaView style={styles.root}>
      <OfflineBanner />
      {currentRole && props.appName !== "پل بازار" && route.name !== "account" && route.name !== "order-detail" ? (
        <SafeAreaView style={styles.accountBar}>
          <Pressable accessibilityRole="button" onPress={() => setRoute({ name: "account", role: currentRole })} style={styles.accountButton}>
            <Text style={styles.accountText}>حساب / اعلان‌ها</Text>
          </Pressable>
        </SafeAreaView>
      ) : null}
      <ScreenTransition transitionKey={routeKey} style={styles.routeHost}>
        {route.name === "account" ? (
          <AccountMobileScreen role={route.role} onLogout={onLogout} onBack={() => setRoute({ name: "workspace", role: route.role })} />
        ) : route.name === "order-detail" ? (
          <OrderDetailMobileScreen mode={props.orderMode} role={route.role} orderId={route.orderId} onBack={() => setRoute({ name: "workspace", role: route.role })} />
        ) : currentRole ? (
          props.workspace({ role: currentRole, onOpenOrder: (orderId) => setRoute({ name: "order-detail", orderId, role: currentRole }), onOpenAccount: () => setRoute({ name: "account", role: currentRole }) })
        ) : (
          <LoginScreen onAuthed={onAuthed} allowedRoles={props.allowedRoles} appName={props.appName} />
        )}
      </ScreenTransition>
      <StatusBar style={mode === "night" ? "light" : "dark"} />
    </SafeAreaView>
  );
}

function makeStyles(colors: { bg: string; surface: string; border: string; text: string }) {
  return StyleSheet.create({
    root: { flex: 1, backgroundColor: colors.bg, direction: "rtl" },
    routeHost: { flex: 1 },
    accountBar: { backgroundColor: colors.bg, paddingHorizontal: 12, paddingTop: 6, direction: "rtl" },
    accountButton: { alignSelf: "flex-end", borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, borderRadius: 999, paddingHorizontal: 12, paddingVertical: 6 },
    accountText: { color: colors.text, fontSize: 11, fontWeight: "600" },
  });
}
