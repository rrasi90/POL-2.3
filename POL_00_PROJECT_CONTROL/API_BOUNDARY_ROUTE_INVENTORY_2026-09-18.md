# POL API / Application Boundary Master Inventory — 2026-09-18

**Document ID:** `POL-API-INVENTORY-001`  
**Status:** ACTIVE / CANONICAL  
**Stage:** 07 — API/Boundary Master Inventory  
**Work ID:** EXEC50-008  
**Source snapshot PR #1:** `b3d6438fef4544a0ae356afc4a9da7a2ee2eb7a1`

## 1. Executive snapshot

- API contract inventory: **50 unique endpoint specifications** after normalizing parameter notation and excluding the duplicated absolute profile URL example.
- Actual FastAPI business routes: **21**.
- Additional operational transport routes: **2** — `/healthz`, `/readyz`.
- HTTP route coverage against the 50 documented business endpoints: **21/50**.
- `POLApplicationBoundary` exposes **29 public command/query methods**.
- HTTP currently reaches **13 boundary methods** (plus the separate authentication/session layer).
- **16 boundary methods are internal-only** today: feedback (3), support (5), referrals (2), returns/RMA (2), and operational workers (3), plus the lower-level `checkout` helper.
- Therefore Stage 07 is an inventory/reconciliation stage, not a claim that the remaining 29 contract endpoints are implemented.

## 2. Runtime route inventory

### Implemented business HTTP routes — 21

| Domain | Method | Actual FastAPI path | Boundary/transport path | Status |
|---|---|---|---|---|
| Auth | POST | `/api/v1/auth/request-otp` | authentication/session layer | HTTP_IMPLEMENTED |
| Auth | POST | `/api/v1/auth/verify-otp` | authentication/session layer | HTTP_IMPLEMENTED |
| Auth | POST | `/api/v1/auth/refresh` | authentication/session layer | HTTP_IMPLEMENTED |
| Auth | POST | `/api/v1/auth/switch-organization` | authentication/session layer | HTTP_IMPLEMENTED |
| Auth | DELETE | `/api/v1/auth/sessions/current` | authentication/session layer | HTTP_IMPLEMENTED |
| Auth | DELETE | `/api/v1/auth/sessions/{session_id}` | authentication/session layer | HTTP_IMPLEMENTED |
| Basket | POST | `/api/v1/baskets` | `basket_create` | HTTP_IMPLEMENTED |
| Basket | POST | `/api/v1/baskets/{basket_id}/items` | `basket_add_item` | HTTP_IMPLEMENTED |
| Basket | POST | `/api/v1/baskets/{basket_id}/allocation-preview` | `basket_allocation_preview` | HTTP_IMPLEMENTED |
| Order | POST | `/api/v1/orders` | `checkout_from_allocation_plan` | HTTP_IMPLEMENTED |
| Order | POST | `/api/v1/orders/{order_id}/accept` | `vendor_order_accept` | HTTP_IMPLEMENTED |
| Order | POST | `/api/v1/orders/{order_id}/reject` | `vendor_order_reject` | HTTP_IMPLEMENTED |
| Order | POST | `/api/v1/orders/{order_id}/partial-acceptance-proposals` | `vendor_partial_acceptance_propose` | HTTP_IMPLEMENTED |
| Order | POST | `/api/v1/orders/{order_id}/partial-acceptance-proposals/{proposal_id}/approve` | `retailer_partial_acceptance_approve` | HTTP_IMPLEMENTED |
| Order | POST | `/api/v1/orders/{order_id}/partial-acceptance-proposals/{proposal_id}/decline` | `retailer_partial_acceptance_decline` | HTTP_IMPLEMENTED |
| Profile | GET | `/api/v1/profile` | `profile_get` | HTTP_IMPLEMENTED |
| Profile | PUT | `/api/v1/profile` | `profile_update` | HTTP_IMPLEMENTED |
| Profile | GET | `/api/v1/profile/completion` | `profile_completion` | HTTP_IMPLEMENTED |
| Profile | GET | `/api/v1/profile/context` | `profile_get` (resolved profile + membership + persona context) | HTTP_IMPLEMENTED / SHARED BOUNDARY |
| Membership | GET | `/api/v1/membership/profile` | `profile_get` | HTTP_IMPLEMENTED |
| Membership | PUT | `/api/v1/membership/profile` | `profile_membership_update` | HTTP_IMPLEMENTED |

### Operational transport routes — 2

| Method | Path | Status |
|---|---|---|
| GET | `/healthz` | OPERATIONAL |
| GET | `/readyz` | OPERATIONAL |

## 3. 50-endpoint contract matrix

| # | Canonical endpoint | Status | Current owner/path |
|---:|---|---|---|
| 1 | GET `/api/v1/products/search` | CONTRACT_ONLY | catalog applicationization |
| 2 | POST `/api/v1/products/match-barcode` | CONTRACT_ONLY | catalog applicationization |
| 3 | POST `/api/v1/product-candidates` | CONTRACT_ONLY | catalog applicationization |
| 4 | POST `/api/v1/vendors/inventory/continuous-scan` | CONTRACT_ONLY | vendor catalog/inventory |
| 5 | POST `/api/v1/vendors/inventory/publish` | CONTRACT_ONLY | vendor catalog/inventory |
| 6 | POST `/api/v1/baskets` | HTTP_IMPLEMENTED | `basket_create` |
| 7 | POST `/api/v1/baskets/{id}/items` | HTTP_IMPLEMENTED | `basket_add_item` |
| 8 | POST `/api/v1/baskets/{id}/allocation-preview` | HTTP_IMPLEMENTED | `basket_allocation_preview` |
| 9 | POST `/api/v1/orders` | HTTP_IMPLEMENTED | `checkout_from_allocation_plan` |
| 10 | POST `/api/v1/orders/{id}/accept` | HTTP_IMPLEMENTED | `vendor_order_accept` |
| 11 | POST `/api/v1/orders/{id}/reject` | HTTP_IMPLEMENTED | `vendor_order_reject` |
| 12 | POST `/api/v1/orders/{id}/partial-acceptance-proposals` | HTTP_IMPLEMENTED | `vendor_partial_acceptance_propose` |
| 13 | POST `/api/v1/orders/{id}/partial-acceptance-proposals/{proposal_id}/approve` | HTTP_IMPLEMENTED | `retailer_partial_acceptance_approve` |
| 14 | POST `/api/v1/orders/{id}/partial-acceptance-proposals/{proposal_id}/decline` | HTTP_IMPLEMENTED | `retailer_partial_acceptance_decline` |
| 15 | POST `/api/v1/orders/{id}/dispatch` | CONTRACT_ONLY | dispatch/delivery runtime |
| 16 | POST `/api/v1/orders/{id}/deliver` | CONTRACT_ONLY | proof-of-delivery boundary |
| 17 | POST `/api/v1/orders/{id}/payments/direct-transfer` | CONTRACT_ONLY | payment evidence API |
| 18 | POST `/api/v1/orders/{id}/payments/{payment_id}/verify` | CONTRACT_ONLY | payment evidence API |
| 19 | POST `/api/v1/orders/{id}/disputes` | CONTRACT_ONLY | dispute/RMA HTTP |
| 20 | PATCH `/api/v1/disputes/{id}/resolve` | CONTRACT_ONLY | dispute/RMA HTTP |
| 21 | POST `/api/v1/auth/request-otp` | HTTP_IMPLEMENTED | authentication/session layer |
| 22 | POST `/api/v1/auth/verify-otp` | HTTP_IMPLEMENTED | authentication/session layer |
| 23 | POST `/api/v1/auth/refresh` | HTTP_IMPLEMENTED | authentication/session layer |
| 24 | POST `/api/v1/auth/switch-organization` | HTTP_IMPLEMENTED | authentication/session layer |
| 25 | DELETE `/api/v1/auth/sessions/current` | HTTP_IMPLEMENTED | authentication/session layer |
| 26 | DELETE `/api/v1/auth/sessions/{id}` | HTTP_IMPLEMENTED | authentication/session layer |
| 27 | POST `/api/v1/support/cases` | CONTRACT_ONLY | `support_create` exists internal-only |
| 28 | POST `/api/v1/support/cases/{id}/messages` | CONTRACT_ONLY | `support_message` exists internal-only |
| 29 | POST `/api/v1/support/cases/{id}/assign` | CONTRACT_ONLY | `support_assign` exists internal-only |
| 30 | PATCH `/api/v1/support/cases/{id}/status` | CONTRACT_ONLY | `support_transition` exists internal-only |
| 31 | GET `/api/v1/inbox/items` | CONTRACT_ONLY | notification HTTP |
| 32 | PATCH `/api/v1/inbox/items/{id}/read` | CONTRACT_ONLY | notification HTTP |
| 33 | PATCH `/api/v1/inbox/items/read-all` | CONTRACT_ONLY | notification HTTP |
| 34 | GET `/api/v1/notifications/preferences` | CONTRACT_ONLY | notification HTTP |
| 35 | PUT `/api/v1/notifications/preferences` | CONTRACT_ONLY | notification HTTP |
| 36 | POST `/api/v1/admin/broadcasts` | CONTRACT_ONLY | admin/ops HTTP |
| 37 | POST `/api/v1/admin/broadcasts/{id}/dispatch` | CONTRACT_ONLY | admin/ops HTTP |
| 38 | GET `/api/v1/invoices` | CONTRACT_ONLY | invoice/settlement HTTP |
| 39 | GET `/api/v1/invoices/{id}` | CONTRACT_ONLY | invoice/settlement HTTP |
| 40 | GET `/api/v1/admin/exceptions/dashboard` | CONTRACT_ONLY | ops dashboard |
| 41 | POST `/api/v1/admin/sla-overrides` | CONTRACT_ONLY | ops SLA boundary |
| 42 | GET `/api/v1/admin/audit-logs` | CONTRACT_ONLY | audit HTTP |
| 43 | GET `/api/v1/categories` | CONTRACT_ONLY | catalog HTTP |
| 44 | POST `/api/v1/admin/categories` | CONTRACT_ONLY | catalog admin HTTP |
| 45 | PATCH `/api/v1/admin/categories/{id}` | CONTRACT_ONLY | catalog admin HTTP |
| 46 | GET `/api/v1/profile` | HTTP_IMPLEMENTED | `profile_get` |
| 47 | PUT `/api/v1/profile` | HTTP_IMPLEMENTED | `profile_update` |
| 48 | GET `/api/v1/profile/completion` | HTTP_IMPLEMENTED | `profile_completion` |
| 49 | PUT `/api/v1/membership/profile` | HTTP_IMPLEMENTED | `profile_membership_update` |
| 50 | GET `/api/v1/profile/context` | HTTP_IMPLEMENTED / SHARED BOUNDARY | `profile_get` |

## 4. ApplicationBoundary-only commands

These are implemented as canonical Python commands but have no current FastAPI route:

- `checkout` — lower-level checkout helper used by `checkout_from_allocation_plan`.
- Feedback: `feedback_list`, `feedback_admin_inbox`, `feedback_reply`.
- Support: `support_create`, `support_get`, `support_message`, `support_assign`, `support_transition`.
- Referral: `create_vendor_referral`, `redeem_vendor_referral`.
- Return/RMA: `return_request`, `return_transition`.
- Ops workers: `process_vendor_acceptance_timeouts`, `reconcile_payments`, `deliver_external_notifications`.

These are **BOUNDARY_READY / NOT_YET_HTTP**, not production-ready claims.

## 5. Contract/document inconsistencies captured

1. `API_Contracts.md` contains the `POST /orders` contract twice in the raw endpoint extraction; the canonical inventory counts it once.
2. The profile contract includes both a relative and an absolute `GET /api/v1/profile` example; the inventory counts one endpoint.
3. Contract path notation mixes `:id` and the actual FastAPI `{id}` style; inventory normalizes both.
4. The application boundary is deliberately transport-neutral, while D-020 makes FastAPI the production HTTP adapter. This is not a second runtime.
5. `GET /api/v1/profile/context` currently reuses `profile_get`; the canonical profile service already returns user profile + active membership + persona context, so this is classified as shared-boundary coverage rather than a missing capability.
6. The remaining contract-only endpoints require applicationization work in the later Stage 13–37 sequence; Stage 07 does not silently mark them implemented.

## 6. Ordered applicationization backlog

| Order | Workstream | Primary stages |
|---:|---|---|
| 1 | Catalog/search/category HTTP | 13–15 |
| 2 | Pricing/inventory HTTP | 16–18 |
| 3 | Order query/timeline + fulfillment/delivery/POD | 20–25 |
| 4 | Payment evidence, invoice, settlement, reconciliation | 26–29 |
| 5 | Dispute/RMA + support | 30–31 |
| 6 | Notification/inbox/provider HTTP | 32–33 |
| 7 | Ops/admin/referral/onboarding | 34–35 |
| 8 | Analytics/KPI telemetry | 36–37 |

**Exit condition for Stage 07:** every documented MVP endpoint has a status, owner path and explicit next-stage assignment; no contract-only endpoint is represented as live HTTP.
