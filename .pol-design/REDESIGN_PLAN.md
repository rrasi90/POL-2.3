# POL Precision Commerce — Visual Redesign Execution Plan

## 1. Operating Boundaries
- **No Domain Changes**: Zero changes to business logic, API requests/payloads, permissions, database, or state machine transitions.
- **Strictly Visual & Presentation**: Styles, markup, Tailwind classes, typography, spacing, surface hierarchy, and UI component composition only.
- **Verification Gate per Slice**: Each slice must pass `npm run typecheck`, Next.js build, and visual inspection.

---

## 2. Slice Breakdown & Sequence

### Slice 1: Foundations (Phase A)
- **Target Files**:
  - `mvp/apps/web/src/app/globals.css`
  - `mvp/packages/tokens/src/index.ts`
- **Objectives**:
  - Establish complete CSS custom property mappings for Light and Night.
  - Define utility classes for surface elevation, borders, focus rings, and shadows.
  - Fix any broken variable fallbacks (e.g. `--pol-light-semantic-warning`).
  - Configure Persian typography smoothing and tabular numerals.

### Slice 2: Global Application Shell (Phase B)
- **Target Files**:
  - `mvp/apps/web/src/components/shell/app-shell.tsx`
- **Objectives**:
  - Implement a polished, role-tailored application shell:
    - Retailer Mode: Modern commerce top bar with search, cart drawer trigger, and role badge.
    - Vendor & Operations Mode: Structured layout with collapsible, categorized sidebar navigation and contextual top bar.
    - Mobile: Ergonomic bottom navigation bar with clear active indicator and smooth drawer.
  - Polished theme toggle (Light / Night with icon indicator).
  - User context badge showing active role and organization.

### Slice 3: Core UI Primitives (Phase C)
- **Target Files**:
  - `mvp/packages/ui/src/button.tsx`
  - `mvp/packages/ui/src/field.tsx`
  - `mvp/packages/ui/src/search-field.tsx`
  - `mvp/packages/ui/src/status-chip.tsx`
  - `mvp/packages/ui/src/qty-stepper.tsx`
  - `mvp/packages/ui/src/states.tsx`
  - `mvp/packages/ui/src/card.tsx` (new atom)
  - `mvp/packages/ui/src/index.ts`
- **Objectives**:
  - Elevate button typography, hover/active elevation, focus-visible outline, and loading spinner.
  - Upgrade form inputs with crisp border transitions, clear validation error styles, and accessible helper text.
  - Refine status chips with distinct tonal badges and contrast compliance.
  - Provide a reusable `Card` and `Badge` component in `@pol/ui`.
  - Upgrade Skeletons to mimic actual card, list, and table geometries.

### Slice 4: Retailer Golden Surfaces (Phase D — D1 Spacious Commerce)
- **Target Files**:
  - `mvp/apps/web/src/app/(dashboard)/retailer/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/retailer/catalog/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/retailer/basket/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/retailer/orders/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/retailer/checkout/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/retailer/shared.ts`
- **Objectives**:
  - D1 spacious density (large touch targets >= 44px, generous margins, bold Toman prices).
  - Prominent search and category discovery.
  - Visual product cards with clear pack size / MOQ / inventory badges.
  - Clean order tracking timeline and action alerts.

### Slice 5: Vendor Golden Surfaces (Phase E — D2 Balanced Operations)
- **Target Files**:
  - `mvp/apps/web/src/app/(dashboard)/vendor/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/vendor/orders/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/vendor/catalog/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/vendor/inventory/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/vendor/inventory/daily/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/vendor/_shared.ts`
- **Objectives**:
  - D2 balanced density (compact operational controls, structured tables).
  - Daily inventory confirmation banner with fast action trigger.
  - Replace internal gap strings with clean merchant-facing copy.
  - Order queue triage with quick accept/reject actions.

### Slice 6: Operations & Admin Golden Surfaces (Phase F — D3 Dense Command)
- **Target Files**:
  - `mvp/apps/web/src/app/(dashboard)/ops/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/ops/queues/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/ops/support/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/ops/reconciliation/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/admin/page.tsx`
  - `mvp/apps/web/src/app/(dashboard)/ops/_shared.ts`
- **Objectives**:
  - D3 dense command layout (8px padding, compact table rows, high data density).
  - Exception-first dashboard with alert severity highlights.
  - Persistent queue filtering and keyboard-friendly inspection.

### Slice 7: Corporate & Public Surfaces (Phase H — Editorial Commerce)
- **Target Files**:
  - `mvp/apps/web/src/app/page.tsx`
  - `mvp/apps/web/src/app/about/page.tsx`
  - `mvp/apps/web/src/app/how/page.tsx`
  - `mvp/apps/web/src/app/pilot/page.tsx`
  - `mvp/apps/web/src/app/contact/page.tsx`
  - `mvp/apps/web/src/app/auth/login/page.tsx`
- **Objectives**:
  - Editorial Precision Commerce layout with brand typography and pilot proof points.
  - Polished phone + six-digit OTP login screen with accessible focus states.

### Slice 8: Mobile Parity & Verification (Phase G)
- **Target Files**:
  - `mvp/apps/mobile/src/theme.ts`
  - `mvp/apps/mobile/src/components/ui.tsx`
- **Objectives**:
  - Full Light and Night token parity in React Native.
  - Action-first field layout with offline network status banner.

### Slice 9: Final Quality Gate & Evidence Package
- Comprehensive check: typecheck, lint, build, Light/Night contrast audit, RTL alignment audit, responsive layout audit.
- Generate `VISUAL_CHANGE_LOG.md` and `VISUAL_QA.md`.
