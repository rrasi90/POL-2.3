/**
 * Precision Commerce tokens — authority: doc 56 (POL-DESIGN-VISUAL-001 v2.0.0)
 * Light + Night first-class. Semantic names only in components.
 */

export const color = {
  light: {
    "bg.canvas": "#F7F9FC",
    "surface.default": "#FFFFFF",
    "surface.subtle": "#F1F5F9",
    "surface.elevated": "#FFFFFF",
    "border.subtle": "#E2E8F0",
    "border.strong": "#CBD5E1",
    "text.primary": "#0F172A",
    "text.secondary": "#475569",
    "text.muted": "#64748B",
    "text.disabled": "#94A3B8",
    "brand.primary": "#2563EB",
    "brand.hover": "#1D4ED8",
    "brand.active": "#1E40AF",
    "brand.accent": "#4F46E5",
    "semantic.success": "#15803D",
    "semantic.warning": "#B45309",
    "semantic.danger": "#B91C1C",
    "semantic.info": "#1D4ED8",
    "focus.ring": "#2563EB",
  },
  night: {
    "bg.canvas": "#0F141C",
    "surface.default": "#151C27",
    "surface.subtle": "#1B2431",
    "surface.elevated": "#202A38",
    "border.subtle": "#2A3646",
    "border.strong": "#3A4A5F",
    "text.primary": "#F8FAFC",
    "text.secondary": "#CBD5E1",
    "text.muted": "#94A3B8",
    "text.disabled": "#64748B",
    "brand.primary": "#60A5FA",
    "brand.hover": "#93C5FD",
    "brand.active": "#3B82F6",
    "brand.accent": "#818CF8",
    "semantic.success": "#4ADE80",
    "semantic.warning": "#FBBF24",
    "semantic.danger": "#F87171",
    "semantic.info": "#60A5FA",
    "focus.ring": "#93C5FD",
  },
} as const;

export type ThemeMode = keyof typeof color;
export type ColorToken = keyof (typeof color)["light"];

/** Doc 56 §4.2 type scale — size/line-height pairs */
export const typeScale = {
  displayXl: { size: 32, lineHeight: 40 },
  displayL: { size: 28, lineHeight: 36 },
  h1: { size: 24, lineHeight: 32 },
  h2: { size: 20, lineHeight: 28 },
  h3: { size: 18, lineHeight: 26 },
  title: { size: 16, lineHeight: 24 },
  body: { size: 14, lineHeight: 22 },
  bodySm: { size: 13, lineHeight: 20 },
  label: { size: 12, lineHeight: 18 },
  caption: { size: 11, lineHeight: 16 },
} as const;

/** Doc 56 §5 — 4px base rhythm */
export const space = {
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  5: 20,
  6: 24,
  7: 32,
  8: 40,
  9: 48,
  10: 64,
} as const;

export const radius = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  pill: 999,
} as const;

/** Doc 56 §11 motion bands (ms) */
export const motion = {
  micro: { min: 120, max: 160 },
  standard: { min: 160, max: 240 },
  overlay: { min: 200, max: 280 },
  complexMax: 400,
} as const;

/** Doc 56 density gears */
export const density = {
  D1: { label: "Spacious Commerce", controlY: 12, rowY: 16 },
  D2: { label: "Balanced Operations", controlY: 10, rowY: 12 },
  D3: { label: "Dense Command", controlY: 8, rowY: 10 },
} as const;

export type DensityKey = keyof typeof density;
export type MotionBand = keyof typeof motion;

/** CSS variable names for runtime theme switch */
export function cssVar(token: ColorToken, mode: ThemeMode): string {
  return `var(--pol-${mode}-${token.replace(/\./g, "-")})`;
}

/** Build `:root` / `[data-theme=night]` custom property map */
export function themeCssVariables(): Record<ThemeMode, Record<string, string>> {
  const out = { light: {}, night: {} } as Record<ThemeMode, Record<string, string>>;
  for (const mode of ["light", "night"] as const) {
    for (const [key, value] of Object.entries(color[mode])) {
      out[mode][`--pol-${mode}-${key.replace(/\./g, "-")}`] = value;
    }
  }
  return out;
}
