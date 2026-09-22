# POL — Precision Commerce Visual Design System

**Document ID:** `POL-DESIGN-VISUAL-001`  
**Version:** `2.0.0`  
**Date:** 2026-09-21  
**Status:** ACTIVE / CANONICAL VISUAL DIRECTION / LIGHT+NIGHT / PENPOT BUILD SOURCE  
**Repository:** `rrasi90/POL-2.3`  
**Branch:** `product-architecture-evolution-2026-09-20`  
**Master Tree:** `50_POL_MASTER_PENPOT_UI_UX_TREE_SPEC_2026-09-21.md` v3.6.0  
**Visual Direction:** **A — Precision Commerce**

---


## 0.5 Token tier architecture

Precision Commerce uses four visual abstraction tiers:

1. Primitive tokens — raw palette, type scale, spacing scale, radius and elevation primitives.
2. Semantic tokens — role-based meaning such as canvas, surface, text, brand, success, warning and focus.
3. Component tokens — component-specific assignments such as button background, input border and card surface.
4. Pattern tokens/rules — composition-level decisions used by repeatable product patterns.

A component should normally consume semantic/component tokens rather than raw primitive values.

## 0.6 Interoperability

The visual system SHOULD remain exportable to a vendor-neutral token exchange format compatible with DTCG 2025.10.

The exchange format does not become the product authority. POL semantic token names and the Master Tree remain authoritative.

## 0.7 Visual authority

This document is the canonical visual authority for the Precision Commerce direction.

Older visual documents remain preserved for traceability. Where they conflict with this document, the current registered visual authority wins.

# 0. Visual decision

POL adopts **Precision Commerce** as the canonical visual direction.

The target is:

> modern, professional, reliable, precise, calm and commerce-native — without looking like a legacy ERP and without becoming decorative consumer-app UI.

This is a **visual system**, not a color palette.

It governs:

- visual hierarchy;
- color;
- typography;
- spacing;
- shape;
- border;
- elevation;
- iconography;
- imagery;
- density;
- motion;
- component composition;
- responsive behavior;
- RTL/bidirectional behavior;
- accessibility;
- Light Theme;
- Night Theme;
- visual QA;
- Penpot token/component structure;
- design-to-code mapping.

---

# 1. Non-negotiable rules

## 1.1 Light + Night are first-class

Every canonical UI surface that exists in Light MUST have a Night counterpart.

This applies to:

- Foundations;
- Components;
- Shared UX;
- States & Patterns;
- Retailer;
- Vendor;
- Operations;
- Field Activator;
- Corporate;
- Prototypes & Flows;
- Design QA.

A Night version is not created by inverting colors after the fact.

The two themes share:

- semantic token names;
- component anatomy;
- interaction logic;
- spacing;
- typography;
- states;
- permissions;
- navigation;
- content hierarchy.

They may differ in:

- surface values;
- border contrast;
- shadow/elevation treatment;
- image treatment;
- emphasis levels;
- selected-state luminance.

## 1.2 Precision before decoration

POL should obtain visual richness from:

1. hierarchy;
2. typography;
3. spacing;
4. alignment;
5. surface layering;
6. restrained color;
7. meaningful imagery.

Avoid decorative gradients, excessive shadows, gratuitous pills, excessive glass effects and large saturated surfaces.

## 1.3 Semantic color only

A color is not allowed to mean two unrelated things in the same semantic layer.

For example:

- blue = primary interaction/brand;
- green = success/positive completion;
- amber = warning/attention;
- red = destructive/error;
- neutral = structure/inactive/default.

Do not use success green simply because it looks attractive.

## 1.4 Product is data-rich, but not visually noisy

POL is a B2B commerce platform.

The visual system must support:

- search;
- catalog browsing;
- SKU comparison;
- prices;
- stock;
- vendor information;
- orders;
- invoices;
- payments;
- delivery;
- operational queues.

Information density is adapted by surface, not by changing the brand language.

---

# 2. Visual DNA

## 2.1 Brand adjectives

The canonical adjectives are:

**Precise · Professional · Reliable · Modern · Clear · Calm · Efficient**

Avoid:

**Playful · Neon · Futuristic · Glass-heavy · Gamified · Luxury-fashion**

The product may still contain expressive campaign imagery in specific contexts, but the product UI remains operationally disciplined.

## 2.2 Composition

Preferred composition:

- strong top-level hierarchy;
- generous but controlled whitespace;
- clear alignment rails;
- consistent card geometry;
- short information clusters;
- restrained secondary content;
- one obvious primary action per meaningful context.

## 2.3 Visual hierarchy

Priority order:

1. task outcome;
2. critical information;
3. primary action;
4. supporting context;
5. secondary actions;
6. metadata.

Do not allow a banner, illustration or decorative accent to outrank the task.

---

# 3. Color architecture

## 3.1 Light theme tokens

| Token | Value | Purpose |
|---|---|---|
| `light.bg.canvas` | `#F7F9FC` | app canvas |
| `light.surface.default` | `#FFFFFF` | primary surface |
| `light.surface.subtle` | `#F1F5F9` | grouped/subtle surface |
| `light.surface.elevated` | `#FFFFFF` | modal/popover/high elevation |
| `light.border.subtle` | `#E2E8F0` | standard divider/border |
| `light.border.strong` | `#CBD5E1` | emphasized border |
| `light.text.primary` | `#0F172A` | primary text |
| `light.text.secondary` | `#475569` | supporting text |
| `light.text.muted` | `#64748B` | metadata/caption |
| `light.text.disabled` | `#94A3B8` | disabled content |
| `light.brand.primary` | `#2563EB` | primary brand/action |
| `light.brand.hover` | `#1D4ED8` | hover |
| `light.brand.active` | `#1E40AF` | pressed/active |
| `light.brand.accent` | `#4F46E5` | limited secondary emphasis |
| `light.semantic.success` | `#15803D` | success |
| `light.semantic.warning` | `#B45309` | warning |
| `light.semantic.danger` | `#B91C1C` | error/destructive |
| `light.semantic.info` | `#1D4ED8` | information |
| `light.focus.ring` | `#2563EB` | keyboard/focus |

## 3.2 Night theme tokens

Night uses blue-charcoal layers, not pure black.

| Token | Value | Purpose |
|---|---|---|
| `night.bg.canvas` | `#0F141C` | app canvas |
| `night.surface.default` | `#151C27` | primary surface |
| `night.surface.subtle` | `#1B2431` | grouped/subtle surface |
| `night.surface.elevated` | `#202A38` | modal/popover/high elevation |
| `night.border.subtle` | `#2A3646` | standard divider/border |
| `night.border.strong` | `#3A4A5F` | emphasized border |
| `night.text.primary` | `#F8FAFC` | primary text |
| `night.text.secondary` | `#CBD5E1` | supporting text |
| `night.text.muted` | `#94A3B8` | metadata/caption |
| `night.text.disabled` | `#64748B` | disabled content |
| `night.brand.primary` | `#60A5FA` | primary brand/action |
| `night.brand.hover` | `#93C5FD` | hover |
| `night.brand.active` | `#3B82F6` | pressed/active |
| `night.brand.accent` | `#818CF8` | limited secondary emphasis |
| `night.semantic.success` | `#4ADE80` | success |
| `night.semantic.warning` | `#FBBF24` | warning |
| `night.semantic.danger` | `#F87171` | error/destructive |
| `night.semantic.info` | `#60A5FA` | information |
| `night.focus.ring` | `#93C5FD` | keyboard/focus |

## 3.3 Color coverage rule

Across ordinary application screens:

- neutral surfaces carry the majority of the visual area;
- primary blue is reserved for primary interaction, active navigation and deliberate emphasis;
- accent indigo is secondary;
- semantic colors appear only where their meaning is relevant.

Large full-viewport saturated backgrounds are NOT a default POL pattern.

## 3.4 Night elevation rule

Night elevation comes primarily from:

1. surface value;
2. border distinction;
3. local contrast.

Do not recreate Light Mode white cards with strong black shadows.

---

# 4. Typography system

## 4.1 Primary UI typeface

**Vazirmatn** remains the primary Persian interface typeface.

Latin fallback may use **Source Sans Pro** where the current implementation already depends on it; the visual system must keep the bilingual rendering coherent.

## 4.2 Type scale

Canonical semantic styles:

- Display XL — 32/40
- Display L — 28/36
- Heading 1 — 24/32
- Heading 2 — 20/28
- Heading 3 — 18/26
- Title — 16/24
- Body — 14/22
- Body Small — 13/20
- Label — 12/18
- Caption — 11/16

Existing small-text usage must not be expanded. 10–11px text is restricted to metadata/caption cases where readability remains acceptable.

## 4.3 Numeric treatment

Prices, quantities, order IDs, dates and operational metrics use:

- stable digit alignment;
- predictable tabular behavior where supported;
- clear separation between number and unit;
- explicit تومان/ریال semantics;
- no decorative numerals.

---

# 5. Spacing system

Base rhythm: **4px**.

Core spacing:

`4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48 / 64`

Rules:

- 4px = micro spacing;
- 8px = control/internal spacing;
- 12px = compact component spacing;
- 16px = default component/group spacing;
- 24px = section spacing;
- 32–48px = major section separation;
- 64px = major page composition.

Avoid arbitrary one-off spacing values unless a documented visual exception exists.

---

# 6. Shape system

## 6.1 Radius

| Token | Value | Typical use |
|---|---:|---|
| radius.xs | 4px | compact utility |
| radius.sm | 8px | controls |
| radius.md | 12px | cards |
| radius.lg | 16px | major surfaces/modal |
| radius.xl | 20px | selected promotional compositions |
| radius.pill | 999px | chips/status only |

Pill geometry is NOT a default container shape.

## 6.2 Border

Default:

`1px solid semantic.border.subtle`

Strong borders are used only for:

- selected state;
- focus;
- field validation;
- critical grouping;
- table/header emphasis.

## 6.3 Shadow

Light theme uses restrained shadows:

- level 0: none;
- level 1: subtle;
- level 2: localized elevation;
- level 3: modal/popover only.

Night theme favors surface contrast and border layers over shadow.

---

# 7. Component visual contract

Every core component MUST have:

- anatomy;
- semantic tokens;
- Light variant;
- Night variant;
- hover;
- pressed;
- focus;
- disabled;
- loading where applicable;
- error where applicable;
- selected where applicable;
- RTL behavior;
- responsive behavior;
- accessibility state.

Required component families include:

- App Shell;
- Top Bar;
- Bottom Navigation;
- Sidebar;
- Search;
- Filter;
- Category Tile;
- Product Card;
- Vendor Card;
- Price Block;
- Inventory Badge;
- Order Row;
- Order Status;
- Invoice Row;
- Financial Activity Row;
- Button;
- Icon Button;
- Input;
- Select;
- Segmented Control;
- Chip;
- Badge;
- Banner;
- Alert;
- Toast;
- Modal;
- Bottom Sheet;
- Table;
- Data Row;
- Empty State;
- Error State;
- Skeleton;
- Confirmation;
- Permission Matrix;
- Timeline;
- Scanner Surface;
- Media Picker;
- Delivery Handoff Card.

---

# 8. Pattern language

## 8.1 Retailer

Retailer surfaces prefer:

- higher whitespace;
- prominent search;
- clear product imagery;
- simple category access;
- readable prices;
- large touch targets;
- low cognitive load.

## 8.2 Vendor

Vendor surfaces prefer:

- moderate information density;
- stronger list/table patterns;
- inventory visibility;
- operational quick actions;
- financial summaries;
- delegated staff context.

## 8.3 Operations

Operations surfaces prefer:

- high information density;
- queue/table patterns;
- compact rows;
- persistent filters;
- visible status;
- exceptions-first hierarchy;
- keyboard-friendly interaction on desktop.

## 8.4 Field Activator

Field surfaces prefer:

- action-first layout;
- large touch targets;
- network-awareness;
- minimal decision count;
- explicit recovery.

## 8.5 Corporate

Corporate surfaces prefer:

- lower density;
- editorial composition;
- restrained imagery;
- clear proof-oriented information;
- brand-led typography.

The same visual DNA applies to all of them.

---

# 9. Imagery and object language

## 9.1 Product imagery

Product images should:

- use consistent crop ratios per context;
- have clean/neutral backgrounds where possible;
- preserve product identity;
- avoid decorative treatment that obscures SKU recognition.

## 9.2 Promotional imagery

Hero/promotional surfaces may use photography or illustration, but they must not overpower:

- price;
- availability;
- primary action;
- seller identity.

## 9.3 Illustration

Illustrations are reserved for:

- onboarding;
- empty states;
- success;
- recovery;
- educational prompts;
- selected promotional contexts.

Do not use illustration as decoration inside every card.

---

# 10. Iconography

Canonical icon language:

- consistent optical box;
- consistent stroke family;
- consistent corner treatment;
- 16 / 20 / 24px primary sizes;
- filled treatment only when required for state emphasis;
- no mixing of unrelated icon families.

Icon meaning must remain understandable without color alone.

---

# 11. Motion

Motion is functional.

Recommended timing bands:

- micro feedback: 120–160ms;
- standard transition: 160–240ms;
- modal/bottom sheet: 200–280ms;
- complex sequence: max ~400ms unless the task requires more.

Motion MUST communicate:

- cause;
- response;
- hierarchy;
- continuity.

Reduced-motion preferences must be respected.

---

# 12. Density profiles

The product uses one visual language with three density profiles:

### D1 — Spacious Commerce
Primary: Retailer

### D2 — Balanced Operations
Primary: Vendor / general Web

### D3 — Dense Command
Primary: Operations

Density changes:

- row height;
- whitespace;
- information per viewport;
- table compactness.

Density does NOT change:

- color semantics;
- typography family;
- icon family;
- radius philosophy;
- brand identity.

---

# 13. Responsive contract

## Mobile

Priorities:

1. task;
2. primary action;
3. critical status;
4. supporting detail.

Use:

- bottom navigation;
- bottom sheets;
- stacked cards;
- horizontal scroll only where semantically justified.

## Desktop

Priorities:

- parallel information;
- table density;
- persistent context;
- sidebar/navigation where appropriate;
- keyboard efficiency.

Light/Night must remain visually coherent across both.

---

# 14. RTL / bidirectional rules

Persian is the primary interface direction.

RTL affects:

- layout direction;
- navigation order;
- alignment;
- icon placement where directional;
- tables where appropriate;
- text hierarchy.

RTL does NOT mirror icons that are semantically non-directional.

Directional icons MUST be validated for:

- back;
- forward;
- next;
- previous;
- expand/collapse;
- delivery route;
- navigation.

Mixed strings must define directionality explicitly for:

- SKU;
- barcode;
- URLs;
- phone numbers;
- order IDs;
- API identifiers;
- Latin brand names.

---

# 15. Theme parity matrix

Each canonical UI page/screen must have at minimum:

| Surface | Light | Night | Contrast QA | State QA | Responsive QA |
|---|---|---|---|---|---|
| Foundations | Required | Required | Required | Required | Required |
| Components | Required | Required | Required | Required | Required |
| Shared UX | Required | Required | Required | Required | Required |
| States & Patterns | Required | Required | Required | Required | Required |
| Retailer | Required | Required | Required | Required | Required |
| Vendor | Required | Required | Required | Required | Required |
| Operations | Required | Required | Required | Required | Required |
| Field Activator | Required | Required | Required | Required | Required |
| Corporate | Required | Required | Required | Required | Required |
| Prototypes & Flows | Required | Required | Required | Required | Required |
| Design QA | Required | Required | Required | Required | Required |

A screen is not visually closed if Night is absent unless the node is explicitly marked **THEME_NOT_APPLICABLE** with a documented reason.

---

# 16. Penpot token architecture

Token namespaces:

`pol.color.*`  
`pol.typography.*`  
`pol.spacing.*`  
`pol.radius.*`  
`pol.border.*`  
`pol.shadow.*`  
`pol.icon.*`  
`pol.motion.*`  
`pol.density.*`

Theme aliases:

`pol.theme.light.*`  
`pol.theme.night.*`

Components consume semantic tokens, not raw hex values, whenever the property is semantic.

Raw values may exist only at the primitive/token layer.

---

# 17. Design-to-code mapping

Canonical CSS/React Native semantic mapping should preserve:

- token name;
- theme;
- semantic role;
- component state.

Example:

`pol.theme.light.surface.default`

maps to the same semantic role as:

`pol.theme.night.surface.default`

The component should not know the hardcoded hex value.

---

# 18. Visual QA

Visual QA must test:

### Structure
- spacing;
- alignment;
- hierarchy;
- component anatomy.

### Theme
- Light;
- Night;
- selected/disabled/hover/focus states;
- modal/overlay surfaces.

### Accessibility
- text contrast;
- focus;
- target size;
- non-color state distinction;
- zoom/text stress.

### RTL
- direction;
- bidi;
- icon semantics;
- mixed identifiers.

### Responsive
- mobile;
- tablet;
- desktop;
- wide desktop where applicable.

### Content stress
- long Persian labels;
- long vendor names;
- long product names;
- large prices;
- empty values;
- error text;
- dense tables.

---

# 19. Golden screens

The following become visual reference screens for the Precision Commerce system:

1. Retailer Home
2. Product Search / Results
3. Product Detail
4. Vendor Storefront
5. Basket
6. Checkout
7. OrderGroup Detail
8. Financial Activity
9. Vendor Dashboard
10. Vendor Catalog
11. Operations Queue
12. Operations Financial Investigation
13. Delivery Handoff
14. Permission Editor
15. Scanner
16. Corporate Landing

Each golden screen requires:

- Light;
- Night;
- mobile;
- desktop;
- key states;
- visual evidence;
- structural evidence.

---

# 20. Migration rule from previous visual system

The new direction supersedes purely decorative or inconsistent visual patterns.

Migration targets:

- replace arbitrary colors with semantic tokens;
- replace mixed radii with the canonical radius scale;
- replace uncontrolled shadows with elevation tokens;
- consolidate icon families;
- remove generic placeholder cards;
- reduce unnecessary pills;
- normalize typography;
- normalize status colors;
- introduce Night variants for every canonical component/screen;
- preserve product behavior and domain truth.

Visual migration must NOT change:

- business rules;
- permissions;
- domain state;
- API semantics;
- financial custody model;
- MVP scope.

---

# 21. Research basis

This system is informed by established design-system practice around semantic tokens, hierarchy, spacing, theming, component systems and accessibility, including:

- Atlassian Design System foundations: `https://atlassian.design/foundations`
- IBM Carbon Design System color guidance: `https://carbondesignsystem.com/elements/color/overview/`
- Shopify Polaris: `https://polaris.shopify.com/`
- Material Design 3: `https://m3.material.io/`
- W3C WCAG 2.2: `https://www.w3.org/TR/wcag/`
- Design Tokens Community Group: `https://www.designtokens.org/`

These sources inform the visual method; they do not override POL's product, domain, API or repository authorities.

---

# 22. Closure rule

For a canonical visual node:

`DESIGN_DEFINED` requires the visual direction and semantic tokens.

`PENPOT_BUILT` requires persisted Light + Night artifacts where applicable.

`VISUAL_VERIFIED` requires independent review of composition, token usage, theme parity and responsive behavior.

A visually attractive screenshot without token/structure/theme evidence is not design closure.

