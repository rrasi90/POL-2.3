# POL — Final Design Tokens v3

Status: CANONICAL VISUAL TOKEN BASELINE

## 1. Design principle
All visual decisions use semantic tokens. Raw values are used only inside this token definition. Screens and components must reference roles, not ad-hoc hex values.

## 2. Color roles

### Brand
- `brand.900` #071226
- `brand.800` #0A1730
- `brand.700` #10254A
- `brand.600` #16345F
- `brand.500` #1D4ED8

### Action
- `action.primary` #1D4ED8
- `action.primary-hover` #1E40AF
- `action.primary-pressed` #1E3A8A
- `action.secondary-bg` #EFF6FF
- `action.secondary-text` #1D4ED8
- `action.focus` #60A5FA

### Neutral
- `neutral.0` #FFFFFF
- `neutral.25` #FCFCFD
- `neutral.50` #F8FAFC
- `neutral.100` #F1F5F9
- `neutral.200` #E2E8F0
- `neutral.300` #CBD5E1
- `neutral.500` #64748B
- `neutral.700` #334155
- `neutral.900` #0F172A

### States
- success: `#166534` text / `#DCFCE7` surface / `#22C55E` accent
- warning: `#92400E` text / `#FEF3C7` surface / `#F59E0B` accent
- danger: `#991B1B` text / `#FEE2E2` surface / `#DC2626` accent
- info: `#075985` text / `#E0F2FE` surface / `#0284C7` accent

### Accent
Champagne gold is brand accent, not a generic status color:
- `accent.gold` #F7D4B6
- use for identity highlights, selected premium/corporate details, separators and limited emphasis.
- never use gold for success/warning semantics.

## 3. Color rules
- Body text must use `neutral.900` or an accessible semantic equivalent.
- `neutral.500` is metadata only; do not use for critical copy.
- Never encode a state using color alone; pair color with label/icon/shape.
- Primary CTA surfaces use blue; gold never replaces primary action blue.
- Large dark surfaces are reserved for shell/header/identity moments, not every card.
- Retailer default canvas is light; Vendor/Ops may use dark shell chrome with light content surfaces.

## 4. Typography

### Families
- UI primary: `Vazirmatn`
- Brand/display/printed: `B Lotus` where the environment has the verified font asset.
- Latin fallback: Inter / Arial / sans-serif as required by environment.

### UI scale
- `display-lg`: 32/40, 700
- `display-md`: 28/36, 700
- `heading-xl`: 24/32, 700
- `heading-lg`: 20/30, 700
- `heading-md`: 18/28, 700
- `body-lg`: 16/26, 400
- `body-md`: 14/22, 400
- `body-sm`: 13/20, 400
- `caption`: 12/18, 400
- `label`: 13/20, 600
- `numeric-xl`: 28/36, 700
- `numeric-lg`: 20/28, 700
- `table`: 13/20, 400/600

### Display rules
B Lotus is allowed for brand headers and long-form corporate content, not for dense operational tables, form controls or numeric-heavy areas unless a verified usability test proves equal or better readability.

### Persian typography
- Use generous line height for Persian text.
- Never vertically center by manually nudging glyphs.
- Persian numerals may be used in prose; IDs, SKU, invoice numbers and technical identifiers remain controlled LTR strings.
- Avoid justified body text.

## 5. Spacing
Use a constrained token scale inspired by 8px systems with 4px micro-steps:
`0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96`

Preferred usage:
- 4: icon/text micro-gap
- 8: control internal gap
- 12: dense row padding/gap
- 16: default content padding
- 24: section/card padding
- 32: major section gap
- 48+: page-level separation

## 6. Geometry
- radius-sm: 6
- radius-md: 10
- radius-lg: 14
- radius-xl: 20
- radius-pill: 999

Operational defaults: radius-md. Avoid excessive rounded cards.

## 7. Elevation
- `elevation-0`: none
- `elevation-1`: 0 1px 2px rgba(15,23,42,.06)
- `elevation-2`: 0 4px 12px rgba(15,23,42,.08)
- `elevation-3`: 0 12px 32px rgba(15,23,42,.12)

Use borders for grouping and elevation only when layering requires it.

## 8. Layout
- Mobile reference: 390×844.
- Desktop reference: 1440×1024.
- Mobile side padding: 16px.
- Desktop content max width: 1200–1280px depending on surface.
- Vendor/Ops tables may use full available width.
- Retailer content should avoid full-width text lines.

## 9. Interaction sizes
- Standard control height: 44px.
- Compact control: 36px for desktop dense tables only.
- Touch-critical control: 48px where feasible.
- Icon button: 44×44 minimum for mobile.
- Focus indicator: 2px visible outline with sufficient contrast.

## 10. Responsive rules
- 360–389: collapse secondary controls into sheets.
- 390–767: mobile single-column operational flow.
- 768–1023: split content where interaction remains understandable.
- 1024–1439: desktop with constrained content.
- 1440+: preserve readable content width; do not stretch every card to viewport edge.

## 11. References
The token strategy follows the general system-design approach used by USWDS: constrained token sets for color, typography and spacing improve consistency and implementation communication. USWDS documents 8px-based spacing tokens and role-based color tokens. citeturn851066search0turn851066search2turn851066search4

WCAG-oriented contrast remains the baseline for critical text and interactive elements. Color must not be the sole carrier of meaning. 
