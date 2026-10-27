# Progress Log — 2026-10-27-cartona-uiux-phase2

Append-only. Each entry: timestamp, checkpoint, actions, results, evidence, commit.

---

## 2026-10-27 — CP0 start

- `git fetch --all --prune` → clean, no new refs.
- Verified base branch `fix/pol-wave1-qa-mock-route-docs-20261027` @ `74e7ded6d695fb52c34414412bda56e634e0515b`, clean tree, in sync with origin.
- Created research branch `research/cartona-uiux-extraction-phase2-20261027` from base HEAD (corpus-bearing branch per approved plan).
- Wrote `baseline.md`, `baseline.json`, `TODO.md`, `progress-log.md`, `execution-plan.md`.
- gh CLI 2.102.0 not authenticated (pre-known; PR step deferred to CP9 per user decision).

## 2026-10-27 — CP0 commit & push verification

- Git guard before commit: `git status --short` → only run-dir files; `git diff --check` → clean; staged paths all within `analysis/rea/runs/2026-10-27-cartona-uiux-phase2/`; no secrets/binary artifacts.
- Commit + push result and remote-SHA verification recorded in the next entry (self-referential; cannot be inside the same commit).

## 2026-10-27 — CP0 commit & push verification (actual result)

- Commit: `83a0a860` "research(cartona): record phase 2 baseline and execution plan" (5 files, +320).
- Push: `git push -u origin research/cartona-uiux-extraction-phase2-20261027` → new branch created on remote.
- Remote verification command: `git ls-remote origin research/cartona-uiux-extraction-phase2-20261027` → `83a0a860275d00ee9ca92835b97980255986a961`; local `git rev-parse HEAD` → `83a0a860275d00ee9ca92835b97980255986a961`. **VERIFIED MATCH.**

## 2026-10-27 — CP1 start

- Reading prior-run artifacts for claim-by-claim audit (executive-summary.md, validation.json, run-log, CSVs) and preparing recount scripts under tools/.

## 2026-10-27 — CP1 complete

- Ran tools/recount_prior_metrics.py (rules in docstring): assets 113 rows (103 declared + 10 infra/twins) vs 119 raw ZIP `assets/` entries (6 = AppsFlyer + dexopt infra) vs 1,445 total ZIP entries; arabic_ui_strings.txt = 1,653 lines / 1,615 unique / 38 duplicate occurrences; Android strings.xml = 490 elements; screen catalog = 21 rows all STATIC_INFERRED, 0 screenshots; endpoint catalog = 70 rows all API_PATH_LITERAL_STRING_ONLY, 0 confirmed functional.
- aapt badging: com.cartona 8.4.6 / 70000083, minSdk 24, targetSdk 36, native-code armeabi-v7a (split only; base APK has no lib/).
- apksigner: Play App Signing, signer cert SHA-256 83891e0a1243…d653ee + SourceStamp present (matches prior claim).
- libapp.so re-hashed from split: 10,945,116 B, SHA-256 e150ce501b87d3c0… (matches prior run's recorded payload identity).
- Output: previous-research-audit.md (claim verdicts + metric normalization table + gaps list).
- CP1 verdict: prior research substantially sound; corrections adopted for this run's vocabulary.

## 2026-10-27 — CP2 complete (pushed aca31ac1, remote verified)

- apk-inventory.csv (8 rows) + raw JSON; integrity report: single Cartona version set (all files versionCode 70000083, same signer cert 83891e0a… + SourceStamp); base APK has zero lib/ entries (base-only install non-functional); POL test APKs are universal-ABI local builds.
- Environment matrix: only installed system image = android-35/google_apis/x86_64 (no Play variant, no ARM translation). Emulator fallback policy documented per Addendum B.
- Tooling research: ARTEMIS researched (Apache-2.0, Windows OK) but NOT activated — requires LLM provider API key + sends screenshots to external model (Addendum C §3-4). Primary path = local ADB + uiautomator + screencap. Source register written (S1-S7).

## 2026-10-27 — CP3 status update

- `adb devices` → 0 devices. Physical device not yet connected by user. Task-301/302 remain NOT_STARTED (blocked on device); recorded as WAITING, not BLOCKED_TECHNICAL. Independent phases continue.

## 2026-10-27 — CP5 complete

- tools/build_asset_inventory.py rebuilt inventory from APK bytes: 113 rows / 103 declared / 106 manifest keys — reproduces prior reconciliation exactly (CONFIRMED).
- Dimensions parsed for all 62 PNGs; fonts recovered: SomarSans (4 weights), Cairo (variable), Rubik (2), + icon fonts (MaterialIcons, Cupertino, Ionicons, lucide, FA7 ×3).
- asset-color-analysis.csv: 64 bitmaps, dominant #ffffff / #455a73 (blue-grey) / #d1d5dc; accents #ff951b, #1d2d92, #f2d585. Labeled asset-derived, not runtime tokens.
- Publication: metadata-only (no binaries); Addendum D applied.
- adb devices re-check at commit time: still 0 devices.

## 2026-10-27 — CP6 complete

- tools/dart_static_sweep.py (fixed two bugs during development: bytes/str set comparison, UTF-16 low-byte range): independent sweep of libapp.so — 70/70 endpoint literals and 24/24 routes verbatim; 15,290 ASCII runs ≥6; 2,176 UTF-16 runs (1,642 Arabic) under this run's documented thresholds.
- NEW: 34 path literals absent from prior catalogs (wallet/BNPL surface /legacy/wallet/top-up, /installment2, /pay/authorize/, /tabs/payment-gateways; onboarding new/returning split; /cart/checkout; /order/success; /cartona_v0016.sqlite). Hygiene: leaked dev path in snapshot (no credentials).
- runtime-vs-static-reconciliation.csv: 21/21 static-CONFIRMED (incl. image_error_state via full Arabic string verbatim); runtime NOT_RUN pending CP4.
- Device re-check: still 0 devices.
