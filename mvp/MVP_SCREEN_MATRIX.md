# POL MVP — SCREEN MATRIX

**Sources:** doc 22 §5–9; doc 30 (R-*); doc 31 (V/O/F/C); Master Tree 50 §7–11 + §38 roles; route map (research-hardening) + 2026-09-20 amendment; DECISION_REGISTER.  
**Status legend:** `IMPLEMENTED` | `VERIFIED` | `BLOCKED_EXTERNAL` | `GAP` | `NOT_APPLICABLE`  
**All screens start `GAP` or `IMPLEMENTED` at Gate 0 = not started → use `NOT_STARTED` equivalent: status `GAP` only if spec incomplete; otherwise leave status `PENDING_BUILD` until Phase 2 — **for Gate 0, status column = `PENDING`** (pre-implementation; not one of the five run-state values until build begins).  
**Role context:** `PUBLIC_ANON` for corporate; authenticated roles otherwise.

**Evidence fields required for VERIFIED:** source · route · API source · implementation path · verification command/result · last QA cycle · status.

---

## A. Shared / Auth

| ID | Title | Route (canonical/prop) | Role/context | Primary APIs (API_MAP) | Source | Status |
|----|-------|------------------------|--------------|------------------------|--------|--------|
| SH-AUTH-01 | Login phone + OTP request | `/auth/login` | PUBLIC_ANON → all | POST `/auth/request-otp` | route map §1; D-018; doc 22 §3.1 | PENDING |
| SH-AUTH-02 | Verify OTP (4-digit) | `/auth/verify` | PUBLIC_ANON → all | POST `/auth/verify-otp` | D-018; route map (OTP digits → 4) | PENDING |
| SH-AUTH-03 | Refresh (implicit) | (client) | all | POST `/auth/refresh` | route map §1 | PENDING |
| SH-PROFILE-01 | Account / profile | `/profile` | authenticated | GET/PUT `/profile`, GET `/profile/context` | route map; R-13; V-12 | PENDING |
| SH-NOTIF-01 | Notifications inbox | `/notifications` | authenticated | GET `/notifications` | route map (path conflict G-004) | PENDING |
| SH-NOTIF-02 | Notification preferences | `/notifications/preferences` | authenticated | GET/PUT `/notifications/preferences` | route map | PENDING |

---

## B. Retailer (R / RT)

| ID | Title | Route | Role | Primary APIs | Source | Status |
|----|-------|-------|------|--------------|--------|--------|
| R-01 | Onboarding / activation | `/auth/*` progressive | RETAILER_OWNER | auth + profile context | doc 22 L222–233; doc 30 R-01A–G; MT RT-01 | PENDING |
| R-02 | Home / operational hub | `/retailer` | RETAILER_OWNER/STAFF | GET `/orders` (actions), profile | doc 22 L235–244; MT RT-02 | PENDING |
| R-03 | Search / catalog | `/retailer/catalog` | RETAILER_* | GET `/catalog/search`, `/catalog/categories`, GET `/search` | doc 22 L246–260; MT RT-06 | PENDING |
| R-03B | Barcode / SKU entry | (in catalog) | RETAILER_* (+scan perm) | POST `products/match-barcode` **CONTRACT** → MOCK/GAP | D-028; amendment | PENDING |
| R-04 | Product detail | `/retailer/catalog/[id]` | RETAILER_* | GET `/catalog/products/{id}`, `/vendors`, compare-* | doc 22 L262–275; MT RT-07 | PENDING |
| R-05 | Vendor comparison | (in product) | RETAILER_* | compare-prices, compare-inventory | doc 22 L277–289; MT RT-07 | PENDING |
| R-06 | Multi-vendor basket | `/retailer/basket` | RETAILER_* | POST `/baskets*` | doc 22 L291–302; MT RT-03; D-014 | PENDING |
| R-07 | Allocation review | `/retailer/checkout/allocation` | RETAILER_* | POST `/baskets/{id}/allocation-preview` | doc 22 L304–314; MT RT-14 | PENDING |
| R-08 | Checkout / confirmation | `/retailer/checkout` | RETAILER_* | POST `/orders` | doc 22 L316–325; MT RT-04 | PENDING |
| R-09 | Order group detail | `/retailer/orders/group/[id]` | RETAILER_* | GET `/orders/group/{id}`, `/orders/group/{id}/orders` | doc 22 L327–341; MT RT-15; D-022 | PENDING |
| R-09B | Child order detail | `/retailer/orders/[id]` | RETAILER_* | GET `/orders/{id}`, items, timeline | doc 22; MT RT-08 | PENDING |
| R-09C | Partial acceptance review | (order detail) | RETAILER_OWNER | approve/decline partial proposals | MT RT-20 | PENDING |
| R-09D | Delivery tracking | (order detail) | RETAILER_* | GET `/orders/{id}/delivery` | MT RT-05 | PENDING |
| R-09E | Handoff / receiver confirm | (order or link) | receiver | GET delivery/proof; confirm patterns | MT RT-19; D-023 | PENDING |
| R-10 | Reorder / history | `/retailer/orders` | RETAILER_* | GET `/orders` | doc 22 L343–349; MT RT-10 | PENDING |
| R-11 | Returns / disputes | `/retailer/orders/[id]/returns` | RETAILER_OWNER | POST/GET `/orders/{id}/returns`, disputes | doc 22 L351–353; MT RT-09 | PENDING |
| R-12 | Support | `/retailer/support` | RETAILER_* | `/support/cases*` | doc 22 L355–363; MT RT-13 | PENDING |
| R-13 | Account | `/profile` (+ org) | RETAILER_* | profile/context; staff mgmt → GAP G-010 | doc 22 L365–373; MT RT-12 | PENDING |
| R-16 | Financial activity | `/retailer/finance` | RETAILER_OWNER | invoices/settlements visibility D-021 | MT RT-16; D-021 | PENDING |
| R-17 | Vendor search | `/retailer/vendors` | RETAILER_* | GET `/storefront/vendors` | MT RT-17; D-024 | PENDING |
| R-18 | Vendor storefront | `/retailer/vendors/[id]` | RETAILER_* | GET storefront vendor + products | MT RT-18; D-024 | PENDING |

---

## C. Vendor (V / VD)

| ID | Title | Route | Role | Primary APIs | Source | Status |
|----|-------|-------|------|--------------|--------|--------|
| V-01 | Dashboard (queue-first) | `/vendor` | VENDOR_* | GET `/orders` (filters), inventory stale | doc 22 L377–387 | PENDING |
| V-02 | Orders queue | `/vendor/orders` | VENDOR_* | GET `/orders` | doc 22 L389–399; MT VD-02 | PENDING |
| V-03 | Order detail + accept/reject/partial | `/vendor/orders/[id]` | VENDOR_* | accept/reject/partial HTTP | doc 22 L401–410; MT VD-02/18 | PENDING |
| V-04 | Catalog | `/vendor/catalog` | VENDOR_* | `/catalog/vendors/products*` | doc 22 L412–420; MT VD-05 | PENDING |
| V-05 | Pricing | `/vendor/catalog/[id]/prices` | VENDOR_* | prices current/set | doc 22 L422–426 | PENDING |
| V-06 | Inventory | `/vendor/inventory` | VENDOR_* | inventory GET/PATCH | doc 22 L428–435; MT VD-01 | PENDING |
| V-07 | Daily inventory confirmation | `/vendor/inventory/daily` | VENDOR_* | inventory/daily/* | doc 22 L437–441 | PENDING |
| V-08 | Referral (attribution only) | `/vendor/referrals` | VENDOR_* | `/referrals*` | doc 22 L443–449; D-016 | PENDING |
| V-09 | Customers | `/vendor/customers` | VENDOR_* | **none** → GAP G-009 | doc 22 L451–455; MT VD-09 | PENDING |
| V-10 | Reconciliation / documents | `/vendor/settlements` | VENDOR_OWNER | `/vendors/settlements`, invoices | doc 22 L457–461; MT VD-06/10/13 | PENDING |
| V-11 | Staff / access | `/vendor/staff` | VENDOR_OWNER | **none** → GAP G-010 | doc 22 L463–468; MT VD-07/15 | PENDING |
| V-12 | Vendor profile | `/profile` vendor ctx | VENDOR_* | profile/context | doc 22 L470–475; MT VD-12 | PENDING |
| V-14 | Storefront management | `/vendor/storefront` | VENDOR_OWNER | storefront read; manage → likely GAP | MT VD-14; D-024 | PENDING |
| V-16 | Barcode / continuous scan | (mobile) | VENDOR_STAFF + inv.scan | match-barcode, continuous-scan **CONTRACT** | MT VD-16; D-028 | PENDING |
| V-17 | Financial activity | `/vendor/finance` | VENDOR_OWNER | settlements/invoices D-021 | MT VD-17 | PENDING |

---

## D. Ops (O / OP)

| ID | Title | Route | Role | Primary APIs | Source | Status |
|----|-------|-------|------|--------------|--------|--------|
| O-01 | Overview (queues first) | `/ops` | OPS_AGENT | exceptions dashboard, queues | doc 22 L479–486; MT OP-04 | PENDING |
| O-02 | Unified queues | `/ops/queues` | OPS_AGENT | orders/support/rma/recon lists | doc 22 L488–499; MT OP-01 | PENDING |
| O-03 | Object detail shell | `/ops/[type]/[id]` | OPS_AGENT | per object | doc 22 L501–508; MT OP-02 | PENDING |
| O-04 | RMA / dispute workbench | `/ops/rma` | OPS_AGENT | returns/disputes (per-order) + GAP global list G-013 | doc 22 L510–516 | PENDING |
| O-05 | Support workbench | `/ops/support` | OPS_AGENT | `/support/cases*` | doc 22 L518–524; MT OP-05 | PENDING |
| O-06 | Reconciliation | `/ops/reconciliation` | OPS_AGENT | `/finance/reconciliation*` | doc 22 L526–530; MT OP-03; G-015 | PENDING |
| O-07 | Risk / reliability | `/ops/risk` | OPS_AGENT | **limited API** → GAP/partial | doc 22 L532–537; MT OP-07/08 | PENDING |
| O-08 | Notification operations | `/ops/notifications` | OPS_AGENT | notifications list + GAP provider ops | doc 22 L539–543 | PENDING |
| O-09 | Pilot analytics | `/ops/analytics` | OPS_AGENT | **none** → GAP G-008 | doc 22 L545–554; G-015 | PENDING |
| O-10 | Admin / context | `/ops/admin` | OPS_AGENT, ADMIN_SUPER | `/admin/audit-logs`, `/admin/exceptions/dashboard` | doc 22 L556–561; MT OP-10 | PENDING |
| O-10B | Admin users/orgs | `/admin/users`, `/admin/orgs` | ADMIN_SUPER | **none** → GAP G-007 | route map §6 | PENDING |
| OP-11 | Permission audit | `/ops/permissions` | ADMIN_SUPER/OPS | **none** → GAP | MT OP-11 | PENDING |
| OP-13 | Master SKU / candidate review | `/ops/catalog-candidates` | OPS/ADMIN | product-candidates **CONTRACT** | MT OP-13 | PENDING |

---

## E. Field (F / FA)

| ID | Title | Route | Role | Primary APIs | Source | Status |
|----|-------|-------|------|--------------|--------|--------|
| F-01 | Today / task list | `/field` or `/field/tasks` | FIELD_ACTIVATOR | GET `/field/tasks` | doc 22 L564–567; MT FA-01 | PENDING |
| F-02 | Retailer activation | `/field/tasks/[id]` activation | FIELD_ACTIVATOR | PATCH task; profile create patterns | doc 22 L569–576; MT FA-02 | PENDING |
| F-03 | Assisted order | (embedded retailer flows) | FIELD_ACTIVATOR | baskets + orders as retailer ctx | doc 22 L578–584; MT FA-03 | PENDING |
| F-04 | Follow-up | task detail notes | FIELD_ACTIVATOR | PATCH `/field/tasks/{id}` | doc 22 L586–590; MT FA-04 | PENDING |
| F-05 | Weak network | (cross-cutting) | FIELD_ACTIVATOR | client sync UX | doc 22 L592–598; MT FA-05 | PENDING |

---

## F. Corporate (C / CP) — PUBLIC_ANON

| ID | Title | Route (PROPOSED G-006) | Role/context | APIs | Source | Status |
|----|-------|------------------------|--------------|------|--------|--------|
| C-01 | Home | `/` | PUBLIC_ANON | none (static) | doc 22 L600+; MT CP-01 | PENDING |
| C-02 | Retailers | `/retailers` | PUBLIC_ANON | none | MT CP-02 | PENDING |
| C-03 | Vendors | `/vendors` | PUBLIC_ANON | none | MT CP-03 | PENDING |
| C-04 | How POL works | `/how` | PUBLIC_ANON | none | MT CP-04 | PENDING |
| C-05 | Ahvaz pilot | `/pilot` | PUBLIC_ANON | none | MT CP-05; D-001 | PENDING |
| C-06 | About | `/about` | PUBLIC_ANON | none | MT CP-06 | PENDING |
| C-07 | Contact | `/contact` | PUBLIC_ANON | none | MT CP-07 | PENDING |
| C-08 | Legal / privacy / trust | `/legal` | PUBLIC_ANON | none | MT CP-08; D-025 copy | PENDING |

---

## G. Platform notes

- **Web:** all families above.  
- **Android (Phase 3):** functional parity §6.5 — same IDs apply where applicable; Field Android-first; barcode mobile-primary; hover N/A (platform-aware states).  
- **Staff role gating:** RETAILER_STAFF / VENDOR_STAFF restricted actions per Master Tree §38.5–38.7 — enforce in UI affordances + server authority.

---

## H. Coverage rollup (update each QA cycle)

| Family | Count | PENDING | IMPLEMENTED | VERIFIED | GAP | BLOCKED | N/A |
|--------|------:|--------:|------------:|---------:|----:|--------:|----:|
| Shared/Auth | 6 | 6 | 0 | 0 | 0 | 0 | 0 |
| Retailer | 20 | 20 | 0 | 0 | 0 | 0 | 0 |
| Vendor | 16 | 16 | 0 | 0 | 0 | 0 | 0 |
| Ops | 13 | 13 | 0 | 0 | 0 | 0 | 0 |
| Field | 5 | 5 | 0 | 0 | 0 | 0 | 0 |
| Corporate | 8 | 8 | 0 | 0 | 0 | 0 | 0 |
| **Total** | **68** | **68** | **0** | **0** | **0** | **0** | **0** |
