# OTP Six-Digit Contract — 2026-10-25

## Decisions and scope

As of 2026-10-25, both POL one-time-code flows use **exactly six numeric digits**, governed by two distinct decisions:

- **D-018 — Authentication/registration OTP:** login and registration codes are six digits. The earlier four-digit value is superseded. Its existing TTL, resend interval, rate limit, attempt cap, phone lockout and token-lifetime values remain unchanged.
- **D-029 — Delivery proof-of-delivery OTP:** delivery verification codes are six digits. This is a format-only delivery decision, separate from D-018. It does not import login TTL/resend/rate-limit policy into delivery.

## Authentication values unchanged by D-018

- OTP TTL: 120 seconds
- Resend interval: 60 seconds
- Rate limit: 3 OTP requests per 5 minutes, scoped to phone + IP
- Maximum verification attempts: 5 per challenge
- Phone lockout: 10 minutes after 5 failed attempts
- Access JWT lifetime: 15 minutes
- Refresh-session lifetime: 30 days
- Refresh-token rotation remains a separate open policy decision

## Delivery values unchanged by D-029

Only code length changes here. Existing delivery expiration, attempt accounting/cap, single-use verification, authorization checks, recipient-only delivery channel and the rule that the dispatch response must not expose the code remain unchanged.

## Scope of this changeset

- Central configuration: `OTP_CODE_LENGTH = 6` for authentication; distinct `DELIVERY_OTP_CODE_LENGTH = 6` for delivery. The explicit test-only authentication code is `123456`; production authentication codes remain cryptographically random.
- Delivery generation now reads the delivery-specific length constant so the two domains share the same current length without sharing their other policy knobs.
- Backend validation: authentication and delivery request schemas accept exactly six numeric digits.
- Mobile/web clients: six-digit login and delivery inputs, length checks, labels and helper text.
- QA fixtures and E2E scripts: valid code samples and browser selectors are updated to six digits.
- Product/API/security/design documentation: current policy is explicit. Dated historical reports are labelled historical rather than having old test evidence silently rewritten.
- Migration 077 updates the delivery column comment. The existing `deliveries.delivery_otp VARCHAR(6)` column already accommodates six digits; no data-type expansion is required. Historical migration 030 remains unchanged.

## Deployment and compatibility

This is a contract change and is **not backward compatible** with clients submitting four-digit codes:

1. Deploy API and clients as a coordinated release.
2. Allow pending four-digit challenges to expire or invalidate them; users must request a new six-digit code after deployment.
3. Ensure the approved SMS.ir OTP template can display six digits.
4. Never expose delivery OTP to the vendor dispatch caller; deliver it only through the canonical authorized recipient channel.
5. Run ordered migration 077 with the repository migration runner so database metadata matches D-029.

## Required verification before merge/release

- [ ] Run authentication contract and HTTP schema tests.
- [ ] Run proof-of-delivery / fulfillment tests, including max-attempt, single-use, authorization and recipient-channel tests.
- [ ] Run the full Python verification suite and web typecheck/build.
- [ ] Run browser E2E login and delivery flow against the revised contract.
- [ ] Build/launch both Android variants and verify six-cell login UI, delivery entry UI, Persian/Latin digit normalization, paste/autofill, focus/backspace and error states.
- [ ] Confirm CI results for the exact PR head SHA.

## Evidence status

GitHub source edits are prepared for review, but local test/build/device verification has **not** been run as part of authoring this changeset. Earlier four-digit test artifacts remain historical evidence and are not certification of this revision. Do not mark either flow runtime-verified until the checks above pass on the final PR head.
