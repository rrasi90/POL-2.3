> **ARCHIVED HISTORICAL EVIDENCE — NOT CURRENT MAINLINE CERTIFICATION**
>
> Source branch: `test/journey-evidence-20261022` (PR #47, observed head `c700232c80cf78dd471ec5b8ca55fcad2b13c414`).
> This copy preserves the dated evidence as originally recorded. Individual evidence rows may refer to earlier SHAs (for example `d5c1096` or `c65c282`). None of these PASS/VERIFIED claims certifies current `main` or the integration branch. Re-run the referenced generator/tests on the exact target SHA before using these results for release decisions.
>
---
# POL — Bug Reproduction Log

Single register for every defect found during QA/verification. One row per defect, one ID per defect, no
duplicates: a bug that reappears gets a new row that links back to the original with `reopened-from`.

## Rules

- `BUG-ID` is permanent. Never renumber, never reuse.
- A row may only be closed with evidence a second person can replay: exact command, SHA, environment, result.
- Never paste secrets, OTPs, tokens, or customer data into this file. Reference the environment and redact.
- "Works for me" is not evidence. Screenshots alone are not evidence; they may accompany a command/log.
- A defect that is intentionally deferred is `DEFERRED` with an owner, a reason, and the TODO-ID that will close it.

## Status vocabulary

| Status | Meaning |
| --- | --- |
| `NEW` | Reported, not triaged |
| `TRIAGED` | Severity, owner, and environment confirmed |
| `IN_PROGRESS` | Fix being written; repro still valid on current SHA |
| `FIXED_PENDING_VERIFY` | Fix pushed; repro must be re-run on the fix SHA |
| `VERIFIED_CLOSED` | Repro fails on fix SHA and regression test exists |
| `DEFERRED` | Accepted risk with owner + closing TODO-ID |
| `DUPLICATE` | Points to the canonical `BUG-ID` |
| `WONT_FIX` | Product decision recorded in `DECISION_REGISTER.md` |

## Severity

`S1` data loss / security / money · `S2` blocked user journey · `S3` degraded but workable · `S4` cosmetic.

## Template

Copy this block per defect:

```markdown
### BUG-000 — <one-line symptom>

| Field | Value |
| --- | --- |
| Status | NEW |
| Severity | S2 |
| Role / persona | Retailer owner |
| Build / variant | retailer (ir.pol.market) · versionCode 100 |
| Branch / SHA | `agent/...` @ `<sha>` |
| Environment | local test · PostgreSQL 18.4 · Android 15 / API 35 emulator |
| Seed / data | `<fixture or seed command>` |
| Preconditions | <state the journey must be in> |
| Steps to reproduce | 1. … 2. … 3. … |
| Expected | <contract / acceptance criterion> |
| Actual | <observed, with request id / correlation id if available> |
| Evidence | command, log path, artifact path, screenshot path |
| Suspected cause | <file:line if known> |
| Linked TODO / BUG | `TODO-0xx` / `BUG-0yy` |
| Owner | <name or `unassigned`> |
| Fix SHA | |
| Regression test | `scripts/test_*.py::test_*` |
| Verified by / at | |
```

## Register

| BUG-ID | Severity | Status | Symptom | Role | SHA found | Linked TODO | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BUG-001 | S4 | `DEFERRED` | `test_photo_proof_requires_delivery_bound_media` used a fixed `storage_key='x'`, so the run failed on any second execution against the same test database — test isolation defect, not a product defect | QA harness | `afa46fc` | `TODO-016`, `TODO-090` | unassigned |
| BUG-002 | S2 | `FIXED` | Missing resources on order paths returned 422 `INVALID_REQUEST` instead of 404 `NOT_FOUND` | Retailer owner / vendor owner | `c65c282` | `TODO-014` | unassigned |
| BUG-003 | S2 | `FIXED` | Stale allocation plan at checkout returned 422 `INVALID_REQUEST`, contradicting the canonical 409 `CONFLICT` contract (G-326) | Retailer owner | `c65c282` | \TODO-014\ | unassigned |
| BUG-004 | S2 | `FIXED` | OTP failed-attempt counter was rolled back with the request transaction, so brute-force lockout never engaged over HTTP (unlimited 4-digit guesses) | All login personas | `c65c282` | `TODO-070` | unassigned |
| BUG-005 | S3 | `FIXED` | Revoking another user's session returned 401 `INVALID_ACCESS_TOKEN` (as if the caller's token were invalid) instead of 403 `FORBIDDEN` | Any authenticated user | `c65c282` | `TODO-070` | unassigned |
| BUG-006 | S4 | `FIXED` | `test_reservation_expiry_worker` asserted a global `expired_reservation_count == 1` while the worker sweeps every expired reservation, so it failed whenever other fixtures left expired rows behind (order-dependent, passed only in full-suite order) | QA harness | `1cf0cc4` | `TODO-090`, `TODO-073` | unassigned |
| BUG-007 | S3 | `FIXED` | Mobile API client issued `fetch` without any abort timeout, so a stalled connection could hang a screen indefinitely with no error, no offline banner and no way to retry | Retailer / vendor app users | `69fe074` | `TODO-074`, `TODO-088` | unassigned |
| BUG-008 | S3 | `FIXED` | `otp_code` pattern `^\d{4}$` accepted non-ASCII digits (Arabic-Indic, fullwidth), so an unusable code passed schema validation instead of returning 422 | All login personas | `c4aa4c8` | `TODO-134` | unassigned |
| BUG-009 | S2 | `FIXED` | `confirmation_date` was only regex-checked, so calendar-invalid dates (`2026-13-01`, `2026-02-30`) reached PostgreSQL and surfaced as a server error instead of 422 | Vendor owner/staff | `c4aa4c8` | `TODO-134` | unassigned |
| BUG-010 | S3 | `FIXED` | Free-text fields accepted control characters (`\x00`, `\x1b`), which can break PostgreSQL text inserts or corrupt logs | All personas | `c4aa4c8` | `TODO-134` | unassigned |
| BUG-011 | S3 | `FIXED` | Integer fields silently coerced booleans to 1 and accepted values beyond the 32-bit column range, producing unintended quantities or overflow errors | Retailer owner/staff, vendor owner/staff | `c4aa4c8` | `TODO-134` | unassigned |
| BUG-012 | S3 | `FIXED` | The Next.js app had no `error.tsx`, `global-error.tsx` or `not-found.tsx`; a render exception fell back to the framework default (English, no tracking id) and unknown routes rendered inside the login shell instead of a Persian not-found page | Retailer/vendor web users | `0b58574` | `TODO-087` | unassigned |
| BUG-013 | S3 | `FIXED` | `@pol/api-client` returned `payload.data` whenever `success` was not explicitly `false`, so a malformed 200 response (no envelope) was treated as success with `undefined` data instead of raising `PARSE_ERROR` | Web users on any screen | `0b58574` | `TODO-087` | unassigned |
| BUG-014 | S4 | `FIXED` | `MVP_API_MAP.md` documented `GET /orders/{order_id}/invoices` (server serves singular `/invoice`) and listed `/healthz`/`/readyz` under the `/api/v1` prefix although they are served at the root | API consumers, QA readers | `1f4bd39` | `TODO-135` | unassigned |
### BUG-002 — Order/order-group/delivery-exception lookups by unknown id answered 422 instead of 404

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S2 |
| Role / persona | Retailer owner, vendor owner, ops agent |
| Build / variant | API `/api/v1` · local runtime |
| Branch / SHA | `test/journey-evidence-20261022` @ `c65c282` (fixed in TODO-014 commit) |
| Environment | local test · PostgreSQL 18.4 · FastAPI TestClient vs `pol_test` |
| Seed / data | `scripts/test_http_delivery_pod_g440_451.py::_seed_dispatch` |
| Preconditions | Authenticated retailer session; random UUID that exists nowhere |
| Steps to reproduce | 1. `GET /api/v1/orders/<random-uuid>` 2. `GET /api/v1/orders/group/<random-uuid>` 3. `GET /api/v1/orders/delivery-exceptions/<random-uuid>` |
| Expected | 404 with `error.code = NOT_FOUND` (route contract; `KeyError` maps to 404) |
| Actual | 422 with `error.code = INVALID_REQUEST` — boundary raised `ValueError("... not found.")` and the mapper maps plain `ValueError` to 422 |
| Evidence | `scripts/test_http_negative_rbac_matrix.py` not-found regressions |
| Suspected cause | `scripts/application_boundary.py` used `ValueError` for three path-id lookups while 32 other lookups correctly use `KeyError` |
| Linked TODO / BUG | `TODO-014` |
| Owner | unassigned |
| Fix SHA | TODO-014 commit on `test/journey-evidence-20261022` |
| Regression test | `scripts/test_http_negative_rbac_matrix.py::TestNotFound` (three cases) |
| Verified by / at | full suite 685/685 PASS (221.78s) |

Residual (intentional, not a defect): payload-referenced ids (payment evidence media, assigned user, vendor) keep `ValueError` to 422 because the request body is invalid rather than the URL target missing.

### BUG-003 — Stale allocation plan at checkout returned 422 instead of the documented 409 CONFLICT

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S2 |
| Role / persona | Retailer owner |
| Build / variant | API `/api/v1` · local runtime |
| Branch / SHA | `test/journey-evidence-20261022` @ `c65c282` (fixed in TODO-014 commit) |
| Environment | local test · PostgreSQL 18.4 · FastAPI TestClient vs `pol_test` |
| Seed / data | allocated basket + confirmed plan via `_seed_dispatch`, then `UPDATE baskets SET version = version + 1` |
| Preconditions | Confirmed allocation plan whose `basket_version` no longer matches `baskets.version` |
| Steps to reproduce | 1. Seed allocation plan 2. bump `baskets.version` 3. `POST /api/v1/orders` with that `allocation_plan_id` |
| Expected | 409 with `error.code = CONFLICT` (G-326 canonical stale/competing-state contract) |
| Actual | 422 with `error.code = INVALID_REQUEST` |
| Evidence | `scripts/test_http_negative_rbac_matrix.py::TestInvalidTransitionsAndPayloads::test_stale_allocation_plan_checkout_is_409` |
| Suspected cause | `scripts/operational_policies.py:215` raised `AllocationIntegrityError` (a `ValueError`) before `scripts/revalidation_checkout.py` could raise its `ConflictError("STALE_BASKET_VERSION: ...")`, making the 409 path unreachable over HTTP |
| Linked TODO / BUG | `TODO-014` · reconciles G-326 (`RESOLVED` in `MVP_KNOWN_GAPS.md`) with runtime |
| Owner | unassigned |
| Fix SHA | TODO-014 commit on `test/journey-evidence-20261022` |
| Regression test | `test_stale_allocation_plan_checkout_is_409`, `scripts/test_operational_policies.py::test_stale_plan_version_rejected` (now expects `ConflictError`) |
| Verified by / at | full suite 685/685 PASS (221.78s) |

### Not a defect — DB session `expires_at` is not enforced on the access-token path

`scripts/auth_boundary.py::validate_access_token` rejects unknown, revoked and EXPIRED sessions but does not compare `user_sessions.expires_at`; access-token lifetime is bounded by the JWT `exp` claim, and `AuthService.refresh_access_token` enforces both `status == 'EXPIRED'` and `expires_at <= now`. Verified by `test_expired_status_session_is_401` (EXPIRED row returns 401). Documented as design, not filed as a defect.

### BUG-004 — OTP brute-force lockout was ineffective over HTTP

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S2 |
| Role / persona | All login personas (retailer, vendor, ops, field) |
| Build / variant | API `/api/v1` · local runtime |
| Branch / SHA | `test/journey-evidence-20261022` @ `c65c282` (fixed in TODO-070 commit) |
| Environment | local test · PostgreSQL 18.4 · FastAPI TestClient vs `pol_test` |
| Seed / data | `scripts/test_http_transport.py::_seed_user` (unique phone per test) |
| Preconditions | A pending LOGIN OTP challenge for the victim phone |
| Steps to reproduce | 1. `POST /auth/request-otp` 2. call `POST /auth/verify-otp` with a wrong code up to ten times 3. inspect `otp_challenges.attempts_count` |
| Expected | Each wrong code increments `attempts_count`; the 5th returns 429 `OTP_LOCKED` and sets `status = BLOCKED`, blocking further guesses |
| Actual | Every attempt returned 422 with `Attempt 1/5`; `attempts_count` stayed `0` and no lockout ever occurred |
| Evidence | `scripts/test_http_auth_matrix.py::TestOtpFailures::test_wrong_otp_persists_attempt_counter`, `..._test_fifth_wrong_otp_locks_the_phone` |
| Suspected cause | `scripts/api/db.py::get_db_cursor` rolls back on any exception, so the `UPDATE otp_challenges SET attempts_count = ... ` executed inside `domain_services.AuthService.verify_otp` was discarded when `InvalidOTPError` propagated to the error handler. Boundary-level tests passed because they inspect the row inside the same open transaction |
| Linked TODO / BUG | `TODO-070` |
| Owner | unassigned |
| Fix SHA | TODO-070 commit on `test/journey-evidence-20261022` |
| Regression test | `scripts/test_http_auth_matrix.py::TestOtpFailures` (counter persistence, 429 lockout, request-otp during lockout) |
| Verified by / at | full suite 695/695 PASS (227.7s) |

Fix: `scripts/api/routes/auth.py::verify_otp` commits the failed-attempt accounting (`cur.connection.commit()`) before re-raising `InvalidOTPError` / `OTPLockoutError`. Successful-path handlers are unchanged.

### BUG-005 — Revoking another user's session answered 401 instead of 403

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S3 |
| Role / persona | Any authenticated user |
| Build / variant | API `/api/v1` · local runtime |
| Branch / SHA | `test/journey-evidence-20261022` @ `c65c282` (fixed in TODO-070 commit) |
| Environment | local test · PostgreSQL 18.4 · FastAPI TestClient vs `pol_test` |
| Seed / data | two users seeded via `_seed_user`, one session each |
| Preconditions | User A holds a valid access token; user B has an active session |
| Steps to reproduce | 1. login A and B 2. `DELETE /auth/sessions/{session_of_B}` with A's bearer token |
| Expected | 403 `FORBIDDEN` — the caller's token is valid, the target session is not theirs |
| Actual | 401 `INVALID_ACCESS_TOKEN`, which told clients (and the SPA 401 interceptor) to discard a perfectly valid session |
| Evidence | `scripts/test_http_auth_matrix.py::TestSessionLifecycle::test_cannot_revoke_another_users_session` |
| Suspected cause | `scripts/auth_application.py::revoke_session` raised `AuthError` for an ownership violation, and `AuthError` maps to 401 |
| Linked TODO / BUG | `TODO-070` |
| Owner | unassigned |
| Fix SHA | TODO-070 commit on `test/journey-evidence-20261022` |
| Regression test | `...::test_cannot_revoke_another_users_session` (also asserts victim session still works) |
| Verified by / at | full suite 695/695 PASS (227.7s) |

### BUG-006 — Reservation-expiry regression test was order-dependent and asserted a global sweep count

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S4 |
| Role / persona | QA harness |
| Build / variant | Backend verification suite · PostgreSQL 18.4 |
| Branch / SHA | `test/journey-evidence-20261022` @ `1cf0cc4` |
| Environment | local test · `pol_test` |
| Seed / data | one vendor product with `reserved_quantity=20` and one `ACTIVE` reservation expired 1 minute ago |
| Preconditions | Another module (for example `test_e2e_mvp_platform`) already left expired `ACTIVE` reservations in the shared test database |
| Steps to reproduce | 1. Run `pytest scripts/test_e2e_mvp_platform.py scripts/test_reservation_expiry_worker.py` 2. Observe the worker processed 10 rows, not 1 |
| Expected | The test asserts this reservation's own effect and stays green in any order or repetition |
| Actual | `assert result["expired_reservation_count"] == 1` failed with `10 == 1` because `limit=10` swept other rows; the module also hardcoded `dbname/pol_test`, `user/postgres`, `host/127.0.0.1` instead of reading the environment |
| Evidence | `136 passed in 96.13s` for the G3 batch after the fix; `1 passed` alone, `36 passed` combined with `test_e2e_mvp_platform.py` |
| Suspected cause | Global-count assertion against a shared database plus missing isolation of pre-existing expired rows |
| Linked TODO / BUG | `TODO-090`, `TODO-073` |
| Owner | unassigned |
| Fix SHA | commit `test: isolate reservation expiry assertion and add destructive-db guards` |
| Regression test | `scripts/test_reservation_expiry_worker.py::test_reservation_expiry_releases_inventory_and_is_idempotent` |
| Verified by / at | 2026-10-23, three orderings (alone / with E2E module / full G3 batch) all green |

### BUG-007 — Mobile API client had no request timeout, so stalled connections never surfaced an error

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S3 |
| Role / persona | Retailer owner/staff, vendor owner/staff |
| Build / variant | Expo mobile, both variants (`ir.pol.market`, `ir.pol.vendor`) |
| Branch / SHA | `test/journey-evidence-20261022` @ `69fe074` |
| Environment | source-level review + `qa:regression` / `qa:pre-apk` gates (device run pending, see TODO-093) |
| Seed / data | n/a |
| Preconditions | Live data mode; server or network accepts the TCP connection but never answers (or answers after minutes) |
| Steps to reproduce | 1. Set `EXPO_PUBLIC_DATA_MODE=live` 2. Put a black-hole endpoint behind `EXPO_PUBLIC_API_BASE_URL` 3. Open any screen that loads data |
| Expected | Request fails within a bounded time with a `NETWORK` error, offline banner appears, user can retry |
| Actual | `fetch` had no timeout or `AbortController`, so the promise never settled; the screen stayed in its loading state forever |
| Evidence | `mvp/apps/mobile/src/api.ts` now wraps every live request in `AbortController` (`REQUEST_TIMEOUT_MS=20000`, `HEALTH_TIMEOUT_MS=5000`), clears the timer in `finally`, maps `AbortError` to `ApiError("NETWORK", ...)`; `qa:regression` 26/26 and `qa:pre-apk` PASS for both variants |
| Suspected cause | The client relied on the platform default (no timeout) |
| Linked TODO / BUG | `TODO-074`, `TODO-088` |
| Owner | unassigned |
| Fix SHA | commit `fix(mobile): bound live API requests with an abort timeout` |
| Regression test | `scripts/mobile_regression_qa.mjs` — "API client bounds every live request with an abort timeout" |
| Verified by / at | 2026-10-23 · typecheck exit 0 · qa:regression 26/26 · qa:pre-apk retailer PASS, vendor PASS |

### BUG-008 — OTP pattern accepted non-ASCII digits

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S3 |
| Role / persona | All login personas |
| Branch / SHA | `test/journey-evidence-20261022` @ `c4aa4c8` |
| Preconditions | Any OTP verify request |
| Steps to reproduce | 1. `POST /api/v1/auth/verify-otp` with `otp_code="١٢٣٤"` (Arabic-Indic) or fullwidth digits |
| Expected | 422 `VALIDATION_ERROR` — OTP codes are ASCII digits |
| Actual | Schema accepted the value because Python `\d` matches Unicode digits; the service then compared a code that can never match |
| Evidence | `scripts/test_schema_fuzz_boundaries.py::TestOtpInputBoundaries` (schema + HTTP 422) |
| Linked TODO / BUG | `TODO-134`, `TODO-070` |
| Fix SHA | commit `harden(schemas): enforce ASCII digits, calendar dates, control-char and integer bounds` |
| Regression test | `TestOtpInputBoundaries::test_unicode_otp_is_rejected_over_http` |
| Verified by / at | 2026-10-23 · full suite 789/789 PASS |

### BUG-009 — Calendar-invalid `confirmation_date` reached the database

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S2 |
| Role / persona | Vendor owner/staff (daily inventory confirmation) |
| Branch / SHA | `test/journey-evidence-20261022` @ `c4aa4c8` |
| Steps to reproduce | 1. `GET /api/v1/vendor/inventory/daily?confirmation_date=2026-13-01` (or the confirm POST) |
| Expected | 422 `VALIDATION_ERROR` for an impossible date |
| Actual | The regex `^\d{4}-\d{2}-\d{2}$` accepted it; PostgreSQL raised `date/time field value out of range` and the request failed as a server error |
| Evidence | `scripts/test_schema_fuzz_boundaries.py::TestCollectionAndPaginationBoundaries::test_date_format_is_strict_ascii` |
| Linked TODO / BUG | `TODO-134` |
| Fix SHA | commit `harden(schemas): enforce ASCII digits, calendar dates, control-char and integer bounds` |
| Regression test | `TestCollectionAndPaginationBoundaries::test_date_format_is_strict_ascii` |
| Verified by / at | 2026-10-23 · full suite 789/789 PASS |

### BUG-010 — Control characters accepted in free-text fields

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S3 |
| Role / persona | All personas submitting text (address, reasons, notes) |
| Branch / SHA | `test/journey-evidence-20261022` @ `c4aa4c8` |
| Steps to reproduce | 1. `POST /api/v1/orders/.../checkout` with `delivery_address` containing `\x00` |
| Expected | 422 `VALIDATION_ERROR` |
| Actual | The value passed validation; PostgreSQL rejects NUL bytes, producing a server error, and other control characters can corrupt logs |
| Evidence | `scripts/test_schema_fuzz_boundaries.py::TestTextBoundaries::test_control_characters_are_rejected` |
| Linked TODO / BUG | `TODO-134` |
| Fix SHA | commit `harden(schemas): enforce ASCII digits, calendar dates, control-char and integer bounds` |
| Regression test | `TestTextBoundaries::test_control_characters_are_rejected` |
| Verified by / at | 2026-10-23 · full suite 789/789 PASS |

### BUG-011 — Booleans and int32 overflow accepted in integer fields

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S3 |
| Role / persona | Retailer owner/staff, vendor owner/staff |
| Branch / SHA | `test/journey-evidence-20261022` @ `c4aa4c8` |
| Steps to reproduce | 1. `POST /api/v1/baskets/current/items` with `requested_quantity=true` 2. Repeat with `2147483648` |
| Expected | 422 for a boolean and for a value outside the 32-bit column range |
| Actual | Pydantic coerced `true` to `1` and accepted the overflow value, deferring failure to the database |
| Evidence | `scripts/test_schema_fuzz_boundaries.py::TestNumericBoundaries` |
| Linked TODO / BUG | `TODO-134` |
| Fix SHA | commit `harden(schemas): enforce ASCII digits, calendar dates, control-char and integer bounds` |
| Regression test | `TestNumericBoundaries::test_boolean_quantity_is_rejected` and `test_int4_overflow_quantity_is_rejected` |
| Verified by / at | 2026-10-23 · full suite 789/789 PASS |

### BUG-012 — No app-level error boundary or not-found page

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S3 |
| Role / persona | Retailer/vendor web users |
| Build / variant | `@pol/web` (Next.js App Router) |
| Branch / SHA | `test/journey-evidence-20261022` @ `0b58574` |
| Environment | local test · `next dev` on 3000 · API on 8001 · Playwright chromium |
| Steps to reproduce | 1. Open a route that does not exist under `/auth/…` 2. Force a render exception inside a route segment |
| Expected | Persian, branded error/not-found surface with a tracking id, a way back home, and no sensitive detail (TODO-087) |
| Actual | Unknown routes were rewritten by middleware into the login shell (HTTP 200) and render failures fell back to the framework default error overlay with no user-facing Persian message or tracking id. There was also no app-level boundary at all — the files were absent. |
| Evidence | Before fix: `tests/resilience.spec.ts` not-found case failed with `Expected: 404, Received: 200`; after fix: 5/5 resilience cases pass, full browser suite 23 passed (33.9s) |
| Suspected cause | `mvp/apps/web/src/app/` had no `error.tsx`, `global-error.tsx`, `not-found.tsx`; middleware rewrites every unauthenticated path to `/auth/login` |
| Linked TODO / BUG | `TODO-087` |
| Owner | unassigned |
| Fix SHA | commit `fix(web): error boundaries, not-found page and correlation-aware client` |
| Regression test | `mvp/apps/web/tests/resilience.spec.ts` (not-found + 500 + invalid JSON + dropped connection + invalid envelope) |
| Verified by / at | 2026-10-23 · `npx playwright test` 23 passed; `next build` exit 0; `tsc --noEmit` exit 0; `eslint` 0 errors |

### BUG-013 — Missing success envelope treated as success

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S3 |
| Role / persona | Web users on any screen using `@pol/api-client` |
| Build / variant | `@pol/api-client` 0.1.0 · web app |
| Branch / SHA | `test/journey-evidence-20261022` @ `0b58574` |
| Environment | local test · Playwright chromium |
| Steps to reproduce | 1. Stub `POST /api/v1/auth/request-otp` to answer `200` with `{"foo":"bar"}` 2. Submit the login form |
| Expected | A visible error and no navigation (`PARSE_ERROR`), never a success path with `undefined` data |
| Actual | `request()` only threw when `payload.success === false`; any other shape fell through to `return payload.data`, so screens could proceed on `undefined` (the login screen only failed later by accident) |
| Evidence | `tests/resilience.spec.ts` → “a 200 response without the success envelope is rejected, not treated as data” |
| Suspected cause | `mvp/packages/api-client/src/index.ts` checked `success === false` but not `success !== true` |
| Linked TODO / BUG | `TODO-087` |
| Owner | unassigned |
| Fix SHA | commit `fix(web): error boundaries, not-found page and correlation-aware client` |
| Regression test | `mvp/apps/web/tests/resilience.spec.ts` (invalid-envelope case) |
| Verified by / at | 2026-10-23 · browser suite 23 passed; `@pol/api-client` typecheck exit 0 |

### BUG-014 — MVP_API_MAP drift against the live OpenAPI document

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S4 |
| Role / persona | API consumers and QA reading the contract map |
| Branch / SHA | `test/journey-evidence-20261022` @ `1f4bd39` |
| Environment | local test · `app.openapi()` on the current tree |
| Steps to reproduce | 1. Parse `MVP_API_MAP.md` rows into `(method, path)` 2. Compare with `app.openapi()["paths"]` |
| Expected | Every documented route/method exists; the map's stated prefix rule holds or documents exceptions |
| Actual | `GET /api/v1/orders/{order_id}/invoices` had no matching operation (actual route is `/orders/{order_id}/invoice`); `/healthz` and `/readyz` were listed under “prefix all with `/api/v1`” but are mounted at the root |
| Evidence | `scripts/test_api_contract_drift.py::test_api_map_rows_exist_in_openapi` failed with those four rows before the map edit and passes after |
| Suspected cause | The map was written before the invoice route was renamed to the singular form and kept the OPS transport in the same prefixed table |
| Linked TODO / BUG | `TODO-135` |
| Owner | unassigned |
| Fix SHA | commit `test(api): guard OpenAPI, API-map and client contract drift` |
| Regression test | `scripts/test_api_contract_drift.py` (map/method parity + client call-site parity) |
| Verified by / at | 2026-10-23 · `pytest scripts/test_api_contract_drift.py` 3 passed |

### BUG-015 — Free-string enums surface as 500 from database CHECK constraints

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S3 |
| Role / persona | retailer (support cases), admin (field tasks), admin (broadcasts), any user (notification preferences) |
| Branch / SHA | `test/journey-evidence-20261022` @ `a05b0d3` |
| Environment | local test · `ENVIRONMENT=test` · `pol_test` |
| Steps to reproduce | 1. `POST /api/v1/support/cases` with `{"case_type":"BOGUS","subject":"x"}` 2. `POST /api/v1/field/tasks` with `{"task_type":"BOGUS", …}` 3. `POST /api/v1/admin/broadcasts` with `{"channel":"BOGUS", …}` 4. `PUT /api/v1/notifications/preferences` with `{"channel":"BOGUS", …}` |
| Expected | 422 `VALIDATION_ERROR` naming the field, no row written |
| Actual | Request passed schema validation, hit the PostgreSQL CHECK constraint and returned 500 with a driver-level error (support case / field task / broadcast / preferences) |
| Evidence | `scripts/test_owasp_api_top10.py::test_invalid_enum_or_reference_is_422_not_500` (8 parameterised cases) — all 422 after the fix |
| Suspected cause | `SupportCaseCreateRequest.case_type/priority`, `SupportCaseTransitionRequest.target_status`, `FieldTaskCreateRequest.task_type`, `DeliveryExceptionReportRequest.exception_type`, `DeliveryExceptionResolveRequest.resolution_type`, `BroadcastCreateRequest.channel/priority`, `NotificationPreferenceUpdateRequest.channel` and `ReturnItemRequest.reason_code` were typed `str` while the database enforced enumerations |
| Linked TODO / BUG | `TODO-131` |
| Owner | unassigned |
| Fix SHA | commit `fix(api): validate enum and reference fields, map integrity errors to 422` |
| Regression test | `scripts/test_owasp_api_top10.py` (invalid enum/reference matrix) + `scripts/test_schema_fuzz_boundaries.py` |
| Verified by / at | 2026-10-23 · `pytest scripts/test_owasp_api_top10.py` 20 passed |

### BUG-016 — Malformed UUID references and dangling foreign keys return 500

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S3 |
| Role / persona | retailer (support cases, delivery exceptions), admin (field tasks), vendor (catalog product linking) |
| Branch / SHA | `test/journey-evidence-20261022` @ `a05b0d3` |
| Environment | local test · `ENVIRONMENT=test` · `pol_test` |
| Steps to reproduce | 1. `POST /api/v1/support/cases` with `related_order_id: "not-a-uuid"` 2. `POST /api/v1/field/tasks` with `assigned_to_user_id: "not-a-uuid"` 3. `POST /api/v1/catalog/vendors/products` with a well-formed but nonexistent `product_id` |
| Expected | 422 with a generic “reference does not exist or is not allowed” message; no database detail leaked |
| Actual | psycopg2 `InvalidTextRepresentation` / `ForeignKeyViolation` propagated to the generic 500 handler |
| Evidence | `scripts/test_owasp_api_top10.py::test_invalid_enum_or_reference_is_422_not_500` — the dangling-`product_id` case now returns `INVALID_REQUEST` from `data_integrity_handler` |
| Suspected cause | FK-bearing fields were `str` without UUID parsing, and no exception handler mapped database integrity errors to the API error contract |
| Linked TODO / BUG | `TODO-131` |
| Owner | unassigned |
| Fix SHA | commit `fix(api): validate enum and reference fields, map integrity errors to 422` |
| Regression test | `scripts/test_owasp_api_top10.py` (UUID/FK matrix) |
| Verified by / at | 2026-10-23 · `pytest scripts/test_owasp_api_top10.py` 20 passed; full suite 857 passed |

### BUG-017 — Provider adapter reported an unverifiable 2xx as delivered

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S3 |
| Role / persona | all users depending on OTP/transactional SMS |
| Branch / SHA | `test/journey-evidence-20261022` @ `a05b0d3` |
| Environment | local test · adapter unit contract |
| Steps to reproduce | Call a provider adapter with a stub transport answering `200` and a body without any message identifier (e.g. `{}` or `[]`) |
| Expected | `ProviderTransientError` — the send cannot be confirmed, so it must be retried, never recorded as delivered |
| Actual | `send` returned a success payload with `message_id=None`, so callers could persist a delivery that the provider never acknowledged |
| Evidence | `scripts/test_provider_adapter_contract.py::test_unverifiable_2xx_is_not_reported_as_success` and the array-body case |
| Suspected cause | The 2xx branch extracted an id from a dict body but fell through to `None` instead of raising |
| Linked TODO / BUG | `TODO-133` |
| Owner | unassigned |
| Fix SHA | commit `fix(api): fail closed on unverifiable provider responses` |
| Regression test | `scripts/test_provider_adapter_contract.py` (10 tests) |
| Verified by / at | 2026-10-23 · `pytest scripts/test_provider_adapter_contract.py` 10 passed |

### BUG-018 — Unbounded request bodies and bulk arrays could exhaust the API

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S3 |
| Role / persona | any authenticated caller (retailer, vendor, admin) |
| Branch / SHA | `test/journey-evidence-20261022` @ `c874459` |
| Environment | local test · `ENVIRONMENT=test` · `pol_test` |
| Steps to reproduce | 1. `POST /api/v1/auth/request-otp` with a body larger than 1 MiB 2. `POST /api/v1/orders/{id}/disputes` with an `items` array of 100k rows |
| Expected | 413 `PAYLOAD_TOO_LARGE` for the oversized body and 422 for an over-cap array, before any database work |
| Actual | Request bodies had no size cap and four bulk arrays (`items`/`changes`) had no `max_length`, so a single caller could force unbounded parsing and row loops |
| Evidence | `scripts/test_resource_limits.py::test_oversized_json_body_is_413_with_envelope`, `test_chunked_body_without_content_length_is_still_bounded`, `test_oversized_dispute_item_list_is_rejected` |
| Suspected cause | No body-limit middleware and no shared array cap; uploads correctly bypass the API via presigned storage, but JSON bodies were never measured |
| Linked TODO / BUG | `TODO-132` |
| Owner | unassigned |
| Fix SHA | commit `fix(api): bound request bodies, bulk arrays and document resource limits` |
| Regression test | `scripts/test_resource_limits.py` (21 tests) + `mvp/RESOURCE_LIMITS.md` |
| Verified by / at | 2026-10-23 · full suite 878 passed |

### BUG-019 — `?next=` deep link was dropped and ADMIN_SUPER landed on /ops

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S4 |
| Role / persona | every role returning to a deep link; admin super |
| Branch / SHA | `test/journey-evidence-20261022` @ `9f53af2` |
| Environment | local test · Playwright chromium |
| Steps to reproduce | 1. Open `/retailer/orders` while logged out → middleware redirects to `/auth/login?next=%2Fretailer%2Forders` 2. Complete OTP login 3. Log in as `ADMIN_SUPER` |
| Expected | After login the user lands on the page they asked for (when their role may open it); `ADMIN_SUPER` lands on `/admin` |
| Actual | Login ignored `next` and always used a hardcoded role map that sent `ADMIN_SUPER` to `/ops`; the `next` parameter was dead code |
| Evidence | `tests/navigation-states.spec.ts` (deep-link restore + role fallback) and `tests/login.spec.ts` ("post-login destination" 4 tests) |
| Suspected cause | `middleware.ts` wrote `next` but the login page navigated from an inline ternary map instead of a shared, validated resolver |
| Linked TODO / BUG | `TODO-079` |
| Owner | unassigned |
| Fix SHA | commit `fix(web): restore deep links and survive reload without re-login` |
| Regression test | `mvp/apps/web/tests/login.spec.ts` + `navigation-states.spec.ts` |
| Verified by / at | 2026-10-23 · browser suite 44 passed |

### BUG-020 — API client never sent or stored the refresh cookie

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S2 (session lost on reload after the 15-minute access token) |
| Role / persona | all web users |
| Branch / SHA | `test/journey-evidence-20261022` @ `9f53af2` |
| Environment | local test · web on `127.0.0.1:3000`, API on `127.0.0.1:8001` |
| Steps to reproduce | 1. Log in through the UI (`client_platform: "web"`) 2. Reload a protected page 3. Observe `auth/refresh` |
| Expected | The httpOnly `pol_refresh` cookie set by `/auth/verify-otp` is stored and sent on `/auth/refresh`, so a reload silently restores the session |
| Actual | `@pol/api-client` called `fetch` without `credentials`, so the browser discarded the `Set-Cookie`; `pol_refresh` never existed and every reload/expiry logged the user out |
| Evidence | `context.cookies()` probe showed only `pol.session`/`pol.role`; after the fix `pol_refresh` is present and refresh returns 200. `tests/navigation-states.spec.ts::refresh keeps the session…` |
| Suspected cause | Client library written for bearer-token-only mobile and reused by the web app without a credentials option |
| Linked TODO / BUG | `TODO-079` |
| Owner | unassigned |
| Fix SHA | commit `fix(web): restore deep links and survive reload without re-login` |
| Regression test | `navigation-states.spec.ts` (reload + session-expiry tests) |
| Verified by / at | 2026-10-23 · browser suite 44 passed |

### BUG-021 — Token refresh overwrote the persisted profile with nulls

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S2 (silent logout on every reload that refreshes) |
| Role / persona | all web users |
| Branch / SHA | `test/journey-evidence-20261022` @ `9f53af2` |
| Environment | local test · Playwright chromium |
| Steps to reproduce | 1. Log in 2. Reload a protected page (access token is memory-only, so a refresh runs) 3. Read `localStorage["pol.auth.profile"]` |
| Expected | Refresh replaces only the access token; user/role stay available for route guards |
| Actual | `tryRefresh` called `setSession({ accessToken })`, which persisted `{user:null, role:null}`; `RequireRole` then saw `role:null` and redirected to login |
| Evidence | Before/after reload probe printed `{"user":null,"role":null}` in localStorage and a jump to `/auth/login`; after the fix the profile and URL survive the reload (`navigation-states.spec.ts::refresh keeps the session…`) |
| Suspected cause | One store action (`setSession`) used for two different intents (full login vs token-only refresh) |
| Linked TODO / BUG | `TODO-079` |
| Owner | unassigned |
| Fix SHA | commit `fix(web): restore deep links and survive reload without re-login` |
| Regression test | `navigation-states.spec.ts` (reload case) |
| Verified by / at | 2026-10-23 · browser suite 44 passed |

### BUG-022 — 13 screens were marked VERIFIED with only an API smoke

| Field | Value |
| --- | --- |
| Status | FIXED |
| Severity | S3 (evidence integrity: the gate reads these statuses) |
| Role / persona | n/a (process + documentation) |
| Branch / SHA | `test/journey-evidence-20261022` @ `6368f42` |
| Environment | repository evidence review |
| Steps to reproduce | 1. Parse `mvp/MVP_SCREEN_MATRIX.md` screen rows 2. Take rows whose status is `VERIFIED` 3. Ask which Playwright spec drives that route |
| Expected | `VERIFIED` means a browser test exercised the screen end to end, as the pre-build gate assumes |
| Actual | 13 routes (`/profile`, `/notifications`, `/notifications/preferences`, `/field`, `/retailer/catalog`, `/retailer/finance`, `/retailer/vendors`, `/retailer/vendors/{id}`, `/vendor/catalog`, `/vendor/inventory/daily`, `/vendor/referrals`, `/vendor/settlements`, plus one duplicate `SH-*` row) were marked `VERIFIED` on the strength of an authenticated API call + a static route 200 — no click-through |
| Evidence | `mvp/SCREEN_TEST_PARITY.md` shows those routes as `GAP`; `scripts/test_screen_parity.py::test_verified_screens_have_a_browser_test` now fails if the state returns |
| Suspected cause | The 2026-09-23 QA cycle promoted screens from "static route 200" without a browser assertion, and no guard compared matrix status against specs |
| Linked TODO / BUG | `TODO-080` |
| Owner | unassigned |
| Fix SHA | commit `test(web): add screen/api/test parity ledger and guards` |
| Regression test | `scripts/test_screen_parity.py` (7 tests) |
| Verified by / at | 2026-10-23 · python suite 891 passed |

