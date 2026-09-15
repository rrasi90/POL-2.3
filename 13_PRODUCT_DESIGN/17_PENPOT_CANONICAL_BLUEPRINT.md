# POL Penpot Canonical Blueprint

Status: CANONICAL DESIGN EXECUTION BLUEPRINT

This document converts the written POL product/design source of truth into the structure that will be created in Penpot. It is an execution blueprint, not a replacement for product, engineering, business, or governance decisions.

## 1. Authority hierarchy

1. `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`
2. Canonical product/business/domain/data/operations documents
3. `13_PRODUCT_DESIGN/14_DESIGN_DECISION_REGISTER.md`
4. `13_PRODUCT_DESIGN/15_CROSS_PROJECT_DESIGN_AUDIT_2026-09-15.md`
5. This blueprint
6. Penpot artifacts

A Penpot screen may visualize a requirement, but it may not silently invent a product rule, permission, commercial policy, financial custody model, or operational guarantee.

## 2. Canonical Penpot page architecture

```text
POL — Product Design
├── 00 — Foundations
├── 01 — Components
├── 02 — Shared UX
├── 03 — States & Patterns
├── 04 — Retailer
├── 05 — Vendor
├── 06 — Operations
├── 07 — Field Activator
├── 08 — Corporate
├── 09 — Prototypes & Flows
└── 10 — Design QA
```

Do not collapse this into a four-page MVP structure. POL is a multi-surface operational system and the page structure must preserve shared patterns, state coverage, and role-specific workflows.

## 3. Foundations

`00 — Foundations`

Required artifacts:
- Brand identity
- POL logo usage
- Color roles and semantic tokens
- Typography and Persian typography test sheet
- Spacing scale
- Radius
- Elevation/shadow
- Iconography
- Grid and breakpoints
- RTL/LTR/mixed-direction rules
- Persian/Arabic numeral policy
- Toman/currency formatting
- Jalali/Gregorian date policy
- Phone formatting
- Motion principles
- Accessibility rules
- Content and localization rules
- Data-density rules
- Operational status language

Typography must not be locked to a custom Persian font until its availability in the target Penpot workspace is verified. Use a verified fallback during automation if necessary.

## 4. Components

`01 — Components`

Organize components by:
- Foundations
- Identity
- Navigation
- Commerce
- Operations
- Forms
- Feedback
- Data display
- Notifications
- Evidence/media
- Accessibility

Each reusable component requires:
- default
- loading
- empty
- error
- disabled
- permission denied where relevant
- long-content stress case where relevant
- RTL/mixed-content case where relevant
- mobile and desktop variants where relevant
- focus/keyboard state where applicable
- semantic token usage

High-priority components:
- Button
- IconButton
- TextField
- OTPField
- SearchField
- Select/Combobox
- QuantityStepper
- ProductCard
- ProductRow
- VendorOfferCard
- VendorComparisonRow
- Price/Pack/MOQ/Availability block
- BasketLine
- AllocationGroup
- OrderStatusTimeline
- DeliveryStatus
- EvidenceUploader
- IssueTypeSelector
- RMA/DisputeCard
- NotificationItem
- SupportCaseCard
- DataTable
- QueueItem
- KPICard
- ConfirmationDialog
- Toast/Banner
- Empty/Error/Retry pattern
- Profile/Persona header
- Tenant/context switcher

## 5. Shared UX

`02 — Shared UX`

### Authentication and session
- Phone entry
- OTP entry
- OTP paste/autofill
- Incorrect OTP
- Expired OTP
- Resend countdown
- Rate limit/blocked challenge
- Session expired
- Session revoked
- Logout
- Device/session list
- Revoke session
- No active organization
- Organization/context selection

### Identity/profile
Use conceptual model:
`UserProfile → MembershipProfile → PersonaProfile → Security → Notifications → Active Tenant Context`

Do not duplicate or redefine the canonical profile contract in UI artifacts.

### Shared patterns
- Search
- Notifications/inbox
- Deep links
- Preferences
- Support
- Permission denied
- Suspended account
- Vendor blocked
- Product unavailable
- Sensitive data masking
- Audit-sensitive confirmation
- Error recovery
- Empty/loading states
- Weak network/offline indication
- Evidence upload

## 6. States & Patterns

`03 — States & Patterns`

This page is mandatory before high-fidelity flow production.

### Product state matrix
- active
- unavailable
- unknown inventory
- stale inventory
- blocked/restricted
- price changed
- price effective in future
- vendor-specific price
- pack/case constraint
- MOQ/MOV not met

### Basket state matrix
- empty
- populated
- saved
- restored
- stale
- session expired
- item unavailable
- quantity invalid
- vendor unavailable
- revalidation required

### Allocation state matrix
- available
- partial
- unfulfilled
- changed after revalidation
- vendor unavailable
- commercial constraint
- user review required

### Order lifecycle matrix
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

For every state define:
- user-visible label
- semantic meaning
- primary next action
- secondary action
- forbidden action
- who can change state
- timestamp shown
- source of truth
- notification behavior
- deep-link target

### RMA/dispute matrix
- issue creation
- item/quantity selection
- evidence capture
- submitted
- vendor response
- operator review
- clarification requested
- approved
- rejected
- refund pending
- refunded
- adjustment
- closed

### Payment state matrix
Keep the model explicitly non-custodial:
- payment method selected
- direct settlement instruction
- evidence submitted/observed
- pending reconciliation
- reconciled
- evidence rejected
- no evidence
- unsupported evidence type

Never present POL as wallet, escrow, stored-value, or custodian of retailer funds.

## 7. Retailer

`04 — Retailer`

Required flow coverage:
1. Authentication
2. Onboarding
3. Home
4. Catalog
5. Search
6. Product detail
7. Vendor comparison
8. Basket
9. Allocation review
10. Checkout/direct settlement
11. Order confirmation
12. Order list/detail
13. Delivery/POD
14. Reorder/saved basket
15. Returns/disputes
16. Support
17. Notifications
18. Profile/security/preferences

Retailer primary hierarchy:
`Product → Pack → MOQ → Price → Availability → Vendor → Order State → Next Action`

Home should prioritize operational work such as reorder and open orders over generic consumer promotion.

## 8. Vendor

`05 — Vendor`

Required flow coverage:
1. Authentication/context
2. Dashboard
3. Catalog
4. Product/listing management
5. Effective pricing
6. Inventory
7. Daily inventory confirmation
8. Orders queue
9. Order acceptance/rejection
10. Preparation/fulfillment
11. Delivery handoff/POD visibility
12. Returns/disputes
13. Payment/reconciliation
14. Referral
15. Notifications
16. Staff/persona management
17. Profile/security

Dashboard is queue-first and exception-first, not vanity-KPI-first.

## 9. Operations

`06 — Operations`

Required workbench areas:
- Dashboard
- Queues
- Orders
- Retailers
- Vendors
- Allocation/inventory/delivery exceptions
- Payment/reconciliation
- RMA/disputes
- Support
- Risk/reliability
- Notifications
- Users/memberships/personas
- Audit
- Analytics

Every operational queue needs:
- reason code
- severity
- age/SLA
- owner/assignment
- evidence
- current state
- next action
- audit history

## 10. Field Activator

`07 — Field Activator`

Task-first mobile workflow:
- Login
- Task queue
- Retailer activation
- Assisted ordering
- Retailer profile/context
- Territory
- Task completion
- Weak network/offline indication
- Retry/sync
- Duplicate-prevention feedback
- Conflict handling
- History

Do not claim fully offline writes unless the backend/runtime explicitly supports them.

## 11. Corporate

`08 — Corporate`

Required pages:
- Home
- About
- How POL works
- For retailers
- For vendors
- Technology/operating model
- Trust/security
- Contact
- Legal
- Privacy

No unsupported claims such as guaranteed lowest price, guaranteed delivery time, or universal stock availability should be hard-coded.

## 12. Prototypes and flows

`09 — Prototypes & Flows`

Canonical prototypes:
- Retailer onboarding → first assisted order
- Retailer self-service first order
- Catalog → search → product → vendor comparison → basket
- Basket → allocation → revalidation → checkout
- Order → fulfillment → delivery/POD
- Reorder
- Return/dispute → evidence → resolution
- Vendor onboarding → catalog → inventory → daily confirmation
- Vendor order queue → acceptance → fulfillment
- Vendor referral → retailer redemption → attribution
- Field activation → assisted order
- Ops queue → investigation → resolution

Prototype each critical failure branch, not only happy paths.

## 13. Design QA

`10 — Design QA`

Every approved flow must pass:
- Functional state coverage
- Product-rule alignment
- RBAC/presentation separation
- RTL
- Persian typography
- Mixed-direction content
- Currency/date/phone formatting
- WCAG-oriented accessibility
- Keyboard/focus behavior where applicable
- Touch target sizing
- Responsive behavior
- Long-content stress
- Empty/loading/error states
- Network failure
- Notification/deep-link behavior
- Analytics event coverage
- Screen-to-contract mapping
- Visual consistency
- Content claim validation

## 14. Artifact naming

Use:
`[SURFACE]_[FLOW]_[SCREEN]_[STATE]_[BREAKPOINT]`

Examples:
- `RETAILER_ONBOARDING_PHONE_DEFAULT_MOBILE`
- `RETAILER_BASKET_REVALIDATION_REQUIRED_MOBILE`
- `VENDOR_ORDER_ACCEPTANCE_PENDING_DESKTOP`
- `OPS_RMA_REVIEW_EVIDENCE_REQUIRED_DESKTOP`

Components use PascalCase. Pages/boards use numbered semantic names. Do not create generic names such as `Frame 123` for canonical artifacts.

## 15. Generation protocol

Because Penpot automation is not transactionally atomic:

`Generate → Export → Inspect → Fix → Approve → Next`

Do not use one giant script for the entire product.

Preferred batches:
1. Foundations
2. Components
3. Shared UX
4. State library
5. Retailer
6. Vendor
7. Operations
8. Field Activator
9. Corporate
10. Prototypes
11. QA

After every major batch, export representative boards and inspect visual output before continuing.
