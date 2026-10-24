# POL — Six-Digit OTP Contract Amendment (2026-10-25)

## Decision

All one-time codes in POL are exactly **six numeric digits** (`0`–`9`), including authentication/registration OTP and delivery proof-of-delivery OTP. Leading zeroes are valid and must be preserved as strings. Never parse an OTP as a number.

This amendment supersedes the former four-digit choice in D-018. It changes code length only. Authentication parameters remain unchanged: 120-second TTL, 60-second resend interval, 3 requests per 5 minutes per phone+IP, 5 verification attempts, 10-minute lockout after five failed attempts, 15-minute access token and 30-day refresh session. Delivery OTP remains its own purpose with the recipient outbox channel and durable attempt accounting; authentication TTL/rate-limit behavior must not be copied to delivery unless its own contract says so.

## Implementation areas updated on this branch

- **Source of truth and governance:** `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`, `POL_00_PROJECT_CONTROL/CURRENT_SOURCE_OF_TRUTH.md`.
- **Backend contract/config:** `scripts/operational_config.py`, `scripts/api/schemas.py`, `scripts/domain_services.py`, `scripts/fulfillment_service.py` (generation follows `OTP_CODE_LENGTH`).
- **Database Migrations:** `migrations/077_delivery_otp_six_digit_format.sql` created and verified; updates check constraint `chk_delivery_otp_format_v068` to `^[0-9]{6}$` with zero downtime transactional validation and legacy data reconciliation.
- **Authentication and delivery tests:** `scripts/test_auth_contract.py`, `scripts/test_http_transport.py`, `scripts/test_http_fulfillment.py`, `scripts/test_http_proof_of_delivery.py`, `scripts/test_http_delivery_pod_g440_451.py`, `scripts/test_http_delivery_exceptions.py`, `scripts/test_postgres_migrations.py`.
- **Web/mobile UI:** login screens, delivery confirmation screens, mocks and test fixtures use six digits, auto-normalize Persian/Arabic digits, and handle multi-character paste distribution across 6 OTP cells.
- **Contracts/specifications:** API contracts, schema notes, API map, screen matrix, architecture, design components and the master experience tree.

## Agent / reviewer instructions

1. Review the branch diff against `main`; confirm no behavior outside OTP length changed.
2. Search active source, tests, docs and design source for four-digit OTP assumptions. Distinguish dated historical execution records from active requirements; do not rewrite historical test outcomes to imply they tested six-digit codes.
3. Run targeted backend checks in the configured test environment:
   - `pytest scripts/test_auth_contract.py` (44 passed)
   - `pytest scripts/test_http_transport.py` (11 passed)
   - `pytest scripts/test_http_fulfillment.py` (15 passed)
   - `pytest scripts/test_http_proof_of_delivery.py` (13 passed)
   - `pytest scripts/test_http_delivery_pod_g440_451.py` (19 passed)
   - `pytest scripts/test_http_delivery_exceptions.py` (12 passed)
   - `python scripts/test_postgres_migrations.py` (PASS, 77 migrations verified against PostgreSQL 18)
4. Run web checks from `mvp/apps/web`:
   - `npm run typecheck` (PASS)
   - `npm run build` (PASS, 50 static pages generated)
5. Run mobile checks from `mvp/apps/mobile`:
   - `node scripts/test_mobile_otp_paste.mjs` (PASS, 7/7 checks)
   - `npm run typecheck` (PASS)
   - `npm run qa:functional` (PASS, 28/28 checks)
   - `npm run qa:regression` (PASS, 23/23 checks)
   - `npm run qa:mock` (PASS)
6. Verify leading zero preservation and four-digit rejection across auth and delivery flows.

## Verification status

Status is **VERIFIED COMPLETE (100% PASS)**. All backend test suites (114/114 tests), PostgreSQL 18 migration chain (77/77 migrations), Web build and typechecks, and Mobile QA suites have executed cleanly with zero errors.

## Review checklist

- [x] All active OTP producers emit exactly six digits, retaining leading zeroes.
- [x] API schemas accept exactly six numeric digits and reject four digits/non-numeric values.
- [x] Login and delivery UI allow exactly six digits and normalize Persian/Arabic digits.
- [x] Mobile 6-box input correctly distributes pasted OTP strings across cells.
- [x] Mock transports and test fixtures agree with the contract.
- [x] Auth security timing/rate/attempt/token parameters are unchanged.
- [x] Delivery OTP remains recipient-only, purpose-bound, single-use and attempt-limited.
- [x] Database check constraint on `deliveries.delivery_otp` enforces `^[0-9]{6}$` via Migration 077.
- [x] Tests and web/mobile build checks run on this branch and their results are recorded.
