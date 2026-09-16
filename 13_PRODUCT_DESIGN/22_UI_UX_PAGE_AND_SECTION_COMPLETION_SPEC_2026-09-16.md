# POL MVP UI/UX Page & Section Completion Specification — 2026-09-16

## Status
`CANONICAL DESIGN EXECUTION SPECIFICATION`

## Purpose
This document completes the screen, section, state and navigation inventory required to start visual design and mock-first frontend implementation for POL MVP.

It is subordinate to the canonical Product Decision Register, canonical domain/API/application contracts and the existing POL design workstream. It does not create new business rules.

## 1. Simplicity principle

POL is a high-frequency B2B operational product. The UI must optimize for the shortest path to the correct action, not for maximum feature exposure.

### Simplicity rules
1. One primary job per screen.
2. One dominant primary action per screen where possible.
3. Show only the information needed for the next decision; expose secondary detail progressively.
4. Reuse the same components and interaction patterns across personas.
5. Never require users to reconstruct information already known by the system.
6. Prefer search, reorder and task queues over deep browsing for routine work.
7. Show commercial constraints before an action can fail: price, pack, MOQ/MOV, availability/freshness.
8. Do not hide operationally important information inside tooltips, decorative cards or modal dialogs.
9. Use progressive disclosure for advanced filters, history and audit details.
10. Preserve entered data during recoverable errors.
11. Prefer inline recovery and contextual next actions over generic error pages. GOV.UK guidance similarly recommends clear, specific recovery instructions and retaining entered values after validation errors. [Source: W3C/GOV.UK research]
12. Never use a UI distinction to imply a permission that is not enforced by the application boundary.
13. Do not introduce a screen merely because the backend has a table; every screen must support an MVP task.

## 2. Global shell

### Retailer mobile / PWA
Primary navigation:
- خانه
- خرید / جستجو
- سفارش‌ها
- سبد
- حساب

Global utilities:
- notifications
- support
- active shop/context when relevant
- back/deep-link handling

### Vendor
Desktop-first shell:
- dashboard
- orders
- inventory
- catalog & pricing
- customers
- daily confirmation
- referral
- reconciliation/documents
- staff/access
- profile

Use responsive mobile layout for urgent vendor tasks; do not simply shrink desktop tables.

### Ops
Desktop operational shell:
- overview/queues
- orders
- vendors
- retailers
- fulfillment exceptions
- support
- RMA/disputes
- reconciliation
- risk/reliability
- notifications
- pilot analytics

### Field
Task-first mobile shell:
- امروز
- مشتریان/سرنخ‌ها
- فعال‌سازی
- سفارش کمکی
- پیگیری‌ها
- مشکلات
- حساب

## 3. Shared UX layer

### 3.1 Authentication
Screens/states:
- phone entry
- phone submitted/loading
- OTP entry
- OTP autofill/paste
- incorrect OTP
- expired OTP
- resend countdown
- rate limit / blocked challenge
- successful authentication
- session expired
- session revoked
- no active organization
- organization/context selection
- logout confirmation where needed
- device/session list
- revoke other session

Simplicity: one question/action per step; do not request information already known.

### 3.2 Profile & security
Sections:
- profile summary
- personal details
- active organization/context
- persona/job context
- notifications
- security
- sessions/devices
- support

Persona adapts presentation; role/permission never comes from profile UI.

### 3.3 Notifications
- inbox
- unread filter
- operational notification detail
- mandatory notification marker
- preference-controlled channels
- failed delivery/retry state
- deep-link destination

### 3.4 Shared system states
Every surface must provide:
- loading
- empty
- error
- permission denied
- suspended/blocked
- network degraded
- retry
- success confirmation

## 4. States & Patterns library

### Product
- active
- unavailable
- unknown inventory
- stale inventory
- future-effective price
- price changed
- vendor-specific offer
- MOQ/MOV constraint
- pack/case constraint

### Basket
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

### Allocation
- fully available
- partially available
- unfulfilled line
- vendor changed
- price changed
- inventory changed
- commercial constraint
- user review required

### Order
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

### RMA/dispute
- issue creation
- issue type selection
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

### Payment/settlement
Non-custodial presentation only:
- method selected
- direct settlement instruction
- evidence submitted
- pending reconciliation
- reconciled
- rejected evidence
- no evidence
- unsupported evidence

## 5. Retailer — POL Market

### R-01 Onboarding
Screens:
1. welcome / value orientation
2. phone
3. OTP
4. shop identity/context
5. membership/context confirmation
6. first-use guide/coachmarks
7. first assisted order entry
8. activation success

Keep onboarding progressive. Collect only what is required for the next operational step.

### R-02 Home
Priority:
1. actions needed today
2. open orders
3. reorder/recent purchases
4. saved lists
5. high-confidence categories/search entry
6. relevant promotions only where evidence-backed

Do not use a consumer-style hero carousel.

### R-03 Search / Catalog
Sections:
- search field
- recent searches
- category entry
- barcode/SKU support where available
- filter/sort
- result list
- no-result recovery
- restricted/unavailable result treatment

Product result minimum hierarchy:
`Product → Pack → MOQ → Price → Availability → Vendor → Quantity`

Use compact rows for routine ordering; cards are allowed where image recognition genuinely helps.

### R-04 Product detail
Sections:
- product identity
- pack/unit
- price
- availability/freshness
- MOQ/MOV
- quantity stepper
- vendor offers
- vendor comparison entry
- add to basket
- saved/reorder action

Primary action must remain obvious; secondary information uses progressive disclosure.

### R-05 Vendor comparison
One comparison pattern, not separate vendor pages by default.

Compare:
- vendor name
- current price
- pack/case
- MOQ/MOV
- availability confidence/freshness
- relevant commercial constraints
- allocation impact

Avoid ranking language unless backed by an explicit canonical algorithm.

### R-06 Basket
Sections:
- line items
- quantity changes
- vendor allocation summary
- unavailable/changed items
- per-vendor subtotal where useful
- final total
- address/contact
- continue to review

Do not force the user to understand internal AllocationPlan mechanics.

### R-07 Allocation review
Purpose: make vendor splitting understandable before commitment.

Show:
- what is available
- which vendor supplies each line
- partial/unfulfilled lines
- price/inventory changes
- actions to accept/modify

Keep algorithm explanation collapsed unless needed.

### R-08 Checkout / confirmation
Stages:
1. validated basket
2. address/contact
3. payment/settlement method
4. payment evidence if applicable
5. final review
6. submit

Use clear final-total hierarchy. Avoid multi-step wizard complexity where one review screen is sufficient.

### R-09 Order group
Parent view:
- overall status
- total
- child vendors/orders
- major exceptions

Child order view:
- vendor
- items
- accepted/rejected quantities
- milestones
- delivery/POD
- payment evidence
- issue/return

### R-10 Reorder
Entry points:
- order detail → خرید مجدد
- purchase history → repeat
- saved list → add to basket

Historical changes must be explained inline before final checkout.

### R-11 Returns / disputes
Flow:
`Select order → select issue → select items/quantity → evidence → submit → track resolution`

### R-12 Support
- help entry
- create case
- category
- message/thread
- attachment
- status
- resolution
- reopen

### R-13 Account
Sections:
- profile
- shop
- addresses
- notification preferences
- security/sessions
- organization context
- usage guide

## 6. Vendor — POL Vendor

### V-01 Dashboard
Primary section is actionable queue:
- new orders
- overdue acceptance
- inventory confirmation
- low/stale inventory
- fulfillment exceptions
- unresolved returns/support
- referral activity

Secondary: selected KPIs.

### V-02 Orders queue
Columns/fields should be task-focused:
- order
- retailer
- age/SLA
- amount
- state
- exception flag
- next action

Support filtering and keyboard-safe table behavior. Sortable table controls should remain keyboard accessible. [Source: Carbon Design System]

### V-03 Order detail
Sections:
- order header/state
- retailer
- item lines
- accept/reject/partial accept
- reason
- preparation state
- handoff/delivery
- evidence/audit

### V-04 Catalog
- search/filter
- product identity
- vendor SKU
- pack
- price
- listing status
- image
- edit state

### V-05 Pricing
- current effective price
- future effective price
- price history
- validation/error state

### V-06 Inventory
- physical quantity
- reserved quantity
- available/sellable where supported
- freshness
- last confirmation
- stale/unknown state
- adjustment action

### V-07 Daily inventory confirmation
Single focused flow:
`Review → Confirm/Edit → Submit → Receipt`

No deep navigation.

### V-08 Referral
- create referral code/link
- share/copy
- attribution summary
- redemption status

No rewards/wallet/credit UI.

### V-09 Customers
- retailer list
- retailer profile summary
- order history
- relationship/referral context

### V-10 Reconciliation/documents
- payment/settlement evidence
- invoice/order references
- reconciliation status
- exception details

### V-11 Staff/access
- staff list
- invite/activation
- persona/job function
- access denied state
- active/inactive membership

### V-12 Vendor profile
- business identity
- operating context
- notifications
- security
- sessions

## 7. Operations — POL Ops

### O-01 Overview
A work queue first, not a dashboard wall.

Sections:
- critical queues
- aging/SLA
- exceptions
- system/provider health summary

### O-02 Unified queues
Filterable queues for:
- orders
- delivery exceptions
- support
- RMA
- reconciliation
- notifications
- vendor inventory confirmation
- risk/reliability

Every row needs reason, severity, age, owner and next action.

### O-03 Object detail
Common detail shell:
- current state
- timeline/audit
- linked retailer/vendor/order
- evidence
- allowed actions
- assignment

### O-04 RMA/Dispute workbench
- claim queue
- evidence review
- vendor response
- clarification
- approve/reject
- adjustment/refund status

### O-05 Support workbench
- case queue
- customer context
- conversation
- assignment/escalation
- SLA
- resolution

### O-06 Reconciliation
- payment evidence
- unmatched transactions
- settlement status
- discrepancy resolution

### O-07 Risk/Reliability
- reason codes
- severity
- reliability events
- evidence
- remediation history

### O-08 Notification operations
- delivery attempts
- failed providers
- retry state
- recipient/deep-link inspection

### O-09 Analytics / Pilot
- activation
- independent orders
- repeat
- fill rate
- acceptance SLA
- exceptions
- referral attribution

Do not turn pilot analytics into decorative BI before the operational queues work.

### O-10 Admin/context
- user/membership/persona context
- role-aware presentation
- audit
- configuration surfaces only for approved controls

## 8. Field Activator

### F-01 Today
- assigned tasks
- due/overdue
- next action

### F-02 Retailer activation
- find/create
- basic business context
- consent
- organization/membership
- profile/persona
- first assisted action
- receipt

### F-03 Assisted order
- retailer context
- search/catalog
- quantity
- basket
- allocation review
- submit via canonical boundary

### F-04 Follow-up
- task status
- notes/evidence
- outcome
- next action

### F-05 Weak network
- offline/degraded indicator
- unsent action
- retry
- last sync
- duplicate prevention
- conflict feedback

## 9. Corporate site

### C-01 Home
Value proposition → problem → how POL works → asset-light model → proof → CTA.

### C-02 Retailers
### C-03 Vendors
### C-04 How POL Works
### C-05 Ahvaz Pilot
### C-06 About
### C-07 Contact
### C-08 Legal / Privacy / Trust

No unsupported claims such as guaranteed lowest price or universal availability.

## 10. Cross-surface components that must be designed first

Priority order:
1. typography / semantic colors / spacing / radius / elevation
2. Button / Input / Search
3. Quantity Stepper
4. Status / Availability / MOQ / Price blocks
5. ProductRow / ProductCard
6. VendorOffer / Comparison
7. BasketLine / AllocationGroup
8. OrderCard / Timeline
9. Error / Empty / Loading / Retry
10. Navigation shells
11. Modal / Sheet / Confirmation
12. Notification / Banner / Toast
13. Evidence / Upload
14. Profile / Tenant / Persona context
15. Tables / Queue / Filters

## 11. Screen naming

Use:
`[SURFACE]_[FLOW]_[SCREEN]_[STATE]_[BREAKPOINT]`

Examples:
- `RETAILER_AUTH_OTP_DEFAULT_MOBILE`
- `RETAILER_CATALOG_SEARCH_EMPTY_MOBILE`
- `RETAILER_BASKET_REVALIDATION_REQUIRED_MOBILE`
- `VENDOR_ORDER_QUEUE_DEFAULT_DESKTOP`
- `OPS_RMA_REVIEW_EVIDENCE_REQUIRED_DESKTOP`
- `FIELD_ACTIVATION_NETWORK_DEGRADED_MOBILE`

## 12. Research-derived simplicity rules

The research baseline consistently supports fast reorder, purchase history, clear commercial constraints, order status and task-first mobile workflows. POL's own research synthesis therefore treats these as core rather than decorative features.

For forms and recoverable errors, current GOV.UK guidance recommends clear specific messages, preserving entered values and avoiding unnecessary validation while typing. citeturn234409search0turn234409search5

For dense operational tables, Carbon's current guidance emphasizes keyboard-accessible sorting and controls inside cells. citeturn234409search1turn234409search3

## 13. Design acceptance criteria

A screen is not complete unless:
- primary job is obvious;
- primary action is obvious;
- critical business information is visible at decision time;
- loading/empty/error/permission states are represented;
- RTL/LTR mixed content works;
- long Persian labels work;
- responsive behavior is specified;
- component states are mapped;
- backend/domain source of truth is identified;
- analytics events are identified;
- unsupported business claims are absent;
- recovery path is explicit.

## 14. High-fidelity execution order

### Batch 1
Foundations + accessibility annotations.

### Batch 2
Core commerce components + state library.

### Batch 3
Shared Auth/Profile/Notification/Support/RMA patterns.

### Batch 4
Retailer core loop.

### Batch 5
Vendor core loop.

### Batch 6
Ops workbench.

### Batch 7
Field Activator.

### Batch 8
Corporate.

### Batch 9
Critical prototypes + failure branches.

### Batch 10
Design QA + frontend contract mapping.

## 15. Research sources

- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- GOV.UK Design System — Error message: https://design-system.service.gov.uk/components/error-message/
- GOV.UK Design System — Error summary: https://design-system.service.gov.uk/components/error-summary/
- GOV.UK Design System — Validation: https://design-system.service.gov.uk/patterns/validation/
- Carbon Design System — Data table accessibility: https://carbondesignsystem.com/components/data-table/accessibility/
- POL repository research synthesis: `13_PRODUCT_DESIGN/01_DEEP_RESEARCH_SYNTHESIS.md`
- POL product/design blueprint: `13_PRODUCT_DESIGN/17_PENPOT_CANONICAL_BLUEPRINT.md`
