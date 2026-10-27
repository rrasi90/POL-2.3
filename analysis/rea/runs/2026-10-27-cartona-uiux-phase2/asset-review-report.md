# Asset Review Report — CP5

**Method:** `tools/build_asset_inventory.py` re-extracted every file entry under `assets/flutter_assets/` directly from `cartona app\cartona.apk` (ZIP bytes), computing SHA-256, size, kind, dimensions (PIL), and role. Color analysis via PIL median-cut on white-composited bitmaps. **Counting rule:** one row per ZIP file entry = 113 rows; 103 declared in AssetManifest.json (manifest keys are pubspec-relative; they map to ZIP paths with a `flutter_assets/` prefix; 3 of 106 manifest keys are URL-encoded Font Awesome twins that don't resolve to separate files) + 10 undeclared infra files. This reproduces the prior run's 113/103/106 reconciliation from raw bytes — CONFIRMED.

## Composition (113 rows)

| Kind | Count | Notes |
|---|---|---|
| png | 62 | app icons, illustrations, empty/error states, campaign art, category images |
| svg | 17 | vector UI assets |
| ttf/otf | 14 | text + icon fonts (see below) |
| json | 7 | config/manifest data |
| js/html/css | 7 | webview payload |
| jpg | 2 | photographic content |
| other (bin/z/yaml/frag) | 4 | shader fragment, packed data |

## Fonts recovered (role: fonts, 14 files)

Text families: **SomarSans** (Regular/Medium/SemiBold/Bold — the primary Arabic-capable UI family), **Cairo** (variable), **Rubik** (regular + italic variable). Icon fonts: MaterialIcons, CupertinoIcons, Ionicons, lucide, Font Awesome 7 (Brands/Free-Regular/Free-Solid).

**Honesty note (mission §25):** presence of these fonts in the bundle does not prove all app text uses them; the snapshot's gen-l10n corpus is Arabic-first, and SomarSans/Cairo are plausible Arabic UI fonts — treating SomarSans as the primary UI family is an **INFERRED** claim until runtime observation (CP4) can confirm rendering.

## Color findings (asset-derived, 64 bitmaps analyzed)

Most frequent dominant/secondary colors across bitmap assets: `#ffffff` (white backgrounds, 50), `#455a73` (blue-grey — appears in 14 assets, likely the core illustration/icon tone), `#d1d5dc` (light grey, 8), plus accents `#ff951b` (orange), `#1d2d92` / `#1e3a8a` (blues), `#f2d585` (gold). Provenance: asset bytes only — **this is an asset palette, not a measured runtime UI palette**; runtime screenshots (CP4) are required before calling any of these design tokens.

## Publication decision (Addendum D)

- Published: `flutter-assets-inventory.csv` (metadata + hashes only), `asset-color-analysis.csv` (hex values + dimensions), `asset-gallery-index.md` (metadata index), this report.
- **Not published:** any asset binary (PNG/SVG/font), contact-sheet images, extracted bytes. All are `cartona-proprietary-unknown`; the mission's design-pattern-over-asset-copy rule makes publication unnecessary — a designer re-creates patterns from the descriptions and measurements.
- Contact sheets: generated locally for review only if needed later; not committed.

## CP5 exit status

- [x] flutter-assets-inventory.csv (113 rows, dims + hashes)
- [x] asset-color-analysis.csv (64 rows)
- [x] asset-gallery-index.md
- [x] asset-count-reconciliation-phase2.json (reproduces prior reconciliation)
- [x] this report with license classification + publication decision
