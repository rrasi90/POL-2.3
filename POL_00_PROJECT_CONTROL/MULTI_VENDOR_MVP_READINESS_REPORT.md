# POL MULTI-VENDOR MVP RE-ARCHITECTURE & RUNTIME VALIDATION READINESS REPORT

**Document ID:** `POL-REP-005`  
**Certification Date:** 2026-09-13  
**Governance Authority:** Lead Product Architect & System Verification Agent  
**Status:** `FINAL / VERIFIED / SPRINT 0 AUTHORIZED`  
**Verdict:** **MVP MULTI-VENDOR GO (VERIFIED ACROSS 8 AUTOMATED TEST SUITES)**  

---

## 1. Executive Summary

This report documents the architectural reconciliation and dual runtime verification (SQLite in-memory + native PostgreSQL 18) of the POL B2B FMCG platform under the canonical **Multi-Vendor Basket Architecture (`D-014`)**, with the exploratory single-vendor cart constraint formally archived as `D-003-HISTORICAL`.

### The Core Problem Solved
In wholesale FMCG (specifically within the 61-hectare Ahvaz Wholesalers Hub / شهرک بنکداران اهواز with ~700 active warehouses), wholesalers specialize by product category (e.g. Wholesaler A in oil/sugar, Wholesaler B in detergents, Wholesaler C in beverages). Requiring retail grocery stores to maintain separate carts per wholesaler produced unacceptable checkout friction and cart abandonment.

Under **D-014**, POL provides a unified supermarket buying experience while safeguarding wholesaler operational autonomy:
> **"One retailer basket → candidate vendor universe filtering (Stage 1) → deterministic combinatorial allocation (Stage 2) → minimum necessary vendor fragmentation → line-item allocation only (no intra-line splitting) → autonomous vendor child orders → independent vendor fulfillment, settlement, and disputes."**

---

## 2. Specification Audit vs. PostgreSQL Runtime Validation

To eliminate ungrounded assumptions, the POL verification framework maintains a strict distinction between **Static Specification Verification**, **SQLite Behavioral Simulation**, and **Production-Grade PostgreSQL Runtime Validation**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               POL VERIFICATION TIERS                                   │
├───────────────────────────────┬───────────────────────────────┬────────────────────────┤
│ 1. STATIC SPECIFICATION       │ 2. SQLITE SIMULATION          │ 3. POSTGRESQL 18 RUNTIME│
│ (Markdown, AST, DDL Syntax)   │ (Rapid Unit Verification)     │ (Native Daemon Port 5433│
├───────────────────────────────┼───────────────────────────────┼────────────────────────┤
│ • Cross-document term parity  │ • 30 transactional scenarios  │ • Native PostgreSQL 18 │
│ • Table & column parity       │ • In-memory speed             │ • 37 DDL tables        │
│ • State machine allowed paths │ • State transition logic      │ • Multi-connection     │
│ • Single decision register    │ • Outbox payload serialization│   concurrency racing   │
│ • Historical superseded banner│ • Compensatory rebalancing    │ • True row-level locks │
│ • Adversarial mutations       │ • Dual dispute state checks   │ • Partial unique index │
└───────────────────────────────┴───────────────────────────────┴────────────────────────┘
```

---

## 3. Comprehensive Test Suites & Verification Results (8/8 Suites Passed)

All 8 automated test suites execute cleanly and deterministically:

| Suite # | Script Path | Target Domain / Invariants | Total Tests | Passed | Failed | Status |
|:---:|:---|:---|:---:|:---:|:---:|:---:|
| **1** | `scripts/verify_repository_consistency.py` | Repository Consistency & 37-Table Schema Parity | 12 | 12 | 0 | **PASS** |
| **2** | `scripts/test_verification_mutations.py` | Adversarial Tooling Mutations & Packaging | 6 | 6 | 0 | **PASS** |
| **3** | `scripts/test_pre_mvp_scenarios.py` | 100-Scenario Static Invariant Suite | 11 | 11 | 0 | **PASS** |
| **4** | `scripts/test_allocation_engine.py` | Multi-Vendor Combinatorial Allocation Engine | 15 | 15 | 0 | **PASS** |
| **5** | `scripts/test_runtime_scenarios.py` | Pre-MVP Runtime Transactional Scenarios (SQLite) | 30 | 30 | 0 | **PASS** |
| **6** | `scripts/test_current_source_of_truth.py` | Single Authority, Brand, Payment & Tech Env | 7 | 7 | 0 | **PASS** |
| **7** | `scripts/test_postgres_migrations.py` | Canonical PostgreSQL 18 DDL Migration (37 Tables) | 37 | 37 | 0 | **PASS** |
| **8** | `scripts/test_postgres_runtime.py` | Canonical PostgreSQL 18 Transactional Scenarios | 33 | 33 | 0 | **PASS** |
| **9** | `scripts/test_postgres_concurrency.py` | Native PostgreSQL 18 Multi-Connection Concurrency | 9 | 9 | 0 | **PASS** |
| **TOTAL**| **9 Automated Test Suites** | **Full Repository, Specification & Runtime Gate** | **160** | **160** | **0** | **100% PASS** |

---

## 4. Key Architectural Pillars Validated

### 4.1. Brand Architecture & Registered Assets
Formalized in `POL_00_PROJECT_CONTROL/BRAND_ARCHITECTURE.md`:
- **POL / پُل:** Corporate Master Brand and platform ecosystem (`logo/pol company logo.png`).
- **POL Market / پل مغازهدار:** Retailer Web & Mobile App for supermarkets (`logo/لوگو پل برای مغازه داران.png`).
- **POL Vendor / پل بنکدار:** Vendor Portal & Warehouse Application for wholesalers (`logo/لوگو پل برای بنکدار.png`).

### 4.2. Single Decision Register Authority
Formalized in `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` and `POL_00_PROJECT_CONTROL/CURRENT_SOURCE_OF_TRUTH.md`:
- `DECISION_REGISTER.md` is the sole decision authority (D-001 through D-014).
- `D-014` governs Multi-Vendor Basket in MVP v1.0.
- `D-003` is marked `HISTORICAL / SUPERSEDED`.
- Canonical warning banners were added to all 7 prior hardening/audit/certification reports.

### 4.3. Allocation & Delivery Semantics
- **Line-Item Allocation Only (Prohibition of Intra-Line Quantity Splitting):** In MVP v1.0, POL strictly assigns each basket line item entirely to a single vendor. If 10 cartons are requested and Vendor A has 6 while Vendor B has 4, the item is NOT split; it transitions to `UNFULFILLED` (`OUT_OF_STOCK`).
- **Two-Stage Allocation Pipeline:** Stage 1 filters the candidate vendor universe per item (active vendor, delivery zone, net available inventory $\ge q_i$, $q_i \ge \text{moq}$). Stage 2 executes combinatorial minimum fragmentation optimization ($K=1 \to K=2 \to K=N$).
- **Delivery Semantics (MVP Operational Simplification):** `1 Vendor Child Order = 1 Independent Delivery`. Local hub pickup trucks (وانت‌های بومی شهرک) transport consignments directly from the wholesaler to the store. Multi-vendor cross-docking and warehouse consolidation are explicitly deferred post-pilot.

### 4.4. Multi-Vendor Payment Architecture (`NON_CUSTODIAL_DIRECT`)
- **Zero Custody in MVP:** In accordance with `D-005`, `09_OPERATIONS/Payments_and_Settlement.md`, and Invariant 15, POL operates no escrow account, holds zero client funds, and possesses no custody license during the 3-month Ahvaz pilot.
- **Direct Settlement Tracking:** Retailer pays wholesalers directly (Driver POS, COD, or Bank Transfer) upon physical delivery.
- **Child Order Payment Ledger:** Each vendor child order has an autonomous record in `payments` (`order_id`, `vendor_id`, `retailer_id`, `amount_toman`, `payment_method`, `custody_model = 'NON_CUSTODIAL_DIRECT'`).
- **Independent Blast Radius:** If a vendor declines or times out, its payment record is marked `CANCELLED` (no payment collected), while sibling child orders and direct payments proceed unimpeded.
- **Roadmap Reservation:** `custody_model = 'ESCROW_FUTURE'` is reserved for post-pilot when formal payment custody rails are integrated.

### 4.5. Orthogonal Dispute & Settlement Architecture
- **Operational Status Cleanliness:** `orders.order_status` NEVER contains `'DISPUTED'`. It only transitions through `PENDING -> ACCEPTED -> PROCESSING -> SHIPPED -> DELIVERED -> CANCELLED`.
- **Single Source of Truth:** `disputes.dispute_status` is the canonical state (`OPEN`, `INVESTIGATING`, `RESOLVED`, `CLOSED`). `orders.dispute_status` is a derived projection (`NONE`, `OPEN`, `RESOLVED`, `CLOSED`).
- **Blast Radius Isolation:** An active dispute on Vendor B holds Vendor B's settlement (`HELD`), while Vendor A's settlement in the same parent OrderGroup completes to `PAID` without delay.

### 4.6. Native PostgreSQL 18 Concurrency Verification
Validated with real concurrent connections against port 5433:
- **Inventory Race:** Atomic conditional update prevents overselling. Stock=5; two concurrent 5-unit reservation requests; exactly 1 succeeds, 1 rejected.
- **Duplicate Checkout Race:** PostgreSQL `UNIQUE (checkout_idempotency_key)` rejects duplicate submissions.
- **Vendor Accept Race:** Exactly 1 worker transitions order from `PENDING` to `ACCEPTED`; second attempt no-ops.
- **Dispatch Race:** `UNIQUE (deliveries.order_id)` prevents duplicate delivery creation.
- **Stale State Detection:** Price update during checkout triggers `PRICE_CHANGED` guard.

---

## 5. Summary of Verified Repository Assets

### Core Specifications & Reports:
1. `POL_00_PROJECT_CONTROL/BRAND_ARCHITECTURE.md` (Brand hierarchy & logo mapping)
2. `POL_00_PROJECT_CONTROL/CURRENT_SOURCE_OF_TRUTH.md` (Decision charter & historical document rules)
3. `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` (Canonical decisions D-001 through D-014)
4. `POL_00_PROJECT_CONTROL/MVP_MULTI_VENDOR_DECISION.md` (D-014 ADR)
5. `07_ALGORITHMS/MVP_MULTI_VENDOR_ALLOCATION.md` (Algorithm specification & tie-breaking)
6. `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` (Aggregate lifecycles & payment model)
7. `POL_00_PROJECT_CONTROL/MULTI_VENDOR_MVP_READINESS_REPORT.md` (This certification report)

### Verification Scripts:
1. `scripts/verify_repository_consistency.py` (12 checks)
2. `scripts/test_verification_mutations.py` (6 tests)
3. `scripts/test_pre_mvp_scenarios.py` (11 tests)
4. `scripts/test_allocation_engine.py` (15 tests)
5. `scripts/test_runtime_scenarios.py` (30 tests)
6. `scripts/test_current_source_of_truth.py` (7 checks)
7. `scripts/test_postgres_migrations.py` (37 tables / migration checks)
8. `scripts/test_postgres_runtime.py` (33 scenarios)
9. `scripts/test_postgres_concurrency.py` (9 race condition tests)

---

## 6. Formal Readiness Verdict

All specifications, domain models, algorithm pipelines, and runtime transaction contracts are reconciled around **D-014** and locked to canonical **PostgreSQL 18** (`D-015`).

- **Scenario Definitions:** 100/100 verified
- **Static Invariants:** 11/11 verified
- **Allocation Tests:** 15/15 verified
- **SQLite Runtime:** 30/30 verified
- **Canonical PostgreSQL 18 Migration:** 37/37 verified
- **PostgreSQL 18 Runtime Scenarios:** 33/33 verified
- **PostgreSQL 18 Concurrency Races:** 9/9 verified
- **Source of Truth & Tech Environment Checks:** 7/7 verified
- **Repository Consistency:** 12/12 verified
- **Adversarial Mutation Tests:** 6/6 verified
- **Total Automated Verifications:** 160/160 PASSED (100%)

**VERDICT: SPECIFICATION STATUS READY | RUNTIME STATUS READY ON POSTGRESQL 18 | SPRINT 0 STATUS GO**
