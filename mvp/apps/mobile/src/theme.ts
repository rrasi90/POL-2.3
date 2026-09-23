export const colors = {
  bg: "#F7F9FC",
  surface: "#FFFFFF",
  border: "#E5EAF0",
  text: "#0F172A",
  textSecondary: "#475569",
  textMuted: "#94A3B8",
  brand: "#1D4ED8",
  warning: "#B45309",
  warningBg: "#FFFBEB",
  success: "#047857",
  danger: "#B91C1C",
};

export const spacing = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24 };

export const card = {
  backgroundColor: colors.surface,
  borderColor: colors.border,
  borderWidth: 1,
  borderRadius: 12,
  padding: spacing.lg,
} as const;
