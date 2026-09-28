# POL — FINAL HARDENING FINDINGS REGISTER

**Status:** LOGGED BEFORE EDIT (Pre-Hardening Audit)  
**Date:** 2026-09-12  
**Governance Scope:** Repository Pre-Sprint 0 Consistency, Master SKU Governance, Packaging Logic, and Pilot Synchronization  

---

## Executive Summary
Prior to executing modifications in the pre-Sprint 0 hardening pass, an exhaustive audit was performed across the canonical document base (211 total files, focused on `00_PROJECT_OVERVIEW`, `01_RESEARCH`, `06_PRODUCT`, `08_DATA`, `09_OPERATIONS`, `11_PILOT`, and `POL_00_PROJECT_CONTROL`).

Eight specific hardening findings (H-01 through H-08) were identified and cataloged below with severity, exact file references, systemic risk evaluation, planned remediation, and verification methods.

---

## Findings Matrix

| Finding ID | Severity | Category | Target Component / File | Description Summary |
|---|---|---|---|---|
| **H-01** | P1 | Decision Governance | `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` | Absence of a unified central Decision Register for D-001..D-013 risking multi-source drift. |
| **H-02** | P1 | Catalog & Packaging Logic | `08_DATA/CATALOG_PRODUCT_MASTER.md` | Need for explicit separation between reference packaging (`products.default_pack_*`) and sellable offers (`vendor_products.packaging_*`). Clarification that inventory is generic (quantity + unit). |
| **H-03** | P0 | Candidate Lifecycle Invariant | `08_DATA/CATALOG_MATCHING.md` (Line 50) | Invariant violation: Document states vendor can immediately sell inventory upon Candidate creation (`DRAFT_PENDING_CATALOG`). Must be blocked from public marketplace listing until catalog review. |
| **H-04** | P1 | Matching Heuristics | `08_DATA/CATALOG_MATCHING.md` (Lines 31-45) | Static confidence thresholds (0.85, 0.50) framed as definitive facts rather than pilot calibration hypotheses. |
| **H-05** | P2 | Operational Claims | `06_PRODUCT/PRD.md` (L211), `08_DATA/DOMAIN_MODEL.md` (L89) | "Under 10 seconds per item" stated as an established operational reality instead of an initial UX/performance target. |
| **H-06** | P1 | Pilot Terminology Synchronization | `11_PILOT/Pilot_Strategy.md`, `11_PILOT/KPIs.md` | Ambiguity between "Pilot Supply Cohort" (5–10 vendors), "Anchor Vendors" (1–2 vendors), and "MVP Basket Allocation" (Single Vendor per basket). |
| **H-07** | P2 | Non-Empirical Language | `11_PILOT/Pilot_Strategy.md` (Line 12) | Use of unscientific phrase "Irrefutable Evidence Pack" (بسته شواهد تزلزل‌ناپذیر) which violates empirical startup governance. |
| **H-08** | P2 | Table Reference Typo | `11_PILOT/KPIs.md` (Line 55) | Typographical reference to obsolete/non-existent table `product_barcodes` instead of canonical `product_identifiers`. |

---

## Detailed Finding Records

### Finding H-01: Centralized Decision Register Missing in Project Control
- **Finding ID:** H-01
- **Severity:** P1 (High)
- **Target Location:** `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` (Missing File), `01_RESEARCH/Assumptions_and_Hypotheses.md`
- **Problem Description:** While `01_RESEARCH/Assumptions_and_Hypotheses.md` defines strategic decisions D-001 through D-013, `POL_00_PROJECT_CONTROL/` lacks a dedicated, standalone Decision Register. This creates a risk of drift where development teams might look for decisions in disparate strategy files.
- **Why It Matters:** Strategic decisions (Ahvaz, 3-month pilot, 0% pilot commission, single vendor MVP basket allocation, asset-light $0 logistics, 5-10 vendor supply cohort) are locked and non-negotiable for Sprint 0. Without a central immutable register, requirements creep can recur.
- **Planned Fix:** Create `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` capturing D-001 through D-013 with formal IDs, titles, status (`LOCKED`), rationale, and downstream file cross-references.
- **Verification Method:** Check file existence, verify exact alignment with D-001..D-013 in `01_RESEARCH/Assumptions_and_Hypotheses.md`, and run repository consistency checks.

---

### Finding H-02: Reference Packaging vs. Sellable Offer Clarity & Generic Inventory Units
- **Finding ID:** H-02
- **Severity:** P1 (High)
- **Target Location:** `08_DATA/CATALOG_PRODUCT_MASTER.md`, `08_DATA/Data_Schema.md`
- **Problem Description:** `order_items` and `vendor_inventories` support generic units (`quantity` + `unit_of_measure`), but `CATALOG_PRODUCT_MASTER.md` does not explicitly state the architectural boundary between:
  1. `products.default_pack_*` (canonical manufacturer reference packaging, e.g. standard case size 24), and
  2. `vendor_products.packaging_*` (the vendor's sellable offer packaging, allowing Vendor A to sell a half-box of 12 or promo bundle of 48 under the same Master Product).
- **Why It Matters:** In FMCG wholesale, wholesalers frequently break cases or sell multi-case bundles. Conflating master product packaging with vendor sellable packaging creates schema bottlenecks or forces artificial master SKU duplication.
- **Planned Fix:** Add explicit architectural governance in `08_DATA/CATALOG_PRODUCT_MASTER.md` stating:
  - `products` holds reference pack metadata for standardization.
  - `vendor_products` defines the sellable packaging offer (`packaging_unit`, `items_per_package`).
  - Inventory quantity is generic (`quantity` + `unit_of_measure`, e.g. 40 CARTON or 240 PIECE).
  - Add test case in `scripts/test_verification_mutations.py` validating that a single Master Product can have multiple distinct sellable vendor packaging configurations.
- **Verification Method:** Execute `python scripts/test_verification_mutations.py`.

---

### Finding H-03: Invariant Violation in Candidate Lifecycle (`CATALOG_MATCHING.md`)
- **Finding ID:** H-03
- **Severity:** P0 (Critical Invariant Violation)
- **Target Location:** `08_DATA/CATALOG_MATCHING.md` (Line 50)
- **Problem Description:** The document states:
  > *"در این حالت یک Product Candidate ثبت شده و Vendor Product موقت ایجاد می‌شود تا وندور بلافاصله بتواند قیمت و موجودی خود را بفروشد."*
  This directly violates the canonical domain invariant defined in `08_DATA/DOMAIN_MODEL.md` and `migrations/000001_initial_schema.sql` where `listing_status` for candidates is `DRAFT_PENDING_CATALOG` and marketplace visibility is strictly blocked (`is_active = FALSE` or unlisted) until human catalog review approves or maps the candidate.
- **Why It Matters:** Allowing unverified product candidates to immediately sell on the public buyer marketplace causes catalog pollution, pricing confusion, duplicate listings, and corrupted order fulfillment during the pilot.
- **Planned Fix:** Update `08_DATA/CATALOG_MATCHING.md` to state:
  - When matching confidence < 0.50, a `product_candidate` is created with status `PENDING_REVIEW`.
  - A linked `vendor_product` is created in status `DRAFT_PENDING_CATALOG`.
  - The offer is **NOT** visible or purchasable on the buyer marketplace until catalog operations approves or maps the candidate to a Master SKU.
  - Candidate images serve as internal matching evidence, not public catalog media.
- **Verification Method:** Grep search for "بفروشد" and verify domain model consistency.

---

### Finding H-04: Matching Heuristics Formulated as Absolute Facts Instead of Hypotheses
- **Finding ID:** H-04
- **Severity:** P1 (High)
- **Target Location:** `08_DATA/CATALOG_MATCHING.md` (Lines 31-45)
- **Problem Description:** Confidence thresholds (`>= 0.85` for Auto-match, `0.50 - 0.84` for Human Review, `< 0.50` for New Candidate) are stated as definitive, mathematically absolute operational limits without stating that they are initial baseline heuristics requiring empirical calibration during pilot intake.
- **Why It Matters:** Real-world Iranian wholesale FMCG titles contain typos, colloquial brand names, and unstructured packaging descriptors. Treating initial threshold values as unchangeable facts prevents the data team from calibrating thresholds based on Pilot precision/recall telemetry.
- **Planned Fix:** Reframe the thresholds in `08_DATA/CATALOG_MATCHING.md` as **"Initial Matching Threshold Hypothesis"** (`[HYPOTHESIS-MATCH-01]`), retaining the 7 standard matching KPI definitions (`precision`, `recall`, `auto_match_rate`, `human_review_rate`, `false_positive_rate`, `latency_p95`, `catalog_lead_time`).
- **Verification Method:** Verify text in `08_DATA/CATALOG_MATCHING.md` and check consistency scripts.

---

### Finding H-05: Unsubstantiated Operational Metric ("Under 10 Seconds")
- **Finding ID:** H-05
- **Severity:** P2 (Medium)
- **Target Location:** `06_PRODUCT/PRD.md` (Line 211), `08_DATA/DOMAIN_MODEL.md` (Line 89)
- **Problem Description:** The texts state that vendor onboarding/item mapping is "under 10 seconds per item" as an established operational metric, whereas no pilot data has yet been collected.
- **Why It Matters:** Stating an unverified target as an accomplished fact violates startup truth-seeking principles and confuses engineering expectations for MVP SLA.
- **Planned Fix:** Reformulate the language across both documents to: **"Initial UX Target: median ≤ 10 seconds per successfully auto-mapped item (P95 target ≤ 20s)"**.
- **Verification Method:** Ripgrep search across repository for "10 ثانیه" / "10 seconds" and confirm rephrasing.

---

### Finding H-06: Pilot Supply Cohort vs. Basket Allocation Terminology Ambiguity
- **Finding ID:** H-06
- **Severity:** P1 (High)
- **Target Location:** `11_PILOT/Pilot_Strategy.md`, `11_PILOT/KPIs.md`, `02_STRATEGY/Market_Strategy.md`
- **Problem Description:** In several sections, "Single Vendor MVP" (an order allocation rule stating that a single basket must be fulfilled by a single vendor) was conflated with the overall pilot supply size (5–10 active vendors, with 1–2 anchor vendors).
- **Why It Matters:** Developers or investors reading "Single Vendor MVP" might mistakenly assume that the entire pilot only has one vendor, undermining the marketplace supply diversity and multi-vendor competitive pricing dynamics.
- **Planned Fix:** Standardize terms across all pilot and strategy documents:
  - **Pilot Supply Cohort:** 5–10 verified wholesale vendors in Ahvaz.
  - **Anchor Vendors:** 1–2 primary high-inventory FMCG distributors ensuring catalog depth.
  - **MVP Basket Allocation Rule:** Single Vendor per Basket (each buyer checkout is routed to exactly one vendor for MVP operations).
- **Verification Method:** Review `11_PILOT/Pilot_Strategy.md` and check automated consistency checks.

---

### Finding H-07: Subjective Marketing Language in Scientific Pilot Documentation
- **Finding ID:** H-07
- **Severity:** P2 (Low/Medium)
- **Target Location:** `11_PILOT/Pilot_Strategy.md` (Line 12)
- **Problem Description:** The document uses the non-empirical phrase:
  > *"بسته شواهد تزلزل‌ناپذیر (Irrefutable Evidence Pack)"*
  which over-promises certainty in an inherently probabilistic, hypothesis-driven startup pilot.
- **Why It Matters:** Professional institutional investors and rigorous technical teams expect disciplined scientific terminology ("Decision-Grade Evidence" or "Investor-Grade Evidence Pack") rather than subjective hyperbole.
- **Planned Fix:** Replace all occurrences of "Irrefutable Evidence Pack" with "Decision-Grade / Investor-Grade Evidence Pack" (بسته شواهد تصمیم‌گیری / بسته شواهد استاندارد سرمایه‌گذاری).
- **Verification Method:** Ripgrep search for "Irrefutable" and "تزلزل‌ناپذیر".

---

### Finding H-08: Obsolete Database Table Reference in KPI Specification
- **Finding ID:** H-08
- **Severity:** P2 (Medium)
- **Target Location:** `11_PILOT/KPIs.md` (Line 55)
- **Problem Description:** Line 55 references `product_barcodes.barcode` in an SQL telemetry example, whereas the canonical table name established in `migrations/000001_initial_schema.sql` and `08_DATA/Data_Schema.md` is `product_identifiers`.
- **Why It Matters:** Direct copy-pasting of telemetry queries by data engineers during Sprint 0 will fail with PostgreSQL `relation "product_barcodes" does not exist`.
- **Planned Fix:** Update `11_PILOT/KPIs.md` line 55 from `product_barcodes` to `product_identifiers` (`identifier_type = 'BARCODE'`). Also explicitly partition all KPIs into:
  - Target (هدف)
  - Minimum Acceptable / Go-No-Go Threshold (حداقل قابل قبول)
  - Actual / Measured (مقدار واقعی - ثبت در طول پایلوت)
- **Verification Method:** Inspect line 55 in `11_PILOT/KPIs.md` and verify SQL correctness against schema.

---

## Conclusion & Action Authorization
All 8 findings are documented with actionable, non-destructive solutions. Proceeding immediately to step-by-step remediation across the codebase.

---

## Reconciliation — 2026-09-25 Remediation Branch

This document is the historical pre-hardening finding record. The following status reflects the current remediation branch and must be read together with the current Source of Truth and release evidence.

| Finding | Current status | Current evidence |
|---|---|---|
| H-01 | RESOLVED | `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` exists and is the centralized decision register. |
| H-02 | RESOLVED | Current catalog/schema governance explicitly separates canonical product packaging from vendor sellable packaging; inventory remains unit-aware. |
| H-03 | RESOLVED IN SOURCE | Candidate creation persists `PENDING_REVIEW`; linked vendor offers use `DRAFT_PENDING_CATALOG` + `is_active=FALSE`; public catalog/storefront queries require `listing_status='ACTIVE'`. HTTP regression coverage verifies the draft state. |
| H-04 | RESOLVED | Matching thresholds are explicitly labeled `[HYPOTHESIS-MATCH-01]` and calibrated against pilot evidence. |
| H-05 | RESOLVED | The `<10s` measure is explicitly described as an Initial UX Target, not an achieved operational fact. |
| H-06 | SUPERSEDED BY CURRENT DECISION MODEL | D-014 defines a unified multi-vendor retailer basket; the old “single vendor per basket” wording is historical and no longer authoritative. |
| H-07 | RESOLVED | Pilot language uses “Decision-Grade / Investor-Grade Evidence Pack”. |
| H-08 | RESOLVED | No current project source references the obsolete `product_barcodes` table; canonical identity uses `product_identifiers`. |

**Residual release gate:** fresh CI execution, deployed provider/browser/device evidence, and any explicitly unresolved product decisions remain separate from source remediation.
