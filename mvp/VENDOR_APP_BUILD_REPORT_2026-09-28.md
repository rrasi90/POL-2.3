# POL Vendor Android App — Pre-APK Release Gate

**Date:** 2026-09-28  
**Repository:** `rrasi90/POL-2.3`  
**Base:** `main` @ `f90fe3117c1881545e32181381ec50a1a6960f9e`  
**Working branch:** `feat/vendor-app-production-20260928-v2`  
**Current HEAD:** `e4f98cb71c09a71b450762207e6ca0b7ff32076a`  
**Pull Request:** #20

## 0. Gate position

The branch is intentionally stopped **immediately before native Android APK assembly**.

This stage covers source/configuration/release-gate work only. It does **not** run:
- `expo prebuild --clean --platform android`
- Gradle `assembleRelease`
- APK installation
- Android device certification

The native build remains the next executable step after the pre-APK gate is satisfied and a current Android build/runtime environment is available.

## 1. Product identity

- Product: **پل بنکدار**
- Android package: `ir.pol.vendor`
- Expo slug: `pol-vendor`
- Allowed roles: `VENDOR_OWNER`, `VENDOR_STAFF`
- Canonical Vendor logo source: `logo/لوگو پل برای بنکدار.png`
- Mobile bundle asset: `mvp/apps/mobile/assets/vendor-logo.png`
- Asset verification: byte-identical to the canonical Git blob
- Asset raster: 581×570 RGBA PNG
- Android icon, adaptive foreground and Android splash are bound to the Vendor asset.

## 2. Vendor workspace

### Home
- operational overview
- pending-order count
- active fulfillment count
- catalog/inventory count
- freshness attention
- today's quick actions
- latest pending orders
- latest inventory rows

### Orders
- server-backed order queue
- accept
- reject
- partial-acceptance proposal
- preparing
- ready
- dispatch handoff
- canonical order-detail screen
- status/timeline visibility

### Inventory
- physical / reserved / sellable quantities
- Vendor SKU and packaging context
- physical inventory update
- current price update
- daily inventory confirmation
- confirmation with declared changes

### Finance
- invoices
- settlement status
- Toman presentation
- no wallet / escrow surface

### Vendor management
- customers
- referral attribution
- staff invite/status lifecycle
- delegated permissions
- effective permission visibility

### Shared support
- support case creation
- related-order support
- case detail
- message submission

## 3. Authorization hardening

A source audit found an important UI authorization mismatch: Vendor Staff could previously see the order-acceptance affordance even though the canonical backend contract protects `order.accept`.

This was corrected before the APK gate:

- `VENDOR_OWNER`: accept / reject / partial acceptance
- `VENDOR_OWNER` + `VENDOR_STAFF`: preparing / ready / dispatch, subject to server authority
- Vendor queue and Order Detail now hide owner-only acceptance controls from staff.
- Runtime server authorization remains authoritative.

## 4. Canonical API preservation

No new business API was invented for the Vendor app.

Current implementation uses existing canonical surfaces, including:

- `GET /api/v1/orders`
- `POST /api/v1/orders/{order_id}/accept`
- `POST /api/v1/orders/{order_id}/preparing`
- `POST /api/v1/orders/{order_id}/ready`
- `POST /api/v1/orders/{order_id}/reject`
- `POST /api/v1/orders/{order_id}/partial-acceptance-proposals`
- `POST /api/v1/orders/{order_id}/dispatch`
- `GET/PATCH /api/v1/catalog/vendors/products/{vendor_product_id}/inventory`
- `GET/POST /api/v1/catalog/vendors/products/{vendor_product_id}/prices`
- `GET/POST /api/v1/inventory/daily/{confirmation_date}...`
- `GET /api/v1/invoices`
- `GET /api/v1/vendors/settlements`
- `GET /api/v1/vendors/customers`
- `GET/POST/PATCH /api/v1/vendors/staff...`
- delegated-permission endpoints
- `GET/POST /api/v1/support/cases...`

## 5. UX / accessibility gate

- Persian-first / RTL product copy
- Light + Night tokenized theme
- shared Precision Commerce direction
- D2 Balanced Operations density
- shared primary buttons and inputs use a minimum 44px height
- reduced bottom navigation density relative to the earlier implementation
- secondary management surfaces remain behind contextual controls

Visual verification remains a device/runtime gate; source tokens alone are not treated as visual certification.

## 6. Deterministic pre-APK checks added

New command:

```
npm run qa:pre-apk --workspace @pol/mobile
```

The gate checks:

- Vendor Expo name / slug / package
- Vendor icon + adaptive foreground + Android splash binding
- PNG signature and dimensions
- byte-level identity of the Vendor logo against the canonical Git blob
- existence of required mobile assets
- absence of obvious embedded secrets in inspected mobile source
- environment-configurable API base URL
- canonical API v1 usage
- Vendor workspace and support wiring
- canonical support case/message route markers
- owner-only acceptance guards
- dedicated Vendor entrypoint selection
- native release command selection
- restoration of the default entrypoint in the build script
- regression-QA coverage for the new Vendor authorization guard

The native builder now invokes this gate immediately before Expo prebuild.

## 7. Repository / PR state

- Main branch: untouched.
- PR #20: open, unmerged.
- Current branch: ahead of main by 61 commits, behind by 0.
- Current HEAD: `7411dba37bda71be544f825dd774f82fc30b9f05`.

## 8. CI status

**Current-head CI is not certified.**

The available GitHub workflow telemetry for the earlier PR execution reports jobs that terminate before exposing executable steps; job logs are unavailable through the current interface. Later connector-created commits on the branch do not have a fresh pull-request workflow run associated with the latest HEAD.

Therefore:
- historical green mobile runs are retained as historical evidence only;
- current HEAD is not marked CI-PASS without fresh execution evidence.

## 9. Host / staging connectivity status

The stored VPS execution record confirms the existing deployment host and that the deployment stack has previously answered `/healthz`, `/readyz` and API requests successfully.

The current assistant runtime does not have an SSH/remote-terminal channel into that host. Direct connection attempts from this environment did not establish a live session. A remote desktop/terminal integration is available to connect, but it is not currently connected.

Therefore no current live-host claim is made for this Vendor branch.

## 10. Final status

| Gate | Status |
|---|---|
| Vendor product source | PASS |
| Canonical Vendor logo binding | PASS |
| Android package/config | PASS |
| Vendor role boundary | PASS |
| Owner-only acceptance authorization | PASS |
| Support surface | PASS |
| Canonical API preservation | PASS |
| Deterministic pre-APK gate | PASS (wired; source checks inspected) |
| Fresh current-head CI | BLOCKED / NOT CERTIFIED |
| Live VPS verification of this branch | BLOCKED / NOT CONNECTED |
| Native Expo prebuild | **NOT RUN** |
| Gradle release APK build | **NOT RUN** |
| APK install/device certification | **NOT RUN** |

## 11. Release boundary

The Vendor application is now at:

**SOURCE / CONFIG READY → PRE-APK GATE → [next: native APK build]**

No APK has been generated in this stage.
