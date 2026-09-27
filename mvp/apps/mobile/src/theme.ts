import React, { createContext, useCallback, useContext, useMemo, useState } from "react";
import { Appearance, StyleSheet } from "react-native";

export type ThemeMode = "light" | "night";

export type Palette = {
  bg: string;
  surface: string;
  border: string;
  text: string;
  textSecondary: string;
  textMuted: string;
  brand: string;
  warning: string;
  warningBg: string;
  success: string;
  successBg: string;
  danger: string;
  dangerBg: string;
  infoBg: string;
  neutralBg: string;
};

const palettes: Record<ThemeMode, Palette> = {
  light: {
    bg: "#F7F9FC",
    surface: "#FFFFFF",
    border: "#E2E8F0",
    text: "#0F172A",
    textSecondary: "#475569",
    textMuted: "#64748B",
    brand: "#2563EB",
    warning: "#B45309",
    warningBg: "#FFFBEB",
    success: "#15803D",
    successBg: "#F0FDF4",
    danger: "#B91C1C",
    dangerBg: "#FEF2F2",
    infoBg: "#EFF6FF",
    neutralBg: "#F1F5F9",
  },
  night: {
    bg: "#0F141C",
    surface: "#151C27",
    border: "#2A3646",
    text: "#F8FAFC",
    textSecondary: "#CBD5E1",
    textMuted: "#94A3B8",
    brand: "#60A5FA",
    warning: "#FBBF24",
    warningBg: "#2A2415",
    success: "#4ADE80",
    successBg: "#123321",
    danger: "#F87171",
    dangerBg: "#3A171A",
    infoBg: "#172A46",
    neutralBg: "#202938",
  },
};

let activeMode: ThemeMode = Appearance.getColorScheme() === "dark" ? "night" : "light";

type ThemeContextValue = {
  mode: ThemeMode;
  colors: Palette;
  setMode: (mode: ThemeMode) => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider(props: { children: React.ReactNode }): React.ReactNode {
  const [mode, setModeState] = useState<ThemeMode>(activeMode);

  const setMode = useCallback((next: ThemeMode) => {
    activeMode = next;
    setModeState(next);
  }, []);

  const value = useMemo<ThemeContextValue>(
    () => ({ mode, colors: palettes[mode], setMode }),
    [mode, setMode],
  );

  return React.createElement(ThemeContext.Provider, { value }, props.children);
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used inside ThemeProvider");
  }
  return context;
}

export function useThemedStyles<T>(factory: (colors: Palette) => T): T {
  const { colors } = useTheme();
  return useMemo(() => factory(colors), [colors, factory]);
}

export function setThemeMode(mode: ThemeMode): void {
  activeMode = mode;
}

export function getThemeMode(): ThemeMode {
  return activeMode;
}

/* Backward-compatible dynamic palette access for code that reads colors directly. */
export const colors = new Proxy({} as Palette, {
  get: (_target, property: string) => palettes[activeMode][property as keyof Palette],
});

export const spacing = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24 };

export const card = {
  backgroundColor: colors.surface,
  borderColor: colors.border,
  borderWidth: 1,
  borderRadius: 12,
  padding: spacing.lg,
} as const;

export const styleSheet = StyleSheet;
