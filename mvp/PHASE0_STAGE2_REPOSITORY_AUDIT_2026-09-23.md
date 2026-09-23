# POL — Stage 2 Repository Audit

**Date:** 2026-09-23  
**Branch:** `main`  
**Stage:** 2 — Repository Audit  
**Status:** **DONE**

## Scope

Audited the current repository tree and representative implementation authorities across:

- Python/FastAPI backend transport
- `POLApplicationBoundary`
- canonical checkout gateway
- PostgreSQL migration chain
- Web application
- Expo/React Native application
- mobile API client and role routing
- mobile parity evidence
- CI workflows
- requirements and workspace configuration
- MVP screen/API/gap control documents

This audit is repository-content based. It does **not** claim local execution of pytest, npm, Expo or Android export because the GitHub integration available for this session does not provide a local project runtime.

## Audit result

### A. Backend architecture — PASS

Verified in source:

`scripts/api/main.py`
- FastAPI is the HTTP transport.
- Routes are mounted under `/api/v1`.
- HTTP handlers delegate through `get_application_boundary`.
- Health/readiness endpoints exist.

`scripts/application_boundary.py`
- `POLApplicationBoundary` is the client-facing command/query facade.
- Checkout delegates to `CanonicalCheckoutGateway`.
- Multi-vendor allocation and child-order construction are represented through the canonical boundary.

`scripts/checkout_gateway.py`
- Checkout has deterministic request fingerprinting.
- Existing idempotency keys are replayed only when the request fingerprint matches.
- Mismatched reuse raises an error.
- Allocation is revalidated before checkout.

**Conclusion:** no second Node/Nest backend runtime was found in the active runtime path.

### B. API contract discipline — PASS with documented gaps

The active FastAPI implementation matches the REAL-route section of `mvp/MVP_API_MAP.md` for the audited basket, catalog and order paths.

Confirmed:
- `POST /api/v1/baskets`
- `POST /api/v1/baskets/{basket_id}/items`
- `POST /api/v1/baskets/{basket_id}/allocation-preview`
- `GET /api/v1/catalog/search`
- `POST /api/v1/orders`
- order lifecycle routes
- order query/detail/timeline routes

The audit did not promote CONTRACT/GAP endpoints into REAL status.

Known unresolved contract gaps remain explicitly documented, including barcode, Vendor Customers, Vendor Staff/delegated permissions, global basket retrieval and partial-acceptance proposal listing.

### C. Web — PASS at implementation-baseline level

Repository contains the expected role surfaces and corporate/public routes represented in the current screen matrix.

The Web theme system has explicit Light and Night semantic variables and a persisted theme hook.

Current status remains the documented baseline:
- implementation exists;
- historical build/typecheck/live evidence exists;
- current post-mobile changes still require fresh regression evidence.

No current CI result is promoted to green from this audit.

### D. Mobile / Expo — IMPLEMENTED FOUNDATION, VERIFICATION OPEN

The repository contains actual Expo source, not merely documentation.

Confirmed:
- `mvp/apps/mobile/App.tsx`
- Login/OTP
- Retailer workspace
- Vendor workspace
- Ops workspace
- Field task surfaces
- Order detail
- Account/profile/notifications
- Support
- Assisted order
- API client with bearer authentication
- Idempotency-Key header support
- Light/Night token palettes
- mobile parity document
- mobile CI workflow

Role routing is backend-derived through `current_organization.role` with canonical seven-role normalization.

**Important audit conclusion:** implementation existence is real, but verification is not complete. Mobile remains IMPLEMENTED rather than VERIFIED until current CI + QA cycles provide evidence.

### E. Mobile theme — PARTIAL

Light/Night semantic palettes exist, but the audit found no completed screen-by-screen Night verification evidence and no final mobile theme QA record.

This is correctly left as an open Phase 3/QA gate rather than being falsely marked complete.

### F. Barcode — correctly blocked at contract level

The mobile parity document now uses the exact contract wording from `mvp/MVP_API_MAP.md`:

`POST /api/v1/products/match-barcode` is CONTRACT-only.

No camera adapter or barcode success semantics were invented.

### G. CI — PRESENT, EXECUTION NOT VERIFIED HERE

`.github/workflows/pol-mvp-mobile.yml` is present and contains:
1. Node 20
2. `npm ci`
3. mobile typecheck
4. Expo config validation
5. Android export

`.github/workflows/pol-verification.yml` is present and provisions PostgreSQL 18, applies the migration chain and runs the verification suite.

The audit does not claim either workflow is currently green because current status checks are not available from the repository status for the current HEAD.

### H. Migration chain — PRESENT

The repository contains migrations 001 through 031, including delivery exceptions at 031.

The canonical PostgreSQL 18 direction is consistent with the active architecture documents.

### I. Governance/documentation corrections performed

During this stage:
- stale tool-specific wording in G-002 was replaced with tool-neutral historical-reference language;
- mobile barcode parity was aligned with the current API map;
- mobile CI evidence requirements were made explicit in the parity record.

## File-level status matrix

| Area | Canonical evidence | Audit status | Action |
|---|---|---|---|
| Backend transport | `scripts/api/main.py` | PASS | none |
| Application boundary | `scripts/application_boundary.py` | PASS | none |
| Checkout/idempotency | `scripts/checkout_gateway.py` | PASS structurally | live replay test remains |
| Basket API | `scripts/api/routes/baskets.py` | PASS structurally | live E2E remains |
| Catalog API | `scripts/api/routes/catalog.py` | PASS structurally | live E2E remains |
| Order API | `scripts/api/routes/orders.py` | PASS structurally | live lifecycle remains |
| Web | `mvp/apps/web/**` | IMPLEMENTED / historical evidence | fresh regression |
| Mobile | `mvp/apps/mobile/**` | IMPLEMENTED | current CI + QA |
| Mobile Night | `theme.ts` + parity | PARTIAL | visual QA |
| Barcode | API Map + parity | GAP / CONTRACT | authoritative contract/runtime |
| Vendor Customers | G-009 | GAP | authoritative API |
| Vendor Staff | G-010 | GAP | authoritative API |
| CI | two workflows | PRESENT / unverified | current run |
| Migrations | `migrations/001…031` | PRESENT | fresh migration test |

## Stage 2 decision

**PASS / DONE**

The repository implementation structure is materially aligned with the canonical architecture. The remaining work is primarily executable verification and explicitly documented contract gaps, not a missing foundational backend/web/mobile codebase.

### Next stage

**Stage 3 — Build/Verification Execution:** run or trigger the current mobile and global verification gates, then fix actual failures rather than relying on historical evidence.
