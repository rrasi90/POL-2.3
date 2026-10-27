# Baseline — Cartona UI/UX Deep Extraction Phase 2

**Run ID:** `2026-10-27-cartona-uiux-phase2`
**Mission start:** 2026-10-27 (local time, Windows host)
**Mission doc:** `C:\Users\rrasi_oorj8fq\Downloads\CARTONA_UIUX_DEEP_EXTRACTION_PHASE2_COMPLETE.md`
**Governing addendum:** Mandatory Execution Addendum A–G (technical safety & evidence integrity) + user refinements on branch/PR strategy, device-first runtime, absolute product-freeze.

## Repository state (OBSERVED at mission start)

| Item | Value | Verification |
|---|---|---|
| Local path | `C:\Star\pol\2.4` | working dir confirmed |
| Remote origin | `https://github.com/rrasi90/POL-2.3.git` | `git remote -v` |
| Base branch | `fix/pol-wave1-qa-mock-route-docs-20261027` | `git branch --show-current` |
| Base HEAD | `74e7ded6d695fb52c34414412bda56e634e0515b` | `git rev-parse HEAD` |
| Working tree | clean, in sync with origin | `git status --short --branch` |
| Research branch | `research/cartona-uiux-extraction-phase2-20261027` created from base HEAD | `git checkout -b` |
| GitHub CLI | gh 2.102.0 installed, **not authenticated** (PR data unverifiable at start) | `gh --version`, `gh pr view 52` (auth error) |
| Last fetch | `git fetch --all --prune` clean, no new refs | session log |

## Branch / PR strategy (locked)

- Research branch forks from `fix/pol-wave1-qa-mock-route-docs-20261027` because it holds the full prior Cartona corpus needed by Phase 1 of this mission.
- Research Draft PR will initially target **base = `fix/pol-wave1-qa-mock-route-docs-20261027`** so its diff contains only `analysis/rea/runs/2026-10-27-cartona-uiux-phase2/**` outputs — never `main`, which would pull Wave 1 commits into the diff.
- Research PR is **not merged** until PR #52 is resolved. After PR #52's fate is known, the branch and PR target will be re-based/re-targeted per the chosen merge strategy and the diff re-verified.
- PR #52 is not touched otherwise.

## Known assets at start (OBSERVED)

### Cartona APKs (host paths; hashes recomputed during CP2)

| Artifact | Bytes | SHA-256 |
|---|---|---|
| `cartona app\cartona.apk` | 41,963,460 | `e4a0f4d1a3a607ad4e06e73fee70bf296c14205696b1cdc20892b5e893df808c` |
| `cartona app\xapk_extracted\com.cartona.apk` (base split; byte-identical to cartona.apk) | 41,963,460 | same |
| `cartona app\xapk_extracted\config.armeabi_v7a.apk` | 18,993,995 | `d232c761a42e71c47b6495ec7c9b85a343e94722e58edb669e1fa6a00f3fb1c8` |
| `cartona app\xapk_extracted\config.en.apk` | 61,849 | `da962ee2b0b0d99b07a42a3970496a4ab95ccd08ea91e3bacdffa9e746749c34` |
| `cartona app\xapk_extracted\config.mdpi.apk` | 139,457 | `5c76dd240306f335801f5649cd35c05812bdeb292ead957b2fd5b7c684300670` |

XAPK manifest (read from `manifest.json`): package `com.cartona`, name "كرتونة", version 8.4.6 / 70000083, minSdk 24, targetSdk 36, splits armeabi_v7a / en / mdpi. Prior jadx decompilation exists at `cartona app\decompiled\` and evidence material at `cartona app\evidence\`.

POL test APKs (secondary; used only for environment context): `artifacts\android\POL-Field-Test.apk`, `POL-Retailer-Test.apk`, `POL-Wholesaler-Test.apk`.

### Android tooling (OBSERVED)

- Android SDK at `C:\Users\rrasi_oorj8fq\AppData\Local\Android\Sdk` (platform-tools 37.0.1, build-tools 36.0.0/35.0.0, cmdline-tools, emulator).
- `JAVA_HOME` → Android Studio JBR, OpenJDK 21.0.9. Python 3.11.15 (venv) and 3.14.2.
- AVD `POL_API_Emulator` (pixel_6, API 35, google_apis/x86_64). No device connected at start.
- Not installed: frida, jadx binary (prior output exists), apktool, scrcpy, 7z.
- Reusable in-repo analysis scripts: none — prior run kept scripts in a private scratch dir. This run commits its own scripts under `tools/`.

### Prior research corpus (OBSERVED, on base branch)

- `13_PRODUCT_DESIGN/57_CARTONA_APP_REVERSE_ENGINEERING_DESIGN_LOGIC_2026-10-05.md`
- `13_PRODUCT_DESIGN/58_CARTONA_SCREEN_BY_SCREEN_SPEC_2026-10-05/` (10 files + data, incl. `arabic_ui_strings.txt` 1,652 lines)
- `analysis/rea/runs/2026-10-27-cartona-remediation-deep-extraction/` (37 files; claims to re-validate: v8.4.6/70000083, package com.cartona, Flutter, 113 archive entries = 103 assets, ~1,494 strings, 70 endpoints, 21 screens STATIC_INFERRED, x86_64 ABI install failure, 6,426 functions / 312 VM classes / 0 app classes, complementary APKs unavailable)
- `analysis/rea/runs/2026-10-26-cartona-comprehensive-extraction/` (19 files)

## User-provided inputs at start

1. A physical ARM Android device **will be connected** for the runtime phase (device-first strategy).
2. GitHub CLI authentication **will be provided** at the PR step (CP9); until then PR steps are recorded as pending/BLOCKED_AUTH if reached.

## Initial constraints

- Absolute product freeze: no changes to POL apps, business logic, API contracts, DB schema, permissions, or unrelated docs. All outputs confined to this run directory.
- No APK modification, no security-control bypass, no real-user account operations, no credential/OTP/PII publication.
- No paid services or unauthorized external API usage.
- Evidence vocabulary: OBSERVED / STATIC_VERIFIED / INFERRED / UNKNOWN / BLOCKED_TECHNICAL / BLOCKED_AUTH / NOT_APPLICABLE.

## Publication rules

- Publish: run-dir markdown/CSV/JSON reports, inventory with hashes, scripts, permitted measurements.
- Not published without explicit justification: APK binaries, decompiled dumps, raw proprietary assets, screenshots/contact sheets (treated as potentially proprietary until classified), any log containing PII.
- Nothing is described as "available in GitHub" unless the remote branch contains it and the remote SHA has been verified after push.
