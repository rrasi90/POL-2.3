# POL Project-Wide Bug Audit — 2026-09-16

Status: ACTIVE ENGINEERING AUDIT  
Branch audited: `research-hardening-2026-09-14`  
HEAD: `af7e5815297360f6a03df5af9838fdb33f40ed71`

## Scope
Repository-wide review of governance, migrations, domain services, allocation, checkout, RBAC/tenant boundaries, payments, RMA, notifications, tests and CI. This is a source inspection audit against the current GitHub branch; it is not a claim of production-runtime execution.

## Confirmed P0/P1 findings

### BUG-001 — Checkout creates child Orders without OrderItems — P0
**Files:** `scripts/revalidation_checkout.py`, `scripts/operational_policies.py`, canonical multi-vendor model.

`RevalidationCheckoutService.revalidate_and_checkout()` inserts an `orders` row for each allocation entry and creates an inventory reservation, but it never inserts `order_items`. The canonical domain explicitly models `Order -> OrderItem`, and RMA/fulfillment/query layers depend on order items.

Impact:
- orders can exist with no physical commercial lines;
- RMA cannot find the returned lines reliably;
- downstream invoice/fulfillment/reporting may have no item detail;
- order totals can exist without line-level persistence.

The current checkout contract test only verifies delegation and does not verify persisted order items.

Recommended fix: create one canonical `order_items` row per allocated basket line, linking the created child order to `vendor_product_id`, requested quantity, price and packaging snapshot; add an integration assertion that every submitted child order has exactly its allocated lines.

### BUG-002 — Checkout child-order creation appears line-level, not vendor-level — P0/P1
`revalidation_checkout.py` loops directly over `vendor_allocations` and creates one `orders` row per element. `validate_allocation_against_basket()` defines `vendor_allocations` as one entry per basket product, so multiple products allocated to the same vendor can create multiple child orders for the same vendor.

Canonical D-014 requires a unified basket partitioned into vendor-specific child orders. The domain model states `OrderGroup -> N Orders`, where each child order represents one vendor contract.

The same loop also creates reservation idempotency keys as `res-{idempotency_key}-{vendor_id}`, which can collide if the same vendor receives multiple allocation lines.

Recommended fix: aggregate allocations by `vendor_id` inside checkout, create one child order per vendor, then insert multiple `order_items` under that child order.

### BUG-003 — RMA refund completion violates separation of duties — P0/P1
`CanonicalReturnService.transition()` allows `REFUND_PENDING`, `REFUNDED` and `CLOSED` when `retailer_ok OR vendor_ok` is true. `_ensure_refund_pending()` writes `approved_by_user_id = actor_user_id`, and `_complete_refund()` completes the linked refund.

This conflicts with the canonical financial/operational rule that the claimant, support verification and financial approval must be separated.

Impact: a retailer/vendor actor can potentially approve or complete a refund path themselves.

Recommended fix: require an authorized operator/finance role for financial approval and refund completion; record a distinct approval actor; forbid claimant/financial-approver self-approval.

### BUG-004 — RMA duplicate line entries can bypass quantity ceiling — P1
`request_return()` validates each requested return line independently against `delivered_quantity` / `ordered_quantity`. It does not aggregate duplicate `order_item_id` entries before checking the limit.

Example: if an item has 10 returnable units, two payload entries of 10 each can each pass the check and create 20 requested return units.

Recommended fix: normalize/aggregate by `order_item_id` before validation, then enforce total requested quantity <= maximum returnable quantity and enforce uniqueness at the request level.

### BUG-005 — Unknown outbox events remain permanently PENDING — P1
`CanonicalIntegrationWorker.process_pending()` selects every PENDING outbox event, publishes explicit passthrough events, processes known notification events, but simply `continue`s for any other event.

Such an event is therefore re-selected forever and never transitions to an explicit terminal/error state. The queue can repeatedly scan the same unsupported event and starve later events depending on batch size/order.

Recommended fix: mark unsupported events with an explicit `UNSUPPORTED`/`FAILED_REVIEW` state and record the reason; preserve retry only for transient processing failures.

### BUG-006 — Payment reconciliation accepts one matching observation despite conflicting trusted evidence — P1
`PaymentReconciliationWorker` sets `exact_match = any(value == expected for value in observed_values)`. Thus one trusted observation matching the expected payment causes `MATCHED` even if another trusted observation for the same payment reports a conflicting amount/reference.

The code intentionally avoids additive double counting, but it does not define a conflict state for mutually inconsistent trusted observations.

Recommended fix: define evidence precedence/consistency rules. If trusted observations conflict, require explicit reconciliation/exception handling rather than auto-resolving on `any()`.

### BUG-007 — Verification script contains a stale 56-table / 001-003 audit model — P1
`scripts/verify_repository_consistency.py` still hardcodes checks against migrations 001, 002 and 003 and a 56-table baseline. The repository's canonical migration chain now extends through migration 023 and the current verified schema baseline is 90 public tables.

This means the legacy verifier can report success while missing defects introduced by later migrations.

The GitHub Actions workflow itself uses the dynamic migration runner plus `run_verification_suite.py`, so this stale verifier is not by itself proof that current CI is green-invalid; however, it is a dangerous standalone audit tool and can mislead engineers/agents.

Recommended fix: delete or rewrite the legacy verifier to consume the full numbered migration chain and current schema manifest.

### BUG-008 — Master E2E test is not a true canonical end-to-end test — P1
`test_e2e_mvp_platform.py` imports legacy `domain_services` and directly mutates database state for acceptance, reservation consumption/release, invoices, support, dispute and notification checks.

The test does invoke `CanonicalCheckoutGateway`, but large portions of the supposed E2E lifecycle bypass the canonical application boundary. It also does not assert the missing `order_items` problem after checkout.

Impact: a green E2E run can coexist with broken client-facing canonical service behavior.

Recommended fix: make E2E tests use only application-boundary commands for user-facing mutations; reserve direct SQL for fixture setup and read-only assertions.

## Confirmed test-coverage gaps

### GAP-001 — No checkout assertion for persisted line items
The checkout contract test is delegation-oriented and does not verify the database aggregate after checkout.

### GAP-002 — No integration test for one-child-order-per-vendor invariant
The allocation test suite verifies vendor selection but does not verify that checkout groups all lines for a vendor under one child order.

### GAP-003 — No RMA duplicate-item regression test
A test should submit duplicate `order_item_id` entries and prove the aggregate quantity limit is enforced.

### GAP-004 — No RMA financial-role authorization test
There should be explicit negative tests for retailer/vendor attempts to approve or complete refunds.

### GAP-005 — No unsupported-outbox-event test
The integration worker suite covers known notification events and referral passthrough, but not an unknown event that must not remain PENDING forever.

## Items inspected and NOT classified as current bugs

- Migration 018 explicitly deletes stale persona subprofiles when a membership role changes, and the user-profile regression test covers that case. Therefore the earlier suspected stale-persona issue is considered fixed.
- Migration 021 enforces session active-organization membership and order-group/basket/retailer consistency at the database boundary.
- Migration 023 intentionally removes the over-strict support-case tenant-equality trigger; this matches the documented support semantics and is not treated as a bug by itself.
- Current branch CI run associated with the audited HEAD completed successfully; this is evidence that the configured CI suite passed, not evidence that the above semantic defects do not exist.

## Security / quality observations for follow-up

### OBS-001 — Provider response metadata may retain unnecessary provider payloads
`provider_adapters.py` persists the complete parsed provider response in the returned metadata. Production privacy/retention policy should decide whether the full response is necessary.

### OBS-002 — Legacy role aliases remain accepted in some application-service role checks
The canonical role source is `organization_memberships.role`; `SUPER_ADMIN`/`OPS_ADMIN` are legacy aliases. The repository intentionally retains them for compatibility, but future code should normalize/remove alias acceptance once legacy fixtures are gone.

### OBS-003 — Idempotency key reuse with different request payload is not explicitly fingerprint-checked
`CanonicalCheckoutGateway._replay_existing()` returns the existing order group whenever the retailer and idempotency key match. A stricter API contract should store/compare a request fingerprint and reject the same key reused for materially different parameters.

## CI evidence
The audited branch HEAD `af7e5815297360f6a03df5af9838fdb33f40ed71` has a completed GitHub Actions verification run with conclusion `success`. The workflow dynamically applies the migration chain and executes the master pytest suite. This does not replace semantic code review.

## Priority repair order
1. BUG-001 — persist `order_items` in canonical checkout.
2. BUG-002 — aggregate checkout into one child order per vendor.
3. BUG-003 — fix RMA financial separation of duties.
4. BUG-004 — aggregate/limit duplicate RMA lines.
5. BUG-005 — terminate or quarantine unsupported outbox events.
6. BUG-006 — resolve conflicting payment evidence explicitly.
7. BUG-007 — retire or rebuild stale verification script.
8. BUG-008 — convert E2E lifecycle mutations to canonical application-boundary commands.
9. Add regression coverage for each fixed issue.

## Audit conclusion
The repository is not ready to be considered implementation-correct merely because CI is green. The highest-risk remaining issues are in the checkout aggregate, RMA authorization, async outbox handling, reconciliation semantics, and verification quality. Design work should not hide these domain/runtime issues.
