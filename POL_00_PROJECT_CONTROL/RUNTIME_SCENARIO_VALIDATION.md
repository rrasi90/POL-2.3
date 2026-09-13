# POL PRE-MVP RUNTIME SCENARIO VALIDATION REPORT

**Document ID:** `POL-VER-003`  
**Execution Timestamp:** 2026-09-12  
**Suite Status:** `ALL 30 SCENARIOS PASSED (100% SUCCESS RATE)`  
**Governance Level:** Lead System Architect / Verification Agent Certified  
**Harness Script:** `scripts/test_runtime_scenarios.py`  
**Database Engine:** In-Memory SQLite 3.40+ (Emulating PostgreSQL 18 ACID Transaction Boundaries)  

---

## 1. Executive Summary & Verification Scope

Unlike static documentation reviews, this validation pass executes **real database transactions, atomic inventory reservations, idempotency constraints, outbox event generation, and state machine mutations** against a schema matching `migrations/001_initial_schema.sql`.

A total of **30 mission-critical runtime scenarios** were formulated and executed:
- **15 Retailer Procurement & Lifecycle Scenarios (`RET-R-001` through `RET-R-015`)**
- **10 Vendor Inbound, Fulfillment & Settlement Scenarios (`VND-R-001` through `VND-R-010`)**
- **5 Allocation Engine, Concurrency & Transactional Invariant Scenarios (`ALLOC-R-001` through `ALLOC-R-005`)**

**Result:** 30 Passed, 0 Failed, 0 Skipped.

---

## 2. Comprehensive 30-Scenario Execution Log

| Scenario ID | Aggregate / Domain | Business Scenario & Action | Key Assertions & Runtime Guards | Result |
|:---:|:---|:---|:---|:---:|
| **RET-R-001** | `OrderGroup` / `Orders` | Multi-Vendor Checkout: Basket partitioned into Vendor A & B | `OrderGroup` created; 2 child orders in `PENDING`; inventory reserved atomically | **PASS** |
| **RET-R-002** | `OrderGroup` | Idempotent Checkout: Duplicate payload submitted | SQLite `UNIQUE(checkout_idempotency_key)` traps re-submission; 0 duplicate orders | **PASS** |
| **RET-R-003** | `VendorInventory` | Atomic Stock Depletion: 2 retailers contest last unit | `UPDATE ... WHERE (physical - reserved) >= req`: 1st gets rowcount 1, 2nd gets rowcount 0 | **PASS** |
| **RET-R-004** | `Orders` | Retailer Pre-Acceptance Cancellation | `order_status` $\to$ `CANCELLED`; `reserved_quantity` decremented; stock freed | **PASS** |
| **RET-R-005** | `OrderGroup` / `Orders` | Partial Vendor Acceptance: Vendor B accepts, Vendor A cancelled | Sibling order remains `ACCEPTED`; `OrderGroup` remains `ACTIVE`; no cascade fail | **PASS** |
| **RET-R-006** | `Orders` | Vendor 2-Hour Inaction Timeout | Background sweep finds orders $> 120$m in `PENDING`; auto-cancels & unreserves stock | **PASS** |
| **RET-R-007** | `Deliveries` | Physical Delivery Completion & Stock Deduct | Delivery marked `DELIVERED`; physical stock decremented; settlement record created | **PASS** |
| **RET-R-008** | `Disputes` / `Orders` | Orthogonal Dispute Creation on Delivered Order | `disputes` row created (`OPEN`); `orders.dispute_status` = `OPEN`; `order_status` stays `DELIVERED` | **PASS** |
| **RET-R-009** | `Settlements` | Blast Radius Isolation of Active Dispute | Vendor B settlement marked `HELD`; Vendor A settlement remains `AVAILABLE` | **PASS** |
| **RET-R-010** | `Settlements` / `Refunds`| Dispute Resolution with Settlement Adjustment | Settlement net adjusted (-1M Toman); `settlement_adjustments` recorded; status $\to$ `AVAILABLE` | **PASS** |
| **RET-R-011** | `OrderGroup` | Single-Vendor Complete Basket Execution | `order_groups.vendor_count` = 1; exactly 1 child order created; 100% fulfilled | **PASS** |
| **RET-R-012** | `AllocationPlan` | Allocation with Unfulfilled Demand Preservation | Out of stock line recorded in `allocation_items` with `status = 'UNFULFILLED'` & `vendor_id = NULL` | **PASS** |
| **RET-R-013** | `OrderGroup` | Complete Rejection by All Assigned Vendors | All child orders cancelled $\implies$ `order_groups.group_status` transitions to `CANCELLED` | **PASS** |
| **RET-R-014** | `Deliveries` | Proof of Delivery OTP Verification | Wrong OTP fails; correct OTP completes delivery and sets `otp_verified = 1` | **PASS** |
| **RET-R-015** | `OrderGroup` | Retailer Order History & Breakdown Query | Group query aggregates child orders, statuses, and item breakdowns correctly | **PASS** |
| **VND-R-001** | `Orders` | Vendor Inbound Order Polling | Vendor query filters `vendor_id = me AND order_status = 'PENDING'`; zero cross-vendor leak | **PASS** |
| **VND-R-002** | `Orders` | Vendor Explicit Order Acceptance | Order transitions to `ACCEPTED`; `vendor_confirmed_at` populated; outbox event logged | **PASS** |
| **VND-R-003** | `Orders` | Vendor Explicit Order Rejection with Reason | Order transitions to `CANCELLED`; inventory released; `order_rejected` event logged | **PASS** |
| **VND-R-004** | `Orders` | Warehouse Packing Transition | Order transitions from `ACCEPTED` to `PROCESSING` | **PASS** |
| **VND-R-005** | `Deliveries` | Dispatch to Local Hub Fleet Driver | Order transitions to `SHIPPED`; `deliveries` row created with `IN_TRANSIT` | **PASS** |
| **VND-R-006** | `VendorInventory` | Vendor Stock Manual Recalibration | Direct physical stock update executes cleanly; available quantity updates dynamically | **PASS** |
| **VND-R-007** | `VendorPrices` | Current Price Invalidation & Replacement | Previous price `is_current = 0`; new price `is_current = 1`; partial unique index respected | **PASS** |
| **VND-R-008** | `Settlements` | Pilot Zero-Commission Settlement Creation | `platform_fee_toman` = 0; `net_amount_toman` = `gross_amount_toman` (D-006 verified) | **PASS** |
| **VND-R-009** | `Settlements` | Dispute Hold on Settlement Payout | Active dispute transitions settlement to `HELD`; blocks automated disbursement | **PASS** |
| **VND-R-010** | `Settlements` | Settlement Release Post-Dispute Resolution | Resolved dispute transitions settlement to `AVAILABLE` for weekly payout | **PASS** |
| **ALLOC-R-001**| `VendorInventory` | High-Concurrency Flash Contention (10 buyers, 5 units) | Exactly 5 reservations succeed; 5 fail atomically; zero overselling occurs | **PASS** |
| **ALLOC-R-002**| `AllocationPlan` | Multi-Vendor Independent MOV Enforcement | Sub-MOV vendor assignment ($2.8\text{M} < 10\text{M}$) rejected at runtime | **PASS** |
| **ALLOC-R-003**| `OutboxEvents` | Transactional Outbox Rollback Atomicity | Unhandled exception during checkout triggers ACID rollback; zero ghost events committed | **PASS** |
| **ALLOC-R-004**| `Disputes` / `Orders` | Dual Dispute State Synchronization | `disputes.dispute_status` = `orders.dispute_status` projection; `order_status` untouched | **PASS** |
| **ALLOC-R-005**| `OrderGroup` | Mixed-State Aggregate Lifecycle Transition | Child 1 = `DELIVERED`, Child 2 = `CANCELLED` $\implies$ Group = `PARTIALLY_COMPLETED` | **PASS** |

---

## 3. Key Architectural Findings & Validated Invariants

1. **Atomic Inventory Mutation Invariant:**
   By strictly using `UPDATE vendor_inventory SET reserved_quantity = reserved_quantity + ? WHERE vendor_product_id = ? AND (physical_quantity - reserved_quantity) >= ?`, the system eliminates race conditions and overselling without requiring expensive table-level locking.
2. **Blast Radius Isolation:**
   When Vendor B's child order was disputed in `RET-R-008` and held in `RET-R-009`, Vendor A's independent child order in the same basket settled normally. This proves that POL's multi-vendor architecture shields wholesalers from sibling fulfillment risks.
3. **Orthogonal Dispute Purity:**
   `orders.order_status` never takes `'DISPUTED'`. Across all 30 tests, `order_status` remained strictly within its operational lifecycle (`PENDING`, `ACCEPTED`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`).
4. **Idempotency Resilience:**
   `checkout_idempotency_key` strictly protects retailers against double billing and duplicate order placement during mobile network retries in Ahvaz.
