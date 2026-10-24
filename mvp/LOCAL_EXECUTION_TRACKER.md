# POL — Local Execution & Verification Tracker
> **Historical runtime tracker:** the dated test results in this file may include a four-digit OTP used by the then-current code. Current contract (2026-10-25): six digits for authentication/registration (D-018) and six digits for delivery (D-029). Re-run impacted checks on the final PR SHA; do not promote prior-SHA evidence.


**Purpose:** This file is the handoff/control sheet for work that cannot be completed through the GitHub repository integration alone.  
**Rule:** When a local item is completed, tell the assistant **«انجام شد»** (or provide the result/log). The assistant will re-check the repository, CI evidence, and this tracker before closing the item.

**Repository:** `rrasi90/POL-2.3`  
**Authoritative main HEAD:** `dbcfb9a974af53772a461db4e3f64afef70350e1`  
**Remediation branch:** `remediation/full-closure-2026-09-25`  
**Current remediation HEAD:** `54e5aab3061bd8ec898f06b1ac37d903f64e4b28`  
**Local verification baseline (pre-remediation device run):** `e7e6464730b7c1cec1ffbed2302da0b87e9e9f7e`
**Latest device evidence build referenced by this tracker:** `62870503e36a6f2c95929862f839e8bd8258e894` (mobile CI 35987850765)

---

## 1. Current stage

### Stage 6 — Mobile QA Cycle 3
**STATUS: HISTORICAL PASS / CURRENT REMEDIATION RE-CERTIFICATION PENDING**

Evidence:
- Mobile CI `35893284378` — SUCCESS
  - Typecheck
  - Functional QA **23/23**
  - Regression/Cross-module QA **11/11**
  - Expo config validation
  - Expo Android export
- Backend CI `35893284312` — SUCCESS
  - migration chain
  - bootstrap verification
  - full verification suite
  - machine-readable artifact

---

## 2. Local-only gates

These require a running local environment/device/emulator and therefore cannot be honestly marked PASS from repository inspection alone.

### LOCAL-01 — Night Theme Visual Verification
**STATUS: PASS (post-remediation retest 2026-09-24)**

Evidence (post-remediation build, emulator-5554, Account theme toggle):
- Light: PASS — `پوسته نمایش: روشن`, center RGB (255,255,255), avgBrightness 240.9 → `artifacts/screenshots/retest_local01_light.png`.
- Night: PASS — `پوسته نمایش: شب`, bg RGB (15,20,28)=`#0F141C`, avgBrightness 41.6 → `artifacts/screenshots/retest_local01_night.png`.
- Toggle path: حساب → تنظیمات → روشن/شب (`AccountMobileScreen.tsx`).
- G-025 verified on the same run (`retest_g025_account*.png`, `retest_g025_theme_screen.png`).

Pre-remediation baseline (`e7e6464`): Light PASS / Night FAIL under system `uimode night only` — superseded by this retest.

---

### LOCAL-02 — Live Basket → Allocation → Checkout → Order E2E
**STATUS: PASS 16/16 (2026-09-24)**

Canonical flow:
`Search → Product → Basket → Allocation Preview → Checkout → Order Group → Child Orders → Order Detail`

Evidence:
- `artifacts/live_basket_checkout_e2e.py` EXIT 0 → `artifacts/live_basket_checkout_e2e.json`
- Order group `f7650c36-e925-48cf-96bd-facaf905ec94`; child orders `SUBMITTED`; timeline events = 2
- Environment: API `:8000` healthz/readyz 200; PostgreSQL 18 `pol` 95 tables; Idempotency-Key UUIDv4; CanonicalCheckoutGateway not bypassed
- Local run note: vendor MOV seed adjusted (test data only) so allocation was reachable

---

### LOCAL-03 — Checkout Idempotency Replay
**STATUS: PASS 12/12 (2026-09-24)**

Evidence:
- `artifacts/local03_idempotency_e2e.py` EXIT 0 → `artifacts/local03_idempotency_e2e.json`
- First request 201 `idempotent_replay=false` → group `aff14467-0bf1-4c7d-85ed-6d58ca2590ef`
- Exact replay same key 201 same group `idempotent_replay=true`
- Same key + different payload → 422 `INVALID_REQUEST`
- DB `order_groups` rows for that key = **1**
- Canonical implementation authority: `scripts/checkout_gateway.py` (fingerprint persisted; API restarted after gateway change)

---

### LOCAL-04 — Device-level mobile smoke
**STATUS: PASS (post-remediation retest 2026-09-24)**

Environment: emulator-5554 (`POL_API_Emulator`), rebuilt debug APK `com.anonymous.polmobile` (`app-debug.apk` 135,989,353 bytes, installed post-remediation), Metro `:8081` (`--host lan`, workspace `mvp/apps/mobile`), adb reverse 8000/8081, API `:8000` with `POL_JWT_SECRET`.

| Check | Result | Evidence |
|-------|--------|----------|
| Install / launch | PASS | adb install + launch; `retest_00_boot.png`, `retest_boot2.png` |
| G-026 local phone → E.164 | PASS | typed `09160007777` → OTP stored `+989160007777\|VERIFIED`; `retest_g026_typed.png`, `retest_g026_after_send.png`, `retest_g026_logged_in.png` |
| Login OTP verify (retailer) | PASS | role `RETAILER_OWNER` on device; HTTP verify-otp `data.access_token` |
| FIELD_ACTIVATOR login | PASS | `+989160009999` / `1234` → field home; `retest_field_phone_typed.png`, `retest_field_logged_in.png`, `retest_field_home.png` |
| Session persists restart | PASS | force-stop + relaunch stays authenticated |
| LOCAL-01 / G-025 Night toggle | PASS | Account روشن/شب; `#0F141C` vs `#FFFFFF`; `retest_local01_night.png`, `retest_local01_light.png` |
| F-01 field task list | PASS | 2× `FIRST_ORDER_ASSIST` tasks; `retest_field_home.png` |
| F-03 open | PASS | `retest_g023_assisted_open.png` |
| G-023 F-03 empty `q` | PASS | client guard: error `عبارت جستجو الزامی است.` + empty state; **no 422, no `/catalog/search` call**; `retest_g023_empty_search.png`, `retest_ui_g023.xml` |
| G-024 F-03 name mapping | PASS | `q=SKU-ALPHA-LIVE` → UI `Alpha Live Product` + SKU (not `—`); `retest_g024_product.png`, `retest_ui_g024_result.xml` |
| Catalog HTTP (authed) | PASS | `GET /api/v1/catalog/search?q=SKU-ALPHA-LIVE` → 200 `canonical_name_fa=Alpha Live Product` |
| Back nav F-03 → list | PASS | بازگشت → field task list |
| F-05 offline banner | NOT OBSERVED | not required for this retest gate |

G-023…G-026 retest complete on the post-remediation build.

---

## 3. Known unresolved repository gaps

These are **not automatically local bugs**. Do not invent implementations for them.

| ID | Status | Current rule |
|---|---|---|
| D-028 / barcode | SOURCE IMPLEMENTED / CAMERA RUNTIME SCOPE | Canonical `/products/match-barcode` accepts legacy + extended payloads; device camera transport remains separate runtime scope |
| V-09 Vendor Customers | RESOLVED | Tenant-scoped canonical HTTP route + web UI implemented |
| V-11 Vendor Staff | RESOLVED | Tenant-scoped list/invite/update HTTP + web UI implemented |
| G-003 catalog path | RESOLVED / COMPATIBLE | `/catalog/search` is retailer runtime; `/products/search` remains registered for canonical compatibility |
| G-004 inbox path | RESOLVED | `/notifications` client projection and durable `/inbox/items*` routes coexist |
| Refresh-token rotation policy | SOURCE IMPLEMENTED / POLICY OPEN | Refresh token rotates and old-token replay fails; D-018 policy wording remains a governance decision |
| Invoice timing | OPEN | Existing default is invoice on ACCEPTED; confirm before finance E2E |
| OpenPencil WAVE-02 | BLOCKED_EXTERNAL | Requires local OpenPencil MCP on `:7600` |
| Real driver metrics | BLOCKED_EXTERNAL | No production metrics source supplied |
| SMS provider | BLOCKED_EXTERNAL | Live provider credentials absent |

---

## 4. Work already completed remotely

- Source-of-truth reconciliation.
- Repository audit.
- Backend verification.
- Mobile CI Cycle 1.
- Mobile functional/state-transition/parity Cycle 2.
- Supported mobile REAL-API parity expansion.
- Mobile Regression/Cross-module Cycle 3.
- Regression test defect correction.
- Documentation reconciliation through the current CI evidence.

Latest mobile Cycle 3 evidence:
- Run `35893284378`
- Functional QA **23/23**
- Regression QA **11/11**
- Expo config **PASS**
- Android export **PASS**

Latest backend evidence:
- Run `35893284312`
- Full verification **SUCCESS**

---

## 5. Execution order from here

1. ~~**LOCAL-02**~~ **DONE** — live basket → allocation → checkout → order E2E (16/16).
2. ~~**LOCAL-03**~~ **DONE** — checkout idempotency replay (12/12).
3. ~~**LOCAL-01 Night**~~ **DONE** — PASS on post-remediation build (runtime theme + Account toggle; see §2 LOCAL-01).
4. ~~**LOCAL-04 retest**~~ **DONE** — PASS on post-remediation build (G-023…G-026; see §2 LOCAL-04).
5. ~~Assistant re-checks evidence and reconciles repository documents.~~ **DONE** — evidence re-audited against current remediation branch.
6. Fresh global regression after remediation. Historical 497/497 remains baseline evidence; current GitHub CI is still failing before useful step execution.
7. Final Delivery DoD audit after fresh CI certification and remaining deployment/provider evidence.

**Important:** Completing a local item does not itself close the stage. The assistant must verify the reported evidence and update the authoritative project documents.

---

## 6. Handoff protocol

When a local task is finished, send:

`انجام شد LOCAL-01`

or, preferably:

`LOCAL-01 انجام شد — نتیجه: PASS — screenshots/log available`

For E2E:

`LOCAL-02 انجام شد — order_group_id: <id> — child_orders: <count>`

For idempotency:

`LOCAL-03 انجام شد — first=<result> replay=<result> duplicate_groups=<count>`

The assistant will then perform the repository-side verification and reconciliation.


---

## 7. Source remediation batch — 2026-09-24

Remote fixes applied for the locally reported findings:

- G-023: F-03 no longer calls catalog search without q.
- G-024: F-03 maps canonical_name_fa and master_sku.
- G-025: runtime Light/Night theme wiring added across the mobile style system, system-aware initialization added, and explicit Light/Night controls added to Account.
- G-026: supported Iranian local phone input is normalized to E.164 and backend OTP transport schemas now enforce E.164.

Verification evidence after source changes:
- Mobile CI run 35987850765 on commit 62870503e36a6f2c95929862f839e8bd8258e894 — SUCCESS.
- Functional/state-transition QA: 28/28.
- Regression/cross-module QA: 15/15.
- Typecheck, Expo config validation, and Android export: PASS.

LOCAL-01 Night and LOCAL-04 device smoke: **RETESTED PASS 2026-09-24** on the rebuilt APK (see §2). CI does not replace device visual evidence; device evidence is now recorded.

---

## 8. Post-remediation device retest — 2026-09-24

Build: debug APK rebuilt after stash→pull→reapply; Metro virtual-entry bundle verified (`toE164`, G-023 guard, ThemeProvider, accountButton present).

| Gate | Pre-remediation | Post-remediation retest | Key evidence |
|------|-----------------|-------------------------|--------------|
| LOCAL-01 Night | FAIL | **PASS** | `retest_local01_night.png` `#0F141C`; `retest_local01_light.png` `#FFFFFF` |
| G-023 empty F-03 search | FAIL (422) | **PASS** (client guard, no API call) | `retest_g023_empty_search.png`, `retest_ui_g023.xml` |
| G-024 name mapping | PARTIAL (`—`) | **PASS** (`Alpha Live Product`) | `retest_g024_product.png`, `retest_ui_g024_result.xml` |
| G-025 theme toggle | FAIL | **PASS** (Account روشن/شب) | `retest_g025_theme_screen.png`, `retest_local01_*` |
| G-026 local phone → E.164 | FAIL | **PASS** (`09160007777` → `+989160007777`) | `retest_g026_typed.png`, OTP row VERIFIED |

Environment notes for this run:
- API started with `POL_JWT_SECRET` (`artifacts/start_api_retest.bat` pattern); healthz/readyz 200.
- Catalog search requires bearer token (401 without); authed retailer/field OTP verify returns `data.access_token`.
- Metro monorepo: working bundle URL `/.expo/.virtual-metro-entry.bundle?platform=android&dev=true&minify=false`.
- Stash `stash@{0}: local-verification-before-723f346` retained as backup (never popped).

---

## 9. Local verification evidence — 2026-09-24 (pre-remediation baseline)

Recorded on `e7e6464` before applying stash → pull to `723f346`. Stash kept as backup: `local-verification-before-723f346`.

| Gate | Result | Artifact |
|------|--------|----------|
| Environment verify | PASS | `artifacts/verify_env_local3.json` |
| Historical full suite | **497/497 PASSED** 165.05s EXIT 0 | `artifacts/pol-test-results.json`, `artifacts/suite_final.log` (pre-remediation baseline evidence) |
| LOCAL-02 | PASS 16/16 | `artifacts/live_basket_checkout_e2e.{py,json}` |
| LOCAL-03 | PASS 12/12 | `artifacts/local03_idempotency_e2e.{py,json}` |
| LOCAL-01 | LIGHT PASS / NIGHT FAIL | `artifacts/screenshots/local01_*` |
| LOCAL-04 | PARTIAL PASS | `artifacts/screenshots/local04_*` |
| Mobile typecheck / expo config / expo export | EXIT 0 | local session logs |
| qa:functional / qa:regression | **not run on this baseline** (scripts absent at `e7e6464`; present on `723f346`) | — |

Environment (local Windows): Windows 11; Node v24.18.0 / npm 12.0.1; Python 3.11.15; Git 2.55; PostgreSQL 18.4 service `postgresql-x64-18` (`pol` + `pol_test` 95 tables); JAVA_HOME Android Studio JBR; Android SDK platform-tools 37.0.1, platforms 35+36, build-tools 35+36, NDK 27.1.12297006, emulator 37.1.11; AVD `POL_API_Emulator` (Pixel 6, API 35); API `:8000` via `artifacts/start_api.bat`.
