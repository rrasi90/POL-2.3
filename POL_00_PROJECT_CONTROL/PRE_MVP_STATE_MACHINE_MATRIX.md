# POL — PRE-MVP AGGREGATE STATE MACHINE MATRIX

**Document ID:** `POL-SMM-001`  
**Status:** `CANONICAL / HARDENED`  
**Governance:** Lead Product Architect & Repository Governance Agent  
**Date:** 2026-09-12  
**Target Architecture:** Event-Driven Transactional Outbox + PostgreSQL 18 DDL  

---

## 1. Overview & Architectural Principles

This document specifies the complete, exhaustive state transition rules for all fourteen (14) core domain aggregates of the POL platform.

### Immutable Principles:
1. **Explicit Forbidden Transitions:** Any state transition not explicitly listed in "Allowed Transitions" is strictly forbidden and must trigger an application-level exception (`InvalidStateTransitionException` / HTTP 409 Conflict) and database state-check guard.
2. **Transactional Outbox Atomicity:** Every state mutation MUST be committed atomically with an `outbox_events` record in the same ACID database transaction.
3. **Idempotency Mandate:** Repeated submissions of the same transition with identical idempotency keys (`Idempotency-Key` header or natural business keys) MUST return the previous successful result without executing duplicate mutations or side effects.
4. **Async Side Effect Decoupling:** External third-party side effects (SMS dispatch, push notifications, analytics) MUST NEVER execute synchronously within the business database transaction.

---

## 2. Exhaustive Aggregate State Transition Tables

### 2.1. Aggregate 1: `Basket` (`baskets`)
- **Initial State:** `ACTIVE`
- **Terminal States:** `CONVERTED_TO_ORDER`, `ABANDONED`

| From State | Allowed To State | Actor | Triggering API / Action | Required Fields & Validation | DB Mutation | Domain Event | Notification | Side Effects | Idempotency & Retry Rule |
|---|---|---|---|---|---|---|---|---|---|
| `[*] (None)` | `ACTIVE` | Retailer | `POST /api/v1/baskets` | `retailer_id`, `created_at` | `INSERT INTO baskets` | `basket_created` | None | Initial cart session created | Idempotent per active retailer session |
| `ACTIVE` | `ACTIVE` | Retailer | `POST /api/v1/baskets/items`, `PATCH ...` | `vendor_product_id`, `quantity >= moq` | `INSERT/UPDATE basket_items` | `basket_item_added` / `basket_item_updated` | None | Updates line items and cart subtotal | Upsert on `(basket_id, vendor_product_id)` |
| `ACTIVE` | `CONVERTED_TO_ORDER` | Retailer | `POST /api/v1/checkout` | Valid `allocation_plan_id`, MOV met, all item MOQs met | `UPDATE baskets SET status = 'CONVERTED_TO_ORDER'` | `basket_converted_to_order` | In-app Order Created modal | Locks basket against further edits | Header `Idempotency-Key` required |
| `ACTIVE` | `ABANDONED` | System (Worker) | Background cleanup after 14 days of inactivity | Last updated > 14 days | `UPDATE baskets SET status = 'ABANDONED'` | `basket_abandoned` | Optional push reminder before expiry | Releases cart cache | Scheduled worker job with batch lock |

- **Forbidden Transitions:**
  - `CONVERTED_TO_ORDER -> ACTIVE` (Cannot revive an already checked-out basket; new basket must be created).
  - `CONVERTED_TO_ORDER -> ABANDONED`
  - `ABANDONED -> CONVERTED_TO_ORDER`

---

### 2.2. Aggregate 2: `AllocationPlan` (`allocation_plans`)
- **Initial State:** `DRAFT`
- **Terminal States:** `COMMITTED`, `EXPIRED`, `SUPERSEDED`

| From State | Allowed To State | Actor | Triggering API / Action | Required Fields & Validation | DB Mutation | Domain Event | Notification | Side Effects | Idempotency & Retry Rule |
|---|---|---|---|---|---|---|---|---|---|
| `[*] (None)` | `DRAFT` | System | Cart checkout preview | `basket_id`, `total_amount_toman`, candidate vendors | `INSERT INTO allocation_plans (status='DRAFT')` | `allocation_preview_generated` | None | Candidate scores computed | Cached preview (TTL 10 min) |
| `DRAFT` | `OPTIMIZED` | System | Algorithmic ranking completion | Optimal vendor allocation determined (D-014 heuristic: minimal vendors K>=1, MOV/MOQ enforced), item coverage calculated | `UPDATE allocation_plans SET status='OPTIMIZED'` | `allocation_plan_optimized` | None | Best feasible allocation plan selected | Deterministic calculation |
| `OPTIMIZED` | `COMMITTED` | Retailer | Checkout submit confirmation | Retailer selects optimized plan and confirms | `UPDATE allocation_plans SET status='COMMITTED'` | `allocation_plan_committed` | None | Triggers order generation | Enforced by basket lock |
| `DRAFT / OPTIMIZED` | `EXPIRED` | System | TTL expiry (10 minutes) | Exceeded 10 min without checkout submit | `UPDATE allocation_plans SET status='EXPIRED'` | `allocation_plan_expired` | None | Invalidates stale pricing preview | Read query triggers refresh |
| `OPTIMIZED` | `SUPERSEDED` | Retailer | Basket modified after preview | New item added or quantity changed | `UPDATE allocation_plans SET status='SUPERSEDED'` | `allocation_plan_superseded` | None | Stale plan archived | New plan replaces old plan |

- **Forbidden Transitions:**
  - `COMMITTED -> DRAFT / OPTIMIZED / EXPIRED` (Once committed, plan is immutable).
  - `EXPIRED -> COMMITTED` (Stale allocation plan cannot be checked out; must re-evaluate prices).

---

### 2.3. Aggregate 3: `OrderGroup` (`order_groups`)
- **Initial State:** `ACTIVE`
- **Terminal States:** `COMPLETED`, `CANCELLED`

| From State | Allowed To State | Actor | Triggering API / Action | Required Fields & Validation | DB Mutation | Domain Event | Notification | Side Effects | Idempotency & Retry Rule |
|---|---|---|---|---|---|---|---|---|---|
| `[*] (None)` | `ACTIVE` | System | Checkout execution | `basket_id`, `retailer_id`, `order_count >= 1` | `INSERT INTO order_groups` | `order_group_created` | Push to Retailer | Master container for order fulfillment | Idempotent via checkout key |
| `ACTIVE` | `COMPLETED` | System | All child orders reach `DELIVERED` | `COUNT(orders WHERE status != 'DELIVERED') = 0` | `UPDATE order_groups SET group_status='COMPLETED'` | `order_group_completed` | Push to Retailer | Group fulfillment closed | Evaluated on every child order delivery |
| `ACTIVE` | `PARTIALLY_COMPLETED` | System | At least one child order delivered and one cancelled/rejected (Future N-Vendor) | Mix of `DELIVERED` and `CANCELLED/REJECTED` | `UPDATE order_groups SET group_status='PARTIALLY_COMPLETED'` | `order_group_partially_completed` | Push to Retailer | Financial reconciliation for partial fulfillment | Auto-updated on child state change |
| `ACTIVE` | `CANCELLED` | System | All child orders cancelled or rejected | `COUNT(orders WHERE status != 'CANCELLED' AND status != 'REJECTED') = 0` | `UPDATE order_groups SET group_status='CANCELLED'` | `order_group_cancelled` | Push/SMS to Retailer | Entire group order terminated | Auto-updated on child cancellation |

- **Forbidden Transitions:**
  - `COMPLETED -> ACTIVE / CANCELLED`
  - `CANCELLED -> ACTIVE / COMPLETED`

---

### 2.4. Aggregate 4: `Order` (`orders`)
- **Initial State:** `CREATED` -> `SUBMITTED`
- **Terminal States:** `DELIVERED`, `CANCELLED`, `REJECTED`

| From State | Allowed To State | Actor | Triggering Action | Required Fields & Validation | DB Mutation | Domain Event | Notification | Financial & Inventory Side Effects | Idempotency & Retry Rule |
|---|---|---|---|---|---|---|---|---|---|
| `[*] (None)` | `CREATED` | System | Checkout init | `retailer_id`, `vendor_id`, `total_amount_toman >= MOV` | `INSERT INTO orders (status='CREATED')` | `order_created` | None | Creates order snapshot | Idempotent via `allocation_plan_id` |
| `CREATED` | `SUBMITTED` | Retailer | Checkout submit | Order items validated, all item MOQs met | `UPDATE orders SET order_status='SUBMITTED'` | `order_submitted` | SMS & Push to Vendor | Reserves inventory (`reserved_quantity += Q`); 120-min SLA timer starts | Unique checkout transaction |
| `SUBMITTED` | `ACCEPTED` | Vendor | `POST /api/v1/vendor/orders/{id}/accept` | Full fulfillment confirmed by vendor | `UPDATE orders SET order_status='ACCEPTED'` | `order_accepted` | SMS & Push to Retailer | Stock reservation confirmed; prepares warehouse slip | Idempotent per order ID |
| `SUBMITTED` | `PARTIALLY_ACCEPTED` | Vendor + Retailer | Vendor marks shortage + Retailer approves revised cart | Items shorted, remaining items `>= MOV`, retailer accepts | `UPDATE orders SET order_status='PARTIALLY_ACCEPTED'` | `order_partially_accepted` | SMS to Retailer | Unfulfilled stock reservation released; order total revised | Retailer confirmation signature |
| `SUBMITTED` | `REJECTED` | Vendor | `POST /api/v1/vendor/orders/{id}/reject` | `rejection_reason` mandatory | `UPDATE orders SET order_status='REJECTED'` | `order_rejected` | SMS & Push to Retailer | All stock reservations released; Vendor SLA penalty logged | Idempotent per order ID |
| `SUBMITTED` | `CANCELLED` | System (Timeout) or Retailer | 120 working minutes elapsed OR buyer cancels before acceptance | System timer expiry OR buyer cancellation | `UPDATE orders SET order_status='CANCELLED', rejection_reason='VENDOR_TIMEOUT'` | `order_cancelled` | Push/SMS to Retailer & Vendor | Stock reservation released; Vendor SLA penalized if timeout | System timer job with row lock |
| `ACCEPTED / PARTIALLY_ACCEPTED` | `PREPARING` | Vendor Staff | `POST /api/v1/vendor/orders/{id}/preparing` | Warehouse staff begins picking items | `UPDATE orders SET order_status='PREPARING'` | `order_preparing` | In-app order status update | Warehouse picking slip printed | Idempotent per order ID |
| `PREPARING` | `READY` | Vendor Staff | `POST /api/v1/vendor/orders/{id}/ready` | Packing verified, dispatch stage ready | `UPDATE orders SET order_status='READY'` | `order_ready` | Alert to Cluster Logistics Carrier | Packages sealed | Idempotent per order ID |
| `READY` | `DISPATCHED` | Vendor / Carrier | `POST /api/v1/vendor/orders/{id}/dispatch` | Carrier name, driver name, phone, vehicle plate | `UPDATE orders SET order_status='DISPATCHED'` | `order_dispatched` | SMS to Retailer with driver info | Stock deducted from physical: `physical_quantity -= Q, reserved_quantity -= Q` | Idempotent per order ID |
| `ACCEPTED / READY` | `CANCELLED` | Ops Admin / Mutual | Emergency pre-dispatch cancellation | Formal cancellation reason, operator user ID | `UPDATE orders SET order_status='CANCELLED'` | `order_cancelled` | SMS to both parties | Stock reservation released | Admin permission required |
| `DISPATCHED` | `DELIVERED` | Driver + Retailer | `POST /api/v1/orders/{id}/delivery/confirm` | POD record created, OTP verified | `UPDATE orders SET order_status='DELIVERED'` | `order_delivered` | SMS receipt to Retailer; push to Vendor | Triggers settlement calculation; initiates 4-hour dispute window | OTP code or digital signature |

- **Explicit Forbidden Transitions:**
  - `DELIVERED -> CANCELLED / REJECTED / SUBMITTED / DISPATCHED` (Delivery is terminal).
  - `CANCELLED -> ACCEPTED / PREPARING / DELIVERED` (Cancelled order cannot be revived).
  - `REJECTED -> ACCEPTED / DELIVERED`
  - `SUBMITTED -> DISPATCHED` (Cannot skip acceptance/preparation).
  - `orders.order_status -> DISPUTED` (**CRITICAL FORBIDDEN RULE:** Dispute is tracked orthogonally in `orders.dispute_status` and `disputes` table).

---

### 2.5. Aggregate 5: `OrderItem` (`order_items`)
- **Initial State:** `PENDING`
- **Terminal States:** `FULFILLED`, `SHORTAGE`, `REJECTED`, `DAMAGED`

| From State | Allowed To State | Actor | Triggering Action | Required Fields & Validation | DB Mutation | Domain Event | Side Effects | Idempotency Rule |
|---|---|---|---|---|---|---|---|---|
| `[*] (None)` | `PENDING` | System | Order creation from allocation | `order_id`, `product_id`, `ordered_quantity > 0` | `INSERT INTO order_items` | `order_item_created` | Line snapshot locked | Unique per `(order_id, vendor_product_id)` |
| `PENDING` | `FULFILLED` | Vendor / Driver | Order acceptance & delivery confirmation | Delivered without shortage | `UPDATE order_items SET fulfillment_status='FULFILLED'` | `order_item_fulfilled` | Line amount fully billed | Idempotent |
| `PENDING` | `SHORTAGE` | Vendor (at acceptance) or Retailer (at delivery) | Out of stock or shortage verified | `accepted_quantity < ordered_quantity` | `UPDATE order_items SET fulfillment_status='SHORTAGE'` | `order_item_shortage_recorded` | Billed amount adjusted to accepted qty | Idempotent |
| `PENDING` | `DAMAGED` | Retailer | Doorstep damage inspection | Photo proof + inspector description | `UPDATE order_items SET fulfillment_status='DAMAGED'` | `order_item_damaged_recorded` | Triggers dispute ticket & settlement deduction | Idempotent |
| `PENDING` | `REJECTED` | Retailer | Wrong SKU delivered | Delivered SKU != Ordered SKU snapshot | `UPDATE order_items SET fulfillment_status='REJECTED'` | `order_item_rejected_recorded` | Return with carrier, line amount deducted | Idempotent |

- **Forbidden Transitions:**
  - `FULFILLED -> PENDING`
  - `SHORTAGE / DAMAGED / REJECTED -> PENDING`

---

### 2.6. Aggregate 6: `Delivery` (`deliveries`)
- **Initial State:** `ASSIGNED`
- **Terminal States:** `DELIVERED`, `FAILED`

| From State | Allowed To State | Actor | Triggering Action | Required Fields | DB Mutation | Domain Event | Notification | Side Effects |
|---|---|---|---|---|---|---|---|---|
| `[*] (None)` | `ASSIGNED` | Vendor / Carrier | Order ready for pickup | `carrier_type`, `carrier_name`, `driver_name`, `driver_phone` | `INSERT INTO deliveries` | `delivery_assigned` | Push to Carrier | Driver assigned |
| `ASSIGNED` | `PICKED_UP` | Driver | Carrier collects goods from warehouse | Pickup timestamp | `UPDATE deliveries SET delivery_status='PICKED_UP'` | `delivery_picked_up` | None | Cargo in driver custody |
| `PICKED_UP` | `IN_TRANSIT` | Driver | Truck departs wholesale hub | Departure timestamp | `UPDATE deliveries SET delivery_status='IN_TRANSIT'` | `delivery_in_transit` | SMS to Retailer | Estimated arrival shared |
| `IN_TRANSIT` | `ARRIVED` | Driver | Driver reaches grocery storefront | Arrival GPS/timestamp | `UPDATE deliveries SET delivery_status='ARRIVED'` | `delivery_arrived` | In-app alert to Retailer | Unloading begins |
| `ARRIVED` | `DELIVERED` | Driver + Retailer | OTP verification & cargo receipt | `proof_of_delivery` record created | `UPDATE deliveries SET delivery_status='DELIVERED'` | `delivery_completed` | SMS receipt | Order transitions to `DELIVERED` |
| `ARRIVED / IN_TRANSIT` | `FAILED` | Driver / Retailer | Store closed / doorstep rejection / wrong address | `outcome IN ('STORE_CLOSED', 'REJECTED_AT_DOOR', 'ADDRESS_NOT_FOUND')` | `UPDATE deliveries SET delivery_status='FAILED'` | `delivery_failed` | Alert to Ops Concierge | Cargo returned to vendor warehouse |

- **Forbidden Transitions:**
  - `DELIVERED -> FAILED / IN_TRANSIT / ASSIGNED`
  - `FAILED -> DELIVERED` (Must generate new delivery attempt/record)

---

### 2.7. Aggregate 7: `Payment` (`payments`)
- **Initial State:** `PENDING`
- **Terminal States:** `SUCCESS`, `FAILED`, `CANCELLED`, `REFUNDED`

| From State | Allowed To State | Actor | Triggering Action | Required Fields | DB Mutation | Domain Event | Notification | Side Effects |
|---|---|---|---|---|---|---|---|
| `[*] (None)` | `PENDING` | System | Order checkout creation | `order_id`, `amount_toman > 0`, `payment_method` | `INSERT INTO payments` | `payment_created` | None | Payment ledger entry opened |
| `PENDING` | `INITIATED` | Retailer | Gateway redirect or POS swipe | `payment_method IN ('ONLINE_GATEWAY', 'POS_ON_DELIVERY', 'CASH_ON_DELIVERY')` | `UPDATE payments SET payment_status='INITIATED'` | `payment_attempted` | None | Logs `payment_attempts` |
| `INITIATED / PENDING` | `SUCCESS` | Driver / Gateway | Gateway callback or driver marks cash/POS collected | `reference_number`, `paid_at` | `UPDATE payments SET payment_status='SUCCESS'` | `payment_completed` | SMS receipt | Invoice marked paid; enables settlement release |
| `INITIATED` | `FAILED` | Driver / Gateway | Insufficient funds, gateway timeout, or buyer cash shortage | `error_code`, attempt status = 'FAILED' | `UPDATE payments SET payment_status='FAILED'` | `payment_failed` | SMS alert | Retries allowed; delivery blocked if unpaid |
| `PENDING` | `CANCELLED` | System | Order cancelled before payment | Order cancellation trigger | `UPDATE payments SET payment_status='CANCELLED'` | `payment_cancelled` | None | Payment expectation closed |
| `SUCCESS` | `REFUNDED` | Ops Admin / Finance | Approved dispute refund executed | Link to `refunds.id` | `UPDATE payments SET payment_status='REFUNDED'` | `payment_refunded` | SMS to Retailer | Adjusts settlement ledger |

- **Forbidden Transitions:**
  - `SUCCESS -> PENDING / INITIATED / FAILED`
  - `CANCELLED -> SUCCESS`
  - `REFUNDED -> SUCCESS`

---

### 2.8. Aggregate 8: `Dispute` (`disputes`)
- **Initial State:** `OPEN`
- **Terminal States:** `RESOLVED`, `CLOSED`

| From State | Allowed To State | Actor | Triggering Action | Required Fields | DB Mutation | Domain Event | Notification | Financial Side Effect |
|---|---|---|---|---|---|---|---|
| `[*] (None)` | `OPEN` | Retailer | `POST /api/v1/orders/{id}/disputes` | `order_id`, `claimed_amount_toman > 0`, `evidence_media_id`, `description` | `INSERT INTO disputes (dispute_status='OPEN')` + `UPDATE orders SET dispute_status='OPEN'` | `dispute_opened` | SMS to Retailer, Vendor & Ops | Settlement payout placed on HOLD |
| `OPEN` | `INVESTIGATING` | Ops Specialist | Ops opens dispute case in admin portal | `assigned_ops_user_id` | `UPDATE disputes SET dispute_status='INVESTIGATING'` + `UPDATE orders SET dispute_status='UNDER_REVIEW'` | `dispute_under_investigation` | In-app alert | Field concierge dispatches if needed |
| `INVESTIGATING` | `RESOLVED` | Ops Admin | `POST /api/v1/ops/disputes/{id}/resolve` | `resolution_outcome`, `approved_amount_toman` | `UPDATE disputes SET dispute_status='RESOLVED', resolved_at=NOW()` | `dispute_resolved` | SMS to both parties | Generates `settlement_adjustments` or `refunds` |
| `RESOLVED` | `CLOSED` | Finance / System | Settlement adjustment or refund confirmed | `closed_at` timestamp | `UPDATE disputes SET dispute_status='CLOSED'` + `UPDATE orders SET dispute_status='CLOSED'` | `dispute_closed` | None | Releases remaining settlement hold |

- **Forbidden Transitions:**
  - `CLOSED -> OPEN / INVESTIGATING`
  - `RESOLVED -> OPEN`
  - `orders.order_status = DISPUTED` (**Strictly forbidden!** Dispute state is isolated).

---

### 2.9. Aggregate 9: `Refund` (`refunds`)
- **Initial State:** `PENDING`
- **Terminal States:** `COMPLETED`, `REJECTED`

| From State | Allowed To State | Actor | Triggering Action | Required Fields | DB Mutation | Domain Event | Side Effects |
|---|---|---|---|---|---|---|---|
| `[*] (None)` | `PENDING` | Ops Admin | Dispute resolved in retailer favor | `order_id`, `dispute_id`, `amount_toman > 0`, `refund_method` | `INSERT INTO refunds` | `refund_created` | Creates pending refund voucher |
| `PENDING` | `APPROVED` | Finance Lead | Finance approves disbursement | `approved_by_user_id` | `UPDATE refunds SET status='APPROVED'` | `refund_approved` | Scheduled for settlement credit or cash direct credit |
| `APPROVED / PENDING` | `COMPLETED` | Finance / System | Vendor direct cash deduction or settlement credit executed | `completed_at` | `UPDATE refunds SET status='COMPLETED'` | `refund_completed` | Settles retailer claim; logs ledger entry |
| `PENDING` | `REJECTED` | Finance Lead | Duplicate or invalid refund claim | Rejection justification | `UPDATE refunds SET status='REJECTED'` | `refund_rejected` | Refund cancelled; dispute re-evaluated |

- **Forbidden Transitions:**
  - `COMPLETED -> PENDING / APPROVED / REJECTED`
  - `REJECTED -> COMPLETED`

---

### 2.10. Aggregate 10: `Settlement` (`settlements`)
- **Initial State:** `PENDING`
- **Terminal States:** `CLOSED`

| From State | Allowed To State | Actor | Triggering Action | Required Fields | DB Mutation | Domain Event | Side Effects |
|---|---|---|---|---|---|---|---|
| `[*] (None)` | `PENDING` | System | Order placed or accepted | `order_id`, `vendor_id`, `gross_amount_toman` | `INSERT INTO settlements` | `settlement_created` | Ledger record initialized |
| `PENDING` | `CALCULATED` | System | Order reaches `DELIVERED` | Commission rate applied, baseline net calculated | `UPDATE settlements SET status='CALCULATED'` | `settlement_calculated` | Net vendor amount computed |
| `CALCULATED` | `DISPUTED` | System | Dispute opened against order | Link to `dispute_id` | `UPDATE settlements SET status='DISPUTED'` | `settlement_held` | Payment payout suspended until dispute closure |
| `DISPUTED` | `RECONCILED` | System | Dispute resolved with adjustments | `adjustment_amount_toman`, `net_vendor_amount_toman` updated | `UPDATE settlements SET status='RECONCILED'` | `settlement_reconciled` | Net adjusted payout confirmed |
| `CALCULATED / RECONCILED` | `CLOSED` | Finance Lead | Payout executed or direct custody confirmed | `settled_at`, `settlement_batch_id` | `UPDATE settlements SET status='CLOSED'` | `settlement_completed` | Payout batch closed and archived |

- **Forbidden Transitions:**
  - `CLOSED -> PENDING / CALCULATED / DISPUTED`
  - `DISPUTED -> CLOSED` (Must reconcile adjustments first via `RECONCILED`).

---

### 2.11. Aggregate 11: `Vendor` (`vendors`)
- **Initial State:** `PENDING_VERIFICATION`
- **Terminal States:** None (Can toggle between `ACTIVE`, `OFFLINE`, `SUSPENDED`)

| From State | Allowed To State | Actor | Triggering Action | Required Fields | DB Mutation | Domain Event | Side Effects |
|---|---|---|---|---|---|---|---|
| `[*] (None)` | `PENDING_VERIFICATION` | Field Rep / Ops | Wholesaler onboarding | `user_id`, `business_name`, `cluster_location`, `warehouse_address` | `INSERT INTO vendors` | `vendor_registered` | Awaits warehouse verification visit |
| `PENDING_VERIFICATION` | `ACTIVE` | Ops Admin | Wholesaler LOI signed and stock verified | Approval by Ops Lead | `UPDATE vendors SET status='ACTIVE'` | `vendor_activated` | Wholesaler items become discoverable in catalog |
| `ACTIVE` | `OFFLINE` | Vendor Owner | Wholesaler sets warehouse closed (e.g. midday closure) | Vendor toggle | `UPDATE vendors SET status='OFFLINE'` | `vendor_went_offline` | Hidden from new cart allocations |
| `OFFLINE` | `ACTIVE` | Vendor Owner | Wholesaler re-opens warehouse | Vendor toggle | `UPDATE vendors SET status='ACTIVE'` | `vendor_went_online` | Re-enabled in cart allocation engine |
| `ACTIVE / OFFLINE` | `SUSPENDED` | Ops Admin | Repeated SLA breaches, fraud, or commercial dispute | Suspension reason | `UPDATE vendors SET status='SUSPENDED'` | `vendor_suspended` | All active listings hidden; active orders escalated |
| `SUSPENDED` | `ACTIVE` | Ops Admin | Wholesaler completes audit or pays settlement adjustment | Re-activation approval | `UPDATE vendors SET status='ACTIVE'` | `vendor_reactivated` | Wholesaler restored to marketplace |

- **Forbidden Transitions:**
  - `PENDING_VERIFICATION -> OFFLINE` (Cannot go offline before initial verification).
  - Unauthorized role changing vendor status (Enforced by RBAC: only `SUPER_ADMIN` or `OPS_ADMIN`).

---

### 2.12. Aggregate 12: `VendorProduct` (`vendor_products`)
- **Initial State:** `DRAFT_PENDING_CATALOG` (if candidate) or `ACTIVE` (if matched to Master Product)
- **Terminal States:** `SUSPENDED` (or archived)

| From State | Allowed To State | Actor | Triggering Action | Required Fields | DB Mutation | Domain Event | Visibility & Marketplace Effect |
|---|---|---|---|---|---|---|---|
| `[*] (None)` | `DRAFT_PENDING_CATALOG` | Vendor / System | Unmatched barcode scanned (`NO_MATCH`) | `candidate_id`, `vendor_sku`, `pack_quantity` | `INSERT INTO vendor_products (listing_status='DRAFT_PENDING_CATALOG')` | `vendor_product_draft_created` | **PUBLIC MARKETPLACE: BLOCKED (Hidden)** |
| `DRAFT_PENDING_CATALOG` | `ACTIVE` | Ops Catalog | Candidate approved or mapped to Master SKU | `product_id != NULL`, `candidate_id` resolved | `UPDATE vendor_products SET listing_status='ACTIVE', product_id=...` | `vendor_product_activated` | **PUBLIC MARKETPLACE: VISIBLE & PURCHASABLE** |
| `[*] (None)` | `ACTIVE` | Vendor | Matched to existing Master Product | `product_id`, `vendor_sku`, `pack_quantity`, valid price & stock | `INSERT INTO vendor_products (listing_status='ACTIVE')` | `vendor_product_created` | **PUBLIC MARKETPLACE: VISIBLE & PURCHASABLE** |
| `ACTIVE` | `INACTIVE` | Vendor | Wholesaler pauses offering this SKU | Vendor toggle | `UPDATE vendor_products SET listing_status='INACTIVE'` | `vendor_product_deactivated` | Hidden from catalog search |
| `INACTIVE` | `ACTIVE` | Vendor | Wholesaler resumes offering SKU | Vendor toggle | `UPDATE vendor_products SET listing_status='ACTIVE'` | `vendor_product_activated` | Restored to catalog search |
| `ACTIVE / INACTIVE` | `SUSPENDED` | Ops Admin | Price gouging, counterfeit, or misrepresentation | Admin reason | `UPDATE vendor_products SET listing_status='SUSPENDED'` | `vendor_product_suspended` | Blocked from marketplace |

- **CRITICAL CATALOG INVARIANT:**
  - `DRAFT_PENDING_CATALOG -> PURCHASABLE` is **STRICTLY FORBIDDEN**.
  - A vendor product with `listing_status = 'DRAFT_PENDING_CATALOG'` MUST NEVER appear in retailer search results, checkout options, or allocation plans.

---

### 2.13. Aggregate 13: `Inventory` (`vendor_inventory`)
- **State Properties:**
  - `physical_quantity`: Actual physical stock on warehouse shelves ($\ge 0$).
  - `reserved_quantity`: Stock locked in pending orders ($\ge 0$).
  - `available_quantity`: `physical_quantity - reserved_quantity` (Stored virtual column).
  - `freshness_status`: `FRESH`, `STALE`, `VERY_STALE`, `UNKNOWN`.

| From Freshness | Allowed To | Actor | Triggering Action | Validation & Thresholds | DB Mutation | Domain Event | Search Effect |
|---|---|---|---|---|---|---|
| `FRESH` | `STALE` | System | Time since last update > 7 days | No price or stock update for 7 days | `UPDATE vendor_inventory SET freshness_status='STALE'` | `inventory_became_stale` | Search ranking degraded |
| `STALE` | `VERY_STALE` | System | Time since last update > 14 days | No price or stock update for 14 days | `UPDATE vendor_inventory SET freshness_status='VERY_STALE'` | `inventory_became_very_stale` | Search ranking severely degraded |
| `STALE / VERY_STALE` | `FRESH` | Vendor | Price or stock confirmation via app or scan | Vendor saves updated stock/price | `UPDATE vendor_inventory SET freshness_status='FRESH', updated_at=NOW()` | `inventory_refreshed` | Full search ranking restored |

- **Concurrency & Quantity Invariants:**
  - **Over-Reservation Prevention:** `physical_quantity - reserved_quantity >= order_quantity`. Any reservation attempting to push `available_quantity < 0` MUST fail immediately with `InsufficientStockException`.
  - **Negative Stock Ban:** `CHECK (physical_quantity >= 0)` and `CHECK (reserved_quantity >= 0)` prevent negative values at the database constraint level.

---

### 2.14. Aggregate 14: `ProductCandidate` (`product_candidates`)
- **Initial State:** `PENDING_REVIEW`
- **Terminal States:** `APPROVED_CANONICAL`, `MERGED_EXISTING`, `REJECTED`

| From State | Allowed To State | Actor | Triggering Action | Required Fields | DB Mutation | Domain Event | Downstream Effect |
|---|---|---|---|---|---|---|---|
| `[*] (None)` | `PENDING_REVIEW` | Vendor / Field Staff | Unmatched barcode scanned (`NO_MATCH`) | `vendor_id`, `proposed_title`, `barcode`, `photo_asset_id` | `INSERT INTO product_candidates (status='PENDING_REVIEW')` | `product_candidate_created` | Enters ops catalog curation queue; linked vendor product is `DRAFT_PENDING_CATALOG` |
| `PENDING_REVIEW` | `APPROVED_CANONICAL` | Ops Catalog | Curator verifies genuine new FMCG item | Master SKU issued, category assigned, `products` record inserted | `UPDATE product_candidates SET status='APPROVED_CANONICAL', resolved_product_id=...` | `product_candidate_approved` | Linked `vendor_products` updated to `ACTIVE` and `product_id` set |
| `PENDING_REVIEW` | `MERGED_EXISTING` | Ops Catalog | Curator matches to existing Master SKU with typo/variant | Target `product_id` selected | `UPDATE product_candidates SET status='MERGED_EXISTING', resolved_product_id=...` | `product_candidate_merged` | Linked `vendor_products` updated to `ACTIVE` and pointed to target `product_id` |
| `PENDING_REVIEW` | `REJECTED` | Ops Catalog | Spam, invalid barcode, non-FMCG item | `review_notes` | `UPDATE product_candidates SET status='REJECTED'` | `product_candidate_rejected` | Linked `vendor_products` set to `SUSPENDED/REJECTED`; cannot be sold |

- **Forbidden Transitions:**
  - `APPROVED_CANONICAL -> PENDING_REVIEW / REJECTED`
  - `MERGED_EXISTING -> PENDING_REVIEW / REJECTED`
  - `REJECTED -> PENDING_REVIEW / APPROVED_CANONICAL`

---

## 3. Concurrency & Idempotency Invariant Verification

1. **Simultaneous Order Acceptance:** If two vendor employees click "Accept" on the same order concurrently:
   - Enforced by pessimistic or optimistic row locking (`SELECT FOR UPDATE WHERE id = :id AND order_status = 'SUBMITTED'`).
   - The first request successfully transitions state to `ACCEPTED`.
   - The second request receives HTTP 409 Conflict or an idempotent response acknowledging the order is already accepted. Zero duplicate inventory deductions.
2. **Concurrent Inventory Allocation (Race Condition):**
   ```sql
   UPDATE vendor_inventory 
   SET reserved_quantity = reserved_quantity + :requested_qty 
   WHERE vendor_product_id = :vpid 
     AND (physical_quantity - reserved_quantity) >= :requested_qty;
   ```
   If rows updated = 0, reservation fails atomically. No race condition can oversell inventory.
3. **Idempotent Dispatch:**
   If the carrier or vendor clicks "Dispatch" twice:
   - First call transitions state from `READY` to `DISPATCHED` and reduces `physical_quantity` and `reserved_quantity`.
   - Second call detects `order_status = 'DISPATCHED'` and returns HTTP 200 with existing delivery record. No double deduction.
