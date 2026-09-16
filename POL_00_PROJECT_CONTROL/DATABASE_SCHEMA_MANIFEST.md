# POL Database Schema Manifest (Historical Baseline & Evolution)

**Historical Baseline:** 56 public base tables (`migrations/001_initial_schema.sql` through `migrations/003_contract_reconciliation.sql`)  
**Current Canonical Manifest:** 90 public base tables (`POL_00_PROJECT_CONTROL/DATABASE_SCHEMA_MANIFEST_2026-09-16.md`)  
**Current Migration Chain:** `migrations/001_*.sql` through `migrations/023_*.sql`  
**Runtime Engine:** PostgreSQL 18.4  

---

## 1. Authority Notice

> [!IMPORTANT]
> The current physical database schema manifest is defined in:
> `POL_00_PROJECT_CONTROL/DATABASE_SCHEMA_MANIFEST_2026-09-16.md`
> 
> This document maintains the permanent historical record of the 56-table foundation established in the initial design phases, as well as the reconciliation requirements governing schema consistency.

---

## 2. Historical 56-Table Domain Baseline

The foundation migration chain (`001`, `002`, `003`) established the initial 56 tables across these core domains:

1. **Identity, Organizations & RBAC:** `users`, `organizations`, `organization_memberships`, `user_sessions`, `refresh_tokens`.
2. **Master SKU & Catalog:** `master_skus`, `categories`, `brands`, `units_of_measure`, `product_pack_specs`, `catalog_mappings`.
3. **Vendor Pricing & Inventory:** `vendor_catalog_items`, `vendor_inventories`, `vendor_price_tiers`, `daily_inventory_confirmations`.
4. **Retailer Basket & Allocation:** `baskets`, `basket_items`, `allocation_plans`, `allocation_plan_items`.
5. **Orders & Fulfillment:** `order_groups`, `orders`, `order_items`, `order_status_history`, `order_state_transitions`.
6. **Payment & Settlement:** `payments`, `payment_attempts`, `settlements`, `vendor_payouts`, `invoices`.
7. **Disputes & Support (Orthogonal Separation):** `disputes`, `dispute_items`, `dispute_evidence`, `support_cases`.
8. **Audit & Operations:** `audit_logs`, `outbox_events`, `system_settings`.

---

## 3. Current 90-Table Extension Overview

As detailed in `DATABASE_SCHEMA_MANIFEST_2026-09-16.md`, migrations `004` through `023` introduced:
- Operational intelligence and decay tracking (`daily_inventory_routing_exception_ledger`)
- Competitive temporal pricing and non-overlapping window constraints
- Outbox and notification delivery worker contracts
- Explicit RMA refund state machines (`REFUND_PENDING`, `REFUNDED`)
- Universal user profile and membership profile integrity (`user_profiles`, `membership_profiles`)
- Strict tenant session binding and cross-entity order/allocation validation

For the complete column definitions, constraints, triggers, and indices of all 90 tables, refer directly to `DATABASE_SCHEMA_MANIFEST_2026-09-16.md` and the SQL migrations under `migrations/`.
