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
| BUG-007 | S3 | `FIXED` | Mobile API client issued `fetch` without any abort timeout, so a stalled connection could hang a screen indefinitely with no error, no offline banner and no way to retry | Retailer / vendor app users | `c6c0a20` | `TODO-074`, `TODO-088` | unassigned |
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
| Branch / SHA | `test/journey-evidence-20261022` @ `c6c0a20` |
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

