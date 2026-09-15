# POL CURRENT SOURCE OF TRUTH & REPOSITORY GOVERNANCE

**Document ID:** `POL-GOV-001`  
**Version:** 1.1 (Canonical)  
**Status:** `LOCKED / OFFICIAL GOVERNANCE CHARTER`  
**Effective Milestone:** Sprint 0 & MVP v1.0  
**Last Audit:** 2026-09-16  

## 1. Authority hierarchy

The repository must have one authoritative decision source and explicit domain contracts. In a conflict, use the following order:

1. `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` — founder/architect decisions.
2. `POL_00_PROJECT_CONTROL/CERTIFICATION_ADDENDUM_2026-09-14.md` — current CI/runtime certification boundary.
3. Current product, domain, data, API and operational contracts listed below.
4. Historical audit reports and exploratory documents are evidence only and must not be used as implementation instructions.

## 2. Canonical decisions

- **D-001:** Ahvaz, specifically the 61-hectare Wholesalers Hub, is the Year-1 launch/pilot geography.
- **D-002:** Pilot duration is 90 calendar days / 12 weeks.
- **D-003:** Historical single-vendor basket decision is superseded.
- **D-014:** MVP v1.0 uses one unified retailer basket with deterministic multi-vendor allocation and minimum necessary vendor fragmentation. Each basket line is assigned to at most one vendor; quantity splitting of a single line across vendors is not supported in MVP.
- **D-005:** Future vendor count is open; no hardcoded maximum of two vendors.
- **D-006:** Pilot vendor take rate is 0%.
- **D-007:** Post-pilot 1–3% category-tiered take rate remains a hypothesis to validate.
- **D-008:** POL owns no delivery fleet; pilot fulfillment uses local cluster logistics.
- **D-009:** Paid advertising is deferred to H2 Year 4.
- **D-010:** Order hierarchy is `Basket -> AllocationPlan -> OrderGroup -> Order -> OrderItem`.
- **D-011:** User-facing monetary amounts are Tomans; USD is for internal analytical/financial modeling.
- **D-012:** Master Product identity is separate from Vendor Product/SKU.
- **D-013:** `Master SKU/backup_no_images.json` is quarantined imported reference data, not live inventory.
- **D-015:** PostgreSQL 18 is the canonical database engine; SQLite is auxiliary only for isolated fast-path tests.

## 3. Canonical IAM vocabulary

The physical database and migration chain use these canonical operator roles:

`RETAILER_OWNER`, `RETAILER_STAFF`, `VENDOR_OWNER`, `VENDOR_STAFF`, `OPS_AGENT`, `ADMIN_SUPER`, `FIELD_ACTIVATOR`.

`SUPER_ADMIN` and `OPS_ADMIN` may exist only as legacy aliases accepted by the reconciliation migration and must never be treated as a separate canonical role vocabulary. Runtime authorization is based on `organization_memberships.role` scoped by `user_sessions.active_organization_id`; `users.role` is deprecated and non-authoritative.

## 4. Canonical product and runtime documents

- Product scope: `06_PRODUCT/MVP_Definition.md`, `06_PRODUCT/PRD.md`, `06_PRODUCT/Order_Lifecycle.md`, `06_PRODUCT/Test_Specification.md`.
- Domain/data: `08_DATA/DOMAIN_MODEL.md`, `08_DATA/Data_Schema.md`, `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md`.
- API: `06_PRODUCT/API_Contracts.md`, `POL_00_PROJECT_CONTROL/CANONICAL_CONTRACT_MATRIX.md`.
- Allocation: `07_ALGORITHMS/MVP_MULTI_VENDOR_ALLOCATION.md`.
- Operations: `09_OPERATIONS/*` and `11_PILOT/*`.
- Database: the complete ordered migration chain `migrations/001_initial_schema.sql` through `migrations/004_operational_intelligence.sql`, plus any later migration added through the same ordered mechanism.

## 5. Database truth

The current migration chain creates/extends a runtime schema observed at **62 base tables** in the latest recorded verification artifact. Migration 004 adds six tables and extends existing inventory/price structures. Therefore any document claiming a canonical total of 56 tables or a migration chain ending at 003 is historical/stale and must not be used as the current schema count.

The recorded CI evidence in `CERTIFICATION_ADDENDUM_2026-09-14.md` reports PostgreSQL **18.6**, 62 base tables, and 47/47 automated tests passed for workflow run `34818313995` on commit `f3a65a3060d2f09ca7bf9cbd1b270b13f539ca2f`. The current `main` tip is later than that tested commit; consequently the CI result certifies that tested commit, not every subsequent commit.

## 6. Runtime certification boundary

`CI_VERIFIED`, `DATABASE_RUNTIME_VERIFIED`, and `DOMAIN_RUNTIME_VERIFIED` are established for the recorded CI run. `FULL_APPLICATION_RUNTIME_VERIFIED` is **not established** because the repository does not yet contain and exercise the complete Android/PWA/API/external-integration production stack.

The canonical checkout entry point is `scripts/checkout_gateway.py::CanonicalCheckoutGateway`. New application callers must use the gateway. `CheckoutService` remains only for compatibility until real application callers have migrated.

## 7. Historical-document rule

Historical reports may be retained for traceability, but any document containing superseded architecture, obsolete schema counts, obsolete role names, or old certification claims must carry a `HISTORICAL / SUPERSEDED` banner and must not be referenced as a current implementation contract.

## 8. Change management

No parallel decision register or competing certification register is permitted. Changes to locked decisions require empirical pilot evidence, architecture review, and a synchronized update of downstream canonical contracts. Code and schema changes must be accompanied by regression tests that prove the affected invariant.
