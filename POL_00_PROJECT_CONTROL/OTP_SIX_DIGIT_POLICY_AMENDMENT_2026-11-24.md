# POL — Six-Digit OTP Policy Amendment

**Decision date:** 2026-11-24  
**Status:** Approved, implemented and merged via PR #59 on 2026-11-24  
**Governing register:** POL_00_PROJECT_CONTROL/DECISION_REGISTER.md  
**Supersedes:** Former four-digit authentication OTP wording in D-018 and the dependent implementation/design documentation

## 1. Decision

All newly issued POL OTPs are standardized to exactly **six ASCII numeric digits**. Codes are strings, not numbers; leading zeroes are significant and must be preserved end-to-end.

This amendment changes the code length only for authentication policy under D-018. It does not silently change the other approved D-018 controls.

## 2. Authentication OTP — D-018

Login and registration OTPs must:

- Contain exactly six ASCII digits (0–9).
- Have a 120-second validity period.
- Enforce a 60-second resend interval.
- Enforce at most 3 OTP requests per 5 minutes per phone number and IP.
- Permit at most 5 verification attempts per challenge.
- Apply a 10-minute phone lockout after 5 failed attempts.
- Issue a 15-minute access JWT after successful verification.
- Use a 30-day refresh-session lifetime.
- Preserve the explicit undecided status of refresh-token rotation as a product/security policy; current runtime behavior is not itself a policy decision.

SMS provider templates, backend generation, request schemas, web/mobile forms, test fixtures and user-facing text must all use the six-digit contract.

## 3. Delivery / proof-of-delivery OTP — D-029

Newly issued delivery/POD OTPs must also contain exactly six ASCII digits, but their lifecycle remains separate from login authentication.

- Generate codes using a cryptographically secure random source and preserve leading zeroes.
- Bind the code to the intended delivery and tenant.
- Deliver it only to the authorized retailer recipient through the canonical transactional outbox/inbox event.
- Never return the recipient OTP in a vendor-facing dispatch response or expose it in logs.
- Consume it once and preserve durable delivery-attempt accounting.
- Keep the existing delivery-specific expiry and attempt limits; do not automatically copy D-018 login TTL, resend or phone-lockout rules into the delivery domain.

## 4. Existing in-flight deliveries

A four-digit delivery code issued before migration 077 may remain usable only for its original delivery until that delivery reaches a terminal state. This is a temporary compatibility rule to avoid stranding a shipment whose recipient has already been given a code.

Migration 077 must:
- Add delivery_otp_length with a six-digit default for new rows.
- Backfill existing rows using the actual stored code length.
- Preserve every currently issued code as-is.
- Never rotate, clear, invalidate or re-send an active code.
- Enforce that a new delivery record stores a six-digit code and length 6.
- Permit a four-digit code only when the same pre-existing delivery row was backfilled with length 4.

Once all pre-migration four-digit deliveries are terminal, a later migration may remove the legacy constraint after an operational check. No new four-digit code may be generated after this amendment.

## 5. Implementation and acceptance

The implementation was selectively re-authored from the audited mainline on:

- feat/six-digit-otp-and-social-impact-readme-20261124

The historical PRs #49 and #50 remain closed and must not be merged wholesale. Their branch tips are materially behind current main and are retained only as historical implementation evidence. Migration 077 is re-authored on the current base with the legacy in-flight safeguard described above.

The exact feature SHA passed the following checks before merge:
- PostgreSQL 18 migration-chain and schema constraint verification.
- Authentication six-digit API and generation tests, including leading-zero handling.
- Delivery six-digit issuance, recipient-only event, tenant binding, single-use and attempt-cap tests.
- Legacy four-digit in-flight completion test.
- Web typecheck/build and browser E2E.
- Mobile typecheck, functional/regression/mock QA, and device-level OTP UI review.
- Static verification and a security/diff review.

The exact PR head SHA `dbf0a2284e4f16d0cc1e7568b78e81e11c5352a6` passed 852/852 backend tests (0 failed, 0 skipped; four warnings) in run `45488346802`; migration chain 001–077 applied successfully in PostgreSQL 18. Browser E2E passed 41/41 in run `45488346616`, mobile verification passed 17/17 Expo/mobile steps plus the QA eligibility gate in run `45488346626`, and the static gate passed 11/11 in run `45488346621`. PR #59 merged to main as `f9eca328b053dfacfe4c42c81c1c9c468fb8b607`.

## 6. Documentation and product communication

All current product, engineering, design and onboarding documents must describe six-digit authentication OTPs and six-digit newly issued delivery OTPs. Historic audit logs may retain the wording that was accurate at the time, but must be explicitly marked as historical where a reader could mistake them for current policy.

The six-digit code change does not authorize a change to pricing, credit, payment custody, refund, settlement, role, tenant, session-rotation or delivery-service guarantees.


## Historical migration metadata

`migrations/030_delivery_otp_column.sql` is an already-released historical migration and is intentionally not rewritten. Its original SQL comment reflects the former D-018 wording and must be read as historical metadata only. Migration 077 updates the live PostgreSQL column comment to the D-029 six-digit new-issuance policy and explicitly describes the temporary in-flight four-digit compatibility rule.


## 7. Post-merge acceptance boundaries — 2026-11-25

- The two original implementation branches `fix/otp-six-digit-contract-20261025` and `fix/otp-six-digit-standard-20261025` remain closed and unmerged. Their original policy objection was superseded, but they remain stale historical branches and must not be merged wholesale.
- The mobile workflow's Android QA APK matrix job was skipped by the existing TODO-084 gate. No APK build, device installation, or physical-device acceptance is claimed by PR #59.
- Updated six-digit OTP UI screenshots, accessibility review on real devices, live SMS.ir template/send/verify acceptance, independent security review, staging deployment and operational sign-off remain separate release gates.
