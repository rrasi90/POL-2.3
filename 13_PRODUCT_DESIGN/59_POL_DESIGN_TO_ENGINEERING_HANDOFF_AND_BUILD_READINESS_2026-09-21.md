# POL — Design → Engineering Handoff & Build Readiness Contract

**Document ID:** `POL-DESIGN-HANDOFF-001`  
**Version:** `1.0.0`  
**Date:** 2026-09-21  
**Status:** ACTIVE / ENGINEERING HANDOFF AUTHORITY  
**Repository:** `rrasi90/POL-2.3`  
**Branch:** `product-architecture-evolution-2026-09-20`  
**Master Tree:** v4.2 target  
**Build Mode:** `GREENFIELD_EMPTY_FILE`

---

# 0. Purpose

The purpose of this contract is to prevent a common failure:

> a visually approved Penpot screen is mistaken for an implementation-ready software specification.

POL is a real B2B platform. After Penpot approval, Web and Android applications must be built against the approved design without reopening product semantics through interpretation.

Therefore:

`DESIGN_APPROVED 
eq ENGINEERING_READY`

Engineering readiness is a separate gate.

---

# 1. Required implementation chain

Every implementation-ready screen must resolve:

`Capability → Experience → Screen → Section → Component → Variant → Action → Permission → UI State → Domain State → Data → API → Error Contract → Notification/Audit → Analytics → Navigation → Responsive → Theme → Frontend Artifact → Test → Evidence`

A missing mandatory link means the screen is not Engineering Ready.

---

# 2. Two different approvals

## Gate A — Design Approval

Meaning:

- information hierarchy is approved;
- visual direction is approved;
- interaction intent is approved;
- Light/Night is approved;
- responsive composition is approved;
- RTL/accessibility treatment is approved.

This does NOT certify backend/API readiness.

## Gate B — Engineering Readiness

Meaning:

- every actionable element has an implementation contract;
- API/command/query mapping is explicit;
- permission is explicit;
- state transition is explicit;
- loading/error/empty/recovery behavior is explicit;
- analytics is explicit where required;
- navigation/deep-link behavior is explicit;
- frontend component mapping is explicit;
- Web/Android platform behavior is explicit;
- test requirements are explicit.

Only Gate B allows implementation to start without product clarification.

---

# 3. Screen Engineering Handoff Record

Every canonical Screen MUST have the following handoff record:

### Identity

- Screen ID
- canonical name
- surface
- persona
- actor
- organization scope
- active membership context
- lifecycle
- priority
- maturity

### User outcome

- user job
- expected result
- success condition
- abandonment/recovery condition

### Layout

- breakpoint class
- responsive rules
- density profile
- page shell
- section order
- sticky/fixed behavior
- scroll behavior

### Visual

- Precision Commerce direction
- Light tokens
- Night tokens
- component tokens
- typography roles
- imagery/assets
- icon references
- motion references

### Components

For each component:

- canonical component ID
- variant
- state
- content contract
- interaction contract
- responsive behavior
- accessibility behavior

### Actions

For each actionable element:

- Action ID
- command/query
- permission
- preconditions
- validation
- idempotency
- concurrency behavior
- expected UI state transition
- domain transition
- postcondition
- audit event
- notification effects
- navigation effects
- error mapping
- recovery path

### Data

- read model/source
- writable model/source
- fields
- formatting
- freshness
- PII sensitivity
- tenancy scope
- snapshot semantics

### API

- endpoint or ApplicationBoundary command/query
- method
- request schema
- response schema
- error envelope
- auth context
- route status
- pagination/filter/sort where relevant
- retry behavior

### Analytics

- event ID
- trigger
- properties
- correlation ID
- KPI/hypothesis linkage
- privacy constraints

### Platform

Web:

- route
- URL/deep-link
- browser state
- desktop behavior
- keyboard/focus

Android:

- screen/navigation mapping
- back behavior
- system permission where applicable
- offline/read-only semantics
- Android-specific interaction

### QA

- unit/component test expectations
- integration tests
- E2E scenario
- accessibility test
- RTL test
- responsive test
- theme test
- network degradation test where applicable

---

# 4. Component → Code contract

A Penpot component is not implementation-ready merely because it is reusable.

Every canonical component should have:

`Penpot Component → Component Contract → Frontend Component → Test Fixture`

The implementation contract should record:

- component ID;
- source-of-truth token refs;
- variant properties;
- allowed values;
- state matrix;
- slots/content model;
- responsive rules;
- accessibility semantics;
- event callbacks;
- data shape if data-bound;
- platform differences.

Penpot Variants should map intentionally to code properties/state rather than producing one unrelated frontend component per visual frame. Penpot documents variants as grouped components distinguished by properties/values, which aligns well with this mapping. citeturn710023search2

---

# 5. Token → Code contract

The visual chain must be:

`Primitive → Semantic → Component → Pattern`

Code must consume semantic/component tokens rather than screen-specific hardcoded values.

Penpot's current token system is explicitly intended to act as a shared language between design, tools and code, and supports token themes and multidimensional theme combinations. citeturn710023search1

POL therefore requires:

- Light semantic tokens;
- Night semantic tokens;
- shared component tokens;
- code token mapping;
- token export/synchronization evidence.

A visual change to a semantic token should be capable of propagating to dependent components without redesigning every screen.

---

# 6. Design → frontend artifact mapping

For each Screen:

`SCR-ID → frontend route → page/view component → child components → state store/query → API client methods → tests`

For each reusable Component:

`CMP-ID → frontend component → variant props → tests`

For each Pattern:

`PATTERN-ID → compositional component/module → consuming screens`

The mapping must be explicit.

A screen may not be marked Engineering Ready if it has no planned frontend artifact mapping.

---

# 7. Design → API rule

A Penpot button must never imply an API exists merely because the button is visually present.

For every action:

- `HTTP_IMPLEMENTED` — live HTTP route may be consumed;
- `BOUNDARY_READY` — implementation may depend on the application boundary but transport work remains;
- `CONTRACT_ONLY` — UI may be designed, but production integration is blocked until API applicationization;
- `DOMAIN_VERIFIED_ONLY` — no frontend integration claim may be made.

The status must remain visible to engineering.

Current repository inventory records **50 business endpoint specifications and 21 implemented business HTTP routes**, plus operational health/readiness routes. Therefore Penpot approval cannot be used as evidence that every designed interaction is already backed by production HTTP. citeturn710023search0

---

# 8. Design → State rule

For every meaningful mutation, engineering must know:

`IDLE → SUBMITTING → PENDING → COMPLETED / FAILED / CANCELLED / EXPIRED / STALE`

where applicable.

For domain-sensitive actions the handoff also records the canonical domain transition.

Examples:

### Vendor acceptance

`SUBMITTED → ACCEPTED`

### Vendor rejection

`SUBMITTED → REJECTED`

### Partial acceptance

proposal:

`NONE → PENDING`

approval:

`SUBMITTED → PARTIALLY_ACCEPTED`

decline:

proposal closes without order mutation.

### Vendor timeout

`SUBMITTED → CANCELLED`

The screen design must not invent alternate domain transitions.

---

# 9. Error and recovery contract

Engineering must receive explicit UX behavior for:

- 400/validation;
- 401/expired session;
- 403/permission;
- 404/missing resource;
- 409/stale state/concurrency;
- 422/business validation;
- 429/rate limit;
- 5xx/service failure;
- network unavailable;
- timeout;
- partial response;
- already-completed action.

For each error:

- UI message;
- action/recovery;
- whether retry is safe;
- whether data must refresh;
- whether navigation changes;
- whether the failure is auditable.

---

# 10. Network / offline contract

POL's visual design must never imply stronger offline guarantees than the canonical runtime.

Each network-dependent screen must declare:

- ONLINE_REQUIRED
- ONLINE_WITH_RETRY
- READ_ONLY_CACHE_ALLOWED
- QUEUED_WRITE_SUPPORTED
- NOT_APPLICABLE

Only the explicitly supported state may be designed.

---

# 11. Analytics handoff

Every critical capability must connect:

`Interaction → Analytics Event → KPI/Hypothesis`

At minimum, engineering should know:

- event name;
- trigger;
- actor;
- organization context;
- screen;
- object ID;
- correlation ID;
- properties;
- privacy classification.

A screen cannot be declared analytically complete because a generic “screen viewed” event exists.

---

# 12. Accessibility / RTL handoff

Approved design must provide implementation-facing semantics for:

- heading hierarchy;
- landmarks;
- labels;
- accessible names;
- keyboard order on Web;
- focus management;
- announcement/live region needs;
- touch targets;
- reduced motion;
- contrast;
- color-independent state communication;
- RTL;
- bidi handling.

Penpot Dev Tools currently provides inspect-mode measurements/properties and production-oriented code inspection, which can support the handoff but does not replace the behavioral contract above. citeturn710023search0

---

# 13. Asset handoff

Every production asset requires:

- asset ID;
- source/provenance;
- licensing/usage status where relevant;
- canonical crop;
- export density;
- format;
- optimization rule;
- placeholder/fallback;
- loading/error behavior.

Product media must continue to obey the canonical Product Media / provenance model.

---

# 14. Design approval checklist

A Screen may receive:

### DESIGN_APPROVED

only when:

- canonical node exists;
- Precision Commerce tokens are used;
- Light/Night are verified;
- component variants are real;
- responsive behavior exists;
- RTL is verified;
- accessibility semantics are resolved;
- critical state coverage exists;
- visual evidence exists;
- structural persistence exists.

### ENGINEERING_READY

only when all of the above PLUS:

- all actions are mapped;
- permissions are mapped;
- domain transitions are mapped;
- API/boundary status is explicit;
- request/response/error contracts exist;
- frontend mapping exists;
- platform mapping exists;
- analytics mapping exists;
- test plan exists;
- network contract exists.

---

# 15. Engineering handoff package

The release handed to engineering must contain:

1. approved Penpot file/revision;
2. Master Tree release snapshot;
3. screen registry;
4. component registry;
5. token registry;
6. state registry;
7. permission mapping;
8. API mapping;
9. analytics mapping;
10. asset manifest;
11. responsive/platform matrix;
12. accessibility/RTL matrix;
13. known limitations;
14. open blockers;
15. design waivers;
16. exact frontend artifact targets.

Penpot's Inspect mode is designed to let developers inspect measurements, properties, assets and production-oriented code from the approved design. It should be used as a supplemental extraction layer, while the Master Tree remains the semantic contract. citeturn710023search0

---

# 16. Engineering readiness states

Canonical states:

`DESIGN_DEFINED`

`PENPOT_BUILT`

`DESIGN_REVIEWED`

`DESIGN_APPROVED`

`ENGINEERING_MAPPED`

`ENGINEERING_READY`

`IMPLEMENTATION_IN_PROGRESS`

`IMPLEMENTED`

`RUNTIME_VERIFIED`

`PILOT_VERIFIED`

Do not collapse them into one “complete” flag.

---

# 17. Hard blockers after Design Approval

Engineering MUST be blocked from starting the affected implementation when:

- approved screen has no API/command mapping;
- protected action has no permission;
- state transition is ambiguous;
- required data source is undefined;
- error/recovery path is missing for a critical action;
- component has no code mapping;
- token has no code mapping;
- mobile/desktop behavior is undefined where required;
- RTL/accessibility semantics are unresolved;
- route is contract-only but the screen is presented as production-integrated;
- required runtime capability is not implemented;
- design claims exceed canonical product/runtime truth.

---

# 18. Design-to-code parity

After implementation:

`Approved Design → Implemented UI → Runtime Screenshot/State → Comparison Evidence`

The verification must include:

- layout;
- typography;
- color/token usage;
- component variants;
- interaction states;
- content hierarchy;
- responsive behavior;
- RTL;
- Night;
- accessibility.

A screenshot matching the design does not prove business behavior.

A passing integration test does not prove visual fidelity.

Both dimensions are required.

---

# 19. Final engineering exit condition

The design system is not considered fully successful merely because Penpot is approved.

The real success chain is:

`CANONICAL PRODUCT TRUTH`
→ `MASTER TREE`
→ `PENPOT`
→ `ENGINEERING HANDOFF`
→ `WEB + ANDROID IMPLEMENTATION`
→ `RUNTIME VERIFICATION`
→ `PILOT OBSERVATION`

The Master Tree is closed for a feature only when the appropriate downstream evidence exists.

