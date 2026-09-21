# POL — Master Product / UI / UX Tree & Penpot Build Specification
## Canonical Product Design Tree — GitHub × Penpot × Product Architecture × API × Permissions × Data × States × Dark/Light

**Document ID:** `POL-DESIGN-TREE-001`  
**Version:** `1.0.0`  
**Date:** 2026-09-21  
**Status:** ACTIVE DESIGN BLUEPRINT / PENPOT BUILD SOURCE  
**Repository:** `rrasi90/POL-2.3`  
**Working Branch:** `product-architecture-evolution-2026-09-20`  
**Primary Intent:** تبدیل معماری محصول، مستندات، APIها، مدل داده، نقش‌ها، state machineها و وضعیت فعلی Penpot به یک درخت واحد و قابل‌ردگیری برای ساخت/تکمیل طراحی.

---

# 0. هدف سند

این سند یک فهرست ساده از صفحه‌ها نیست.

این سند باید به‌عنوان **Product Design Tree** برای POL استفاده شود؛ یعنی از ریشه محصول شروع شود و به ترتیب زیر پایین برود:

```
POL
├── Surface / Persona
│   ├── Page / Experience
│   │   ├── Screen / Frame
│   │   │   ├── Section
│   │   │   │   ├── Component
│   │   │   │   ├── Interaction
│   │   │   │   ├── State
│   │   │   │   ├── Data
│   │   │   │   ├── Permission
│   │   │   │   └── API / Domain Contract
│   │   │   └── Navigation / Relationship
│   │   └── Theme / Responsive Variants
│   └── Cross-surface Dependencies
└── Global Design System
    ├── Foundations
    ├── Components
    ├── Shared UX
    ├── States & Patterns
    ├── Prototypes
    └── QA
```

بنابراین «وجود یک Frame» به‌تنهایی به معنی تکمیل شدن capability نیست.

هر capability زمانی درختی کامل است که حداقل این لایه‌ها مشخص باشند:

1. مقصد/Persona
2. Screen
3. هدف صفحه
4. Sections
5. Actions
6. States
7. Data / Entities
8. Permission
9. API / Domain dependency
10. Navigation relationship
11. Light/Dark behavior
12. Mobile/Desktop behavior
13. Prototype coverage
14. QA coverage
15. Missing / Open Decision

---

# 1. SOURCE SNAPSHOT

## 1.1 GitHub

Canonical working repository:

`rrasi90/POL-2.3`

Architecture branch:

`product-architecture-evolution-2026-09-20`

Key architecture wave:

- `POL_00_PROJECT_CONTROL/PRODUCT_EVOLUTION/PRODUCT_ARCHITECTURE_EVOLUTION_WAVE_01_2026-09-20.md`
- GitHub Issue #5 — Product Architecture Wave 01
- GitHub PR #6 — `feat: add product architecture evolution wave 01`

Issue #5 explicitly identifies these P0/P1 design-relevant capabilities:

- Financial Activity read model
- OrderGroup → child Orders → Vendor Invoices UX
- Vendor Search + Vendor Storefront
- Lightweight Delivery Handoff without a full Driver App
- Neutral settlement wording
- Web + Android parity
- Delegated organization permissions
- Permission catalog / grants / revokes / audit
- Delivery handoff token
- Android foundation
- Barcode scanner / continuous scan
- Master SKU / media provenance

P2:

- Stored-value Wallet
- Full Driver App
- Advanced wallet reconciliation
- Rich offline sync

---

## 1.2 Penpot

Current Penpot export inspected:

- File: `New File 1`
- Penpot export version: `penpot/2.18.0-RC5`
- Revision: `116`
- Export modified: `2026-09-20T09:27:01.434350Z`
- 11 design pages

Pages:

1. `00 — Foundations`
2. `01 — Components`
3. `02 — Shared UX`
4. `03 — States & Patterns`
5. `04 — Retailer`
6. `05 — Vendor`
7. `06 — Operations`
8. `07 — Field Activator`
9. `08 — Corporate`
10. `09 — Prototypes & Flows`
11. `10 — Design QA`

The inspected export contains approximately 75 meaningful top-level design frames/boards plus a small number of generic `Text` / `Rectangle` artifacts that should not be treated as canonical screens.

---

# 2. SOURCE-OF-TRUTH RULE

When sources disagree:

**Architecture / adopted Product Evolution > API / data contract > explicit design specification > current Penpot artifact**

But a contradiction must NOT be silently erased.

Every contradiction must be registered under:

**CONFLICT / DECISION REQUIRED**

This prevents old Penpot content from silently becoming product behavior.

---

# 3. MASTER PRODUCT TREE

```mermaid
flowchart TD

  P[POL — B2B Wholesale Operating Platform]

  P --> F[00 Foundations]
  P --> C[01 Components]
  P --> SU[02 Shared UX]
  P --> ST[03 States & Patterns]

  P --> R[Retailer Surface]
  P --> V[Vendor Surface]
  P --> O[Operations Surface]
  P --> FA[Field Activator Surface]
  P --> CP[Corporate / Trust Surface]

  P --> PR[09 Prototypes & Flows]
  P --> QA[10 Design QA]

  R --> R_AUTH[Authentication & Activation]
  R --> R_DISC[Discovery]
  R --> R_COM[Commerce]
  R --> R_ORDER[Orders]
  R --> R_FIN[Financial Activity]
  R --> R_DEL[Delivery]
  R --> R_RET[Returns / Disputes]
  R --> R_SUPPORT[Support]
  R --> R_ACCOUNT[Account / Security]

  V --> V_AUTH[Authentication / Context]
  V --> V_STORE[Storefront]
  V --> V_CAT[Catalog]
  V --> V_INV[Inventory]
  V --> V_ORDER[Order Operations]
  V --> V_DEL[Dispatch / Handoff]
  V --> V_FIN[Finance]
  V --> V_STAFF[Staff / Permissions]
  V --> V_PROFILE[Vendor Profile]

  O --> O_QUEUE[Operational Queues]
  O --> O_CASE[Case / Arbitration]
  O --> O_FIN[Financial Investigation]
  O --> O_PERM[Permission Audit]
  O --> O_CAT[Catalog Governance]
  O --> O_MEDIA[Media Provenance]
  O --> O_DEL[Delivery Exceptions]
  O --> O_SUPPORT[Support]
  O --> O_PILOT[Pilot Analytics]
  O --> O_ADMIN[Admin / Context]

  FA --> FA_TASK[Tasks / Route]
  FA --> FA_ACT[Retailer Activation]
  FA --> FA_ORDER[Assisted Ordering]
  FA --> FA_VISIT[Visit / Follow-up]
  FA --> FA_NET[Weak Network]

  CP --> CP_HOME[Institutional Trust]
  CP --> CP_RETAIL[Retailer Value]
  CP --> CP_VENDOR[Vendor Value]
  CP --> CP_FLOW[How POL Works]
  CP --> CP_PILOT[Ahvaz Pilot]
  CP --> CP_LEGAL[Legal / Privacy / Contact]
```

---

# 4. GLOBAL DESIGN SYSTEM TREE

## 4.1 Foundations

Existing Penpot foundation areas include:

- Brand Identity & Official Logos
- Semantic Color Tokens & Roles
- Persian Typography & Numeric Scales
- Spacing, Elevation & Radius System
- RTL & Commercial Invariants
- Dark Mode Semantic Tokens & Surface Elevation

### Required canonical foundation layers

```
Foundations
├── Brand
│   ├── POL logo
│   ├── wordmark
│   ├── icon treatment
│   └── safe-area rules
├── Color
│   ├── light semantic tokens
│   ├── dark semantic tokens
│   ├── interactive
│   ├── success
│   ├── warning
│   ├── danger
│   ├── info
│   ├── disabled
│   └── focus
├── Typography
│   ├── Vazirmatn
│   ├── headings
│   ├── body
│   ├── labels
│   ├── tabular numerals
│   └── code / ID / SKU / barcode / URL treatment
├── Spacing
│   ├── 4/8pt system
│   ├── page margins
│   ├── section gaps
│   └── density variants
├── Shape
│   ├── radius
│   ├── border
│   └── elevation
├── Layout
│   ├── mobile
│   ├── tablet
│   ├── desktop
│   └── operations desktop
├── Direction
│   ├── RTL
│   ├── LTR
│   └── mixed-direction content
└── Accessibility
    ├── contrast
    ├── touch target
    ├── focus
    ├── error visibility
    └── non-color status indication
```

---

# 5. LIGHT / DARK THEME CONTRACT

Dark mode is not a separate visual product.

It is the same information architecture and component behavior with semantic token substitution.

## 5.1 Required modes

Every production surface must support:

- Light
- Dark

unless explicitly marked:

- `LIGHT_ONLY`
- `DARK_ONLY`
- `SYSTEM_ADAPTIVE`

## 5.2 Theme mapping

| Semantic role | Light | Dark | Rule |
|---|---|---|---|
| Canvas | Light background token | Dark background token | Never hard-code page color |
| Surface | Surface-1 | Dark Surface-1 | Preserve hierarchy |
| Elevated Surface | Surface-2 | Dark Surface-2 | Preserve depth |
| Primary Text | Text-Primary | Dark Text-Primary | Contrast first |
| Secondary Text | Text-Secondary | Dark Text-Secondary | Never use disabled as body text |
| Border | Border-Default | Border-Dark | Maintain structural separation |
| Accent | POL Accent | POL Accent Dark | Same semantic meaning |
| Success | Success | Success-Dark | Color + icon/text |
| Warning | Warning | Warning-Dark | Color + icon/text |
| Danger | Danger | Danger-Dark | Color + icon/text |
| Info | Info | Info-Dark | Color + icon/text |
| Focus | Focus | Focus-Dark | Keyboard/touch visible |

## 5.3 Dark-mode rules

Dark mode must preserve:

- hierarchy
- spacing
- information priority
- status semantics
- CTA order
- interaction patterns
- content density

Dark mode must NOT mean:

- simply inverting colors
- lowering contrast
- replacing all surfaces with one dark gray
- using glow/decorative gradients for status
- hiding secondary text
- changing meaning of state colors

---

# 6. COMPONENT TREE

```
Components
├── Navigation
│   ├── App Bar
│   ├── Side Navigation
│   ├── Bottom Navigation
│   ├── Breadcrumb
│   └── Context Switcher
├── Input
│   ├── Text Input
│   ├── Search
│   ├── Phone
│   ├── OTP
│   ├── Select
│   ├── Date
│   ├── Number
│   └── Quantity Stepper
├── Commerce
│   ├── Product Card
│   ├── Vendor Card
│   ├── Vendor Offer Row
│   ├── Basket Line
│   ├── Order Card
│   ├── OrderGroup Card
│   ├── Invoice Card
│   └── Allocation Group
├── Operational
│   ├── Queue Row
│   ├── SLA Badge
│   ├── Status Chip
│   ├── Exception Banner
│   ├── Timeline
│   ├── Evidence Block
│   └── Audit Event
├── Finance
│   ├── Financial Activity Row
│   ├── Payment Status
│   ├── Invoice Summary
│   ├── Settlement Status
│   └── Reconciliation Row
├── Security
│   ├── Permission Matrix
│   ├── Permission Editor
│   ├── Session Card
│   ├── OTP Input
│   └── Handoff Verification
├── Scanner
│   ├── Scanner Overlay
│   ├── Scan Result
│   ├── Candidate Product
│   ├── Exact Match
│   ├── Ambiguous Match
│   └── No Match
├── Media
│   ├── Media Card
│   ├── Upload
│   ├── Provenance Badge
│   ├── Approval Status
│   └── Evidence Preview
└── Feedback
    ├── Toast
    ├── Alert
    ├── Empty
    ├── Loading
    ├── Skeleton
    └── Network Banner
```

Every component must have:

- default
- hover where applicable
- pressed
- focus
- disabled
- loading
- error
- empty where applicable
- light
- dark
- mobile density
- desktop density where applicable

---

# 7. RETAILER TREE

## Retailer root

```
Retailer
├── Authentication & Activation
│   ├── RT-01 Authentication
│   ├── Shop Context
│   ├── First Use
│   └── Activation Success
├── Home
│   └── RT-02 Home & Operational Hub
├── Discovery
│   ├── RT-06 Search / Catalog / Filters
│   ├── RT-17 Vendor Search [NEW]
│   ├── RT-18 Vendor Storefront [NEW]
│   └── RT-07 Product Detail / Vendor Comparison
├── Commerce
│   ├── RT-03 Multi-Vendor Basket
│   ├── RT-14 Allocation Review
│   └── RT-04 Checkout / Confirmation
├── Orders
│   ├── RT-15 OrderGroup Detail [NEW]
│   ├── RT-08 Child Order Detail
│   ├── RT-10 Order History / Reorder
│   └── RT-20 Partial Acceptance Review [NEW]
├── Financial
│   └── RT-16 Financial Activity [NEW]
├── Delivery
│   ├── RT-05 Tracking & Delivery
│   └── RT-19 Delivery Handoff / Receiver Confirmation [NEW]
├── Returns / Disputes
│   └── RT-09 Returns / Dispute Filing
├── Account
│   ├── RT-12 / RT-13 Account
│   ├── Profile Completion
│   ├── Organization Context
│   └── Session Security
└── Support
    └── RT-12 / RT-13 Support
```

---

## RT-01 — Authentication & Activation

### Purpose
ورود/ثبت‌نام retailer، ایجاد tenant context و آماده‌سازی اولین خرید.

### Sections
1. Brand / identity
2. Phone
3. OTP
4. Shop context
5. Minimal activation guidance
6. Activation success

### Actions
- enter phone
- request OTP
- verify OTP
- resend
- change phone
- establish organization context
- continue to first action

### States
- initial
- submitting
- invalid phone
- invalid OTP
- expired OTP
- rate limited
- network failure
- authenticated
- organization selection

### Data
- user
- phone
- otp_challenge
- session
- organization
- membership

### API
- POST auth/request-otp
- POST auth/verify-otp
- POST auth/refresh
- POST auth/switch-organization

### Permission
Unauthenticated until verification; after login, scope by active membership.

### Theme
Light + Dark.

### Conflict
Technical Architecture currently specifies a **4-digit OTP**. Older retailer design specs/Penpot artifacts contain 6-digit / 5-box variants. Target new canonical design must use the current backend/auth contract; do not preserve an older OTP shape silently.

---

## RT-02 — Home & Operational Hub

### Purpose
به retailer بگو «الان چه کاری باید انجام بدهم؟»

### Sections
1. App bar
2. Active shop context
3. Notification/support
4. Today queue
5. Continue ordering
6. Reorder strip
7. Search
8. Category shortcuts
9. Bottom navigation

### Primary paths
Search / Continue purchase > attention item > reorder.

### States
- new user
- normal
- no history
- open exception
- degraded network

### Data
- recent orders
- pending orders
- notifications
- saved items
- active organization

### Relationships
Home → Search
Home → Order Detail
Home → Reorder
Home → Notifications
Home → Support

---

## RT-06 — Search / Catalog / Filter Drawer

### Purpose
Product-first discovery.

### Sections
1. Search
2. Scanner / SKU action where available
3. Recent searches
4. Category/filter chips
5. Results
6. Active filters
7. No result

### Result fields
- image
- product name
- pack
- MOQ
- price
- availability
- vendor
- quantity

### States
- initial
- suggestions
- loading
- results
- no result
- error
- filtered
- barcode lookup

### APIs
- GET categories
- GET products/search
- POST products/match-barcode
- GET products/{id}/vendors

---

## RT-17 — Vendor Search [NEW]

### Purpose
Vendor-first discovery for retailers with trusted/repeat suppliers.

### Sections
1. Vendor search field
2. Category
3. Location/context
4. Availability/freshness
5. Vendor results
6. Sort/filter
7. Empty state

### Vendor result fields
- vendor identity
- verification/freshness signal
- catalog coverage
- availability
- ordering constraints
- operating context

### Actions
- open storefront
- apply filter
- search again

### Relationship
Vendor Search → Vendor Storefront → Catalog → Product → Basket.

---

## RT-18 — Vendor Storefront [NEW]

### Purpose
یک Vendor را به‌عنوان یک B2B operating storefront نمایش می‌دهد.

### Sections
1. Vendor identity
2. Verification / freshness
3. Business context
4. Category shortcuts
5. Catalog
6. Product rows
7. Packaging
8. Price / availability
9. MOQ/MOV
10. Ordering CTA
11. Support / vendor policy where authorized

### Important rule
Storefront نباید به consumer marketplace تبدیل شود.

### Data
- vendor
- vendor_products
- inventory
- price
- packaging
- MOQ/MOV

### Relationships
Storefront → Product Detail
Storefront → Basket
Storefront → Vendor Profile where applicable

---

## RT-07 — Product Detail / Vendor Comparison

### Purpose
تصمیم خرید روی یک Master Product با چند Vendor Offer.

### Sections
1. Product media
2. Product identity
3. Pack/unit
4. Price
5. MOQ/MOV
6. Availability/freshness
7. Vendor
8. Quantity
9. Add to basket
10. Compare vendors
11. Provenance/media indicator

### Vendor comparison
Neutral comparison only.

Do not show:
«بهترین فروشنده»

unless a canonical ranking algorithm exists.

---

## RT-03 — Multi-Vendor Basket

### Purpose
جمع‌کردن کالاها پیش از allocation.

### Sections
1. Header
2. Basket lines
3. Changed/unavailable warnings
4. Vendor grouping after allocation when known
5. Totals
6. Commercial caveat
7. Continue

### States
- empty
- normal
- stale item
- price changed
- inventory changed
- network degraded
- revalidation required

---

## RT-14 — Allocation Review

### Purpose
نمایش اینکه Basket چگونه میان Vendorها تقسیم شده.

### Sections
1. Explanation
2. Allocation groups
3. Vendor identity
4. Assigned lines
5. Subtotal
6. Constraints
7. Changed line
8. Reason
9. Continue / edit

### Relationship
Basket → Allocation Review → Checkout.

---

## RT-04 — Checkout & Confirmation

### Purpose
آخرین review قبل از commit.

### Sections
1. Delivery/contact
2. Vendor / order groups
3. Direct settlement method
4. Evidence instruction where applicable
5. Final total
6. Important terms
7. Submit

### Rule
The UI must not imply one universal legal/vendor invoice.

### Outcome
POST /orders

---

## RT-15 — OrderGroup Detail [NEW]

### Purpose
نمایش parent purchase به همراه child orderهای مستقل.

### Tree

```
OrderGroup
├── Summary
│   ├── Group ID
│   ├── Overall state
│   ├── Total amount
│   ├── Vendor count
│   ├── Child order count
│   └── Invoice count
├── Vendor Order A
│   ├── Vendor
│   ├── Items
│   ├── Requested / Accepted / Rejected qty
│   ├── Invoice
│   ├── Payment
│   ├── Fulfillment
│   ├── Delivery
│   └── Dispute
└── Vendor Order B
    └── same structure
```

### Critical invariant
Checkout ≠ one universal vendor invoice.

Canonical:
**Checkout → OrderGroup → Vendor Orders → Vendor Invoices**

### Data
order_groups, orders, order_items, invoices, payments, deliveries, disputes, settlements.

---

## RT-08 — Child Order Detail

### Sections
1. Order header
2. Vendor
3. Items
4. Quantity states
5. Invoice
6. Payment state
7. Fulfillment timeline
8. Delivery/POD
9. Financial activity link
10. Issue/support link

### State
Use operational order state and separate dispute projection.

---

## RT-20 — Partial Acceptance Review [NEW]

### Purpose
Retailer proposal review when Vendor cannot fulfill the full requested quantity.

### Sections
1. Original request
2. Proposed acceptance
3. Differences
4. Reason
5. Impact on amount
6. Timeline
7. Approve
8. Decline

### Quantity table
- requested
- available
- accepted
- rejected

### Reasons
- stock shortage
- unavailable
- packaging constraint
- operational issue
- other

### Relationships
Vendor Partial Acceptance Proposal → Notification → RT-20 → Approve/Decline → Order state/timeline.

### API dependency
- GET/POST partial-acceptance-proposals
- approve proposal
- decline proposal

---

## RT-16 — Financial Activity [NEW]

### Purpose
Read-only financial visibility; **not a wallet**.

### Tree

```
Financial Activity
├── Filters
│   ├── Date
│   ├── OrderGroup
│   ├── Order
│   ├── Vendor
│   ├── Invoice
│   ├── Payment status
│   └── Settlement status
├── Activity list
└── Activity detail
    ├── Order
    ├── OrderGroup
    ├── Invoice
    ├── Payment
    ├── Refund
    └── Authorized settlement status
```

### States
- pending
- verified
- failed
- refunded
- disputed
- reconciled
- under review

### Rule
Never display:
- stored wallet balance
- POL customer funds
- POL-owned custody account

---

## RT-05 — Order Tracking / Delivery

### Sections
1. OrderGroup / Child Order context
2. Current state
3. Timeline
4. Vendor
5. Delivery reference
6. ETA/window
7. Exception
8. Handoff entry

### State model
- preparing
- ready
- dispatched
- in transit
- delivered
- exception

---

## RT-19 — Delivery Handoff / Receiver Confirmation [NEW]

### Purpose
Restricted operational handoff surface.

### Sections
1. Delivery reference
2. Store / recipient
3. Driver/carrier identity when applicable
4. Delivery checklist
5. Handoff token / OTP
6. Confirmation
7. POD result
8. Failure / retry

### Security states
- active
- invalid
- expired
- already used
- rate limited
- verified
- exception

### Rules
Token is:
- short-lived
- high entropy
- single-use where possible
- rate-limited
- not an auth session
- cannot independently change financial state

### MVP boundary
No full dedicated Driver App.

---

## RT-09 — Returns / Disputes

### Flow
1. select order
2. issue type
3. items/quantity
4. evidence
5. submit
6. track resolution

### Issue types
- incomplete
- wrong product
- damaged
- quantity mismatch
- other

### Data
dispute, dispute_items, evidence/media.

---

## RT-10 — Order History / Reorder

### Sections
- filters
- order cards
- historical price changes
- reorder diff
- compatible items
- adjustment

### Rule
Show change explicitly when historical price/availability differs.

---

## RT-12/13 — Account / Support / Security

### Account tree
```
Account
├── Personal profile
├── Profile completion
├── Organization context
├── Membership
├── Role
├── Permissions summary
├── Active sessions
│   ├── current
│   ├── other devices
│   └── revoke
├── Logout all
└── Support
```

### APIs
- GET/PUT profile
- GET profile/completion
- GET profile/context
- session revoke
- logout all where available

---

# 8. VENDOR TREE

```
Vendor
├── Dashboard
├── Storefront Management [NEW]
├── Catalog
├── Product / SKU
├── Pricing
├── Inventory
├── Daily Inventory Confirmation
├── Orders
│   ├── Queue
│   ├── Detail
│   └── Partial Acceptance [NEW]
├── Dispatch
├── Delivery Handoff
├── Financial Activity [NEW]
├── Reconciliation
├── Documents / Invoices
├── Staff / Delegated Permissions [NEW]
├── Profile
├── Customers
└── Referral
```

---

## VD-01 — Daily Inventory & Price

### Sections
1. inventory freshness
2. stale warning
3. inventory rows
4. price state
5. bulk actions
6. publish/confirm

### Inventory row
- product
- physical qty
- reserved
- sellable
- freshness
- action

Unknown ≠ zero.

---

## VD-02 — Order Acceptance Queue

### Desktop
Table:

`Order | Retailer | Amount | Age | Status | Exception | Action`

### Filters
- status
- date
- exception
- search

### SLA
Canonical vendor acceptance timeout:
**120 working minutes / 2 hours**, respecting the Ahvaz working calendar.

Any 30-minute Penpot copy is stale and must be corrected.

---

## VD-03 — Loading / Fleet / Delivery

### Sections
1. accepted orders
2. picking/packing
3. ready
4. driver/carrier metadata
5. dispatch
6. handoff
7. POD

### MVP rule
This is vendor-side dispatch orchestration, not a full standalone Driver App.

---

## VD-04 — Shortage / Discrepancy

### Sections
1. order context
2. expected
3. actual
4. difference
5. evidence
6. reason
7. action
8. audit

---

## VD-05 — Catalog / SKU / Packaging / Pricing Engine

### Product row
- master product
- vendor SKU
- pack
- price
- availability
- image
- updated at

### Relationships
Master Product ↔ Vendor Product/SKU.

Do not merge these concepts visually.

---

## VD-06 — Bank Reconciliation / Direct Settlement Audit

### Sections
1. expected
2. observed
3. payment evidence
4. reference
5. invoice
6. settlement status
7. mismatch
8. audit

### Financial rule
Neutral wording only.

---

## VD-07 — Settings / Staff

Existing staff surface is not enough by itself.

It must connect to VD-15.

---

## VD-12 — Vendor Profile & Identity

### Sections
- identity
- business metadata
- address
- operating info
- documents
- contact context

---

## VD-13 — Documents & Invoices

### Tree
```
Documents
├── Invoice List
├── Invoice Detail
├── Supporting Documents
├── Payment Evidence
└── Export/Download where permitted
```

---

## VD-14 — Vendor Storefront Management [NEW]

### Sections
1. vendor identity
2. storefront presentation
3. catalog categories
4. visibility
5. operating information
6. policies
7. contact context
8. preview

### Important
The management surface controls canonical Vendor profile/catalog exposure; it does not create a separate storefront data model.

---

## VD-15 — Staff & Delegated Permissions [NEW]

### Model

**Organization → Membership → Role → Delegated Permissions → Client Surface**

### Staff row
- member
- role
- status
- last activity
- permission summary

### Permission detail
```
Member
├── Base Role
├── Granted Permissions
├── Revoked Permissions / exclusions where supported
├── Effective Access
├── Client Surface
└── Audit History
```

### Example permissions
- catalog.view
- catalog.manage
- inventory.view
- inventory.scan
- inventory.adjust
- price.view
- price.manage
- order.view
- order.accept
- order.fulfillment
- delivery.dispatch
- delivery.handoff
- payment.view
- payment.record
- settlement.view
- membership.manage
- reports.view

### Security invariants
- deny by default
- least privilege
- tenant scoped
- privilege ceiling
- server-side enforcement
- auditability

---

## VD-16 — Barcode Scanner / Continuous Scan [NEW]

### Flow
```
Permission
→ Camera
→ Scan
→ Normalize Barcode
→ Match
├── EXACT
├── HIGH_CONFIDENCE
├── AMBIGUOUS
└── NO_MATCH
```

### Exact
Open matching product/SKU.

### High confidence
Show confidence and confirmation.

### Ambiguous
Show candidate products.

### No match
Manual search + candidate flow.

### Continuous scanning
- scan
- identify
- quantity
- price where authorized
- save & next
- session progress
- failure/retry
- connectivity feedback

### Permission
`inventory.scan` must be independently delegatable.

---

## VD-17 — Financial Activity [NEW]

Vendor-facing read model.

### Filters
- date
- order
- invoice
- payment
- refund
- settlement

### Detail
Financial Activity → Order → Invoice → Payment → Settlement status.

No wallet.

---

## VD-18 — Partial Acceptance Proposal [NEW]

### Flow
Order → inability to fully fulfill → proposal → retailer notification → retailer decision.

### Required
- requested
- available
- accepted
- rejected
- reason
- amount impact
- expiry / SLA context
- audit

---

## VD-08 — Referral

### Sections
- referral code/link
- share
- attribution
- redemption state

No reward wallet.

---

## VD-09 — Customers

### Customer row
- retailer
- recent orders
- relationship
- referral context

---

## VD-10 — Reconciliation

Exception-first.

### States
- matched
- mismatch
- pending evidence
- under review
- resolved

---

# 9. OPERATIONS TREE

```
Operations
├── OP-01 Exceptions
├── OP-02 Arbitration
├── OP-03 Reconciliation
├── OP-04 Ahvaz KPI / Health
├── OP-05 Support
├── OP-07 Risk / Notifications
├── OP-08 Notification Operations
├── OP-10 Admin / Context
├── OP-11 Permission Audit [NEW]
├── OP-12 Financial Activity Investigation [NEW]
├── OP-13 Master SKU / Candidate Review [NEW]
├── OP-14 Media Provenance Review [NEW]
└── OP-15 Delivery Handoff Exceptions [NEW]
```

---

## OP-01 — Exceptions

### Universal queue row
`Severity/State → Reason → Age → Owner → Action`

### Sources
- orders
- delivery
- payment
- support
- RMA
- reconciliation
- system/provider

---

## OP-02 — Arbitration

### Three-pane desktop
1. queue
2. case detail
3. evidence/decision

### Case detail
- entities
- timeline
- evidence
- decision
- audit

---

## OP-03 — Reconciliation

### Sections
- mismatch queue
- evidence
- expected vs observed
- resolution
- audit

---

## OP-04 — Ahvaz KPI / Health

Decision-grade, not decorative dashboard.

### Metrics
- activation
- independent orders
- repeat
- fill rate
- acceptance SLA
- exceptions
- referral attribution

---

## OP-05 — Support

Conversation-first.

### Context panel
- customer
- organization
- order
- order group
- invoice
- delivery
- previous tickets

---

## OP-07/08 — Risk / Notifications

### Risk
- severity
- reason
- evidence
- remediation history

### Notifications
- delivery attempt
- provider
- failure reason
- retry
- final state

---

## OP-10 — Admin / Context

Infrequent high-risk controls should remain separate from daily queues.

---

## OP-11 — Permission Audit [NEW]

### Audit record
- actor
- target membership
- permission
- action (Grant/Revoke)
- timestamp
- reason
- source client
- organization

### Filters
- actor
- permission
- target
- date
- action
- organization

---

## OP-12 — Financial Activity Investigation [NEW]

### Purpose
Cross-entity read-only trace.

### Tree
```
Financial Investigation
├── Activity
├── OrderGroup
├── Child Order
├── Vendor
├── Invoice
├── Payment
├── Refund
├── Settlement
├── Evidence
└── Audit
```

### Rule
No alternate financial source of truth.

---

## OP-13 — Master SKU / Candidate Review [NEW]

### Candidate
- barcode
- name
- brand
- manufacturer
- category
- packaging
- confidence
- source
- duplicate signal
- status

### States
- candidate
- needs review
- verified
- rejected
- duplicate
- merged

### Critical
Unknown barcode must never auto-promote to Master Product.

---

## OP-14 — Media Provenance Review [NEW]

### Canonical provenance
- VENDOR_UPLOADED
- MANUFACTURER_PROVIDED
- POL_OWNED
- USER_UPLOADED

### Additional metadata when applicable
- source_url
- source_type
- rights_status
- import_method
- imported_at
- verified_at
- verified_by

### Review states
- uploading
- active
- pending
- approved
- rejected
- private reference

### Rule
Publicly visible ≠ rights cleared.

---

## OP-15 — Delivery Handoff Exceptions [NEW]

### Exceptions
- token expired
- invalid
- replay/used
- rate limited
- recipient mismatch
- delivery context missing
- verification failed

### Resolution
- retry
- regenerate where authorized
- manual verification
- escalate
- close

---

# 10. FIELD ACTIVATOR TREE

```
Field Activator
├── FA-01 Daily Route & Task List
├── FA-02 In-Store Assisted Order Creation
├── FA-03 Onboarding & Merchant Consent
├── FA-04 Follow-up & Proof of Visit
└── FA-05 Weak Network & Offline Queue
```

## FA-01
`what → where → due → next action`

States:
- scheduled
- in progress
- blocked
- completed
- overdue

## FA-02

Persistent retailer context while searching/building basket.

Reuse retailer commerce components.

## FA-03

### Sections
- identity
- consent
- store context
- minimum data
- confirmation
- receipt

## FA-04

### Timeline
- current state
- note/evidence
- outcome
- next action

## FA-05

### MVP boundary
Current architecture marks rich offline sync as P2.

Therefore MVP design should emphasize:

- connection status
- local unsent state
- retry
- duplicate prevention
- last sync
- preserved input

It must not imply a fully distributed offline transaction engine unless separately adopted.

---

# 11. CORPORATE TREE

```
Corporate
├── CP-01 Institutional Landing & Trust Portal
├── CP-02 Ahvaz Pilot & Asset-Light Operational Model
├── CP-03 Non-Custodial Architecture & Trust Governance
└── CP-04…CP-08 About / Contact / Legal Portal
```

### Rules
Corporate UI must avoid unsupported claims such as:

- 100% guarantee
- guaranteed settlement
- guaranteed delivery
- unsupported market-size claims
- unsupported legal/compliance claims

Preferred framing:

- operational visibility
- documented process
- auditable workflow
- non-custodial architecture
- role-based access
- pilot scope
- evidence-based claims

---

# 12. PROTOTYPE TREE

## FL-01 — End-to-End Transaction

```
Retailer
→ Vendor Search / Product Search
→ Vendor Storefront
→ Product
→ Basket
→ Allocation Review
→ Checkout
→ OrderGroup
→ Vendor Child Orders
→ Vendor Invoices
→ Payment
→ Fulfillment
→ Dispatch
→ Delivery
→ Handoff
→ POD
→ Financial Activity
→ Settlement Status
```

## FL-02 — Failure / Recovery

Must cover:

- vendor rejection
- timeout
- partial acceptance
- payment failure
- delivery exception
- handoff failure
- network degradation
- support escalation

## FL-03 — Failure Branches / Dark Mode

All critical failures must be visible in dark mode without semantic loss.

---

# 13. STATE TREE

```
Global States
├── Loading
├── Empty
├── Error
├── Success
├── Partial
├── Pending
├── Disabled
├── Unauthorized
├── Permission Denied
├── Network Degraded
└── Retryable
```

## Financial States

- PENDING
- VERIFIED
- FAILED
- REFUNDED
- DISPUTED
- RECONCILED
- UNDER_REVIEW

## Order States

- DRAFT
- ACTIVE
- PENDING
- ACCEPTED
- PARTIALLY_ACCEPTED
- PROCESSING / PREPARING
- READY
- SHIPPED / DISPATCHED
- DELIVERED
- CANCELLED
- REJECTED where exposed as distinct source state

## OrderGroup States

- DRAFT
- ACTIVE
- COMPLETED
- PARTIALLY_COMPLETED
- CANCELLED

## Partial Acceptance States

- PROPOSED
- PENDING_REVIEW
- APPROVED
- DECLINED
- EXPIRED

## Scanner States

- CAMERA_PERMISSION_REQUEST
- CAMERA_PERMISSION_DENIED
- SCANNING
- DETECTED
- PROCESSING
- EXACT
- HIGH_CONFIDENCE
- AMBIGUOUS
- NO_MATCH
- NETWORK_ERROR
- RETRY

## Delivery Handoff States

- ACTIVE
- INVALID
- EXPIRED
- USED
- RATE_LIMITED
- VERIFIED
- ESCALATED

## Permission States

- NOT_AUTHORIZED
- GRANTED
- REVOKED
- PENDING_REVIEW

## Media States

- UPLOADING
- ACTIVE
- PENDING
- APPROVED
- REJECTED
- PRIVATE_REFERENCE

## Product Candidate States

- CANDIDATE
- NEEDS_REVIEW
- VERIFIED
- REJECTED
- DUPLICATE
- MERGED

---

# 14. ENTITY RELATIONSHIP TREE

```
User
└── Membership
    ├── Organization
    ├── Role
    └── Delegated Permissions
        └── Client Surface

Product Master
├── Category
├── Brand
├── Barcode
├── Product Media
└── Vendor Product / SKU
    ├── Vendor
    ├── Price
    ├── Inventory
    └── Packaging

Retailer
└── Basket
    └── Allocation Plan
        └── OrderGroup
            ├── Child Order A
            │   ├── Items
            │   ├── Invoice A
            │   ├── Payment A
            │   ├── Delivery A
            │   └── Settlement A
            └── Child Order B
                ├── Items
                ├── Invoice B
                ├── Payment B
                ├── Delivery B
                └── Settlement B

Order
├── Timeline
├── Dispute Projection
└── Support Context

Financial Activity
├── Payment
├── Refund
├── Order Amount
├── Invoice Amount
└── Authorized Settlement Status

Delivery
└── Handoff Token
    └── POD

Media Asset
└── Product Media
    ├── Provenance
    ├── Approval
    └── Source Metadata
```

---

# 15. CRITICAL NAVIGATION GRAPH

```mermaid
flowchart LR
  SEARCH[Search] --> PRODUCT[Product Detail]
  SEARCH --> VENDOR_SEARCH[Vendor Search]

  VENDOR_SEARCH --> STOREFRONT[Vendor Storefront]
  STOREFRONT --> PRODUCT

  PRODUCT --> COMPARE[Vendor Comparison]
  COMPARE --> BASKET[Basket]
  PRODUCT --> BASKET

  BASKET --> ALLOCATION[Allocation Review]
  ALLOCATION --> CHECKOUT[Checkout]
  CHECKOUT --> GROUP[OrderGroup]

  GROUP --> ORDER_A[Vendor Order A]
  GROUP --> ORDER_B[Vendor Order B]

  ORDER_A --> INV_A[Invoice A]
  ORDER_B --> INV_B[Invoice B]

  ORDER_A --> PARTIAL[Partial Acceptance]
  PARTIAL --> APPROVE[Approve / Decline]

  ORDER_A --> DELIVERY[Delivery]
  DELIVERY --> HANDOFF[Handoff]
  HANDOFF --> POD[POD]

  GROUP --> FIN[Financial Activity]
  FIN --> PAYMENT[Payment]
  FIN --> REFUND[Refund]
  FIN --> SETTLE[Settlement Status]

  ORDER_A --> DISPUTE[Dispute]
  DISPUTE --> SUPPORT[Support]
```

---

# 16. WEB / ANDROID PARITY TREE

## Shared

Both clients share:

- identity
- organization context
- role
- permissions
- backend
- domain model
- API contract
- event semantics

## Android emphasis

- barcode scan
- warehouse action
- quick order acceptance
- picking
- dispatch
- delivery confirmation
- exception capture
- field activity

## Web emphasis

- management
- tables
- catalog maintenance
- price history
- reconciliation
- staff permissions
- operations
- analytics
- multi-record work

### Rule
Android is not a reduced Web clone.

Web and Android may use different layouts for the same canonical capability.

---

# 17. PERMISSION TREE

```
Organization
└── Membership
    ├── Base Role
    ├── Delegated Grant
    ├── Delegated Revoke
    ├── Effective Permission Set
    └── Audit
```

## Permission examples

### Catalog
- catalog.view
- catalog.manage

### Inventory
- inventory.view
- inventory.scan
- inventory.adjust

### Pricing
- price.view
- price.manage

### Orders
- order.view
- order.accept
- order.fulfillment

### Delivery
- delivery.dispatch
- delivery.handoff

### Finance
- payment.view
- payment.record
- settlement.view

### People
- membership.manage

### Reporting
- reports.view

## Invariants

- deny by default
- server-side enforcement
- least privilege
- tenant isolation
- privilege ceiling
- auditability
- same authorization boundary on Web + Android

---

# 18. API / UI TRACEABILITY TREE

## Authentication

UI → API

- Request OTP → POST /api/v1/auth/request-otp
- Verify OTP → POST /api/v1/auth/verify-otp
- Refresh → POST /api/v1/auth/refresh
- Switch organization → POST /api/v1/auth/switch-organization
- Revoke current session → DELETE /api/v1/auth/sessions/current
- Revoke specific session → DELETE /api/v1/auth/sessions/{id}
- Logout all where implemented by canonical auth contract

## Catalog

- Search → GET /api/v1/catalog/products/search
- Categories → GET /api/v1/catalog/categories
- Barcode Match → POST /api/v1/catalog/products/match-barcode
- Product Vendors → GET /api/v1/catalog/products/{id}/vendors
- Candidate Create → POST /api/v1/catalog/candidates
- Candidate Approve → POST /api/v1/catalog/candidates/{id}/approve

## Vendor Inventory

- Continuous scan → POST /api/v1/vendor/inventory/continuous-scan
- Update price → PATCH /api/v1/vendor/inventory/{vendor_sku}/price
- Update quantity → PATCH /api/v1/vendor/inventory/{vendor_sku}/quantity
- Publish inventory → POST /api/v1/vendor/inventory/publish

## Media

- Presigned upload → POST /api/v1/media/presigned-url
- Confirm upload → POST /api/v1/media/confirm-upload

## Orders

- Quote → POST /api/v1/orders/quote
- Create → POST /api/v1/orders
- List → GET /api/v1/orders
- Detail → GET /api/v1/orders/{id}
- Status transition → PATCH /api/v1/orders/{id}/status
- Dispute → POST/PATCH canonical dispute routes
- Partial acceptance → canonical partial-acceptance proposal routes
- Timeline → canonical order timeline route where exposed

## Profile

- GET /profile
- PUT /profile
- GET /profile/completion
- GET /profile/context

### Rule
If a UI control has no supporting contract, mark:

`DESIGN DEPENDENCY / CONTRACT GAP`

Do not invent an API solely to justify a button.

---

# 19. MEDIA / PROVENANCE TREE

```
Product Media
├── Media Asset
│   ├── storage provider
│   ├── object key
│   ├── MIME
│   ├── size
│   ├── checksum
│   ├── uploader
│   └── status
├── Product Media
│   ├── media type
│   ├── sort order
│   ├── primary
│   ├── source provenance
│   ├── approval status
│   └── approver
└── External Source Metadata
    ├── source URL
    ├── source type
    ├── rights status
    ├── import method
    ├── imported at
    └── verified at
```

### Canonical provenance
- VENDOR_UPLOADED
- MANUFACTURER_PROVIDED
- POL_OWNED
- USER_UPLOADED

---

# 20. DESIGN QA TREE

```
Design QA
├── Architecture Coverage
├── Screen Coverage
├── Component Coverage
├── State Coverage
├── API Traceability
├── Permission Traceability
├── Data Traceability
├── RTL
├── LTR / Mixed Direction
├── Accessibility
├── Light Mode
├── Dark Mode
├── Responsive
│   ├── Mobile
│   ├── Tablet
│   ├── Desktop
│   └── Ops Desktop
├── Prototype
├── Error Recovery
└── Implementation Readiness
```

A QA result may only be:

- PASS
- OPEN
- BLOCKED
- NEEDS REVIEW
- DEPENDS ON CONTRACT

Never declare 100% PASS merely because frames exist.

---

# 21. PENPOT CURRENT → TARGET DELTA

## Existing and retain

### Retailer
- RT-01 Authentication
- RT-02 Home
- RT-03 Multi-Vendor Basket
- RT-04 Checkout
- RT-05 Tracking/Delivery
- RT-06 Search/Catalog
- RT-07 Product Detail/Vendor Comparison
- RT-08 Child Order
- RT-09 Return/Dispute
- RT-10 Order History/Reorder
- RT-12/13 Account/Support
- RT-14 Allocation Review

### Vendor
- VD-01 Inventory/Price
- VD-02 Order Acceptance
- VD-03 Loading/Delivery
- VD-04 Shortage/Discrepancy
- VD-05 Catalog/SKU/Pricing
- VD-06 Reconciliation/Settlement Audit
- VD-07 Settings/Staff
- VD-12 Vendor Profile
- VD-13 Documents/Invoices

### Operations
- OP-01 Exceptions
- OP-02 Arbitration
- OP-03 Reconciliation
- OP-04 Ahvaz KPI
- OP-05 Support
- OP-07 Risk/Notifications
- OP-08 Notifications/Risk
- OP-10 Admin/Context

### Field
- FA-01 Route/Tasks
- FA-02 Assisted Order
- FA-03 Onboarding/Consent
- FA-04 Follow-up/Proof
- FA-05 Weak Network

### Corporate
- CP-01 Landing/Trust
- CP-02 Ahvaz Pilot
- CP-03 Non-Custodial/Governance
- CP-04…08 Legal/About/Contact

### Prototype
- FL-01 End-to-End
- FL-02 Failure/Recovery
- FL-03 Failure/Edge Cases Dark

### QA
- QA-01 Master Certification
- QA-02 Craft Standards
- QA-03 Dark Mode Audit

---

# 22. REQUIRED NEW PENPOT BOARDS

## P0

### Retailer
- RT-15 — OrderGroup Detail
- RT-16 — Financial Activity
- RT-17 — Vendor Search
- RT-18 — Vendor Storefront
- RT-19 — Delivery Handoff / Receiver Confirmation
- RT-20 — Partial Acceptance Review

### Vendor
- VD-14 — Vendor Storefront Management
- VD-15 — Staff & Delegated Permissions
- VD-16 — Barcode Scanner / Continuous Scan
- VD-17 — Financial Activity
- VD-18 — Partial Acceptance Proposal

### Operations
- OP-11 — Permission Audit
- OP-12 — Financial Activity Investigation
- OP-13 — Master SKU / Candidate Review
- OP-14 — Media Provenance Review
- OP-15 — Delivery Handoff Exceptions

## Shared UX additions

- Permission lifecycle
- Financial Activity patterns
- OrderGroup / Invoice relationship
- Handoff token states
- Scanner lifecycle
- Candidate Product lifecycle
- Media provenance lifecycle
- Session / security patterns
- Partial acceptance patterns

---

# 23. CONTRADICTION REGISTER

| Topic | Existing Source | Current Canonical Direction | Design Action |
|---|---|---|---|
| Vendor acceptance | Penpot contains 30m | 120 working minutes / 2h | Replace all stale 30m references |
| OTP | Older Penpot/spec has 5/6-box OTP | Technical auth contract states 4-digit | Canonicalize design to auth contract; keep conflict recorded until verified |
| Settlement | Penpot contains guarantee-like wording | Neutral settlement visibility | Replace guarantee language |
| Driver | Some older architecture/test references mention Driver App | Wave 01 explicitly says no full Driver App in MVP | Keep lightweight handoff surface only |
| Offline | FA-05 implies richer offline flow | Rich offline sync is P2 | Constrain MVP to preserved input/retry/sync feedback |
| QA | Existing Penpot QA claims all pages passed | New architecture introduces uncovered capabilities | Reopen QA |
| Small text | Many 9–11px samples | Use larger UI text by default | Review and justify exceptions |
| RTL | Many Persian text nodes structurally use LTR paragraph flags | Mixed-direction correctness required | Visual QA all mixed data |

---

# 24. SCREEN RECORD SCHEMA

Every future Penpot screen in this project must be documented with this record:

```
SCREEN
├── ID
├── Name
├── Persona
├── Surface
├── Goal
├── Entry points
├── Exit / destinations
├── Primary action
├── Secondary actions
├── Sections
├── Components
├── Data entities
├── API dependencies
├── Permission dependencies
├── State matrix
├── Validation rules
├── Error / recovery
├── Light theme
├── Dark theme
├── Mobile behavior
├── Desktop behavior
├── Accessibility
├── Prototype coverage
├── Existing Penpot board
├── Required new board
├── Frontend route / contract
├── QA status
├── Dependencies
└── Open decisions
```

---

# 25. COMPONENT RECORD SCHEMA

```
COMPONENT
├── Component ID
├── Semantic purpose
├── Variants
├── Sizes
├── Density
├── Light
├── Dark
├── State model
├── Accessibility
├── RTL/LTR
├── Data contract
├── Events/actions
├── Parent surfaces
└── QA
```

---

# 26. STATE RECORD SCHEMA

```
STATE
├── Domain
├── State ID
├── Trigger
├── Visible content
├── Allowed actions
├── Forbidden actions
├── CTA
├── Recovery
├── Notification
├── Audit event
├── Light behavior
└── Dark behavior
```

---

# 27. RELATIONSHIP TYPES

Every meaningful node relationship should use one of these labels:

- `CONTAINS`
- `NAVIGATES_TO`
- `OPENS`
- `DEPENDS_ON`
- `READS_FROM`
- `WRITES_TO`
- `AUTHORIZED_BY`
- `TRIGGERS`
- `BLOCKED_BY`
- `ESCALATES_TO`
- `REUSES`
- `VARIANT_OF`
- `AUDITED_BY`
- `PROJECTS`
- `DERIVES_FROM`

This makes the tree more useful than a flat sitemap.

---

# 28. IMPLEMENTATION READINESS MATRIX

| Capability | UI | States | API | Permission | Prototype | Dark | Mobile | Desktop | QA |
|---|---|---|---|---|---|---|---|---|---|
| Authentication | Existing | Required | Yes | Yes | Partial | Yes | Yes | Yes | Reopen |
| Product Search | Existing | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Reopen |
| Vendor Search | Missing | Required | Wave 01 | Yes | Missing | Required | Yes | Yes | Open |
| Vendor Storefront | Missing | Required | Wave 01 | Yes | Missing | Required | Yes | Yes | Open |
| OrderGroup | Partial | Required | Yes | Yes | Partial | Required | Yes | Yes | Open |
| Financial Activity | Missing | Required | Read model | Yes | Missing | Required | Yes | Yes | Open |
| Partial Acceptance | Missing | Required | Yes | Yes | Missing | Required | Yes | Yes | Open |
| Scanner | Partial | Required | Yes | Yes | Missing | Required | Android-first | Desktop review | Open |
| Permissions | Partial | Required | Yes | Core | Missing | Required | Yes | Yes | Open |
| Handoff | Partial | Required | Wave 01 | Yes | Missing | Required | Yes | Yes | Open |
| Media Provenance | Partial | Required | Yes | Yes | Missing | Required | Yes | Yes | Open |
| Master SKU Candidate | Missing | Required | Yes | Ops-only | Missing | Required | Limited | Yes | Open |
| Sessions/Security | Partial | Required | Yes | Yes | Partial | Required | Yes | Yes | Open |

---

# 29. WHAT PENPOT MUST NEVER BECOME

Do not let the design accidentally become:

- a consumer marketplace
- a POL wallet
- a custody/escrow product
- a full Driver App in MVP
- a separate mobile business logic stack
- a generic ERP dashboard
- a decorative KPI wall
- a marketplace with unsupported rankings
- an auto-created Master Product system
- an untraceable financial UI
- a role-only client-side security model

---

# 30. FINAL BUILD ORDER FOR PENPOT

## Wave A — Canonicalize existing foundations
1. Foundations
2. Dark semantic tokens
3. RTL/mixed-direction rules
4. Components
5. Shared UX
6. States

## Wave B — P0 capability additions
7. RT-15 OrderGroup
8. RT-16 Financial Activity
9. RT-17 Vendor Search
10. RT-18 Vendor Storefront
11. RT-19 Delivery Handoff
12. RT-20 Partial Acceptance
13. VD-14 Storefront Management
14. VD-15 Permissions
15. VD-16 Scanner
16. VD-17 Financial Activity
17. VD-18 Partial Acceptance
18. OP-11 Permission Audit
19. OP-12 Financial Investigation
20. OP-13 Candidate Review
21. OP-14 Media Provenance
22. OP-15 Handoff Exceptions

## Wave C — Integration
23. update prototypes
24. update navigation
25. update notifications
26. update account/security
27. update delivery state
28. update financial traceability

## Wave D — QA
29. Light QA
30. Dark QA
31. RTL QA
32. Mobile QA
33. Desktop QA
34. API traceability
35. permission traceability
36. prototype QA
37. unresolved contradiction review

---

# 31. DEFINITION OF DONE

این سند و طراحی‌های متناظر فقط زمانی «کامل» تلقی می‌شوند که:

### Product
هر capability واقعی مسیر UX مشخص داشته باشد.

### Screen
هر screen هدف، section، action و destination داشته باشد.

### State
هر action مهم حداقل success/failure/loading/empty/permission state داشته باشد.

### Architecture
UI با domain model و state machine تضاد نداشته باشد.

### Financial
Financial Activity فقط read model باشد.

### Commerce
OrderGroup از child Orders و Vendor Invoices تفکیک شده باشد.

### Security
Permission، Session و Handoff به‌صورت قابل مشاهده و قابل audit طراحی شده باشند.

### Catalog
Master Product، Vendor SKU، barcode matching و candidate governance تفکیک شده باشند.

### Media
Media provenance قابل مشاهده باشد.

### Clients
Web و Android parity در capability داشته باشند، نه الزاماً layout یکسان.

### Theme
Light و Dark از semantic tokens استفاده کنند.

### RTL
Persian و mixed-direction data صحیح باشند.

### Prototype
Core transaction و failure branches قابل تست باشند.

### QA
هیچ ادعای PASS بدون evidence باقی نماند.

---

# 32. FINAL DESIGN PRINCIPLE

این فایل باید به‌عنوان **درخت مادر طراحی POL** در نظر گرفته شود.

Penpot نباید فقط مجموعه‌ای از mockupها باشد.

Penpot باید یک representation بصری از این زنجیره باشد:

**Business Capability → Persona → Surface → Screen → Section → Component → State → Action → Permission → Data → API → Domain Event → Audit → Prototype → QA**

بنابراین، هر چیزی که در این زنجیره وجود دارد اما در Penpot نمایش داده نشده، یک **Design Gap** است.

و هر چیزی که در Penpot وجود دارد اما در این زنجیره جای واقعی ندارد، یک **Unsupported / Unmapped Artifact** است.

---

# 33. OPERATING RULE FOR FUTURE DESIGN WORK

هر بار capability جدیدی به GitHub اضافه شد:

1. capability را به این tree اضافه کن.
2. Persona را تعیین کن.
3. Screen/Frame را مشخص کن.
4. child sections را ثبت کن.
5. stateها را ثبت کن.
6. API dependency را ثبت کن.
7. permission را ثبت کن.
8. relationshipها را ثبت کن.
9. Light/Dark را مشخص کن.
10. mobile/desktop behavior را ثبت کن.
11. prototype را update کن.
12. QA را reopen کن.

هیچ feature جدیدی نباید مستقیماً و بدون به‌روزرسانی این tree وارد Penpot شود.

---

# 34. SOURCE REFERENCES

- `POL_00_PROJECT_CONTROL/PRODUCT_EVOLUTION/PRODUCT_ARCHITECTURE_EVOLUTION_WAVE_01_2026-09-20.md`
- `POL_00_PROJECT_CONTROL/CAPABILITY_COVERAGE_MATRIX.md`
- `POL_00_PROJECT_CONTROL/PLATFORM_COMPLETION_GAP_REGISTER.md`
- `POL_00_PROJECT_CONTROL/PENPOT_COMPLETION_MATRIX.md`
- `13_PRODUCT_DESIGN/17_PENPOT_CANONICAL_BLUEPRINT.md`
- `13_PRODUCT_DESIGN/18_DESIGN_COMPLETION_PLAN.md`
- `13_PRODUCT_DESIGN/21_MVP_DESIGN_AND_FRONTEND_READINESS_GATE_2026-09-16.md`
- `13_PRODUCT_DESIGN/22_UI_UX_PAGE_AND_SECTION_COMPLETION_SPEC_2026-09-16.md`
- `13_PRODUCT_DESIGN/30_RETAILER_SCREEN_BY_SCREEN_SPEC_2026-09-16.md`
- `13_PRODUCT_DESIGN/31_VENDOR_OPS_FIELD_CORPORATE_SCREEN_BY_SCREEN_SPEC_2026-09-16.md`
- `13_PRODUCT_DESIGN/47_PROJECT_WIDE_BUG_AUDIT_2026-09-16.md`
- `06_PRODUCT/Roles_and_Permissions.md`
- `06_PRODUCT/Technical_Architecture_Spec.md`
- `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md`
- `08_DATA/PRODUCT_MEDIA_MODEL.md`

---

# 35. DOCUMENT STATUS

**Status:** Active.

**Interpretation:** This file is the canonical planning and traceability layer for the next Penpot completion wave. It does not claim that all listed screens already exist.

**Primary next action:** Build / update Penpot from this tree, then update the tree with actual Penpot frame IDs and QA evidence.

**Critical unresolved source conflicts:** OTP length representation, historical Driver App references, richer offline implications, and other stale Penpot wording must remain visible until canonicalized by the governing runtime/API contract.


---

# 36. DEEP AUDIT — SEMANTIC MODEL OF THE TREE

## 36.1 نتیجه بازرسی ساختاری

نسخه فعلی Tree از نظر «چه صفحه‌هایی لازم است؟» پایه خوبی دارد، اما برای تبدیل شدن به **Master Design Architecture** باید یک لایه دیگر به آن اضافه شود.

درخت نباید فقط این باشد:

`Surface → Screen → Section`

بلکه باید این ساختار را داشته باشد:

```
POL
└── Business Capability
    ├── Actor / Role
    ├── Surface / Client
    ├── Experience
    │   └── Screen
    │       ├── Section
    │       │   ├── Component
    │       │   ├── Data
    │       │   ├── Action
    │       │   ├── UI State
    │       │   └── Permission
    │       ├── Domain State
    │       ├── API Contract
    │       ├── Domain Event
    │       ├── Audit Event
    │       ├── Notification
    │       ├── Navigation
    │       ├── Light/Dark
    │       ├── Mobile/Desktop
    │       └── QA
    └── Cross-Surface Dependencies
```

این تفکیک ضروری است؛ زیرا یک «Role» با «Persona»، یک «Domain State» با «UI State»، و یک «Permission» با «Visibility» یک مفهوم نیست.

---

# 37. DEFINITIONS — معنی دقیق هر سطح

## 37.1 Business Capability

قابلیتی که سیستم باید برای کسب‌وکار فراهم کند.

مثال:

- Multi-Vendor Ordering
- Financial Visibility
- Vendor Discovery
- Inventory Adjustment
- Delivery Handoff
- Delegated Access

Capability پاسخ می‌دهد:

> سیستم چه مسئله‌ای را حل می‌کند؟

Capability مستقیماً UI نیست.

---

## 37.2 Actor

یک موجودیتی که در یک flow عملیاتی عمل انجام می‌دهد.

Actor می‌تواند باشد:

- human user
- organization member
- operator
- system worker
- external provider

مثال:

`Vendor Owner` یک human actor است.

`Notification Worker` یک system actor است.

---

## 37.3 Role

Role مجموعه‌ای از اختیارات پایه یک Membership است.

Roles canonical:

- ADMIN_SUPER
- OPS_AGENT
- FIELD_ACTIVATOR
- VENDOR_OWNER
- VENDOR_STAFF
- RETAILER_OWNER
- RETAILER_STAFF

Role تعیین می‌کند کاربر «در سازمان چه مسئولیتی دارد».

Role به‌تنهایی نباید به‌عنوان authorization نهایی مدل شود.

---

## 37.4 Persona

Persona از منظر طراحی تجربه تعریف می‌شود.

مثال:

- Retail Buyer
- Vendor Operator
- Operations Agent
- Field Activator
- Corporate Viewer

Persona ممکن است چند Role را شامل شود.

مثال:

`Retailer Experience`

می‌تواند:

- RETAILER_OWNER
- RETAILER_STAFF

را پوشش دهد.

---

## 37.5 Surface

محیط تعامل است.

نمونه:

- Retailer Mobile
- Vendor Web
- Operations Desktop
- Android Field
- Corporate Web

Surface الزاماً معادل Role نیست.

---

## 37.6 Experience

یک goal-oriented journey یا مجموعه flowهای مرتبط.

مثال:

`Vendor Order Acceptance Experience`

ممکن است شامل:

- Queue
- Detail
- Full Accept
- Partial Accept
- Reject
- Timeline

باشد.

---

## 37.7 Screen

یک destination یا stateful interface مستقل.

Screen باید ID یکتا داشته باشد.

مثال:

`VD-02`

---

## 37.8 Section

یک بخش معنایی داخل Screen.

مثال در Order Detail:

- Header
- Items
- Payment
- Invoice
- Delivery
- Timeline

Section نباید صرفاً یک مستطیل بصری باشد.

---

## 37.9 Component

یک building block reusable.

مثال:

- OrderGroup Card
- Financial Activity Row
- Permission Editor

---

## 37.10 Action

یک فرمان کاربر یا system action.

مثال:

- Accept
- Reject
- Grant
- Revoke
- Verify
- Retry
- Approve

هر Action باید:

- actor
- permission
- precondition
- validation
- result
- failure
- audit

داشته باشد.

---

## 37.11 UI State

حالتی که صرفاً نحوه نمایش/تعامل interface را تعریف می‌کند.

مثال:

- Loading
- Empty
- Disabled
- Modal Open
- Validation Error

---

## 37.12 Domain State

وضعیت واقعی موجودیت در business domain.

مثال:

`Order = ACCEPTED`

یا:

`Settlement = PENDING`

UI State و Domain State نباید با هم قاطی شوند.

---

## 37.13 Permission

مجوز اجرای یک capability/action است.

مثال:

`inventory.adjust`

وجود permission به معنی visibility نیست.

ممکن است UI یک action را برای کاربر نشان دهد ولی Backend آن را رد کند؛ طراحی باید این حالت را نیز مشخص کند.

---

## 37.14 Data Contract

تعریف داده‌ای که Screen می‌خواند یا می‌نویسد.

مثال:

Financial Activity:

- order_id
- invoice_id
- payment_status
- refund_status
- settlement_status

---

## 37.15 API Contract

مسیر runtime که interface را به application boundary متصل می‌کند.

باید مشخص شود:

- method
- route
- request
- response
- auth
- permission
- errors
- retryability

---

## 37.16 Domain Event

رخدادی که business state تغییر کرده است.

مثال:

- order_created
- order_accepted
- product_match_confirmed
- payment_verified

---

## 37.17 Audit Event

ثبت امنیتی/حاکمیتی یک عمل.

مثال:

`permission.granted`

با:

- actor
- target
- permission
- timestamp
- reason

---

## 37.18 Notification

پیامی که به actor اطلاع می‌دهد یک event یا change رخ داده است.

مثال:

Vendor partial acceptance proposal

→ Retailer notification

---

## 37.19 Navigation Relationship

نحوه انتقال کاربر بین nodes.

هر رابطه باید type داشته باشد:

- NAVIGATES_TO
- OPENS
- RETURNS_TO
- DEEP_LINKS_TO
- ESCALATES_TO

---

# 38. ROLE CATALOG — نقش دقیق هر Role

## 38.1 ADMIN_SUPER

### مأموریت
Governance سطح پلتفرم.

### مسئولیت
- platform configuration
- admin management
- security audit
- high-risk system actions
- global controls

### نباید
- به‌عنوان نقش روزمره Vendor یا Retailer استفاده شود.
- با delegation عادی سازمانی قابل تفویض باشد.

### Surface
Operations / Admin Web.

### حساسیت
CRITICAL.

### Audit
تمام تغییرات حساس.

---

## 38.2 OPS_AGENT

### مأموریت
اجرای عملیات روزانه POL.

### مسئولیت
- exceptions
- disputes
- support
- catalog review
- candidate product review
- broadcast
- operational intervention
- reconciliation review

### Surface
Operations Web.

### Primary queue
Exception-first.

---

## 38.3 FIELD_ACTIVATOR

### مأموریت
فعال‌سازی و آموزش retailer.

### مسئولیت
- store onboarding
- consent
- assisted order
- visit proof
- follow-up
- field tasks

### عدم اختیار پیش‌فرض
- مدیریت مالی
- تغییر settlement
- تغییر global roles
- promotion of Master Product

### Surface
Android-first Field.

---

## 38.4 VENDOR_OWNER

### مأموریت
مدیریت تجاری و عملیاتی Vendor.

### مسئولیت
- catalog
- price
- inventory
- order acceptance
- fulfillment
- staff
- documents
- settlement visibility

### قابلیت delegation
مدیریت اعضای سازمان و تفویض capabilityهای مجاز.

---

## 38.5 VENDOR_STAFF

### مأموریت
اجرای عملیات انبار و سفارش.

### مسئولیت پایه
- inventory.view
- inventory.scan
- order.view
- order.fulfillment
- delivery.dispatch

### قابلیت‌های حساس
- inventory.adjust
- price.manage
- delivery.handoff

فقط در صورت delegation/authorization.

---

## 38.6 RETAILER_OWNER

### مأموریت
تصمیم‌گیری خرید B2B برای مغازه.

### مسئولیت
- search
- compare
- basket
- checkout
- order review
- payment evidence where relevant
- delivery confirmation
- dispute
- support
- retailer staff management

---

## 38.7 RETAILER_STAFF

### مأموریت
اجرای خرید/تحویل روزمره به نمایندگی از مغازه.

### مسئولیت پایه
- view orders
- follow delivery
- receiver confirmation
- quantity discrepancy reporting

### عدم اختیار پیش‌فرض
- organization-level governance
- high-risk financial changes

---

# 39. GLOBAL FOUNDATIONS — توضیح ریزدانه

## 39.1 Brand

### Logo
مسئول:

- product identity
- navigation anchor
- authentication identity

### Safe area
حداقل فاصله اطراف mark.

### Dark
لوگو باید نسخه مناسب contrast داشته باشد.

---

## 39.2 Color

Color token باید semantic باشد:

```
color.background.canvas
color.surface.1
color.surface.2
color.text.primary
color.text.secondary
color.border.default
color.action.primary
color.status.success
color.status.warning
color.status.danger
color.focus
```

هیچ Screen نباید مستقیماً HEX را در تعریف معنایی خود استفاده کند.

---

## 39.3 Typography

### Vazirmatn
فونت اصلی Persian UI.

### نقش‌های typographic

- Display
- H1
- H2
- H3
- Body
- Body Compact
- Label
- Caption
- Numeric
- Mono-like data

### داده‌های حساس به direction

- SKU
- barcode
- invoice ID
- tracking ID
- phone
- email
- URL
- IBAN

باید direction مستقل داشته باشند.

---

## 39.4 Density

### Retailer
Low/Medium density.

### Vendor
Medium/High density.

### Operations
High density.

### Corporate
Low density.

Density نباید فقط با کوچک کردن font حاصل شود.

---

# 40. COMPONENT SYSTEM — نقش هر خانواده

## Navigation

### App Bar
مسئول:

- identity
- context
- global actions
- back/navigation

### Context Switcher
مسئول:

- organization
- active tenant
- membership context

### Bottom Navigation
Mobile operational navigation.

---

## Input

### Search
مسئول discovery، نه query execution.

### OTP
مسئول authentication verification.

### Quantity Stepper
باید:

- min
- max
- inventory constraint
- MOQ
- unit
- validation

را بشناسد.

---

## Commerce

### Product Card
نمایش:

- master product identity
- pack
- commercial offer
- availability

### Vendor Offer Row
رابط بین:

Master Product → Vendor Product → Offer.

### Basket Line
باید تفاوت:

requested quantity

و

allocated quantity

را تحمل کند.

---

## Operational

### Queue Row

هر Row:

`State → Reason → Age → Owner → Action`

را منتقل می‌کند.

### SLA Badge
نباید صرفاً countdown تزئینی باشد.

باید:

- SLA basis
- elapsed
- remaining
- breach

را در صورت نیاز نشان دهد.

---

## Finance

### Financial Activity Row

هر row باید context داشته باشد:

- type
- amount
- related object
- status
- timestamp

### Settlement Status

نباید به معنی custody یا guarantee باشد.

---

## Security

### Permission Editor

باید Effective Permission را نشان دهد، نه فقط checkbox خام.

### Session Card

باید:

- device
- client
- last active
- current session
- revoke

را داشته باشد.

### Handoff Verification

باید token را به delivery context متصل کند.

---

# 41. SHARED UX — نقش هر Pattern

## SH-01 Navigation
یک navigation grammar مشترک.

## SH-02 Revalidation / Conflict

زمانی استفاده می‌شود که client snapshot با canonical state متفاوت شده:

- price changed
- stock changed
- basket version changed

## SH-03 Notifications

Notification باید:

- source
- severity
- timestamp
- unread
- action

داشته باشد.

## SH-04 Evidence / POD

Evidence باید:

- type
- source
- uploader
- timestamp
- status
- linked object

داشته باشد.

---

# 42. STATE SYSTEM — تفکیک کامل

## 42.1 Product

### Domain states
- active
- inactive
- candidate
- archived

### Availability
- available
- low
- stale
- unknown
- unavailable

این دو state dimension نباید یکی شوند.

---

## 42.2 Order

### Lifecycle
- pending
- accepted
- partially accepted
- processing
- shipped
- delivered
- cancelled

### Dispute projection
- none
- open
- investigating
- resolved
- closed

Dispute state نباید lifecycle order را overwrite کند.

---

## 42.3 Payment

- pending
- initiated
- success
- failed
- cancelled

## 42.4 Settlement

- pending
- authorized
- held
- adjusted
- reconciled

### مهم
Payment state ≠ Settlement state.

---

# 43. RETAILER — SCREEN-BY-SCREEN ROLE SPECIFICATION

## RT-01 Authentication

### Actor
Unauthenticated user.

### Role transition
No membership → authenticated user → active organization membership.

### Business outcome
User can reach authorized Retailer surface.

### Side effects
- OTP challenge
- session creation
- organization context

---

## RT-02 Home

### Actor
Retailer Owner/Staff.

### Job
تشخیص next best operational action.

### Reads
- open orders
- notifications
- exceptions
- recent purchases

### Writes
Usually none; navigation actions only.

---

## RT-06 Search

### Actor
Retailer Owner/Staff.

### Job
Find canonical product.

### Reads
- categories
- products
- vendor offers
- inventory visibility

### Actions
- search
- filter
- scan
- open product

---

## RT-17 Vendor Search

### Actor
Retailer.

### Job
Find a trusted/desired supplier.

### Reads
- vendor identity
- catalog coverage
- availability signal
- commercial context

### Side effects
None until product selection/basket.

---

## RT-18 Vendor Storefront

### Actor
Retailer.

### Job
Browse one supplier's commercial catalog.

### Reads
- vendor
- vendor products
- price
- inventory
- packaging
- MOQ/MOV

### Critical UX boundary
Do not make “Vendor” look like a social profile; it is a commercial operating surface.

---

## RT-07 Product Detail

### Actor
Retailer.

### Job
Choose a purchasable offer for a Master Product.

### Reads
Master Product + Vendor Offers.

### Writes
Basket mutation.

---

## RT-03 Basket

### Actor
Retailer.

### Job
Build requested purchase.

### Critical logic
Basket quantity is not yet Vendor commitment.

---

## RT-14 Allocation Review

### Actor
Retailer.

### Job
Understand system/vendor allocation before commitment.

### Reads
AllocationPlan.

### Outcome
Approve allocation or return to basket.

---

## RT-04 Checkout

### Actor
Retailer Owner, or authorized Retailer member.

### Job
Commit purchase.

### Critical precondition
Canonical revalidation before create.

### Side effects
OrderGroup + child Orders + downstream events.

---

## RT-15 OrderGroup

### Actor
Retailer.

### Job
Understand one purchase composed of multiple vendor contracts.

### Primary relationship
OrderGroup is aggregation, not vendor invoice.

### Reads
- OrderGroup
- child orders
- invoices
- payments
- deliveries
- disputes
- settlement visibility

---

## RT-08 Child Order

### Actor
Retailer.

### Job
Inspect one vendor contract.

### Information hierarchy
Vendor → Items → Commercial document → Fulfillment → Delivery → Finance → Issues.

---

## RT-20 Partial Acceptance

### Actor
Retailer Owner or authorized staff.

### Job
Approve/decline Vendor proposal.

### Critical distinction
This is not editing the original order silently.

It is a proposal response.

---

## RT-16 Financial Activity

### Actor
Authorized retailer member.

### Job
Answer:

> چه رویداد مالی‌ای برای سفارش من اتفاق افتاده و وضعیت آن چیست؟

### Not allowed
Question like:

> موجودی پول من در POL چقدر است؟

because MVP has no stored-value wallet.

---

## RT-05 Delivery

### Actor
Retailer.

### Job
Track fulfillment/delivery.

### Side effects
No financial mutation through tracking screen.

---

## RT-19 Handoff

### Actor
Authorized receiver.

### Job
Confirm physical handoff.

### Security
Restricted capability.

### Side effect
POD / delivery completion.

---

## RT-09 Returns/Disputes

### Actor
Retailer.

### Job
Open structured commercial case.

### Critical separation
Dispute ≠ order lifecycle state.

---

## RT-10 Reorder

### Actor
Retailer.

### Job
Reuse historical purchase intent without blindly replaying stale commercial values.

---

## RT-12 Account

### Actor
Authenticated member.

### Job
Manage identity/context/security.

---

## RT-13 Support

### Actor
All authorized retailer members.

### Job
Get help with context attached.

---

# 44. VENDOR — SCREEN-BY-SCREEN ROLE SPECIFICATION

## VD-01 Inventory / Price

### Actor
Vendor Owner / authorized staff.

### Job
Keep sellable stock and price current.

### Critical distinction
Physical stock, reserved stock and sellable stock are different values.

---

## VD-02 Order Queue

### Actor
Vendor Owner / order-accept permission.

### Job
Decide within 120 working minutes.

### Primary actions
- accept
- reject
- propose partial acceptance

### SLA
Ahvaz working calendar.

---

## VD-03 Loading / Dispatch

### Actor
Vendor fulfillment staff.

### Job
Move accepted order through physical fulfillment.

### State progression
Accepted → Preparing → Ready → Dispatched.

---

## VD-04 Discrepancy

### Actor
Fulfillment staff.

### Job
Report expected vs actual quantities.

---

## VD-05 Catalog

### Actor
Vendor Owner / catalog.manage.

### Job
Maintain Vendor Product mapping to Master Product.

---

## VD-06 Reconciliation

### Actor
Vendor Owner / authorized finance member.

### Job
Compare commercial/financial evidence without implying POL custody.

---

## VD-07 Settings / Staff

### Actor
Vendor Owner.

### Job
Manage organization-level configuration.

---

## VD-14 Storefront Management

### Actor
Vendor Owner / delegated catalog owner.

### Job
Control public-to-retailer commercial representation.

---

## VD-15 Staff & Delegated Permissions

### Actor
Vendor Owner / membership.manage.

### Job
Configure effective capabilities.

### Critical output
Effective Permission Set.

Not merely raw checkbox state.

---

## VD-16 Scanner

### Actor
Vendor Owner or authorized staff with inventory.scan.

### Job
Fast inventory/catalog interaction.

### Special states
- camera permission denied
- no match
- ambiguous
- network degraded

---

## VD-17 Financial Activity

### Actor
Authorized vendor finance/owner.

### Job
Trace Vendor-side payment/refund/settlement activity.

---

## VD-18 Partial Acceptance

### Actor
Vendor with order acceptance/fulfillment authority.

### Job
Propose what can actually be fulfilled.

### Side effect
Creates proposal, not immediate order mutation until approved by allowed flow.

---

# 45. OPERATIONS — SCREEN-BY-SCREEN ROLE SPECIFICATION

## OP-01 Exceptions

### Actor
OPS_AGENT.

### Job
Find work requiring intervention.

### Universal model
Severity → Reason → Age → Owner → Action.

---

## OP-02 Arbitration

### Actor
OPS_AGENT; restricted high-risk actions may require elevated admin capability.

### Job
Resolve disputes without corrupting underlying order lifecycle.

---

## OP-03 Reconciliation

### Actor
OPS financial/operations authority.

### Job
Resolve mismatches.

---

## OP-04 Pilot Analytics

### Actor
OPS / authorized management.

### Job
Operational decision support.

### Not
Decorative dashboard.

---

## OP-05 Support

### Actor
OPS_AGENT.

### Job
Resolve support cases using contextual evidence.

---

## OP-07 Risk

### Actor
OPS_AGENT / admin depending action.

### Job
See reliability/risk events and remediation.

---

## OP-08 Notifications

### Actor
Operations.

### Job
Inspect delivery status of notification attempts.

---

## OP-10 Admin

### Actor
ADMIN_SUPER / authorized OPS.

### Job
Context/configuration controls.

---

## OP-11 Permission Audit

### Actor
OPS/security-authorized actor.

### Job
Investigate who granted what, to whom, when and why.

### Critical fields
actor, target, permission, action, timestamp, reason, client.

---

## OP-12 Financial Investigation

### Actor
Authorized finance/operations.

### Job
Trace canonical records across domains.

### Rule
Read/trace, not alternate ledger creation.

---

## OP-13 Candidate Review

### Actor
OPS catalog authority.

### Job
Prevent unknown barcodes from becoming Master Product automatically.

---

## OP-14 Media Provenance

### Actor
OPS catalog/media authority.

### Job
Validate source/provenance/approval of images.

---

## OP-15 Handoff Exceptions

### Actor
OPS_AGENT.

### Job
Resolve restricted delivery surface failures.

---

# 46. FIELD ACTIVATOR — DETAILED ROLE

## FA-01

### Actor
FIELD_ACTIVATOR.

### Job
Prioritize today's physical field work.

### Data
- task
- retailer
- location
- due time
- status

---

## FA-02

### Actor
FIELD_ACTIVATOR + Retailer.

### Job
Assist purchase without taking commercial ownership away from retailer.

### Important
The Field Activator is an assistant, not the commercial buyer unless the authorization model explicitly allows the action.

---

## FA-03

### Actor
FIELD_ACTIVATOR.

### Job
Collect only required onboarding data and consent.

### Evidence
Receipt/confirmation.

---

## FA-04

### Actor
FIELD_ACTIVATOR.

### Job
Record visit outcome and next action.

---

## FA-05

### Actor
FIELD_ACTIVATOR.

### Job
Preserve operational continuity during degraded connectivity.

### MVP boundary
No unverified rich offline transactional database.

---

# 47. CORPORATE — DETAILED AUDIENCE MODEL

Corporate screens are not an operational Role.

They are **external trust/audience experiences**.

Possible audiences:

- prospective retailer
- prospective vendor
- partner
- investor
- institutional stakeholder
- legal/privacy reader

Therefore the tree should treat Corporate as:

`Audience Surface`

not:

`User Role`.

---

# 48. PROTOTYPE ROLE

Prototype pages are not production surfaces.

They are **verification artifacts**.

Their job is to prove:

- navigation
- state transitions
- critical interactions
- happy path
- failure path
- role boundary
- theme consistency

A prototype screen can represent several production screens/states.

---

# 49. QA ROLE

QA page is not a design gallery.

It is the evidence layer.

For every certified surface:

```
Capability
→ Artifact
→ Contract
→ State
→ Theme
→ Responsive
→ Permission
→ Prototype
→ Evidence
→ Result
```

---

# 50. CROSS-SURFACE RELATIONSHIP MATRIX

## Product Discovery

Retailer Search
→ Product
→ Vendor Offer
→ Basket

Vendor Search
→ Vendor Storefront
→ Catalog
→ Product
→ Basket

## Order

Basket
→ Allocation
→ Checkout
→ OrderGroup
→ Child Order

## Finance

Child Order
→ Invoice
→ Payment
→ Refund
→ Settlement Status

OrderGroup
→ Financial Activity aggregation

## Delivery

Child Order
→ Delivery
→ Handoff
→ POD

## Exception

Any operational object
→ Exception
→ Support / Arbitration
→ Audit

## Security

Membership
→ Role
→ Delegated Permission
→ Client Capability
→ Audit

---

# 51. SIDE-EFFECT MATRIX

Every important action in the Tree should declare whether it:

| Action | Reads | Writes | Domain Event | Audit | Notification |
|---|---|---|---|---|---|
| Search | Catalog | No | No | No | No |
| Add to Basket | Product/Offer | Basket | Basket Updated | Usually no | No |
| Checkout | Basket/Allocation | OrderGroup/Orders | Order Created | Yes where required | Vendor Order Notification |
| Accept Order | Order | Order | Order Accepted | Yes | Retailer Notification |
| Partial Proposal | Order | Proposal | Proposal Created | Yes | Retailer Notification |
| Approve Partial | Proposal | Order/Proposal | Proposal Approved | Yes | Vendor Notification |
| Grant Permission | Membership | Permission Grant | Permission Granted | Yes | Target Notification |
| Revoke Permission | Membership | Permission Grant | Permission Revoked | Yes | Target Notification |
| Scan | Catalog/Inventory | Depending flow | Barcode Scanned | Optional | No |
| Candidate Approve | Candidate | Master Product | Product Match Confirmed | Yes | Relevant users |
| Handoff Verify | Delivery | Delivery/POD | Delivery Completed | Yes | Retailer/Vendor |
| Payment Evidence | Order/Invoice | Evidence | Payment Evidence Created | Yes | Authorized parties |

This matrix is part of the design contract.

---

# 52. VISIBILITY VS AUTHORIZATION

The Tree must explicitly distinguish:

### Visible
The user can see the UI element.

### Enabled
The user may attempt the action.

### Authorized
Backend permits the action.

### Audited
The action is recorded.

### Irreversible
The action has meaningful one-way consequence.

Example:

A Vendor Staff member may SEE an order.

They may not be ENABLED to reject it.

Or they may be enabled only if:

`order.accept`

is delegated.

Frontend visibility is never sufficient security.

---

# 53. DOMAIN STATE VS UI STATE EXAMPLE

For Vendor Order Queue:

### Domain
`order_status = PENDING`

### UI
- loading
- loaded
- filter active
- modal open

These are different axes.

The design tree must never represent UI loading as a business order state.

---

# 54. PENPOT AUDIT FINDINGS

## Finding 1 — OTP component conflict

Current Penpot contains:

`01 — Components / Form Inputs, Stepper & 5-Digit OTP`

Current Technical Architecture describes 4-digit OTP.

### Required action
Rename/update the component to canonical runtime value after contract verification.

---

## Finding 2 — Existing screen grouping hides semantic boundaries

Examples:

- RT-12 & RT-13 combined
- VD-07 contains Settings & Staff
- CP-04 to CP-08 represented as a combined portal
- OP-07 & OP-08 combined

### Required action
One physical Frame may still be acceptable for related views, but the Tree must map each logical experience separately.

---

## Finding 3 — State library is incomplete

Existing States page contains:

- product lifecycle
- basket/revalidation
- allocation
- order lifecycle
- RMA
- settlement

Missing explicit canonical patterns:

- Financial Activity
- Permission Lifecycle
- Scanner Lifecycle
- Handoff Lifecycle
- Partial Acceptance
- Candidate Product
- Media Provenance
- Session Security

---

## Finding 4 — Component page is incomplete against architecture

Architecture now requires explicit reusable patterns for:

- Financial Activity
- Permission Matrix
- Permission Editor
- Scanner
- Candidate Product
- Provenance Badge
- Handoff Verification
- Session Card
- Partial Acceptance

These should exist as reusable component definitions, not be invented separately on each screen.

---

## Finding 5 — Design QA is stale

Existing QA certification predates the complete Wave 01 delta.

Therefore it must be considered:

`REOPENED`

until the new capabilities are audited.

---

## Finding 6 — Current Penpot top-level artifact hygiene

The inspected export contains approximately:

- 69 named top-level frames
- 11 Root Frame placeholders
- 6 generic top-level Text/Rectangle artifacts

The generic artifacts must be reviewed and removed or mapped.

---

# 55. PENPOT CONSTRUCTION RULES — MICRO LEVEL

When building a new screen:

## Step 1
Create canonical Frame name.

Example:

`RT-16 — Financial Activity`

## Step 2
Create screen shell.

## Step 3
Add information hierarchy.

## Step 4
Attach reusable components.

## Step 5
Add data examples.

## Step 6
Add interaction states.

## Step 7
Add dark variant.

## Step 8
Add mobile variant.

## Step 9
Map permissions.

## Step 10
Map API.

## Step 11
Connect prototype.

## Step 12
Record QA.

A screen is incomplete if Steps 6–12 are missing.

---

# 56. DATA FIDELITY RULE

Mock values in Penpot must resemble canonical domain values.

Examples:

### Order
- order ID
- vendor
- status
- amount
- timestamp

### Invoice
- invoice ID
- issuing Vendor
- amount
- state

### Payment
- method
- amount
- status
- reference

### Settlement
- status
- relevant party/context
- adjustments where authorized

Do not fabricate business claims in sample data.

---

# 57. DESIGNING FINANCIAL LANGUAGE

Financial UX should distinguish:

- مبلغ سفارش
- مبلغ فاکتور
- پرداخت
- استرداد
- وضعیت پرداخت
- وضعیت تسویه
- adjustment
- dispute hold

Never collapse all into one generic:

`پرداخت شد`

when the underlying states differ.

---

# 58. DESIGNING ORDER LANGUAGE

Use:

### Parent
سفارش گروهی / OrderGroup

### Child
سفارش بنکداری / Vendor Order

### Document
فاکتور Vendor

### Operational
وضعیت آماده‌سازی / ارسال / تحویل

### Financial
وضعیت پرداخت / تسویه

These are different concepts and deserve separate visual treatment.

---

# 59. DESIGNING PARTIAL ACCEPTANCE LANGUAGE

Avoid presenting it as:

«سفارش شما تغییر کرد»

Prefer a proposal concept:

«بنکدار امکان تأمین کامل این اقلام را ندارد و پیشنهاد پذیرش جزئی ارسال کرده است.»

Then show:

- requested
- proposed
- difference
- reason
- commercial impact
- decision

This preserves agency and traceability.

---

# 60. DESIGNING DELIVERY HANDOFF LANGUAGE

Avoid implying:

«POL مسئول تحویل تضمینی است.»

Use operational wording:

- آماده تحویل
- در حال تأیید تحویل
- تأیید هویت گیرنده
- ثبت رسید تحویل
- خطا در تأیید
- نیاز به بررسی عملیات

No financial guarantee is implied.

---

# 61. DESIGNING PERMISSION LANGUAGE

Permission UX should explain:

### Base Role
The default responsibility.

### Delegated Permission
An additional capability explicitly granted.

### Effective Access
What the user can actually execute now.

### Audit
Who changed it.

This prevents a confusing checkbox-only model.

---

# 62. DESIGNING SCANNER LANGUAGE

### Exact
«کالای متناظر پیدا شد.»

### High Confidence
«احتمال تطابق بالا است — تأیید کنید.»

### Ambiguous
«چند کالای مشابه پیدا شد.»

### No Match
«کالایی با این بارکد پیدا نشد.»

Never say:

«محصول ساخته شد»

for a raw unknown barcode.

---

# 63. DESIGNING MEDIA PROVENANCE

Each canonical image should have a small semantic label where relevant:

- منبع سازنده
- بارگذاری بنکدار
- مالکیت/دارایی پُل
- بارگذاری کاربر

Approval:

- در انتظار بررسی
- تأییدشده
- ردشده
- مرجع خصوصی

---

# 64. RESPONSIVE DESIGN RESPONSIBILITY

## Mobile

Priority:
- one primary action
- compact hierarchy
- touch
- sticky action where necessary
- scanning
- quick confirmation

## Desktop

Priority:
- inspection
- comparison
- tables
- multi-record work
- side context
- audit detail

Responsive behavior must be documented per screen rather than assumed globally.

---

# 65. FINAL SEMANTIC CHECKLIST FOR EVERY SCREEN

Before marking a screen complete, answer all:

### Why
What problem does this screen solve?

### Who
Which actor uses it?

### Role
Which roles can act?

### Scope
Which organization/tenant context?

### Reads
Which data does it read?

### Writes
Which data can it modify?

### Action
What is the primary action?

### Permission
Which permission authorizes it?

### Preconditions
When can action execute?

### Success
What changes?

### Failure
What can fail?

### Recovery
How does user recover?

### Audit
What is logged?

### Notification
Who must be informed?

### Navigation
Where did user come from and where can they go?

### Theme
What changes in Dark?

### Platform
What differs on Android/Web?

### Accessibility
What must remain usable?

### QA
What evidence proves completion?

Only after all are answered should the Screen be marked fully mapped.

---

# 66. NEXT TREE EXPANSION PRIORITY

برای ادامه توسعه این سند، ترتیب دقیق باید این باشد:

1. Retailer deep tree
2. Vendor deep tree
3. Operations deep tree
4. Field deep tree
5. Corporate deep tree
6. Shared UX deep tree
7. State matrix
8. Permission matrix
9. API/data matrix
10. Penpot frame-to-tree ID mapping
11. Prototype coverage
12. QA evidence

The current document now defines the semantic vocabulary needed for these expansions.
