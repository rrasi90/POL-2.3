# Flutter/Dart Static Analysis Report — CP6

**Payload identity (re-verified):** `libapp.so` from `config.armeabi_v7a.apk`, 10,945,116 B, SHA-256 `e150ce501b87d3c0ff8b45548b05be151733e839ea00a0b3947620cd0f8f3df2` — byte-identical to the payload the prior run analyzed.
**Tool:** `tools/dart_static_sweep.py` (independent regex sweep; rules in docstring; raw results `dart-static-sweep.json`).

## 1. Independent sweep results vs prior claims

| Metric (counting rule documented) | This run | Prior run | Assessment |
|---|---|---|---|
| Printable-ASCII runs ≥ 6 chars | **15,290** | 15,407 | Same order; boundary-rule differences (prior rule not fully published). Both are lower bounds. |
| UTF-16LE runs ≥ 4 units | **2,176** | 1,966 | Same; different run-length/alignment thresholds |
| Arabic-language UTF-16 runs | **1,642** | 1,494 | Same; threshold differences. Neither count equals the 1,653-line curated file (CP1 §2 — three distinct corpora) |
| Prior 70 endpoint path literals found **verbatim** | **70/70** | 70 recorded | Prior catalog independently CONFIRMED against raw bytes |
| Prior 24 navigation route literals found **verbatim** | **24/24** | 24 recorded | CONFIRMED |

**All sweep counts are string-pool evidence: presence ≠ runtime execution.**

## 2. New facts found this run (34 path literals absent from prior catalogs)

Highlights with design relevance (full list in `dart-static-sweep.json`):

- Auth/OTP: `/otp/verify`, `/otp/acquire2`, `/auth/`
- Cart/checkout: `/cart/checkout`, `/cart/detail2`, `/order/success`
- Onboarding: `/onboarding/new_user2`, `/onboarding/returning_user`, `/announcement/already-have-account`, `/announcement/create-account2`, `/announcement/new-app/switch2`
- Wallet/BNPL (credit): `/legacy/wallet/top-up`, `/installment2`, `/pay/authorize/`, `/tabs/payment-gateways`, `/tabs/installment-profile` — confirms a wallet/credit surface exists in Cartona that the prior 21-screen catalog did not carry as its own screen
- Supplier surfaces: `/supplier/products`, `/supplier/profile`, `/supplier-categories2`
- Campaigns: `/products/flash-offers`, `/eid-al-adha/scratch2`, `/home#offers_section2`, `/home#ramadan_products_section`
- Infra: `/analytics/track`, `/delivery/ack`, `/deep_linking/handler`, local DB name `/cartona_v0016.sqlite`

**Hygiene finding:** the snapshot embeds a developer-machine path `/home/ahmed/Documents/cartona-platform-flutter/.cursor/debug-79ba62.log` — a build-hygiene observation about Cartona's release pipeline; no credentials involved. Recorded as STATIC_VERIFIED trivia, not security advice.

## 3. Snapshot recovery claims (re-affirmed, CONFIRMED_BY_PROVENANCE)

Per CP1: 6,426 function entry addresses + 312 VM-internal classes, 0 app-level classes — tool outputs remain in the private local corpus; payload byte-identity re-verified this run. Dart 3.9.2 (`exact-hash`, r2flutter) accepted as authoritative. No Dart source, widget tree, or semantic function names recovered — no overclaim.

## 4. Reconciliation

`runtime-vs-static-reconciliation.csv` (21 rows, one per prior catalog screen):

- `static_reverified_20261027` = **CONFIRMED for 21/21** — every screen's route literal, endpoint strings, or (for `image_error_state`) the full Arabic error string verbatim in the payload.
- `runtime_observation` = NOT_RUN for all rows until CP4 produces evidence; `reconciliation_status` = PENDING_RUNTIME. Statuses upgrade only with runtime artifacts (screenshots/logs).

## 5. Implications for CP8 mapping

- The wallet/BNPL surface (`/legacy/wallet/top-up`, `/installment2`, `/pay/authorize/`, payment-gateways tab) strengthens the CP7/CP8 comparison against POL's invoice-only "finance" tab — POL has **no wallet/credit screen** (verified in repo exploration), so any adopt-pattern must be classified as REQUIRES_PRODUCT_DECISION, not VISUAL_ONLY.
- Onboarding distinguishes new vs returning users — a pattern candidate for POL's login flow.
- `/order/success` implies an explicit post-checkout success state; POL has a checkout success screen (RetailerMobileScreen) — compare treatments in CP8.
