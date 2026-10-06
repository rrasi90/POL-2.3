# POL Mobile Motion System — Engineering Spec

- **Doc ID:** POL-DESIGN-MOBILE-MOTION-001
- **Date:** 2026-10-06
- **Scope:** `mvp/apps/mobile` only (ir.pol.market + ir.pol.vendor)
- **Status:** Implemented on `feat/mobile-motion-layer` (PR-01..PR-03)
- **Canonical references:** `56_POL_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM_2026-09-21.md` §11 (timing bands, reduced motion), `.pol-design/*` (visual refinement rules), docs 57/58 (Cartona — interaction patterns only, clean-room)
- **Dependency policy:** React Native core `Animated` exclusively. No Lottie / Reanimated / Moti / Gesture-Handler / SVG. Zero new runtime dependencies.

---

## 1. Architecture

```
mvp/apps/mobile/src/motion/
├── motionTokens.ts      ← single source: durations, easings, springs, stagger, shake
├── motionTypes.ts       ← MotionDirection ("forward"|"back"|"up"|"down")
├── useReducedMotion.ts  ← AccessibilityInfo singleton (isReduceMotionEnabled + reduceMotionChanged)
├── FadeIn.tsx           ← entrance: fade + vertical drift, delay = stagger hook
├── SlideIn.tsx          ← semantic direction, RTL-mapped inside the primitive
├── ScreenTransition.tsx ← enter-only route/tab transition, keyed by semantic identity
├── PressScale.tsx       ← animated press (usePressScale hook + wrapper)
├── PopOnChange.tsx      ← scale pop on value change (qty / totals / badge / KPI)
├── Pulse.tsx            ← decorative repeating ring (pointerEvents none)
├── SuccessCheck.tsx     ← ring + check from rotated bordered views (no SVG)
├── ErrorShake.tsx       ← revision-triggered shake + useErrorTrigger()
├── SkeletonPulse.tsx    ← ambient pulse + 4 surface-geometry skeletons
├── OrderProgress.tsx    ← order lifecycle axis (presentation mapping)
├── DeliveryProgress.tsx ← delivery lifecycle axis (presentation mapping)
└── SplashSequence.tsx   ← JS brand moment (layer B of two-layer splash)
```

Rules enforced by review:

1. Screens never call `Animated` directly — only primitives from `src/motion/`.
2. Screens never hardcode durations/easings — only `motionTokens`.
3. Motion color always via `useTheme()` — no hex literals in the motion layer.
4. `useNativeDriver: true` everywhere; only opacity/transform. No color/width/height/layout animation in primitives.
5. No unmount/exit choreography (enter-only), except the two-phase basket-line removal (fade → drop from state).
6. Stagger capped at 8 items (`motionStagger.maxItems`); complex sequences ≤ 400ms.
7. Every primitive renders its final visual state instantly under reduced motion; semantic feedback is never removed, only animation.

## 2. Motion tokens (from canonical §11 bands)

| Token | Value | Band |
|---|---|---|
| `duration.micro` | 140ms | micro feedback 120–160 |
| `duration.base` | 200ms | standard transition 160–240 |
| `duration.emphasis` | 280ms | modal class 200–280 |
| `duration.sequence` | 400ms | complex sequence ceiling |
| `crossfade` | 70/70ms | label ↔ spinner half-swaps |
| `loop.period` | 960ms | ambient (skeleton) |
| springs | press `speed 32 / bounciness 6`, pop `tension 240 / friction 16`, bump `tension 340 / friction 16` | **pending on-device tuning** |
| `scale.press / pop` | 0.97 / 1.08 | — |
| `drift.sm / md` | 8 / 14px | — |
| `stagger.step / maxItems` | 36ms / 8 | — |
| `shake.amplitude / step` | 8px / 45ms | total ≈ 270ms |

## 3. Golden Motion Set — implementation map

| ID | Motion | Where | Primitives |
|---|---|---|---|
| M-01 | Splash (two layers) | `AppShell.tsx` + `SplashSequence` | brand mark pop → wordmark → tagline; cut short the moment boot is ready; never extends boot |
| M-02 | Auth | `LoginScreen.tsx` | entrance sequence, phone↔OTP SlideIn (RTL-aware), OTP digit pop, revision-based error shake |
| M-03 | Product → Cart | `RetailerMobileScreen.tsx` | add feedback + cart badge `PopOnChange` bump in bottom nav |
| M-04 | Basket quantity | same | qty pop, total pop; zero-qty lines fade out then unmount |
| M-05 | Allocation | same | allocation/checkout cards FadeIn, totals pop |
| M-06 | Checkout | same | Btn loading only; success handled at screen level (no API coupling in Btn) |
| M-07 | Order success | same | `SuccessCheck` + staggered order-id/amount reveal |
| M-08 | Acceptance | `OrderDetailMobileScreen.tsx` | stepper dot pop + line fill on ACCEPTED / PARTIALLY_ACCEPTED / REJECTED |
| M-09 | Fulfillment | same | PREPARING → READY stage transitions on the same stepper |
| M-10 | Shipment | same | READY → DISPATCHED via animated stepper; route-line language (no truck) |
| M-10B | Delivery axis | `DeliveryProgress.tsx` | independent axis from `delivery_status`; marker shuttle IN_TRANSIT, pulse ARRIVED |
| M-11 | Delivery confirmation | same | OTP → SuccessCheck → DELIVERED (requires BUG-01 hotfix on `main`) |
| M-12 | Barcode | `VendorMobileScreen.tsx` | lookup pulse, result fade-in per scan revision, no-match shake + candidate state |
| M-13 | Loading system | motion layer | `RetailerCatalogSkeleton`, `RetailerOrderSkeleton`, `VendorOrderSkeleton`, `VendorInventorySkeleton` |
| M-14 | Error / recovery | `ui.tsx` | `ErrorBox` shake on signature change (`revision` prop supported) |
| M-15 | Navigation | `AppShell.tsx`, tab dispatchers | fade-through on semantic route/tab keys |

## 4. State architecture (critical)

- `OrderLifecycleStage` / `DeliveryLifecycleStage` are **view-model presentation mappings** inside the motion layer — not business enums. Source of truth remains backend `order_status` and `delivery_status`.
- The two axes are independent (order DISPATCHED can coexist with delivery PICKED_UP / IN_TRANSIT) and are rendered by separate primitives.
- `Btn` owns only pressed/disabled/loading. Business success feedback lives in screens.
- No API contract, RBAC, order state machine, or payload change accompanies motion.

## 5. Functional defects (separate hotfix branch, merged to `main` before motion)

- **BUG-01** `OrderDetailMobileScreen.tsx` — delivery OTP regex `/^\\d{4}$/` never matched; delivery confirmation was impossible. Fixed to `/^\d{4}$/`.
- **BUG-02** `VendorMobileScreen.tsx:819` — unbraced JSX conditional rendered literal code text AND showed the finance quick action for all roles (role-gating violation). Wrapped in `{...}`.

## 6. QA protocol

- Gates per phase: `typecheck` + `qa:functional` + `qa:regression` (all green at PR-01/02/03).
- Runtime: QA x86_64 APK (`scripts/build_qa_x86.mjs`), emulator `POL_API_Emulator` (Pixel 6 API 35), `EXPO_PUBLIC_DATA_MODE=mock` for hermetic flows; capture matrix LIGHT / NIGHT / REDUCED-MOTION per §19 of the execution plan.
- Evidence: screenshots into `mvp/apps/mobile/visual-qa/captures/` with SHA256 + manifest per the visual-qa protocol; VISUAL_CHANGE_LOG entry.

## 7. Roadmap

- **PR-04 (P1 polish):** vendor/retailer home entrances, inventory save feedback, finance, support, account, notifications.
- **PR-05 (P2):** shared `BottomNav` (active indicator slide + badge bump), theme transition decision (deferred — color animation is outside the native-driver policy; instant today).
- **PR-06:** full visual QA matrix + ledger closure.
