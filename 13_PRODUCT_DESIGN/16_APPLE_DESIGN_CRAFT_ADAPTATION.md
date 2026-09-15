# POL Apple Design Craft Adaptation

## Status
`DESIGN FOUNDATION / REVIEW LAYER`

This document adapts the public `dickwu/apple-design-skill` review method to POL. It does **not** make Apple HIG the product design source of truth, and it does not turn POL into an Apple-style UI. POL remains a Persian-first B2B operational product whose canonical business and authorization rules come from the project decision register and application boundary.

## 1. Why this layer exists

The existing POL design system already establishes B2B operational UX, RTL-first behavior, semantic tokens, accessibility, responsive behavior, and state-driven components. The Apple Design Skill adds a useful second lens: every screen should have a clear purpose, preserve user agency, use familiar interaction patterns, demonstrate craft, and avoid generic generated-interface patterns.

The adopted principles are:

1. **Purpose** — every screen has one dominant operational job.
2. **Agency** — retailers and operators can inspect, recover, undo where safe, and avoid accidental irreversible actions.
3. **Responsibility** — permissions, payment responsibility, data use, and irreversible actions are explicit.
4. **Familiarity** — standard mobile/desktop interaction patterns are preferred over novel controls.
5. **Flexibility** — layouts survive RTL, text scaling, narrow widths, keyboard input, pointer input, and different personas.
6. **Simplicity** — remove controls that do not help the current job.
7. **Craft** — alignment, typography, state transitions, copy, spacing, and interaction feedback are deliberate.
8. **Delight** — personality may exist, but decoration never competes with ordering or operational work.

These principles are a review lens, not replacement product requirements.

## 2. POL-specific translation

| Apple Design Skill concept | POL interpretation |
|---|---|
| Tab bar / top-level navigation | POL Market uses persistent primary mobile navigation; Vendor/Ops use responsive sidebar/navigation patterns appropriate to dense operational work. |
| Sheets / dialogs | Use for focused temporary tasks such as confirmation, filtering, allocation explanation, and compact exception handling. Do not hide critical commercial information in a transient surface. |
| Search | Search is a primary procurement operation, not a decorative header element. SKU/barcode/name/pack-aware search must be considered. |
| Lists / tables | Retailer surfaces favor scannable compact lists; Vendor/Ops can use dense tables where comparison and queue processing benefit from them. |
| Semantic colors | All status and action colors remain semantic tokens. Never use color alone to communicate state. |
| Dynamic Type / text scaling | Translate to system text scaling and browser zoom/accessibility settings. Layout must survive large text without truncating critical price, MOQ, availability, or order-state information. |
| Safe areas | Mobile UI must respect device insets and keyboard avoidance. |
| Undo / recovery | Prefer reversible actions for routine changes. Irreversible order cancellation, return, refund, or membership actions require explicit confirmation and clear consequences. |
| Feedback | Prefer inline state feedback, banners, toasts, and timeline updates over alert-heavy flows. |
| Platform conventions | Adopt principles rather than blindly copying iOS components because POL also targets Android, Web/PWA, desktop Vendor, and Ops surfaces. |

## 3. The POL design thesis

**POL should feel like a reliable operational bridge, not a consumer marketplace.**

The visual system should make the correct business action obvious: find the right product, understand pack/MOQ/price/availability, place or repeat an order, understand allocation and fulfillment, and recover from exceptions.

The product's point of view is therefore **operational clarity through structured information** rather than decorative novelty.

## 4. Signature element

The signature element should be the **POL Operational Status Language**: a consistent visual grammar that makes commercial and fulfillment truth immediately scannable.

It combines:
- product identity;
- pack size / unit;
- MOQ or quantity increment;
- current price and price context;
- availability confidence/freshness;
- vendor identity;
- order state;
- next available action.

This is more defensible and more product-specific than a decorative gradient, glass effect, oversized hero number, or generic card treatment.

## 5. Accessibility quality floor

The Apple Design Skill review method uses measured accessibility checks rather than adjectives. POL should therefore validate, at minimum:

- text contrast against its actual semantic surface;
- interactive target dimensions and spacing;
- visible keyboard focus on desktop;
- screen-reader labels and logical reading order;
- no state communicated by color alone;
- system/browser text scaling;
- reduced motion behavior;
- reduced transparency behavior where applicable;
- narrow viewport and long Persian-label stress;
- RTL/LTR mixed-content correctness for SKU, barcode, URL, ID, dates, and numeric values.

The existing POL accessibility requirement remains WCAG 2.2 AA-oriented. Apple-specific numeric thresholds are treated as an additional review lens, not as a substitute for WCAG.

## 6. Anti-generic design rules

The following patterns should be rejected unless a concrete product reason exists:

- decorative gradients used only to make a screen look modern;
- oversized hero statistics on operational screens where a queue would be more useful;
- excessive glass/blur surfaces;
- repeated large rounded cards for every piece of information;
- arbitrary 01/02/03 numbering without semantic meaning;
- excessive pills and badges;
- full-width primary buttons on wide desktop layouts when a compact action is clearer;
- promotional home screens that displace open orders or replenishment actions;
- custom navigation controls where a familiar platform pattern solves the same problem;
- icon-only controls without an accessible name;
- dense tables squeezed into mobile rather than redesigned as task-oriented lists.

## 7. Screen review contract

Before a Figma screen is considered design-ready, review it in this order:

### A. Accessibility
- Can all critical information be read at large text sizes?
- Are contrast and target sizes measurable?
- Is state communicated without color alone?
- Is keyboard and screen-reader operation plausible?

### B. Convention
- Is the navigation pattern familiar for the target surface?
- Are sheets, dialogs, search, tabs, lists, tables, and confirmation patterns used appropriately?
- Are mobile and desktop behaviors intentionally different where necessary?

### C. Operational craft
- Is the primary job obvious within seconds?
- Are price, pack, MOQ, availability, vendor, and next action visually prioritized where relevant?
- Are loading, empty, stale, error, partial, and success states designed rather than implied?

### D. Content
- Does every action label say what will happen?
- Do errors explain recovery?
- Does terminology match the POL Persian glossary?
- Are commercial claims backed by runtime data or an approved product decision?

### E. Restraint
- What can be removed without reducing comprehension?
- Is there one product-specific visual signature rather than many decorative accents?

## 8. Required screen-level metadata for Figma

Every canonical screen should record:

- Persona / active membership context;
- Platform target;
- Primary job;
- Entry conditions;
- Primary action;
- Secondary actions;
- Data dependencies;
- Domain states represented;
- Loading / empty / error / partial / success states;
- Accessibility requirements;
- Analytics events;
- Deep-link destination if entered from a notification;
- Destructive/irreversible actions and recovery path.

## 9. Apple-HIG review boundary

The external skill is based on Apple's HIG and explicitly distinguishes platform conventions from cross-platform principles. POL should adopt the latter broadly, while applying platform-specific conventions selectively:

- **Retailer mobile:** mobile conventions, touch targets, safe areas, keyboard avoidance, familiar bottom navigation.
- **Vendor web/desktop:** dense information architecture, keyboard/pointer support, responsive side navigation, tables and queue workflows.
- **Ops web:** operational density and keyboard efficiency take precedence over consumer-mobile conventions.
- **Field Activator:** touch-first, task-first, weak-network-aware states; do not invent offline writes until backend support exists.
- **Corporate website:** brand expression and acquisition patterns rather than application navigation conventions.

## 10. Relationship to canonical POL decisions

This layer cannot override:

- D-001 Ahvaz-only Year 1;
- D-002 three-month pilot;
- D-006 0% pilot commission;
- D-007 1–3% post-pilot commission hypothesis;
- D-008 asset-light logistics;
- D-010 Basket → AllocationPlan → OrderGroup → Order → OrderItem;
- D-014 Multi-Vendor Basket;
- D-015 PostgreSQL 18 canonical runtime;
- D-016 Vendor Referral MVP;
- D-017 User Profile + Persona Context MVP.

It also cannot turn future capabilities such as wallet, BNPL, rewards, AI recommendations, owned logistics, or manufacturer dashboards into current UI requirements.

## 11. Figma gate

Before high-fidelity Figma work begins, the following must be true:

1. visual tokens have explicit numeric values and contrast evidence;
2. typography has verified Persian/Latin font availability and scaling behavior;
3. component variants include the states required by the domain;
4. auth/session, commerce/order, RMA/dispute, payment, notification, and support state matrices are mapped;
5. screen-to-API/application-boundary dependencies are documented;
6. analytics acceptance events are attached to critical journeys;
7. the Driver/logistics product boundary is explicitly recorded;
8. Figma pages and components follow deterministic naming and versioning;
9. every high-fidelity screen can pass the review contract in Section 7.

## 12. Sources

Primary external review method: `dickwu/apple-design-skill`, which routes reviews through Apple's Human Interface Guidelines and explicitly requires reading the relevant guideline files before making claims. The current repository states that the skill contains 122 HIG pages and eight design principles, and that accessibility, platform conventions, visual craft, interaction, and content are reviewed separately.

POL remains governed by its own product, business, data, and engineering source-of-truth documents.
