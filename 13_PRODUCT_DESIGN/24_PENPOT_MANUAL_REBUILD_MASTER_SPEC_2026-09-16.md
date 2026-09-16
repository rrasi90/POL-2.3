# POL — Penpot Manual Rebuild Master Specification

**Date:** 2026-09-16  
**Status:** CANONICAL HANDOFF FOR MANUAL PENPOT REBUILD  
**Purpose:** Provide a complete page-by-page, section-by-section and state-by-state implementation sheet for manually recreating the POL MVP design in Penpot.

> This document is a visual execution handoff. It does not create new business rules. Business/domain/authorization rules remain governed by the canonical Decision Register, product specification, API/data contracts and existing design source of truth.

## 0. Authority and execution rule

Use this order when a visual choice conflicts with another artifact:

1. `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`
2. Canonical product/business/domain/data/operations documents
3. `13_PRODUCT_DESIGN/14_DESIGN_DECISION_REGISTER.md`
4. `13_PRODUCT_DESIGN/15_CROSS_PROJECT_DESIGN_AUDIT_2026-09-15.md`
5. `13_PRODUCT_DESIGN/22_UI_UX_PAGE_AND_SECTION_COMPLETION_SPEC_2026-09-16.md`
6. This document
7. Penpot implementation

Never invent commercial rules, permissions, financial custody, inventory guarantees, SLA commitments or ranking logic in Penpot.

---

# 1. Penpot file/page structure

Create exactly these pages, in this order:

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

Do not collapse the architecture into fewer role pages.

---

# 2. Global Penpot frame conventions

## 2.1 Naming
Use:
`[SURFACE]_[FLOW]_[SCREEN]_[STATE]_[BREAKPOINT]`

Examples:
- `RETAILER_AUTH_OTP_DEFAULT_MOBILE`
- `RETAILER_CATALOG_SEARCH_EMPTY_MOBILE`
- `RETAILER_BASKET_REVALIDATION_REQUIRED_MOBILE`
- `VENDOR_ORDER_QUEUE_DEFAULT_DESKTOP`
- `OPS_RMA_REVIEW_EVIDENCE_REQUIRED_DESKTOP`
- `FIELD_ACTIVATION_NETWORK_DEGRADED_MOBILE`

## 2.2 Breakpoints

### Mobile
Primary retailer/field reference: 390 × 844.

### Desktop
Primary vendor/ops reference: 1440 × 1024.

### Corporate
Primary desktop reference: 1440 × 1200.

Also create responsive annotations for 360, 768 and 1024 widths where layout behavior changes.

## 2.3 RTL/LTR

- Persian UI is RTL by default.
- Product/SKU/phone/URL/code/payment references may remain LTR inside controlled containers.
- Never reverse identifiers, invoice numbers or alphanumeric SKUs.
- Mixed-direction text must be stress-tested with long Persian labels.

## 2.4 Visual language

- Midnight Navy foundation: `#0A1730`
- Primary CTA family: `#2563EB` / `#1D4ED8`
- Champagne Gold accent: `#F7D4B6`
- Digital UI: Vazirmatn where available/verified.
- Printed-document typography: B Lotus.
- Avoid decorative consumer-marketplace treatment.
- Prefer dense but legible operational layouts.
- Avoid unnecessary gradients, hero carousels and decorative dashboards.

## 2.5 Signature information hierarchy

For retailer commerce surfaces:
`Product → Pack → MOQ → Price → Availability → Vendor → Order State → Next Action`

For all operational surfaces:
`State/Severity → Reason → Age/SLA → Owner → Next Action`

---

# 3. 00 — Foundations

Create one clearly labelled board for each foundation area.

## FND-01 Brand
- POL corporate identity
- POL Market / پل مغازهدار
- POL Vendor / پل بنکدار
- logo clear-space and minimum size
- primary/secondary lockups
- approved logo assets

## FND-02 Semantic color tokens
Show:
- brand
- action
- success
- warning
- danger
- info
- neutral
- surface
- border
- text primary/secondary/muted/inverse
- disabled

## FND-03 Typography
Show a Persian specimen using:
- headings
- body
- captions
- tables
- numeric values
- mixed Persian/Latin product names
- long labels

## FND-04 Spacing / radius / elevation
Document the scale used by components and screen layouts.

## FND-05 Icons
Show:
- navigation
- search
- filter
- add/remove
- order states
- commerce
- support
- security
- evidence

## FND-06 Grid and responsive rules
Document:
- mobile page padding
- desktop content max-width
- table density
- card gaps
- column behavior
- mobile stacking rules

## FND-07 RTL/LTR and localization
Include examples for:
- Persian labels
- SKU
- phone
- URL
- dates
- currency/Toman
- Jalali/Gregorian

## FND-08 Accessibility
Annotate:
- contrast
- focus ring
- touch target
- keyboard order
- text scaling
- error recovery
- non-color status indicators

## FND-09 Data density and status language
Show canonical examples for:
- available
- unavailable
- stale
- pending
- exception
- completed
- blocked

---

# 4. 01 — Components

Build actual reusable components where Penpot supports components/variants. Do not leave this page as a visual-only catalog.

## 4.1 Foundations
- Button / primary / secondary / tertiary / danger / disabled / loading
- IconButton / default / hover / focus / disabled
- Divider
- Badge
- Tag

## 4.2 Forms
- TextField
- SearchField
- OTPField
- Select
- Combobox
- Date/input pattern
- QuantityStepper
- Checkbox
- Radio
- Switch
- FileUpload

## 4.3 Commerce
- ProductCard
- ProductRow
- PriceBlock
- PackBlock
- MOQBlock
- AvailabilityBlock
- VendorOfferCard
- VendorComparisonRow
- BasketLine
- AllocationGroup
- OrderCard
- OrderStatusTimeline
- DeliveryStatus

## 4.4 Operations
- QueueItem
- QueueTable
- KPI card
- SLA indicator
- Assignment selector
- Timeline
- Evidence item
- RMA/Dispute card
- SupportCaseCard

## 4.5 Feedback
- InlineError
- ErrorSummary
- EmptyState
- LoadingSkeleton
- RetryBlock
- PermissionDenied
- SuspendedState
- SuccessState
- NetworkDegraded
- Toast
- Banner
- ConfirmationDialog

## 4.6 Identity/context
- ProfileHeader
- ActiveOrganizationContext
- PersonaContext
- TenantSwitcher
- SessionRow
- NotificationItem

Every relevant component needs default, loading, empty, error, disabled, focus/keyboard and long-content stress variants.

---

# 5. 02 — Shared UX

## SH-01 Authentication
Frames:
1. phone entry
2. submitted/loading
3. OTP
4. OTP autofill/paste
5. incorrect OTP
6. expired OTP
7. resend countdown
8. rate limit/blocked
9. success
10. session expired
11. session revoked
12. no active organization
13. organization selection
14. logout confirmation
15. sessions/devices
16. revoke session

## SH-02 Profile & Security
Sections:
- profile summary
- personal details
- active organization
- persona/job context
- notifications
- security
- sessions/devices
- support

## SH-03 Notifications
- inbox
- unread filter
- notification detail
- mandatory marker
- channel preferences
- failed delivery
- deep link

## SH-04 Support
- help entry
- case creation
- case thread
- attachment
- status
- resolution
- reopen

## SH-05 Deep-link and recovery patterns
- missing target
- invalid link
- forbidden
- session expired
- retry
- preserved form data

---

# 6. 03 — States & Patterns

Create full state matrices. Each state board must include:
`Label → Meaning → Primary Next Action → Secondary Action → Forbidden Action → Actor/Authority → Timestamp → Source → Notification → Deep Link`

## ST-01 Product
- active
- unavailable
- unknown inventory
- stale inventory
- future-effective price
- price changed
- vendor-specific offer
- MOQ/MOV constraint
- pack/case constraint

## ST-02 Basket
- empty
- normal
- saved
- restored
- stale
- session expired
- item unavailable
- quantity invalid
- vendor unavailable
- revalidation required

## ST-03 Allocation
- fully available
- partially available
- unfulfilled line
- vendor changed
- price changed
- inventory changed
- commercial constraint
- review required

## ST-04 Order
- submitted
- accepted
- partially accepted
- rejected
- cancelled
- preparing
- ready
- dispatched
- delivered
- exception
- dispute
- adjustment
- refund pending
- refunded
- completed

## ST-05 RMA / Dispute
- issue creation
- type selection
- item/quantity selection
- evidence upload
- submitted
- vendor response
- operator review
- clarification requested
- approved
- rejected
- adjustment
- refund pending
- refunded
- closed

## ST-06 Payment / settlement
Non-custodial only:
- method selected
- direct settlement instruction
- evidence submitted
- pending reconciliation
- reconciled
- rejected evidence
- no evidence
- unsupported evidence

---

# 7. 04 — Retailer / POL Market

Primary frame size: 390 × 844. Use compact B2B ordering patterns.

## R-01 Onboarding
Frames:
- welcome
- phone
- OTP
- shop identity/context
- membership/context confirmation
- coachmarks
- first assisted order
- activation success

## R-02 Home
Sections, in order:
1. actions needed today
2. open orders
3. reorder/recent purchases
4. saved lists
5. category/search entry
6. evidence-backed promotions only

## R-03 Search / Catalog
Sections:
- search field
- recent searches
- categories
- barcode/SKU entry where supported
- filters/sort
- results
- no-result recovery
- restricted/unavailable result

## R-04 Product Detail
Sections:
- product identity
- pack/unit
- price
- availability/freshness
- MOQ/MOV
- quantity stepper
- vendor offers
- comparison entry
- add to basket
- save/reorder

## R-05 Vendor Comparison
Columns/rows:
- vendor
- price
- pack/case
- MOQ/MOV
- availability confidence/freshness
- commercial constraints
- allocation impact

No unsupported ranking language.

## R-06 Basket
Sections:
- line items
- quantity changes
- vendor allocation summary
- changed/unavailable lines
- per-vendor subtotal when useful
- final total
- contact/address
- continue to review

## R-07 Allocation Review
Sections:
- available lines
- vendor assignment
- partial/unfulfilled lines
- price changes
- inventory changes
- commercial constraints
- accept/modify actions

Keep algorithm detail collapsed.

## R-08 Checkout / Confirmation
Sections:
- validated basket
- address/contact
- direct settlement method
- evidence if applicable
- final review
- submit

## R-09 Order Group
Parent:
- overall state
- total
- child vendors/orders
- major exceptions

Child order:
- vendor
- items
- accepted/rejected qty
- milestones
- delivery/POD
- settlement evidence
- issue/return

## R-10 Reorder
Frames:
- from order detail
- from purchase history
- from saved list
- historical changes warning

## R-11 Returns / Disputes
Flow:
`Order → Issue → Items/Qty → Evidence → Submit → Track Resolution`

## R-12 Support
- help
- create case
- category
- thread
- attachment
- status
- resolution
- reopen

## R-13 Account
- profile
- shop
- addresses
- notification preferences
- security/sessions
- organization context
- usage guide

### Retailer critical prototypes
Prototype these paths end-to-end:
1. Search → Product → Add → Basket → Allocation → Checkout
2. Home → Reorder → Basket
3. Order → Issue → Evidence → Submit
4. Notification → Deep link → Correct object

---

# 8. 05 — Vendor / POL Vendor

Primary frame size: 1440 × 1024. Create a mobile responsive companion for urgent tasks.

## V-01 Dashboard
Top:
- actionable queue
- overdue acceptance
- inventory confirmation
- low/stale inventory
- fulfillment exceptions
- unresolved returns/support
- referral activity

Secondary:
- selected operational KPIs

## V-02 Orders Queue
Columns:
- order
- retailer
- age/SLA
- amount
- state
- exception
- next action

Include filters, search and keyboard-safe table behavior.

## V-03 Order Detail
- header/state
- retailer
- items
- accept/reject/partial accept
- reason
- preparation
- handoff/delivery
- evidence/audit

## V-04 Catalog
- search/filter
- product identity
- vendor SKU
- pack
- price
- listing status
- image
- edit state

## V-05 Pricing
- current effective price
- future-effective price
- price history
- validation/error

## V-06 Inventory
- physical quantity
- reserved quantity
- available/sellable where supported
- freshness
- last confirmation
- stale/unknown
- adjustment

## V-07 Daily Inventory Confirmation
Flow:
`Review → Confirm/Edit → Submit → Receipt`

## V-08 Referral
- referral code/link
- share/copy
- attribution summary
- redemption status

No rewards, wallet or credit UI.

## V-09 Customers
- retailer list
- profile summary
- order history
- relationship/referral context

## V-10 Reconciliation / Documents
- settlement evidence
- invoice/order refs
- reconciliation status
- exceptions

## V-11 Staff / Access
- staff list
- invite/activation
- persona/job function
- access denied
- active/inactive membership

## V-12 Vendor Profile
- business identity
- operating context
- notifications
- security
- sessions

### Vendor critical prototypes
1. Dashboard → Order → Accept
2. Dashboard → Inventory confirmation
3. Order → Partial accept → Reason → Submit
4. Reconciliation → Evidence → Result

---

# 9. 06 — Operations / POL Ops

Primary frame: 1440 × 1024.

## O-01 Overview
Work queue first:
- critical queues
- aging/SLA
- exceptions
- system/provider health

## O-02 Unified Queues
Filterable queues:
- orders
- delivery exceptions
- support
- RMA
- reconciliation
- notifications
- vendor inventory confirmation
- risk/reliability

Every row:
`Reason | Severity | Age | Owner | Next Action`

## O-03 Object Detail
Common shell:
- current state
- timeline/audit
- linked retailer/vendor/order
- evidence
- allowed actions
- assignment

## O-04 RMA / Dispute Workbench
- claim queue
- evidence review
- vendor response
- clarification
- approve/reject
- adjustment/refund status

## O-05 Support Workbench
- case queue
- customer context
- conversation
- assignment/escalation
- SLA
- resolution

## O-06 Reconciliation
- payment evidence
- unmatched transactions
- settlement status
- discrepancy resolution

## O-07 Risk / Reliability
- reason codes
- severity
- events
- evidence
- remediation history

## O-08 Notification Operations
- delivery attempts
- failed providers
- retry state
- recipient/deep-link inspection

## O-09 Pilot Analytics
Metrics surfaces:
- activation
- independent orders
- repeat
- fill rate
- acceptance SLA
- exceptions
- referral attribution

Keep analytics operational, not decorative.

## O-10 Admin / Context
- user/membership/persona context
- role-aware presentation
- audit
- approved configuration only

### Ops critical prototypes
1. Queue → Object detail → action → audit
2. RMA → evidence → review → decision
3. Reconciliation → discrepancy → resolution
4. Reliability event → remediation history

---

# 10. 07 — Field Activator

Primary frame: 390 × 844.

## F-01 Today
- assigned tasks
- due/overdue
- next action

## F-02 Retailer Activation
- find/create
- business context
- consent
- organization/membership
- profile/persona
- first assisted action
- receipt

## F-03 Assisted Order
- retailer context
- search/catalog
- quantity
- basket
- allocation review
- submit via canonical boundary

## F-04 Follow-up
- task status
- notes/evidence
- outcome
- next action

## F-05 Weak Network
- degraded/offline indicator
- unsent action
- retry
- last sync
- duplicate prevention
- conflict feedback

### Field critical prototype
`Today → Retailer → Assisted Order → Allocation → Submit → Receipt`

---

# 11. 08 — Corporate

Primary frame: 1440 × 1200.

## C-01 Home
Sections:
- value proposition
- problem
- how POL works
- asset-light operating model
- proof/evidence
- CTA

## C-02 Retailers
## C-03 Vendors
## C-04 How POL Works
## C-05 Ahvaz Pilot
## C-06 About
## C-07 Contact
## C-08 Legal / Privacy / Trust

No unsupported claims such as guaranteed lowest price or universal availability.

---

# 12. 09 — Prototypes & Flows

Create flow maps and then interactive prototypes for only the critical operational paths.

## PR-01 Retailer first order
`Auth → Home → Search → Product → Basket → Allocation → Checkout → Order Group`

## PR-02 Retailer reorder
`Home/History → Reorder → Review Changes → Basket → Checkout`

## PR-03 Retailer dispute
`Order → Return/Dispute → Issue → Evidence → Submit → Status`

## PR-04 Vendor fulfillment
`Dashboard → Queue → Order Detail → Accept/Partial/Reject → Preparation`

## PR-05 Vendor inventory confirmation
`Dashboard → Daily Confirmation → Edit → Confirm → Receipt`

## PR-06 Ops exception
`Overview → Queue → Object Detail → Evidence → Action → Audit`

## PR-07 Field assisted order
`Today → Retailer → Assisted Order → Allocation → Submit → Receipt`

## PR-08 Notification deep links
At least one example per major role.

## PR-09 Failure branches
Prototype:
- session expiration
- stale basket
- item unavailable
- price changed
- vendor unavailable
- network degraded
- permission denied
- evidence rejected

---

# 13. 10 — Design QA

Create a checklist board plus annotated screenshots/frames.

## QA-01 Information hierarchy
- one primary job per screen
- one dominant primary action
- critical decision data visible

## QA-02 Content
- Persian-first labels
- no unexplained English product jargon
- no emojis as functional UI
- long-label stress case
- mixed Persian/Latin stress case

## QA-03 Accessibility
- keyboard order
- focus visibility
- touch target
- contrast
- non-color status encoding
- zoom/text scaling

## QA-04 Responsive
- 360
- 390
- 768
- 1024
- 1440

## QA-05 State coverage
Every core screen has:
- loading
- empty
- error
- permission denied where relevant
- retry
- success confirmation

## QA-06 Domain fidelity
Verify:
- D-014 Multi-Vendor Basket preserved
- AllocationPlan is visible only as understandable outcome, not internal complexity
- D-016 referral active without reward
- D-017 universal profile/persona context
- no wallet/escrow/BNPL/custodial payment language
- no unauthorized role implications

## QA-07 Frontend handoff
Each finished screen must identify:
- source component
- state
- backend/domain source of truth
- analytics event(s)
- responsive behavior
- recovery path

---

# 14. Screen completion matrix

Mark each frame with one of:

- `WIREFRAME` — layout only
- `HI-FI` — production visual treatment
- `INTERACTIVE` — connected prototype
- `QA-PASS` — passes acceptance checklist

### Mandatory screen count

- Shared/Auth/Profile/Support/Notifications: 20+ states
- Retailer: R-01..R-13
- Vendor: V-01..V-12
- Operations: O-01..O-10
- Field: F-01..F-05
- Corporate: C-01..C-08
- Components: all listed in Section 4
- States: all listed in Section 6
- Prototypes: PR-01..PR-09
- QA: QA-01..QA-07

The minimum requirement is **functional coverage**, not merely one artboard per ID. Screens with materially different error/loading/empty/permission conditions require distinct state frames.

---

# 15. Manual Penpot build order

Follow this order exactly to minimize rework:

1. Foundations
2. Actual reusable Components
3. Shared UX
4. States & Patterns
5. Retailer core loop
6. Vendor core loop
7. Ops workbench
8. Field
9. Corporate
10. Prototypes
11. QA

Never polish downstream screens before the shared components and states are stable.

---

# 16. Final handoff rule

The Penpot file is complete only when:

- all 11 pages exist;
- all surface flows exist;
- critical components are reusable;
- state matrices are represented;
- critical prototypes work;
- Persian-first content is applied;
- responsive behavior is annotated;
- core accessibility requirements are visible;
- D-014/D-016/D-017 are preserved;
- financial custody boundaries are preserved;
- unsupported claims are absent;
- design QA is signed off.
