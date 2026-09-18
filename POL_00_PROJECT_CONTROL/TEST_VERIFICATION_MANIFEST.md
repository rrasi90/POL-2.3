# POL Platform Test Verification Manifest

**Document ID:** `POL-TEST-MANIFEST-v1.0`  
**Date:** September 14, 2026  
**Latest baseline amendment:** 2026-09-18 — Stage 01
**Status:** **ACTIVE / CANONICAL**  
**Target Engine:** PostgreSQL 18.x (Native Windows / Docker `postgres:18-alpine`)  
**Python Runtime:** Python 3.11+ | pytest 8.0+ | psycopg2-binary 2.9.9+  

---

## 1. Executive Summary

This manifest is the authoritative, definitive registry of all test suites, verification scripts, and machine-readable evidence generators for the POL B2B FMCG Middleware Platform.

Every claim made in the platform documentation or engineering reports maps directly to an executable test suite registered in this manifest.

### 2.1 Current execution baseline — 2026-09-18
- Repository branch: `research-hardening-2026-09-14`
- PR #1 current head at snapshot: `e6484daf9f0926b807577c71477d8f1405c24a3e`
- Latest completed verification run observed on that head: Run #333.
- CI checkout executed the PR merge ref; machine-readable artifact recorded merge commit `7bf440dd55d300253d099c6f70c5c76973bd8e25`.
- PostgreSQL: 18.6; public base-table count: **93**.
- Test collection: **209**; passed **170**; failed **39**; skipped **0**; overall **FAILED**.
- Environment/bootstrap verifier step: **success**.
- Therefore the repository is **not CI_VERIFIED** at this snapshot. No `209/209` or equivalent green claim is valid.
- Failure families in Run #333: Batch 2 RMA/outbox (15), Batch 3 contract matrix (5), E2E MVP platform (14), vendor-acceptance-timeout (5).


```text
Claim in Architecture / Spec
            ↓
Test Module in Manifest
            ↓
Local PostgreSQL 18 Execution (RUNTIME_VERIFIED)
            ↓
GitHub Actions Clean Environment (CI_VERIFIED)
            ↓
Machine-Readable Artifact: artifacts/pol-test-results.json
```

---

## 2. Verification Taxonomy & Standards

| Status Label | Criteria | Required Evidence |
| :--- | :--- | :--- |
| **`STATIC_VERIFIED`** | Code/schema structure, contracts, and datasets pass without DB | AST / Regex / File parsing passes |
| **`RUNTIME_VERIFIED`** | Tests executed against real, live PostgreSQL 18 database | 0 failures, 0 warnings, real transactions |
| **`CI_VERIFIED`** | Reproducible execution in clean GitHub Actions runner | Green workflow run on `main` branch |
| **`PARTIALLY_VERIFIED`**| Verified with caveats or mocks | Documented known limitations |

---

## 3. Automation Tooling Registry

### 3.1. Environment & Bootstrap Verifier (`scripts/verify_environment.py`)
- **Purpose:** Smoke and sanity validator for local and CI environments before running test suites.
- **Checks:**
  1. Python runtime version `>= 3.11`.
  2. Python dependency availability (`psycopg2`, `pytest`).
  3. Complete SQL migration chain, dynamically discovered by `scripts/migration_runner.py` (current repository range: `001` → `028`).
  4. PostgreSQL 18 connection on port 5432/5433 (via `POL_PG_PORT` or `PGPORT`).
  5. Target database schema integrity (current CI baseline: 93 public base tables).
  6. Trigger integrity (`trg_enforce_org_membership_role_invariant`).
- **CLI Commands:**
  ```bash
  python scripts/verify_environment.py
  python scripts/verify_environment.py --json
  ```
- **Exit Code:** `0` on success, `1` on any failure.

### 3.2. Canonical Migration Runner (`scripts/migration_runner.py`)
- **Purpose:** Dynamically discovers and applies SQL migrations in strict alphanumeric order (`001` -> `002` -> `003` -> ...).
- **Guarantees:**
  - Transactional DDL execution (`BEGIN ... COMMIT`).
  - Safety check prohibiting destructive drops on non-test databases.
  - Returns ordered applied list and verified active table count.
- **CLI Command:**
  ```bash
  python scripts/migration_runner.py
  ```

### 3.3. Test Runner & Machine-Readable Artifact Generator (`scripts/run_verification_suite.py`)
- **Purpose:** Runs the entire test suite via pytest, captures per-test execution telemetry, and generates `artifacts/pol-test-results.json`.
- **Output Artifact:** `artifacts/pol-test-results.json` containing:
  - Git commit hash, branch, dirty flag
  - Python version & executable path
  - PostgreSQL version & active table count
  - Total collected, passed, failed, skipped, and duration
  - Array of individual test results (`nodeid`, `outcome`, `duration`)
- **CLI Command:**
  ```bash
  python scripts/run_verification_suite.py
  ```

---

## 4. Test Suites Master Catalog (static contract index; execution inventory is dynamic)

| # | Suite File | Tests | Category | DB Req | Target Domain & Invariants Verified |
| :-: | :--- | :-: | :---: | :---: | :--- |
| **01** | `scripts/test_postgres_migrations.py` | 1 | MIGRATION | Real PG 18 | Migration chain integrity; full numbered chain (`001` → current) + incremental upgrade |
| **02** | `scripts/test_postgres_runtime.py` | 1 | RUNTIME | Real PG 18 | 33 Mission-Critical Runtime Scenarios (15 Retailer, 10 Vendor, 8 Allocation/Gov) |
| **03** | `scripts/test_identity_tenant_isolation.py` | 6 | IAM/ISOLATION | Real PG 18 | Multi-org tenant boundaries; Section 11 role matrix; Section 13 non-authoritative `users.role`; Section 14 multi-org sessions; Section 15 legacy links; Section 16 negative cross-tenant attack matrix |
| **04** | `scripts/test_postgres_concurrency.py` | 9 | CONCURRENCY | Real PG 18 | 9 ACID race scenarios: inventory race, duplicate checkout, scarce stock, vendor accept, dispatch creation, refund, dispute creation, vendor isolation, stale price |
| **05** | `scripts/test_admin_authorization.py` | 1 | IAM | Real PG 18 | Admin RBAC permissions, audit logging with correlation IDs, operational exception dashboards |
| **06** | `scripts/test_allocation_engine.py` | 1 | ALGORITHM | Static | 15 allocation algorithm invariants: MOQ, MOV, score-based tie-breaking, coverage metrics |
| **07** | `scripts/test_basket_versioning.py` | 1 | RUNTIME | Real PG 18 | Basket optimistic locking (`version`), allocation plan invalidation on basket mutation |
| **08** | `scripts/test_broadcasts.py` | 1 | RUNTIME | Real PG 18 | Ops admin broadcast publishing, batch inbox item fan-out, recipient list immutability |
| **09** | `scripts/test_current_source_of_truth.py` | 1 | STATIC | Static | Architectural SSoT coherence across 7 architecture documents and contracts |
| **10** | `scripts/test_e2e_mvp_platform.py` | 1 | E2E | Real PG 18 | Master 16-step end-to-end integration lifecycle using `domain_services.py` across all domains |
| **11** | `scripts/test_inventory_reservations.py` | 1 | RUNTIME | Real PG 18 | Stock reservation state machine, active reservation partial index, over-allocation prevention |
| **12** | `scripts/test_invoice_access.py` | 1 | ISOLATION | Real PG 18 | Separate invoice entities, multi-vendor split order invoices, financial invariant (`total = SUM(items)`), tenant visibility |
| **13** | `scripts/test_notification_event_matrix.py` | 1 | STATIC | Static | Notification event matrix verification against domain trigger catalog |
| **14** | `scripts/test_notifications.py` | 1 | RUNTIME | Real PG 18 | Transactional outbox event publishing, worker dispatch, user notification preferences |
| **15** | `scripts/test_pre_mvp_scenarios.py` | 1 | STATIC | Static | 11 static scenario invariants and state transition rules |
| **16** | `scripts/test_runtime_scenarios.py` | 1 | MOCK RUNTIME| In-Memory | 30 mock transactional runtime scenarios for rapid local testing loops |
| **17** | `scripts/test_sla_calendar.py` | 1 | RUNTIME | Static | Ahvaz business calendar, Friday/holiday exclusions, vendor acceptance SLA deadlines |
| **18** | `scripts/test_support_cases.py` | 1 | RUNTIME | Real PG 18 | Customer support case lifecycle (`OPEN` -> `CLOSED`), threaded messages, orthogonal separation from financial disputes |
| **19** | `scripts/test_verification_mutations.py` | 6 | ADVERSARIAL | Real PG 18 | 6 adversarial mutations: dataset count, partial unique index, SKU uniqueness, `DISPUTED` enum in `orders`, carton-only API, multi-packaging offers |
| **20** | `scripts/test_operational_intelligence.py` | 10 | OP_INTEL | Real PG 18 | Daily 1-tap confirmation, delta updates, reminder deduplication, missed decay, feedback submission & triage, cross-tenant isolation, pre-commit price & stock revalidation, simplicity UX contracts |

---

## 5. Detailed Test Suite Specifications

### Suite 03: `scripts/test_identity_tenant_isolation.py` (6 Tests)
- **Commands:** `pytest scripts/test_identity_tenant_isolation.py -v`
- **Invariants Tested:**
  1. `test_tenant_isolation`: Verifies organizations, memberships, duplicate membership constraint (`uq_org_user`), basic basket scoping, session lifecycle (`ACTIVE` -> `REVOKED`), OTP brute-force defense (5 failed attempts -> `BLOCKED`).
  2. `test_section_11_role_org_matrix`: Asserts valid role assignments succeed (7 cases) and invalid combinations (10 cases) are rejected by `trg_enforce_org_membership_role_invariant`.
  3. `test_section_13_users_role_non_authoritative`: Proves changing `users.role` has 0 effect on authorization; revoked user is denied even with `users.role = 'ADMIN_SUPER'`.
  4. `test_section_14_multi_organization_runtime`: Single user holding memberships across multiple organizations; active session context strictly isolates data; membership revocation causes immediate cutoff.
  5. `test_section_15_legacy_actor_links`: Proves `retailers.organization_id` and `vendors.organization_id` are authoritative; multiple actors can share legacy `user_id` without unique collision.
  6. `test_section_16_cross_tenant_negative_matrix`: Comprehensive cross-domain negative attack matrix:
     - Invoices: Org A querying/mutating Org B invoices returns `None` / 0 rows modified.
     - Orders: Org A querying/mutating Org B orders returns `None` / 0 rows modified.
     - Inventory: Vendor 1 modifying Vendor 2 stock or price returns 0 rows modified.
     - Support: Org A querying or posting to Org B support cases returns `None` / 0 rows inserted.
     - Inbox: User A querying or marking User B inbox item returns `None` / 0 rows modified.

### Suite 04: `scripts/test_postgres_concurrency.py` (9 Tests)
- **Commands:** `pytest scripts/test_postgres_concurrency.py -v`
- **Invariants Tested:**
  1. `test_concurrency_1_inventory_race`: 5 threads competing for 1 scarce physical stock item -> exactly 1 succeeds, 4 fail safely.
  2. `test_concurrency_2_duplicate_checkout_same_key`: Identical idempotency key submitted in parallel -> exactly 1 creates order, other caught by unique constraint.
  3. `test_concurrency_3_checkout_different_keys_scarce_stock`: Multiple checkouts with distinct idempotency keys but scarce stock -> no overselling.
  4. `test_concurrency_4_vendor_accept_race`: Competing vendor accept calls -> exactly 1 transitions order.
  5. `test_concurrency_5_dispatch_creation_race`: Competing dispatch creations -> exactly 1 delivery record.
  6. `test_concurrency_6_refund_race`: Parallel refund requests -> idempotent single execution.
  7. `test_concurrency_7_dispute_creation_race`: Duplicate dispute attempts on same order -> exactly 1 dispute created.
  8. `test_concurrency_8_multi_vendor_dispute_isolation`: Dispute on Vendor B does not block settlement calculation on Vendor A.
  9. `test_concurrency_9_stale_state_price_change`: Vendor price changes while basket checkout is pending -> stale checkout rejected or recalculated.

---

## 6. Continuous Integration (CI) Specifications

- **Workflow File:** `.github/workflows/pol-verification.yml`
- **Trigger:** `push` and `pull_request` on `main`.
- **Runner:** `ubuntu-latest` with container service `postgres:18-alpine`.
- **Execution Sequence in CI:**
  1. Checkout code (`actions/checkout@v4`).
  2. Setup Python 3.11 (`actions/setup-python@v5`).
  3. Install dependencies (`pip install -r requirements-dev.txt`).
  4. Apply migration chain (`python scripts/migration_runner.py`).
  5. Verify environment & schema (`python scripts/verify_environment.py --json`).
  6. Execute full verification suite (`python scripts/run_verification_suite.py`).
  7. Upload artifact (`actions/upload-artifact@v4`).

---

## 7. Execution Runbook

To reproduce full verification on any machine:

```bash
# 1. Verify dependencies
pip install -r requirements-dev.txt

# 2. Verify environment & database readiness
python scripts/verify_environment.py

# 3. Apply migrations to pol_test
python scripts/migration_runner.py

# 4. Execute test suite and generate machine-readable artifact
python scripts/run_verification_suite.py

# 5. Inspect generated machine-readable artifact
cat artifacts/pol-test-results.json
```
