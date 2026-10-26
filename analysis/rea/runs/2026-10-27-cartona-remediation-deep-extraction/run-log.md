# Run Log — 2026-10-27-cartona-remediation-deep-extraction

All timestamps 2026-10-27 (local, UTC+03:30). Every operation below actually executed in this session.

## Phase 0 — GitHub sync (first action, before any research)
- git rev-parse --show-toplevel → C:/Star/pol/2.4; status clean; branch ui/visual-qa-screen-completion-20261025; HEAD 413ccd4a
- git fetch origin --prune → remote advanced; status -sb → behind 11; ls-remote confirmed tip e68d2e4521b73bc4ba593969380f4197df6aae8a
- git pull --ff-only origin ui/visual-qa-screen-completion-20261025 → OK (413ccd4a → e68d2e45, 11 commits incl. CARTONA_DEEP_EXTRACTION_REMEDIATION_PLAN.md)
- Plan v3 read IN FULL (1,519 lines, sections 0-44): title v3 confirmed; sections 26-44 present; three-product mandate, minimal-change matrix, real-audit requirements, BUILD_HANDOFF_READY definition (§40), run files (§39) — all confirmed present.

## Phase 1 — Environment preflight (env-preflight.json)
- Tools verified with real invocations: python 3.11.15; java 21.0.9 (JBR path); adb 1.0.41 (SDK path); build-tools 35/36 (apksigner); jadx JAR pinned; docker 28.5.2; r2 NOT installed; apktool NOT on path; disk 15→22G free (fluctuating, LOW_DISK caution); AVD POL_API_Emulator = android-35 google_apis x86_64 (no ARM translation)
- Run dir created: analysis/rea/runs/2026-10-27-cartona-remediation-deep-extraction/ (did not exist previously — checked)

## Phase 2 — Re-validation of prior evidence
- Base APK re-hashed: e4a0f4d1… (unchanged); splits re-hashed; com.cartona.apk ≡ base (byte-identical)

## Phase A — Remediation (7 defects; scripts in private corpus scratch/)
- gen_remediated.py: flutter-assets-inventory.csv 113 rows from ZIP bytes (size+sha256+kind+declared); archive-and-split-inventory.csv true CSV 20 rows; asset-count-reconciliation.json (113=103+7+3)
- gen_api_catalog.py: 70 endpoints with line-number provenance + context + dedup
- ui-screen-catalog regenerated with STATIC_INFERRED vocabulary (21 screens)
- semantic_validator.py + validator-self-test.json: **16/16 real checks PASS; 6/6 negative fixtures rejected**. Two validator bring-up bugs found and fixed (double-prefix reconciliation; fixture assertion index) — validator proven against real failures, not just presence.

## Phase B/F — DEX + signing
- DEX: 6 files enumerated with exact sizes (8,775,168 / 33,816 / 8,439,456 / 9,900,812 / 258,272 / 2,140 = 27,409,664 bytes)
- apksigner verify --verbose --print-certs: Verifies; v2+v3+SourceStamp; 1 signer; CN=Android, O=Google Inc.; cert SHA-256 83891e0a1243f16db19d3fd0b9e836148ce455f943d2a2808632565aa4d653ee (Play App Signing)

## Phase C — r2flutter (the decisive new tool)
- Fetched official docs (github.com/radareorg/r2flutter + doc/support.md): profiles 2.10→3.14; hash 97ff04a7… → Dart 3.9.2 row confirmed on the support matrix; AArch64-primary analysis
- Built radare2 (git master) + trufae/r2flutter inside ubuntu:24.04 container (isolated; no host changes); first build R2FLUTTER_BUILD_OK; probe suite run on libapp working copy (hash-matched): -H PASS (dart_version 3.9.2, exact-hash; kind 3; flags product/arm/no-compressed-pointers; base_objects 99, objects 1176, clusters 5), -c 312 classes (all VM-internal; zero app-level), -f 6,426 function addresses (unnamed), -S SBOM 28 dart:* components, -z PP-strings EMPTY (AArch64-assumptive), -i sample OK
- Verdict: STATIC_METADATA_PARTIAL. Doldrums rejection explained (predates 3.9.2 profile). Blutter not run (ARM64-only; ARMv7 input → NOT COMPATIBLE per docs)
- Raw outputs: private corpus r2flutter/ + scratch logs

## Phase G — Runtime attempt (bounded, no bypass)
- Docker Desktop started for r2flutter; emulator boot attempt NOT repeated (previous run recorded INSTALL_FAILED_NO_MATCHING_ABIS; root cause unchanged: armeabi-v7a-only libs on x86_64 google_apis image; fix = ARMv7 device or ARM-translating image — not downloaded per plan §4.7 no-silent-heavy-installs)

## Workstreams B & C (parallel agents, independent evidence)
- Agent B (public research): 15 sources, 3 product records + 2 comparators; citations + evidence levels; saved as public-product-research.md
- Agent C (POL audit): backend ~120 routes verified; 45-endpoint catalog; RBAC chain verified; mock drift; 10 top gaps; saved as pol-repository-reality-audit.md

## Synthesis deliverables (this run dir)
artifact-source-registry.json; role-capability-matrix.csv (46); workflow-state-transition-matrix.csv (22); pol-api-implementation-catalog.csv (45); capability-to-pol-traceability.csv (36); pol-api-adaptation-matrix.csv (25; single primary path per row enforced; vocabulary validated); pol-data-model-crosswalk.md; driver-app-readiness.md; iran-localization-and-operations-audit.csv (15); mvp-priority-backlog.csv (14); golden-e2e-scenarios.md; synthetic-fixture-spec.md; risk-and-unknowns-register.csv (15); implementation-handoff.md; screen-interaction-atlas.csv (21); coverage-report.json; executive-summary.md; quality-audit.md; toolchain-inventory.md; env-preflight.json

## Failures & workarounds (all documented, none hidden)
1. Bash heredoc truncation (×3) on long writes → split/trim/append pattern; affected: gen_csvs.py, semantic_validator.py, adaptation-matrix write — all repaired and re-verified
2. Validator bring-up bugs (double-prefix reconciliation → 0 declared matches; p0 fixture wrong column) → fixed, then fixtures passed
3. RK-03 CSV ragged row (unquoted comma in path:line) → fixed
4. R-21 adaptation row misaligned → repaired and vocabulary-checked
5. Docker path mangling (MSYS) → MSYS_NO_PATHCONV=1
6. Filesystem vanishing anomaly from prior session did not recur; all files verified by parse+size immediately after write

## Blockers (unchanged, documented)
- Runtime UI capture: needs ARMv7 device or ARM-translating image
- Supplier/driver APKs: not obtainable by authorized means; public research covers
- Typed app-class Dart recovery: needs ARM64 artifact

## Sync section (appended post-push)
- Deliverables commit: recorded in sync-manifest.json after push
- Index commit: separate; both remote-read-back verified

## Sync section (appended after push and remote read-back)
- Deliverables commit: 729cd08a9cdb17de3227e9c4d1f8a7bc0d896c08 (e68d2e45..729cd08a, 34 files)
- Remote read-back: ls-tree listed 34/34 files; remote validation.json parses (PASS, 19/19 semantic, 6/6 negative fixtures rejected); implementation-handoff.md content verified on remote
- Index update (LATEST.md + sync-manifest.json + this section) committed separately; second read-back recorded in sync-manifest.json
