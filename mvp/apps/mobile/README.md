# POL MVP Mobile

Phase 3 Expo client under the monorepo. This app uses the backend as the sole
source of business rules and keeps the mobile API client local to the app.

## Current implementation

- Backend-derived role routing for all seven canonical roles.
- 4-digit OTP auth (D-018).
- Field-first F-01…F-05 with request-failure offline state + healthz retry.
- Retailer foundation: catalog search, basket, allocation preview, checkout with Idempotency-Key, orders and order detail.
- Vendor foundation: order queue/actions, partial-acceptance proposal, inventory, daily confirmation, settlements and order detail.
- Ops/Admin foundation: exceptions dashboard, queue read model, reconciliation and ADMIN audit read.
- Central Light/Night palette foundation.
- No Driver App (D-023).

## Verification

CI workflow: .github/workflows/pol-mvp-mobile.yml

Required checks:
1. npm ci from mvp/
2. mobile typecheck
3. Expo public config validation
4. Expo Android export

Mobile status remains IMPLEMENTED until the evidence is recorded in parity.md and
MVP_SCREEN_MATRIX.md. Minimum three Phase-3 QA cycles are required.

## Explicit remaining work

- Remaining mobile screen parity: support, vendor search/storefront, customers/staff and return/dispute write flow.
- D-028 barcode camera/matching path remains contract-only until its authoritative request/response contract and runtime dependency are available.
- Screen-by-screen Night-theme visual verification remains a QA gate.
- Live basket → allocation → checkout e2e remains a local-environment execution task.
