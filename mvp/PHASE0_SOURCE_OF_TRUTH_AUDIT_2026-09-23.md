# POL — Stage 1 Source-of-Truth Audit

**Date:** 2026-09-23  
**Branch:** `main`  
**Stage:** 1 — Source of Truth Lock / Governance Reconciliation  
**Status:** **DONE**

## Objective

Reconcile the active product, architecture, design-control and delivery documents so an agent can execute against one current source of truth without silently inheriting stale branch, route, verification or implementation claims.

## Authority chain verified

1. `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`
2. `POL_00_PROJECT_CONTROL/CURRENT_SOURCE_OF_TRUTH.md`
3. `06_PRODUCT/MVP_Definition.md` / `06_PRODUCT/PRD.md`
4. Domain/data/order authorities
5. `mvp/MVP_API_MAP.md`
6. `13_PRODUCT_DESIGN/50_POL_MASTER_PRODUCT_EXPERIENCE_DELIVERY_CONTROL_TREE_SPEC_2026-09-21.md`
7. `mvp/BUILD_PLAN.md`
8. `mvp/MVP_SCREEN_MATRIX.md`
9. `mvp/MVP_KNOWN_GAPS.md`
10. `mvp/PHASE5_DELIVERY_REPORT.md`

## Reconciliations performed

### 1. Current branch authority
- `main` is the authorized execution branch in `mvp/BUILD_PLAN.md`.
- Master Tree metadata was aligned to `main`.
- The previous architecture-evolution branch is retained only as historical lineage.

### 2. Current implementation status
- The Source of Truth no longer states that Android/Expo source is absent.
- Current state is: Android/Expo source exists; Phase 3 implementation and verification remain incomplete.
- Historical certification evidence is explicitly separated from current verification evidence.

### 3. Historical verification evidence
- Earlier PR/CI evidence (including older 212/212 and prior certification lineage) is retained only as historical evidence.
- Current readiness requires evidence from the current `main` HEAD.

### 4. Decision authority range
- Governance references were aligned with the currently effective Decision Register through D-028 rather than stopping at D-020.

### 5. API authority
- Master Tree live search wording was aligned to the current REAL route `/api/v1/catalog/search`.
- `mvp/MVP_API_MAP.md` remains the current HTTP contract authority.
- Historical/contract-only paths are not to be used as live endpoints merely because they remain documented for traceability.

### 6. Existing GAP / CONFLICT discipline
The following remain intentionally unresolved and are not to be guessed:
- G-003 catalog legacy-path conflict
- G-004 inbox/notification path conflict
- G-009 Vendor Customers
- G-010 Vendor Staff / delegated permissions
- G-011 contract-only admin capabilities
- G-012 basket list
- G-013 global returns list
- G-021 partial-acceptance proposal list
- D-028 barcode runtime contract
- refresh-token rotation
- invoice timing
- storefront write fields
- OpenPencil MCP availability

These are correctly represented as GAP / CONFLICT / BLOCKED_EXTERNAL / OPEN according to the applicable source.

## Canonical invariants confirmed

- Basket → AllocationPlan → OrderGroup → Order → OrderItem
- Multi-vendor basket is MVP canonical.
- PostgreSQL 18 is the canonical database.
- Python is the authoritative production backend runtime.
- FastAPI is a thin transport layer over `POLApplicationBoundary`.
- Authorization is sourced from organization membership context.
- No frontend second business-logic layer.
- No second backend runtime.
- Historical evidence cannot be promoted to current verification without fresh execution.
- No missing contract is to be invented.

## Stage 1 result

**PASS / DONE**

The repository governance layer is sufficiently reconciled for the next stage.

### Next stage

**Stage 2 — Repository Audit:** inspect the actual Backend, Web, Mobile and Infrastructure implementation against the canonical documents and produce a file-level implementation/status matrix.