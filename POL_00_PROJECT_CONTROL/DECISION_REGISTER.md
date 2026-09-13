# POL PROJECT DECISION REGISTER (CANONICAL SOURCE OF TRUTH)

**Document ID:** `POL-DEC-001`  
**Status:** `LOCKED / CANONICAL`  
**Governance Level:** Lead Product Architect / Founder Approved  
**Last Audit:** 2026-09-12 (Pre-Sprint 0 Hardening Pass)  
**Cross-Reference:** `01_RESEARCH/Assumptions_and_Hypotheses.md` (RES-REG-001)  

---

## 1. Governance Principles & Invariant Policy

All decisions recorded in this register are **LOCKED** for Sprint 0 and MVP execution.  
- No engineer, product manager, or external contributor may alter or bypass these decisions without explicit Founder/Architect signed authorization based on empirical pilot telemetry.
- These decisions serve as the foundational constraints for software architecture, database schema, operational protocols, and commercial modeling.

---

## 2. Canonical Strategic Decision Register (D-001 through D-014)

| Decision ID | Canonical Decision Title | Approved Formal Decision | Strategic Rationale & Invariant Guardrail | Affected Canonical Documents |
|:---:|:---|:---|:---|:---|
| **D-001** | **Launch Geography & Scope** | **Ahvaz** (Specifically the 61-hectare Wholesalers Hub / شهرک بنکداران اهواز with ~700 active warehouses) is the sole launch and pilot geography for Year 1. Expansion outside Ahvaz is prohibited prior to Gate 1 passage. | Maximum physical inventory density, localized logistics network, lower cost of operations compared to Tehran, extreme climate creating acute demand for remote ordering. | `00_PROJECT_OVERVIEW/Opportunity_Definition.md`, `06_PRODUCT/PRD.md`, `11_PILOT/Pilot_Strategy.md` |
| **D-002** | **Pilot Duration & Horizon** | Pilot duration is strictly **3 Months (90 calendar days / 12 weeks)**. Neither compressed to 1 month nor extended beyond 90 days before Gate 1 evaluation. | Allows observation of 3 to 4 complete supermarket reorder cycles to empirically capture retention, repeat purchase behavior, and true operational churn. | `11_PILOT/Pilot_Strategy.md`, `01_RESEARCH/Assumptions_and_Hypotheses.md` |
| **D-003** | **MVP Basket Allocation Rule (HISTORICAL v0)** | In MVP v0, single vendor per basket was initially specified to minimize initial operational complexity. **SUPERSEDED by D-014 for MVP v1.0**. | Retained for historical traceability. Transitioned to multi-vendor basket per Founder/Architect directive to prevent cart abandonment and solve retailer FMCG procurement fragmentation. | `POL_00_PROJECT_CONTROL/MVP_MULTI_VENDOR_DECISION.md` |
| **D-004** | **Data Model Multi-Vendor Extensibility** | Database schema, domain aggregates, and outbox event models MUST natively support **$N$-Vendor order allocation** from Day 1. | Decouples the logical basket (`Basket`, `BasketItem`) from fulfillment orders (`OrderGroup`, `Order`, `OrderItem`). Prevents architectural rewrites when multi-vendor routing is enabled. | `08_DATA/Data_Schema.md`, `08_DATA/DOMAIN_MODEL.md`, `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` |
| **D-005** | **Open Future Vendor Count (No Hardcode)** | The maximum number of vendors per order in future multi-vendor phases is **OPEN (NOT hardcoded to $\le 2$)**. | Optimal vendor count is an optimization function balancing cross-docking/delivery cost, buyer delivery friction, and item availability. Hardcoding $\le 2$ artificially constrains algorithm optimization. | `06_PRODUCT/Future_Cart_Allocation_Research.md`, `07_ALGORITHMS/MVP_MULTI_VENDOR_ALLOCATION.md` |
| **D-006** | **Pilot Take Rate / Commission** | Platform commission during the 3-month Ahvaz pilot is **0.0% (Free for Vendors)**. | Eliminates adoption friction, incentivizes wholesalers to maintain updated stock/prices, and establishes baseline cost-to-serve without pricing resistance. | `03_BUSINESS_MODEL/Revenue_Model.md`, `11_PILOT/Vendor_LOI.md` |
| **D-007** | **Post-Pilot Commission Framework** | Post-pilot monetization is modeled as a **Category-Tiered Take Rate of 1.0% to 3.0%** (Hypothesis to be validated in Month 3). | Aligns with FMCG wholesaler gross margins: ~1.0% for low-margin staple commodities (rice, oil, sugar) up to 3.0% for higher-margin personal care and detergents. | `03_BUSINESS_MODEL/Commission_Model.md`, `03_BUSINESS_MODEL/Business_Model_and_Unit_Economics.md` |
| **D-008** | **POL Logistics Fleet Cost** | POL logistics asset ownership and direct fleet capex/opex is **$0.00 (Asset-Light Model)**. Deliveries utilize existing local hub truck fleets (وانت‌های بومی شهرک). | Avoids vehicle depreciation, maintenance overhead, and driver liabilities. POL acts as logistics coordinator/facilitator rather than fleet operator. | `09_OPERATIONS/Fulfillment.md`, `02_STRATEGY/Strategic_Thesis.md` |
| **D-009** | **Advertising & Monetization Timeline** | In-app sponsored listings, banners, and advertising products are deferred to **H2 Year 4 (Post-Market Density)**. | Prevents degradation of trust during network seeding. Wholesaler ranking in Years 1–3 is 100% meritocratic based on verified stock, price, and fulfillment SLA. | `06_PRODUCT/Discovery.md`, `03_BUSINESS_MODEL/Revenue_Model.md` |
| **D-010** | **Order Entity Hierarchy Separation** | Strict separation of order lifecycle entities: `Basket -> AllocationPlan -> OrderGroup -> Order -> OrderItem`. | Enforces clear separation between buyer basket intent and vendor fulfillment commitments, providing clean auditability for state transitions. | `08_DATA/Data_Schema.md`, `08_DATA/DOMAIN_MODEL.md`, `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` |
| **D-011** | **Dual Currency Presentation vs Storage** | User-facing UI, invoices, and SMS communications use **100% Tomans (تومان)**. Financial models, reporting, and analytical registers reference **USD ($)** for inflation-invariant analysis. | Eliminates cognitive friction for local retail buyers while protecting business model comparability against severe Rial devaluation. | `00_PROJECT_OVERVIEW/Glossary.md`, `06_PRODUCT/PRD.md` |
| **D-012** | **Master Product vs Vendor Product Separation** | Absolute architectural separation between **`Master Product` (physical canonical identity)** and **`Vendor Product / SKU` (vendor's sellable commercial offer)**. | Ensures global catalog integrity (barcodes, normalized titles, brand taxonomy, standard reference pack) while allowing vendor autonomy over prices, inventory, and sellable pack sizes. | `08_DATA/CATALOG_PRODUCT_MASTER.md`, `08_DATA/INVENTORY_MODEL.md` |
| **D-013** | **Imported Dataset Role & Quarantine** | The initial raw catalog dataset (`backup_no_images.json`) is strictly classified as **`IMPORTED_REFERENCE` (Quarantined Reference Seed)**. | External scrapings/imports lack verified barcodes (100% missing in seed), contains noise, and do not represent active POL vendor inventory, live prices, or real user ratings. | `08_DATA/Master_SKU_Import_Audit.md`, `08_DATA/Data_Schema.md` |
| **D-014** | **Multi-Vendor Basket in MVP** | In MVP v1.0, retail buyers construct ONE unified basket across multiple wholesalers. POL's deterministic Allocation Engine dynamically partitions the basket into feasible vendor-specific child orders grouped under an OrderGroup, enforcing independent vendor MOV, SKU MOQ, physical availability, and minimum order fragmentation, while preserving independent fulfillment, acceptance, delivery, settlement, and dispute lifecycles. | Maximizes FMCG basket completion, avoids forcing retailer to split carts manually, fulfills POL's core value proposition of intelligent routing while protecting wholesalers with strict independent MOV/MOQ and order execution. | `POL_00_PROJECT_CONTROL/MVP_MULTI_VENDOR_DECISION.md`, `07_ALGORITHMS/MVP_MULTI_VENDOR_ALLOCATION.md`, `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` |
| **D-015** | **Canonical Database & Technical Environment** | **PostgreSQL 18** is the sole canonical production, staging, migration, and runtime database engine. In-memory SQLite is restricted exclusively to fast-path isolated unit tests. `psycopg2-binary>=2.9.9` is the canonical driver. All prior references to PostgreSQL 16 are formally superseded. | Eliminates dialect and concurrency divergence, leverages PostgreSQL 18 native query performance, transactional outbox atomicity, partial unique indexing, and native JSONB indexing. | `POL_00_PROJECT_CONTROL/TECHNICAL_ENVIRONMENT.md`, `migrations/001_initial_schema.sql` |

---

## 3. Downstream Traceability Verification

All code generators, database migration scripts, API controllers, and operational playbooks must link their design constraints directly to one of the Decision IDs above:

- **Sprint 0 Migrations:** Must adhere to D-004, D-010, D-012, D-013, D-014.
- **Order Engine MVP:** Must enforce D-014 (superseding D-003) while implementing schema conforming to D-004 and D-005.
- **Catalog Management Service:** Must enforce D-012 and D-013.
- **Pilot Operations:** Must strictly execute according to D-001, D-002, D-006, D-008, and D-014.

---

## 4. Change Control Policy
Modifications to any decision in this register require:
1. Documented failure or disconfirmation of the underlying hypothesis via pilot telemetry in `01_RESEARCH/Evidence_Register.md`.
2. Architecture review meeting between Lead Architect and Lead Engineer.
3. Formal version increment of this document with signed Git commit.
