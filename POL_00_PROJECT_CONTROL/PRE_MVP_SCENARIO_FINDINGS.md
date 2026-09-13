# POL — PRE-MVP SCENARIO STRESS TEST FINDINGS REGISTER

**Document ID:** `POL-SF-001`  
**Status:** `LOGGED & REMEDIATED`  
**Governance:** Lead Product Architect & Repository Governance Agent  
**Date:** 2026-09-12  

> [!WARNING]
> **HISTORICAL / SUPERSEDED**
> 
> This document reflects an earlier POL architecture.
> The current MVP Multi-Vendor architecture supersedes the previous Single-Vendor MVP decision.
> **Current source of truth:** `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`  
> **Current decision:** `D-014`

---

## 1. Executive Summary

During the pre-MVP 100-scenario behavioral stress test, seven (7) specific architectural findings (SF-01 through SF-07) across P0, P1, and P2 severities were identified. Each finding has been rigorously analyzed, traced to its root cause, and remediated in the canonical specification documents without compromising strategic foundations or delaying Sprint 0.

---

## 2. Findings Summary Matrix

| Finding ID | Severity | Category | Target Files | Problem Summary | Remediation Status |
|:---:|:---:|:---|:---|:---|:---:|
| **SF-01** | **P0** | Architectural Contradiction | `07_ALGORITHMS/Cart_Allocation.md` | Active split-cart checkout description contradicted `D-003` (Single-Vendor MVP). | **REMEDIATED** |
| **SF-02** | **P0** | Event Naming Contradiction | `06_PRODUCT/Test_Specification.md` | Referenced legacy event `order_disputed` instead of canonical `dispute_opened`. | **REMEDIATED** |
| **SF-03** | **P1** | Operational SLA Inconsistency | `06_PRODUCT/Order_Lifecycle.md`, `11_PILOT/KPIs.md` | Ambiguity between target acceptance time (<45 min) and hard acceptance timeout (2 hours). | **REMEDIATED** |
| **SF-04** | **P1** | Semantic Ambiguity & Coexistence | `00_PROJECT_OVERVIEW/Glossary.md` | MOQ defined strictly as cartons; coexistence rules with MOV at checkout unspecified. | **REMEDIATED** |
| **SF-05** | **P1** | Undefined Edge-Case Behavior | `07_ALGORITHMS/Cart_Allocation.md`, `06_PRODUCT/API_Contracts.md` | Undefined system behavior when no single vendor stocks 100% of cart items. | **REMEDIATED** |
| **SF-06** | **P1** | Concurrency Specification Gap | `08_DATA/INVENTORY_MODEL.md`, `08_DATA/DOMAIN_MODEL.md` | Missing explicit SQL atomic conditional reservation pattern for race condition safety. | **REMEDIATED** |
| **SF-07** | **P2** | Security & API Specification | `06_PRODUCT/API_Contracts.md`, `06_PRODUCT/Roles_and_Permissions.md` | Semantic ambiguity between HTTP 401 (Unauthenticated) and HTTP 403 (Forbidden/RBAC). | **REMEDIATED** |

---

## 3. Detailed Finding Records

### Finding SF-01: Split-Cart Contradiction in Cart Allocation Specification
- **Finding ID:** SF-01
- **Severity:** P0 (Critical Invariant Contradiction)
- **Scenarios Impacted:** RET-021, RET-030, VND-021
- **Observed Behavior:** `07_ALGORITHMS/Cart_Allocation.md` (Lines 16 and 71) described active split-cart checkout: *"سناریوی ب (بهترین قیمت تفکیکی — Best Split-Cart): در صورتی که اختلاف قیمت بیش از ۵٪ باشد، تفکیک سبد میان ۲ بنکدار به صورت پیشنهاد اختیاری ارائه می‌شود."*
- **Expected Behavior:** In accordance with canonical decision `D-003` (Single-Vendor per Basket for MVP), active split-cart checkout is disabled for MVP v1.0. Multi-vendor cart allocation is strictly a future research capability (`D-004`, `D-005`).
- **Root Cause:** Historical algorithm proposal text remained in `Cart_Allocation.md` after `D-003` was locked.
- **Authoritative Source:** `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` (Decision `D-003`).
- **Files Affected:** `07_ALGORITHMS/Cart_Allocation.md`.
- **Fix Applied:** Refactored `Cart_Allocation.md` to specify:
  1. MVP cart optimization evaluates and returns strictly single-vendor allocations (`Best Single-Vendor`).
  2. Multi-vendor split-cart algorithms are designated as post-pilot research (`Future_Cart_Allocation.md`, `Future_Cart_Allocation_Research.md`).
  3. No active MVP UI or API endpoint allows multi-vendor cart checkout.
- **Verification:** Grep search for "Best Split-Cart" confirms zero active occurrences.

---

### Finding SF-02: Legacy Dispute Event Name in Test Specification
- **Finding ID:** SF-02
- **Severity:** P0 (Contract / Event Inconsistency)
- **Scenarios Impacted:** RET-051..060, VND-039
- **Observed Behavior:** `06_PRODUCT/Test_Specification.md` (Line 52) stated: *"And رویداد 'order_disputed' منتشر شده و پیامک ثبت شکایت برای خریدار و بنکدار ارسال می‌گردد"*.
- **Expected Behavior:** In accordance with the orthogonal dispute domain architecture (`Event_Architecture.md`, `DOMAIN_MODEL.md`), dispute events are independently named: `dispute_opened`, `dispute_resolved`, `dispute_closed`. `order_disputed` is deprecated.
- **Root Cause:** Incomplete audit update in BDD test specification file during previous pass.
- **Authoritative Source:** `08_DATA/Event_Architecture.md` §3 (Table of Domain Events).
- **Files Affected:** `06_PRODUCT/Test_Specification.md`.
- **Fix Applied:** Replaced `order_disputed` with `dispute_opened`.
- **Verification:** Grep search confirms zero occurrences of `order_disputed` in active documentation.

---

### Finding SF-03: Ambiguity Between Target Acceptance Time vs Hard Acceptance Timeout
- **Finding ID:** SF-03
- **Severity:** P1 (Operational & State Machine Ambiguity)
- **Scenarios Impacted:** RET-039, VND-023
- **Observed Behavior:** Documentation variously mentioned "< 45 minutes" (KPI target), "< 60 minutes" (first month target), "< 90 minutes" (in table), and "2 hours" (exception timeout) without a clear hierarchy separating operational goals from hard system cancellations.
- **Expected Behavior:** A formal, deterministic rule separating:
  - `Target Acceptance Time`: Median < 45 minutes (Operational UX/KPI target).
  - `Hard Acceptance Timeout`: Exactly 120 working minutes (08:00–18:00 Ahvaz business hours).
  - Explicit action on timeout: Automatic cancellation, inventory release, SMS to retailer, ops alert, -0.25 vendor reputation penalty.
- **Root Cause:** Conflating performance aspirations (targets) with timeout event triggers.
- **Authoritative Source:** `06_PRODUCT/Exception_Handling.md` (EX-07), `11_PILOT/KPIs.md`.
- **Files Affected:** `06_PRODUCT/Order_Lifecycle.md`, `11_PILOT/KPIs.md`.
- **Fix Applied:** Added Section 2.1 to `06_PRODUCT/Order_Lifecycle.md` detailing the exact timeout mechanics, events, and reputation penalty.
- **Verification:** Verified state transition table in `PRE_MVP_STATE_MACHINE_MATRIX.md`.

---

### Finding SF-04: Generic Unit MOQ vs Monetary MOV Semantic Coexistence
- **Finding ID:** SF-04
- **Severity:** P1 (Commerce Validation Gap)
- **Scenarios Impacted:** RET-024..029
- **Observed Behavior:** `00_PROJECT_OVERVIEW/Glossary.md` defined MOQ as "حداقل تعداد کارتن" (cartons only) and lacked explicit checkout rules for the coexistence of SKU-level MOQ and vendor-level MOV.
- **Expected Behavior:**
  - MOQ (`vendor_inventory.moq`): Minimum Order Quantity for a specific SKU in generic units (CARTON, BOX, PIECE, PACK).
  - MOV (`vendors.min_order_value_toman`): Minimum Order Value for the vendor in Tomans.
  - Both must be satisfied at checkout: failing MOQ triggers HTTP 422 `MOQ_VIOLATION`; failing MOV triggers HTTP 422 `MOV_VIOLATION`.
- **Root Cause:** Legacy text assumed wholesale orders only deal in cartons and did not codify the validation algorithm.
- **Authoritative Source:** `08_DATA/Data_Schema.md`, `08_DATA/INVENTORY_MODEL.md`.
- **Files Affected:** `00_PROJECT_OVERVIEW/Glossary.md`.
- **Fix Applied:** Updated Glossary with canonical generic unit definitions and explicit checkout validation logic.
- **Verification:** Unit tests in test harness.

---

### Finding SF-05: Undefined Edge-Case Behavior When No Single Vendor Can Fulfill Cart
- **Finding ID:** SF-05
- **Severity:** P1 (UX / Commercial Logic Gap)
- **Scenarios Impacted:** RET-030
- **Observed Behavior:** When a retailer selects items where no single vendor has 100% stock, earlier documentation was silent on what the UI and allocation engine must do in Single-Vendor MVP.
- **Expected Behavior:** Deterministic system behavior:
  1. Engine selects the vendor providing the maximum fulfilled order value and coverage ($\ge MOV$).
  2. Unfulfilled items are clearly flagged in the preview as `UNFULFILLED` / unstocked by this vendor.
  3. Retailer is offered smart in-stock substitutes from the same vendor.
  4. If retailer declines substitutes, unfulfilled items remain in the active cart, and the retailer can proceed with the fulfilled items or switch vendors.
  5. The unfulfilled items can later be ordered from another vendor as a separate, distinct order.
- **Root Cause:** Absence of explicit single-vendor edge-case specification.
- **Authoritative Source:** `07_ALGORITHMS/Cart_Allocation.md`, `06_PRODUCT/PRD.md`.
- **Files Affected:** `07_ALGORITHMS/Cart_Allocation.md`.
- **Fix Applied:** Documented in `Cart_Allocation.md` §4 and scenario RET-030.
- **Verification:** Scenario RET-030 assertion verification.

---

### Finding SF-06: Concurrency Protection on Inventory Reservation
- **Finding ID:** SF-06
- **Severity:** P1 (Data Integrity / Concurrency)
- **Scenarios Impacted:** RET-031, VND-027
- **Observed Behavior:** Specifications described inventory deduction but did not mandate atomic database-level conditional updates to prevent overselling race conditions under high concurrent demand.
- **Expected Behavior:** Formal atomic update pattern:
  `UPDATE vendor_inventory SET reserved_quantity = reserved_quantity + :qty WHERE vendor_product_id = :id AND (physical_quantity - reserved_quantity) >= :qty;`
  Zero rows updated indicates immediate stockout failure.
- **Root Cause:** High-level domain descriptions without explicit query-level concurrency guardrails.
- **Authoritative Source:** `08_DATA/INVENTORY_MODEL.md`, `08_DATA/DOMAIN_MODEL.md`.
- **Files Affected:** `08_DATA/INVENTORY_MODEL.md`, `POL_00_PROJECT_CONTROL/PRE_MVP_STATE_MACHINE_MATRIX.md`.
- **Fix Applied:** Added atomic SQL concurrency invariant to state machine matrix and inventory model.
- **Verification:** Adversarial test simulation in test harness.

---

### Finding SF-07: Disambiguation of Authentication (401) vs Authorization (403)
- **Finding ID:** SF-07
- **Severity:** P2 (API Standards & Security)
- **Scenarios Impacted:** RET-009, VND-004..006
- **Observed Behavior:** Some API error examples colloquially used 403 for missing tokens or 401 for unauthorized role access.
- **Expected Behavior:** Canonical RFC 9110 / REST standards:
  - **HTTP 401 Unauthorized:** Missing, expired, malformed, or invalid JWT/OTP authentication token.
  - **HTTP 403 Forbidden:** Valid authentication, but user's assigned role lacks permission for the requested resource (e.g. `RETAILER` accessing `/api/v1/vendor/orders`, or `VENDOR_STAFF` attempting `/api/v1/vendor/prices`).
- **Root Cause:** Casual use of HTTP error codes across different documentation sections.
- **Authoritative Source:** `06_PRODUCT/Roles_and_Permissions.md`, `06_PRODUCT/API_Contracts.md`.
- **Files Affected:** `06_PRODUCT/API_Contracts.md`.
- **Fix Applied:** Standardized status code mappings in API contracts and scenario assertions.
- **Verification:** Validated across negative authorization scenarios.
