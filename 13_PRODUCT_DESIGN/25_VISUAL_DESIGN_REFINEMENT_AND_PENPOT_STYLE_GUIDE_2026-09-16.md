# POL — Visual Design Refinement & Penpot Style Guide

**Date:** 2026-09-16  
**Status:** CANONICAL VISUAL REFINEMENT FOR PENPOT MANUAL REBUILD  
**Scope:** typography, color, spacing, layout, accessibility, density, component styling, and page-level visual rules.

This document refines the visual execution of POL without changing product, domain, authorization, payment-custody, or operational rules. It supplements `24_PENPOT_MANUAL_REBUILD_MASTER_SPEC_2026-09-16.md`.

---

# 1. Design direction

POL should look like a **serious Iranian B2B operating system**, not a consumer marketplace and not an admin template.

Visual goals:
- trustworthy
- calm
- premium but restrained
- fast to scan
- Persian-first
- operationally dense without looking crowded
- visually distinctive through navy + blue + warm gold, not through gradients or decoration

Use the visual principle:

> **Hierarchy first, decoration last.**

Carbon's current guidance similarly recommends a dominant neutral foundation, a primary blue action family, and restrained use of additional colors. citeturn881801search11turn881801search14

---

# 2. Typography strategy

## 2.1 Digital product UI

### Primary UI family
`Vazirmatn`

Use for:
- navigation
- buttons
- forms
- search
- catalog
- tables
- operational queues
- status labels
- numbers and dense transactional information

Reason: POL is a frequent-use digital B2B interface. The typography must remain highly legible in dense operational layouts. Current design-system research consistently treats type scale, line height and legibility as foundational rather than decorative. citeturn881801search0turn881801search4

### Fallback stack
`Vazirmatn, Vazir, Tahoma, Arial, sans-serif`

Verify actual font availability before freezing the Penpot master.

## 2.2 B Lotus usage

`B Lotus` is an **approved POL secondary typeface**, not the default dense UI font.

Use B Lotus for:
- printed invoices/documents
- formal reports
- certificates
- presentation/editorial headlines where a Persian serif voice adds character
- selected corporate storytelling sections
- large display headings in marketing/corporate work when readability is verified

Do not use B Lotus for:
- 10–14px operational data
- dense tables
- small buttons
- OTP/code entry
- compact status labels
- long transactional lists

This preserves the requested Persian character of B Lotus while protecting the readability requirements of high-frequency UI. GOV.UK's current typography guidance likewise prioritizes tested readability, consistent hierarchy and responsive sizing. citeturn881801search0turn881801search2

## 2.3 Type scale

### Mobile UI
- Display: 28 / 34
- H1: 24 / 30
- H2: 20 / 26
- H3: 18 / 24
- Body: 16 / 24
- Body compact: 15 / 22
- Caption: 14 / 20
- Dense metadata: 13 / 18
- Minimum UI text: 14px unless a specialist use case is explicitly justified

### Desktop UI
- Display: 32 / 40
- H1: 28 / 36
- H2: 22 / 30
- H3: 19 / 26
- Body: 16 / 24
- Body compact: 15 / 22
- Caption: 14 / 20
- Dense metadata: 13 / 18

Avoid the 9–12px text that appeared in earlier visual exploration. It is unsuitable as a default for a Persian-first operational product.

GOV.UK's current type scale keeps regular body text at 19px and small body at 16px, with responsive adjustments explicitly made to improve legibility. POL can use a slightly tighter operational scale, but the same principle applies: readable body sizes first, then density. citeturn881801search0turn881801search1

## 2.4 Weight rules

- Regular 400: body, metadata
- Medium 500: controls, important metadata
- Semibold 600: section titles, important values
- Bold 700: H1/H2, critical state labels, major totals

Do not use bold on whole paragraphs.

## 2.5 Text alignment

- Persian body text: right aligned
- Persian headings: right aligned by default
- Numeric tables: right aligned unless column semantics require another alignment
- SKU / codes / URLs / identifiers: LTR within controlled containers
- Never fully justify body paragraphs

This is consistent with current GOV.UK guidance that RTL content should be right aligned and justified text should generally be avoided for readability. citeturn881801search3

---

# 3. Color system v2

## 3.1 Brand palette

### Midnight Navy
`#0A1730`

Use for:
- top-level brand surfaces
- dark hero sections
- corporate navigation
- deep backgrounds
- important trust surfaces

### Action Blue
`#2563EB`

Use for:
- primary CTA
- links
- selected interactive controls
- active navigation

Calculated contrast against white is approximately **5.17:1**, suitable for normal-sized text when used as text/button foreground under the tested combination.

### Action Blue Strong
`#1D4ED8`

Use for:
- pressed/strong action
- high-emphasis CTA on light surfaces

Contrast against white is approximately **6.70:1**.

### Champagne Gold
`#F7D4B6`

Use sparingly for:
- premium accent
- key highlight
- brand ornament
- selected corporate emphasis

Do not use gold as the sole indicator of a state.

Gold against Midnight Navy has a very high contrast ratio (approximately **12.77:1**) under the tested pair.

## 3.2 Neutral palette

- Ink: `#101828`
- Slate: `#344054`
- Muted: `#667085`
- Subtle text: `#98A2B3`
- Border: `#D0D5DD`
- Surface: `#FFFFFF`
- Surface Soft: `#F8FAFC`
- Surface Warm: `#FAF9F7`
- Canvas: `#F3F6FA`
- Dark surface 1: `#111C2E`
- Dark surface 2: `#17233A`

Do not use pure black as the main text color on white unless required by a specific content context.

## 3.3 Semantic status colors

### Success
- Text: `#067647`
- Surface: `#ECFDF3`
- Border: `#ABEFC6`

### Warning
- Text: `#B54708`
- Surface: `#FFFAEB`
- Border: `#FEDF89`

### Danger
- Text: `#B42318`
- Surface: `#FEF3F2`
- Border: `#FECDCA`

### Info
- Text: `#175CD3`
- Surface: `#EFF8FF`
- Border: `#B2DDFF`

Semantic states must always use more than color alone: icon, label, or shape must reinforce the meaning. Carbon explicitly recommends designs that remain understandable to users who cannot distinguish certain colors. citeturn881801search5

## 3.4 Color application rule

Use approximate visual distribution:
- 70% neutrals/surfaces
- 20% navy/structural brand
- 8% action blue
- 2% gold/semantic highlights

This is a visual target, not a literal pixel formula.

Never use five saturated colors on one screen.

---

# 4. Contrast rules

Target:
- normal text: WCAG AA minimum 4.5:1
- large text: minimum 3:1
- meaningful non-text UI boundaries/icons: target 3:1 where applicable

All important actions, links, labels and status information must remain distinguishable without relying on hue alone.

Carbon's accessibility guidance uses WCAG-oriented contrast and explicitly emphasizes that good contrast benefits both users with disabilities and users working in difficult visual conditions. citeturn881801search5turn881801search7

---

# 5. Layout system

## 5.1 Mobile
Primary reference: `390 × 844`.

Use:
- page padding: 16px
- compact screen padding: 12px only for dense list/table surfaces
- section gap: 24px
- component gap: 12–16px
- card internal padding: 16px
- bottom navigation safe-area aware

## 5.2 Desktop
Primary reference: `1440 × 1024`.

Recommended content behavior:
- main content max width: 1200–1280px where practical
- 12-column grid
- outer gutter: 32px
- major column gap: 24px
- card gap: 16–24px
- dense table row height: 48–56px

GOV.UK's current layout guidance recommends starting small-screen-first and controlling line length rather than filling the entire desktop canvas. citeturn881801search10

## 5.3 Card rules

Card means **information grouping**, not decoration.

Default:
- radius: 12px
- border: 1px neutral
- shadow: none or extremely subtle
- white surface on light canvas

Elevated card only when:
- overlay
- popover
- modal/sheet
- high-priority action panel

Avoid 20–24px corner radii as a generic style.

---

# 6. Navigation styling

## Retailer mobile
Bottom navigation:
- 5 destinations maximum
- icon + label
- selected state = action blue + stronger weight
- unselected = muted neutral
- no gold selected tab

Top bar:
- brand/context left or centered according to information hierarchy
- primary task title on right
- support/notifications as secondary actions

## Vendor / Ops desktop
Sidebar:
- width: 248–272px
- navy structural region
- selected item: visible blue-accent surface, not only text color
- icons + labels always shown for primary navigation

Do not create floating "glassmorphism" navigation.

---

# 7. Buttons

Primary:
- blue fill
- white text
- radius 10px
- height 44px mobile / 40px desktop minimum

Secondary:
- white/light surface
- neutral border
- ink text

Tertiary:
- no container
- action blue text/icon

Danger:
- only for destructive actions
- never visually compete with the normal primary CTA

Button label examples:
- `افزودن به سبد`
- `ثبت سفارش`
- `تأیید موجودی`
- `پذیرش سفارش`
- `مشاهده جزئیات`
- `ارسال مدرک`

Avoid English labels unless they are unavoidable technical identifiers.

---

# 8. Commerce visual hierarchy

Use this hierarchy consistently:

`نام محصول → بسته → حداقل سفارش → قیمت → موجودی → بنکدار → مقدار → اقدام`

## Product Row
Recommended ordering:
1. product image, if recognition helps
2. product name
3. pack/case
4. availability
5. price
6. MOQ
7. quantity stepper / CTA

Do not make imagery larger than the commercial decision information.

## Price
- primary price: semibold/bold
- currency label smaller than number
- old price only when comparison is genuinely needed
- never use red merely because a price is high

## Availability
Show:
- available
- موجودی نامشخص
- موجودی به‌روز نیست
- ناموجود

Always include explanatory microcopy for unknown/stale inventory.

---

# 9. Vendor comparison visual pattern

Never design it like a consumer "best seller" ranking.

Use a neutral comparison table/card:

`بنکدار | قیمت | بسته | حداقل سفارش | وضعیت موجودی | اثر بر سبد`

No stars, fake scores or unsupported ranking badges.

---

# 10. Basket / Allocation visualization

The basket is the central visual expression of D-014.

Show one retailer basket, grouped into child vendor sections only where operationally useful.

Example:

`سبد شما`

`بنکدار الف`
- روغن لادن 4 عدد
- ماکارونی زر 2 کارتن

`بنکدار ب`
- رب روژین 6 عدد

Then:
- subtotal per group where useful
- total basket value
- explicit changed/unavailable lines
- one clear next action

Do not expose internal terms such as `AllocationPlan` to the retailer.

---

# 11. Order status styling

Status must use:
`icon + label + optional color + timeline position`

Do not use color-only states.

Example:
- ثبت شد
- پذیرفته شد
- در حال آماده‌سازی
- آماده ارسال
- ارسال شد
- تحویل شد
- نیازمند پیگیری

Critical exceptions receive stronger contrast and a clear next action.

---

# 12. Operations queue styling

Every row should answer in under two seconds:

**What happened? How serious is it? How old is it? Who owns it? What should I do?**

Recommended visual order:
1. severity/state
2. reason
3. age/SLA
4. object ID
5. actor/object context
6. next action

Avoid KPI cards above the queue unless they directly help triage.

---

# 13. Forms and validation

- label always visible before input
- helper text only when useful
- error message directly adjacent to the field
- preserve user input after recoverable errors
- do not validate aggressively while the user is still typing unless necessary
- show one concrete recovery action

Current GOV.UK guidance explicitly emphasizes clear errors, preserving entered values and readable typography. citeturn881801search0turn881801search3

---

# 14. Imagery rules

Use real FMCG packaging imagery selectively.

Preferred:
- white/neutral background
- consistent product cutout treatment
- same apparent camera scale for comparable products
- enough resolution for recognition

Avoid:
- stock lifestyle photography in transactional screens
- oversized hero product imagery
- decorative product collage

Retailer catalog imagery should support **recognition**, not dominate the ordering task.

---

# 15. Brand personality by surface

## POL Market
Warmest and simplest.
- more white space
- clearer product recognition
- friendly but not playful
- very limited gold

## POL Vendor
Most operational.
- denser tables
- stronger navy shell
- clear queue emphasis
- blue action hierarchy

## POL Ops
Most information-dense.
- highest table density
- neutral surfaces
- semantic status colors
- almost no decorative imagery

## Field Activator
Fastest mobile surface.
- large touch targets
- short labels
- obvious next action
- weak-network state highly visible

## Corporate
Most branded.
- B Lotus may be used for selected large Persian display headings
- more generous spacing
- controlled photography/illustration
- navy + gold accent allowed more prominently

---

# 16. Penpot build rules

1. Put all tokens in `00 — Foundations`.
2. Use actual reusable Penpot components in `01 — Components`.
3. Do not duplicate a component only to change color; use variants.
4. Every major component gets a stress frame with long Persian content.
5. Every critical flow has a default and a failure/recovery state.
6. Component names follow a stable semantic naming pattern.
7. Use the official POL logos from the repository assets.
8. Use B Lotus only where this guide permits it.
9. Use Vazirmatn for normal digital operational UI.
10. Never introduce an unapproved raw hex color directly in a screen.
11. Never use emoji as interface icons.
12. Never use decorative gradients on operational screens.
13. Never make a critical action depend on hover.
14. Preserve enough whitespace around primary actions to prevent accidental taps.

---

# 17. High-fidelity screen recipe

Every finished screen should contain, in this order:

1. navigation/context
2. page title
3. one-line task framing if needed
4. primary task area
5. secondary information
6. recovery/exception area
7. next action

The visual hierarchy should be explainable without reading every label.

---

# 18. Research basis

The refinement incorporates current guidance from:
- GOV.UK Design System — type scale and responsive typography. citeturn881801search0turn881801search1
- GOV.UK Design System — RTL alignment, avoiding justified body text, and font sizing. citeturn881801search3
- GOV.UK Design System — layout, small-screen-first and controlled line length. citeturn881801search10
- IBM Carbon Design System — accessible visual language, neutral layering, blue action family and restrained color usage. citeturn881801search11turn881801search14
- IBM Carbon Accessibility — contrast and non-color-dependent communication. citeturn881801search5turn881801search7
- Existing POL design-system and canonical page inventory. fileciteturn193file0 fileciteturn190file0

---

# 19. Final Penpot acceptance gate

A visual screen is accepted only when:

- Persian typography is readable at 100% zoom.
- No default UI text is below 14px.
- Body copy has appropriate line height.
- Main text/background pair passes the contrast target.
- Status is understandable without color alone.
- Primary action is visually dominant.
- Commercial constraints appear before the user commits.
- Long Persian labels do not break layout.
- Mixed LTR identifiers render correctly.
- Empty/loading/error/recovery states exist.
- B Lotus usage follows the approved contexts.
- No unapproved color or decorative treatment appears.
