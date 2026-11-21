# Quality Audit — Remediation of Known Defects (Run 2026-10-27)

Each defect follows the mandated cycle: **review previous evidence → reproduce → root cause → fix → positive test → negative test → source reconciliation → record**. Validator self-test: `validator-self-test.json` (16/16 real-file checks PASS; 6/6 negative fixtures rejected).

## QA-1 — `archive-and-split-inventory.csv` was JSON (defect §2.1)

- **Before evidence:** run 2026-10-26 file began `{` and parsed only as JSON; the `.csv` extension was wrong. Reproduced by reading the old file (still intact, immutable).
- **Root cause:** the previous generator copied `category-summary.json` directly to a `.csv` filename instead of serializing rows.
- **Fix:** new generator (`scratch/gen_remediated.py`) emits a real 5-column CSV: `artifact_label, file, category, entry_count, total_uncompressed_bytes` — 20 data rows covering base + 3 splits.
- **Positive test:** CSV parses; uniform width 5; 20 rows.
- **Negative test:** fixture `json-as-csv.csv` (JSON content with .csv extension) is **rejected** by the validator (no header/ragged).
- **Status: FIXED, root cause resolved.**

## QA-2 — `flutter-assets-inventory.csv` `size_bytes` column corrupted (defect §2.2)

- **Before evidence:** all 106 rows carried the asset *path string* in `size_bytes`.
- **Root cause (found by reproduction):** previous generator read `AssetManifest.json` values, which are **lists of variant path strings** (e.g. `["assets/fonts/Cairo/…ttf"]`), and assigned `v[0]` — a path — to the size column. The manifest does not carry sizes at all.
- **Fix:** new generator reads **actual ZIP entries** of `assets/flutter_assets/` and computes `size_bytes` from `ZipInfo.file_size` and `sha256` from real entry bytes. Additional columns: `kind` (font/raster/vector/config/web/license), `group`, `declared_in_assetmanifest`.
- **Positive test:** 113 data rows; every `size_bytes` a non-negative integer; every `sha256` 64-hex; paths unique (validator checks all three).
- **Negative tests:** fixtures `string-size.csv` and `short-sha.csv` both **rejected**.
- **Status: FIXED, root cause resolved.**

## QA-3 — 113 vs 106 asset-count discrepancy unreconciled (defect §2.2 item 6)

- **Reconciliation (path-level, machine-checked):** `asset-count-reconciliation.json`
  - Archive: 113 file entries (0 directory entries).
  - AssetManifest: 106 declared keys; **103 match archive paths** (archive paths are `assets/flutter_assets/<key>`; a first-fix bug that double-prefixed `assets/` produced 0 matches and was caught by the validator itself, then corrected).
  - Only in archive (10): `AssetManifest.bin`, `AssetManifest.json`, `FontManifest.json`, `NOTICES.Z`, `NativeAssetsManifest.json`, `fonts/MaterialIcons-Regular.otf`, `shaders/ink_sparkle.frag` (7 Flutter-infrastructure files never declared in the manifest) + 3 Font Awesome fonts stored **URL-encoded** (`Font%20Awesome%207%20Brands-Regular-400.otf`).
  - Only in manifest (3): the same 3 Font Awesome fonts with **decoded spaces** — same files, name-encoding difference, not missing assets.
  - Arithmetic: 113 = 103 + 7 infra + 3 URL-encoded twins.
- **Validator check:** `asset_count_113_106_reconciled` — PASS.
- **Status: FIXED with exact path-level reconciliation.**

## QA-4 — API catalog evidence too shallow (defect §2.3)

- **Before evidence:** 70 rows, all `http_method=UNKNOWN`, one shared evidence ID, no source location or context.
- **Root cause:** generator emitted only the path; no per-endpoint provenance.
- **Fix:** new generator records per endpoint: `source_location` (line number in the libapp.so ASCII string-pool extraction), `input_sha256` (hash of the exact snapshot copy analyzed), `evidence_id`, `adjacent_context` (up to 4 neighboring string-pool lines), `raw_variants` (dedup rule: longest variant kept per normalized key, trailing `2` suffixes merged, full variant list preserved).
- **HTTP method policy:** remains UNKNOWN unless directly recovered from code — guessing from path shape is forbidden. Relation status: all `STRING_ONLY` (no caller evidence yet recovered).
- **Status: FIXED (evidence depth); method determination remains honestly UNKNOWN.**

## QA-5 — UI catalog naming/observation status (defect §2.4)

- **Before evidence:** 21 rows with no screenshots and no status vocabulary.
- **Fix:** `ui-screen-catalog.csv` regenerated with explicit `observation_status` column; all 21 screens `STATIC_INFERRED` (none RUNTIME_OBSERVED — none were observed); screenshot column `NONE`; blocker recorded per row.
- **Validator check:** `ui_status_vocabulary` — rejects any `RUNTIME_OBSERVED` row without screenshot evidence.
- **Status: FIXED.**

## QA-6 — Validator checked structure but not meaning (defect §2.5)

- **Root cause:** previous validation was parse + count only (this is what let QA-1/QA-2 ship).
- **Fix:** new semantic validator (`scratch/semantic_validator.py`) with type/schema checks, ID format, uniqueness, reconciliation assertions, secret scanning, binary-file rejection, POL path resolution, and P0-acceptance-criteria enforcement. Row counts stated **including header** explicitly.
- **Self-test:** `validator-self-test.json` — 16/16 real-file checks PASS; 6/6 negative fixtures rejected (json-as-csv, string-size, short-sha, secret-like, ragged CSV, P0-without-criteria). Two validator bugs were themselves caught during bring-up (double-prefix reconciliation mismatch; wrong fixture assertion index) — fixed before PASS was claimed.
- **Status: FIXED and self-tested.**

## QA-7 — Dart recovery status & ABI blocker (defect §2.2 item 7)

- **Previous status:** typed recovery BLOCKED (Doldrums rejects snapshot hash); runtime UI BLOCKED (`INSTALL_FAILED_NO_MATCHING_ABIS`).
- **New development this run:** r2flutter (radareorg/trufae) was built in an isolated Docker container and **successfully parsed the ARMv7 libapp.so header** with `version_source: exact-hash` → **Dart 3.9.2** (tag_style OBJECT_HEADER v3.4+, cws 8, no-compressed-pointers, product/arm/android flags). This **corrects** the earlier Dart-2.14-era inference (REA's `kind 3` reading was a layout kind, not a version determination). Full probe results: `flutter-snapshot-and-code-recovery.md`.
- **Runtime UI:** still BLOCKED — root cause unchanged (armeabi-v7a-only libs; available emulator is x86_64 Google APIs without ARM translation). Fix requires an ARMv7-capable device or ARM-translating image; not downloaded per plan §4.7 (no silent heavy installs).
- **Status: PARTIAL — snapshot metadata now VERIFIED; typed class/function recovery pending probe results (see recovery report); UI capture BLOCKED with documented prerequisites.**

## Header-count note (per §2.5)

All CSV row counts quoted in this run's reports are **data rows excluding the header**, and the validator asserts widths over **all rows including header**. Where a legacy count included the header (e.g. "32-row matrix"), the new reports state the convention explicitly.
