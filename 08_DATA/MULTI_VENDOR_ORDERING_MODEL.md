# POL MULTI-VENDOR ORDERING DOMAIN & DATA MODEL SPECIFICATION

**Document ID:** `POL-DAT-004`  
**Version:** 2.0 (Canonical MVP)  
**Status:** `LOCKED / IMPLEMENTATION-READY`  
**Governance:** Lead Data Architect / Founder Approved  
**Associated Decision:** `D-014` (Multi-Vendor Basket in MVP), `D-004` (Multi-Vendor Extensibility), `D-010` (Entity Separation)  
**Schema Parity Reference:** `migrations/001_initial_schema.sql` & `08_DATA/Data_Schema.md`  

---

## 1. Domain Aggregate Hierarchy

Under **D-014**, the ordering system strictly separates buyer purchase intent from vendor commercial commitments, while giving the retail buyer a unified checkout experience:

```
[Baskets / BasketItems]
           │
           ▼
[AllocationPlans / AllocationItems] (Deterministic Heuristic Engine)
           │
           ▼
[OrderGroups] (Parent Unified Transaction Aggregate)
     ├── Total Amount, Retailer ID, Status, Created At
     │
     ├── [Child Orders: Vendor 1] ───► [OrderItems] ───► [Deliveries] ───► [Settlement V1]
     │                                    ▲
     │                                    │
     │                           [Disputes: Vendor 1]
     │
     └── [Child Orders: Vendor 2] ───► [OrderItems] ───► [Deliveries] ───► [Settlement V2]
                                          ▲
                                          │
                                 [Disputes: Vendor 2]
```

### Key Relational Mappings:
1. **`baskets` (1) $\to$ (N) `basket_items`**: Logical staging cart for the retail buyer. No vendor assignment is locked in at this stage.
2. **`baskets` (1) $\to$ (N) `allocation_plans`**: Each allocation run creates a snapshot plan. The accepted plan is converted to an `order_groups` record.
3. **`allocation_plans` (1) $\to$ (N) `allocation_items`**: Contains item assignments to `vendor_id`. Items that cannot be fulfilled carry `status = 'UNFULFILLED'` and `vendor_id = NULL`.
4. **`order_groups` (1) $\to$ (N) `orders`**: Parent container grouping all vendor child orders resulting from a single checkout transaction.
5. **`orders` (1) $\to$ (N) `order_items`**: Exact physical commercial contract committed to a specific wholesaler (`vendor_id`).
6. **`orders` (1) $\to$ (N) `deliveries`**: Physical logistics fulfillment unit. Dispatched via local hub fleet (وانت‌های بومی).
7. **`orders` (1) $\to$ (0..N) `disputes`**: Orthogonal dispute record attached to an order or specific item.
8. **`orders` (1) $\to$ (1..N) `payments`**: Financial payment tracking records per vendor child order (`custody_model = 'NON_CUSTODIAL_DIRECT'`). Aggregated at the `order_groups` level for unified buyer visibility.
9. **`orders` (1) $\to$ (0..1) `settlements`**: Financial settlement ledger calculated and audited per vendor order.

---

## 2. Aggregate Lifecycle & State Transition Matrix

### 2.1. Parent `OrderGroup` Lifecycle

The `order_groups` aggregate coordinates the buyer's high-level order progress across all participating wholesalers.

```
       ┌──────────┐
       │  DRAFT   │ (Checkout Initiated)
       └────┬─────┘
            │ Checkout Confirmed / Dispatched
            ▼
       ┌──────────┐
       │  ACTIVE  │ ◄─── At least one child order in (PENDING, ACCEPTED, PROCESSING, SHIPPED)
       └────┬─────┘
            ├────────────────────────────────────────┬────────────────────────────────────────┐
            │ All Child Orders DELIVERED             │ Mixed: Some DELIVERED, others CANCELLED│ All Child Orders CANCELLED/REJECTED
            ▼                                        ▼                                        ▼
    ┌───────────────┐                       ┌─────────────────────┐                   ┌───────────────┐
    │   COMPLETED   │                       │ PARTIALLY_COMPLETED │                   │   CANCELLED   │
    └───────────────┘                       └─────────────────────┘                   └───────────────┘
```

| State | Definition | Trigger / Precondition |
|:---|:---|:---|
| `DRAFT` | Allocation confirmed; order group created | Created by `POST /api/v1/orders` |
| `ACTIVE` | Child orders dispatched to vendors; fulfillment & direct payment in progress | OrderGroup confirmed; child orders created |
| `COMPLETED` | 100% of child orders successfully reached `DELIVERED` | All child orders marked `DELIVERED` |
| `PARTIALLY_COMPLETED` | At least 1 child order `DELIVERED`, and at least 1 child order `CANCELLED` or `REJECTED` | Terminal states reached for all child orders with mixed results |
| `CANCELLED` | 100% of child orders failed (`CANCELLED` or `REJECTED`) | All vendors rejected or timed out |

---

### 2.2. Vendor Child `Order` Lifecycle

Each child order represents an autonomous contract with a single wholesaler. Its lifecycle transitions independently of other sibling orders in the same `OrderGroup`.

```
                    ┌─────────────┐
                    │   PENDING   │ (Created; Acceptance Timer Started: 15m target / 2h timeout)
                    └──────┬──────┘
             ┌─────────────┴─────────────┐
             │ Vendor Accepts            │ Vendor Rejects / 2h Timeout / Retailer Pre-Accept Cancel
             ▼                           ▼
      ┌─────────────┐             ┌─────────────┐
      │  ACCEPTED   │             │  CANCELLED  │ (Terminal: Inventory unreserved, payment cancelled)
      └──────┬──────┘             └─────────────┘
             │ Packing Complete
             ▼
      ┌─────────────┐
      │ PROCESSING  │
      └──────┬──────┘
             │ Handed to Hub Driver
             ▼
      ┌─────────────┐
      │   SHIPPED   │
      └──────┬──────┘
             │ Delivered to Store + OTP Verified
             ▼
      ┌─────────────┐
      │  DELIVERED  │ (Terminal Fulfillment: Direct payment completed, settlement audit starts)
      └─────────────┘
```

#### Child Order State Transition Rules:
1. **`PENDING`:**
   - Inventory is reserved: `vendor_inventory.reserved_quantity += requested_quantity`.
   - Outbox event published: `order_created` (with `vendor_id`, `order_id`, `order_group_id`).
   - Timeout timer armed for 2 hours (120 minutes).
2. **`ACCEPTED`:**
   - Vendor commits to fulfill: `vendor_confirmed_at = NOW()`.
   - Outbox event: `order_accepted`.
3. **`REJECTED` / `CANCELLED`:**
   - If vendor declines or timeout fires: `order_status = 'CANCELLED'`.
   - Reserved inventory is released: `vendor_inventory.reserved_quantity -= requested_quantity`.
   - Associated payment record marked `CANCELLED` (no payment collected).
   - Outbox event: `order_cancelled` (or `order_rejected`).
   - Sibling child orders in the same `OrderGroup` remain completely unaffected!
4. **`PROCESSING`:**
   - Vendor warehouse marks packing complete: `warehouse_packed_at = NOW()`.
5. **`SHIPPED`:**
   - Local hub driver picks up consignment: `dispatched_at = NOW()`.
   - `deliveries` record transitions to `IN_TRANSIT`.
6. **`DELIVERED`:**
   - Store receives goods and validates digital OTP / signature.
   - Physical inventory decremented: `physical_quantity -= quantity`, `reserved_quantity -= quantity`.
   - Direct payment executed via Driver POS, COD, or Bank Transfer (`payments.payment_status = 'SUCCESS'`).
   - `orders.order_status = 'DELIVERED'`, `actual_delivery_time = NOW()`.
   - Settlement record created: `settlements.status = 'PENDING'`.

---

## 3. Orthogonal Dispute Integration

In accordance with architectural invariant **CHECK 2** and **D-010**:
- `orders.order_status` NEVER contains `'DISPUTED'`. An order that is disputed remains in its operational status (`DELIVERED` or `SHIPPED`).
- `disputes` is a distinct aggregate table referencing `order_id` and optional `order_item_id`.
- **Projection State:** `orders.dispute_status` is a derived projection (`NONE`, `OPEN`, `RESOLVED`, `CLOSED`) reflecting whether any active dispute exists for that child order.
- **Canonical State:** `disputes.dispute_status` is the canonical source of truth for dispute investigations (`OPEN`, `INVESTIGATING`, `RESOLVED`, `CLOSED`).
- **Blast Radius Isolation:** If Retailer opens a dispute for damaged items on Vendor A's child order:
  - Vendor A's settlement is held (`settlement_status = 'HELD'`).
  - Vendor B's child order, direct payment, and settlement proceed completely unimpeded!

---

## 4. Payment & Financial Settlement Model

### 4.1. Canonical Payment Architecture: `NON_CUSTODIAL_DIRECT` (MVP Pilot)
In accordance with **D-005**, **09_OPERATIONS/Payments_and_Settlement.md**, and architectural Invariant 15:
- **Zero Custody of Funds in MVP:** POL does **NOT** operate a central escrow account, hold customer funds, or possess a Central Bank payment intermediary / PSP custody license during the 3-month Ahvaz pilot.
- **Direct Commercial Settlement:** Funds flow directly from Retailer to Wholesaler upon physical delivery or through direct bilateral financial rails.
- **Roadmap Distinction:**
  - `custody_model = 'NON_CUSTODIAL_DIRECT'`: **Canonical MVP Pilot implementation.**
  - `custody_model = 'ESCROW_FUTURE'`: **Roadmap architectural reservation** (for Year 2+ scaling if POL obtains formal regulatory and banking custody clearance).

### 4.2. Multi-Vendor Payment Coordination
Although payment custody is direct and non-custodial, the POL platform maintains rigorous end-to-end transactional observability across multi-vendor baskets:
1. **Consolidated Retailer View (`OrderGroup` Level):**
   - The retail buyer sees a single consolidated checkout total: `order_groups.total_amount_toman`.
   - Aggregate payment status reflects overall completion (`PENDING`, `PARTIALLY_PAID`, `PAID`).
2. **Independent Child Order Payment Ledger (`Order` Level):**
   - Each vendor child order generates its own independent record in `payments`:
     - `order_id`: References the specific child order.
     - `retailer_id`: Identifies the buyer.
     - `vendor_id`: Identifies the specific receiving wholesaler.
     - `amount_toman`: Exactly equals `orders.total_amount_toman`.
     - `payment_method`: `POS_DRIVER`, `CASH_ON_DELIVERY`, `DIRECT_BANK_TRANSFER`, `CHEQUE_SAYYAD`, or `ONLINE_MOCK`.
     - `payment_status`: `PENDING` $\to$ `INITIATED` $\to$ `SUCCESS` (or `FAILED` / `CANCELLED`).
     - `custody_model`: Enforced as `'NON_CUSTODIAL_DIRECT'`.
     - `reference_number`: Bank transaction reference, POS trace, or cheque ID.
3. **Vendor Rejection / Cancellation Handling:**
   - If Vendor B rejects their child order or times out (2h SLA), Vendor B's child order transitions to `CANCELLED`.
   - The corresponding `payments` record for Vendor B is marked `CANCELLED` (funds were never transferred).
   - Retailer owes nothing to Vendor B.
   - Sibling child orders (e.g. Vendor A) and their payments proceed completely unaffected.
4. **Post-Delivery Settlement & Discrepancies:**
   - When Vendor A's child order reaches `DELIVERED`, POL generates a `settlements` record for reconciliation:
     $$\text{net\_vendor\_amount} = \text{gross\_amount} - \text{commission\_amount} - \text{adjustment\_amount}$$
   - In Pilot, $\text{commission\_amount} = 0$ (0% take rate per D-006).
   - If physical shortages or damaged items are identified, the retailer files an orthogonal dispute (`disputes` table).
   - Once resolved, a `settlement_adjustments` record is recorded (e.g. `SHORTAGE_DEDUCTION`), and if already paid, a `refunds` entry tracks the vendor's direct credit or cash refund to the retailer.

### 4.3. Delivery Semantics (MVP Operational Simplification)
- In POL MVP, **1 Vendor Child Order = 1 Delivery**.
- This is explicitly designated as an **MVP Operational Simplification**:
  - Each participating wholesaler independently packs their items into wholesale cartons.
  - A local hub vehicle (وانت بومی) is dispatched directly to that wholesaler's warehouse in Ahvaz Wholesalers Hub (شهرک بنکداران اهواز).
  - The driver performs pickup, verifies OTP, transports goods directly to the retailer's store, and collects the delivery confirmation OTP.
  - No central cross-dock facility, intermediate consolidation hub, or vehicle co-loading across competing wholesalers is introduced during Pilot. Consolidated multi-vendor delivery runs are deferred to post-Pilot scaling.

---

## 5. Relational DDL Parity Verification

This multi-vendor model uses the exact relational schema defined in `migrations/001_initial_schema.sql`:
- Table `order_groups`:
  - `id UUID PRIMARY KEY`, `retailer_id UUID NOT NULL`, `group_status VARCHAR(30) NOT NULL`, `total_amount_toman BIGINT NOT NULL`, `checkout_idempotency_key VARCHAR(128) UNIQUE`.
- Table `orders`:
  - `id UUID PRIMARY KEY`, `order_group_id UUID NOT NULL REFERENCES order_groups(id)`, `vendor_id UUID NOT NULL REFERENCES vendors(id)`, `order_status VARCHAR(30) NOT NULL`, `dispute_status VARCHAR(30) NOT NULL DEFAULT 'NONE'`.
- Table `order_items`:
  - `id UUID PRIMARY KEY`, `order_id UUID NOT NULL REFERENCES orders(id)`, `vendor_product_id UUID NOT NULL REFERENCES vendor_products(id)`, `quantity_requested INT NOT NULL`, `unit_price_toman BIGINT NOT NULL`.
- Table `allocation_items`:
  - `status VARCHAR(30) NOT NULL CHECK (status IN ('ALLOCATED', 'UNFULFILLED'))`, `vendor_id UUID NULL REFERENCES vendors(id)`.

Zero DDL schema alterations are required; the canonical database architecture was already designed multi-vendor ready from inception.


---

## 2026-09-20 Product Architecture Amendment — OrderGroup / Invoice / Financial Activity

### A. Unified buyer order, vendor child orders, and invoices

The existing OrderGroup model remains canonical.

A retailer checkout creates one parent OrderGroup and one or more vendor child Orders. The financial document visible to the retailer is therefore a set of vendor-specific invoices beneath one unified purchase.

Canonical relationship:

**Retailer Checkout → OrderGroup → Vendor Orders → Vendor Invoices**

The UI must never imply that a multi-vendor checkout produces a single legally/commercially identical vendor invoice.

### B. Required retailer visibility

OrderGroup detail should expose:

- total requested amount
- vendor count
- child order count
- invoice count
- invoice amount per vendor
- payment status per vendor order/invoice
- fulfillment status per vendor order
- delivery status per vendor order
- dispute status where applicable

The financial history screen should aggregate existing canonical payment, refund, invoice and settlement records without creating a second source of truth.

### C. Financial activity is a read model, not a wallet

A Financial Activity view may combine:

**Payment → Refund → Order Amount → Invoice Amount → Payment Status → Authorized Settlement Status**

This is visibility only. It must not introduce a stored-value customer balance.

### D. Future wallet boundary

Any future stored-value wallet must be modeled as a separate financial ledger/account domain. Payments and refunds remain transaction records and must not be reinterpreted as wallet entries.

No schema change is required for this amendment.
