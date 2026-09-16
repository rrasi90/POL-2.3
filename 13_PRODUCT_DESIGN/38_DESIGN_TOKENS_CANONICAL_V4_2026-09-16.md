# POL Canonical Design Tokens v4

## Token policy
All components consume semantic tokens. Screens must not introduce raw colors or arbitrary spacing.

## Typography
### Families
- `font.ui.fa = Vazirmatn`
- `font.display.fa = B Lotus`
- `font.print.fa = B Lotus`
- `font.latin = Inter`

### Usage
- UI body, controls, tables, operational labels: Vazirmatn.
- Brand/editorial headings and printed documents: B Lotus.
- Latin product/technical values use Inter where mixed-script rendering is cleaner.

### Scale
- display-xl 40/48, display-lg 32/40, display-md 28/36
- h1 24/32, h2 20/28, h3 18/26
- body-lg 17/28, body-md 15/24, body-sm 13/20
- caption 12/18
- numeric-xl 28/36, numeric-lg 22/30, numeric-md 16/24
- dense-table 13/20; never below 12px for meaningful UI text

## Core colors
Brand:
- navy-950 `#071426`
- navy-900 `#0A1730`
- navy-800 `#10264A`
- blue-600 `#2563EB`
- blue-700 `#1D4ED8`
- blue-800 `#1E40AF`
- gold-300 `#F7D4B6`

Neutral:
- white `#FFFFFF`
- gray-25 `#FCFDFE`
- gray-50 `#F7F9FC`
- gray-100 `#EEF2F7`
- gray-200 `#D9E0EA`
- gray-300 `#B8C2D1`
- gray-500 `#667085`
- gray-700 `#344054`
- gray-900 `#101828`

Semantic:
- success-700 `#047857`; success-bg `#ECFDF3`
- warning-700 `#B45309`; warning-bg `#FFFAEB`
- danger-700 `#B42318`; danger-bg `#FEF3F2`
- info-700 `#175CD3`; info-bg `#EFF8FF`

## Surface roles
- background: gray-50
- surface: white
- surface-subtle: gray-25
- surface-inverse: navy-900
- border-default: gray-200
- border-strong: gray-300
- text-primary: gray-900
- text-secondary: gray-700
- text-muted: gray-500
- text-inverse: white
- action-primary: blue-600
- action-primary-hover: blue-700

## Spacing
Base unit 4px; preferred production rhythm 8px.
- 4, 8, 12, 16, 20, 24, 32, 40, 48, 64
- dense row vertical padding: 8–12
- standard card padding: 16–24
- screen side padding mobile: 16
- screen side padding desktop: 24–32

## Geometry
- radius-sm 6
- radius-md 10
- radius-lg 14
- radius-xl 20
- control-height-sm 32
- control-height-md 40
- control-height-lg 48
- touch-target default 44

## Elevation
Use restrained shadows; grouping should primarily come from spacing, borders and surface contrast. Shadows are secondary.

## Focus
- focus-ring: 2px solid blue-700
- focus-offset: 2px
- high-risk focus states require visible boundary against both component and background.

## RTL/LTR
- UI flow RTL.
- Numbers, SKUs, URLs, IDs and timestamps use direction-isolated LTR containers.
- Never mirror semantic icons such as checkmarks; mirror directional icons only when meaning is directional.

## Density modes
- `comfortable`: primary retailer mobile
- `compact`: vendor/ops desktop queues
- `dense`: audit-heavy operations tables only

## B Lotus rules
- Never use B Lotus below 14px.
- Never use B Lotus for dense tables or numeric-heavy controls.
- Always test Arabic/Persian joining and glyph consistency in Penpot.
