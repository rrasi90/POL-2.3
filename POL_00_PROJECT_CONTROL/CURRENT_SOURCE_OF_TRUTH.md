# POL CURRENT SOURCE OF TRUTH & REPOSITORY GOVERNANCE

**Document ID:** `POL-GOV-001`  
**Version:** 1.1 (Canonical)  
**Status:** `LOCKED / OFFICIAL GOVERNANCE CHARTER`  
**Effective Milestone:** Sprint 0 & MVP v1.0  
**Last Audit:** 2026-09-21  

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
| **Strategic & Architectural Decisions** | `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` | Sole authority for Founder Decisions D-001 through D-028; later amendments supersede earlier decisions explicitly. | Absolute precedence. |
| **Current MVP Scope & Requirements** | `06_PRODUCT/MVP_Definition.md`, `06_PRODUCT/PRD.md` | Feature matrix, core flows, boundaries and MVP inclusions/exclusions. | Must conform to D-001–D-020. |
| **Identity & Access Management** | `06_PRODUCT/Roles_and_Permissions.md`, `POL_00_PROJECT_CONTROL/USER_PROFILE_AND_PERSONA_MODEL.md` | Identity, tenant membership, authorization, persona context and UX preferences. | `organization_memberships.role` is authorization SSoT; `users.role` is legacy/deprecated. |
| **Order Lifecycle & State Transitions** | `06_PRODUCT/Order_Lifecycle.md`, `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` | OrderGroup, child Orders, Delivery and exception state machines. | Governs backend workflows and UI state mapping. |
| **Domain Entities & Business Invariants** | `08_DATA/DOMAIN_MODEL.md` | Ubiquitous language, aggregates and invariants. | Governs domain service behavior. |
| **Database Schema & Migrations** | `migrations/001_*.sql` through `migrations/031_*.sql`, `08_DATA/Data_Schema.md`, `POL_00_PROJECT_CONTROL/DATABASE_SCHEMA_MANIFEST_2026-09-16.md` | PostgreSQL 18 DDL, constraints, indexes, triggers and foreign keys. | The numbered migration chain is the physical schema authority. |
| **API Contracts & DTOs** | `06_PRODUCT/API_Contracts.md`, `POL_00_PROJECT_CONTROL/CANONICAL_CONTRACT_MATRIX.md`, `POL_00_PROJECT_CONTROL/CANONICAL_CONTRACT_MATRIX_CORRECTIONS_2026-09-16.md`, `POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md` | REST/JSON contracts and application-boundary commands. | Correction overlay supersedes conflicting legacy terminology. |
| **Allocation Engine Algorithm** | `07_ALGORITHMS/MVP_MULTI_VENDOR_ALLOCATION.md` | Deterministic multi-vendor allocation, MOV/MOQ and ranking. | Governs allocation implementation. |
| **Brand & Design System** | `POL_00_PROJECT_CONTROL/BRAND_ARCHITECTURE.md`, `13_PRODUCT_DESIGN/` | Brand hierarchy, design system, interaction patterns and visual language. | Design may not override product/engineering decisions. |
| **Operations, Fulfillment & Logistics** | `09_OPERATIONS/Fulfillment.md`, `09_OPERATIONS/Payments_and_Settlement.md`, `09_OPERATIONS/Support_and_Disputes.md` | Field SOPs, logistics, direct settlement and support/dispute operations. | Governs operational workflows. |
| **Async Workers & Event Runtime** | `POL_00_PROJECT_CONTROL/WORKER_ARCHITECTURE.md`, `08_DATA/Event_Architecture.md` | Canonical PostgreSQL 18 transactional outbox + Python worker execution model. | Supersedes BullMQ/Redis Streams as the MVP event transport. |
| **Pilot Definition & Metrics** | `11_PILOT/Pilot_Strategy.md`, `11_PILOT/KPIs.md`, `11_PILOT/Success_Criteria.md` | Ahvaz pilot parameters and Gate 1 telemetry. | Governs pilot validation. |
| **Readiness & Certification** | `POL_00_PROJECT_CONTROL/GLOBAL_ENGINEERING_AUDIT_2026-09-14.md`, `POL_00_PROJECT_CONTROL/REPOSITORY_COMPLETION_AUDIT_2026-09-16.md`, `POL_00_PROJECT_CONTROL/CERTIFICATION_ADDENDUM_2026-09-14.md` | Explicit separation of verified domain core vs remaining production-applicationization gates. | No document may claim production readiness beyond these boundaries. |

---

## 3. Active Document Rule

All active documents MUST represent the current architecture:

- Current MVP basket model is **Multi-Vendor (`D-014`)**.

**Repository-truth sync (2026-09-18):** Stage 04 audit-start PR #1 control-document HEAD was `4539c77a557290dc8476b6c29d3a7cfeab36feea`; subsequent control-only commits record the synchronized document changes. Latest completed full verification on the PR lineage is Run #365 (`35378830823`) with 212/212 pass on certified code head `5ac5974b2caf045f8020e3c8b48f889ed3ff94e9`. The PR remains open and unmerged.
- Single-Vendor MVP is historical only (`D-003`).
- Vendor count is open; no hardcoded `<=2` rule.
- MVP payment remains `NON_CUSTODIAL_DIRECT`.
- Vendor Referral is active MVP (`D-016`) without rewards/wallet/credit incentives.
- Universal User Profile + Membership Persona Context is active MVP (`D-017`).
- PostgreSQL 18 is the sole canonical runtime database.
- Authentication OTP policy: 4-digit, 120s TTL, 3/5min rate limit per phone+IP, 15-min access token, 30-day refresh (`D-018`).
- Production backend runtime: Python; canonical domain/application implementation (`D-019`).
- Production HTTP framework: FastAPI as thin transport adapter behind `POLApplicationBoundary` (`D-020`).

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
2. Changes to D-001–D-020 require explicit superseding decisions.
3. Code, migrations, tests and design artifacts must be traceable to current canonical documents.
4. Generated local artifacts must not be committed to the repository.
5. Production-readiness claims must distinguish domain verification from HTTP/auth/provider/UI/observability/deployment/recovery implementation.

### Agentic Design Execution — 2026-09-21

For AI-agent-driven Penpot construction, the execution control authority is:
`13_PRODUCT_DESIGN/52_POL_PENPOT_AGENTIC_DESIGN_EXECUTION_PROTOCOL_2026-09-21.md`

It governs agent behavior during design construction: preflight, capability probing, atomic mutations, checkpoints, visual/structural verification, approvals, resumability, rollback, and evidence separation. It does not override product decisions or domain/API authority.

### Product Architecture Evolution — 2026-09-20

The current product-design authority now also includes:

- POL_00_PROJECT_CONTROL/PRODUCT_EVOLUTION/PRODUCT_ARCHITECTURE_EVOLUTION_WAVE_01_2026-09-20.md

This document records the adopted product-architecture direction for:
- Financial Activity without MVP stored-value Wallet
- Multi-vendor OrderGroup -> vendor Orders -> vendor Invoices visibility
- Lightweight Delivery Handoff without a full Driver App
- Product-first and Vendor-first discovery
- Neutral settlement wording
- Web + Android for every persona with delegated permissions
- Barcode scanning as a first-class operational capability
- Master SKU and product-media provenance

These directions refine presentation, UX and implementation sequencing without overriding D-001 through D-020 or the canonical PostgreSQL/Python/FastAPI architecture. The Decision Register amendments D-021 through D-028 are the governing product decisions for this wave.


---

## 7. Deep-Saturation Design Control — 2026-09-21

The five-pass design saturation audit is registered as a supporting design-control artifact:

- `13_PRODUCT_DESIGN/53_POL_MASTER_TREE_DEEP_SATURATION_AUDIT_2026-09-21.md`

The active Master Tree is now Version 3.5.0:

- `13_PRODUCT_DESIGN/50_POL_MASTER_PENPOT_UI_UX_TREE_SPEC_2026-09-21.md`
- `13_PRODUCT_DESIGN/54_POL_MASTER_TREE_EXECUTABLE_SCHEMA_2026-09-21.md`
- `13_PRODUCT_DESIGN/55_POL_MASTER_TREE_NODE_SCHEMA_2026-09-21.json`

The active agent execution protocol is now Version 1.1.0:

- `13_PRODUCT_DESIGN/52_POL_PENPOT_AGENTIC_DESIGN_EXECUTION_PROTOCOL_2026-09-21.md`

The Master Tree saturation layer adds control-plane requirements for context packaging, execution identity, trust boundaries, mutation intent, persistence proof, semantic/structural/visual evidence, state freshness, task/command contracts, accessibility/RTL/network semantics, token/component lifecycle, analytics tracking governance and change-impact controls.

These controls govern how design work is safely constructed and verified. They do not create new product capabilities and do not override product, domain, database, API or operations authorities.


### Executable Master Tree — 2026-09-21

The human-readable Master Tree and its executable schema are now registered as the active design-control pair:

- Human semantic authority: `13_PRODUCT_DESIGN/50_POL_MASTER_PENPOT_UI_UX_TREE_SPEC_2026-09-21.md`
- Machine-readable structural authority: `13_PRODUCT_DESIGN/55_POL_MASTER_TREE_NODE_SCHEMA_2026-09-21.json`
- Closure/validation rules: `13_PRODUCT_DESIGN/54_POL_MASTER_TREE_EXECUTABLE_SCHEMA_2026-09-21.md`

The executable schema constrains structure and evidence reporting; it does not override product/domain/API authority.
