# POL CURRENT SOURCE OF TRUTH & REPOSITORY GOVERNANCE

**Document ID:** `POL-GOV-001`  
**Version:** 1.4 (Canonical)  
**Status:** `LOCKED / OFFICIAL GOVERNANCE CHARTER`  
**Effective Milestone:** Sprint 0 & MVP v1.0  
**Last Audit:** 2026-09-28  
**Targeted source-path audit:** 2026-11-17 against `main` @ `fbcdd7448d809a3281cc1ea8c43218d42e8762ca` (targeted documentation/source-path and migration-inventory review only; not a full runtime or release audit).  

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
        Design Artifacts / Frontend / Mobile / Backend
```

`DECISION_REGISTER.md` is the highest repository-level product authority. Design artifacts may refine presentation and interaction but may not change business rules, authorization rules, financial custody rules, or MVP scope.

---


### Tool-Agnostic Execution Law

The Master Product / Experience / Delivery Tree is tool-neutral. No design, coding, AI-agent, documentation or QA product is a source of product truth merely by being used in execution. Canonical requirements, business rules, domain/API contracts, state machines, permissions, acceptance criteria and release gates remain invariant when an execution tool is replaced.

Canonical design/build authority:
`13_PRODUCT_DESIGN/50_POL_MASTER_PRODUCT_EXPERIENCE_DELIVERY_CONTROL_TREE_SPEC_2026-09-21.md` — **Master Tree v4.3.0**, interpreted as the tool-agnostic product/design/delivery registry.

## 2. Canonical Authorities by Domain

| Domain | Authoritative Canonical File(s) | Scope & Responsibility | Precedence Rule |
|:---|:---|:---|:---|
| **Strategic & Architectural Decisions** | `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` | Sole authority for Founder Decisions D-001 through D-029; later amendments supersede earlier decisions explicitly. | Absolute precedence. |
| **Current MVP Scope & Requirements** | `06_PRODUCT/MVP_Definition.md`, `06_PRODUCT/PRD.md` | Feature matrix, core flows, boundaries and MVP inclusions/exclusions. | Must conform to the currently effective Decision Register, D-001–D-029; later explicit amendments supersede earlier decisions. |
| **Identity & Access Management** | `06_PRODUCT/Roles_and_Permissions.md`, `POL_00_PROJECT_CONTROL/USER_PROFILE_AND_PERSONA_MODEL.md`, Master Tree VD-15 | Identity, tenant membership, role authorization, delegated permissions, persona context and UX preferences. | `organization_memberships.role` is the base authorization SSoT; effective access is `base role permissions + active delegated grants`, always scoped to an active user, active organization and active membership. `users.role` is legacy/deprecated. |
| **Order Lifecycle & State Transitions** | `06_PRODUCT/Order_Lifecycle.md`, `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` | OrderGroup, child Orders, Delivery and exception state machines. | Governs backend workflows and UI state mapping. |
| **Domain Entities & Business Invariants** | `08_DATA/DOMAIN_MODEL.md` | Ubiquitous language, aggregates and invariants. | Governs domain service behavior. |
| **Database Schema & Migrations** | `migrations/001_*.sql` through the current `main` migration head (`077` as verified by the contiguous numbered migration files and `POL_00_PROJECT_CONTROL/DATABASE_SCHEMA_MANIFEST.md` at the audit SHA), `08_DATA/Data_Schema.md`, and `POL_00_PROJECT_CONTROL/DATABASE_SCHEMA_MANIFEST.md` | PostgreSQL 18 DDL, constraints, indexes, triggers and foreign keys. | The complete numbered forward-only migration chain is the physical schema authority; later migrations supersede earlier physical state without rewriting historical migrations. |
| **API Contracts & DTOs** | `06_PRODUCT/API_Contracts.md`, `POL_00_PROJECT_CONTROL/CANONICAL_CONTRACT_MATRIX.md`, `POL_00_PROJECT_CONTROL/CANONICAL_CONTRACT_MATRIX_CORRECTIONS_2026-09-16.md`, and the implementation boundary in `scripts/application_boundary.py` | REST/JSON contracts and application-boundary commands. | Correction overlay supersedes conflicting legacy terminology. |
| **Allocation Engine Algorithm** | `07_ALGORITHMS/MVP_MULTI_VENDOR_ALLOCATION.md` | Deterministic multi-vendor allocation, MOV/MOQ and ranking. | Governs allocation implementation. |
| **Brand & Design System** | `POL_00_PROJECT_CONTROL/BRAND_ARCHITECTURE.md`, `13_PRODUCT_DESIGN/56_POL_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM_2026-09-21.md`, `13_PRODUCT_DESIGN/50_POL_MASTER_PRODUCT_EXPERIENCE_DELIVERY_CONTROL_TREE_SPEC_2026-09-21.md` | Brand hierarchy, Precision Commerce visual direction, design tokens, interaction patterns, Light/Night visual language and design QA. | Design may not override product/engineering decisions. |
| **Operations, Fulfillment & Logistics** | `09_OPERATIONS/Fulfillment.md`, `09_OPERATIONS/Payments_and_Settlement.md`, `09_OPERATIONS/Support_and_Disputes.md` | Field SOPs, logistics, direct settlement and support/dispute operations. | Governs operational workflows. |
| **Async Workers & Event Runtime** | `POL_00_PROJECT_CONTROL/WORKER_ARCHITECTURE.md`, `08_DATA/Event_Architecture.md` | Canonical PostgreSQL 18 transactional outbox + Python worker execution model. | Supersedes BullMQ/Redis Streams as the MVP event transport. |
| **Pilot Definition & Metrics** | `11_PILOT/Pilot_Strategy.md`, `11_PILOT/KPIs.md`, `11_PILOT/Success_Criteria.md` | Ahvaz pilot parameters and Gate 1 telemetry. | Governs pilot validation. |
| **Readiness & Certification** | `POL_00_PROJECT_CONTROL/GLOBAL_ENGINEERING_AUDIT_2026-09-14.md`, `POL_00_PROJECT_CONTROL/REPOSITORY_COMPLETION_AUDIT_2026-09-16.md`, `POL_00_PROJECT_CONTROL/CERTIFICATION_ADDENDUM_2026-09-14.md` | Explicit separation of verified domain core vs remaining production-applicationization gates. | No document may claim production readiness beyond these boundaries. |

---

## 3. Active Document Rule

All active documents MUST represent the current architecture:

- Current MVP basket model is **Multi-Vendor (`D-014`)**.

**Historical lineage note (2026-09-18):** Stage 04 audit-start PR #1 and its Run #365 evidence belong to an earlier certification lineage. They are retained for traceability only and are not current `main` verification evidence. Current verification must be established from the current `main` HEAD and current CI/runtime evidence.
- Single-Vendor MVP is historical only (`D-003`).
- Vendor count is open; no hardcoded `<=2` rule.
- MVP payment remains `NON_CUSTODIAL_DIRECT`.
- Vendor Referral is active MVP (`D-016`) without rewards/wallet/credit incentives.
- Universal User Profile + Membership Persona Context is active MVP (`D-017`).
- PostgreSQL 18 is the sole canonical runtime database.
- Authentication OTP policy: six-digit, 120s TTL, 3/5min rate limit per phone+IP, 15-min access token, 30-day refresh (`D-018`).
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
2. Changes to D-001–D-029 require explicit superseding decisions.
3. Code, migrations, tests and design artifacts must be traceable to current canonical documents.
4. Generated local artifacts must not be committed to the repository.
5. Production-readiness claims must distinguish domain verification from HTTP/auth/provider/UI/observability/deployment/recovery implementation.

### Tool-Agnostic Design Execution — 2026-09-21

Design construction is governed by the written Master Tree, the canonical visual design system, repository safety rules, and the evidence ledgers in `mvp/`. Execution tooling is interchangeable and is never itself a product authority.

### Product Architecture Evolution — 2026-09-20

The current product-architecture direction is represented by the active Decision Register and the current Master Tree.

This document records the adopted product-architecture direction for:
- Financial Activity without MVP stored-value Wallet
- Multi-vendor OrderGroup -> vendor Orders -> vendor Invoices visibility
- Lightweight Delivery Handoff without a full Driver App
- Product-first and Vendor-first discovery
- Neutral settlement wording
- Web + Android for every persona with delegated permissions
- Barcode scanning as a first-class operational capability
- Master SKU and product-media provenance

These directions refine presentation, UX and implementation sequencing without overriding the currently effective D-001 through D-029 decisions or the canonical PostgreSQL/Python/FastAPI architecture. The Decision Register amendments D-021 through D-029, including the 2026-11-24 OTP update, are the governing product decisions for this wave.


---

### Precision Commerce Visual Direction — 2026-09-21

POL's canonical product visual direction is **A — Precision Commerce**.

The active visual authority on this branch is:

- `13_PRODUCT_DESIGN/56_POL_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM_2026-09-21.md`
- `13_PRODUCT_DESIGN/50_POL_MASTER_PRODUCT_EXPERIENCE_DELIVERY_CONTROL_TREE_SPEC_2026-09-21.md`

Operational closure evidence is maintained in:

- `mvp/MVP_SCREEN_MATRIX.md`
- `mvp/MVP_API_MAP.md`
- `mvp/MVP_KNOWN_GAPS.md`

Required theme policy: **Light + Night are first-class variants for every applicable canonical screen, section and component.** Night is semantic theming, not color inversion.

The visual system governs appearance, tokens, typography, shape, elevation, density, motion, RTL presentation and visual QA only. It does not override product/domain/API/permission/financial/MVP authorities.




### Design Approval → Engineering Readiness — 2026-09-21

The project explicitly separates DESIGN_APPROVED from ENGINEERING_READY. Design approval certifies the written/design layer; engineering readiness additionally requires action, permission, state, data, API, error/recovery, analytics, platform and test mappings.

Current implementation state is governed by `mvp/BUILD_PLAN.md`, `mvp/MVP_SCREEN_MATRIX.md` and current repository evidence: Web has a partial live-verified baseline; Android/Expo source exists and is in Phase 3 verification. Remaining mobile parity and verification gates must not be described as absent source. These are engineering workstreams, not claims of design failure.
### Greenfield design tool Build Mode — 2026-09-21

The current design execution target is a completely new, empty design tool file.

`BUILD_MODE = GREENFIELD_EMPTY_FILE`

Historical design tool is evidence only. Construction begins from WAVE-00 empty-file preflight and proceeds dependency-first:

Foundations → Components → Patterns → Golden Screens → Product Surfaces → Prototypes → QA.

### Master Tree v4 Registry Upgrade — 2026-09-21

The Master Tree is a registry-first control model:

Canonical Node Registry → Federated Views → Relationship Graph → Closure Profiles → Evidence → Artifact Binding → Drift Control → Release Snapshot.

This upgrade does not create new product capabilities. It strengthens canonicality, applicability-aware closure, many-to-many evidence/relationships, artifact identity, source health, agent source packets and executable fitness functions.

Repeated screen IDs in derived sections are projections, not independent sources of truth.

## 7.1 Historical Remediation Checkpoint — 2026-09-25 (superseded by live GitHub state)

This is a historical checkpoint from 2026-09-25, retained for traceability. It recorded that the remediation branch described at that time had been integrated into main. The remaining statements in this checkpoint about current CI failures and closure classes are date-bounded; they are not present-day CI claims. Use live branch refs and workflow runs for the exact SHA under review. Source presence alone is not runtime or release certification.

Current unresolved closure classes are:
- explicit product/security decisions: D-018 refresh-token rotation, invoice timing, D-024 storefront write scope;
- deployment/provider/observability evidence;
- selected deep mobile management UI parity;
- fresh CI certification after the current GitHub Actions execution blocker is resolved.

The repository must not mark these items VERIFIED merely because source implementation exists.

## 7. Deep-Saturation Design Control — 2026-09-21

The active design-control set on the current branch is:

- `13_PRODUCT_DESIGN/50_POL_MASTER_PRODUCT_EXPERIENCE_DELIVERY_CONTROL_TREE_SPEC_2026-09-21.md`
- `13_PRODUCT_DESIGN/56_POL_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM_2026-09-21.md`
- `mvp/MVP_KNOWN_GAPS.md`
- `mvp/MVP_SCREEN_MATRIX.md`
- `mvp/MVP_API_MAP.md`

Execution safety and verification are governed by `.agents/rules/00-pol-canonical-safety.md` plus the active Master Tree and evidence ledgers. These controls govern how work is safely constructed and verified; they do not create new product capabilities or override product, domain, database, API or operations authorities.


### Executable Master Tree — 2026-09-21

The active human-readable design authority is `13_PRODUCT_DESIGN/50_POL_MASTER_PRODUCT_EXPERIENCE_DELIVERY_CONTROL_TREE_SPEC_2026-09-21.md`; closure/validation evidence is maintained in `mvp/MVP_KNOWN_GAPS.md`, `mvp/MVP_SCREEN_MATRIX.md`, and `mvp/MVP_API_MAP.md`.

## Historical Remediation Re-Audit Checkpoint — 2026-09-26 (superseded)

- Main remains authoritative at the main branch; remediation changes remain isolated on `remediation/full-closure-2026-09-25`.
- Current remediation head at this checkpoint: `c380e7c1a0d9c3d993d45629707ab411829b1dd5`.
- Additional closure completed after the prior saturation audit:
  - valid organization switching corrected and regression-protected;
  - retailer staff blocked from basket mutation, allocation, checkout and formal dispute opening;
  - retailer partial-acceptance decisions restricted to retailer owners;
  - vendor order acceptance/rejection restricted to vendor owners;
  - vendor staff baseline order.accept removed and delegation ceilings prevent re-granting owner-only capabilities;
  - mobile CI Node runtime aligned with Expo SDK 57 requirements;
  - project evidence documents reconciled against the current remediation branch.
- Current CI is not certifiable: the latest remediation workflow jobs fail before useful step execution, with no executable step metadata and unavailable job logs.
- Historical backend/mobile/device results remain historical evidence for their respective commits and are not promoted to current-head PASS.
- Remaining unresolved closure classes are still the explicit governance/product decisions, deployment/provider/browser/device evidence, and the external OpenPencil/runtime dependencies identified in the audit register.
\n

## Historical Post-Reaudit Remediation Checkpoint — 2026-09-26 (superseded)
- Remediation branch: `remediation/full-closure-2026-09-25`
- Latest remediation head at checkpoint: `5c40c14a619e0c530ae795638b556d79d7f86705`
- Additional source-level findings closed after the prior checkpoint: G-052 delegated-permission ceiling enforcement at evaluation time; G-053 product-media tenant/provenance authorization; G-054 fail-closed handling and database invariant for legacy unbound in-flight uploads.
- Regression coverage added/extended in `scripts/test_delegated_permissions.py` and `scripts/test_media_service.py`.
- Fresh GitHub Actions executions continue to terminate with failed jobs whose step lists are empty, including reruns. Therefore current-head CI certification remains **blocked by execution/evidence**, not marked PASS.
- Main remains unchanged; these changes are isolated to the remediation branch/PR.

- Latest post-reaudit source head: `52e5c79c5874aa53f15af8a0048c945f8e234298`.
- Additional closure after the prior checkpoint: G-055 Field Task HTTP/boundary contract alignment; G-056 Support related-order tenant binding.
- Regression coverage added in `scripts/test_http_field_tasks.py` and `scripts/test_http_support.py`.

- Fresh CI executions on the latest head continue to fail before any workflow step is reported (`steps=[]`); this remains an execution/evidence blocker, not a source-level PASS/FAIL determination.
- G-057 HTTP referral redemption is now wired to canonical first-touch attribution with deterministic idempotency; `scripts/test_http_referrals.py` covers creation + replay.
