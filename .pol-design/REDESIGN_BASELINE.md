# POL Visual Redesign — Baseline Audit Report

**Date:** 2026-09-27  
**Branch:** `ui/redesign-precision-commerce`  
**Authoritative Reference:** `13_PRODUCT_DESIGN/56_POL_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM_2026-09-21.md` (POL-DESIGN-VISUAL-001 v2.0.0)  
**Application Scope:** `@pol/web` (Next.js 15), `@pol/mobile` (Expo React Native), `@pol/ui`, `@pol/tokens`

---

## 1. Executive Summary
The POL MVP codebase currently compiles and builds cleanly (50 routes in Next.js, 0 TypeScript errors). However, its visual presentation is an early developer-scaffolded baseline that does not yet express the authoritative **Precision Commerce** design language. The UI suffers from monotonous card-grid layouts across all roles, lack of density differentiation between Retailer (D1), Vendor (D2), and Operations (D3), raw CSS variable typos (e.g. `--pol-light-warning`), leaky internal remediation strings (`G-007`, `G-013`) in user-facing cards, minimal visual hierarchy, flat top-navigation with no persistent sidebar for complex ops/vendor tools, and incomplete Night/RTL polish.

---

## 2. Current Strengths
1. **Solid Token Foundation (`@pol/tokens`)**: Exact color palettes for Light (`#F7F9FC`, `#FFFFFF`, `#2563EB`, etc.) and Night (`#0F141C`, `#151C27`, `#60A5FA`, etc.), canonical type scale (10 steps from Display XL to Caption), and 4px rhythm are already encoded.
2. **Centralized `@pol/ui` Primitives**: Core primitives (`Button`, `Field`, `SearchField`, `StatusChip`, `QtyStepper`, `EmptyState`, `ErrorState`, `Skeleton`) exist and have basic accessibility attributes (`aria-busy`, `role="alert"`, `useId`).
3. **Tailwind v4 CSS Variables**: `globals.css` properly wires `:root` and `html[data-theme="night"]` mapping semantic variables.
4. **Clean Component-to-API Boundary**: Pages consume `getApi()` and state hooks cleanly, allowing purely visual refactoring without touching API contracts.

---

## 3. Discovered Weaknesses & Visual Defects

### A. Information Hierarchy & Composition
- **Monotonous Card-on-Card Grids**: Almost every page (`retailer`, `vendor`, `ops`) defaults to a generic 3-column grid of plain rounded cards with tiny subtitle text.
- **Lack of Density Specialization**:
  - Retailer (D1 Spacious) lacks prominent hero search, category discovery tiles, and bold pricing/MOQ badges.
  - Vendor (D2 Balanced) lacks operational overview widgets and clear tabular inventory statuses.
  - Operations (D3 Dense Command) is styled identically to Retailer, with oversized cards instead of compact high-density queues, persistent filters, and exception badges.
- **Top Navigation Scaffolding**: `AppShell` uses a single horizontal scroll/wrap list of 18 text links in the top header. There is no sidebar navigation, no role-based sub-navigation, no active brand bar, and no profile avatar/context chip.

### B. Typography & Numeric Presentation
- **Inconsistent Headings**: Page titles vary between `text-[24px]` and `text-[20px]` with arbitrary margins.
- **Numeric Misalignment**: Toman prices, order numbers, and quantities often lack `tabular-nums` and consistent currency suffixes (`تومان`).
- **Internal Gap Noise**: Developer markers (e.g., `G-007 — بدون CRUD`, `شکاف G-013`) are rendered as primary card descriptions.

### C. Color & Token Inconsistencies
- **Broken Token References**: e.g., `border-[var(--pol-light-warning, var(--pol-light-border-strong))]` in `retailer/page.tsx` references a non-existent token (the canonical token is `--pol-light-semantic-warning`).
- **Hardcoded & Raw Classes**: Arbitrary tailwind opacity values and border colors scattered in page files instead of semantic token variables.
- **Night Surface Contrast**: In Night mode, secondary cards have identical luminance to the canvas, reducing edge separation and component distinction.

### D. Status & Feedback Treatments
- **Generic Status Chips**: Status tones in `StatusChip` use a single subtle background tint with border opacity, missing distinct tonal contrast between `warning`, `danger`, and `info`.
- **Sparse Empty States**: `EmptyState` lacks contextual iconography and clear secondary guidance.
- **Missing Loading States**: Skeletons only render raw pulsing rectangles without simulating the real geometry of product cards, tables, or order lists.

### E. RTL & Bidirectional Presentation
- **Mixed LTR/RTL Text**: Phone numbers, SKU codes, and order IDs (e.g. UUID prefixes) occasionally render with reversed punctuation or broken brackets when inline with Persian text.
- **Directional Chevrons**: Navigational chevrons lack explicit RTL mirroring classes.

### F. Accessibility & Touch Targets
- **Sm Controls on Touch**: `sm` buttons (h-8 = 32px) are used on mobile retailer pages where touch targets must be at least 44px (WCAG 2.2 AA).
- **Subtle Focus Rings**: Keyboard focus rings rely on default outline without sufficient contrast in both Light and Night modes.

---

## 4. Priority Refinement Targets
1. **Foundations**: Normalize `globals.css` and token utility classes; fix broken variable fallbacks; add elevation levels and focus ring styling.
2. **Global Shell**: Redesign `AppShell` with role-aware navigation (Retailer top bar + cart drawer, Vendor/Ops sidebar + header breadcrumbs, mobile bottom navigation).
3. **Core Primitives (`@pol/ui`)**: Refine `Button`, `Field`, `SearchField`, `StatusChip`, `QtyStepper`, `EmptyState`, `ErrorState`, `Skeleton`, and add `Card` and `Table` primitives.
4. **Golden Domain Screens**:
   - **Retailer Home & Catalog**: D1 Spacious Commerce, search-first, visual product cards, clear Toman price blocks, cart badge.
   - **Vendor Dashboard & Orders**: D2 Balanced Operations, inventory health badges, quick action triage.
   - **Operations Overview & Queues**: D3 Dense Command, compact exception rows, status triage.
   - **Shared Pages**: Login, Profile, Notifications, Corporate editorial surfaces.
