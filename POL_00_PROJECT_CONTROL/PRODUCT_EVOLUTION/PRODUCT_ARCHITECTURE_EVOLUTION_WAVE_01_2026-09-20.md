
# POL — Product Architecture Evolution Wave 01
## 2026-09-20 — Research, Founder Directions, and Engineering Backlog

**Status:** ADOPTED PRODUCT DIRECTION / IMPLEMENTATION FOLLOW-UP  
**Repository:** rrasi90/POL-2.3  
**Branch:** product-architecture-evolution-2026-09-20  
**Baseline:** a86529327bceb440299cd7f02dae2261e7d2b843

---

## 1. Purpose

This document converts the founder's 2026-09-19/20 product notes into a research-backed product architecture amendment.

The goal is to preserve the already-certified POL core while avoiding premature financial custody, duplicated order models, duplicated mobile/web business logic, or insecure delivery links.

The canonical engineering baseline already contains several of the required foundations:

- Multi-vendor MVP allocation (D-014)
- OrderGroup -> Orders separation
- order-level payments and invoices
- non-custodial direct settlement
- retailer/vendor role separation
- delivery records without a dedicated driver organization
- barcode scan and product-match domain events
- Master Product vs Vendor Product / SKU separation

The work below therefore extends and connects existing primitives rather than introducing parallel concepts.

---

# 2. Research Findings

## 2.1 Financial history without a stored-value wallet

The current POL data model already has payments, payment attempts, refunds, settlements, and invoices. Therefore an MVP wallet is not required to provide a coherent financial-history experience.

The MVP should expose a Financial Activity view composed from those canonical records:

- پرداخت
- استرداد وجه
- مبلغ سفارش
- مبلغ فاکتور
- وضعیت پرداخت
- وضعیت تسویه, where the viewer is authorized to see it

External marketplace payment architectures also separate the payment event from later movement of funds between parties; Stripe documents this explicitly for multi-party marketplace flows. This is useful as an architectural analogy, not as a recommendation to copy Stripe's custody model into POL. [1]

### Adopted direction

**No stored-value Wallet in MVP.**

POL must not represent a user-facing balance that users can deposit into, keep inside POL, or withdraw from as a wallet balance.

Instead, implement a Financial Activity read surface over the existing payment, refund, invoice, order and settlement data.

### Future-wallet readiness

Future Wallet support remains possible through a separate financial ledger/accounting subsystem.

The future wallet must be treated as a new financial domain, not as a reinterpretation of the current payments table.

Required future concepts:

- wallet/account
- immutable ledger entries
- available balance
- pending/held balance if ever required
- funding
- withdrawal
- refund/credit semantics
- reconciliation
- idempotency
- authorization and audit

No wallet schema is added in this wave.

---

## 2.2 One retailer checkout -> multiple vendor invoices

The existing POL order model already supports:

Basket -> AllocationPlan -> OrderGroup -> Order -> OrderItem

Under D-014, one retailer checkout can create multiple child orders.

Therefore the UX must make this relationship explicit:

**یک سفارش خرید -> چند سفارش بنکداری -> چند فاکتور**

The retailer should see one unified order first and then its vendor-specific commercial documents.

Required Order Detail information:

- total order amount
- participating vendors
- child-order status
- invoice count
- invoice amount per vendor
- payment status per invoice/order
- delivery state per child order

This is a UX exposure of the existing domain model; it does not require a competing invoice hierarchy.

Marketplace payment architectures similarly separate a customer purchase from seller-specific financial allocation. Stripe documents splitting one payment across multiple connected accounts. [1]

POL remains non-custodial and does not copy Stripe's custody model.

---

## 2.3 Delivery without a Driver App

The current POL model intentionally does not require a dedicated driver organization/application in MVP.

The correct MVP approach is a minimal Delivery Handoff Surface:

Dispatch -> Delivery Link -> Retailer/Receiver Confirmation -> POD

The delivery surface should contain only:

- order/delivery reference
- recipient/store
- delivery address or map action
- driver/carrier identity when applicable
- delivery checklist
- confirmation action

The final delivery confirmation remains tied to the retailer or authorized receiver and/or delivery OTP.

### Security requirements

A delivery link is a sensitive capability token. OWASP recommends cryptographically secure high-entropy identifiers, server-side expiration, controlled lifetime, and invalidation after use, and warns that URL-exposed identifiers can leak through logs/history/referrers. [2][3]

Therefore a delivery handoff token must be:

- cryptographically random
- opaque
- server-generated
- high entropy
- short-lived
- single-use where possible
- rate-limited
- invalidated after completion
- HTTPS only
- Cache-Control: no-store
- Referrer-Policy: no-referrer
- never sufficient by itself to change financial state
- backed by the delivery/order authorization context

The link is a restricted delivery task surface, not an authenticated user session.

No full driver account system is introduced in this wave.

---

## 2.4 Vendor-first discovery and Vendor Storefront

POL should support two equivalent discovery paths.

### Product-first

Search Product -> Compare Vendor Offers -> Add to Basket

### Vendor-first

Search Vendor -> Vendor Storefront -> Browse Vendor Catalog -> Add to Basket

This is important in B2B because retailers can have habitual or trusted suppliers.

### Vendor Storefront

A vendor page should expose:

- vendor identity
- activity/freshness signal
- catalog categories
- product listings
- prices
- availability
- packaging
- MOQ/MOV rules where applicable
- ordering action

The storefront is another view over the canonical Vendor/Product/Inventory domain, not a new commerce backend.

---

## 2.5 Settlement wording must not become a future promise

Do not use wording such as:

> «تضمین تسویه مستقیم پل»

because the financial operating model may evolve after the pilot.

Canonical neutral wording:

> **«پرداخت و تسویه طبق شرایط ثبت‌شده سفارش و طرفین معامله انجام می‌شود.»**

The UI should describe the current process without making a permanent promise about who will ultimately control or route funds.

---

## 2.6 Every persona on Web + Android, with manager-controlled access

All POL personas should be able to use both:

- Web client
- Android client

The two clients share:

- backend
- domain model
- identity
- organization context
- authorization policy
- APIs
- event semantics

They do not need identical screen layouts.

### Target access model

Organization -> Membership -> Role -> Delegated Permissions -> Client Surface

A manager can grant or revoke permitted capabilities for organization members within platform boundaries.

Example:

VENDOR_STAFF A:
- inventory.view
- inventory.scan
- order.view
- order.fulfillment

VENDOR_STAFF B:
- inventory.view
- inventory.scan
- inventory.adjust
- price.manage
- order.view
- order.fulfillment

The backend remains the final authority. Clients only expose authorized capabilities.

OWASP recommends least privilege and deny-by-default authorization. [4]

Therefore:

- hiding a button is not authorization
- client-side role checks are not sufficient
- every protected command/resource must be authorized server-side
- Web and Android must use the same authorization boundary

### Client strategy

Android should optimize for:

- field work
- warehouse work
- quick actions
- scanning
- picking
- dispatch
- delivery confirmation
- exception capture

Web should optimize for:

- management
- search
- catalog maintenance
- pricing
- reporting
- reconciliation
- multi-record operations

Both clients cover all personas; capabilities determine what each individual actually sees and can execute.

---

## 2.7 Scanner as a first-class operational capability

Barcode scanning is directly connected to:

- Master Product matching
- Vendor SKU mapping
- Inventory update
- candidate-product creation
- warehouse productivity

The repository already defines:

- product_barcode_scanned
- product_match_confirmed
- product_candidate_created
- inventory_quantity_updated

and a Continuous Scan UX.

Google ML Kit provides on-device Android barcode scanning, supports common formats such as EAN-13, EAN-8, UPC-A, UPC-E, Code 128, QR Code, Data Matrix and PDF417, and can operate without a network connection. Google also recommends restricting detected formats when the expected formats are known to improve scanning performance. [5][6]

### POL scanner direction

1. camera scanner
2. barcode normalization
3. product lookup
4. exact-match result
5. ambiguous-match result
6. unknown-product candidate flow
7. inventory quantity entry
8. price entry where authorized
9. Save & Next continuous scanning
10. offline capture where safe
11. server reconciliation after connectivity returns

Unknown scans must never silently create a canonical Master Product.

Unknown barcode:
Candidate -> Catalog review -> Approved Master Product

---

# 3. Product Architecture Result

POL becomes one product with two clients:

POL
- Web
- Android
- Shared FastAPI Boundary
- ApplicationContext
- Organization Membership
- Role + Permissions
- Domain Services
- PostgreSQL 18

The clients must not become separate backends.

---

# 4. Canonical UX Surface Expansion

## Retailer

- Product Search
- Vendor Search
- Vendor Storefront
- Unified Basket
- Multi-vendor Order Detail
- Invoice List
- Invoice Detail
- Financial Activity
- Delivery Tracking / Handoff
- Delivery Confirmation
- Dispute / Support

## Vendor

- Vendor Storefront Management
- Catalog
- Inventory
- Barcode Scanner
- Orders
- Picking / Packing
- Dispatch
- Delivery Handoff
- Payments / Receipts
- Settlements
- Financial Activity
- Staff & Permissions

## Operations

- User & Membership Management
- Permission Management
- Catalog Review
- Candidate Product Review
- Delivery Exceptions
- Payment/Reconciliation Exceptions
- Audit

All surfaces are organization-scoped and permission-enforced.

---

# 5. Implementation Order

## P0 — Product architecture and UX contract

1. Financial Activity read model specification
2. Multi-vendor order -> invoice UX contract
3. Vendor Search + Vendor Storefront
4. Delivery Handoff Surface
5. Neutral payment/settlement wording
6. Web + Android parity contract
7. Delegated permission model

## P1 — Engineering implementation

8. Permission catalog + delegated grants
9. Financial activity API/read model
10. Vendor search/storefront API
11. Delivery handoff token model/API
12. Android foundation for all personas
13. Scanner implementation
14. Master SKU/media provenance pipeline

## P2 — Future option value

15. Stored-value Wallet
16. Full Driver App
17. Advanced financial ledgering / wallet reconciliation
18. Richer offline sync

---

# 6. Scope Guardrails

This wave does not introduce:

- POL custody of user funds
- stored-value wallet balances
- a full driver application
- a second backend/runtime
- separate authorization logic per client
- automatic promotion of unknown barcodes to canonical products
- unsupported legal claims about product images or intellectual-property rights

---

# 7. Engineering Acceptance Criteria

### Authorization

- same permission semantics on Web and Android
- server-side enforcement
- deny-by-default
- organization scoped
- delegated permissions auditable

### Commerce

- one retailer checkout can show multiple child orders and invoices
- invoice visibility is tenant scoped
- financial activity links payment/refund/invoice/order records

### Delivery

- no driver app required for MVP
- delivery handoff is short-lived and restricted
- final delivery confirmation is auditable
- token misuse is rate limited and invalidated

### Catalog

- Master Product and Vendor SKU remain separate
- barcode scan never bypasses catalog governance
- image/media provenance is recorded

### Product

- vendor-first and product-first discovery both supported
- every persona can use the product through Web and Android
- each client exposes only capabilities authorized for the active membership

---

# 8. Research Sources

[1] Stripe — Create separate charges and transfers:
https://docs.stripe.com/connect/separate-charges-and-transfers

[2] OWASP — Forgot Password Cheat Sheet:
https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html

[3] OWASP — Session Management Cheat Sheet:
https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html

[4] OWASP — Authorization Cheat Sheet:
https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html

[5] Google ML Kit — Barcode Scanning:
https://developers.google.com/ml-kit/vision/barcode-scanning

[6] Google ML Kit — Barcode Scanning on Android:
https://developers.google.com/ml-kit/vision/barcode-scanning/android

---

## Final architectural position

**Wallet:** future-ready, not active.

**Order -> Invoice:** explicit in MVP UX.

**Delivery:** lightweight handoff surface, no full driver app in MVP.

**Vendor discovery:** product-first + vendor-first.

**Settlement language:** neutral and future-proof.

**Clients:** Web + Android for every persona, capability-driven by manager-controlled permissions.

**Scanner:** first-class Android operational capability.

**Master SKU/media:** preserve canonical identity and record provenance instead of embedding unverified rights claims.
