# Final Report — Cartona UI/UX Deep Extraction Phase 2

**Run:** `2026-10-27-cartona-uiux-phase2` · **Final status: `PARTIAL — BLOCKED WITH EVIDENCE`**

## 1. Executive summary

The mission extracted and published a complete static-evidence package for Cartona v8.4.6 (APK identity, splits, signing, assets, strings, routes, API-path literals, screen catalog) and a fully mapped, scored, risk-classified adoption plan for POL — every claim re-derived from raw bytes with documented counting rules. The runtime-observation phase (real app install + screenshots) was exhausted across **three environments with full evidence**: no armeabi-v7a-capable Android environment exists on this host, and the planned physical device was never connected during the run window. Screenshots: **zero real captures** — honestly reported, not substituted with mocks.

## 2–3. Scope, branch, GitHub state

- Scope: research/documentation only; absolute product freeze (verified: 42 changed files, **0 outside the run dir, 0 product files**).
- Branch `research/cartona-uiux-extraction-phase2-20261027` forked from `fix/pol-wave1-qa-mock-route-docs-20261027` @ `74e7ded6`. Research PR strategy: Draft PR with base = the Wave-1 branch (diff = research outputs only); never merged before PR #52 resolves.

## 4. Evidence summary table

| Indicator | Verified result | Evidence |
|---|---|---|
| APKs examined | 8 (5 Cartona artifacts incl. byte-identical base copies + 3 POL test builds) | apk-inventory.csv |
| App version executed | **NOT RUN** | runtime-sessions.csv |
| Screens OBSERVED (runtime) | **0** | reconciliation CSV |
| Screens STATIC_VERIFIED (re-derived from raw bytes this run) | **21/21** | runtime-vs-static-reconciliation.csv |
| Screens INFERRED-only remaining | 0 (all upgraded with verbatim evidence) | — |
| Runtime screens BLOCKED | all (BLOCKED_RUNTIME) | android-installation-results.md §8 |
| Real screenshots | **0** (no mocks substituted; publication rules honored) | screenshot-manifest absent by design |
| Interaction flows executed | 0 (BLOCKED_TECHNICAL) | test-scenarios.csv |
| Asset rows | 113 (103 declared; dims + sha256) | flutter-assets-inventory.csv |
| Cartona→POL patterns | 18 | cartona-to-pol-pattern-mapping.csv |
| Scored POL gaps | 16 (2×P0, 6×P1, 2×P2, 1×P3, 4×HOLD, 2×PENDING_CP4) | pol-ux-gap-register.csv |
| QA checks | **110/110 PASS (exit 0)**; runtime attempts 4 (all BLOCKED evidence) | qa-validation-report.md |
| POL product-code changes | **0** | git diff vs base branch |
| Remote SHA verification | every push verified via `git ls-remote` (log in progress-log.md) | progress-log.md |

## 5–6. Environment & runtime attempts (all BLOCKED_TECHNICAL, evidence-logged)

| # | Environment | Result |
|---|---|---|
| 0 | Physical ARM device | **never connected** (`adb devices` empty at every check) |
| 1 | google_apis API 35 x86_64 (existing AVD) | attempt 1: `INSTALL_FAILED_MISSING_SPLIT` (density split mandatory); attempt 2 (4 splits): `INSTALL_FAILED_NO_MATCHING_ABIS res=-113` — no native bridge |
| 2 | google_apis_playstore API 34 x86_64 (official image downloaded 1,510,752,654 B == Content-Length, unzip-verified; AVD `CP4_Play34`) | `INSTALL_FAILED_NO_MATCHING_ABIS` — libndk translates **arm64-v8a only** (`abilist32` empty) |
| 3 | google_apis API 25 x86 (houdini hypothesis) | **disproven before install**: `abilist=x86`, zero houdini references in system.img/ramdisk.img |

Root cause across all environments: Cartona ships **armeabi-v7a-only** native code (base APK has zero `lib/` entries; all native code in the ABI split). sdkmanager downloads failed twice on connection resets; both images were recovered via resumable download of the official zips with size + zip-integrity verification. `com.cartona` was never installed; no partial state exists.

## 7–11. Static evidence package

- **Identity:** com.cartona 8.4.6/70000083, minSdk 24, targetSdk 36, Play App Signing (cert `83891e0a…` + SourceStamp) — re-verified via aapt/apksigner.
- **Prior-research audit:** all 10 claims re-verified; metrics disentangled (1,494 snapshot strings ≠ 1,615-unique curated file ≠ 490 Android resources; 70 endpoint refs = string-pool literals, 0 confirmed functional; 113 curated asset rows vs 119 raw ZIP `assets/` entries vs 1,445 total).
- **Independent payload sweep:** 15,290 ASCII runs; 2,176 UTF-16 runs (1,642 Arabic); **70/70 endpoint literals + 24/24 routes verbatim**; 34 new path literals (wallet/BNPL surface `/installment2`, `/legacy/wallet/top-up`, `/pay/authorize/`; onboarding new/returning; `/order/success`; leaked dev path documented as hygiene finding).
- **Assets:** 113 rows with dimensions + hashes; fonts SomarSans/Cairo/Rubik + 5 icon families; asset palette `#455a73`/`#d1d5dc`/`#ff951b`… (asset-derived only, never presented as runtime tokens).
- **Complementary apps:** retail 500K+ / suppliers 10K+ / driver 500+ installs from fresh official listings; supplier & driver APKs UNAVAILABLE (business-gated).

## 12–17. Design system & POL mapping

Design tokens carry explicit source+confidence; geometry/runtime palette are UNKNOWN by rule (never estimated-as-measured). 18 patterns mapped to exact POL files (`RetailerMobileScreen.tsx`, `VendorMobileScreen.tsx`, `LoginScreen.tsx`, `components/ui.tsx`, `theme.ts`); 16 gaps mechanically scored (published formula): **P0** image-error placeholder + illustration empty states; **P1** reorder (guarded), supplier signals, category illustrations, home hierarchy, signup success, vendor statements; **HOLD** wallet/BNPL, map tracking, onboarding split, seasonal campaigns. Persian copy standards (ی/ک, RTL, `i18n/fa.ts` helpers) documented. Nothing implemented.

## 18–21. QA, blockers, non-goals, reproducibility

- QA gate `tools/qa_validate.py`: **110/110 PASS, exit 0** (CSV/JSON validity, unique IDs, evidence-reference resolution, hash formats, secret/personal-path scans — it caught and fixed 3 CSV defects + 2 path leaks during development).
- Blocked items: all runtime observation (BLOCKED_TECHNICAL); supplier/driver APK access (BLOCKED_AUTH-class); PR #52 verification + PR creation (BLOCKED_AUTH until `gh auth login`).
- Not executed: every runtime flow (NOT_RUN, honestly recorded); ARTEMIS not activated (optional; requires authorized model API + external data handling).
- Reproduce: `python tools/qa_validate.py analysis/rea/runs/2026-10-27-cartona-uiux-phase2 .`; installation evidence in `android-installation-results.md`.

## 22. Commits & publication

All commits pushed and remote-verified: `83a0a860` → `bafaaaea` → `aca31ac1` → `2a8dd5c5` → `1fb2e6c2` → `3d8cd555` → `c48c77e6` → `faea41e6` → `f7647882` → (final commit this report). Branch: `research/cartona-uiux-extraction-phase2-20261027` on `github.com/rrasi90/POL-2.3`.

## 23. Final status & next step

**`PARTIAL — BLOCKED WITH EVIDENCE`** — every executable phase complete; runtime observation blocked by the absence of any armeabi-v7a-capable Android environment.

**Single next step to reach COMPLETE:** connect a physical ARM Android device (USB debugging on) → rerun CP3 install (AVDs and `tools/capture_screen.py` are ready) → CP4 screenshots → upgrade reconciliation → append to this report. Secondary: `gh auth login` for PR #52 verification + research Draft PR.
