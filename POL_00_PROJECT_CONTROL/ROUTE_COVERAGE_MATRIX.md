# POL Route Coverage Matrix

**Status:** CANONICAL ENGINEERING QA CHECKLIST
**Purpose:** Prevent isolated-domain completeness from being mistaken for end-to-end platform completeness.

## Status vocabulary

- **GREEN:** canonical writer/reader boundary exists and automated route tests pass.
- **AMBER:** domain model exists, but canonical application boundary or provider execution is not yet complete.
- **RED:** broken invariant, missing source-of-truth, or failing route test.

| Route | SSoT / writer | Async boundary | Main failure modes | Automated evidence | Status |
|---|---|---|---|---|---|
| Auth / membership | `organization_memberships`, `user_sessions` | N/A | revoked membership, wrong org, invalid role | tenant/identity matrix | GREEN* |
| Basket -> Allocation | `baskets`, `allocation_plans` | N/A | stale version, invalid mapping, expired plan | allocation + basket tests | GREEN |
| Allocation -> Checkout | `CanonicalCheckoutGateway` | transactional DB | stale price, stale stock, MOQ/MOV, capacity | checkout + concurrency + integration tests | GREEN* |
| Checkout -> Reservation | `inventory_reservations`, `vendor_inventory` | outbox after commit | oversell, duplicate checkout, partial reservation | concurrency 1–3 | GREEN* |
| Order -> Vendor response | `orders` | outbox/notification | timeout, reject, double accept | runtime + concurrency | GREEN* |
| Order -> Fulfillment | `deliveries`, `proof_of_delivery` | integration worker | duplicate dispatch, invalid POD | runtime delivery scenarios | GREEN* |
| Payment -> Settlement | `payments`, `settlements` | reconciliation worker | wrong amount, duplicate evidence, dispute hold | payment/runtime tests | GREEN* |
| Dispute -> Adjustment | `disputes`, `refunds`, settlement projection | outbox | duplicate dispute/refund, wrong blast radius | runtime + concurrency | GREEN* |
| Daily inventory -> reminder | `daily_inventory_confirmations`, `vendor_inventory_responsibilities` | outbox | wrong recipient, duplicate reminder, missing PENDING row | integration + operational tests | GREEN* |
| Reminder -> logical notification | `outbox_events`, `notification_templates` | canonical integration worker | arbitrary recipient, missing template | integration worker tests | GREEN* |
| Vendor -> Referral -> Retailer | `vendor_referrals`, `vendor_referral_attributions` | outbox passthrough for analytics | wrong tenant, duplicate attribution, over-redemption | `test_vendor_referral.py` | GREEN* |
| Notification -> delivery | `notification_deliveries` | delivery worker | retry storm, duplicate channel, recursive outbox | delivery boundary tests | AMBER |
| Feedback -> Admin | `feedback_submissions` | outbox | tenant leakage, missing context, no triage ownership | feedback tests | AMBER |
| Feedback reply -> user | `feedback_submissions`, `notifications` | delivery worker | wrong user, missing delivery | integration tests | AMBER |
| Support -> case lifecycle | `support_cases`, assignments/messages | N/A | reassignment race, unauthorized notes | support tests | AMBER |
| Returns / RMA | `returns`, `return_items` | N/A | reverse-logistics execution completeness, refund linkage | schema/runtime evidence | AMBER |
| Analytics / KPI | event + metric lineage | async analytics | metric drift, wrong cohort/timezone | lineage tests | AMBER |
| External provider delivery | provider adapter boundary | worker/provider | provider failure, retry/backoff, credential/config | not live tested | AMBER |

\* GREEN means the domain route and database behavior are verified; it does **not** mean the production API/mobile/web runtime is complete.

## Gate to visual-design phase

POL should not begin full visual-system engineering until all MVP-critical rows are GREEN and every AMBER row has a documented explicit reason that is outside the UI scope.

Required pre-UI gates:

1. Migrations 001→N apply from an empty PostgreSQL 18 database.
2. Full verification suite is zero-failure.
3. Cross-domain integration suite is zero-failure.
4. Canonical workers have explicit ownership of every async side effect.
5. No legacy service can be reached from the application boundary.
6. Route-level negative tests exist for tenant, state, price, stock, recipient and idempotency failures.
7. The API/client contract is specified for every GREEN route.
8. Simplicity invariants remain green after the API boundary is introduced.
9. Vendor Referral is treated as an MVP acquisition route, not as a future monetization feature.
