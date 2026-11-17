import { Easing } from "react-native";

// Single source of motion timing for the whole app. Bands are canonical:
// 13_PRODUCT_DESIGN/56_POL_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM §11 —
// micro 120–160ms, standard 160–240ms, modal 200–280ms, complex sequence ≤400ms.
export const motionDuration = {
  micro: 140,
  base: 200,
  emphasis: 280,
  sequence: 400,
} as const;

// Half-swaps inside buttons/chips (label ↔ spinner, chip label change).
export const motionCrossfade = { out: 70, in: 70 } as const;

// Ambient loop period (skeleton shimmer) — outside the interaction bands.
export const motionLoop = { period: 960 } as const;

export const motionEasing = {
  standard: Easing.bezier(0.2, 0, 0, 1),
  decelerate: Easing.out(Easing.cubic),
  accelerate: Easing.in(Easing.cubic),
  ambient: Easing.inOut(Easing.quad),
} as const;

// Springs are initial values pending on-device (Android) evaluation; tune here only.
export const motionSpring = {
  press: { speed: 32, bounciness: 6 },
  pop: { tension: 240, friction: 16 },
  bump: { tension: 340, friction: 16 },
} as const;

export const motionScale = {
  press: 0.97,
  pop: 1.08,
} as const;

export const motionDrift = {
  sm: 8,
  md: 14,
} as const;

export const motionStagger = {
  step: 36,
  maxItems: 8,
} as const;

export const motionShake = {
  amplitude: 8,
  step: 45,
} as const;

// POL renders Persian layouts via `direction: "rtl"` style roots, which does
// not mirror transform translateX — semantic directions are mapped explicitly.
export const RTL_LAYOUT = true;

export function staggerDelay(index: number): number {
  return Math.min(index, motionStagger.maxItems - 1) * motionStagger.step;
}