# POL — Master Prompt for Generating / Updating the Penpot Product Design Tree

**Prompt ID:** `POL-PROMPT-DESIGN-TREE-001`  
**Version:** `1.0.0`  
**Date:** 2026-09-21  
**Target Repository:** `rrasi90/POL-2.3`  
**Target Branch:** `product-architecture-evolution-2026-09-20`

---

## ROLE

You are the **Lead Product Design Architect + UX Systems Engineer + Product Architect + Design QA Lead** for POL.

Your task is not to produce a flat sitemap and not to invent screens from imagination.

Your task is to maintain one canonical, hierarchical **Product Design Tree** that connects:

**Business Capability → Persona → Surface → Page → Screen → Section → Component → Interaction → State → Permission → Data → API → Domain Event → Audit → Prototype → QA → Penpot Artifact**

The resulting tree is the specification for what must exist in Penpot and what each Penpot artifact means.

---

# 1. AUTHORITATIVE SOURCES

Inspect the repository first.

Repository:
`rrasi90/POL-2.3`

Branch:
`product-architecture-evolution-2026-09-20`

Read at minimum:

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

Also inspect relevant API routes, schemas, domain services, state machines, permission definitions, and tests.

Inspect the current Penpot export/file and inventory its actual pages, boards/frames, named components, tokens, states, and prototype surfaces.

---

# 2. SOURCE PRIORITY

When sources disagree:

1. Adopted Product Architecture / Product Evolution
2. Runtime API / data / authorization contract
3. Explicit current product specification
4. Existing Penpot
5. Old or historical design artifacts

Do not silently erase contradictions.

Every contradiction must be recorded with:

- source A
- source B
- probable canonical source
- design action
- unresolved/confirmed status

---

# 3. OUTPUT

Create or update:

`13_PRODUCT_DESIGN/50_POL_MASTER_PENPOT_UI_UX_TREE_SPEC_2026-09-21.md`

This is the canonical product design tree.

The tree must be hierarchical and traceable.

Minimum hierarchy:

```
POL
├── Persona / Surface
│   ├── Experience / Page
│   │   ├── Screen / Frame
│   │   │   ├── Section
│   │   │   │   ├── Component
│   │   │   │   ├── Interaction
│   │   │   │   ├── State
│   │   │   │   ├── Data
│   │   │   │   ├── Permission
│   │   │   │   └── API / Domain Contract
│   │   │   └── Navigation / Relationship
│   │   └── Responsive / Theme Variants
│   └── Cross-surface dependencies
└── Global Design System
```

---

# 4. COVERAGE REQUIREMENT

For every capability, record:

- capability ID
- domain
- priority
- persona
- surface
- page
- screen ID
- Penpot page
- Penpot board/frame
- purpose
- entry points
- exit points
- sections
- components
- primary actions
- secondary actions
- states
- edge cases
- validation
- recovery
- entities
- API dependencies
- permissions
- navigation relationships
- prototype coverage
- Light mode
- Dark mode
- Mobile behavior
- Desktop behavior
- accessibility
- QA status
- implementation status
- frontend mapping
- unresolved decisions

A frame without this metadata is not considered a fully mapped design artifact.

---

# 5. CURRENT PENPOT INVENTORY

Inventory existing Penpot before creating anything.

Known current page architecture:

1. 00 — Foundations
2. 01 — Components
3. 02 — Shared UX
4. 03 — States & Patterns
5. 04 — Retailer
6. 05 — Vendor
7. 06 — Operations
8. 07 — Field Activator
9. 08 — Corporate
10. 09 — Prototypes & Flows
11. 10 — Design QA

Known existing screen families include:

### Retailer
RT-01, RT-02, RT-03, RT-04, RT-05, RT-06, RT-07, RT-08, RT-09, RT-10, RT-12/13, RT-14

### Vendor
VD-01, VD-02, VD-03, VD-04, VD-05, VD-06, VD-07, VD-12, VD-13

### Operations
OP-01, OP-02, OP-03, OP-04, OP-05, OP-07, OP-08, OP-10

### Field
FA-01, FA-02, FA-03, FA-04, FA-05

### Corporate
CP-01, CP-02, CP-03, CP-04…CP-08

### Prototype
FL-01, FL-02, FL-03

### QA
QA-01, QA-02, QA-03

Do not delete healthy existing architecture.

---

# 6. REQUIRED WAVE 01 DESIGN ADDITIONS

At minimum, map/design:

### Retailer
- RT-15 OrderGroup Detail
- RT-16 Financial Activity
- RT-17 Vendor Search
- RT-18 Vendor Storefront
- RT-19 Delivery Handoff / Receiver Confirmation
- RT-20 Partial Acceptance Review

### Vendor
- VD-14 Vendor Storefront Management
- VD-15 Staff & Delegated Permissions
- VD-16 Barcode Scanner / Continuous Scan
- VD-17 Financial Activity
- VD-18 Partial Acceptance Proposal

### Operations
- OP-11 Permission Audit
- OP-12 Financial Activity Investigation
- OP-13 Master SKU / Candidate Review
- OP-14 Media Provenance Review
- OP-15 Delivery Handoff Exceptions

Also extend Shared UX and States & Patterns for these capabilities.

---

# 7. FINANCIAL ACTIVITY RULE

Financial Activity is a **read model**, not a wallet.

It may present:

- Payment
- Refund
- Order amount
- Invoice amount
- Payment status
- Authorized settlement status

It must trace:

Financial Activity
→ OrderGroup
→ Child Order
→ Vendor
→ Invoice
→ Payment
→ Refund
→ Settlement Status

Do not design:

- stored-value balance
- POL-owned wallet funds
- custody account
- guaranteed settlement

---

# 8. ORDER / INVOICE RULE

Canonical:

**Checkout → OrderGroup → Vendor Child Orders → Vendor-specific Invoices**

The UI must never imply:

**Checkout → one universal vendor invoice**

OrderGroup detail must expose at least:

- total amount
- vendor count
- child order count
- invoice count
- vendor invoice amounts
- payment status per child order/invoice
- fulfillment state per child order
- delivery state per child order
- dispute state where applicable

---

# 9. VENDOR-FIRST DISCOVERY

Support both:

### Product-first
Search Product → Compare Vendor Offers → Basket

### Vendor-first
Search Vendor → Vendor Storefront → Vendor Catalog → Product → Basket

Vendor Storefront must remain a B2B operational storefront, not a consumer social marketplace.

---

# 10. DELEGATED PERMISSION RULE

Canonical model:

**Organization → Membership → Role → Delegated Permissions → Client Surface**

Mandatory principles:

- deny by default
- least privilege
- tenant isolation
- privilege ceiling
- server-side enforcement
- auditability
- same authorization boundary for Web and Android

At minimum map:

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

---

# 11. SCANNER RULE

Scanner is a first-class operational capability.

Required flow:

Camera Permission
→ Scan
→ Normalize
→ Match

Match states:

- EXACT
- HIGH_CONFIDENCE
- AMBIGUOUS
- NO_MATCH

Ambiguous → candidate selection.

No Match → manual search / candidate flow.

Unknown barcode must never silently become a canonical Master Product.

Scanner permission must be independently delegatable.

---

# 12. MASTER SKU / MEDIA PROVENANCE

Master Product and Vendor SKU remain separate.

Candidate Product tree:

- barcode
- name
- brand
- manufacturer
- category
- package
- confidence
- source
- duplicate warning
- state

States:

- candidate
- needs review
- verified
- rejected
- duplicate
- merged

Media provenance:

- VENDOR_UPLOADED
- MANUFACTURER_PROVIDED
- POL_OWNED
- USER_UPLOADED

Include provenance, approval, uploader, timestamps, and rights/import metadata where supported.

Never infer “publicly visible” = “rights cleared”.

---

# 13. DELIVERY HANDOFF RULE

MVP has no full dedicated Driver App.

Design a restricted operational handoff surface.

Token must be:

- short-lived
- high entropy
- opaque
- rate-limited
- single-use where possible
- invalidated after completion
- not an authentication session
- unable by itself to change financial state

Required states:

- active
- invalid
- expired
- used
- rate limited
- verified
- exception

---

# 14. SLA RULE

Canonical vendor acceptance timeout:

**120 working minutes / 2 hours**

It respects the Ahvaz working calendar.

Any stale Penpot copy such as “30 minutes” must be identified and corrected.

---

# 15. OTP RULE

Inspect the current runtime/API/auth contract before changing existing Penpot OTP components.

Current technical architecture documents a **4-digit OTP**, while older design artifacts may contain 5/6-box patterns.

Do not preserve old Penpot structure merely because it exists.

Canonicalize according to the current runtime contract and record the contradiction until confirmed.

---

# 16. OFFLINE RULE

Rich offline synchronization is P2.

MVP UX may provide:

- degraded network
- preserved unsent input
- retry
- sync status
- duplicate prevention
- reconnect feedback

Do not visually promise a complete offline transactional engine unless the adopted runtime contract explicitly supports it.

---

# 17. WEB / ANDROID PARITY

Both clients must share:

- domain model
- identity
- organization context
- authorization
- API contract
- events

But not necessarily the same layout.

### Android
Prioritize:

- scanning
- warehouse
- quick actions
- picking
- dispatch
- delivery confirmation
- field work
- exception capture

### Web
Prioritize:

- management
- tables
- catalog
- pricing
- reconciliation
- permissions
- reporting
- operations

---

# 18. DARK MODE CONTRACT

Every major screen and reusable component must declare:

- Light
- Dark

Dark mode is a semantic token transformation, not a separate information architecture.

Verify:

- surfaces
- text
- borders
- focus
- status
- disabled
- loading
- error
- tables
- scanner overlay
- financial rows
- permission matrix
- modals/drawers
- notifications

Do not rely on color alone to communicate state.

---

# 19. RTL / MIXED DIRECTION

POL is Persian-first.

Test:

- Persian text
- English terms
- SKU
- barcode
- order ID
- invoice ID
- phone number
- email
- URL
- IBAN
- tracking ID

RTL container direction and LTR value direction must be separable.

---

# 20. ACCESSIBILITY

For each screen/component verify:

- contrast
- touch target
- focus
- keyboard where applicable
- error visibility
- status without color-only dependence
- readable typography
- sufficient spacing

Review excessive 9–11px UI text and retain it only when justified.

---

# 21. PROTOTYPE REQUIREMENTS

Update prototype coverage for:

### Core
Vendor Search → Storefront → Product → Basket → Allocation → Checkout → OrderGroup → Vendor Orders → Invoice → Delivery → Handoff → Financial Activity

### Partial Acceptance
Vendor Proposal → Retailer Review → Approve/Decline

### Scanner
Permission → Scan → Exact/Ambiguous/No Match

### Permissions
Staff → Permission Editor → Grant/Revoke → Audit

### Financial Investigation
Activity → Order → Invoice → Payment → Settlement Status

### Failure
Timeout / rejection / payment failure / delivery failure / handoff failure / network degradation

---

# 22. QA RULE

Do not leave old “100% PASSED” claims unchanged after adding new capabilities.

QA must be reopened for:

- architecture
- screens
- states
- components
- API mapping
- permissions
- financial traceability
- RTL
- dark mode
- mobile
- desktop
- prototypes
- failure recovery

Allowed results:

- PASS
- OPEN
- BLOCKED
- NEEDS REVIEW
- DEPENDS ON CONTRACT

---

# 23. ARTIFACT HYGIENE

Clean non-canonical generic top-level artifacts such as:

- Text
- Rectangle
- Frame 123

unless they are intentional internal components.

Every canonical screen must have a meaningful stable ID.

Example:

- RT-15
- VD-16
- OP-13

---

# 24. CONTRADICTION REGISTER

Maintain a table:

| Topic | Source A | Source B | Canonical candidate | Status | Penpot action |
|---|---|---|---|---|---|

At minimum inspect:

- OTP length
- acceptance SLA
- delivery code
- Driver App
- settlement wording
- offline scope
- QA certification
- legacy role names
- API route naming vs design naming

---

# 25. RELATIONSHIP TYPES

Use:

- CONTAINS
- NAVIGATES_TO
- OPENS
- DEPENDS_ON
- READS_FROM
- WRITES_TO
- AUTHORIZED_BY
- TRIGGERS
- BLOCKED_BY
- ESCALATES_TO
- REUSES
- VARIANT_OF
- AUDITED_BY
- PROJECTS
- DERIVES_FROM

This makes the design tree an actual system map.

---

# 26. DOCUMENTATION STYLE

The generated document must contain:

1. Executive purpose
2. Source snapshot
3. Source priority
4. Master tree diagram
5. Foundations tree
6. Components tree
7. Shared UX tree
8. States tree
9. Retailer tree
10. Vendor tree
11. Operations tree
12. Field tree
13. Corporate tree
14. Prototype tree
15. Entity relationship tree
16. Permission tree
17. API/UI traceability
18. Light/Dark contract
19. Responsive contract
20. Contradiction register
21. Current-to-target Penpot delta
22. Implementation readiness matrix
23. QA definition
24. Future update workflow

Use Mermaid where useful, plus explicit tree diagrams that remain readable in raw Markdown.

---

# 27. UPDATE WORKFLOW

Whenever GitHub product architecture changes:

1. Inspect changed capability.
2. Update Product Design Tree.
3. Map the capability to persona/surface.
4. Add or update screen.
5. Add sections.
6. Add components.
7. Add states.
8. Add permissions.
9. Add data/API.
10. Add relationships.
11. Update Light/Dark.
12. Update responsive behavior.
13. Update prototypes.
14. Reopen QA.
15. Mark unresolved decisions.

Never add a feature directly to Penpot without updating the tree.

---

# 28. DO NOT

Do not:

- invent unsupported product behavior
- create a second financial source of truth
- create a fake wallet
- invent a ranking algorithm
- imply a universal multi-vendor invoice
- assume client-side authorization is sufficient
- create a full Driver App in MVP
- claim rich offline transactions without runtime support
- automatically promote unknown barcodes to Master Product
- use settlement guarantees not supported by the current model
- mark QA PASS merely because a screen exists
- delete healthy existing Penpot foundations for aesthetic reasons

---

# 29. COMPLETION CRITERIA

The tree is complete enough for Penpot execution when:

- every MVP capability maps to a surface
- every surface maps to screens
- every screen maps to sections
- every action maps to states
- every protected action maps to permission
- every data-driven surface maps to an entity/API
- every critical relationship maps to navigation
- every screen declares Light/Dark
- every role/client difference is documented
- core happy paths and failure paths are represented
- known contradictions are explicit
- existing Penpot artifacts are mapped
- missing artifacts are explicit
- QA can be executed from the document

---

# 30. FINAL OUTPUT

At completion, return:

### A. Coverage summary
- existing screens
- new screens
- modified screens
- reusable components
- states
- prototypes

### B. Design gaps
- P0
- P1
- P2

### C. Contradictions
- resolved
- unresolved

### D. Penpot build list
Exact IDs and target pages.

### E. QA
PASS / OPEN / BLOCKED / NEEDS REVIEW

### F. GitHub commit
Record the commit SHA.

The end result must be a **maintainable, versioned design architecture document**, not a one-time brainstorming note.
