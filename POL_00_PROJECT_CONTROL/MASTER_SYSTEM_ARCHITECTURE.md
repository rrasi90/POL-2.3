# POL — Master System Architecture

**Document ID:** POL-ARCH-MASTER-001  
**Current Status:** CANONICAL SPECIFICATION  
**Governing Decisions:** D-001 through D-015 (Multi-Vendor MVP D-014, PostgreSQL 18 Canonical D-015, NON_CUSTODIAL_DIRECT Settlement)  
**Target Release:** POL MVP Pilot (Sprint 0 Target)  

---

## 1. Executive Summary & Purpose

This document provides the single comprehensive architectural blueprint for the **POL (پُل)** B2B FMCG platform. It bridges the mature Commerce Core (Baskets, Allocation Engine, Multi-Vendor OrderGroups, Inventory, Settlements, Disputes) with the complete Platform Core (Identity, Organizations, Memberships, Auth/Sessions, Notifications, Inbox, Admin Control Plane, Support Cases, Field Tasks, SLAs, and Observability).

An engineer building Sprint 0 must be able to navigate every domain boundary, database ownership rule, event flow, and authorization boundary directly from this document.

---

## 2. Actors & User Types

POL recognizes five primary human and automated actors:

| Actor | Category | Description | Primary Interface |
| :--- | :--- | :--- | :--- |
| **Retailer Owner / Staff** | Tenant Actor | Supermarket and grocery store operators in Ahvaz pilot. Builds unified baskets, confirms orders, receives deliveries, verifies OTP, submits direct payment proofs, and logs support inquiries or disputes. | Retailer Web/Mobile App (POL Market) |
| **Vendor Owner / Staff** | Tenant Actor | FMCG wholesalers and master distributors. Manages product listings, prices, inventory availability, reviews incoming orders, marks packing/dispatch, provides driver info, and reviews settlement summaries. | Vendor Web Portal (POL Vendor) |
| **POL Platform Admin / Ops** | Platform Actor | Central operations personnel. Manages catalog taxonomy, reviews candidate SKUs, monitors the Exception Dashboard, handles tier-2 support, and oversees dispute resolution. | Admin Control Plane (POL Ops Console) |
| **Field Activator / Visitor** | Operational Field Actor | Dedicated field agents operating in target Ahvaz districts. Registers retailer leads, verifies store locations, provides on-site training, assists with first order, and performs spot checks. | Field Operations Interface / Mobile Web |
| **System Daemon / Workers** | Automated Actor | Background asynchronous workers executing outbox event dispatch, inventory reservation expiry, vendor acceptance SLA timeout enforcement, and SMS/Push notifications. | PostgreSQL / Worker Service |

---

## 3. Organizations & Multi-Tenant Model

To support multi-user teams and strict organizational data isolation, the platform enforces a 3-tier identity hierarchy:

`	ext
Organization (Tenant Boundary)
   │
   ├── Membership (Role, Scope, Status)
   │      └── User (Credentials, Phone, Profile)
   │
   └── Business Profile (Retailer or Vendor Entity)
`

1. **Organization Types**:
   - RETAILER: Organization operating one or more retail stores.
   - VENDOR: Organization operating wholesale FMCG distribution.
   - OPERATOR: Platform operator organization (POL Core Ops).
2. **Tenant Isolation Invariants**:
   - Every operational resource (baskets, orders, deliveries, payments, settlements, invoices, support_cases) belongs strictly to an organization_id.
   - Direct database queries and API handlers must enforce WHERE organization_id = :current_tenant_id. Cross-tenant data leakage is a P0 security violation.
   - A single User may hold memberships in more than one organization (e.g., an owner with a retail branch and a small wholesale depot), but each API request operates under an explicit organization_id context passed via session token.

---

## 4. Roles & Permissions (RBAC Matrix)

| Role Code | Tenant Scope | Capabilities & Permissions |
| :--- | :--- | :--- |
| `RETAILER_OWNER` | Retailer Org | Full management: invite staff, modify store profile, place orders, confirm delivery OTP, submit payment proof, open disputes, view invoices. |
| `RETAILER_STAFF` | Retailer Org | Operational tasks: build basket, view orders, confirm delivery OTP. Restricted: cannot manage memberships or change bank accounts. |
| `VENDOR_OWNER` | Vendor Org | Full management: manage catalog offers, set prices, update inventory, accept/reject orders, assign drivers, view settlements and bank details. |
| `VENDOR_STAFF` | Vendor Org | Fulfillment tasks: review orders, mark packaged, update dispatch status. Restricted: cannot modify settlement bank accounts or manage staff. |
| `FIELD_ACTIVATOR` | Operator Org | Field force tasks: register new retailer leads, verify store coordinates, complete onboarding checklists, log field visits. Restricted: no financial access. |
| `OPS_ADMIN` | Operator Org | Daily operational management: resolve support cases, catalog SKU deduplication, review candidate products, monitor vendor SLA timers. |
| `SUPER_ADMIN` | Operator Org | Unrestricted platform control: user suspension, broadcast messaging, dispute resolution, financial adjustments, system feature flags. |

---

## 5. Architectural Domains & Core Entities

```
                               ┌───────────────────────────────────────────────┐
                               │           POL Master Architecture             │
                               └───────────────────────┬───────────────────────┘
                                                       │
         ┌─────────────────────────┬───────────────────┴───────────────────┬─────────────────────────┐
         ▼                         ▼                                       ▼                         ▼
┌──────────────────┐     ┌──────────────────┐                    ┌──────────────────┐     ┌──────────────────┐
│  Identity & Auth │     │  Commerce Core   │                    │ Fulfillment/Pay  │     │ Platform Services│
├──────────────────┤     ├──────────────────┤                    ├──────────────────┤     ├──────────────────┤
│ Organizations    │     │ Baskets & Items  │                    │ Deliveries       │     │ Notifications    │
│ Memberships      │     │ Allocation Engine│                    │ Proof of Delivery│     │ User Inbox Items │
│ Users & Sessions │     │ OrderGroups      │                    │ Direct Payments  │     │ Support Cases    │
│ User Devices     │     │ Orders & Items   │                    │ Settlements (0%) │     │ Field Tasks      │
│ OTP Challenges   │     │ Reservations     │                    │ Disputes/Refunds │     │ Admin Audit Log  │
└──────────────────┘     └──────────────────┘                    └──────────────────┘     └──────────────────┘
```

### Domain Catalog & Entity Breakdown
1. **Identity & Access Management (IAM)**:
   - `organizations`, `organization_memberships`, `users`, `user_sessions`, `user_devices`, `otp_challenges`.
2. **Catalog & Merchandising**:
   - `brands`, `categories`, `subcategories`, `products`, `product_reference_metadata`, `product_identifiers`, `media_assets`, `product_media`, `product_candidates`, `product_merge_history`, `vendor_products`, `vendor_prices`.
3. **Inventory & Reservations**:
   - `vendor_inventory`, `inventory_audit_log`, `inventory_reservations`.
4. **Basket & Procurement**:
   - `baskets` (with `version`), `basket_items`, `allocation_plans` (with `basket_version`), `allocation_items`.
5. **Orders & Group Aggregation**:
   - `order_groups`, `orders`, `order_items`, `invoices`, `invoice_items`.
6. **Fulfillment & Logistics (Option A Driver Model)**:
   - `deliveries` (stores vendor/carrier driver name, phone, vehicle info), `delivery_attempts`, `proof_of_delivery`.
7. **Direct Payments & Settlements (NON_CUSTODIAL_DIRECT)**:
   - `payments`, `payment_attempts`, `settlements` (0% pilot commission per D-006), `settlement_adjustments`.
8. **Trust, Disputes & Reputation**:
   - `disputes` (orthogonal to order_status), `refunds`, `reputations`, `reputation_snapshots`.
9. **Communication & Messaging**:
   - `notifications`, `notification_deliveries`, `user_inbox_items`, `notification_preferences`, `broadcast_messages`, `broadcast_recipients`.
10. **Customer Support & Field Operations**:
    - `support_cases`, `support_case_messages`, `support_case_assignments`, `field_tasks`.
11. **Platform Audit & Governance**:
    - `admin_audit_logs`, `outbox_events`, `domain_events_log`.

---

## 6. Domain Event Architecture & Outbox Pattern

All transactional state changes emit strongly-typed domain events within the same PostgreSQL transaction via the outbox_events table. External integrations (SMS, Push, Analytics) **never** run synchronously inside the user transaction.

`	ext
[HTTP API Request]
       │
       ▼
[PostgreSQL Transaction Begin]
   ├── 1. Apply Business State Change (e.g. Orders, Reservations)
   ├── 2. Insert Outbox Event (Payload, Event Name, Correlation ID)
[PostgreSQL Transaction Commit]
       │
       ▼ (Asynchronous Dequeue)
[Poller / Background Worker]
   ├── Read UNPUBLISHED events with SELECT FOR UPDATE SKIP LOCKED
   ├── Dispatch to Handlers (Notification Engine, Inbox Projector, Audit)
   └── Mark Event as PUBLISHED (or FAILED with retry backoff)
`

### Core Canonical Domain Events
- ORDER_GROUP_SUBMITTED, ORDER_SUBMITTED, ORDER_ACCEPTED, ORDER_REJECTED, ORDER_TIMEOUT_EXPIRED
- ORDER_DISPATCHED, DELIVERY_OTP_GENERATED, ORDER_DELIVERED, ORDER_CANCELLED
- PAYMENT_RECORDED, PAYMENT_VERIFIED, SETTLEMENT_CALCULATED, SETTLEMENT_CLOSED
- DISPUTE_OPENED, DISPUTE_RESOLVED, DISPUTE_REJECTED
- INVENTORY_RESERVATION_CREATED, INVENTORY_RESERVATION_CONSUMED, INVENTORY_RESERVATION_RELEASED, INVENTORY_RESERVATION_EXPIRED
- SUPPORT_CASE_OPENED, SUPPORT_CASE_ASSIGNED, SUPPORT_CASE_RESOLVED
- ADMIN_BROADCAST_PUBLISHED

---

## 7. External Service Providers & Fault Isolation

| Service Type | Provider Candidate (Pilot) | Isolation Strategy | Fallback / Graceful Degradation |
| :--- | :--- | :--- | :--- |
| **SMS Gateway** | Kavenegar / Magfa / Farapayamak | Outbox asynchronous worker with retry queue. | Secondary SMS provider fallback; in-app notification remains primary. |
| **Push Notifications** | WebPush / Firebase Cloud Messaging | Asynchronous outbox worker. Non-blocking. | In-App Inbox stores all unread messages permanently. |
| **Map & Geocoding** | Neshan / Balad / OpenStreetMap | Client-side map rendering; coordinates stored as static floats. | Textual address string serves as canonical fallback for delivery. |
| **Object Storage** | S3-compatible (MinIO / ArvanCloud) | Upload presigned URLs; media metadata saved in PostgreSQL. | Local filesystem storage mounted for local development and test harness. |

---

## 8. Database Ownership & Storage Guarantees

- **Database Engine**: PostgreSQL 18.4+ (Single Canonical SSoT per D-015).
- **Schema Separation**: Primary business tables live in public schema.
- **Data Integrity Invariants**:
  - UUID Primary Keys (gen_random_uuid()).
  - Strict Foreign Key referential integrity across all relationships.
  - Domain CHECK constraints on all enum/state fields.
  - Partial Unique Indexes for concurrency guards (e.g., uq_vendor_product_current_price, uq_dispute_open_per_order).
  - Row-level lock safety (SELECT FOR UPDATE) for inventory reservations and outbox processing.

---

## 9. API Surface & Protocols

The platform exposes RESTful JSON APIs adhering to standardized error handling (Exception_Handling.md) and correlation ID tracking:

1. **Retailer API (/api/v1/retailer/*)**:
   - Auth, Profile, Product Search & Catalog, Basket Management (GET/POST /basket), Allocation (POST /basket/allocate), Checkout (POST /orders/checkout), Order Tracking, Delivery OTP, Payment Proof, Disputes, Inbox, Support.
2. **Vendor API (/api/v1/vendor/*)**:
   - Auth, Catalog Offer & Pricing, Inventory Bulk Update & Barcode Drafts, Order Queue (ACCEPT, REJECT, DISPATCH), Driver Info, Settlement Statements, Support.
3. **Platform Operations API (/api/v1/admin/*)**:
   - Exception Dashboard (/admin/exceptions), Category Taxonomy Management, SKU Review & Candidate Merge, Vendor Verification Workflow, Broadcast Messaging, Support Case Assignment, Audit Logs.
4. **Field Force API (/api/v1/field/*)**:
   - Task List (GET /field/tasks), Store Visit Check-in, Retailer Onboarding Lead Submission.

---

## 10. Asynchronous Background Jobs

| Worker Job | Frequency / Trigger | Action | Failure Policy |
| :--- | :--- | :--- | :--- |
| **Outbox Event Dispatcher** | Continuous poll (1s interval) | Reads outbox_events (status = 'PENDING'), dispatches to internal event bus. | Exponential backoff (1s, 5s, 30s, 5m), max 5 retries. |
| **Vendor SLA Timeout Monitor** | Every 60 seconds | Checks orders in SUBMITTED status where 
ow() > vendor_sla_deadline. Rejects order and releases reservations. | Idempotent transition to REJECTED. |
| **Reservation Expiry Cleanup** | Every 60 seconds | Finds reservations in ACTIVE state where 
ow() > expires_at. Updates to EXPIRED and returns stock to vailable_quantity. | Atomic transaction with inventory audit log entry. |
| **Notification Push/SMS Worker** | Outbox event consumer | Sends push/SMS, records provider message ID, updates 
otification_deliveries. | Mark FAILED, queue retry or switch to fallback channel. |
| **Broadcast Dispatcher** | Event-triggered | Resolves audience segment, creates recipient snapshots, and generates notification records. | Batch processing with cursor; resume on crash. |

---

## 11. Notification & User Inbox System

1. **Inbox as Durable Store**:
   - Notifications write a permanent record to user_inbox_items for the recipient user.
   - User inbox items persist regardless of whether external SMS or Push successfully reaches the device.
2. **Preference Controls**:
   - Users can toggle Push and SMS channels per notification category (Orders, Security, Support, Marketing).
   - Critical transactional notifications (Order Confirmation, Delivery OTP, Security Alerts) bypass user opt-outs.

---

## 12. Admin Control Plane & Operations

1. **Exception-First Philosophy**:
   - The primary Admin screen is **not** a generic metric chart; it is an active queue of operational exceptions requiring human triage:
     - ORDERS_APPROACHING_SLA_TIMEOUT (Vendor has < 30 minutes remaining).
     - SUB_MOV_ALLOCATION_FAILURES (Retailer basket items that failed vendor minimums).
     - UNRESOLVED_DISPUTES (Disputes open > 24 hours).
     - OUTBOX_DELIVERY_FAILURES (Events failing external dispatch).
     - UNRESOLVED_SUPPORT_CASES (Support tickets unassigned > 1 hour).
2. **Category & Taxonomy Governance**:
   - Admin manages hierarchical Categories and Subcategories.
   - Products are validated to ensure subcategory.category_id == product.category_id.

---

## 13. Auditability, Correlation ID & Compliance

1. **Correlation ID Propagation**:
   - Every incoming HTTP request must extract or generate X-Correlation-ID.
   - The correlation_id is propagated to:
     - Application logs.
     - Database audit entries (dmin_audit_logs.correlation_id).
     - Outbox events (outbox_events.payload -> correlation_id).
     - Worker jobs and external provider metadata tags.
2. **Admin Action Auditing**:
   - Any sensitive admin action (Vendor approval/suspension, dispute resolution, refund approval, category deletion, system config change) writes an immutable record to dmin_audit_logs capturing: ctor_user_id, ction, 	arget_entity_type, 	arget_entity_id, state_before_json, state_after_json, 
eason, ip_address, 	imestamp.

---

## 14. Observability, Metrics & Pilot SLO Targets

### Core Operational Metrics
- orders_submitted_total, orders_accepted_total, orders_rejected_total, orders_timeout_total.
- asket_allocation_failure_rate (Target: < 2%).
- endor_sla_breach_rate (Target: < 5%).
- direct_payment_verification_lead_time (Target: < 4 hours).
- dispute_rate_per_order (Target: < 3%).
- 
otification_delivery_success_rate (Target: > 98%).

### Pilot SLO Targets
| Service Level Objective | Target | Measurement Window |
| :--- | :--- | :--- |
| **API Availability** | 99.5% uptime | Monthly |
| **Checkout Response Latency** | p95 < 800ms | 5-minute rolling |
| **Allocation Calculation Latency** | p95 < 400ms | 5-minute rolling |
| **Vendor Acceptance SLA Enforcement** | 100% within 120s of deadline | Continuous |
| **OTP Delivery Time** | p90 < 15 seconds | 1-hour rolling |
