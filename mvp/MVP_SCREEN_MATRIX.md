# POL MVP — SCREEN MATRIX

**Sources:** doc 22 §5–9; doc 30 (R-*); doc 31 (V/O/F/C); Master Tree 50 §7–11 + §38 roles; route map (research-hardening) + 2026-09-20 amendment; DECISION_REGISTER.  
**Status legend:** `IMPLEMENTED` | `VERIFIED` | `BLOCKED_EXTERNAL` | `GAP` | `NOT_APPLICABLE`  
**Pre-build:** `PENDING` (Phase 0 Gate).  
**Role context:** `PUBLIC_ANON` for corporate; authenticated roles otherwise.

**Evidence fields required for VERIFIED:** source · route · API source · implementation path · verification command/result · last QA cycle · status.

**QA note (2026-09-22):** typecheck EXIT 0 + `next build` EXIT 0 for Phase 2 web modules (auth/retailer/ops/field/corporate + vendor). Runtime e2e against live FastAPI not run in that cycle → status `IMPLEMENTED`.

**QA note cycle 5 (2026-09-23):** live FastAPI `:8000` (DB `pol`, 95 tables) + Next `:3001` up. 19 screens promoted to `VERIFIED` — authenticated API smoke 200 + static route 200 + structural audit EXIT 0 (see §Live-evidence). Remaining IMPLEMENTED screens still lack full click-through e2e (Phase 4).

---

## A. Shared / Auth

| ID | Title | Route (canonical/prop) | Role/context | Primary APIs (API_MAP) | Source | Status |
|----|-------|------------------------|--------------|------------------------|--------|--------|
| SH-AUTH-01 | Login phone + OTP request | `/auth/login` | PUBLIC_ANON → all | POST `/auth/request-otp` | route map §1; D-018; doc 22 §3.1 | VERIFIED |
| SH-AUTH-02 | Verify OTP (4-digit) | `/auth/login` (step) | PUBLIC_ANON → all | POST `/auth/verify-otp` | D-018; route map (OTP digits → 4) | VERIFIED |
| SH-AUTH-03 | Refresh (implicit) | (client) | all | POST `/auth/refresh` | route map §1 | VERIFIED |
| SH-PROFILE-01 | Account / profile | `/profile` | authenticated | GET/PUT `/profile`, GET `/profile/context` | route map; R-13; V-12 | VERIFIED |
| SH-NOTIF-01 | Notifications inbox | `/notifications` | authenticated | GET `/notifications` | route map (path conflict G-004) | VERIFIED |
| SH-NOTIF-02 | Notification preferences | `/notifications/preferences` | authenticated | GET/PUT `/notifications/preferences` | route map | VERIFIED |

### §A evidence — Phase 2 Module 1 + web build (QA cycle 1, 2026-09-22)

| ID | Implementation | Verification |
|----|----------------|--------------|
| SH-AUTH-01/02 | `apps/web/src/app/auth/login/page.tsx` (4-digit OTP) | `cd mvp && npm run typecheck` → exit 0; `cd mvp && npm run build` → exit 0 |
| SH-AUTH-03 | `packages/api-client/src/index.ts` (onRefresh on 401 → single retry); `apps/web/src/lib/auth/api.ts` | typecheck/build exit 0 |
| SH-PROFILE-01 | `apps/web/src/app/(dashboard)/profile/page.tsx` | typecheck/build exit 0 |
| SH-NOTIF-01 | `apps/web/src/app/(dashboard)/notifications/page.tsx` | typecheck/build exit 0 |
| SH-NOTIF-02 | `apps/web/src/app/(dashboard)/notifications/preferences/page.tsx` | typecheck/build exit 0 |

---

## B. Retailer (R / RT)

| ID | Title | Route | Role | Primary APIs | Source | Status |
|----|-------|-------|------|--------------|--------|--------|
| R-01 | Onboarding / activation | `/auth/*` progressive | RETAILER_OWNER | auth + profile context | doc 22 L222–233; doc 30 R-01A–G; MT RT-01 | IMPLEMENTED |
| R-02 | Home / operational hub | `/retailer` | RETAILER_OWNER/STAFF | GET `/orders` (actions), profile | doc 22 L235–244; MT RT-02 | VERIFIED |
| R-03 | Search / catalog | `/retailer/catalog` | RETAILER_* | GET `/catalog/search`, `/catalog/categories`, GET `/search` | doc 22 L246–260; MT RT-06 | VERIFIED |
| R-03B | Barcode / SKU entry | (in catalog) | RETAILER_* (+scan perm) | POST `products/match-barcode` **CONTRACT** → MOCK/GAP | D-028; amendment | GAP |
| R-04 | Product detail | `/retailer/catalog/[id]` | RETAILER_* | GET `/catalog/products/{id}`, `/vendors`, compare-* | doc 22 L262–275; MT RT-07 | IMPLEMENTED |
| R-05 | Vendor comparison | (in product) | RETAILER_* | compare-prices, compare-inventory | doc 22 L277–289; MT RT-07 | IMPLEMENTED |
| R-06 | Multi-vendor basket | `/retailer/basket` | RETAILER_* | POST `/baskets*` | doc 22 L291–302; MT RT-03; D-014 | IMPLEMENTED |
| R-07 | Allocation review | `/retailer/checkout` | RETAILER_* | POST `/baskets/{id}/allocation-preview` | doc 22 L304–314; MT RT-14 | IMPLEMENTED |
| R-08 | Checkout / confirmation | `/retailer/checkout` | RETAILER_* | POST `/orders` | doc 22 L316–325; MT RT-04 | IMPLEMENTED |
| R-09 | Order group detail | `/retailer/orders/group/[id]` | RETAILER_* | GET `/orders/group/{id}`, `/orders/group/{id}/orders` | doc 22 L327–341; MT RT-15; D-022 | IMPLEMENTED |
| R-09B | Child order detail | `/retailer/orders/[id]` | RETAILER_* | GET `/orders/{id}`, items, timeline | doc 22; MT RT-08 | IMPLEMENTED |
| R-09C | Partial acceptance review | (order detail) | RETAILER_OWNER | POST approve/decline partial proposals (derive `proposal_id` from timeline `event_data`) | MT RT-20 | IMPLEMENTED |
| R-09D | Delivery tracking | (order detail) | RETAILER_* | GET `/orders/{id}/delivery` | MT RT-05 | IMPLEMENTED |
| R-09E | Handoff / receiver confirm | (order or link) | receiver | GET delivery/proof; POST `/orders/{id}/deliver` | MT RT-19; D-023 | IMPLEMENTED |
| R-10 | Reorder / history | `/retailer/orders` | RETAILER_* | GET `/orders` | doc 22 L343–349; MT RT-10 | VERIFIED |
| R-11 | Returns / disputes | `/retailer/orders/[id]/returns` | RETAILER_OWNER | POST/GET `/orders/{id}/returns`, disputes | doc 22 L351–353; MT RT-09 | IMPLEMENTED |
| R-12 | Support | `/retailer/support` | RETAILER_* | `/support/cases*` | doc 22 L355–363; MT RT-13 | IMPLEMENTED |
| R-13 | Account | `/profile` (+ org) | RETAILER_* | profile/context; staff mgmt → GAP G-010 | doc 22 L365–373; MT RT-12 | IMPLEMENTED |
| R-16 | Financial activity | `/retailer/finance` | RETAILER_OWNER | GET `/invoices` (D-021 no wallet) | MT RT-16; D-021 | VERIFIED |
| R-17 | Vendor search | `/retailer/vendors` | RETAILER_* | GET `/storefront/vendors` | MT RT-17; D-024 | VERIFIED |
| R-18 | Vendor storefront | `/retailer/vendors/[id]` | RETAILER_* | GET storefront vendor + products | MT RT-18; D-024 | VERIFIED |

### §B evidence — Retailer module (QA cycle 1, 2026-09-22)

| ID | Implementation | Verification |
|----|----------------|--------------|
| R-02/06/10/13 | `retailer/page.tsx`, `basket/page.tsx`, `orders/page.tsx`, `../profile/page.tsx` | typecheck/build exit 0 |
| R-03/04/05 | `retailer/catalog/page.tsx`, `catalog/[id]/page.tsx` | typecheck/build exit 0 |
| R-07/08 | `retailer/checkout/page.tsx` (allocation-preview + POST orders) | typecheck/build exit 0 |
| R-09 | `retailer/orders/group/[id]/page.tsx` | typecheck/build exit 0 |
| R-09B | `retailer/orders/[id]/page.tsx` | typecheck/build exit 0 |
| R-09C | `retailer/orders/[id]/page.tsx` partial-acceptance panel (approve/decline; proposal_id from timeline event_data) | typecheck/build exit 0 |
| R-09D | same file delivery panel (GET `/orders/{id}/delivery`) | typecheck/build exit 0 |
| R-09E | same file handoff/proof + POST `/deliver` (OTP 4-digit schema; G-022 RESOLVED) | typecheck/build exit 0 |
| R-09C/D/E | same order detail: derive proposals from timeline; GET delivery + proof; POST approve/decline/deliver | typecheck/build exit 0 |
| R-11 | `retailer/orders/[id]/returns/page.tsx` | typecheck/build exit 0 |
| R-12 | `retailer/support/page.tsx` | typecheck/build exit 0 |
| R-16 | `retailer/finance/page.tsx` (wallet note D-021) | typecheck/build exit 0 |
| R-17/18 | `retailer/vendors/page.tsx`, `vendors/[id]/page.tsx` | typecheck/build exit 0 |
| R-03B | no CONTRACT call invented | status GAP (G-003-adjacent) |

---

## C. Vendor (V / VD)

| ID | Title | Route | Role | Primary APIs | Source | Status |
|----|-------|-------|------|--------------|--------|--------|
| V-01 | Dashboard (queue-first) | `/vendor` | VENDOR_* | GET `/orders` (filters), inventory stale | doc 22 L377–387 | IMPLEMENTED |
| V-02 | Orders queue | `/vendor/orders` | VENDOR_* | GET `/orders` | doc 22 L389–399; MT VD-02 | IMPLEMENTED |
| V-03 | Order detail + accept/reject/partial | `/vendor/orders/[id]` | VENDOR_* | accept/reject/partial HTTP | doc 22 L401–410; MT VD-02/18 | IMPLEMENTED |
| V-04 | Catalog | `/vendor/catalog` | VENDOR_* | `/catalog/vendors/products*` | doc 22 L412–420; MT VD-05 | VERIFIED |
| V-05 | Pricing | `/vendor/catalog/[id]/prices` | VENDOR_* | prices current/set | doc 22 L422–426 | IMPLEMENTED |
| V-06 | Inventory | `/vendor/inventory` | VENDOR_* | inventory GET/PATCH | doc 22 L428–435; MT VD-01 | IMPLEMENTED |
| V-07 | Daily inventory confirmation | `/vendor/inventory/daily` | VENDOR_* | inventory/daily/* | doc 22 L437–441 | VERIFIED |
| V-08 | Referral (attribution only) | `/vendor/referrals` | VENDOR_* | `/referrals*` | doc 22 L443–449; D-016 | VERIFIED |
| V-09 | Customers | `/vendor/customers` | VENDOR_* | **none** → GAP G-009 | doc 22 L451–455; MT VD-09 | GAP |
| V-10 | Reconciliation / documents | `/vendor/settlements` | VENDOR_OWNER | `/vendors/settlements`, invoices | doc 22 L457–461; MT VD-06/10/13 | VERIFIED |
| V-11 | Staff / access | `/vendor/staff` | VENDOR_OWNER | **none** → GAP G-010 | doc 22 L463–468; MT VD-07/15 | GAP |
| V-12 | Vendor profile | `/profile` vendor ctx | VENDOR_* | profile/context | doc 22 L470–475; MT VD-12 | VERIFIED |
| V-14 | Storefront management | `/vendor/storefront` | VENDOR_OWNER | storefront read; write → GAP | MT VD-14; D-024 | VERIFIED |
| V-16 | Barcode / continuous scan | (mobile) | VENDOR_STAFF + inv.scan | match-barcode, continuous-scan **CONTRACT** | MT VD-16; D-028 | NOT_APPLICABLE |
| V-17 | Financial activity | `/vendor/finance` | VENDOR_OWNER | settlements/invoices D-021 | MT VD-17 | IMPLEMENTED |

### §C evidence — Vendor module (QA cycle 1, 2026-09-22)

| ID | Implementation | Verification |
|----|----------------|--------------|
| V-01/02 | `vendor/page.tsx`, `vendor/orders/page.tsx` | typecheck/build exit 0 |
| V-03 | `vendor/orders/[id]/page.tsx` (accept/reject/partial/preparing/ready/dispatch/deliver) | typecheck/build exit 0 |
| V-04/05 | `vendor/catalog/page.tsx`, `catalog/[id]/prices/page.tsx` | typecheck/build exit 0 |
| V-06/07 | `vendor/inventory/page.tsx`, `inventory/daily/page.tsx` | typecheck/build exit 0 |
| V-08 | `vendor/referrals/page.tsx` (D-016 attribution only) | typecheck/build exit 0 |
| V-10/17 | `vendor/settlements/page.tsx`, `vendor/finance/page.tsx` | typecheck/build exit 0 |
| V-14 | `vendor/storefront/page.tsx` (read-only D-024) | typecheck/build exit 0 |
| V-09/11 | GAP shells, no fake CRUD | status GAP (G-009/G-010) |
| V-16 | web N/A; Phase 3 Android | NOT_APPLICABLE (web) |

---

## D. Ops (O / OP)

| ID | Title | Route | Role | Primary APIs | Source | Status |
|----|-------|-------|------|--------------|--------|--------|
| O-01 | Overview (queues first) | `/ops` | OPS_AGENT | exceptions dashboard, queues | doc 22 L479–486; MT OP-04 | IMPLEMENTED |
| O-02 | Unified queues | `/ops/queues` | OPS_AGENT | orders/support/rma/recon lists | doc 22 L488–499; MT OP-01 | IMPLEMENTED |
| O-03 | Object detail shell | `/ops/[type]/[id]` | OPS_AGENT | per object (orders/support/recon/returns) | doc 22 L501–508; MT OP-02 | IMPLEMENTED |
| O-04 | RMA / dispute workbench | `/ops/rma` | OPS_AGENT | returns/disputes (per-order) + GAP global list G-013 | doc 22 L510–516 | IMPLEMENTED |
| O-05 | Support workbench | `/ops/support` | OPS_AGENT | `/support/cases*` | doc 22 L518–524; MT OP-05 | IMPLEMENTED |
| O-06 | Reconciliation | `/ops/reconciliation` | OPS_AGENT | `/finance/reconciliation*` | doc 22 L526–530; MT OP-03; G-015 | IMPLEMENTED |
| O-07 | Risk / reliability | `/ops/risk` | OPS_AGENT | **limited API** → GAP/partial | doc 22 L532–537; MT OP-07/08 | GAP |
| O-08 | Notification operations | `/ops/notifications` | OPS_AGENT | notifications list + GAP provider ops | doc 22 L539–543 | IMPLEMENTED |
| O-09 | Pilot analytics | `/ops/analytics` | OPS_AGENT | **none** → GAP G-008 | doc 22 L545–554; G-015 | GAP |
| O-10 | Admin / context | `/ops/admin` | OPS_AGENT, ADMIN_SUPER | `/admin/audit-logs`, `/admin/exceptions/dashboard` | doc 22 L556–561; MT OP-10 | IMPLEMENTED |
| O-10B | Admin users/orgs | `/admin/users`, `/admin/orgs` | ADMIN_SUPER | **none** → GAP G-007 | route map §6 | GAP |
| OP-11 | Permission audit | `/ops/permissions` | ADMIN_SUPER/OPS | **none** → GAP | MT OP-11 | GAP |
| OP-13 | Master SKU / candidate review | `/ops/catalog-candidates` | OPS/ADMIN | product-candidates **CONTRACT** | MT OP-13 | GAP |

### §D evidence — Ops + Admin (QA cycle 1, 2026-09-22)

| ID | Implementation | Verification |
|----|----------------|--------------|
| O-01/02/04/05/06/08/10 | `ops/page.tsx`, `queues`, `rma`, `support`, `reconciliation`, `notifications`, `ops/admin` | typecheck/build exit 0 |
| O-10B | `admin/users/page.tsx`, `admin/orgs/page.tsx` (GAP stubs) | status GAP (G-007) |
| O-07/09/OP-11/OP-13 | GAP shells | status GAP |
| O-03 | `ops/[type]/[id]/page.tsx` (generic detail shell) | typecheck/build exit 0 |

---

## E. Field (F / FA)

| ID | Title | Route | Role | Primary APIs | Source | Status |
|----|-------|-------|------|--------------|--------|--------|
| F-01 | Today / task list | `/field` | FIELD_ACTIVATOR | GET `/field/tasks` | doc 22 L564–567; MT FA-01 | VERIFIED |
| F-02 | Retailer activation | `/field/tasks/[id]` activation | FIELD_ACTIVATOR | PATCH task; profile create patterns | doc 22 L569–576; MT FA-02 | IMPLEMENTED |
| F-03 | Assisted order | (link into retailer flows) | FIELD_ACTIVATOR | baskets + orders as retailer ctx | doc 22 L578–584; MT FA-03 | IMPLEMENTED |
| F-04 | Follow-up | task detail notes | FIELD_ACTIVATOR | PATCH `/field/tasks/{id}` | doc 22 L586–590; MT FA-04 | IMPLEMENTED |
| F-05 | Weak network | (cross-cutting offline banner) | FIELD_ACTIVATOR | client sync UX | doc 22 L592–598; MT FA-05 | IMPLEMENTED |

### §E evidence — Field (QA cycle 1, 2026-09-22)

| ID | Implementation | Verification |
|----|----------------|--------------|
| F-01/02/04 | `field/page.tsx`, `field/tasks/[id]/page.tsx` | typecheck/build exit 0 |
| F-03/05 | task → retailer link + offline banner in field module | typecheck/build exit 0 |

---

## F. Corporate (C / CP) — PUBLIC_ANON

| ID | Title | Route (PROPOSED G-006) | Role/context | APIs | Source | Status |
|----|-------|------------------------|--------------|------|--------|--------|
| C-01 | Home | `/` | PUBLIC_ANON | none (static) | doc 22 L600+; MT CP-01 | IMPLEMENTED |
| C-02 | Retailers | `/retailers` | PUBLIC_ANON | none | MT CP-02 | IMPLEMENTED |
| C-03 | Vendors | `/vendors` | PUBLIC_ANON | none | MT CP-03 | IMPLEMENTED |
| C-04 | How POL works | `/how` | PUBLIC_ANON | none | MT CP-04 | IMPLEMENTED |
| C-05 | Ahvaz pilot | `/pilot` | PUBLIC_ANON | none | MT CP-05; D-001 | IMPLEMENTED |
| C-06 | About | `/about` | PUBLIC_ANON | none | MT CP-06 | IMPLEMENTED |
| C-07 | Contact | `/contact` | PUBLIC_ANON | none | MT CP-07 | IMPLEMENTED |
| C-08 | Legal / privacy / trust | `/legal` | PUBLIC_ANON | none | MT CP-08; D-025 copy | IMPLEMENTED |

### §F evidence — Corporate (QA cycle 1, 2026-09-22)

| ID | Implementation | Verification |
|----|----------------|--------------|
| C-01…C-08 | `app/page.tsx`, `retailers/`, `vendors/`, `how/`, `pilot/`, `about/`, `contact/`, `legal/` | typecheck/build exit 0 (static prerender 50 routes) |

---

### §Live-evidence — QA cycle 5 (2026-09-23) — live FastAPI + Next smoke

**Commands:** API smoke script against `http://127.0.0.1:8000/api/v1/*` (retailer `+989160007777` / vendor `+989160008888`, OTP `1234`, tokens in `artifacts/auth_verify.json` + `artifacts/auth_vendor.json`, evidence `artifacts/live_api_evidence_c5.json`) · Next route GETs on `:3001` · `python artifacts/structural_audit.py` → EXIT 0 · route crawl `artifacts/route_crawl_3001.json` 47/47 HTTP 200.

| ID | Route (:3001) | API source (live) | Result | Cycle |
|----|---------------|-------------------|--------|-------|
| SH-AUTH-01 | GET `/auth/login` 200 | POST `/auth/request-otp` 200 PENDING | PASS | 5 |
| SH-AUTH-02 | (login step) | POST `/auth/verify-otp` 200 → 393-char access token | PASS | 5 |
| SH-AUTH-03 | (client implicit) | POST `/auth/refresh` 200 → new token pair | PASS | 5 |
| SH-PROFILE-01 | GET `/profile` 200 | GET `/profile`, `/profile/context`, `/profile/completion` 200 (88%) | PASS | 5 |
| SH-NOTIF-01 | GET `/notifications` 200 | GET `/notifications` 200 | PASS | 5 |
| SH-NOTIF-02 | GET `/notifications/preferences` 200 | GET+PUT `/notifications/preferences` 200 (PUSH) | PASS | 5 |
| R-02 | GET `/retailer` 200 | GET `/orders?limit=3` 200 + profile context 200 | PASS | 5 |
| R-03 | GET `/retailer/catalog` 200 | GET `/catalog/search?q=وروغ` 200 + `/catalog/categories` 200 + `/search` 200 | PASS | 5 |
| R-10 | GET `/retailer/orders` 200 | GET `/orders?limit=3` 200 | PASS | 5 |
| R-16 | GET `/retailer/finance` 200 | GET `/invoices` 200 | PASS | 5 |
| R-17 | GET `/retailer/vendors` 200 | GET `/storefront/vendors` 200 `{items,total,page,page_size}` | PASS | 5 |
| R-18 | GET `/retailer/vendors` 200 (list+detail client) | GET `/storefront/vendors/{id}` 200 + `.../products` 200 (seeded catalog) | PASS | 5 |
| V-04 | GET `/vendor/catalog` 200 | GET `/catalog/vendors/products` 200 (vendor token) | PASS | 5 |
| V-07 | GET `/vendor/inventory/daily` 200 | GET `/inventory/daily/2026-09-23` 200 (PENDING confirmation) | PASS | 5 |
| V-08 | GET `/vendor/referrals` 200 | GET `/referrals` 200 | PASS | 5 |
| V-10 | GET `/vendor/settlements` 200 | GET `/vendors/settlements` 200 | PASS | 5 |
| V-12 | `/profile` vendor ctx (SH-PROFILE-01 route) | GET `/profile/context` + `/profile` 200 (vendor token) | PASS | 5 |
| V-14 | GET `/vendor/storefront` 200 | storefront read 200 (write remains GAP D-024) | PASS | 5 |
| F-01 | GET `/field` 200 | GET `/field/tasks` 200 | PASS | 5 |

Non-admin RBAC spot-check: retailer token → GET `/admin/audit-logs` **403** (expected). Structural audit: `window_loc=0 console_log=0 fake_success=0`.

---

## G. Platform notes

- **Web:** all families above (Phase 2).  
- **Android (Phase 3):** functional parity §6.5 — same IDs apply where applicable; Field Android-first; barcode mobile-primary; hover N/A (platform-aware states).  
- **Staff role gating:** RETAILER_STAFF / VENDOR_STAFF restricted actions per Master Tree §38.5–38.7 — enforce in UI affordances + server authority.

---

## H. Coverage rollup (update each QA cycle)

| Family | Count | PENDING | IMPLEMENTED | VERIFIED | GAP | BLOCKED | N/A |
|--------|------:|--------:|------------:|---------:|----:|--------:|----:|
| Shared/Auth | 6 | 0 | 0 | 6 | 0 | 0 | 0 |
| Retailer | 20 | 0 | 13 | 6 | 1 | 0 | 0 |
| Vendor | 16 | 0 | 7 | 6 | 2 | 0 | 1 |
| Ops | 13 | 0 | 8 | 0 | 5 | 0 | 0 |
| Field | 5 | 0 | 4 | 1 | 0 | 0 | 0 |
| Corporate | 8 | 0 | 8 | 0 | 0 | 0 | 0 |
| **Total** | **68** | **0** | **40** | **19** | **8** | **0** | **1** |

**Cycle 1 (2026-09-22):** typecheck exit 0; `next build` exit 0 (50 routes).  
**Cycle 2 (2026-09-22):** closed R-09C/D/E + O-03 → IMPLEMENTED; typecheck exit 0; `next build` exit 0 (50 routes incl. `/ops/[type]/[id]`).  
**Cycle 3 (2026-09-22):** eslint exit 0 (0 errors / 17 warnings); typecheck exit 0; `next build` exit 0 (50 routes). Module DoD cycle min (≥3) met for Phase 2 web. Still `IMPLEMENTED` not `VERIFIED` until live FastAPI e2e.
**Cycle 4 (2026-09-23):** infra regression — pytest suite green at gate count; typecheck/lint/build/structural audit green (no status flips).
**Cycle 5 (2026-09-23):** live e2e smoke — FastAPI `:8000` on `pol` 95 tables + Next `:3001`; 19 screens → `VERIFIED` (40 IMP / 19 VER / 8 GAP / 1 N/A); see §Live-evidence. Structural audit EXIT 0.


## I. Phase 3 Android implementation evidence — 2026-09-23

This section records mobile implementation evidence separately from the canonical screen status.
A mobile implementation is not promoted to VERIFIED until its required QA/evidence is recorded.

| Mobile surface | Canonical coverage | Implementation | Current status |
|---|---|---|---|
| Authentication | SH-AUTH-01/02 | apps/mobile/src/screens/LoginScreen.tsx | IMPLEMENTED |
| Retailer commerce foundation | R-02/R-03/R-06/R-07/R-08/R-10 | apps/mobile/src/screens/RetailerMobileScreen.tsx | IMPLEMENTED |
| Vendor operations foundation | V-01/V-02/V-03/V-06/V-07/V-10 | apps/mobile/src/screens/VendorMobileScreen.tsx | IMPLEMENTED |
| Operations foundation | O-01/O-02/O-06/O-10 | apps/mobile/src/screens/OpsMobileScreen.tsx | IMPLEMENTED |
| Field-first | F-01…F-05 | existing FieldTaskList/Detail/AssistedOrder screens + OfflineBanner | IMPLEMENTED |
| Barcode | R-03B/V-16, D-028 | contract-only; camera/matching adapter not activated | GAP / CONTRACT |
| Remaining mobile parity | order detail, returns, support, vendor storefront/customers/staff and other applicable screens | not yet ported | OPEN |

Verification requirements:
- .github/workflows/pol-mvp-mobile.yml
- typecheck
- Expo config validation
- Android export
- minimum 3 Phase-3 QA cycles
- Night-theme visual verification
- evidence update before VERIFIED

### I. Phase 3 Android coverage update — 2026-09-23

| Capability | Mobile surface | Status |
|---|---|---|
| Shared profile | `AccountMobileScreen` → GET/PUT `/api/v1/profile` + profile context | IMPLEMENTED |
| Shared notifications | `AccountMobileScreen` → GET `/api/v1/notifications` | IMPLEMENTED |
| Retailer vendor search | `RetailerMobileScreen` → GET `/api/v1/storefront/vendors` | IMPLEMENTED |
| Retailer vendor storefront | `RetailerMobileScreen` → GET `/api/v1/storefront/vendors/{id}` + products | IMPLEMENTED |
| Retailer support | `SupportMobileScreen` → cases + messages | IMPLEMENTED |
| Retailer returns/disputes | `OrderDetailMobileScreen` → POST returns/disputes | IMPLEMENTED |
| Vendor customers/staff | no authoritative HTTP contract | GAP |
| D-028 barcode | no authoritative mobile contract/runtime adapter | GAP / CONTRACT |
| Mobile verification | CI + 3 QA cycles + Night visual evidence | OPEN |
