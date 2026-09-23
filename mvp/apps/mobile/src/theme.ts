export type ThemeMode = "light" | "night";

type Palette = {
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
  danger: string;
};

const palettes: Record<ThemeMode, Palette> = {
  light: {
    bg: "#F7F9FC",
    surface: "#FFFFFF",
    border: "#E5EAF0",
    text: "#0F172A",
    textSecondary: "#475569",
    textMuted: "#64748B",
    brand: "#2563EB",
    warning: "#B45309",
    warningBg: "#FFFBEB",
    success: "#047857",
    danger: "#B91C1C",
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
    danger: "#F87171",
  },
};

let activeMode: ThemeMode = "light";

export function setThemeMode(mode: ThemeMode): void {
  activeMode = mode;
}

export function getThemeMode(): ThemeMode {
  return activeMode;
}

/* Proxy keeps the existing colors property API while switching palettes centrally. */
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
