/**
 * Precision Commerce tokens — source: 13_PRODUCT_DESIGN/56_... (doc 56)
 * Light + Night first-class. Expand in Phase 1 from doc 56 §3–4, §11.
 */

export const motion = {
  /** micro feedback ms */
  micro: { min: 120, max: 160 },
  /** standard transition ms */
  standard: { min: 160, max: 240 },
  /** modal / bottom sheet ms */
  overlay: { min: 200, max: 280 },
  /** complex sequence cap ms */
  complexMax: 400,
} as const;

export const radius = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  pill: 999,
} as const;

export type MotionBand = keyof typeof motion;
