# POL MVP — API MAP

**Authority:** `POL_00_PROJECT_CONTROL/API_BOUNDARY_ROUTE_INVENTORY_2026-09-18.md` (50-endpoint contract) + **actual** FastAPI routes on `origin/research-hardening-2026-09-14` `scripts/api/**` + `API_APPLICATION_BOUNDARY.md`.  
**Rule:** No endpoint outside this map without adding a sourced row first (CONTRACT_ONLY or REAL). Never invent fields.

---

## 1. Envelope (authoritative — from `scripts/api/errors.py`)

**Success:**
```json
{ "success": true, "data": <payload> }
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "STRING_CODE",
    "message": "Human message.",
    "details": {},
    "timestamp": "ISO-8601-Z"
  }
}
```

Source: `scripts/api/errors.py` → `success_payload` / `error_payload`.  
HTTP may also set `X-Correlation-ID`.

**Pagination (where used):** follow response schema returned by the specific route (orders list uses `{data,total,offset,limit}` style per backend tests/queries — confirm per endpoint when wiring; do not assume beyond this note).

**Auth:** `Authorization: Bearer <access_token>`; 15-min access / 30-day refresh (D-018). Refresh-token rotation remains OPEN; current implementation reuses the stored refresh-token hash.

---

## 2. Status legend

| Tag | Meaning |
|-----|---------|
| `REAL` | Implemented FastAPI route (verified in `scripts/api/routes/*` on research-hardening) |
| `CONTRACT` | In 50-endpoint inventory but not HTTP-implemented → **mock allowed** (same contract) |
| `BOUNDARY` | Python boundary method, no HTTP → mock or GAP per screen need |
| `GAP` | Needed by screen but no contract/behavior definable from canon |
| `OPS` | Operational transport (health) |

---

## 3. REAL routes (prefix all with `/api/v1`)

### 3.1 Auth — `scripts/api/routes/auth.py` (`/auth`)

| Method | Path | Notes |
|--------|------|-------|
| POST | `/auth/request-otp` | OTP 4-digit D-018; returns otp_request_id, TTL |
| POST | `/auth/verify-otp` | returns tokens + profile context |
| POST | `/auth/refresh` | issues a new access token; **refresh-token rotation is NOT implemented** (D-018 policy remains OPEN) |
| POST | `/auth/switch-organization` | |
| DELETE | `/auth/sessions/current` | |
| DELETE | `/auth/sessions/{session_id}` | |
| POST | `/auth/logout-all` | |

### 3.2 Profile / membership — `profile.py`

| Method | Path |
|--------|------|
| GET | `/profile` |
| GET | `/profile/completion` |
| GET | `/profile/context` |
| PUT | `/profile` |
| GET/PUT | `/membership/profile` (membership_router prefix `/membership`) |

### 3.3 Baskets — `baskets.py` (`/baskets`)

| Method | Path |
|--------|------|
| POST | `/baskets` |
| POST | `/baskets/{basket_id}/items` |
| POST | `/baskets/{basket_id}/allocation-preview` |

### 3.4 Catalog — `catalog.py` (`/catalog`)

| Method | Path |
|--------|------|
| GET | `/catalog/search` |
| GET | `/catalog/categories` |
| GET | `/catalog/products/{product_id}` |
| GET | `/catalog/products/{product_id}/vendors` |
| GET | `/catalog/products/{product_id}/compare-prices` |
| GET | `/catalog/products/{product_id}/compare-inventory` |

### 3.4.1 Canonical public catalog routes

| Method | Path |
|--------|------|
| GET | `/products/search` |
| POST | `/products/match-barcode` |
| POST | `/product-candidates` |
| GET | `/categories` |

### 3.5 Unified search — `catalog_search.py` (`/search`)

| Method | Path |
|--------|------|
| GET | `/search` |

### 3.6 Vendor catalog — `vendor_catalog.py` (`/catalog/vendors`)

| Method | Path |
|--------|------|
| GET/POST | `/catalog/vendors/products` |
| PATCH | `/catalog/vendors/products/{vendor_product_id}` |
| GET/POST | `/catalog/vendors/products/{vendor_product_id}/prices` |
| GET | `/catalog/vendors/products/{vendor_product_id}/prices/current` |
| GET/PATCH | `/catalog/vendors/products/{vendor_product_id}/inventory` |

### 3.7 Daily inventory — `daily_inventory.py` (`/inventory/daily`)

| Method | Path |
|--------|------|
| GET | `/inventory/daily/{confirmation_date}` |
| POST | `/inventory/daily/{confirmation_date}/confirm` |
| POST | `/inventory/daily/{confirmation_date}/confirm-with-changes` |

### 3.8 Orders — `orders.py` (`/orders`)

| Method | Path |
|--------|------|
| POST | `/orders` | checkout |
| GET | `/orders` | list (query params per `OrderQueryParams`) |
| GET | `/orders/{order_id}` |
| GET | `/orders/{order_id}/items` |
| GET | `/orders/{order_id}/timeline` |
| GET | `/orders/group/{order_group_id}` |
| GET | `/orders/group/{order_group_id}/orders` |
| POST | `/orders/{order_id}/accept` |
| POST | `/orders/{order_id}/reject` |
| POST | `/orders/{order_id}/partial-acceptance-proposals` | Idempotency-Key UUIDv4 required |
| POST | `/orders/{order_id}/partial-acceptance-proposals/{proposal_id}/approve` | R-09C; no GET list → G-021 |
| POST | `/orders/{order_id}/partial-acceptance-proposals/{proposal_id}/decline` | optional `{reason≤1000}` |
| POST | `/orders/{order_id}/preparing` |
| POST | `/orders/{order_id}/ready` |
| POST | `/orders/{order_id}/dispatch` |
| POST | `/orders/{order_id}/deliver` | DeliveryConfirmRequest; otp pattern `^\d{4}$` (D-018; G-022 RESOLVED) |
| GET | `/orders/{order_id}/delivery` | R-09D |
| GET | `/orders/{order_id}/delivery/proof` | R-09E; may return `{message:"No proof…"}` |
| POST/GET | `/orders/{order_id}/delivery-exceptions` |
| GET/PATCH | `/orders/delivery-exceptions/{exception_id}` (+ `/resolve`, `/escalate`) |
| POST/GET | `/orders/{order_id}/payments/evidence` |
| POST | `/orders/{order_id}/payments/verify` |

### 3.9 Returns / disputes

| Method | Path | File |
|--------|------|------|
| POST/GET | `/orders/{order_id}/returns` | returns.py |
| POST/GET | `/orders/{order_id}/disputes` | disputes.py |

### 3.10 Support — `support.py` (`/support/cases`)

| Method | Path |
|--------|------|
| POST/GET | `/support/cases` |
| GET | `/support/cases/{case_id}` |
| POST | `/support/cases/{case_id}/messages` |
| POST | `/support/cases/{case_id}/assign` | canonical assignment |
| PATCH | `/support/cases/{case_id}/status` | canonical status transition |
| PATCH | `/support/cases/{case_id}` | legacy-compatible status transition alias |

### 3.11 Finance — `finance.py`

| Method | Path |
|--------|------|
| GET | `/invoices` |
| GET | `/invoices/{invoice_id}` (as implemented) |
| GET | `/vendors/settlements` |
| GET | `/settlements/{settlement_id}` |
| GET | `/orders/{order_id}/invoices` (order_invoice_router on `/orders`) |

### 3.12 Reconciliation — `reconciliation.py`

| Method | Path |
|--------|------|
| GET | `/finance/reconciliation` |
| GET | `/finance/reconciliation/{case_id}` |
| PATCH | `/finance/reconciliation/{case_id}/resolve` |

### 3.13 Admin — `admin.py` (`/admin`)

| Method | Path |
|--------|------|
| GET | `/admin/audit-logs` |
| GET | `/admin/exceptions/dashboard` |
| POST | `/admin/broadcasts` |
| POST | `/admin/broadcasts/{broadcast_id}/dispatch` |
| POST | `/admin/categories` |
| PATCH | `/admin/categories/{category_id}` |

### 3.14 Referrals — `referrals.py`

| Method | Path |
|--------|------|
| POST/GET | `/referrals` |
| GET | `/referrals/{referral_id}` |
| POST | `/referrals/{referral_id}/redeem` |

### 3.15 Notifications — `notifications.py` (`/notifications`)

| Method | Path |
|--------|------|
| GET | `/notifications` | notification projection including read/deep-link state |
| GET/PUT | `/notifications/preferences` |

**Note:** Canonical inbox routes `/inbox/items*` are implemented alongside `/notifications*`; both are real HTTP surfaces and are covered by notification transport tests.

### 3.16 Field — `field.py` (`/field`)

| Method | Path |
|--------|------|
| GET/POST | `/field/tasks` |
| GET/PATCH | `/field/tasks/{task_id}` |

### 3.17 Vendor storefront — `vendor_storefront.py` (`/storefront`)

| Method | Path |
|--------|------|
| GET | `/storefront/vendors` |
| GET | `/storefront/vendors/{vendor_id}` |
| GET | `/storefront/vendors/{vendor_id}/products` |

### 3.18 Operational

| Method | Path |
|--------|------|
| GET | `/healthz` |
| GET | `/readyz` |

---

## 4. CONTRACT-only (from 50-endpoint inventory — mock with same contract)

| # | Endpoint | Use |
|---|----------|-----|
| 4 | POST `/api/v1/vendors/inventory/continuous-scan` | VD-16 — CONTRACT_ONLY; scan-session semantics remain open |
| 5 | POST `/api/v1/vendors/inventory/publish` | VD-01 publish — CONTRACT_ONLY; publish transition semantics remain open |
| 17–20 | payments/disputes variants | partially REAL; exact direct-transfer/payment-id verify and dispute-resolve paths remain open |
| 41 | POST `/api/v1/admin/sla-overrides` | CONTRACT_ONLY; canonical deadline column name requires clarification |

Any screen needing a `CONTRACT` row before backend HTTP exists → **MOCK adapter** (same method/path/envelope), tagged `MOCK` in use-notes; no business rules in mock.

---

## 5. BOUNDARY-ready (no HTTP; mock or UI-only if screen requires)

feedback_*, support_* (HTTP now REAL for cases), referral (HTTP REAL), return_request/return_transition (partial HTTP REAL for create/list by order), workers (not client-facing).

---

## 6. Screen → API dependency summary

| Screen family | Primary REAL APIs | MOCK/CONTRACT needs |
|---------------|-------------------|---------------------|
| Auth/OTP | auth/* | — |
| Profile | profile/*, membership/* | — |
| Catalog browse/detail | catalog/*, search | barcode match if scan UI |
| Vendor storefront browse | storefront/* | — |
| Basket/allocation/checkout | baskets/*, POST orders | — |
| Order list/detail/group/timeline | orders GET/* | — |
| Vendor accept/reject/partial | orders accept/reject/partial | — |
| Fulfillment dispatch/POD | orders preparing/ready/dispatch/deliver | handoff UX (D-023) |
| Returns/disputes | orders returns/disputes | — |
| Support | support/cases/* | — |
| Notifications | notifications/* | inbox path conflict if contract-literal |
| Preferences | notifications/preferences | — |
| Vendor catalog/price/inventory | catalog/vendors/*, inventory/daily/* | continuous-scan/publish CONTRACT |
| Invoices/settlements | finance routes | — |
| Reconciliation | finance/reconciliation | — |
| Referrals | referrals/* | — |
| Field tasks | field/tasks* | — |
| Admin audit/exceptions | admin/* | users/orgs administration remains GAP; broadcasts and categories admin are REAL |
| Pilot analytics O-09 | **GAP** (no analytics HTTP) | MOCK read-model or GAP |
| Vendor customers V-09 | **GAP/CONTRACT** (no list API found) | GAP → mock list from orders if needed |
| Staff/access V-11 | **GAP** | GAP |
| Permission mgmt | **GAP** | GAP |

---

## 7. Change control

Adding a row requires: source (inventory #, route file path, or decision ID) + status REAL|CONTRACT|BOUNDARY|GAP.  
Client must not call paths absent from this file.
