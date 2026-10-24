# POL Vendor Android App — Full Audit & Pre-Mock Readiness
> **Historical audit (2026-09-29):** the login/authentication source contract was four-digit at that time. Current D-018 (revised 2026-10-25) and D-029 specify six numeric digits for login/registration and delivery verification respectively. Re-run affected flows before using this audit as current verification.

**Date:** 2026-09-29
**Repository:** `rrasi90/POL-2.3`
**Branch:** `feat/vendor-app-production-20260928-v2`
**Scope:** Vendor Android application only; native APK build intentionally excluded.

## 1. Audit conclusion

The Vendor application was audited against the active POL repository sources, Vendor API routes, application-boundary behavior, RBAC helpers, Master Tree / screen matrix, mobile parity records, branding assets, and the VPS deployment record.

The current implementation is suitable for the **Mock-Data Verification stage**, but it is not yet a certified Android release. The remaining release gates are executable verification (typecheck/QA), device visual/runtime verification, live HTTPS API verification, and only then native APK assembly.

## 2. Findings resolved in this audit

### A-01 — Canonical Vendor logo was referenced but missing from mobile bundle
**Severity:** P0 release correctness
**Resolution:** Added `mvp/apps/mobile/assets/vendor-logo.png` from the canonical repository asset.
**Proof:** mobile asset Git blob SHA equals canonical `d6b0bc5c4ea5aa66e0feb739bfc176589d89a182`; 581×570 RGBA PNG.
**Status:** RESOLVED.

### A-02 — Vendor Staff acceptance affordance conflicted with backend authorization
**Severity:** P0 RBAC
**Resolution:** Queue and Order Detail hide/block accept/reject/partial acceptance for `VENDOR_STAFF`; backend remains authoritative.
**Status:** RESOLVED.

### A-03 — Vendor Staff finance visibility exceeded the current role matrix
**Severity:** P0 RBAC / Finance
**Resolution:** Invoice and settlement list/detail boundaries now require `VENDOR_OWNER` for vendor tenants. HTTP regression tests were added for Vendor Staff denial.
**Status:** RESOLVED.

### A-04 — Active API contract text documented stale Vendor Staff acceptance authority
**Severity:** P1 contract drift
**Resolution:** `06_PRODUCT/API_Contracts.md` was reconciled to Owner-only acceptance/rejection/partial-acceptance authority.
**Status:** RESOLVED.

### A-05 — Vendor Screen matrix under-described V-14 and V-16
**Severity:** P1 traceability
**Resolution:** V-14 storefront and V-16 barcode/continuous-scan were added to mobile parity and screen-matrix coverage. Camera remains a device/runtime gate.
**Status:** RESOLVED.

### A-06 — Finance response-field mismatch could render valid data as “—”
**Severity:** P1 data mapping
**Finding:** invoices return `total_amount`; settlements return `net_vendor_amount_toman` rather than the prior mobile-only field names.
**Resolution:** Mobile finance cards now accept the canonical response keys.
**Status:** RESOLVED.

### A-07 — Persian/RTL baseline was incomplete
**Severity:** P1 usability / localization
**Resolution:**
- bundled Vazirmatn Regular/SemiBold/Bold;
- explicit RTL at the mobile shell and shared Screen layer;
- numeric/identifier inputs use LTR presentation;
- Persian/Arabic input digits are normalized to API-safe numeric values;
- amounts and quantities display with Persian digits;
- Vendor operational timestamps use `Asia/Tehran`;
- Persian calendar formatting is provided for Vendor-facing date/time output.
**Status:** IMPLEMENTED; visual/device proof still required.

### A-08 — Offline visibility was not consistently surfaced at app-shell level
**Severity:** P1 operational UX
**Resolution:** shared `OfflineBanner` is mounted by `AppShell`; rich offline synchronization remains intentionally out of scope.
**Status:** RESOLVED.

### A-09 — Storefront and barcode capability were only partially represented in Vendor Android
**Severity:** P1 capability coverage
**Resolution:** Vendor Android now exposes storefront read visibility, barcode lookup/match/candidate flow, continuous-scan submission and inventory publish workflow. Native camera/continuous physical capture remains device-gated.
**Status:** SOURCE-IMPLEMENTED / RUNTIME-GATED.

### A-10 — No isolated Mock transport existed for capability verification
**Severity:** P1 testability
**Resolution:** Added deterministic in-memory `mockTransport.ts`, connected through the same mobile API client, plus an executable Mock QA runner.
**Status:** IMPLEMENTED.

## 3. Mock coverage

The Mock transport currently exercises:
- OTP login and Vendor Owner / Vendor Staff role selection
- order queue, acceptance, rejection, preparation, ready and dispatch
- order items and timeline
- physical/reserved/sellable inventory
- inventory mutation
- owner-only pricing
- daily inventory confirmation and confirmation-with-changes
- invoices and settlements with Owner-only finance
- customers
- staff invite/status
- delegated permission view/grant/revoke
- Vendor storefront read
- barcode EXACT / HIGH_CONFIDENCE / AMBIGUOUS / NO_MATCH states
- candidate creation
- continuous scan + publish
- support cases + messages
- profile/context
- notifications/preferences
- current session
- health/readiness probes

The Mock layer is selected with `EXPO_PUBLIC_DATA_MODE=mock` and the Vendor release gate rejects Mock mode.

## 4. Persian / Iranian UX research applied

The implementation follows platform/localization guidance rather than simply mirroring an LTR layout:

- React Native treats layout direction as a first-class hierarchy property; RTL changes the meaning of start/end edges and child layout direction. Source: https://reactnative.dev/docs/flexbox
- Android localization guidance requires explicit handling of localized strings, numbers, currency and graphics, and recommends testing localized layouts on actual devices/emulators. Source: https://developer.android.com/guide/topics/resources/localization
- Android's localization testing guidance highlights RTL and bidirectional text issues as real UI failure modes. Source: https://developer.android.com/guide/topics/resources/pseudolocales
- Unicode CLDR provides locale-specific Persian number/date/time patterns. Source: https://unicode.org/cldr/charts/49/verify/dates/fa.html
- Vazirmatn documents the difference between Persian, Arabic and Latin digits and provides `ss01` for Persian digit substitution and `tnum` for tabular numbers. Source: https://github.com/rastikerdar/vazirmatn/blob/master/website/src/_docs/HELP-fa.md

Practical POL rules now used:
1. Persian copy is RTL.
2. Product/merchant identifiers, phone numbers, barcodes and ISO-like API dates are presented LTR.
3. Persian numeric display is used for user-facing counts and Toman values, while API payloads remain normalized.
4. Operational density stays D2 Balanced Operations.
5. Semantic theme tokens remain Light + Night.
6. Primary actions retain at least 44px touch targets through shared components.
7. Error/network states are explicit rather than silently falling back to fabricated data.

## 5. Known remaining gates

### R-01 — Native device camera
The barcode business contract is present, but actual Android camera permission, camera frame capture, scan detection and physical-device behavior still require device/runtime verification.

### R-02 — Screen-by-screen visual verification
The current source is RTL/theme-ready, but source inspection is not a substitute for screenshots on the target Android runtime.

### R-03 — Executable current-head verification
Fresh GitHub workflow attempts currently terminate before exposing executable steps; they are not treated as PASS evidence.

### R-04 — Live VPS endpoint
The recorded VPS is reachable and previously answered health/API endpoints, but the documented public endpoint is HTTP. A release APK requires a real HTTPS endpoint and current-branch live preflight.

### R-05 — Native build
`expo prebuild --clean --platform android` and Gradle `assembleRelease` remain intentionally unexecuted.

## 6. Required sequence from here

**Stage 1 — Mock QA**
Run the Vendor app with `EXPO_PUBLIC_DATA_MODE=mock`.
Exercise both Owner and Staff accounts, then deliberately test positive/negative role cases and all lifecycle/state branches.

**Stage 2 — Device QA**
Use a real Android runtime/emulator. Verify RTL, typography, truncation, numeric bidi behavior, dark/night theme, touch targets, keyboard behavior, scrolling, and barcode camera runtime.

**Stage 3 — Pre-APK gate**
Re-run typecheck, functional QA, regression QA, mock QA, Expo config, deterministic pre-APK gate and current CI.

**Stage 4 — APK**
Only after the previous gates are green and the live API endpoint is HTTPS.

**Stage 5 — VPS**
Set the exact live API endpoint, run `qa:live`, then perform authenticated smoke/e2e against the staging VPS. The APK is built against that validated endpoint, not the development fallback.

## 7. Release boundary

Current state:

**AUDITED / SOURCE-IMPLEMENTED → MOCK VERIFICATION → DEVICE VERIFICATION → PRE-APK → NATIVE APK → LIVE VPS**

No APK was built as part of this audit.
