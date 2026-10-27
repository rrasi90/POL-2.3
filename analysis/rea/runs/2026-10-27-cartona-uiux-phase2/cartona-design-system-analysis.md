# Cartona Design System Analysis — CP8 (evidence status per claim)

**Evidence ceiling:** no runtime observation yet (CP4 pending device). Everything below is asset- or payload-derived; geometry and runtime palette are UNKNOWN by rule (mission §32: estimated values are never published as measured). Companion data: `design-token-inventory.csv`, `component-pattern-catalog.csv`, `asset-color-analysis.csv`.

## 1. Color (asset-derived, STATIC_VERIFIED at asset level)

Dominant tones across the 64 analyzed bitmaps: white `#ffffff` (backgrounds of illustration assets), blue-grey `#455a73` (14 assets — the visual identity carrier of illustrations), light grey `#d1d5dc`. Accents: orange `#ff951b`, deep blues `#1d2d92`/`#1e3a8a`, gold `#f2d585` (campaign/seasonal family).

**Confidence caveat:** this is the illustration palette, not a measured runtime UI palette. The app's chrome (nav, buttons, CTA) is UNKNOWN until CP4. POL must not adopt these hex values (see pol-design-system-compatibility.md).

## 2. Typography (presence STATIC_VERIFIED, roles INFERRED)

SomarSans (4 weights — Arabic-capable, likely primary), Cairo (variable), Rubik (2 variants). Plus 5 icon-font families. Actual text rendering unverified until runtime.

## 3. Localization & RTL (STATIC_VERIFIED)

Arabic-first via Flutter `gen-l10n` (error-string evidence); `layoutDirection` configChanges + `values-ldrtl` resources; en locale split exists. RTL-native design is structural, not an afterthought — the same discipline POL already applies with Vazirmatn + `direction: "rtl"`.

## 4. Structure (routes STATIC_VERIFIED as strings, layout INFERRED)

24 navigation routes + 34 additional path literals (CP6). Three-surface model: discover (home/categories/search/suppliers) → transact (cart/checkout/orders/reorder/tracking) → account (wallet/credit/branches/users/notifications/settings). Distinctive surfaces vs POL: wallet+BNPL, reorder-first orders, seasonal campaign system, onboarding new/returning split.

## 5. Component vocabulary (component-pattern-catalog.csv, 16 components)

Image-tile categories, illustration-backed empty/error states (2 of the strongest adoptable patterns), supplier cards with terms signals, dedicated search, OTP flow, cart validation, order success screen, status chips. Components with UNKNOWN runtime shape: bottom sheets, skeletons, dialogs — deferred to CP4.

## 6. What POL should take — and what it should not

**Take (pattern level):** illustration-backed state communication; reorder as first-class; supplier trust signals on cards; explicit post-checkout success; graceful image failure.
**Do not take:** Cartona branding/colors/fonts/assets; group-order minimum-bypass mechanics (BUSINESS_LOGIC_RISK); BNPL mechanics (product decision); OSM tracking dependency (product decision).

## 7. Open items blocking full design-system extraction

1. Runtime screenshots (CP4) — needed for geometry, runtime palette, nav bar layout, spacing.
2. Post-auth screens (BLOCKED_AUTH without an authorized test account).
3. Typed Dart app classes — not recoverable on ARMv7 with available tools (CP1/CP6 verdict stands).
