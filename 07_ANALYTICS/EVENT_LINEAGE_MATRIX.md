# POL — Analytics Event Lineage Matrix

**Document ID:** POL-MATRIX-ANALYTICS-001
**Stage:** 36 — Analytics Event Lineage
**Target Release:** POL MVP Pilot

---

## 1. Purpose

This matrix maps every platform KPI to its source events, source tables, and calculation logic. It provides full traceability from executive metrics back to raw database state, ensuring every number in the pilot dashboard can be audited to a specific event or table.

---

## 2. Global Conventions

| Convention | Rule |
| :--- | :--- |
| **Timezone — Storage** | All `created_at`, `updated_at`, `paid_at`, `delivered_at` columns store UTC (`TIMESTAMPTZ`). |
| **Timezone — Reports** | All KPI reports render in `Asia/Tehran` (UTC+3:30 / UTC+4:30 DST). |
| **Retailer Cohort** | Defined by `retailers.created_at` (signup date). A retailer belongs to the cohort of the week/month of its signup. |
| **Vendor Cohort** | Defined by `vendors.created_at` when `vendors.status = 'ACTIVE'` (activation date). |
| **Monetary Units** | All amounts stored in Iranian Toman (`BIGINT`). |

---

## 3. KPI Lineage Matrix

| KPI | Description | Source Event(s) | Source Table(s) | Calculation Logic | Cohort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GMV** | Gross Merchandise Value — total value of orders placed in period. | `ORDER_SUBMITTED` | `orders.total_amount_toman` | `SUM(total_amount_toman) WHERE created_at BETWEEN :start AND :end AND order_status NOT IN ('CANCELLED')` | Retailer signup week/month |
| **AOV** | Average Order Value — mean order size per retailer. | `ORDER_SUBMITTED` | `orders.total_amount_toman` | `SUM(total_amount_toman) / COUNT(DISTINCT order_id) WHERE order_status NOT IN ('CANCELLED')` | Retailer signup week/month |
| **Repeat Rate** | Fraction of retailers with 2+ completed orders in period. | `ORDER_DELIVERED` | `orders` | `COUNT(retailer_id WHERE order_count >= 2) / COUNT(DISTINCT retailer_id) WHERE order_status = 'DELIVERED'` | Retailer signup week/month |
| **OTIF** | On-Time In-Full — orders delivered by scheduled date with full quantity. | `ORDER_DELIVERED`, `PROOF_OF_DELIVERY` | `deliveries`, `order_items` | `COUNT(orders WHERE delivered_at <= scheduled_date AND delivered_quantity >= ordered_quantity) / COUNT(orders WHERE order_status = 'DELIVERED')` | Retailer signup week/month |
| **Self-Service Rate** | Fraction of orders placed without field activator assistance. | `ORDER_SUBMITTED` | `orders`, `order_groups` | `COUNT(orders WHERE checkout_source = 'SELF_SERVICE') / COUNT(ALL orders)` | Retailer signup week/month |
| **Churn** | Retailers with zero orders in trailing 30-day window. | `ORDER_SUBMITTED` | `orders`, `retailers` | `COUNT(retailers WHERE last_order_date < :window_start) / COUNT(active retailers)` | Retailer signup week/month |
| **Cost-to-Serve** | Platform cost per delivered order (Ops labor + logistics). | `ORDER_DELIVERED`, `FIELD_TASK_COMPLETED` | `orders`, `field_tasks`, `admin_audit_logs` | `(SUM(field_task_cost) + SUM(delivery_cost)) / COUNT(delivered orders)` | Vendor activation week/month |
| **CAC** | Customer Acquisition Cost — total acquisition spend per activated retailer. | `FIELD_TASK_COMPLETED`, `RETAILER_ACTIVATED` | `field_tasks`, `retailers`, `organization_memberships` | `SUM(field_task_cost WHERE task_type = 'ONBOARD_RETAILER') / COUNT(retailers WHERE onboarding_status = 'ACTIVE_SELF_SERVICE')` | Vendor activation week/month |
| **Vendor Continuation** | Fraction of vendors still active after N months. | `VENDOR_ONBOARDING_APPROVED` | `vendors` | `COUNT(vendors WHERE status = 'ACTIVE' AND months_since_activation >= N) / COUNT(vendors WHERE months_since_activation >= N)` | Vendor activation week/month |
| **Catalog Coverage** | Fraction of master products with at least one active vendor listing. | `CANDIDATE_SKU_APPROVED` | `products`, `vendor_products` | `COUNT(DISTINCT product_id FROM vendor_products WHERE listing_status = 'ACTIVE') / COUNT(DISTINCT product_id FROM products WHERE is_active = TRUE)` | N/A (platform-wide) |

---

## 4. Source Event Definitions

| Event Name | Trigger | Table | Key Columns |
| :--- | :--- | :--- | :--- |
| `ORDER_SUBMITTED` | Retailer submits basket at checkout | `orders` | `order_status = 'SUBMITTED'`, `total_amount_toman`, `created_at` |
| `ORDER_ACCEPTED` | Vendor accepts order within SLA | `orders` | `order_status = 'ACCEPTED'` |
| `ORDER_REJECTED` | Vendor rejects order | `orders` | `order_status = 'REJECTED'`, `rejection_reason` |
| `ORDER_DISPATCHED` | Vendor marks order ready for pickup | `orders` | `order_status = 'DISPATCHED'` |
| `ORDER_DELIVERED` | Proof of delivery confirmed | `deliveries`, `proof_of_delivery` | `delivery_status = 'DELIVERED'`, `delivered_at` |
| `PROOF_OF_DELIVERY` | OTP/physical proof captured | `proof_of_delivery` | `otp_verified`, `accepted_at`, `issue_reported_at_delivery` |
| `FIELD_TASK_COMPLETED` | Field activator completes task | `field_tasks` | `task_type`, `status = 'COMPLETED'`, `completed_at` |
| `VENDOR_ONBOARDING_APPROVED` | Vendor approved by admin | `vendors` | `status = 'ACTIVE'` |
| `CANDIDATE_SKU_APPROVED` | Product candidate approved | `product_candidates` | `status = 'APPROVED_CANONICAL'` |
| `RETAILER_ACTIVATED` | Retailer reaches self-service status | `retailers` | `onboarding_status = 'ACTIVE_SELF_SERVICE'` |

---

## 5. Source Table Inventory

| Table | Primary Use in Lineage | Key Columns for KPI |
| :--- | :--- | :--- |
| `orders` | GMV, AOV, Repeat Rate, OTIF, Self-Service Rate, Churn | `id`, `retailer_id`, `vendor_id`, `order_status`, `total_amount_toman`, `created_at` |
| `order_items` | OTIF (quantity check), AOV (line detail) | `order_id`, `ordered_quantity`, `delivered_quantity` |
| `deliveries` | OTIF (on-time check) | `order_id`, `delivery_status`, `scheduled_date`, `delivered_at` |
| `proof_of_delivery` | OTIF (delivery confirmation) | `delivery_id`, `otp_verified`, `accepted_at` |
| `vendors` | Vendor Continuation, Cost-to-Serve | `id`, `status`, `created_at` |
| `retailers` | Churn, Cohort definition | `id`, `onboarding_status`, `created_at` |
| `field_tasks` | Cost-to-Serve, CAC | `task_type`, `status`, `completed_at` |
| `products` | Catalog Coverage (denominator) | `id`, `is_active` |
| `vendor_products` | Catalog Coverage (numerator) | `product_id`, `listing_status` |
| `organization_memberships` | User-tenant scoping | `organization_id`, `user_id`, `role` |

---

## 6. Audit Trail

Every KPI calculation must reference this matrix. The `scripts/analytics_lineage.py` module provides:
- `KPI_DEFINITIONS`: machine-readable dict of all KPIs with source tables, events, and calculation formulas.
- `validate_lineage(cur)`: verifies all referenced source tables exist in the live database.

---

## 7. Notes

- All timestamps are UTC in storage; dashboard queries convert to `Asia/Tehran` at render time.
- `order_groups` tracks the basket→order split; `total_amount_toman` on `orders` is the canonical per-order value.
- Vendor cohort is based on activation date (`vendors.status = 'ACTIVE'`), not signup date.
- Catalog Coverage is a snapshot metric, not event-driven — it is recomputed on each dashboard refresh.
