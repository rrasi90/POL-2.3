# POL — Design System v2: Research-Based Visual & Interaction Rules

**Date:** 2026-09-16  
**Status:** CANONICAL VISUAL EXECUTION GUIDE  
**Purpose:** Rebuild POL's visual language from first principles using established design-system and accessibility guidance, rather than decorating the existing screens.

## 0. Core rule: design as if nothing is known

Every POL visual decision must be justified by one or more of:
1. user task and business context;
2. established interaction/design-system principles;
3. accessibility requirements;
4. POL's canonical product rules;
5. measured visual QA.

Do not preserve a visual choice merely because it exists in the current Penpot file.

The design system uses semantic tokens rather than ad-hoc visual values. This follows established design-system practice: USWDS treats typography, spacing, color and related properties as discrete tokens, while Carbon uses role-based tokens across color, spacing and typography. citeturn180897search0turn892394search6

## 1. Design goals

POL should feel:
- dependable rather than flashy;
- fast rather than feature-heavy;
- professional rather than corporate-cold;
- Persian-first rather than translated-from-English;
- operational rather than consumer-marketplace;
- calm under error and exception states.

The visual system must make scanning, comparison, ordering, confirmation and recovery easier.

## 2. Visual hierarchy principles

### 2.1 Scale
Use type size, weight and container scale to create hierarchy. Do not use color as the primary hierarchy mechanism.

### 2.2 Contrast
Use contrast to separate priority levels, not to decorate every element.

### 2.3 Proximity
Related information must be visually close. Action controls should stay close to the object they modify. This is a core Gestalt principle and is especially important for task-focused interfaces. citeturn892394search0turn892394search2

### 2.4 Common region
Use a light container/background change when proximity alone is insufficient. Do not put every element into a card.

### 2.5 Balance
Avoid equal visual weight for unequal priorities. The primary task must dominate.

### 2.6 One focal point
Each screen should have one dominant task/focal region. Secondary operations should be visually quieter.

NN/g's current visual-design guidance identifies scale, hierarchy, balance, contrast and Gestalt as central principles affecting usability. citeturn892394search5

## 3. Color system v2

### 3.1 Role-based architecture

Use these semantic layers:

```text
color.brand.*
color.action.*
color.surface.*
color.text.*
color.border.*
color.success.*
color.warning.*
color.danger.*
color.info.*
color.focus.*
color.overlay.*
```

Do not place raw hex values directly in component specifications.

### 3.2 POL brand palette

**Core identity**
- `brand.navy.950` = `#071426`
- `brand.navy.900` = `#0A1730`
- `brand.navy.800` = `#102342`
- `brand.blue.700` = `#1D4ED8`
- `brand.blue.600` = `#2563EB`
- `brand.blue.500` = `#3B82F6`
- `brand.gold.400` = `#C79A5B`
- `brand.gold.300` = `#D9B77A`
- `brand.gold.100` = `#F7E7CF`

The previous Champagne Gold `#F7D4B6` is retained only as a warm highlight/accent, not as a primary text color.

### 3.3 Neutral scale

```text
neutral.0   = #FFFFFF
neutral.25  = #FCFDFE
neutral.50  = #F7F8FA
neutral.100 = #F0F2F5
neutral.200 = #E2E6EB
neutral.300 = #CBD1D9
neutral.400 = #98A2B3
neutral.500 = #667085
neutral.600 = #475467
neutral.700 = #344054
neutral.800 = #1D2939
neutral.900 = #101828
```

Default light UI should use `neutral.0` or `neutral.25` for the main canvas, not navy as the whole application background. Navy is used strategically for shell, brand moments and high-confidence emphasis.

### 3.4 Semantic colors

Success:
- `success.700 = #067647`
- `success.100 = #ECFDF3`

Warning:
- `warning.700 = #B54708`
- `warning.100 = #FFFAEB`

Danger:
- `danger.700 = #B42318`
- `danger.100 = #FEF3F2`

Info:
- `info.700 = #175CD3`
- `info.100 = #EFF8FF`

These colors are paired with labels/icons/borders. Never communicate state by color alone. USWDS and Carbon both emphasize accessibility, contrast and non-color cues. citeturn180897search1turn180897search3turn892394search3

### 3.5 Color usage ratio

For non-neutral colors, start approximately from:
- 60% primary/brand family;
- 30% secondary/supporting family;
- 10% accent.

This is a starting proportion, not a rigid rule. USWDS explicitly uses a similar role-based 60/30/10 framing for theme colors. citeturn180897search2

### 3.6 Color rules

- Primary CTA: `brand.blue.700` or `brand.blue.600` on white/light surfaces.
- Primary CTA text: white.
- Body text: `neutral.800` or darker.
- Secondary text: `neutral.600`.
- Placeholder/muted text: `neutral.500`, only where contrast remains sufficient.
- Gold is accent, not body text.
- Danger is for destructive/error semantics, never decoration.
- Success/warning/danger/info cards must include text/icon plus color.
- Avoid large saturated surfaces behind large text unless contrast is verified.

WCAG AA baseline for normal text is 4.5:1 and large text is 3:1; graphical/non-text contrast also needs explicit review. citeturn180897search1turn892394search13

## 4. Typography v2

### 4.1 Font strategy

**Primary operational UI:** Vazirmatn  
**Display/editorial/printed Persian:** B Lotus  
**Numerical/technical fallback:** Vazirmatn with tabular numerals where supported, otherwise a system numeric fallback.

Why not B Lotus everywhere? A typeface can be brand-appropriate but still suboptimal for dense UI controls, tables and compact operational data. Typography must be optimized for readability and interaction, not only identity. USWDS and Carbon both treat typography as a functional readability system. citeturn180897search4turn892394search1

### 4.2 Type tokens

```text
Display XL: 36 / 48 / 700
Display L : 30 / 40 / 700
Display M : 26 / 36 / 700
H1        : 24 / 34 / 700
H2        : 20 / 30 / 700
H3        : 18 / 28 / 700
Body L    : 16 / 26 / 400
Body M    : 15 / 24 / 400
Body S    : 14 / 22 / 400
Label L   : 14 / 20 / 600
Label M   : 13 / 20 / 600
Caption   : 12 / 18 / 400
Micro     : 11 / 16 / 500 (QA-only; avoid for critical information)
```

### 4.3 Persian-specific rules

- Use full Persian shaping; do not fake bold with transforms.
- Avoid long all-caps Latin mixed into Persian.
- Do not squeeze Persian text to make English-style layouts fit.
- Keep numbers and identifiers visually distinct from prose.
- Use adequate line-height for Persian diacritics and joining forms.
- Never make 11–12px the default UI text. Small text is for tertiary metadata only.
- Headings must have logical hierarchy; typography guidance should remain structurally meaningful. citeturn180897search10

### 4.4 B Lotus usage

Use B Lotus for:
- corporate hero/headline moments;
- printed documents;
- investor/official PDF layouts;
- major Persian campaign/editorial headings;
- selected onboarding brand moments.

Do not use B Lotus for:
- dense data tables;
- SKU/invoice identifiers;
- quantity steppers;
- compact filters;
- OTP/phone fields;
- operational dashboards.

### 4.5 Typography QA

Every new Penpot page gets:
- short Persian labels;
- long Persian labels;
- mixed Persian/Latin product name;
- Persian digits and Latin digits;
- price/Toman;
- SKU/invoice ID;
- long error message;
- button label stress test.

## 5. Spacing system

Base unit: **4px**.

```text
space-1  = 4
space-2  = 8
space-3  = 12
space-4  = 16
space-5  = 20
space-6  = 24
space-8  = 32
space-10 = 40
space-12 = 48
space-16 = 64
space-20 = 80
```

Use 8/12/16/24/32 most frequently. Use 4 and 20 only for micro-adjustments.

Do not create arbitrary 13px/17px/23px spacing unless a measured component requirement justifies it.

## 6. Layout system

### Mobile 390 × 844
- page side padding: 16px
- safe-area-aware bottom navigation
- minimum comfortable touch target: 44px for primary interactive controls
- section spacing: 24px
- component internal padding: typically 12–16px

### Desktop 1440 × 1024
- application shell + content canvas
- content max width: 1280px unless workflow needs full-width table
- side navigation: 240–264px
- page padding: 32px
- content section gap: 32px
- table row height: 48–56px depending on density

### Responsive
At 1024px:
- simplify side navigation;
- reduce secondary columns;
- keep critical actions visible.

At 768px:
- collapse multi-column content into priority-ordered stacks;
- convert wide tables into cards/row details where needed.

At 390/360px:
- preserve task order;
- remove decorative panels before removing operational information;
- keep CTA visible without excessive scrolling.

## 7. Surface architecture

### Light operational default
Use:
- canvas: neutral.25
- primary content surfaces: neutral.0
- borders: neutral.200
- primary text: neutral.900
- secondary text: neutral.600
- primary action: blue.700

### Navy brand surfaces
Use navy for:
- corporate header;
- retailer/vendor brand areas;
- strong contextual headers;
- selected high-level navigation states.

Do not make every card navy.

### Gold accent
Use gold for:
- small brand accents;
- selected highlights;
- premium/official document styling;
- separators or subtle markers.

Do not use gold as a general interactive action color.

## 8. Component geometry

### Buttons
Primary:
- height 44px mobile / 40–44px desktop;
- horizontal padding 16–20px;
- radius 10px;
- font 14–15px, weight 600;
- icon gap 8px.

Secondary:
- same height;
- neutral border;
- no filled navy background by default.

Destructive:
- use danger semantic tokens;
- confirmation for irreversible operations.

### Inputs
- min height 44px;
- radius 10px;
- border 1px;
- clear focus ring 2px+
- labels above input;
- supporting text directly below;
- errors directly adjacent to the affected field.

### Cards
Default card:
- radius 12px;
- border 1px neutral.200;
- no heavy shadow;
- padding 16px.

Use cards to group meaning, not because every object needs a container. Proximity and whitespace often communicate grouping better. citeturn892394search0turn892394search10

### Product row
Mobile height target: 72–96px depending on metadata.
Order:
`product identity → pack → price → availability → MOQ → quantity/action`

Do not bury the CTA below unrelated metadata.

### Status
Every state uses:
`icon/symbol + label + optional short explanation`

Examples:
- `موجود` + check
- `ناموجود` + minus/block icon
- `نیازمند بررسی` + alert icon
- `در انتظار تأیید` + clock icon

Never color-only.

## 9. Information density rules

POL is operational B2B, so density matters. But dense does not mean tiny.

Use a hierarchy of:
1. task-critical information;
2. decision-support information;
3. context;
4. audit/history;
5. decorative/brand content.

Only categories 1–3 belong in the main decision surface by default.

For tables:
- keep row actions close to row data;
- use clear column headers;
- avoid excessive zebra striping;
- use status pills sparingly;
- keep numeric columns aligned consistently;
- never hide key action behind hover-only behavior.

## 10. Navigation principles

### Retailer
`خانه → خرید → سفارش‌ها → سبد → حساب`

Use bottom navigation only for top-level destinations.

### Vendor/Ops
Use persistent side navigation with clear active state.

### Field
Task list first; deep navigation second.

Navigation should expose the user's mental model, not backend table names.

## 11. Persian-first content rules

Use simple operational language:
- `افزودن به سبد`
- `ثبت سفارش`
- `تأیید سفارش`
- `تکرار سفارش`
- `بررسی و ثبت`
- `در انتظار تأیید`
- `نیازمند بررسی`
- `تلاش دوباره`
- `بازگشت به سفارش`

Avoid unnecessary English labels such as `Dashboard`, `Checkout`, `Status`, `Submit`, `Review` when a clear Persian equivalent exists.

English may remain where it is a recognized identifier/product name or where technical LTR data is genuinely required.

## 12. Interaction rules

- Primary action appears where attention is already concentrated.
- Action must remain near the object it modifies. citeturn892394search2
- Preserve user-entered values after recoverable errors.
- Never rely on hover for critical information.
- Focus must be visibly distinct.
- Disabled controls explain why they are unavailable where useful.
- Success feedback should confirm the result and expose the next useful action.
- Error messages state: what happened + what the user can do next.

## 13. Accessibility rules

Target WCAG 2.2 AA-oriented implementation.

Minimum design checks:
- normal text contrast ≥ 4.5:1;
- large text contrast ≥ 3:1;
- meaningful non-text graphics/control boundaries generally ≥ 3:1;
- visible focus;
- keyboard-operable interaction;
- no color-only state communication;
- logical reading order;
- responsive text scaling;
- sufficient target size;
- zoom-friendly layout.

USWDS and Carbon both emphasize perceivable, operable and understandable interfaces, visible focus, large interaction targets and non-color state cues. citeturn180897search3turn892394search3

## 14. Motion

- 120–180ms for small state transitions;
- 180–240ms for sheets/drawers;
- no animation for critical error meaning;
- respect reduced-motion preferences in implementation.

## 15. Image and product photography

Product images are functional recognition aids.

Rules:
- consistent crop ratio;
- clean background;
- avoid random stock photography inside operational screens;
- use real FMCG packaging where it materially helps recognition;
- image must never replace the product name, pack or commercial data.

## 16. Screen composition template

Every screen should be designed through this sequence:

```text
1. Context
2. Page title
3. Immediate task / critical state
4. Primary content
5. Primary action
6. Secondary information
7. Recovery/help
8. Persistent navigation
```

Do not begin from decoration. Begin from the decision the user needs to make.

## 17. QA gate before a screen enters Penpot final

A screen fails visual QA if any of these is true:
- primary action cannot be identified in 3 seconds;
- two unrelated regions look like one group;
- body text is smaller than 13px without a strong reason;
- status depends on color only;
- important information is separated too far from the action using it;
- typography hierarchy is ambiguous;
- there is excessive card nesting;
- a decorative element competes with a task-critical element;
- Persian labels wrap awkwardly or clip;
- mixed-direction content is visually reversed;
- contrast has not been reviewed;
- mobile layout requires horizontal scrolling for a primary task.

## 18. Research sources used

- U.S. Web Design System — Design Tokens. citeturn180897search0
- U.S. Web Design System — Color and accessibility. citeturn180897search1
- U.S. Web Design System — Accessibility. citeturn180897search3
- U.S. Web Design System — Typography. citeturn180897search4turn180897search10
- Carbon Design System — Typography. citeturn892394search1
- Carbon Design System — Themes/Tokens. citeturn892394search6
- Carbon Design System — Accessibility. citeturn892394search3
- Nielsen Norman Group — 5 Principles of Visual Design in UX. citeturn892394search5
- Nielsen Norman Group — Proximity Principle. citeturn892394search0turn892394search2

## 19. Penpot build instruction

The 00 — Foundations page must be rebuilt before role-specific pages.

Then build in this order:
1. tokens;
2. typography specimens;
3. buttons/inputs;
4. product/price/MOQ/availability primitives;
5. basket/allocation/order primitives;
6. states;
7. navigation shells;
8. retailer core loop;
9. vendor core loop;
10. ops;
11. field;
12. corporate;
13. prototype flows;
14. accessibility QA.

Any existing Penpot object that conflicts with this document should be treated as legacy until explicitly reconciled against the canonical product/design rules.