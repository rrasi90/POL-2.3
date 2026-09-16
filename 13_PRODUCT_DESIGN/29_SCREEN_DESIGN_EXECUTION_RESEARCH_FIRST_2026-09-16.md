# POL — Research-First Screen Design Execution

**Date:** 2026-09-16  
**Status:** CANONICAL DESIGN EXECUTION ADDENDUM  
**Purpose:** Define how every POL screen must be designed from first principles and verified against established design-system guidance before Penpot implementation.

## 0. Operating rule

Before designing a screen, answer:
1. What is the user's job on this screen?
2. What decision must become easy?
3. What information is necessary for that decision?
4. What is the primary action?
5. What can fail?
6. How does the user recover?
7. What must remain visible during recovery?
8. Which accessibility constraints apply?
9. Which established design-system pattern is appropriate?
10. What evidence supports the visual choice?

Do not start from decoration, cards, gradients or an arbitrary dashboard template.

## 1. Research hierarchy for design decisions

Use sources in this order:

1. POL canonical product/domain/governance documents.
2. WCAG 2.2 and W3C accessibility guidance.
3. Established design systems with documented patterns, especially Carbon and GOV.UK.
4. Relevant interaction research and platform conventions.
5. Visual preference only after the above constraints are satisfied.

A visual choice that conflicts with product truth or accessibility is rejected.

## 2. Information hierarchy

### 2.1 Retailer
Use:
`Job/State → Product → Pack → MOQ → Price → Availability → Vendor → Quantity → Next Action`

The user should be able to identify the purchasable unit and commercial constraints without opening another screen.

### 2.2 Vendor/Ops
Use:
`Severity/State → Reason → Age/SLA → Object → Owner → Next Action`

Operational screens are work surfaces, not KPI galleries.

## 3. Layout principles

### 3.1 Containers
- Mobile reference: 390×844.
- Desktop reference: 1440×1024.
- Mobile horizontal padding: 16 px baseline; 20 px for major sections where breathing room is needed.
- Desktop readable content width: normally 1120–1280 px; allow wider queue/table areas when required by data density.
- Use full-width rows for critical alerts and tables; do not place dense tables inside narrow decorative cards.

### 3.2 Spacing
Use a semantic scale centered on 4/8 px increments:
- 4: micro separation
- 8: icon/label separation and tight grouping
- 12: compact internal spacing
- 16: default component padding / mobile section spacing
- 20: medium section spacing
- 24: component-group separation
- 32: major section separation
- 40–48: page-level separation

The exact token may adapt responsively; avoid one-off gaps. Established systems such as GOV.UK explicitly use systematic responsive spacing rather than arbitrary values.

## 4. Typography

### 4.1 UI typography
Primary UI family: **Vazirmatn**.

Recommended tokens:
- Display: 32/40, 700
- H1: 28/36, 700
- H2: 22/30, 700
- H3: 18/26, 700
- Body Large: 17/28, 400
- Body: 15/24, 400
- Body Medium: 15/24, 600
- Caption: 13/20, 400
- Micro label: 12/18, 600 only where necessary
- Numeric emphasis: 20–28 px depending on hierarchy; use tabular figures for operational values where supported.

Do not build core UI around 9–11 px text.

### 4.2 B Lotus
Use **B Lotus** selectively for:
- corporate / editorial headings
- printed or exportable documents
- ceremonial or brand-led display moments
- long-form Persian documents where verified rendering is available

Do not use B Lotus for dense tables, compact controls, OTP, SKU, price cells or operational microcopy unless readability has been explicitly verified.

## 5. Color system v2

Base neutrals:
- `navy-950 #071427`
- `navy-900 #0A1730`
- `navy-800 #12264A`
- `blue-700 #1D4ED8`
- `blue-600 #2563EB`
- `blue-100 #DBEAFE`
- `blue-050 #EFF6FF`
- `gold-300 #F7D4B6`
- `gold-050 #FFF7F1`
- `white #FFFFFF`
- `slate-900 #172033`
- `slate-700 #344054`
- `slate-600 #475467`
- `slate-500 #667085`
- `slate-300 #D0D5DD`
- `slate-200 #EAECF0`
- `slate-100 #F2F4F7`
- `slate-050 #F8FAFC`

Semantic states:
- Success: `#15803D`, background `#F0FDF4`
- Warning: `#B45309`, background `#FFFBEB`
- Danger: `#B42318`, background `#FEF3F2`
- Info: `#175CD3`, background `#EFF8FF`

Rules:
- Never use color as the sole indicator of state.
- Primary text must remain high contrast on its layer.
- Secondary text must not be used for essential commercial information.
- CTA blue is reserved primarily for actionable controls, not large decorative surfaces.
- Gold is an accent, not a second CTA system.

## 6. Shape and elevation

- Default control radius: 10 px.
- Compact controls: 8 px.
- Large cards / sheets: 14–16 px.
- Avoid pill-shaped UI except tags, filters and status chips where the shape has semantic meaning.
- Default elevation should be subtle; hierarchy should come primarily from spacing, border, typography and layering.
- Use 1 px borders on most data surfaces; do not outline every nested element.

## 7. Buttons

### Primary
- solid blue
- text white
- minimum 44 px high for touch-oriented surfaces
- one primary CTA per screen where possible

### Secondary
- white / surface background
- border slate-300
- dark text

### Tertiary
- text-only or low-emphasis button

### Destructive
- use danger family; never make destructive actions visually equal to routine primary actions.

Do not put multiple visually dominant blue buttons beside each other without clear hierarchy.

## 8. Inputs and forms

Every field needs:
- label
- value
- optional hint
- focus state
- disabled state if relevant
- error state if relevant
- recovery guidance if relevant

Do not rely on placeholder text as the only label.

For validation errors:
- preserve user input;
- show the field error;
- show a page-level error summary when multiple or significant errors exist;
- move focus to the error summary when appropriate;
- keep error language specific and actionable.

## 9. Product cards and rows

### ProductRow is the default ordering primitive
Recommended order:
1. product image/icon where recognition helps
2. product name
3. pack/unit
4. MOQ
5. price
6. availability/freshness
7. vendor
8. quantity stepper / add action

Use ProductCard only when imagery materially improves recognition. Do not turn every product row into a large consumer card.

## 10. Basket and allocation

The basket is one unified retailer object even when fulfillment is split across vendors.

### BasketLine
Keep:
- product
- pack
- quantity
- unit price
- line total
- current availability
- vendor assignment where already determined

### AllocationGroup
Group by vendor only after allocation exists.

Visual rule:
- retailer sees outcome first;
- algorithmic mechanics remain secondary;
- changed lines are highlighted with reason and next action;
- avoid presenting allocation as an opaque technical object.

## 11. Operational queues

Use a real table/list when the user must compare rows and act across them. Do not convert a queue into decorative KPI cards.

Every queue row should provide:
`Object | State/Severity | Reason | Age/SLA | Owner | Next Action`

Sortable tables must be keyboard operable; interactive controls inside cells remain reachable in normal tab order. Carbon documents this as a core accessibility behavior.

## 12. Summary lists

Use summary-list style blocks for key-value facts:
- Order number → value
- Vendor → value
- Last updated → date
- Settlement state → status

Do not use summary lists as substitutes for actual tables or lists when the data is tabular.

## 13. Empty/loading/error

### Loading
Prefer skeletons that approximate the final geometry for content-heavy surfaces.

### Empty
Explain:
1. what is empty;
2. why it may be empty;
3. the next useful action.

### Error
Do not write generic copy such as «خطایی رخ داد» when more specific information is available.

Preferred pattern:
`چه اتفاقی افتاد → چه چیزی تغییر کرده → الان چه کار کن`

### Network degraded
Show local state and retry without destroying entered work.

## 14. Navigation

### Retailer mobile
Bottom navigation only for high-frequency destinations:
`خانه | خرید | سفارش‌ها | سبد | حساب`

Do not create a bottom-nav destination for every feature.

### Vendor/Ops desktop
Side navigation grouped by work:
- Today / Overview
- Commerce or Orders
- Exceptions
- Inventory / Reconciliation
- Relationships / Support
- Administration

Use clear active state; do not rely only on a color shift.

## 15. Accessibility gates

Every screen must pass:
- target-size minimum requirements;
- visible focus;
- keyboard path where applicable;
- semantic grouping;
- non-color status cues;
- long Persian label test;
- mixed Persian/Latin test;
- zoom/text scaling test;
- reduced-motion behavior where relevant.

WCAG 2.2 sets a 24×24 CSS pixel minimum target size for pointer inputs with stated exceptions; POL should normally design primary mobile controls at 44 px or larger to provide comfortable touch interaction.

## 16. Research gates before approval

For every new pattern, record:
- problem being solved
- source/pattern consulted
- why chosen
- alternative rejected
- accessibility implication
- mobile behavior
- desktop behavior
- state coverage

This makes design decisions inspectable instead of taste-based.

## 17. Screen-level acceptance test

A Penpot screen is not complete until:
- the primary task is obvious in 3 seconds or less;
- the user can identify the next action without hunting;
- no essential field is hidden in a tooltip;
- critical commercial constraints are visible before commitment;
- state changes are understandable without color alone;
- error recovery is explicit;
- long Persian text does not break geometry;
- dense information is grouped without visual noise;
- repeated components look and behave consistently;
- the design contains no unsupported product promise.

## 18. Research sources used for this addendum

- W3C WCAG 2.2 — Target Size (Minimum)
- GOV.UK Design System — Spacing
- GOV.UK Design System — Error message / Error summary / Validation
- GOV.UK Design System — Summary list
- Carbon Design System — Data table accessibility and style
- POL canonical product, design and decision documents
