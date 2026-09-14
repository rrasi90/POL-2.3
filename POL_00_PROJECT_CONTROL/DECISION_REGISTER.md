# POL PROJECT DECISION REGISTER (CANONICAL SOURCE OF TRUTH)

**Document ID:** `POL-DEC-001`  
**Status:** `LOCKED / CANONICAL`  
**Governance Level:** Lead Product Architect / Founder Approved  
**Last Audit:** 2026-09-14 (Cross-Domain MVP Hardening Pass)  
**Cross-Reference:** `01_RESEARCH/Assumptions_and_Hypotheses.md` (RES-REG-001)  

---

## 1. Governance Principles & Invariant Policy

All decisions recorded in this register are **LOCKED** for Sprint 0 and MVP execution.

- No engineer, product manager, or external contributor may alter or bypass these decisions without explicit Founder/Architect signed authorization based on empirical pilot telemetry.
- These decisions serve as foundational constraints for software architecture, database schema, operational protocols, and commercial modeling.
- A feature marked **MVP** in this register must not be moved to a future phase without a new superseding decision.
- A feature marked **FUTURE / NOT MVP** must not be activated through UI, API, pricing, or operations merely because its database foundation exists.

---

## 2. Canonical Strategic Decision Register (D-001 through D-016)

| Decision ID | Canonical Decision Title | Approved Formal Decision | Strategic Rationale & Invariant Guardrail | Affected Canonical Documents |
|:---:|:---|:---|:---|:---|
| **D-001** | **Launch Geography & Scope** | **Ahvaz** (Specifically the 61-hectare Wholesalers Hub / شهرک بنکداران اهواز) is the sole launch and pilot geography for Year 1. Expansion outside Ahvaz is prohibited prior to Gate 1 passage. | Maximum physical inventory density and localized operations during validation. | `00_PROJECT_OVERVIEW/Opportunity_Definition.md`, `06_PRODUCT/PRD.md`, `11_PILOT/Pilot_Strategy.md` |
| **D-002** | **Pilot Duration & Horizon** | Pilot duration is strictly **3 Months (90 calendar days / 12 weeks)**. | Captures multiple FMCG reorder cycles and real operational retention. | `11_PILOT/Pilot_Strategy.md`, `01_RESEARCH/Assumptions_and_Hypotheses.md` |
| **D-003** | **MVP Basket Allocation Rule (HISTORICAL v0)** | Single-vendor basket was the historical MVP v0 rule. **SUPERSEDED by D-014.** | Retained only for traceability. | `POL_00_PROJECT_CONTROL/MVP_MULTI_VENDOR_DECISION.md` |
| **D-004** | **Data Model Multi-Vendor Extensibility** | Database schema, domain aggregates, and outbox event models MUST natively support **N-vendor** order allocation from Day 1. | Prevents architectural rewrite when vendor routing expands. | `08_DATA/Data_Schema.md`, `08_DATA/DOMAIN_MODEL.md`, `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` |
| **D-005** | **Open Future Vendor Count** | Future maximum vendor count per order remains **OPEN**; no hardcoded `<=2` constraint. | Vendor count must remain an optimization variable. | `06_PRODUCT/Future_Cart_Allocation_Research.md`, `07_ALGORITHMS/MVP_MULTI_VENDOR_ALLOCATION.md` |
| **D-006** | **Pilot Take Rate / Commission** | Pilot commission is **0.0%**. | Removes adoption friction during the 90-day validation period. | `03_BUSINESS_MODEL/Revenue_Model.md`, `11_PILOT/Vendor_LOI.md` |
| **D-007** | **Post-Pilot Commission Framework** | Post-pilot take-rate hypothesis is **1.0%–3.0%**, subject to validation. | Revenue must follow observed vendor economics. | `03_BUSINESS_MODEL/Commission_Model.md`, `03_BUSINESS_MODEL/Business_Model_and_Unit_Economics.md` |
| **D-008** | **POL Logistics Fleet Cost** | POL owns **no delivery fleet** in the pilot. Local hub / partner carrier capacity is used. | Preserves asset-light economics. | `09_OPERATIONS/Fulfillment.md`, `02_STRATEGY/Strategic_Thesis.md` |
| **D-009** | **Advertising & Monetization Timeline** | Sponsored listings, banners, and in-app advertising are deferred to **H2 Year 4**. | Trust and supply quality take precedence over early monetization. | `06_PRODUCT/Discovery.md`, `03_BUSINESS_MODEL/Revenue_Model.md` |
| **D-010** | **Order Entity Hierarchy Separation** | Strict separation: `Basket -> AllocationPlan -> OrderGroup -> Order -> OrderItem`. | Separates buyer intent from vendor fulfillment commitments. | `08_DATA/Data_Schema.md`, `08_DATA/DOMAIN_MODEL.md`, `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` |
| **D-011** | **Dual Currency Presentation vs Storage** | UI, invoices, and SMS use **Tomans**; analytical/strategic registers may use **USD**. | Local UX plus inflation-invariant strategic analysis. | `00_PROJECT_OVERVIEW/Glossary.md`, `06_PRODUCT/PRD.md` |
| **D-012** | **Master Product vs Vendor Product Separation** | `Master Product` and `Vendor Product / SKU` are separate canonical entities. | Preserves catalog identity while allowing vendor-specific offers. | `08_DATA/CATALOG_PRODUCT_MASTER.md`, `08_DATA/INVENTORY_MODEL.md` |
| **D-013** | **Imported Dataset Role & Quarantine** | Imported catalog data remains `IMPORTED_REFERENCE` and is never treated as live vendor truth without verification. | Prevents reference data from becoming false operational inventory. | `08_DATA/Master_SKU_Import_Audit.md`, `08_DATA/Data_Schema.md` |
| **D-014** | **Multi-Vendor Basket in MVP** | MVP v1.0 uses ONE unified retailer basket across multiple wholesalers. The deterministic Allocation Engine partitions it into vendor-specific child orders with independent MOV/MOQ, inventory, acceptance, fulfillment, delivery, settlement and dispute lifecycles. | Core POL value proposition; supersedes D-003. | `POL_00_PROJECT_CONTROL/MVP_MULTI_VENDOR_DECISION.md`, `07_ALGORITHMS/MVP_MULTI_VENDOR_ALLOCATION.md`, `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` |
| **D-015** | **Canonical Database & Technical Environment** | **PostgreSQL 18** is the sole canonical production, staging, migration and runtime database. SQLite is restricted to isolated unit tests only. | Eliminates dialect/concurrency divergence. | `POL_00_PROJECT_CONTROL/TECHNICAL_ENVIRONMENT.md`, `migrations/001_initial_schema.sql` |
| **D-016** | **Vendor Referral in MVP** | **Vendor Referral is a mandatory MVP capability.** Vendors create a referral code/link; a retailer redeems it once as first-touch attribution during onboarding/activation; attribution is persisted, auditable and connected to the order lifecycle. **No monetary referral reward, wallet, credit, or complex incentive engine is activated in MVP.** | Vendor relationships are a direct acquisition channel in the Ahvaz B2B model. POL must measure supplier-led acquisition before adding paid/referral incentives. | `scripts/vendor_referral.py`, `migrations/013_vendor_referral_mvp_and_integrity_fixes.sql`, `scripts/test_vendor_referral.py` |

---

## 3. MVP vs Future Activation Rule

The presence of a database foundation does **not** mean the feature is active.

### ACTIVE IN MVP
- Assisted onboarding / assisted first order
- Vendor catalog + price + inventory visibility
- Unified multi-vendor basket and deterministic allocation
- Checkout revalidation + reservation
- Order acceptance / fulfillment / delivery / POD
- Digital invoice / order history
- Support / dispute / RMA foundations
- Transactional notifications
- Daily vendor inventory confirmation
- **Vendor Referral attribution (D-016)**
- Non-custodial direct payment + reconciliation foundation

### ARCHITECTURE-READY BUT NOT ACTIVATED IN MVP
- Personalized pricing
- Advanced commercial terms / trade promotions
- BNPL / embedded credit
- Wallet / escrow / custody
- Sponsored products / advertising
- Advanced AI recommendation / forecasting
- Complex loyalty / gamification / social commerce
- Owned logistics / warehouse infrastructure
- Multi-touch referral incentives

See `POL_00_PROJECT_CONTROL/FUTURE_VERSION_NOT_MVP.md`. That document is explicitly non-MVP and must not be treated as a current product specification.

---

## 4. Downstream Traceability Verification

All code generators, database migration scripts, API controllers and operational playbooks must link their design constraints directly to one of the Decision IDs above.

- **Sprint 0 Migrations:** D-004, D-010, D-012, D-013, D-014, D-016.
- **Order Engine MVP:** D-014 plus D-004/D-005.
- **Vendor Referral MVP:** D-016; attribution-first and incentive-free.
- **Pilot Operations:** D-001, D-002, D-006, D-008, D-014, D-016.

---

## 5. Change Control Policy

Modifications to any decision in this register require:
1. Documented failure or disconfirmation of the underlying hypothesis via pilot telemetry in `01_RESEARCH/Evidence_Register.md`.
2. Architecture review between Lead Architect and Lead Engineer.
3. Formal version increment of this document with signed Git commit.
