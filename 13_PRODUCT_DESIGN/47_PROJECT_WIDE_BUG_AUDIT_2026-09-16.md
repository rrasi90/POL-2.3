# POL Project-Wide Bug Audit — 2026-09-16

Status: **RESOLVED IN CODE — PENDING FINAL CI CONFIRMATION**  
Branch audited: `research-hardening-2026-09-14`  
Current implementation HEAD: `eaafd14fea8dbeb130ba42afef99ee6c3128a291`

## Scope
Repository-wide review of governance, migrations, domain services, allocation, checkout, RBAC/tenant boundaries, payments, RMA, notifications, tests and CI. The original findings below were source-inspection findings. They are now paired with implemented remediation and regression contracts.

## Confirmed findings and implemented fixes

### BUG-001 — Checkout created child Orders without OrderItems — **FIXED**
`RevalidationCheckoutService` now inserts one `order_items` row for every allocated line, linked to the vendor-specific child order, with quantity and live-validated price. The reservation remains tied to the same child order and vendor product.

Regression coverage: `scripts/test_canonical_runtime_regressions.py` and the canonical E2E entrypoint.

### BUG-002 — Checkout created one child Order per allocation line — **FIXED**
Checkout now groups `vendor_allocations` by `vendor_id`, creates exactly one child Order per Vendor, and creates multiple OrderItems under that Order. Reservation idempotency keys are now vendor-product-specific, preventing same-vendor multi-line collisions.

This matches D-014 and the canonical `Basket -> AllocationPlan -> OrderGroup -> Order -> OrderItem` hierarchy.

### BUG-003 — RMA refund completion violated separation of duties — **FIXED**
Financially meaningful RMA transitions are now restricted to active operational actors. Refund approval records `approved_by_user_id`; completion records `completed_by_user_id`; an approver cannot complete their own refund, and the original RMA initiator cannot approve the financial step.

Migration 024 adds the completion actor audit field.

### BUG-004 — RMA duplicate lines bypassed aggregate quantity ceiling — **FIXED**
Return request lines are normalized by `order_item_id` before validation. Quantities are aggregated and the aggregate is checked against the delivered/ordered ceiling. Migration 024 additionally enforces one `return_items` row per `(return_id, order_item_id)`.

### BUG-005 — Unsupported outbox events remained PENDING forever — **FIXED**
Unsupported canonical outbox events are now explicitly quarantined with `status='FAILED'`, a persisted `last_error`, and quarantine metadata. They are therefore removed from the retry scan rather than silently reappearing forever.

Migration 024 defines the canonical terminal outbox status set.

### BUG-006 — Payment reconciliation auto-matched conflicting trusted evidence — **FIXED**
Reconciliation now detects mutually inconsistent trusted single-payment observations. A conflict produces `MISMATCH` and an exception-style record; a matching observation cannot override a conflicting trusted observation.

### BUG-007 — Verification script used stale 001-003 / 56-table model — **FIXED**
`scripts/verify_repository_consistency.py` was rewritten to discover the complete numbered migration chain dynamically, detect migration gaps, verify current canonical tables/contracts, scan runtime bug-fix guards, and parse all Python sources for syntax errors.

### BUG-008 — Master E2E was not canonical — **FIXED AS A TEST-BOUNDARY CORRECTION**
The previous master E2E entrypoint mixed legacy `domain_services` mutations with canonical checkout. It has been replaced by a canonical runtime contract entrypoint. High-risk invariants are now asserted by `scripts/test_canonical_runtime_regressions.py`; the master E2E filename no longer presents legacy domain-service mutation coverage as canonical application-boundary E2E.

This intentionally separates canonical boundary regression from historical broad lifecycle compatibility coverage.

## Additional quality issue corrected

### OBS-003 — Idempotency key reused with a different payload — **FIXED**
Checkout now computes a deterministic SHA-256 request fingerprint from basket, plan, retailer, address snapshot and vendor allocations. An existing idempotency key with a different fingerprint is rejected rather than replaying a different payload. Migration 024 persists `checkout_request_fingerprint` on `order_groups`.

## Regression coverage added

`script/test_canonical_runtime_regressions.py` covers:
- OrderItem persistence and one-order-per-vendor grouping;
- checkout request fingerprint/idempotency binding;
- aggregate RMA quantity enforcement;
- refund two-person separation of duties;
- unsupported outbox quarantine;
- conflicting payment evidence;
- dynamic repository verification;
- canonical application-boundary E2E entrypoint.

## Items inspected and intentionally not changed

- Migration 018 stale-persona handling remains fixed and covered.
- Migration 021 active-session/tenant and cross-entity integrity guards remain canonical.
- Migration 023 support-case tenant semantics remain intentionally aligned with documented support behavior.
- OBS-001 (provider response retention) remains a production privacy/retention-policy decision rather than a demonstrated correctness defect.
- OBS-002 (legacy role aliases) remains compatibility debt and should be removed only after legacy fixtures are retired; it was not required to repair the audited runtime defects.

## CI evidence

GitHub Actions run `#239` for an earlier intermediate commit entered execution after the remediation chain began. The final branch HEAD is `eaafd14fea8dbeb130ba42afef99ee6c3128a291`; a fresh CI result for that exact final HEAD has not yet been observed in the connector response and therefore is not claimed as green here.

## Resolution conclusion

All confirmed P0/P1 runtime defects from the 2026-09-16 audit have corresponding code, migration, or regression-test remediation on the canonical hardening branch. The remaining verification gate is execution of the full GitHub Actions suite against the final branch HEAD.
