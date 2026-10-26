# Run Log — 2026-10-26-cartona-comprehensive-extraction

## Objective
Maximize technically recoverable information from the authorized Cartona XAPK (all splits), extend the preserved Revision-2 audit, and re-audit POL against current source. Analysis-only; no POL code changes.

## Git state (observed)
- Root C:/Star/pol/2.4; branch ui/visual-qa-screen-completion-20261025; working tree clean.
- Before start: local HEAD c6ee417a, remote had advanced (c6ee417a..83f38efb; 0 ahead/2 behind) -> fast-forward merge --ff-only (no force/reset). Local HEAD after merge: 83f38efb.
- The comprehensive prompt arrived via that fast-forward (analysis/rea/COMPREHENSIVE_CARTONA_EXTRACTION_PROMPT.md, 253 lines) — read in full and followed.

## Commands/tools actually executed (chronological)
1. sha256sum + stat over cartona.apk, com.cartona.apk (=base, hash-identical), config.armeabi_v7a/en/mdpi.apk, manifest.json, icon.png.
2. REA MCP identify_flutter_build on config.en (ev_bf9eb76f...) and config.mdpi (ev_b6eed37b...): no AOT — resource-only splits.
3. Python archive-inventory generator (zipfile) -> categorized CSVs for base + 3 splits into private corpus (base: 6 DEX, 113 flutter-assets, 1194 res, 82 META-INF).
4. Res-tree enumeration of apktool decode (957 xml, 286 png); network_security_config.xml decoded (cleartext only 10.0.2.2 — CORRECTION); appsflyer backup + data-extraction rules decoded.
5. AssetManifest categorization: 87 assets/ + 10 packages (cupertino_icons, flutter_inappwebview(+web), flutter_osm_plugin(+web), font_awesome_flutter, ionicons, lucide_icons, routing_client_dart, wakelock_plus).
6. gen-l10n error string found -> Arabic strings re-searched as UTF-16LE -> 1,494 Arabic UI strings recovered (CORRECTION of revision-2 limitation). Domain counts recorded.
7. String sweeps: no graphql, no /v2|/api prefixes; ~30 state/feature flags; config constants (ABANDONED_CART_TIMEOUT_DURATION_HOURS, APPS_FLYER_* identifiers); Segment events; one embedded Google API key found (AIzaSy..., value withheld everywhere).
8. REA inspect_analysis_view dart-aot pages: package_uris (6/6 exact, ev_18ae4731...), class_like_tokens page 1 (ev_a4d04d70...).
9. Typed recovery: pip install doldrums (not on PyPI) -> cloned rscloura/Doldrums -> trial on working copy -> Exception: Unsupported Dart SDK, snapshot hash: 97ff04a7... (BLOCKED, exact error). blutter recorded as future option.
10. Security sweep: exported components (5, all framework-required), signature-protected custom permission.
11. Runtime UI attempt: existing POL_API_Emulator (API 35, Google APIs, x86_64) started via android-emulator plugin; adb install-multiple of full split set -> INSTALL_FAILED_NO_MATCHING_ABIS. No bypass, no new image. UI capture BLOCKED.
12. POL re-audit: api-client/src/index.ts read (78-line generic client, token-refresh retry, no endpoint bindings); mobile screens mock-driven (678-line mock); 9 screens + fa.ts confirmed.

## Incident record
A transient filesystem anomaly caused the first batch of run files to disappear after successful writes. All files were regenerated from preserved generator scripts (saved in the private corpus scratch/) and verified by parse + hash before commit. Nothing was fabricated; all regenerated content derives from the recorded evidence.

## Files produced (this run directory)
executive-summary.md, artifact-inventory.json, archive-and-split-inventory.csv, manifest-components.csv, flutter-assets-inventory.csv, flutter-snapshot-and-code-recovery.md, symbol-and-class-index.csv, api-endpoint-catalog.csv, route-feature-map.csv, ui-screen-catalog.csv, ui-ux-design-system.md, user-journey-maps.md, domain-data-model.md, security-and-integrity-review.md, pol-feature-gap-matrix.csv (33 rows), implementation-priorities.md, coverage-and-limitations.md, validation.json (16/16 PASS), run-log.md.

## Validation
16/16 checks PASS (JSON parse, CSV parse + widths, APK hash vs disk, evidence-ID format, no live API key committed, no binaries committed, gap-status vocabulary, POL paths resolve).

## Sync result
Appended after push: commit SHA and remote read-back recorded in sync-manifest.json and LATEST.md.
