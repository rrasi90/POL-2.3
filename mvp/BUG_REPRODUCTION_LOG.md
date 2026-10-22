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
