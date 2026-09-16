# POL Design System v1

## Purpose
A single component and visual language for POL Market, POL Vendor, Ops, Field Activator and Corporate surfaces.

## Canonical visual refinement
The detailed visual execution rules are defined in:
`13_PRODUCT_DESIGN/25_VISUAL_DESIGN_REFINEMENT_AND_PENPOT_STYLE_GUIDE_2026-09-16.md`

That guide is authoritative for typography, color tokens, spacing, layout, accessibility, density, component styling and Penpot visual acceptance. This file remains the high-level design-system contract.

## Design character
- Trustworthy, operational, modern B2B.
- Dense enough for commerce operations, calm enough for frequent retailer use.
- Clear hierarchy over decorative complexity.
- Persian-first RTL with robust LTR handling for prices, IDs, dates and technical values.

## Foundation layers
### Color
Use semantic roles rather than component-specific colors:
- `surface-*`
- `text-*`
- `border-*`
- `brand-*`
- `success-*`
- `warning-*`
- `danger-*`
- `info-*`
- `interactive-*`

Final numeric values and usage rules are defined in the visual refinement guide. No raw hex value should leak into component specs outside the foundation/token layer.

### Typography
Digital operational UI uses `Vazirmatn` as the primary Persian family where verified. `B Lotus` is an approved secondary POL typeface for printed documents, reports, selected corporate/editorial display headings, and other explicitly approved contexts. It is not the default dense transactional UI typeface.

Support numeric readability, tabular figures for operational tables, and distinct display/body/caption scales.

### Spacing
Use a 4/8-based scale with explicit dense-data exceptions. Do not use arbitrary one-off gaps in production components.

### Shape / elevation
Prefer moderate radius and restrained elevation. Cards should communicate grouping, not decoration.

### Motion
Use short transitions for state confirmation, drawer/sheet movement and navigation. Never make essential information depend on animation.

## Component families
- Buttons / icon buttons
- Text fields / numeric inputs
- Search / filter / sort
- Chips / badges / status
- Product cards / compact product rows
- Vendor cards
- Basket line items
- Quantity stepper
- Price / pack / MOQ blocks
- Order status timeline
- Order table / responsive order list
- Empty / loading / skeleton / error states
- Bottom navigation / top bar / side navigation
- Modal / sheet / drawer / confirmation
- Toast / inline notification / banner
- Avatar / identity block
- Profile and organization switcher
- Tabs / segmented controls
- Data tables
- Pagination
- Upload / media

## State model
Every interactive component defines at least:
`default`, `hover`, `focus`, `pressed`, `disabled`, `loading`, `error`, `success` where applicable.

## Accessibility baseline
Design to WCAG 2.2 AA-oriented practices. Interactive targets should meet or exceed the 24x24 CSS px minimum; POL's production components should normally target larger touch areas to support the target demographic. Focus must be visible and not obscured.

## Content rules
- Buttons describe actions: `افزودن به سبد`, `ثبت سفارش`, `تکرار سفارش`.
- Errors explain what happened and how to recover.
- Preserve entered values when validation fails.
- Avoid technical error codes in user-facing copy.
- Never hide a critical commercial constraint solely in tooltip text.

## Source-of-truth relationship
Design components may represent backend states but cannot reinterpret domain rules. Price, availability, MOQ, allocation and authorization states come from canonical application contracts.
