# POL Product Design Program

## Status
RESEARCH + DESIGN FOUNDATION / CANONICAL WORKSTREAM

## Canonical base
- Branch: `research-hardening-2026-09-14`
- Current hardening baseline: `22c3b8a`
- Product decisions remain governed by `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`.

## Purpose
This directory is the product-design source of truth for POL interfaces. It sits above implementation and below canonical product/business decisions.

## Delivery sequence
1. Phase 1 — Design Foundation: design system, brand, navigation, layout, accessibility, content patterns.
2. Phase 2 — Retailer: POL Market onboarding through ordering, tracking, reorder and profile.
3. Phase 3 — Vendor: vendor console, catalog, pricing, inventory, orders, referral and staff personas.
4. Phase 4 — Operations: internal Admin/Ops workbench.
5. Phase 5 — Field Activator: task-first mobile workflow.
6. Phase 6 — Corporate Website: public acquisition and credibility site.
7. Phase 7 — Frontend implementation: production UI against stable contracts.
8. Phase 8 — Backend productionization: HTTP/auth/providers/observability/deployment/recovery and release certification in parallel with implementation.

## Design principles
- B2B operational UX, not consumer commerce with a business login bolted on.
- Reduce time-to-correct-order before adding visual novelty.
- Make price, pack, MOQ, availability and order state visible at the point of decision.
- Mobile prioritizes replenishment and operational tasks; desktop supports deeper management.
- Assisted ordering remains a first-class path; self-service should progressively remove unnecessary dependence on sales reps.
- Persona controls presentation and workflow, never authorization.
- Backend/application boundary remains the business-rule SSoT; UI cannot invent pricing, stock, MOQ, allocation or permission rules.
- Persian/RTL is first-class; localization is structural, not a late translation layer.
- Accessibility target: WCAG 2.2 AA-oriented design and keyboard/touch support.

## Evidence-derived design direction
Current research consistently points toward fast reorder, purchase history, honest stock/price context, order tracking and low-friction mobile use. Faire exposes purchase history, order/shipping information and reorder on mobile; Cartona positions retailer ordering, supplier connection, inventory visibility and order tracking as core workflows; udaan emphasizes quick signup, repeat orders and real-time delivery tracking. These patterns support POL's existing product thesis rather than changing it. [Web evidence: Faire, Cartona, udaan]

## Exit criteria
A phase is not complete when screens merely look finished. It is complete when its user journeys, states, edge cases, accessibility, data/contract dependencies and measurable acceptance criteria are documented.
