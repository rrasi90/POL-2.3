# Executive Summary — Comprehensive Cartona Extraction (Run 2026-10-26)

**Extends** (does not replace) `runs/2026-10-26-cartona-revision-2-import-02/`. Revision-2 findings remain authoritative; this run deepens extraction and corrects two earlier limitations.

## What this run added

1. **Arabic UI corpus recovered — 1,494 strings.** Revision-2 recorded Arabic strings as absent; they are present in the Dart snapshot as two-byte (UTF-16LE) strings. Domain counts: order 236, supplier/merchant 93, offers 49, payment 47, delivery 44, search 39, wallet 32, cashback 28, branch 28, confirm 21, cancel 22, OTP 11, GMV-target 11, returns 5. Localization mechanism: Flutter `gen-l10n` (error string observed in snapshot).
2. **Product-state model exposed.** ~30 boolean state/feature keys: anti-fraud (`is_mocked`, `is_any_fake_gps_app_installed`, `is_any_app_cloner_installed`, `is_developer_mode_enabled`), credit/installment (`is_credit_exhausted`, `is_legacy_installment_activated/suspended`), supplier attributes (`has_fast_delivery`, `has_free_delivery_offer`, `has_integration`), account (`has_multiple_addresses`, `is_new_joiner`, `has_active_gmv_target`), registration form fields (`is_business_name_filled`, `is_business_type_selected`, ...).
3. **Cleartext-traffic finding corrected.** `usesCleartextTraffic=true` is overridden by `network_security_config.xml`: cleartext only for `10.0.2.2` (emulator loopback). Production is HTTPS-enforced.
4. **Full archive inventory.** Base: 6 DEX, 113 flutter-asset entries, 1,194 res entries, 82 META-INF; ABI split: 6 native libs; en/mdpi: resource-only (no AOT — verified).
5. **Typed Dart recovery attempted, honestly blocked.** Doldrums (Dart 2.10-only) installed and trialled on a working copy; rejected the snapshot: `Unsupported Dart SDK, snapshot hash: 97ff04a7...`. Blutter (matched SDK + C++ build) recorded as future option. REA bounded projections exhausted where supported (package_uris: 6 exact; class tokens: 2,000 of >=4,000 capped).
6. **Runtime UI capture blocked with exact error.** `POL_API_Emulator` (API 35, Google APIs, x86_64) started; `adb install-multiple` of the split set failed `INSTALL_FAILED_NO_MATCHING_ABIS` (armeabi-v7a-only libs, no ARM translation on Google APIs image). No image downloaded, no bypass. Prerequisites documented in `ui-ux-design-system.md`.
7. **Security finding (sanitized): a live Google API key (`AIzaSy...` pattern) is embedded in the Dart snapshot.** Value withheld from all committed artifacts. AppsFlyer identifiers likewise present (values withheld).

## Deliverables

19 files per `COMPREHENSIVE_CARTONA_EXTRACTION_PROMPT.md`, validated; raw corpus at `C:/Star/pol-2.4-private-analysis/cartona/e4a0f4d1.../` (outside Git). POL application code untouched.

## Status

Static extraction: PASS (bounded by snapshot tooling). Typed Dart recovery: BLOCKED. Runtime UI capture: BLOCKED (ABI; prerequisites documented). Per-file validation in `validation.json`.
