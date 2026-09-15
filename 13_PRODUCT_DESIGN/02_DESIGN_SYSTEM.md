# POL Design System v1

## Purpose
A single component and visual language for POL Market, POL Vendor, Ops, Field Activator and Corporate surfaces.

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

The final numeric palette is to be decided after brand exploration and contrast verification. No raw hex value should leak into component specs.

### Typography
Define Persian and Latin families as tokens. Support numeric readability, tabular figures for operational tables, and distinct display/body/caption scales.

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
Design to WCAG 2.2 AA-oriented practices. Interactive targets should meet or exceed the 24x24 CSS px minimum; POL's production components should normally target larger touch areas to support the target demographic. Focus must be visible and not obscured. citeturn990483search0

## Content rules
- Buttons describe actions: `افزودن به سبد`, `ثبت سفارش`, `تکرار سفارش`.
- Errors explain what happened and how to recover.
- Preserve entered values when validation fails.
- Avoid technical error codes in user-facing copy.
- Never hide a critical commercial constraint solely in tooltip text.

## Source-of-truth relationship
Design components may represent backend states but cannot reinterpret domain rules. Price, availability, MOQ, allocation and authorization states come from canonical application contracts.
