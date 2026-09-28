# POL Precision Commerce — Visual Rules & Invariants

## 1. Non-Negotiable Invariants
1. **Light + Night First-Class Parity**: Every surface, component, and state MUST support both Light and Night. Night uses blue-charcoal surfaces (`#151C27`, `#1B2431`, `#202A38`), not pure black or inverted shadows.
2. **Semantic Color Only**: Colors are strictly reserved for their semantic domain:
   - Brand Blue (`#2563EB` / `#60A5FA`): Primary actions and selected navigation.
   - Accent Indigo (`#4F46E5` / `#818CF8`): Secondary brand highlights.
   - Success Green (`#15803D` / `#4ADE80`): Positive operational completion, active status.
   - Warning Amber (`#B45309` / `#FBBF24`): Pending actions, warnings, required verification.
   - Danger Red (`#B91C1C` / `#F87171`): Destructive actions, errors, rejections.
   - Neutral Gray (`#0F172A`..`#CBD5E1`): Backgrounds, surfaces, borders, text.
3. **Persian & RTL Native**:
   - Vazirmatn is primary UI font.
   - RTL reading order, right-aligned text rails, mirrored directional icons (chevron, arrow, route).
   - Non-directional icons (search, barcode, scanner, phone, settings) are NEVER mirrored.
   - Numeric values, SKU, barcodes, phone numbers, and URLs maintain correct LTR/tabular presentation.
4. **4px Rhythm Scale**: Only use increments of 4px: `4, 8, 12, 16, 20, 24, 32, 40, 48, 64px`.
5. **Radius Scale**:
   - `xs` (4px): Utility controls / micro badges
   - `sm` (8px): Inputs, buttons, segmented controls
   - `md` (12px): Standard cards and panels
   - `lg` (16px): Modals, dialogs, drawers
   - `pill` (999px): Status chips and pill badges only (never for containers).

## 2. Visual Anti-Patterns
- NO purple-blue gradient backgrounds or gradient text.
- NO glassmorphism or blur cards on data-dense commerce tables.
- NO card-nested-in-card-nested-in-card visual soup.
- NO arbitrary or raw hex color codes in component files.
- NO color as the sole indicator of state (always pair with text, icon, or badge).
- NO tiny unreadable metadata (< 11px).
