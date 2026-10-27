# Previous-Research Audit — CP1

**Auditor run:** 2026-10-27-cartona-uiux-phase2
**Objects audited:** run `2026-10-26-cartona-comprehensive-extraction` (19 files), run `2026-10-27-cartona-remediation-deep-extraction` (37 files), docs `13_PRODUCT_DESIGN/57_…` and `13_PRODUCT_DESIGN/58_…/`
**Recount tool:** `tools/recount_prior_metrics.py` (rules in its docstring; raw output `tools/recount-results.json`)
**Verification commands:** `aapt dump badging`, `apksigner verify --print-certs`, direct `zipfile` enumeration + SHA-256 of `cartona app/cartona.apk` and the three XAPK splits.

Verdict vocabulary: `CONFIRMED` (independently re-derived this run) · `CONFIRMED_BY_PROVENANCE` (reported numbers internally consistent and payload identity verified; re-derivation would require the private tool corpus) · `REVISED` (true but misleading without a correction) · `WRONG` · `UNVERIFIABLE` · `NOT_RUN`

---

## 1. Claim-by-claim verdicts (mission §9)

| # | Prior claim | Verdict | This run's evidence |
|---|---|---|---|
| 1 | Cartona version 8.4.6, versionCode 70000083 | **CONFIRMED** | `aapt dump badging cartona.apk` → `name='com.cartona' versionCode='70000083' versionName='8.4.6'`, minSdk 24, targetSdk 36 |
| 2 | Android package `com.cartona` | **CONFIRMED** | same badging output; split `config.armeabi_v7a` same package/versionCode |
| 3 | Flutter-based implementation | **CONFIRMED** | `lib/armeabi-v7a/libapp.so` (10,945,116 B, SHA-256 `e150ce501b87d3c0…`) + `libflutter.so` inside the armeabi-v7a split; snapshot kind 3 per prior r2flutter header read |
| 4 | "113 asset inventory entries" | **CONFIRMED, with scope correction** | 113 = curated inventory rows (103 declared in AssetManifest + 10 infra/URL-encoded twins). Raw ZIP reality: **1,445 total entries; 119 under `assets/`**. The 6-entry delta vs 113 = 4 AppsFlyer SDK internals + `assets/dexopt/baseline.prof(m)` — infra, not UI assets. Prior reconciliation (113/106, 10+3) reproduced exactly. |
| 5 | "≈1,494 Arabic UI strings extracted" | **CONFIRMED as a DISTINCT metric — must not be equated with the 1,652-line file** | Three different corpora exist: (a) **1,494** = Arabic strings among 1,966 UTF-16LE runs recovered from the Dart snapshot (run 2026-10-26; raw dump private/local-only, not re-derivable here); (b) **`58_…/data/arabic_ui_strings.txt` = 1,653 lines, 1,615 unique records, 38 duplicate occurrences** (recounted this run); (c) **490 `<string>` elements** in decompiled `res/values/strings.xml`. These are different extraction sources (snapshot string pool vs curated corpus vs Android resources). See §2. |
| 6 | "70 endpoint references" | **REVISED framing** | All 70 rows carry `http_method=UNKNOWN` + `relation_status=STRING_ONLY`; per-row classification (Addendum F): **70 × API_PATH_LITERAL_STRING_ONLY, 0 × URL_LITERAL, 0 × CONFIRMED_FUNCTIONAL_ENDPOINT**. They are path-shaped string-pool literals from libapp.so (ASCII pool, per-row line provenance). Presence of the literal ≠ a working API route. The prior catalog was internally honest (STRING_ONLY) but the summary word "endpoint" invites over-reading. |
| 7 | 21 screens, all `STATIC_INFERRED` | **CONFIRMED** | `ui-screen-catalog.csv`: 21 data rows, status distribution `{STATIC_INFERRED: 21}`, 0 rows with any screenshot value |
| 8 | x86_64 emulator install failure (ABI) | **CONFIRMED as historical fact, root cause consistent** | Base APK has **no `lib/` entries at all**; all native code is in the `config.armeabi_v7a` split (`native-code: 'armeabi-v7a'` per aapt). The existing AVD is `google_apis/x86_64` API 35 with no ARM translation. Install without the split set or on a non-ARMv7-capable runtime must fail. Re-test scheduled as CP3 supplementary evidence only. |
| 9 | 6,426 function addresses + 312 VM classes, 0 app-level classes | **CONFIRMED_BY_PROVENANCE** | Numbers + method documented in `flutter-snapshot-and-code-recovery.md` (r2flutter, isolated build). Raw tool outputs live in a private local corpus (not committed), so counts are not re-derivable here — but the analyzed payload is byte-identical (libapp.so SHA-256 `e150ce501b87d3c0…` re-hashed this run from the split). Verdict: accept as provenance-backed; treat as address-map counts, not business-logic inventory. |
| 10 | Complementary APKs (supplier/driver) unavailable | **CONFIRMED** | No Cartona APKs other than the 4 audited files exist under `C:\Star\pol` (searched); supplier/driver apps remain publicly-documented only |

## 2. Metric-normalization table (Addendum F) — the three string corpora

| Metric | Count | Source | Counting rule | Evidence status |
|---|---|---|---|---|
| Arabic UI strings from Dart snapshot | 1,494 (of 1,966 UTF-16LE runs) | libapp.so string pool | printable UTF-16LE runs, run 2026-10-26 | CONFIRMED_BY_PROVENANCE (raw dump private; curated report committed) |
| Curated string corpus file | 1,653 lines; 1,615 unique; 38 duplicate occurrences | `58_…/data/arabic_ui_strings.txt` | line count; unique on stripped full line | CONFIRMED (recounted this run) |
| Android resource strings | 490 | decompiled `res/values/strings.xml` | count of `<string name=` elements | CONFIRMED (recounted this run) |

**Rule going forward:** any report in this run that cites a string count must name which of the three corpora it means. The historical "1,494 vs 1,652" confusion is resolved as two different extraction sources, not an error in either.

## 3. Quality assessment of prior runs

**Supported by raw evidence (strong):** APK identity, signing (Play App Signing, signer cert SHA-256 `83891e0a1243f16db19d3fd0b9e836148ce455f943d2a2808632565aa4d653ee`, SourceStamp present — re-verified via apksigner), asset hashing (113 distinct SHA-256s, all 64-hex, paths unique), per-endpoint provenance (source line + input hash + evidence ID), validator self-test (19/19 semantic + 6/6 negative fixtures, per `validation.json`).

**Inference-only (adequately labeled by the prior run):** all 21 screens (STATIC_INFERRED — no runtime capture was possible), endpoint functionality (STRING_ONLY), snapshot naming (no semantic names recovered).

**Internal consistency:** `validation.json` phase map and gates are mutually consistent; `RUNTIME_PARITY_VERIFIED: NOT CLAIMED` is correct and honest. The handoff's premise (retailer needs mock coverage; vendor most complete; no DRIVER role) is grounded in `pol-repository-reality-audit.md` file paths — spot-checked against the repo during exploration (`ir.pol.market` / `ir.pol.vendor` variants verified to exist; no DRIVER role found).

**Gaps found in prior work (for this run to improve):**
1. No committed analysis tooling (private scratch) — this run commits its scripts under `tools/`.
2. Fresh decompile skipped (Oct-5 tree reused with provenance) — acceptable, but this run re-verifies key facts directly from APK bytes.
3. The "113 archive entries" phrasing omits the 119 raw `assets/` ZIP entries and the 1,445 total entries — scope now documented above.
4. "70 endpoints" lacks a functional/literal split in summaries — now classified per-row.
5. Prior runtime blocker (ABI) was documented but no compatible-runtime alternatives were exhausted — CP3/CP2 address this (device-first + verified-compatibility emulator research).

## 4. Corrections carried into this run

- Every count in this run's reports names its counting rule and source corpus.
- Endpoint language: "API path literals (string-pool evidence)" unless runtime/call-site proof exists.
- Asset language: "113 curated inventory rows (103 declared)" with raw ZIP counts alongside where relevant.
- Screen statuses can only move upward (STATIC_INFERRED → STATIC_VERIFIED → OBSERVED) with artifact- or runtime-backed evidence.

**CP1 result: prior research is substantially sound; two framing corrections (endpoints, asset-entry scope) and one metric disentanglement (three string corpora) adopted.**
