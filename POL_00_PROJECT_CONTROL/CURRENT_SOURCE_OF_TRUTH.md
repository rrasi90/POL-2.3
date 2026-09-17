# POL CURRENT SOURCE OF TRUTH & REPOSITORY GOVERNANCE

**Document ID:** `POL-GOV-001`  
**Version:** 1.1 (Canonical)  
**Status:** `LOCKED / OFFICIAL GOVERNANCE CHARTER`  
**Effective Milestone:** Sprint 0 & MVP v1.0  
**Last Audit:** 2026-09-16  

---

## 1. Hierarchy of Authority

To eliminate architectural drift, cross-document contradictions, and unauthorized scope alterations, all development, modeling, design and operational protocols must trace their constraints to the authoritative documents defined in this charter.

```
DECISION AUTHORITY
  DECISION_REGISTER.md
        │
        ├── PRODUCT SPECIFICATION
        ├── TECHNICAL / DATA MODEL
        ├── OPERATIONS
        └── PRODUCT DESIGN
                 │
                 ▼
        Figma / Penpot / Frontend
```

`DECISION_REGISTER.md` is the highest repository-level product authority. Design artifacts may refine presentation and interaction but may not change business rules, authorization rules, financial custody rules, or MVP scope.

---

## 2. Canonical Authorities by Domain

| Domain | Authoritative Canonical File(s) | Scope & Responsibility | Precedence Rule |
|:---|:---|:---|:---|
| **Strategic & Architectural Decisions** | `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` | Sole authority for Founder Decisions D-001 through D-017. | Absolute precedence. |
| **Current MVP Scope & Requirements** | `06_PRODUCT/MVP_Definition.md`, `06_PRODUCT/PRD.md` | Feature matrix, core flows, boundaries and MVP inclusions/exclusions. | Must conform to D-001–D-017. |
| **Identity & Access Management** | `06_PRODUCT/Roles_and_Permissions.md`, `POL_00_PROJECT_CONTROL/USER_PROFILE_AND_PERSONA_MODEL.md` | Identity, tenant membership, authorization, persona context and UX preferences. | `organization_memberships.role` is authorization SSoT; `users.role` is legacy/deprecated. |
| **Order Lifecycle & State Transitions** | `06_PRODUCT/Order_Lifecycle.md`, `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` | OrderGroup, child Orders, Delivery and exception state machines. | Governs backend workflows and UI state mapping. |
| **Domain Entities & Business Invariants** | `08_DATA/DOMAIN_MODEL.md` | Ubiquitous language, aggregates and invariants. | Governs domain service behavior. |
| **Database Schema & Migrations** | `migrations/001_*.sql` through `migrations/022_*.sql`, `08_DATA/Data_Schema.md`, `POL_00_PROJECT_CONTROL/DATABASE_SCHEMA_MANIFEST_2026-09-16.md` | PostgreSQL 18 DDL, constraints, indexes, triggers and foreign keys. | The numbered migration chain is the physical schema authority. |
| **API Contracts & DTOs** | `06_PRODUCT/API_Contracts.md`, `POL_00_PROJECT_CONTROL/CANONICAL_CONTRACT_MATRIX.md`, `POL_00_PROJECT_CONTROL/CANONICAL_CONTRACT_MATRIX_CORRECTIONS_2026-09-16.md`, `POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md` | REST/JSON contracts and application-boundary commands. | Correction overlay supersedes conflicting legacy terminology. |
| **Allocation Engine Algorithm** | `07_ALGORITHMS/MVP_MULTI_VENDOR_ALLOCATION.md` | Deterministic multi-vendor allocation, MOV/MOQ and ranking. | Governs allocation implementation. |
| **Brand & Design System** | `POL_00_PROJECT_CONTROL/BRAND_ARCHITECTURE.md`, `13_PRODUCT_DESIGN/` | Brand hierarchy, design system, interaction patterns and visual language. | Design may not override product/engineering decisions. |
| **Operations, Fulfillment & Logistics** | `09_OPERATIONS/Fulfillment.md`, `09_OPERATIONS/Payments_and_Settlement.md`, `09_OPERATIONS/Support_and_Disputes.md` | Field SOPs, logistics, direct settlement and support/dispute operations. | Governs operational workflows. |
| **Pilot Definition & Metrics** | `11_PILOT/Pilot_Strategy.md`, `11_PILOT/KPIs.md`, `11_PILOT/Success_Criteria.md` | Ahvaz pilot parameters and Gate 1 telemetry. | Governs pilot validation. |
| **Readiness & Certification** | `POL_00_PROJECT_CONTROL/GLOBAL_ENGINEERING_AUDIT_2026-09-14.md`, `POL_00_PROJECT_CONTROL/REPOSITORY_COMPLETION_AUDIT_2026-09-16.md`, `POL_00_PROJECT_CONTROL/CERTIFICATION_ADDENDUM_2026-09-14.md` | Explicit separation of verified domain core vs remaining production-applicationization gates. | No document may claim production readiness beyond these boundaries. |

---

## 3. Active Document Rule

All active documents MUST represent the current architecture:

- Current MVP basket model is **Multi-Vendor (`D-014`)**.
- Single-Vendor MVP is historical only (`D-003`).
- Vendor count is open; no hardcoded `<=2` rule.
- MVP payment remains `NON_CUSTODIAL_DIRECT`.
- Vendor Referral is active MVP (`D-016`) without rewards/wallet/credit incentives.
- Universal User Profile + Membership Persona Context is active MVP (`D-017`).
- PostgreSQL 18 is the sole canonical runtime database.

Active documents MUST NOT silently reintroduce superseded rules through examples, API terminology, UI copy, or test fixtures.

Canonical order entity hierarchy (documented in `08_DATA/DOMAIN_MODEL.md` and `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md`):

```
Basket -> AllocationPlan -> OrderGroup -> Order -> OrderItem
```

The `Basket` holds retailer demand, the `AllocationPlan` splits it across eligible vendors (D-014), each `OrderGroup` is the parent transaction, each child `Order` is a single-vendor contract, and each `OrderItem` is the atomic unit for delivery, settlement and disputes.

---

## 4. Historical Documents Governance Policy

Historical exploratory, hardening and certification documents are preserved for traceability. If they describe superseded architecture, they must carry an explicit `HISTORICAL / SUPERSEDED` banner and point to `DECISION_REGISTER.md`.

Historical documents are evidence of project evolution, not active requirements.

---

## 5. Design Governance

`13_PRODUCT_DESIGN/` is the written design source of truth. The execution order is:

`Repository Sync → Repository Audit → Specification Completion → Design Foundation → Components → Shared UX → States → Product Surfaces → Prototype → Design QA → Frontend Handoff`.

No visual artifact becomes canonical until the corresponding written requirement and decision are recorded.

---

## 6. Change Management

1. No competing decision registers or shadow PRDs.
2. Changes to D-001–D-017 require explicit superseding decisions.
3. Code, migrations, tests and design artifacts must be traceable to current canonical documents.
4. Generated local artifacts must not be committed to the repository.
5. Production-readiness claims must distinguish domain verification from HTTP/auth/provider/UI/observability/deployment/recovery implementation.
