# Golden E2E Scenarios — Three-Role Flow (Run 2026-10-27)

Design-only in this run (no test code changed; no POL code modified). Each scenario maps to real POL endpoints/tables from the reality audit; missing steps are recorded as FAILING GAPS, not mocked into green (plan §36.2).

## G1 — Happy path (wholesaler → retailer → delivery)

| # | Step | Actor | POL endpoint (real) | Expected state write | Status in POL today |
|---|---|---|---|---|---|
| 1 | Vendor publishes product+price+stock | VENDOR_OWNER | POST /catalog/vendors/products + prices + inventory | vendor_products/prices/inventory | EXISTS [TEST_VERIFIED test_http_vendor_catalog] |
| 2 | Retailer searches + adds to basket | RETAILER_* | GET /search; POST /baskets/{id}/items | basket_items | EXISTS [TEST_VERIFIED test_http_baskets] |
| 3 | Allocation preview (multi-vendor) | RETAILER_* | POST /baskets/{id}/allocation-preview | allocation_plan (preview) | EXISTS |
| 4 | Checkout | RETAILER_* | POST /orders + Idempotency-Key | orders/order_items/order_groups + reservations | EXISTS [TEST_VERIFIED test_http_checkout] |
| 5 | Vendor accepts (or timeout) | VENDOR_OWNER | POST /orders/{id}/accept | order ACCEPTED | EXISTS [TEST_VERIFIED + timeout worker test] |
| 6 | Vendor prepares/dispatches w/ driver meta | VENDOR_OWNER | preparing → ready → dispatch | PREPARING/READY/DISPATCHED + deliveries row | EXISTS |
| 7 | Pickup → transit → arrive | OPS/vendor | delivery/picked-up|in-transit|arrived | delivery_status transitions | EXISTS |
| 8 | Delivery + OTP confirm | driver-shaped actor (today: ops/vendor) | POST /orders/{id}/deliver | DELIVERED + OTP verify | EXISTS [TEST_VERIFIED POD tests] |
| 9 | Retailer sees timeline | RETAILER_* | GET /orders/{id}/timeline | read-only | EXISTS |
| 10 | Invoice visible | RETAILER/VENDOR | GET /invoices | read-only | EXISTS |

**G1 is fully backed by real endpoints + tests today.** The only role-shaped gap: step 7-8 actor is not a driver principal (see driver-app-readiness.md).

## G2 — Exception: shortage partial acceptance

1-5 as G1 → vendor proposes partial (POST partial-acceptance-proposals) → retailer approves (approve) → order PARTIALLY_ACCEPTED → continue G1 steps 6-10 with adjusted items. EXISTS [TEST_VERIFIED test_partial_acceptance]. Two-party protocol; single-sided forced acceptance must fail (negative test present).

## G3 — Exception: delivery failure

Steps 1-7 → delivery/failed + delivery-exception record → resolve/escalate → redelivery or dispute. EXISTS [TEST_VERIFIED test_http_delivery_exceptions].

## G4 — Dispute → refund → settlement

Delivered order → retailer opens dispute → OPS investigate → resolve (ADJUSTED_SHORTAGE) → refund issue/approve/complete (finance/refunds) → settlement adjustment SHORTAGE_DEDUCTION at period close. EXISTS at code level; **dedicated HTTP test for refunds approve/complete MISSING** (audit gap #10) — a failing-gap test to write in the implementation run.

## G5 — Concurrency & idempotency (negative battery)

- Duplicate checkout with same Idempotency-Key → single order (fingerprint migration 061) [TEST_VERIFIED]
- Inventory race: two retailers, last unit → reservation invariant (migrations 022/056/057) [TEST_VERIFIED test_postgres_concurrency]
- Vendor acceptance after timeout → rejected transition
- Staff (delegated) attempts order.accept → denied by ROLE_DELEGATION_DENY [TEST_VERIFIED test_delegated_permissions]
- Cross-tenant read: retailer A reads vendor B invoice → denied (tenant isolation [TEST_VERIFIED test_identity_tenant_isolation])
- Expired/stale token with switched org → 401 (auth boundary org check)

## G6 — Driver offline / duplicate delivery (DESIGN GAP — cannot pass today)

Driver submits "deliver" twice over flaky network → exactly one DELIVERED + one OTP consumption. **No driver mutation surface exists → this is a documented failing-gap test for the driver implementation run** (workflow WF-21; driver-app-readiness.md §missing-5).

## Cartona-evidence anchoring

G1 mirrors Cartona's evidenced retailer loop (endpoints/routes from artifact). G2-G4 have no Cartona artifact evidence (POL-canonical designs; Cartona's exact dispute/refund behavior unknown from static evidence + public sources). G6's Cartona behavior is unknown (MARKETING_CLAIM only) — POL must define its own semantics.
