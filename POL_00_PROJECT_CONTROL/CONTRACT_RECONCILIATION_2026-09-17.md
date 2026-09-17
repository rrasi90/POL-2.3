# POL Contract Reconciliation — Batch 3 (2026-09-17)

**Status:** CANONICAL RECONCILIATION RECORD (BATCH 3)
**Authority hierarchy applied:** `DECISION_REGISTER.md` → canonical product specifications → technical/data model → operations/API contracts → design.
**Scope:** documentation reconciliation + contract regression tests only. No runtime rewrite, no frontend, no Penpot, no transport framework.

## 1. Resolved contradictions (clear authority)

| # | Contract | Authority A (wins) | Conflicting artifact | Resolution |
|---|---|---|---|---|
| R-01 | Child order initial state | `06_PRODUCT/Order_Lifecycle.md` §2 (`SUBMITTED`), `migrations/001_initial_schema.sql` `orders_order_status_check` (no `PENDING`), runtime checkout (`revalidation_checkout.py` inserts `SUBMITTED`) | `06_PRODUCT/API_Contracts.md` §5.1 example said `PENDING` | API contract example corrected to `SUBMITTED`; example explicitly marks `PENDING` as obsolete. No new state invented. |
| R-02 | Order state vocabulary | `Order_Lifecycle.md` + migration 001 CHECK constraint | Any drift toward `PROCESSING`/`CONFIRMED`/`COMPLETED` | Locked by regression test `test_order_lifecycle_states_match_schema_vocabulary` and DB-level negative tests (`test_database_rejects_non_canonical_order_states`). `CREATED/SUBMITTED/ACCEPTED/PARTIALLY_ACCEPTED/REJECTED/CANCELLED/PREPARING/READY/DISPATCHED/DELIVERED` are the only canonical order states. |
| R-03 | Dispute orthogonality | `Order_Lifecycle.md` §3 (dispute is a separate state machine on `disputes` / `orders.dispute_status`) | Any conflation of `DISPUTED` into `order_status` | Regression test `test_dispute_state_projection_is_orthogonal` proves `DELIVERED` + `OPEN` coexist and `DISPUTED` violates the DDL check. |
| R-04 | Payment states & custody | `DECISION_REGISTER.md` D-006/D-015 + migration 001 `payments` CHECK (`PENDING, INITIATED, SUCCESS, FAILED, CANCELLED, REFUNDED`, `NON_CUSTODIAL_DIRECT`) | Legacy `PAID_DIRECT` / escrow vocabulary | Regression test `test_payment_states_are_canonical_non_custodial` locks the vocabulary. |
| R-05 | Authorization SSoT | `Roles_and_Permissions.md` §2.2, `IDENTITY_AND_MEMBERSHIP.md` §3, correction overlay C-01 | Legacy `users.role`, `vendors.user_id`, `retailers.user_id` as authorization | Confirmed unchanged: boundary evaluates `organization_memberships.role` + active org status only (`returns_rma.py`, `application_boundary.py`, `canonical_support.py`, `canonical_feedback.py`). Negative tenant tests added in `test_batch3_contract_matrix.py`. |
| R-06 | Acceptance timeout | `Order_Lifecycle.md` §2.1 (hard 120-minute working-calendar timeout, `VENDOR_TIMEOUT` auto-cancel), `operational_config.py` `VENDOR_ACCEPTANCE_SLA_HOURS = 2`, `test_sla_calendar.py` | None found | Consistent. No change. |

## 2. CONTRACT BLOCKER — AUTH OTP POLICY

Canonical sources disagree on the OTP digit count and no source in the authority hierarchy resolves it:

- `06_PRODUCT/Technical_Architecture_Spec.md` §3: "کد یکبارمصرف **۴ رقمی**" (4-digit), 120-second expiry, 3 SMS / 5 minutes / phone+IP, 15-minute access + 30-day refresh tokens.
- `08_DATA/IDENTITY_AND_MEMBERSHIP.md` §2.5: `code_hash` documented as "hash of the **5-digit** verification code", 120-second window, 5 attempts.
- `06_PRODUCT/API_Contracts.md` §7.2: example `otp_code: "482910"` (6-digit), 120s expiry, 60s resend interval, 3 requests / 10 minutes, 5 attempts → 10-minute block, 86400s (`expires_in`) token.
- `scripts/operational_config.py`: `OTP_CODE_LENGTH = 6`, `OTP_TTL_SECONDS = 120`, `OTP_MAX_ATTEMPTS = 5`, `OTP_LOCKOUT_MINUTES = 10` (runtime values; the shipped `request_otp` generates a 6-digit code).
- Resend interval: only `API_Contracts.md` states one (60s); no other authority. Rate-limit window: 5 min (Technical Spec) vs 10 min (API Contract).

```text
CONTRACT BLOCKER — AUTH OTP POLICY
Authority A: 06_PRODUCT/Technical_Architecture_Spec.md §3 (4 digits, 3/5min, 15min access + 30d refresh)
Authority B: 06_PRODUCT/API_Contracts.md §7 (6-digit example, 3/10min, 60s resend, 86400s token)
Authority C: 08_DATA/IDENTITY_AND_MEMBERSHIP.md §2.5 (5 digits)
Why code cannot safely choose: all three are canonical product/data specs; DECISION_REGISTER.md
contains no OTP decision; the runtime constant (6) is implementation, not product authority,
and standardizing on it would silently ratify one disputed document.
Decision required: Founder/Architect must fix digit count, resend interval, rate-limit window,
and access/refresh token lifetimes in DECISION_REGISTER.md.
```

Auth implementation around these values was **not** invented or changed. Existing OTP runtime behavior is untouched.

## 3. CONTRACT BLOCKER — PRODUCTION RUNTIME STACK

```text
CONTRACT BLOCKER — PRODUCTION RUNTIME STACK
Authority A: 06_PRODUCT/Technical_Architecture_Spec.md §2 approves Node.js 20 + TypeScript +
             NestJS/Fastify as the backend runtime/framework.
Authority B: POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md (canonical pre-UI engineering
             contract) declares transport "framework-neutral until the production API stack is
             selected" and the executable boundary is Python (scripts/application_boundary.py).
Why code cannot safely choose: the two sources have competing authority (product tech-stack
approval vs engineering governance charter) and DECISION_REGISTER.md records no superseding
stack decision (D-015 covers PostgreSQL only).
Decision required: Founder/Architect must either reaffirm Node/NestJS for the transport layer
or supersede Technical_Architecture_Spec.md §2.
```

### Bounded architecture decision record (ADR-B3-01) — factual, no stack choice

1. **Is Node/NestJS an approved future direction?** `UNKNOWN` — Technical_Architecture_Spec.md approves it, but the boundary charter defers stack selection; see blocker above.
2. **Is Python currently the canonical executable domain/runtime?** Yes. `scripts/application_boundary.py` (`POLApplicationBoundary`) is the sole client-facing command/query facade; the full 134-test verification harness executes against PostgreSQL 18 through it.
3. **Which layer owns business logic?** The canonical Python domain services/gateways behind `POLApplicationBoundary` (checkout gateway, RMA, support, feedback, profiles, referral, workers). Transport owns none.
4. **Adapter strategy that avoids duplicating business logic:** a future transport adapter (whatever the stack) must be a thin translation layer: transport payload → `ApplicationContext(user_id, organization_id, correlation_id)` → `POLApplicationBoundary` method → canonical domain service → PostgreSQL transaction → outbox → async worker. No business rules in the adapter; no direct domain-table writes; error mapping per `API_APPLICATION_BOUNDARY.md` §6 (`PermissionError`→403, `KeyError`→404, `ValueError`/state→409/422, retryable provider failure→worker retry, permanent provider failure→durable FAILED).
5. **Can an HTTP adapter call `POLApplicationBoundary` safely?** Yes, conditionally: it must (a) derive `organization_id` only from a validated session/membership, never from client body; (b) open one transaction per command; (c) map the error classes above; (d) never import `domain_services` (enforced by `test_canonical_runtime_regressions.py::test_legacy_import_detector_*` and `test_checkout_gateway_contract.py`).

## 4. Route coverage reassessment (AMBER rows)

Classification proposal only: `ROUTE_COVERAGE_MATRIX.md` itself is **not edited** in this batch; each AMBER row below is classified A (can be made GREEN now without a product-policy decision), B (blocked by missing provider/runtime infrastructure) or C (blocked by a missing business/contract decision). Matrix rows may be flipped to GREEN in a future batch only after this record is approved.

| Route | Class | Reason |
|---|---|---|
| Notification → delivery | B | Worker + lease/retry/FAILED semantics are implemented and tested (`provider_delivery_worker.py`), but no real SMS/push provider is configured (`test_route_hardening.py::test_external_provider_configuration_is_explicit` proves unconfigured adapters raise `ProviderConfigurationError`). GREEN requires live provider credentials, not code. |
| Feedback → Admin | A (eligible for GREEN upon approval) | Canonical writer/reader boundary exists (`CanonicalFeedbackService.list_for_admin`) with passing automated route evidence (`test_canonical_feedback.py`, `test_route_hardening.py`): tenant isolation, admin authorization, reply → `FEEDBACK_REPLIED` outbox row. |
| Feedback reply → user | B | Outbox → notification creation is tested, but final user-visible delivery depends on the same unconfigured external delivery infrastructure as row 1. |
| Support lifecycle | A (eligible for GREEN upon approval) | Canonical boundary (`CanonicalSupportService`): tenant-scoped reads, ops-only assignment/transition/internal notes, access audit ledger — all covered by passing tests (`test_route_hardening.py`, `test_support_cases.py`). |
| Returns / RMA | A (eligible for GREEN upon approval) | Tenant-context enforcement, ops role parity, refund two-person control, DB refund invariant, dedupe/outbox — covered by `test_batch2_rma_and_outbox.py` and `test_batch3_contract_matrix.py`. Reverse-logistics physical execution remains operational, not code. |
| Analytics / KPI | B | The business KPI register exists and is canonical (`11_PILOT/KPIs.md`: 12 pilot + 9 catalog KPIs with formulas and Go/No-Go thresholds), and lineage tables exist; what is missing is the async analytics runtime that computes/certifies these metrics from `orders`/`order_groups`/`payments`/`settlements`/`outbox_events` with tested lineage. Infrastructure/runtime gap, not a business decision. |
| External provider delivery | B | Adapter contract exists (`provider_adapters.py`); live provider execution, credentials and backoff behavior are untested against a real provider. |

No AMBER row is claimed GREEN by domain-service existence alone; only rows with passing automated route evidence are marked as GREEN-eligible, and only after approval of this record.

## 5. Simplicity invariants

Verified unchanged: no contract exposes allocation internals, retry leases, provider credentials, worker implementation details or financial custody internals. Enforcement evidence: `test_operational_intelligence.py::test_simplicity_ux_invariants`, `API_APPLICATION_BOUNDARY.md` §9, checkout responses exposing only `order_group_id`/`order_count`/child orders.

## 6. Tests added (Batch 3)

`scripts/test_batch3_contract_matrix.py` — 12 PostgreSQL-backed contract tests:
- state vocabulary lock (lifecycle doc vs migration 001 CHECK);
- API contract `SUBMITTED` example regression;
- DB rejection of `PENDING/PROCESSING/CONFIRMED/COMPLETED` (CheckViolation on `orders_order_status_check`, snapshot unchanged);
- tenant negatives for checkout: wrong org, suspended membership, missing context (all `PermissionError`, zero state change);
- live revalidation negatives: stale price, insufficient stock (rejected pre-reservation, snapshot unchanged);
- illegal RMA transition at the application boundary (`ACCEPTED → REFUNDED` jump rejected, zero refunds created);
- dispute orthogonality; payment-state/custody vocabulary lock.

### Boundary negative-test matrix coverage status (acceptance §6)

Covered by passing PostgreSQL-backed tests: wrong organization, inactive (suspended) membership, missing active context, illegal order state, illegal RMA transition, stale vendor price, insufficient inventory, reservation race (existing `test_postgres_concurrency.py` 1–3), replay idempotency, same key different payload (`test_e2e_mvp_platform.py` fingerprint tests), cross-tenant key misuse (checkout `Idempotency key is already bound to another retailer`).

**Gap — recipient negatives:** the matrix requires wrong-organization / unauthorized-recipient tests at the route level. The outbox recipient policy is verified positively and implicitly (worker rejects events without explicit routing; quarantine path tested), but there is **no dedicated negative test** proving that a recipient from a *wrong organization* is rejected at notification creation. This remains an open item for the next batch (candidate location: `canonical_integration_worker.py` routing assertions in `test_canonical_integration_worker.py`).
