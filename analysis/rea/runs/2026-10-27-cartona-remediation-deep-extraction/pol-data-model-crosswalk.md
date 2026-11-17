# POL Data Model Crosswalk (Run 2026-10-27)

Maps Cartona-observed entities (static evidence) to POL canonical tables (migrations 001-077, [CODE_VERIFIED]). Source of truth rule: **POL migrations + application_boundary.py are canonical; Cartona strings are behavioral reference only.**

| Entity | Cartona evidence | POL canonical | Crosswalk notes |
|---|---|---|---|
| Retailer/User | /v3/retail/me; is_*_filled form flags | users + organizations + organization_memberships | POL adds org/branch scoping Cartona strings don't reveal |
| Branch | /v3/retail/branches + branch-management | organizations (org-type scoped) | POL has org model; branch-as-sub-entity NOT explicit — verify before multi-branch UI (R-14) |
| Supplier/Vendor | suppliers app + is_cartona_suppliers_app_installed | organizations(VENDOR) + vendor_products | — |
| Product | /search/v2/products/* | products + vendor_products + catalog_identifiers | POL has canonical-product + vendor-listing split; Cartona model unknown |
| Barcode | POL barcode endpoints exist | catalog_matching.py | Cartona barcode evidence: none in snapshot — POL ahead |
| Price | /search/v2/suppliers/discount/* | vendor_prices (history) | MOQ/MOV filters not in POL (R-05 partial) |
| Inventory | POL daily-inventory exists | vendor_inventory + inventory_audit_log + reservations | Cartona inventory semantics unknown; POL stricter |
| Cart | sqlite carts (reorder/abandon cols) | baskets + basket_items | Cartona has local-first + server sync; POL baskets are server-side only — offline cart NOT in POL (gap for weak networks) |
| Order | /orders route + lifecycle tokens (8) | orders (10 states incl PARTIALLY_ACCEPTED) + order_groups | POL state machine is a superset [CODE_VERIFIED 001:396-401] |
| OrderGroup | POL canonical | order_groups | Cartona multi-vendor cart evidence: allocation-preview endpoint exists — consistent |
| Delivery | /order-tracking + driver app | deliveries + delivery_attempts + POD + delivery_status(6) | POL stage machine is canonical; driver actor missing (D-01) |
| Payment | /wallet + finance URLs | payments (NON_CUSTODIAL_DIRECT) + payment_evidence | Cartona wallet/credit has NO POL counterpart (R-16/R-17 gaps) |
| Invoice | POL canonical | invoices + invoice_items | — |
| Settlement | POL canonical | settlements + adjustments (5 types) | Cartona evidence: none (supplier reports claimed publicly) |
| Dispute/Return | order-support-tickets (Cartona, thin) | disputes(4-state)+returns+refunds | POL far richer; Cartona dispute vocabulary unknown |
| Support | Freshchat SDK + tickets route | support_cases + messages | Cartona uses 3rd-party Freshchat; POL first-party — independent design, keep |
| Notifications | /v3/retail/notifications + FCM | notifications + inbox + preferences | POL lacks FCM device registration (R-18) |
| Campaigns | in-app-stories + eid cashback | (none) | POL_MISSING (R-20/R-21) |
| Credit/BNPL | Cartona Credit webapp + plans | (none) | POL_MISSING — EXTERNAL_INTEGRATION if pursued |

## Source-of-truth decisions documented (plan §31.3)

- Price/stock truth: vendor_products/vendor_prices/vendor_inventory rows; order-item snapshots immutable (migration-enforced).
- Concurrency: reservation invariants (022/056/057) + idempotency fingerprints (061).
- Audit: append-only permission_audit_events + admin audit (049) + inventory_audit_log.
- Worker truth: **in-process Python workers + DB outbox** — the DOMAIN_MODEL.md "BullMQ/Redis" diagram is stale ([CODE_VERIFIED] test_worker_architecture.py:15-16 forbids it).
- Tenant boundary: org_id in JWT vs session.active_organization_id (auth_boundary.py:141-142) — Cartona's cross-org behavior unknown; POL rule is canonical.

## Known inconsistencies to resolve in implementation run

1. Cartona-style **client-side cart persistence** (offline cart) has no POL representation — decide whether POL keeps server-only baskets (current) or adds local-first cart sync (needed for weak-network Iranian retail).
2. **Branch** entity: Cartona treats branches as first-class (branch-management); POL org model needs verification before building R-14 UI.
3. Dispute vocabulary in POL docs is stale (audit §4) — docs fix O-05.
