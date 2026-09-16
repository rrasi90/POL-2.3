# POL MVP Design & Frontend Readiness Gate — 2026-09-16

## Status
`DESIGN-READY / MOCK-FRONTEND-READY / PRODUCTION-RUNTIME-NOT-YET-READY`

## Purpose
This document closes the design-input gaps identified by the 2026-09-15 cross-project design audit and establishes the minimum contract set required before high-fidelity UI production and mock-first frontend implementation.

It does not override `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`, product/domain/data contracts, or the canonical application boundary.

## 1. Authority

1. `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`
2. Canonical product/domain/data/operations documents
3. `POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md`
4. `13_PRODUCT_DESIGN/14_DESIGN_DECISION_REGISTER.md`
5. This readiness gate
6. Penpot/Figma artifacts

Undocumented behavior remains `OPEN`; no design artifact may invent a business rule.

## 2. MVP product surfaces

### Retailer / POL Market
- Mobile-first Android + responsive Web/PWA
- Authentication and tenant context
- Home / current actions / reorder
- Search and catalog
- Product and vendor-offer comparison
- Unified basket
- Allocation review and revalidation
- Checkout / direct settlement evidence
- Order-group and child-order tracking
- Delivery / POD visibility
- Reorder
- RMA/dispute
- Support
- Notifications
- Profile/security/context

### Vendor / POL Vendor
- Responsive desktop-first Web + mobile support
- Authentication/context
- Queue-first dashboard
- Catalog / product listing
- Effective pricing
- Inventory and freshness
- Daily inventory confirmation
- Order acceptance/rejection/partial acceptance
- Fulfillment and delivery handoff
- Returns/disputes
- Payment/reconciliation evidence
- Vendor referral
- Staff/persona/context management
- Notifications and profile/security

### Operations / POL Ops
- Queue-first workbench
- Order/fulfillment exceptions
- Retailer/vendor context
- Allocation/inventory exceptions
- Payment reconciliation
- RMA/disputes
- Support
- Reliability/risk
- Notification delivery failures
- Audit/evidence
- Pilot analytics

### Field Activator / POL Field
- Task-first mobile workflow
- Retailer/vendor activation
- Assisted first order
- Follow-up
- Weak-network/retry/duplicate-prevention feedback
- History

### Corporate
- Public acquisition/trust surface only
- No unsupported product or commercial claims

## 3. Authentication & session UX contract

Canonical screens/states:
- Phone entry
- OTP entry
- OTP paste/autofill
- Incorrect OTP
- Expired OTP
- Resend countdown
- Rate-limit / blocked challenge
- Session expired
- Session revoked
- Active-session/device list
- Revoke other session
- Logout
- No active organization
- Organization/context selection

Rules:
- Authentication state is independent of persona.
- Active organization is resolved from authenticated session/membership context; never from arbitrary UI input.
- UI may show permission-dependent presentation but never grants authorization.
- Form values are preserved on recoverable validation errors.
- Accessible authentication patterns must be represented at component and flow level.

## 4. Identity / profile / persona mapping

Use the canonical conceptual chain:
`UserProfile → MembershipProfile → PersonaProfile → Security → Notifications → Active Tenant Context`

Profile UI may expose context and preferences but cannot edit RBAC.

Supported MVP persona presentations:
- Retailer owner/staff
- Vendor owner/staff with job function context
- Ops/support/finance/field operational scopes
- Field activator

The physical database table names are not UI vocabulary.

## 5. Commerce state library

### Product / offer
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
- unfulfilled
- changed after revalidation
- vendor unavailable
- commercial constraint
- user review required

A single basket remains the retailer mental model. Allocation may create multiple vendor child orders. One line item cannot be quantity-split across vendors in MVP.

### Order
- submitted / pending
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

For every state, design must show:
- meaning
- timestamp
- primary next action
- secondary action when valid
- forbidden action
- actor capable of changing state
- source of truth
- notification behavior
- deep-link destination

## 6. Checkout / payment / settlement UX boundary

Checkout must visually separate:
1. basket validation
2. allocation/revalidation result
3. address/contact confirmation
4. direct payment method/evidence path
5. final confirmation

Payment is non-custodial:
- no wallet balance
- no stored-value presentation
- no escrow implication
- no POL-held customer funds

Visible payment states may include:
- method selected
- settlement instruction
- evidence submitted/observed
- pending reconciliation
- reconciled
- evidence rejected
- no evidence
- unsupported evidence type

Client UI never becomes the authority for price, inventory, allocation, authorization or idempotency.

## 7. Delivery / POD boundary

MVP has no dedicated POL Driver product surface unless a later architecture decision creates one.

For current design:
- Retailer sees delivery status and POD state.
- Vendor sees fulfillment/delivery handoff state.
- Ops sees delivery exceptions and evidence.
- Physical delivery remains vendor / local hub / partner-carrier responsibility under the asset-light model.
- Do not design guaranteed driver ETA or unsupported offline delivery writes.

## 8. RMA / dispute UX contract

Required flow:
`Order/Delivery → report issue → select issue type → select item/quantity → evidence → submit → vendor response / operator review → clarification if needed → resolution → adjustment/refund state → closure`

Issue examples supported by the domain may include shortage, damage, mismatch, delivery delay and doorstep rejection.

Required states:
- draft
- submitted
- vendor response pending
- operator review
- clarification requested
- approved
- rejected
- adjustment pending
- refund pending
- refunded
- closed

Every dispute must preserve evidence, timeline and affected scope.

## 9. Support UX contract

Required capabilities:
- create case
- category/reason
- priority where supported
- attachments/evidence
- message thread
- assignment/ownership
- escalation
- SLA/age
- resolution
- reopen

Support UI must distinguish:
- user-correctable problem
- business-rule rejection
- system/service failure
- permission/tenant restriction

No raw stack traces or internal database details in end-user surfaces.

## 10. Notification UX contract

Notification architecture must distinguish:
- in-app inbox
- push
- SMS
- mandatory operational/legal notifications
- preference-controlled notifications
- delivery failure/retry
- read/unread state
- deep-link target

Critical transactional records cannot be hidden merely because a user disabled a preference channel.

Every notification type used in design must map to a known event/template/route contract.

## 11. Vendor comparison contract

A vendor-offer comparison surface is mandatory for retailer purchase decisions.

Show where available:
- vendor identity
- price
- pack/case size
- MOQ/MOV
- availability confidence/freshness
- relevant commercial constraints
- allocation impact

Do not label a vendor as cheapest/best unless the canonical runtime data and product rules explicitly support that claim.

## 12. Localization/content contract

MVP is Persian-first and RTL-first.

Required formatting and stress coverage:
- Persian UI copy
- Arabic/Persian digit policy
- Toman display
- phone number formatting
- Jalali/Gregorian display policy
- SKU/barcode/URL/ID mixed-direction handling
- numeric and tabular readability
- long Persian labels
- pluralization where applicable
- accessibility labels in Persian

Content claims must be classified as evidence, validated capability, target or hypothesis. Unsupported guarantees are prohibited.

## 13. Analytics / UX telemetry contract

Critical events to map to screens/components:
- onboarding_start
- onboarding_completed
- first_assisted_order
- first_independent_order
- search_success
- product_view
- add_to_basket
- allocation_review
- allocation_accepted
- checkout_success
- checkout_failure
- vendor_accept
- vendor_reject
- reorder
- exception_create
- exception_resolve
- support_create
- referral_redeem
- abandonment_point

Each event must define:
- event name
- triggering action/state
- actor/persona
- minimum properties
- source screen
- success/failure interpretation
- canonical downstream owner

Telemetry is measurement infrastructure, not a substitute for product state.

## 14. Frontend implementation contract

Approved implementation direction:
- Web: Next.js / React
- Retailer mobile: React Native / Expo
- Shared domain contracts and design tokens across surfaces
- Backend/application boundary remains authoritative

Frontend layers:
`UI components → feature/page modules → state/query layer → API/contract adapter → auth/session adapter → design tokens → analytics adapter`

Before HTTP runtime is complete, deterministic mock adapters may be used. Mocks must follow canonical contracts and be removable.

Never move business rules such as price, stock, allocation, permissions or order acceptance into frontend-only logic.

## 15. Screen-to-contract requirement

Every canonical screen must declare:
- route/surface
- persona/context
- primary job
- entry conditions
- data dependencies
- domain states represented
- primary/secondary actions
- loading/empty/error/partial states
- API/application-boundary dependencies
- analytics events
- notification/deep-link behavior
- accessibility requirements
- irreversible actions and recovery path

## 16. Design system acceptance gate

A component is not approved until applicable cases have been checked:
- default
- hover / pressed
- focus
- disabled
- loading
- empty
- error
- success
- permission denied
- long content
- RTL/LTR mixed content
- mobile/desktop variant
- keyboard behavior
- touch target size
- semantic color usage

The shared POL visual language must implement the operational hierarchy:
`Product → Pack → MOQ → Price → Availability → Vendor → Order State → Next Action`.

## 17. Production-readiness boundary

Design-ready and mock-frontend-ready does not mean production-ready.

Still outside the visual design gate:
- concrete HTTP runtime deployment
- production OTP/SMS credentials/provider certification
- refresh-token rotation infrastructure
- live push/SMS delivery certification
- observability/deployment/alerting
- backup/restore/PITR certification
- production migration operations
- complete client-to-API integration

These are implementation/release gates after design and mock-flow completion.

## 18. Final gate

The project may begin high-fidelity visual design and mock-first frontend implementation when:

- repository hardening branch passes current-head CI;
- canonical decisions are reconciled;
- foundations/tokens/components are defined;
- authentication/session states are covered;
- commerce/order/allocation states are covered;
- RMA/support/payment/notification states are covered;
- vendor comparison is explicit;
- localization/content rules are explicit;
- analytics events are mapped;
- each screen has a contract mapping;
- no UI requirement invents an unsupported backend capability.

This gate authorizes design and mock-first implementation. It does not certify the production runtime.
