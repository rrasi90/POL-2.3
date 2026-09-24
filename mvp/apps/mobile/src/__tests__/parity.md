# Phase 3 Android parity matrix — functional, not pixel

The mobile implementation must preserve business capability, applicable screen/route semantics,
permissions, API semantics and platform-appropriate states. UI does not need to be pixel-identical.

| Family | Canonical IDs | Mobile implementation | APIs | Status |
|---|---|---|---|---|
| Shared/Auth | SH-AUTH-01/02, SH-PROFILE-01, SH-NOTIF-01/02 | src/screens/LoginScreen.tsx + AccountMobileScreen.tsx | auth OTP, profile/context, notifications, notification preferences | IMPLEMENTED |
| Retailer | R-02, R-03, R-06, R-07, R-08, R-10, R-11, R-12, R-16, R-17, R-18 | RetailerMobileScreen.tsx + OrderDetailMobileScreen.tsx + SupportMobileScreen.tsx | catalog/search, vendor search/storefront, basket/allocation/checkout, orders/detail/timeline, returns/disputes, support cases/messages, invoices | IMPLEMENTED |
| Vendor | V-01, V-02, V-03, V-06, V-07, V-08, V-10, V-17 | VendorMobileScreen.tsx + OrderDetailMobileScreen.tsx | order queue/actions, partial acceptance, items/timeline, inventory, daily inventory, referrals, settlements, invoices | IMPLEMENTED |
| Ops | O-01, O-02, O-06, O-10 | src/screens/OpsMobileScreen.tsx | exceptions dashboard, orders, reconciliation, audit logs | IMPLEMENTED (ADMIN_SUPER audit) |
| Field | F-01…F-05 | FieldTaskList/Detail/AssistedOrderScreen.tsx + OfflineBanner | field tasks, healthz | IMPLEMENTED |
| Barcode | R-03B / V-16 | no camera adapter yet | POST `/api/v1/products/match-barcode` is CONTRACT_ONLY in `mvp/MVP_API_MAP.md`; no runtime route is available | GAP / CONTRACT |
| Vendor Customers/Staff | V-09 / V-11 | no CRUD invented | no authoritative HTTP contract | GAP |
| Retailer order detail / returns / support | R-09…R-13 | order detail, return/dispute submission and support are implemented; remaining notifications/profile are shared | routes available per API map | IMPLEMENTED foundation |

## Mobile-wide rules

- No Driver App (D-023).
- D-028 barcode capability may use a camera adapter when the contract/runtime dependency is available; do not invent barcode matching semantics.
- F-05 MVP is request-failure state + healthz retry. No rich offline sync is claimed.
- Role is taken from backend membership context; client does not infer permissions.
- Checkout uses the Idempotency-Key header.
- Light/Night token sets exist centrally; profile/notifications/preferences are shared across authenticated roles; full screen-by-screen Night verification remains a QA task until visual evidence is recorded.
- At least three Phase-3 QA cycles are required before claiming final mobile DoD.

## QA evidence

- CI workflow: `.github/workflows/pol-mvp-mobile.yml`
- Required checks currently wired: mobile typecheck + Expo config validation + Android export.
- CI cycle 1 is evidenced by run `35884012647`. Functional/state-transition/parity QA cycle 2 is evidenced by run `35886815013` with **23/23 deterministic checks passing**; this remains contract/state coverage rather than device-level exploratory QA. Regression/cross-module QA cycle 3 is evidenced by run `35893284378` with **11/11 checks passing**, plus typecheck, Expo config validation and Android export. Visual Night verification remains a separate local gate.
- Status must remain IMPLEMENTED until the corresponding CI/evidence row is recorded.

## Local device notes (LOCAL-04, 2026-09-24, pre-remediation build)

Run against APK `com.anonymous.polmobile` on emulator-5554 (AVD `POL_API_Emulator`) at commit `e7e6464`, **before** the G-023…G-026 source remediation batch:

- Light theme PASS (`#F7F9FC` field list / assisted order / login).
- Night FAIL under system `uimode night yes` (G-025 at the time).
- Login requires E.164 `+989160007777`; raw `09160007777` rejected (G-026 at the time).
- Session survives app restart.
- F-01 empty state PASS; F-03 open PASS; back navigation PASS.
- F-03 initial `GET /catalog/search?limit=40` without `q` → 422 (G-023); `q=Alpha` → 200 but UI showed `—` for `canonical_name_fa`/`master_sku` (G-024).
- F-05 offline banner not observed under airplane mode without a failed fetch.

Screenshots: `artifacts/screenshots/local01_*`, `local04_*`. Full run detail: `mvp/LOCAL_EXECUTION_TRACKER.md`.

**Retest completed** on the post-remediation build (2026-09-24) — see section below.

## Local device retest (post-remediation, 2026-09-24)

Run against rebuilt debug APK `com.anonymous.polmobile` on emulator-5554 after source remediation G-023…G-026:

- Light theme PASS (Account toggle روشن; white center `#FFFFFF`).
- Night theme PASS (Account toggle شب; bg `#0F141C`) — G-025 closed on device.
- Login accepts local `09160007777` / `09160009999`; backend stores E.164 `+989160007777` / `+989160009999` — G-026 closed.
- FIELD_ACTIVATOR device login PASS; F-01 task list shows seeded `FIRST_ORDER_ASSIST` tasks.
- F-03 open PASS; back navigation PASS.
- F-03 empty search: client-side guard shows `عبارت جستجو الزامی است.` + empty state; **no 422 and no catalog request** — G-023 closed.
- F-03 `q=SKU-ALPHA-LIVE`: UI renders `Alpha Live Product` (+ SKU line), not `—` — G-024 closed.
- Session survives app restart.

Screenshots: `artifacts/screenshots/retest_*`. UI dumps: `artifacts/retest_ui_g023.xml`, `retest_ui_g024_result.xml`. Full run detail: `mvp/LOCAL_EXECUTION_TRACKER.md` §2 and §8.

Remote status for G-023…G-026: **SOURCE REMEDIATED / LOCAL RETEST PASS**.
