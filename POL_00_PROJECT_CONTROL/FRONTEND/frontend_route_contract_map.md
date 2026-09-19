# POL MVP — Frontend Route-to-Contract Master Map
**Stage:** 38  
**Date:** 2026-09-19  
**Status:** COMPLETE

---

## Purpose
Every canonical screen maps to: route → persona → context → data → command → state → analytics → notification → recovery.

---

## Persona Definitions

| Persona | Auth Role | Dashboard |
|---------|-----------|-----------|
| Super Admin | `ADMIN_SUPER` | `/admin` |
| Ops Agent | `OPS_AGENT` | `/ops` |
| Field Activator | `FIELD_ACTIVATOR` | `/field` |
| Vendor Owner | `VENDOR_OWNER` | `/vendor` |
| Vendor Staff | `VENDOR_STAFF` | `/vendor` |
| Retailer Owner | `RETAILER_OWNER` | `/retailer` |
| Retailer Staff | `RETAILER_STAFF` | `/retailer` |

---

## Screen → Route → Contract Map

### 1. Authentication
| Screen | Route | Persona | API | State | Notes |
|--------|-------|---------|-----|-------|-------|
| Login (phone) | `/auth/login` | ALL | POST `/api/v1/auth/request-otp` | `otp_sent` | OTP 6-digit, TTL 120s |
| Verify OTP | `/auth/verify` | ALL | POST `/api/v1/auth/verify-otp` | `authenticated` | max 5 attempts, lockout 10min |
| Refresh Token | (implicit) | ALL | POST `/api/v1/auth/refresh` | `token_refreshed` | 30d refresh session |

### 2. Vendor Dashboard
| Screen | Route | Persona | API | State | Analytics |
|--------|-------|---------|-----|-------|-----------|
| Vendor Overview | `/vendor` | VENDOR_OWNER, VENDOR_STAFF | GET `/api/v1/vendor/profile` | `loaded` | `vendor_continuation` |
| Vendor Orders | `/vendor/orders` | VENDOR_OWNER, VENDOR_STAFF | GET `/api/v1/vendor/orders` | `loaded` | `otif` |
| Vendor Inventory | `/vendor/inventory` | VENDOR_OWNER | GET `/api/v1/vendor/inventory` | `loaded` | `catalog_coverage` |
| Vendor Settlements | `/vendor/settlements` | VENDOR_OWNER | GET `/api/v1/vendors/settlements` | `loaded` | `cost_to_serve` |

### 3. Retailer Dashboard
| Screen | Route | Persona | API | State | Analytics |
|--------|-------|---------|-----|-------|-----------|
| Retailer Overview | `/retailer` | RETAILER_OWNER, RETAILER_STAFF | GET `/api/v1/retailer/profile` | `loaded` | `repeat_rate` |
| Catalog Browse | `/retailer/catalog` | RETAILER_OWNER, RETAILER_STAFF | GET `/api/v1/catalog` | `loaded` | `catalog_coverage` |
| Place Order | `/retailer/orders/new` | RETAILER_OWNER | POST `/api/v1/orders` | `created` | `gmv`, `aov` |
| Order History | `/retailer/orders` | RETAILER_OWNER, RETAILER_STAFF | GET `/api/v1/orders` | `loaded` | `gmv` |
| Order Detail | `/retailer/orders/:id` | RETAILER_OWNER, RETAILER_STAFF | GET `/api/v1/orders/:id` | `loaded` | — |
| Invoices | `/retailer/invoices` | RETAILER_OWNER | GET `/api/v1/invoices` | `loaded` | — |
| Notifications | `/retailer/notifications` | RETAILER_OWNER, RETAILER_STAFF | GET `/api/v1/notifications` | `loaded` | — |
| Preferences | `/retailer/notifications/preferences` | RETAILER_OWNER | GET/PUT `/api/v1/notifications/preferences` | `loaded` | — |

### 4. Field Activator
| Screen | Route | Persona | API | State | Analytics |
|--------|-------|---------|-----|-------|-----------|
| Field Tasks | `/field/tasks` | FIELD_ACTIVATOR, OPS_AGENT | GET `/api/v1/field/tasks` | `loaded` | `self_service_rate` |
| Task Detail | `/field/tasks/:id` | FIELD_ACTIVATOR, OPS_AGENT | GET `/api/v1/field/tasks/:id` | `loaded` | — |
| Update Task | (inline) | FIELD_ACTIVATOR, OPS_AGENT | PATCH `/api/v1/field/tasks/:id` | `updated` | — |

### 5. Ops Dashboard
| Screen | Route | Persona | API | State | Analytics |
|--------|-------|---------|-----|-------|-----------|
| Audit Logs | `/ops/audit-logs` | OPS_AGENT, ADMIN_SUPER | GET `/api/v1/admin/audit-logs` | `loaded` | — |
| Exceptions Dashboard | `/ops/exceptions` | OPS_AGENT, ADMIN_SUPER | GET `/api/v1/admin/exceptions/dashboard` | `loaded` | — |
| Reconciliation | `/ops/reconciliation` | OPS_AGENT | GET `/api/v1/finance/reconciliation` | `loaded` | — |
| Support Cases | `/ops/support` | OPS_AGENT | GET `/api/v1/support/cases` | `loaded` | — |
| Referrals | `/ops/referrals` | OPS_AGENT | GET `/api/v1/referrals` | `loaded` | `cac` |

### 6. Admin Dashboard
| Screen | Route | Persona | API | State | Analytics |
|--------|-------|---------|-----|-------|-----------|
| Users | `/admin/users` | ADMIN_SUPER | (Admin API) | `loaded` | — |
| Organizations | `/admin/orgs` | ADMIN_SUPER | (Admin API) | `loaded` | — |

---

## Notification Events

| Event | Template | Channel | Persona |
|-------|----------|---------|---------|
| `ORDER_ACCEPTED` | order_accepted_template | PUSH, INBOX | RETAILER_OWNER |
| `ORDER_DISPATCHED` | order_dispatched_template | PUSH, SMS, INBOX | RETAILER_OWNER |
| `ORDER_DELIVERED` | order_delivered_template | PUSH, INBOX | RETAILER_OWNER |
| `PAYMENT_RECEIVED` | payment_received_template | PUSH, INBOX | VENDOR_OWNER |
| `FIELD_TASK_ASSIGNED` | field_task_assigned_template | PUSH, SMS | FIELD_ACTIVATOR |
| `SUPPORT_CASE_UPDATED` | support_case_updated_template | PUSH, INBOX | RETAILER_OWNER, VENDOR_OWNER |

---

## Recovery Patterns

| Error State | Recovery Action | Route |
|-------------|-----------------|-------|
| 401 Unauthorized | Redirect to login | `/auth/login` |
| 403 Forbidden | Show "Access Denied" | current page |
| 404 Not Found | Show "Not Found" | `/404` |
| 500 Server Error | Show "Something went wrong" | current page + retry |
| Network Error | Show "Offline" banner | current page |
| OTP Expired | Resend OTP | `/auth/login` |
| Order Conflict | Refresh + toast | current page |

---

## State Management Contract

| Domain | State Shape | Source API | Refresh Trigger |
|--------|-------------|------------|-----------------|
| `auth` | `{ user, token, org }` | `/auth/*` | login/refresh |
| `orders` | `{ list, current, filters }` | `/orders` | pull-to-refresh |
| `vendor` | `{ profile, inventory, orders }` | `/vendor/*` | background sync |
| `retailer` | `{ profile, catalog, orders }` | `/retailer/*` | background sync |
| `field` | `{ tasks, currentTask }` | `/field/*` | polling (30s) |
| `notifications` | `{ items, preferences }` | `/notifications` | push notification |
| `support` | `{ cases, currentCase }` | `/support/*` | real-time (WebSocket future) |
