# مانیفست کانونیکال اسکیما و زنجیره Migration پلتفرم پُل

**شناسه:** `POL-SCHEMA-MANIFEST-2026`  
**نسخه:** 2.2  
**وضعیت:** `CANONICAL`  
**Database:** PostgreSQL 18  
**Latest recorded CI runtime:** PostgreSQL 18.6  
**Latest recorded base-table count:** 62

## 1. Canonical migration chain

The physical schema is built from the complete ordered migration chain:

```text
001_initial_schema.sql
  -> 002_platform_core_schema.sql
  -> 003_contract_reconciliation.sql
  -> 004_operational_intelligence.sql
  -> N (future numbered migrations)
```

`scripts/migration_runner.py` dynamically discovers and applies the ordered SQL chain. Migration 004 is therefore part of the current canonical schema and must not be omitted from documentation or CI.

## 2. Current table count

The latest repository verification artifact records **62 base tables** after the current migration chain. Migration 004 adds six tables:

1. `daily_inventory_confirmations`
2. `daily_inventory_confirmation_items`
3. `feedback_submissions`
4. `vendor_reliability_events`
5. `product_identity_lifecycle_logs`
6. `returns`

It also extends `vendor_inventory` with inventory freshness/confidence fields and `vendor_prices` with price-version/effective-date fields.

Any previous document stating **56 tables** is historical and not a current schema count.

## 3. Canonical IAM roles

Runtime authorization uses `organization_memberships.role` scoped by the active organization in `user_sessions.active_organization_id`.

Canonical roles are:

```text
RETAILER_OWNER
RETAILER_STAFF
VENDOR_OWNER
VENDOR_STAFF
OPS_AGENT
ADMIN_SUPER
FIELD_ACTIVATOR
```

`SUPER_ADMIN` and `OPS_ADMIN` are legacy aliases retained by migration compatibility logic; they are not separate canonical role names. `users.role` is deprecated and non-authoritative.

## 4. Core canonical entities

The current schema includes the Commerce Core (`baskets`, `basket_items`, `allocation_plans`, `allocation_items`, `order_groups`, `orders`, `order_items`), Catalog/Merchandising, Inventory, Fulfillment, Payments/Settlements, Disputes/Refunds, Identity/IAM, Notifications, Support, Field Operations, Audit/Outbox, and the six Migration-004 operational-intelligence/RMA tables listed above.

The exact physical DDL remains the ordered migration chain itself; this document is a manifest, not a second DDL source.

## 5. Verification evidence

Recorded CI evidence (`34818313995`) tested commit `f3a65a3060d2f09ca7bf9cbd1b270b13f539ca2f` using PostgreSQL 18.6 and observed 62 base tables with 47 collected tests, all 47 passing. This evidence certifies that tested commit only. The current `main` branch contains subsequent commits and therefore requires a fresh CI run before a new runtime certification claim.
