# POL — Local Execution & Verification Tracker

**Purpose:** This file is the handoff/control sheet for work that cannot be completed through the GitHub repository integration alone.  
**Rule:** When a local item is completed, tell the assistant **«انجام شد»** (or provide the result/log). The assistant will re-check the repository, CI evidence, and this tracker before closing the item.

**Repository:** `rrasi90/POL-2.3`  
**Branch:** `main`  
**Latest main HEAD:** `723f346402cf0fbb7ef9af3a0c46fa6e299d5cd2` (verified locally 2026-09-24)  
**Local verification baseline (pre-remediation device run):** `e7e6464730b7c1cec1ffbed2302da0b87e9e9f7e`  
**Code under remediation verification:** `62870503e36a6f2c95929862f839e8bd8258e894` (mobile CI 35987850765)

---

## 1. Current stage

### Stage 6 — Mobile QA Cycle 3
**STATUS: CLOSED / PASS**

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
**STATUS: LIGHT PASS / NIGHT FAIL (pre-remediation) — NIGHT RETEST REQUIRED (post-remediation)**

Evidence (local run 2026-09-24 on `e7e6464` build):
- Light: PASS — field list / assisted order / login bg `#F7F9FC`; screenshots `artifacts/screenshots/local01_light_*`, `local01_day_restored*`.
- Night: FAIL on that build — system `cmd uimode night yes` did not change app colors (`artifacts/screenshots/local01_night_system_mode*.png`). Pre-remediation `theme.ts` was effectively light-only in runtime styles and `app.json` had `userInterfaceStyle: "light"`.
- After source remediation (G-025): runtime Light/Night context + Account controls + `userInterfaceStyle: "automatic"`. **Full screen-by-screen Night visual gate still OPEN on the updated build** — CI does not replace device visual evidence.

Do not mark Night PASS merely because a Night palette exists.

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
**STATUS: PARTIAL PASS (2026-09-24, pre-remediation build) — RETEST REQUIRED (post-remediation)**

Environment: emulator-5554 (`POL_API_Emulator`), APK `com.anonymous.polmobile` via `expo prebuild` + `gradlew assembleDebug`, Metro `:8081` CI mode, adb reverse 8000/8081.

| Check | Result | Evidence |
|-------|--------|----------|
| Install / launch | PASS | adb install Success; `local01_boot_01*` |
| Login OTP `+989160007777` / `1234` | PASS | `local04_success*`; raw `09160007777` failed (G-026 at the time) |
| Session persists restart | PASS | force-stop + relaunch stays on field list |
| F-01 empty | PASS | `local01_light_field_list*` |
| F-03 open | PASS | `local04_f03_open*` |
| F-03 without `q` | FAIL (G-023 pre-fix) | 422 `Request validation failed.` |
| F-03 `q=Alpha` mapping | PARTIAL (G-024 pre-fix) | API 200; UI `—` for `canonical_name_fa`/`master_sku` |
| F-05 offline banner | NOT OBSERVED | airplane mode; banner only after failed healthz fetch |
| Back nav F-03 → list | PASS | `local04_back_list_final*` |

Post-remediation retest still required for G-023…G-026 (see §7).

---

## 3. Known unresolved repository gaps

These are **not automatically local bugs**. Do not invent implementations for them.

| ID | Status | Current rule |
|---|---|---|
| D-028 / barcode | GAP / CONTRACT | No runtime barcode adapter until authoritative HTTP/runtime contract exists |
| V-09 Vendor Customers | GAP | No invented CRUD |
| V-11 Vendor Staff | GAP | No invented permission CRUD |
| G-003 catalog path | documented conflict | Use REAL `/catalog/search`; do not force contract-only `/products/search` |
| G-004 inbox path | documented conflict | Use REAL `/notifications` |
| Refresh-token rotation policy | OPEN | Do not invent policy |
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
3. **LOCAL-01 Night** — screen-by-screen visual on **post-remediation** build (runtime theme + Account toggle).
4. **LOCAL-04 retest** — device smoke on **post-remediation** build (G-023…G-026).
5. Assistant re-checks evidence and reconciles repository documents.
6. Final global regression (local suite already **497/497** on pre-remediation tree — re-run after any source merge).
7. Final Delivery DoD audit.

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

LOCAL-01 Night and LOCAL-04 device smoke still require a fresh install/retest of the updated build; CI does not replace device visual evidence.

---

## 8. Local verification evidence — 2026-09-24 (pre-remediation baseline)

Recorded on `e7e6464` before applying stash → pull to `723f346`. Stash kept as backup: `local-verification-before-723f346`.

| Gate | Result | Artifact |
|------|--------|----------|
| Environment verify | PASS | `artifacts/verify_env_local3.json` |
| Full suite | **497/497 PASSED** 165.05s EXIT 0 | `artifacts/pol-test-results.json`, `artifacts/suite_final.log` |
| LOCAL-02 | PASS 16/16 | `artifacts/live_basket_checkout_e2e.{py,json}` |
| LOCAL-03 | PASS 12/12 | `artifacts/local03_idempotency_e2e.{py,json}` |
| LOCAL-01 | LIGHT PASS / NIGHT FAIL | `artifacts/screenshots/local01_*` |
| LOCAL-04 | PARTIAL PASS | `artifacts/screenshots/local04_*` |
| Mobile typecheck / expo config / expo export | EXIT 0 | local session logs |
| qa:functional / qa:regression | **not run on this baseline** (scripts absent at `e7e6464`; present on `723f346`) | — |

Environment (local Windows): Windows 11; Node v24.18.0 / npm 12.0.1; Python 3.11.15; Git 2.55; PostgreSQL 18.4 service `postgresql-x64-18` (`pol` + `pol_test` 95 tables); JAVA_HOME Android Studio JBR; Android SDK platform-tools 37.0.1, platforms 35+36, build-tools 35+36, NDK 27.1.12297006, emulator 37.1.11; AVD `POL_API_Emulator` (Pixel 6, API 35); API `:8000` via `artifacts/start_api.bat`.
