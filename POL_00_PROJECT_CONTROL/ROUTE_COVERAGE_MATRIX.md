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
| Universal user profile | `user_profiles` | none required | missing profile, cross-user write, stale identity projection | `test_user_profiles.py` | GREEN |
| Membership persona profile | `membership_profiles` + role-specific profile tables | none required | wrong tenant context, stale persona after role change | `test_user_profiles.py` | GREEN |
| Basket -> Allocation | `baskets`, `allocation_plans` | N/A | stale version, invalid mapping, expired plan | allocation + basket tests | GREEN |
| Allocation -> Checkout | `CanonicalCheckoutGateway` | transactional DB | stale price, stale stock, MOQ/MOV, capacity | checkout + concurrency + integration tests | GREEN* |
| Checkout -> Reservation | `inventory_reservations`, `vendor_inventory` | outbox after commit | oversell, duplicate checkout, partial reservation | concurrency 1–3 | GREEN* |
| Order -> Vendor response | `orders` | outbox/notification | timeout, reject, double accept | runtime + concurrency | GREEN* |
| Order -> Fulfillment | `deliveries`, `proof_of_delivery` | integration worker | duplicate dispatch, invalid POD | runtime delivery scenarios | GREEN* |
| Payment -> Settlement | `payments`, `settlements` | reconciliation worker | wrong amount, duplicate evidence, dispute hold | payment/runtime tests | GREEN* |
| Dispute -> Adjustment | `disputes`, `refunds`, settlement projection | outbox | duplicate dispute/refund, wrong blast radius | runtime + concurrency | GREEN* |
| RMA -> Refund | `returns`, `refunds` | outbox optional | missing refund linkage, zero refund, duplicate refund | route hardening + RMA tests | GREEN* |
| Daily inventory -> reminder | `daily_inventory_confirmations`, `vendor_inventory_responsibilities` | outbox | wrong recipient, duplicate reminder, missing PENDING row | integration + operational tests | GREEN* |
| Reminder -> logical notification | `outbox_events`, `notification_templates` | canonical integration worker | arbitrary recipient, missing template | integration worker tests | GREEN* |
| Vendor -> Referral -> Retailer | `vendor_referrals`, `vendor_referral_attributions` | outbox passthrough for analytics | wrong tenant, duplicate attribution, over-redemption | `test_vendor_referral.py` | GREEN* |
| Notification -> delivery | `notification_deliveries` | delivery worker | retry storm, duplicate channel, provider failure | delivery boundary tests | AMBER |
| Feedback -> Admin | `feedback_submissions` | outbox | tenant leakage, missing context, no triage ownership | feedback tests | AMBER |
| Feedback reply -> user | `feedback_submissions`, `notifications` | delivery worker | wrong user, missing delivery | integration tests | AMBER |
| Support -> case lifecycle | `support_cases`, assignments/messages | N/A | reassignment race, unauthorized notes | support tests | AMBER |
| Returns / RMA | `returns`, `return_items` | N/A | reverse-logistics execution completeness, inspection quantities | schema/runtime evidence | AMBER |
| Analytics / KPI | event + metric lineage | async analytics | metric drift, wrong cohort/timezone | lineage tests | AMBER |
| External provider delivery | provider adapter boundary | worker/provider | provider failure, retry/backoff, credential/config | not live tested | AMBER |

\* GREEN means the domain route and database behavior are verified; it does **not** mean the production API/mobile/web runtime is complete.

## Batch 4 evidence qualification — 2026-09-17

This section supersedes the GREEN-eligibility recommendations in `CONTRACT_RECONCILIATION_2026-09-17.md` section 4. No AMBER route is promoted by Batch 4. GREEN* entries above remain limited historical domain/database evidence, not certification of a complete authenticated application route.

| Route | Previous | Result | Evidence and remaining gate |
|---|---|---|---|
| Notification -> delivery | AMBER | AMBER | `test_batch4_recipient_membership_isolation` in `scripts/test_canonical_integration_worker.py` verifies active recipient membership and no unauthorized notification/delivery creation. It does not certify live SMS/push delivery, channel fan-out or retry recovery. |
| Feedback -> Admin | AMBER | AMBER | Existing feedback tests verify direct service reads/admin checks. `application_boundary.py` does not pass the active operator context into admin reads/replies; `_require_admin` checks any operator membership. Complete active-context route evidence is absent. |
| Feedback reply -> user | AMBER | AMBER | Reply outbox routing exists, but active-context authorization, repeated reply delivery semantics and complete user delivery evidence remain incomplete. Provider credentials alone do not close the route. |
| Support -> case lifecycle | AMBER | AMBER | Direct service tests verify ownership and ops restrictions. Read/message/assignment/transition facade methods do not propagate active organization context. Owner/any-operator checks are not full active-tenant route evidence. |
| Returns / RMA | AMBER | AMBER | Batch 2/3 tests verify request/transition/refund controls; they do not certify reverse-logistics execution and inspection quantities, the failure modes for this row. The narrower RMA -> Refund row is a separate claim. |
| Analytics / KPI | AMBER | AMBER | `11_PILOT/KPIs.md` defines KPIs; lineage schema checks do not prove an operational calculation/read pipeline with correct cohorts and timezone behavior. |
| External provider delivery | AMBER | AMBER | Adapter/configuration tests are not live provider certification. Deployment, channel policy integration and failure recovery remain gates. |

Recipient membership is checked at canonical worker materialization time, using the existing `organization_memberships` and active `organizations` authority with row locks. Missing routing or inactive/mismatched membership raises `IntegrationWorkerError` before notification creation. Event-specific producer role/aggregate selection remains separate; Batch 4 does not certify arbitrary producer payloads or direct SQL notification writes.

See `BATCH4_CONTRACT_CLOSURE_2026-09-17.md` for policy blockers, individual pre-UI gate qualifications and design synchronization requirements. An unchanged GREEN* label must not override these explicit limitations.



## Batch 6C HTTP transport evidence — 2026-09-18

Batch 6C-3 adds authenticated HTTP coverage for the retailer commerce entrypoints:
- `POST /api/v1/baskets`
- `POST /api/v1/baskets/{basket_id}/items`
- `POST /api/v1/baskets/{basket_id}/allocation-preview`

The automated transport evidence is green at the tested boundary, and the PostgreSQL application-boundary test verifies basket creation, optimistic versioning, deterministic allocation and allocation-plan persistence. The GREEN classification still does not certify deployed production API/mobile/web runtime.

Batch 6C-4 adds the first authenticated vendor-side order transition:
- `POST /api/v1/orders/{order_id}/accept`

This route is limited to `SUBMITTED -> ACCEPTED` for an active vendor member. The tested mutation consumes active inventory reservations, decrements physical inventory, updates accepted quantities and creates tenant-scoped `ORDER_ACCEPTED` outbox events. This does **not** close partial acceptance, rejection, timeout automation, preparation/dispatch/delivery transitions or live notification provider execution.

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
10. Universal and persona profile contracts are tested for every supported MVP persona.
