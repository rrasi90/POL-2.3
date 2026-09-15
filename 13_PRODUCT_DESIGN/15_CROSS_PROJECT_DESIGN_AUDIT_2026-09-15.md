# POL Cross-Project Product Design Audit — 2026-09-15

## Scope
This audit cross-checks the new `13_PRODUCT_DESIGN` workstream against the existing POL product, domain, data, operations, GTM and research documents on canonical branch `research-hardening-2026-09-14`.

## Overall verdict
`13_PRODUCT_DESIGN` is structurally sound and correctly establishes a written design source of truth before Figma. It covers the five major product surfaces and establishes the right design-system principles.

However, it is **not yet complete enough to enter high-fidelity Figma production without a second design-input pass**. Several existing capabilities and domain states are present elsewhere in the repository but have not yet been promoted into explicit design requirements.

## Coverage matrix

| Domain / capability | Design folder status | Required action |
|---|---|---|
| Brand / visual language | PARTIAL | Lock tokens only after contrast and Persian typography validation |
| Navigation / IA | COVERED | Add global notification/deep-link behavior matrix |
| Responsive / RTL / accessibility | COVERED | Add exact component acceptance measurements and keyboard/focus matrix |
| User Profile / Persona | COVERED ELSEWHERE + PARTIAL HERE | Pull canonical profile/security/session flows explicitly into design program |
| Auth / OTP / session lifecycle | MISSING | Add dedicated authentication UX contract before Figma auth screens |
| Retailer onboarding | PARTIAL | Reconcile assisted onboarding spec with self-service/runtime states |
| Retailer catalog/search | COVERED | Add barcode/SKU/pack/variant and no-result/restriction states |
| Vendor comparison | PARTIAL | Define explicit vendor-offer comparison pattern; PRD currently expects comparison |
| Basket | COVERED | Add save/restore/session-expiry/revalidation states |
| Multi-vendor allocation | COVERED | Need complete visual state matrix for partial/unfulfilled allocations |
| Checkout | PARTIAL | Add direct-payment/evidence, confirmation, replay/idempotency and failure states |
| Order lifecycle | PARTIAL | Map every canonical order state and allowed user action to UI |
| Delivery / POD | PARTIAL | Define dispatch, ETA, POD and delivery exception surfaces; no dedicated driver app is currently specified |
| Payment / settlement | PARTIAL | Define non-custodial payment evidence and reconciliation views without implying wallet/escrow |
| RMA / returns / disputes | MISSING | Add retailer, vendor and Ops flows plus evidence upload and refund/adjustment states |
| Support | MISSING | Add support inbox/thread/create/escalation/attachment states |
| Notifications / inbox | PARTIAL | Add notification center, mandatory vs preference-controlled channels, delivery states and deep links |
| Vendor dashboard | COVERED | Add queue counts, stale inventory, acceptance SLA and exception drill-down states |
| Vendor catalog/price | PARTIAL | Include effective-date price, historical visibility and rejected/blocked listing states |
| Vendor inventory | COVERED | Add stale/unknown/reserved/physical reconciliation and confirmation failure states |
| Daily inventory confirmation | COVERED | Add reminder, overdue, routing-error and confirmation receipt states |
| Vendor referral | COVERED | Add retailer redemption/deep-link path and attribution confirmation |
| Staff / persona UX | COVERED | Add invitation/activation, context switch and access-denied states |
| Ops workbench | COVERED | Add cross-domain object timeline and bulk/queue operation patterns |
| Risk / reliability | PARTIAL | Add operator-facing reason codes, severity, evidence and remediation patterns |
| Field Activator | COVERED | Add offline/weak-network states without claiming unsupported offline writes |
| Corporate website | COVERED | Add legal/privacy/trust content requirements and SEO/content governance |
| Analytics / UX telemetry | MISSING | Add event taxonomy and acceptance metrics to design gates |
| Frontend contracts | COVERED | Add screen-to-contract mapping and mock fixture ownership |
| Figma governance | COVERED | Add artifact naming/versioning and design QA checklist |

## Critical findings

### 1. Authentication is a first-class product journey but not yet a design document
The repository already specifies OTP challenges, sessions, devices, tenant context and session revocation. The design folder currently references accessible authentication but does not define the actual UX.

Required screens/states:
- phone entry;
- OTP entry;
- auto-fill/paste support;
- incorrect OTP;
- expired OTP;
- resend countdown;
- rate-limit / blocked challenge;
- session expired;
- revoked session;
- device/session list;
- revoke other sessions;
- logout;
- no active organization;
- organization/context selection.

WCAG 2.2 explicitly covers accessible authentication, redundant entry and target size; these should become component and flow acceptance criteria, not just prose. 

### 2. The canonical profile UX exists outside `13_PRODUCT_DESIGN`
`06_PRODUCT/USER_PROFILE_UX_SPEC.md` is already a canonical MVP UX contract and contains profile/security/notification/work-context behavior. It must be treated as an upstream design dependency, not accidentally duplicated with divergent behavior.

The design system needs a canonical mapping between:
`UserProfile → MembershipProfile → PersonaProfile → Security → Notifications → Active Tenant Context`.

### 3. The commerce design needs a full state matrix
The current retailer document covers the happy path well, but the repository contains materially richer states.

The design system must explicitly map:
- basket created / stale;
- allocation available / partial / unfulfilled;
- revalidation required;
- price changed;
- inventory changed;
- vendor unavailable;
- order submitted;
- accepted;
- partially accepted;
- rejected;
- cancelled;
- preparing;
- ready;
- dispatched;
- delivered;
- dispute open / under review / resolved;
- refund / adjustment states.

### 4. Returns, disputes and evidence are missing from the design workstream
The domain already treats exceptions as a normal operational capability, including damaged goods, item mismatch, delivery delay, doorstep rejection, evidence capture and dispute resolution. This requires actual UX rather than only a generic `issue/return` button.

Minimum flows:
- report issue;
- select issue type;
- affected items/quantities;
- photo/evidence capture;
- submit claim;
- claim timeline;
- operator request for clarification;
- resolution/adjustment/refund status;
- retailer confirmation;
- vendor response.

### 5. Payment UI must remain non-custodial
The design workstream should show payment method/evidence and reconciliation status but must not visually imply a POL wallet, escrow balance or stored customer funds. The canonical model is direct retailer↔vendor settlement with POL observing evidence.

### 6. Notification center is under-specified
The repository has notification delivery, templates, routing and delivery attempts. Design must distinguish:
- inbox notification;
- push;
- SMS;
- mandatory operational/legal notifications;
- user-controlled preferences;
- delivery failure/retry;
- deep-link target.

### 7. Vendor comparison needs an explicit pattern
The PRD describes retailer comparison of vendor offers, while the current retailer UX only mentions vendor context where relevant. A dedicated comparison/offer-selection pattern is needed for:
- vendor identity;
- price;
- pack/case size;
- MOQ;
- availability confidence;
- relevant commercial constraints;
- allocation impact.

### 8. Onboarding documentation contains claims that need design/content governance
The existing onboarding playbook includes wording such as finding the “cheapest” vendor and specific delivery/vehicle behavior. These are operational/content claims and should not become hard-coded UI promises unless they are supported by the canonical runtime data and approved business decisions.

### 9. Field Activator offline behavior needs a visual contract
The current UX document correctly avoids promising unsupported offline writes. Nevertheless, the design system must define:
- offline indicator;
- unsent action state;
- retry;
- duplicate-prevention feedback;
- last-synced timestamp/context;
- conflict resolution if server state changes.

### 10. There is no dedicated Driver product in the planned product surface set
The canonical logistics model uses vendor/3PL/van delivery, but the current product-design sequence has no Driver surface. This is not necessarily a defect: a dedicated driver application may intentionally remain out of MVP. It must, however, be explicitly recorded as either:
- external/phone-based logistics workflow; or
- future POL Driver surface.

Otherwise delivery/POD UI requirements will remain ambiguous.

## Additional design inputs that must be added before high-fidelity work

### Content and localization
- Persian-first terminology glossary;
- Arabic/Persian digit policy;
- phone-number formatting;
- Toman formatting;
- Jalali/Gregorian date display policy;
- mixed RTL/LTR rules for SKU, barcode, URLs, IDs and numbers;
- pluralization and long-label stress cases.

### Trust and safety
- permission denied;
- suspended account;
- vendor blocked;
- unavailable product;
- suspected abuse/risk state;
- sensitive data masking;
- audit-sensitive actions requiring confirmation.

### Commercial visibility
- price effective time;
- price changed since basket;
- vendor-specific pricing;
- MOQ/MOV explanation;
- quantity increment/case pack;
- stock freshness indicator;
- unavailable/unknown inventory states.

### Analytics / measurement
Each critical journey needs an acceptance metric and event taxonomy:
- onboarding start/completion;
- first assisted order;
- first independent order;
- search success;
- add-to-basket;
- allocation acceptance;
- checkout success/failure;
- vendor acceptance/rejection;
- repeat order;
- exception creation/resolution;
- support contact;
- referral redemption;
- abandonment point.

## Conflicts / reconciliation items

### Frontend framework
`06_PRODUCT/PRD.md` currently describes Android as React Native / Expo while `13_PRODUCT_DESIGN/14_DESIGN_DECISION_REGISTER.md` leaves frontend framework choice open. This should be reconciled before implementation, but it does not block visual design.

### API contract terminology
`06_PRODUCT/API_Contracts.md` uses `/profile` contracts and some examples differ in method naming (`PUT` vs the newer design-program wording of `PATCH`). The design workstream should remain transport-agnostic and use action semantics, while the canonical API contract is resolved before frontend integration.

### Persona profile naming
Identity documentation contains conceptual persona table names such as `wholesaler_profiles` / `staff_profiles`, while newer membership-persona migrations use role-specific membership profile tables. Design must use the canonical conceptual term `PersonaProfile` and avoid hard-coding implementation table names into UI documents.

### Commission UI
`05_BUSINESS_MODEL/Commission_Model.md` contains category-specific post-pilot rates, while D-007 remains a 1–3% hypothesis. Design should not expose a “final commission matrix” as established policy. At most, Ops/Admin may need a clearly labelled configuration/experiment surface later.

## Phase gates before Figma high-fidelity

1. Resolve the four reconciliation items above.
2. Add authentication/session UX.
3. Add full commerce/order/dispute/payment/notification state matrix.
4. Add support and RMA flows.
5. Add analytics acceptance events.
6. Add content/localization contract.
7. Decide whether Driver is explicitly out-of-scope for MVP.
8. Only then lock visual tokens and high-fidelity screens.

## Status
**AUDIT COMPLETE — DESIGN WORKSTREAM NEEDS INPUT COMPLETION BEFORE HIGH-FIDELITY Figma.**
