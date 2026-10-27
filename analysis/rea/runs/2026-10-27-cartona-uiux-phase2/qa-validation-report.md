# QA Validation Report — CP9 (rolling)

**Gate:** `tools/qa_validate.py <run_dir> <repo_root>` — exit 0 = all PASS.
**Latest run:** 2026-10-27 → **100/100 checks PASS, exit code 0** (full output retained in session log).

## Checks performed (Addendum E/F/G)

1. CSV parse + header + uniform width — all run-dir CSVs
2. JSON parse — all run-dir JSONs
3. Evidence references: every filename-shaped token in `cartona-to-pol-pattern-mapping.csv` `evidence_reference` and `pol_current_file` resolves to a real file (run dir / prior run dir / repo root)
4. SHA-256 format (64-hex) in both inventories
5. No secret-like strings; no host personal paths (rule whitelists the documented Cartona build-machine finding `/home/ahmed/…`, which is evidence, not a leak of this environment)
6. Unique ID columns (pattern_id, gap_id, archive_path)

## Defects found by this gate during development (and fixed)

| Defect | Fix |
|---|---|
| 3 CSVs had ragged rows (unquoted commas) | regenerated through csv.writer round-trip (uniform widths 10/21/10) |
| Evidence-ref validator split prose on `+`/`;` naively → false FAILs | rule changed to filename-shaped-token resolution |
| `baseline.json` / `environment-matrix.json` contained host user path `C:\Users\…` | redacted to `%LOCALAPPDATA%\Android\Sdk`; JSONs re-validated |
| First validator run caught `pol_current_file` prose treated as path | filename-token rule applied |

## Not yet gated (pending CP3/CP4)

- screenshot-manifest cross-checks (no runtime screenshots exist yet — manifest will be validated when populated)
- final product-freeze diff review (performed at mission end)
- final report consistency counts (performed at mission end)
