# POL — Six-Digit OTP Contract Amendment (2026-10-25)

## Decision

All one-time codes in POL are exactly **six numeric digits** (`0`–`9`), including authentication/registration OTP and delivery proof-of-delivery OTP. Leading zeroes are valid and must be preserved as strings. Never parse an OTP as a number.

This amendment supersedes the former four-digit choice in D-018. It changes code length only. Authentication parameters remain unchanged: 120-second TTL, 60-second resend interval, 3 requests per 5 minutes per phone+IP, 5 verification attempts, 10-minute lockout after five failed attempts, 15-minute access token and 30-day refresh session. Delivery OTP remains its own purpose with the recipient outbox channel and durable attempt accounting; authentication TTL/rate-limit behavior must not be copied to delivery unless its own contract says so.

## Implementation areas updated on this branch

- **Source of truth and governance:** `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`, `POL_00_PROJECT_CONTROL/CURRENT_SOURCE_OF_TRUTH.md`.
- **Backend contract/config:** `scripts/operational_config.py`, `scripts/api/schemas.py`, `scripts/domain_services.py`, `scripts/fulfillment_service.py` (generation follows `OTP_CODE_LENGTH`).
- **Authentication and delivery tests:** `scripts/test_auth_contract.py`, `scripts/test_http_transport.py`, `scripts/test_http_fulfillment.py`, `scripts/test_http_proof_of_delivery.py`, `scripts/test_http_delivery_pod_g440_451.py`.
- **Web/mobile UI:** login screens, delivery confirmation screens, mocks and Playwright test fixtures use six digits and reject four-digit values.
- **Contracts/specifications:** API contracts, schema notes, API map, screen matrix, architecture, design components and the master experience tree.
- **Database:** `deliveries.delivery_otp` was already `VARCHAR(6)`; no widening migration is needed. Do not rewrite historical migrations; migration 030's comment is updated for the current six-digit code.

## Agent / reviewer instructions

1. Review the branch diff against `main`; confirm no behavior outside OTP length changed.
2. Search active source, tests, docs and design source for four-digit OTP assumptions. Distinguish dated historical execution records from active requirements; do not rewrite historical test outcomes to imply they tested six-digit codes.
3. Run targeted backend checks in the configured test environment:
   - `pytest scripts/test_auth_contract.py`
   - `pytest scripts/test_http_transport.py`
   - `pytest scripts/test_http_fulfillment.py`
   - `pytest scripts/test_http_proof_of_delivery.py`
   - `pytest scripts/test_http_delivery_pod_g440_451.py`
4. Run web checks from `mvp/`, including login and delivery-flow Playwright specs, mobile/web typechecks and relevant build gates. Do not claim PASS without current logs.
5. Add explicit negative tests proving four-digit codes are rejected for both login and delivery, and positive tests accepting six digits including leading zeroes.
6. Verify the mobile six-box input handles paste/autofill, delete/backspace, focus movement, leading zeroes and Android keyboard behavior. If issues appear, fix them in scope and record exact evidence in `TODO_LIST.md` / the execution log.
7. Treat old four-digit screenshots, local-run reports and dated release summaries as history only. Fresh CI/device/runtime evidence is required before marking this change verified.

## Verification status

Source edits are committed to this dedicated branch, but this session has not executed the local Python/Node test suites, typechecks, Android builds or device/runtime capture. Status is **implementation submitted / verification pending**, not PASS.

## Review checklist

- [ ] All active OTP producers emit exactly six digits, retaining leading zeroes.
- [ ] API schemas accept exactly six numeric digits and reject four digits/non-numeric values.
- [ ] Login and delivery UI allow exactly six digits.
- [ ] Mock transports and test fixtures agree with the contract.
- [ ] Auth security timing/rate/attempt/token parameters are unchanged.
- [ ] Delivery OTP remains recipient-only, purpose-bound, single-use and attempt-limited.
- [ ] Tests and web/mobile build checks run on this branch and their results are recorded.
