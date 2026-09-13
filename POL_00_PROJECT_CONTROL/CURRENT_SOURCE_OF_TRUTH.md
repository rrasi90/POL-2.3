# POL CURRENT SOURCE OF TRUTH & REPOSITORY GOVERNANCE

**Document ID:** `POL-GOV-001`  
**Version:** 1.0 (Canonical)  
**Status:** `LOCKED / OFFICIAL GOVERNANCE CHARTER`  
**Effective Milestone:** Sprint 0 & MVP v1.0  
**Last Audit:** 2026-09-13  

---

## 1. Hierarchy of Authority

To eliminate architectural drift, cross-document contradictions, and unauthorized scope alterations, all development, modeling, and operational protocols must trace their constraints to the authoritative documents defined in this charter.

```
                     ┌──────────────────────────────────────────────┐
                     │ DECISION AUTHORITY (FOUNDER & ARCHITECT)     │
                     │ POL_00_PROJECT_CONTROL/DECISION_REGISTER.md  │
                     └──────────────────────┬───────────────────────┘
                                            │
           ┌────────────────────────────────┼────────────────────────────────┐
           ▼                                ▼                                ▼
┌───────────────────────┐      ┌─────────────────────────┐      ┌────────────────────────┐
│ PRODUCT SPECIFICATION │      │ TECHNICAL & DATA MODEL  │      │ OPERATIONAL PROTOCOLS  │
│ 06_PRODUCT/           │      │ 08_DATA/ & 06_PRODUCT/  │      │ 09_OPERATIONS/         │
│ • MVP_Definition.md   │      │ • DOMAIN_MODEL.md       │      │ • Fulfillment.md       │
│ • PRD.md              │      │ • Data_Schema.md        │      │ • Payments_and_...     │
│ • Order_Lifecycle.md  │      │ • API_Contracts.md      │      │ • Support_and_...      │
│ • Test_Specification  │      │ • MULTI_VENDOR_ORDER... │      │ 11_PILOT/              │
│ 07_ALGORITHMS/        │      │ • migrations/001_...    │      │ • Pilot_Strategy.md    │
│ • MVP_MULTI_VENDOR... │      │                         │      │ • KPIs.md              │
└───────────────────────┘      └─────────────────────────┘      └────────────────────────┘
```

---

## 2. Canonical Authorities by Domain

| Domain | Authoritative Canonical File(s) | Scope & Responsibility | Precedence Rule |
|:---|:---|:---|:---|
| **Strategic & Architectural Decisions** | `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` | Sole repository-wide authority for Founder Decisions (D-001 to D-015). | **Absolute Precedence**: Overrules all other documents in case of conflict. |
| **Current MVP Scope & Requirements** | `06_PRODUCT/MVP_Definition.md`<br>`06_PRODUCT/PRD.md` | Feature matrix, core user flows, boundary conditions, and MVP inclusions/exclusions. | Governs functional backlog and Sprint 0 acceptance criteria. |
| **Identity & Access Management (IAM)** | `06_PRODUCT/Roles_and_Permissions.md` | Multi-user organizations, memberships, session management, and RBAC (`User -> Organization -> Membership -> Role`). | `users.role` deprecated; `memberships.role` is authoritative SSoT. |
| **Order Lifecycle & State Transitions** | `06_PRODUCT/Order_Lifecycle.md`<br>`08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` | Aggregate state machines for `OrderGroup`, child `Orders`, and `Deliveries`. | Governs backend workflow engines and worker timers. |
| **Domain Entities & Business Invariants**| `08_DATA/DOMAIN_MODEL.md` | Ubiquitous language, aggregate boundaries, transactional invariants. | Governs domain entities and domain service logic. |
| **Database Schema & Migrations** | `migrations/001_initial_schema.sql`<br>`migrations/002_platform_core_schema.sql`<br>`08_DATA/Data_Schema.md`<br>`POL_00_PROJECT_CONTROL/DATABASE_SCHEMA_MANIFEST.md` | DDL, 56 canonical tables, check constraints, partial indexes, and foreign keys. | DDL in migrations chain (001 + 002) is the physical schema authority. |
| **API Contracts & DTOs** | `06_PRODUCT/API_Contracts.md`<br>`POL_00_PROJECT_CONTROL/CANONICAL_CONTRACT_MATRIX.md` | REST/JSON endpoints, request/response payloads, HTTP status codes, canonical contract matrix across 26 domains. | Governs frontend-backend integration and API gateways. |
| **Allocation Engine Algorithm** | `07_ALGORITHMS/MVP_MULTI_VENDOR_ALLOCATION.md` | Heuristic allocation pipeline, MOV/MOQ evaluation, objective ranking. | Governs `scripts/allocation_engine.py` implementation. |
| **Brand & Design System** | `POL_00_PROJECT_CONTROL/BRAND_ARCHITECTURE.md` | Brand hierarchy (`POL`, `POL Market`, `POL Vendor`), logo assets, surfaces. | Governs UI/UX typography, logos, app naming, and copies. |
| **Operations, Fulfillment & Logistics** | `09_OPERATIONS/Fulfillment.md`<br>`09_OPERATIONS/Payments_and_Settlement.md`<br>`09_OPERATIONS/Support_and_Disputes.md` | Field SOPs, local hub fleet coordination (وانت‌های بومی, Option A metadata), dispute resolution. | Governs field ops, driver dispatch, and customer support. |
| **Pilot Definition & Metrics** | `11_PILOT/Pilot_Strategy.md`<br>`11_PILOT/KPIs.md`<br>`11_PILOT/Success_Criteria.md` | Ahvaz pilot parameters, cohort sizing, Gate 1 evaluation KPIs. | Governs pilot telemetry and validation gates. |
| **Readiness & Certification** | `POL_00_PROJECT_CONTROL/FINAL_PLATFORM_ARCHITECTURE_AUDIT.md` | Sole document authorized to issue the pre-Sprint-0 platform runtime certification. | Supersedes all previous hardening/certification reports. |

---

## 3. Active Document Rule

All active documents listed above **MUST represent the CURRENT architecture**:
- The current MVP model is **Multi-Vendor Basket Allocation (`D-014`)**:
  - One unified retailer basket $\rightarrow$ intelligent heuristic allocation $\rightarrow$ minimum necessary vendor fragmentation $\rightarrow$ 1..N vendor child orders $\rightarrow$ independent fulfillment, delivery, dispute, and settlement.
- Active documents **MUST NOT** describe Single-Vendor per Basket as the current MVP rule.
- Active documents **MUST NOT** contradict the brand architecture (`POL Market / پل مغازهدار` for retailers, `POL Vendor / پل بنکدار` for wholesalers, `POL / پُل` for corporate).

---

## 4. Historical Documents Governance Policy

Documents generated during earlier exploratory, hardening, or certification phases that reference the superseded Single-Vendor rule (`D-003-HISTORICAL`) or earlier audits are **preserved for auditability and historical traceability**.

However, to prevent developer confusion, all historical documents MUST display the canonical banner at the very top:

```markdown
> [!WARNING]
> **HISTORICAL / SUPERSEDED**
> 
> This document reflects an earlier POL architecture.
> The current MVP Multi-Vendor architecture supersedes the previous Single-Vendor MVP decision.
> **Current source of truth:** `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`  
> **Current decision:** `D-014`
```

---

## 5. Change Management & Prohibition of Duplicate Registers

1. **Zero Competing Registers:** No engineer, product manager, or external contributor may create secondary decision logs, shadow PRDs, or competing certification documents.
2. **Amendment Protocol:** Amendments to any decision in `DECISION_REGISTER.md` require:
   - Documented empirical disconfirmation from Ahvaz pilot telemetry.
   - Written approval from Founder and Lead Product Architect.
   - A synchronized update across all downstream active documents.
