# Catalog Domain Audit — Stage 13 Output

**Date:** 2026-09-19
**Commit:** (pending Stage 13 close)

---

## Executive Summary

The POL catalog domain has a **mature, well-designed database schema** (15+ catalog-related tables, 8+ indexes, 5+ triggers, multi-identifier barcode architecture, temporal pricing with GiST exclusion) but an **almost entirely unimplemented application layer**. The database is ready for a full catalog management system; the code layer needs the matching services and endpoints.

---

## Catalog Schema Inventory

### Master Catalog (Layer 1: POL-wide reference data)

| Table | Columns | Key Features |
|---|---|---|
| `brands` | id, name_fa, name_en, slug, is_active, created_at | GIN trigram on name_fa |
| `categories` | id, name_fa, slug, icon_url, display_order, created_at | Flat tree (no parent_id) |
| `subcategories` | id, category_id(FK), name_fa, slug, display_order, created_at | CASCADE delete |
| `products` | id, master_sku(UNIQUE), canonical_name_fa, brand_id, category_id, subcategory_id, base_unit, default_pack_unit, default_pack_quantity, ... | GIN trigram on name_fa, external_source tracking |
| `product_reference_metadata` | id, product_id(FK), source_name, external_id, raw_observed_price_rials, ... | UNIQUE(product_id, source_name) |
| `product_identifiers` | id, product_id(FK), vendor_id(FK nullable), identifier_scope, identifier_type, identifier_value, packaging_scope, ... | Multi-scope barcode model, CHECK constraints |
| `media_assets` | id, storage_provider, storage_bucket, storage_key, mime_type, file_size_bytes, status, provenance, ... | S3-compatible media |
| `product_media` | id, product_id(FK), media_asset_id(FK), is_primary, display_order | UNIQUE(product_id, media_asset_id) |
| `product_candidates` | id, vendor_id(FK), proposed_title, proposed_brand, barcode, vendor_sku, status, resolved_product_id(FK), ... | Full lifecycle status machine |
| `product_merge_history` | id, merged_from_product_id, merged_into_product_id(FK), reason, performed_by_user_id(FK) | Merge audit trail |

### Vendor Supply (Layer 2: vendor-scoped)

| Table | Columns | Key Features |
|---|---|---|
| `vendor_products` | id, vendor_id(FK), product_id(FK nullable), candidate_id(FK nullable), vendor_sku, packaging_unit, pack_quantity, sales_unit, is_active, listing_status | UNIQUE(vendor_id, vendor_sku), CHECK target logic |
| `vendor_inventory` | id, vendor_product_id(UNIQUE FK), inventory_unit, physical_quantity, reserved_quantity, moq, freshness_status, inventory_confidence, verification_source | GENERATED available_quantity, CHECK reserved <= physical |
| `vendor_prices` | id, vendor_product_id(FK), price_toman, effective_from, effective_to, is_current | GiST temporal exclusion, trigger-based rotation |
| `inventory_audit_log` | id, vendor_id(FK), vendor_product_id(FK), old_quantity, new_quantity, old_price_toman, new_price_toman, source_trigger, actor_user_id(FK) | Audit trail (never written to by Python code) |

### Inventory Confirmation (Layer 2 extension)

| Table | Columns | Key Features |
|---|---|---|
| `daily_inventory_confirmations` | id, vendor_id(FK), confirmation_date, status, actor_user_id, confirmed_at, ... | UNIQUE(vendor_id, confirmation_date) |
| `daily_inventory_confirmation_items` | id, confirmation_id(FK), vendor_product_id(FK), previous_quantity, declared_quantity, GENERATED difference | UNIQUE(confirmation_id, vendor_product_id) |
| `vendor_inventory_responsibilities` | id, vendor_id(FK), user_id(FK), responsibility_type, is_primary, ... | UNIQUE(vendor_id, user_id, responsibility_type) |

---

## Gaps Analysis

### Zero HTTP Catalog Endpoints

The entire API surface has 23 routes (auth, baskets, orders, profile, ops). **Zero catalog routes exist.** 12+ catalog routes are planned in the API contract.

### Zero Catalog Management Domain Services

No Python service implements:
- Product/Brand/Category CRUD
- Product candidate lifecycle (propose → approve → reject → merge)
- Barcode scan/match (`POST /products/match-barcode`)
- Continuous scan inventory session
- Inventory manual adjustment
- Price update service
- Media upload/presigned URL
- Product search with pg_trgin
- Vendor offer listing per product
- Retailer saved list management
- Commercial terms management

### Only Existing Writers

| Path | Tables Written |
|---|---|
| Checkout flow | vendor_inventory (reserved_quantity), inventory_reservations |
| Canonical vendor order accept/reject | vendor_inventory (physical_quantity), inventory_reservations |
| Canonical partial acceptance | vendor_inventory |
| Daily inventory confirmation | daily_inventory_confirmations, daily_inventory_confirmation_items, vendor_inventory (confidence fields) |
| Basket allocation | allocation_plans, allocation_items (read-only on catalog tables) |

### Test Gaps

| Missing Test | Priority |
|---|---|
| `product_identifiers` barcode lookup + uniqueness enforcement | HIGH |
| `product_candidates` full lifecycle (propose → approve → reject → merge) | HIGH |
| Barcode scan match logic (EXACT / HIGH_CONFIDENCE / AMBIGUOUS / NO_MATCH) | HIGH |
| `inventory_audit_log` write coverage | MEDIUM |
| Product/media association CRUD | MEDIUM |
| Brand/category CRUD + cascade behavior | MEDIUM |
| `DRAFT_PENDING_CATALOG` → `ACTIVE` transition on candidate approval | MEDIUM |
| Saved list management | LOW |
| Commercial terms management | LOW |

---

## Key Semantic Findings

### Barcode Architecture

- **Multi-identifier model by design.** 1:N barcodes per product (EAN13, EAN8, UPC_A, GTIN14, IRANCODE, INTERNAL_BARCODE). Prevents single-column barcode antipattern.
- **Vendor-scoped vs global identifiers.** GLOBAL/PACKAGING are product-wide; VENDOR_INTERNAL are scoped per-vendor with separate uniqueness.
- **Barcodes are VARCHAR** (preserves leading zeros for UPC-A, internal barcodes).
- **Normalization pipeline documented but not implemented.** Persian→Latin digit conversion, whitespace removal, uppercase exist in catalog profiling scripts but are not shared.
- **No barcode checksum validation** (Modulo-10 for EAN-13/EAN-8/UPC-A documented but unwritten).

### Product Candidate Lifecycle

- Full status machine designed: PENDING_REVIEW → APPROVED_CANONICAL / MERGED_EXISTING / REJECTED
- `chk_vendor_product_target` CHECK enforces: DRAFT_PENDING_CATALOG listings require candidate_id; ACTIVE listings require product_id.
- Bridge between vendor scan → candidate → canonical product → vendor listing.

### Pack / Unit Semantics

- Three-layer hierarchy: base_unit (PIECE/BOTTLE/PACK) → default_pack_unit + default_pack_quantity (canonical) → vendor_products.packaging_unit + pack_quantity (vendor-specific).
- Vendor can differ from canonical (vendor sells in packs of 6 while canonical default is 12).
- Allocation engine keys on (product_id, packaging_unit).

### MOQ Semantics

- **Two distinct minimums:**
  - `vendor_inventory.moq` — per-SKU minimum order quantity (enforced at allocation + checkout)
  - `vendors.min_order_value_toman` — per-vendor minimum order value (enforced at allocation + checkout)
- MOQ is in vendor_inventory (operational property), not vendor_products (listing property).

### Price Temporal Semantics

- At most one current price per vendor_product (partial unique index).
- Temporal exclusion prevents overlapping price windows (GiST exclusion constraint).
- Trigger-based price rotation closes previous price on new current price insertion.
- `consumer_price_per_unit_toman` is display-only, never used in business logic.

### Inventory Audit Log

- Table exists with CHECK(source_trigger: BARCODE_SCAN, ORDER_CHECKOUT, MANUAL_EDIT, SESSION_PUBLISH) but **no Python code writes to it**.
- MEDIUM priority to implement: write audit records on every inventory mutation.

---

## Implementation Backlog (Recommended Stages 14-50 Scope)

### Phase 1: Catalog Read API (HIGH priority)
1. Product search endpoint with pg_trgm fuzzy matching
2. Category tree endpoint
3. Product detail endpoint with media
4. Vendor offers per product endpoint

### Phase 2: Catalog Management (HIGH priority)
5. Barcode scan/match service
6. Product candidate CRUD + lifecycle service
7. Product CRUD + is_verified promotion
8. Brand/Category CRUD

### Phase 3: Vendor Catalog Operations (MEDIUM priority)
9. Price update service
10. Inventory manual adjustment service
11. Continuous scan inventory session
12. Inventory publish to marketplace
13. Barcode checksum validation
14. Normalization pipeline (Persian→Latin, whitespace)

### Phase 4: Retailer Catalog Operations (LOW priority)
15. Retailer saved list management
16. Commercial terms management
17. Product merge service + audit trail

---

## Exit Criteria: Domain model canonical and implementation-ready

**PASS.** The schema is mature and well-constrained. The semantic model (barcodes, candidates, packs, MOQ, pricing, audit) is fully designed at the DB level. The application layer is the gap — this audit provides the backlog for Stages 14+.
