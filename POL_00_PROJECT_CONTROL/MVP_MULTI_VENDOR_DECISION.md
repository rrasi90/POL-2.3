# POL MVP MULTI-VENDOR ARCHITECTURE DECISION (D-014)

**Document ID:** `POL-DEC-014`  
**Decision Title:** Multi-Vendor Basket Allocation & Independent Execution in MVP  
**Status:** `LOCKED / CANONICAL`  
**Governance Level:** Founder & Lead Product Architect Approved  
**Supersedes:** `D-003` (Single Vendor per Basket in MVP v0 — marked HISTORICAL)  
**Date:** 2026-09-12  
**Target Milestone:** MVP Release v1.0 (Ahvaz Pilot)  

---

## 1. Context & Business Rationale

In the initial exploratory architecture (D-003), POL specified a "Single-Vendor per Basket" constraint to reduce early operational complexity. However, empirical market analysis of Ahvaz Wholesalers Hub (شهرک بنکداران اهواز) and grocery retail procurement economics revealed a critical product failure risk:

1. **Category Specialization of Wholesalers:** No single wholesaler stocks the full spectrum of FMCG items a supermarket needs (e.g., Wholesaler A specializes in grains/oil, Wholesaler B in confectionery/beverages, Wholesaler C in detergents/hygiene).
2. **Cart Abandonment Under Single-Vendor Constraints:** Forcing a supermarket owner to fragment their order into multiple disconnected sessions or prune items artificially destroys the primary value proposition of digital wholesale procurement: *one-stop shop convenience*.
3. **Founder & Product Strategic Decision:** A retailer must be allowed to build **ONE unified basket**. The POL platform assumes the cognitive burden of solving the multi-vendor procurement puzzle by running an intelligent, deterministic allocation algorithm that routes items to wholesalers while minimizing order fragmentation.

---

## 2. Formal Architecture Decision: D-014

### Canonical Statement
> **In POL MVP, a Retailer builds ONE unified basket containing products from potentially multiple wholesalers. POL's deterministic Allocation Engine dynamically partitions the basket into feasible, optimal vendor-specific sub-orders (Child Orders) grouped under a single parent OrderGroup, enforcing vendor MOV, SKU MOQ, physical availability, and minimum order fragmentation, while preserving independent fulfillment, acceptance, delivery, settlement, and dispute lifecycles for each wholesaler.**

### Foundational Invariants

1. **Unified Retailer Experience:**
   - The retail buyer sees a single shopping cart, a single unified checkout review, and a single consolidated payment authorization intent.
   - The buyer can inspect the allocation breakdown (which wholesaler fulfills which item and subtotal) prior to payment confirmation.

2. **Open Vendor Count ($N \ge 1$, No Hardcoded Limit):**
   - In accordance with **D-005**, the vendor count per basket is **NOT hardcoded to $\le 2$**.
   - The allocation algorithm naturally penalizes unnecessary vendor fragmentation through its objective hierarchy, favoring 1 vendor if feasible, then 2, then $N$ as necessary to satisfy the retailer's basket.

3. **Strict Vendor Autonomy & Independent Feasibility:**
   - **Independent MOV Enforcement:** Every allocated vendor sub-basket must independently satisfy that vendor's Minimum Order Value (`vendor_mov_toman`). If an allocation candidate assigns items totaling less than the vendor's MOV, that allocation candidate is strictly non-viable and rejected.
   - **Independent SKU MOQ Enforcement:** Every allocated item must meet or exceed the vendor's sellable pack Minimum Order Quantity (`vendor_moq`).
   - **Independent Acceptance SLA:** Each vendor receives their own child order (`orders`) with an independent acceptance timer (15-minute operational target, 2-hour hard timeout). A timeout or rejection by Vendor A does not cancel or invalidate Vendor B's accepted order.

4. **Independent Physical Fulfillment & Logistics:**
   - Each vendor packs and dispatches their portion independently.
   - In accordance with **D-008** (Asset-Light Logistics), local hub transport (وانت‌های بومی شهرک) dispatches per vendor order or coordinates consolidated drop-off where route efficiency allows, without cross-dock inventory warehousing by POL.

5. **Orthogonal Dispute & Financial Integrity:**
   - Discrepancies, shortages, or damaged goods attach strictly to the specific child `orders` or `order_items` via the independent `disputes` aggregate (satisfying D-010 and the orthogonal dispute invariant).
   - Settlement (`settlements`) is computed and disbursed per vendor order; dispute withholdings on Vendor A never block timely settlement to Vendor B.

6. **Unfulfilled Demand Preservation:**
   - Items that cannot be feasibly allocated due to out-of-stock, MOV failures, or geographic constraints are recorded in `allocation_items` with `status = 'UNFULFILLED'` and `vendor_id = NULL`. They are transparently surfaced to the retailer with clear explainability codes (e.g., `VENDOR_MOV_NOT_MET`, `OUT_OF_STOCK`).

---

## 3. Structural Transition: D-003 vs D-014

| Dimension | Historical MVP v0 (D-003) | Canonical MVP v1.0 (D-014) |
|:---|:---|:---|
| **Retailer Basket** | Single vendor per basket only | Unified multi-vendor capable basket |
| **Catalog Browsing** | Filtered by single vendor or forced switch | Unified Master Product catalog with vendor offers |
| **Allocation Engine** | Single-vendor selection heuristic | Multi-vendor combinatorial heuristic with MOV/MOQ |
| **Order Aggregate** | 1 Basket = 1 Order | 1 Basket = 1 AllocationPlan = 1 OrderGroup = $N$ Orders |
| **Vendor Count** | Hardcoded = 1 | Open $N$ (Optimized to minimum necessary) |
| **Vendor MOV Check** | Global basket value $\ge$ vendor MOV | Per-vendor sub-basket value $\ge$ vendor MOV |
| **Vendor Rejection** | Entire basket fails | Only that vendor's child order fails; other vendors proceed |
| **Dispute Blast Radius** | Affects entire order | Confined strictly to affected vendor child order |
| **Database Schema Change** | N/A (Schema was already designed $N$-vendor ready per D-004) | 0 Schema migrations required; 100% schema parity preserved |

---

## 4. Governance & Verification Mandate

1. `07_ALGORITHMS/MVP_MULTI_VENDOR_ALLOCATION.md` defines the formal heuristic algorithm and tie-breaking specifications.
2. `08_DATA/MULTI_VENDOR_ORDERING_MODEL.md` defines the exact aggregate lifecycles, states, and relational mappings.
3. `scripts/allocation_engine.py` provides the canonical deterministic implementation.
4. `scripts/test_allocation_engine.py` validates the 15 baseline allocation invariants.
5. `scripts/test_runtime_scenarios.py` validates the 30 mission-critical runtime scenarios with transactional integrity.
