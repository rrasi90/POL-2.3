# POL Vendor Android App — Build Report
**Date:** 2026-09-28
**Repository:** `rrasi90/POL-2.3`
**Base:** `main` @ `f90fe3117c1881545e32181381ec50a1a6960f9e`
**Working branch:** `feat/vendor-app-production-20260928-v2`
**Pull Request:** #20

## 1. Product
The first dedicated mobile product is the wholesaler/vendor application:
- Product name: **پل بنکدار**
- Android package: `ir.pol.vendor`
- Allowed roles: `VENDOR_OWNER`, `VENDOR_STAFF`
- Backend authorization remains canonical.

## 2. Implemented vendor workspace
The Vendor mobile workspace has been rebuilt around the daily wholesaler operating loop:

### Home
- operational overview
- pending-order count
- active-fulfillment count
- catalog/inventory count
- freshness attention count
- today's action shortcuts
- latest pending orders
- latest inventory rows

### Orders
- order queue
- server-backed order states
- accept
- preparing
- ready
- order detail handoff to the canonical OrderDetail screen

### Inventory
- physical / reserved / sellable visibility
- freshness attention
- vendor SKU / packaging context
- physical inventory adjustment
- current price update through the canonical pricing endpoint
- daily inventory confirmation
- confirmation-with-changes

### Finance
- invoices
- settlement status
- Toman presentation
- no wallet / escrow UI

### Vendor management
- customers
- referral attribution view
- customers
- staff lifecycle
- delegated permission editor
- effective permission set

## 3. UX architecture
- Persian-first RTL
- Light / Night theme compatibility
- Precision Commerce visual direction
- D2 Balanced Operations density
- 44px+ core interactive targets inherited from the shared mobile system
- six-item primary bottom navigation keeps core operations accessible while retaining a dedicated support entry
- secondary sections moved behind contextual segmented controls

## 4. Canonical API preservation
No new business endpoint was invented. The implementation uses existing canonical contracts including:
- `GET /api/v1/orders`
- `POST /api/v1/orders/{order_id}/accept`
- `POST /api/v1/orders/{order_id}/preparing`
- `POST /api/v1/orders/{order_id}/ready`
- `GET/PATCH /api/v1/catalog/vendors/products/{vendor_product_id}/inventory`
- `GET/POST /api/v1/catalog/vendors/products/{vendor_product_id}/prices`
- `GET/POST /api/v1/inventory/daily/{confirmation_date}...`
- `GET /api/v1/invoices`
- `GET /api/v1/vendors/settlements`
- `GET /api/v1/vendors/customers`
- `GET/POST/PATCH /api/v1/vendors/staff...`
- staff delegated-permission endpoints

## 5. Role boundary
The Vendor Android product is independently scoped:
- retailer roles are rejected at the login result boundary
- persisted sessions with a non-vendor role are cleared by the Vendor App shell
- Vendor Owner / Vendor Staff permissions remain server-authoritative

## 6. Verification status
### Source verification
**PASS**
- branch created from the current mobile split head
- Vendor workspace source updated
- regression QA updated to the split AppShell architecture
- Login role filtering added

### Repository lineage
**PASS**
- branch is ahead of main
- branch is not behind main
- no main/protected branch mutation performed

### CI
**NOT CERTIFIED ON CURRENT FINAL HEAD**
The repository's pull-request workflow started on an earlier commit in the same implementation branch and failed before useful steps were exposed by the available GitHub job-log interface. A rerun was queued for that historical head, but it is not evidence for the current final head. Therefore this report does not mark current-head CI as PASS.

### Device / release APK
**NOT CERTIFIED YET**
The branch contains the existing Expo prebuild + Gradle APK builder and the Vendor package configuration. A current-head installable APK build and device smoke test still require an executable Android build/runtime environment.

## 7. Release gate
This report intentionally distinguishes:
`SOURCE_BUILT` → current state
`CI_CERTIFIED` → pending fresh current-head execution
`DEVICE_CERTIFIED` → pending fresh Android runtime execution
