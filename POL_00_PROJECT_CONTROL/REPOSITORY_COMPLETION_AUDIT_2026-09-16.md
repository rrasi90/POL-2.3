# POL Repository Completion Audit — 2026-09-16

**Status:** ACTIVE AUDIT RECORD  
**Branch:** `research-hardening-2026-09-14`  
**Scope:** repository-wide governance, data, application boundary, security, operational domain, tests, generated-artifact hygiene and design-readiness dependencies.  

## Executive result

The repository already contains the majority of the product/domain specification required for the next design phase. The audit confirmed that the principal remaining pre-design work was **specification consistency and integrity hardening**, not product discovery.

Concrete issues found during this pass were repaired in the branch. The current repository must still pass CI on the latest HEAD before the Design Completion gate is declared closed.

## Areas reviewed

- `00_PROJECT_OVERVIEW` through `13_PRODUCT_DESIGN`
- `POL_00_PROJECT_CONTROL`
- PostgreSQL migration chain
- application-boundary services and operational policies
- verification and regression tests
- GitHub Actions verification workflow
- research outputs and generated-artifact hygiene
- current product/design decision registers
- canonical user profile/persona model
- multi-vendor basket/order/allocation architecture

## Findings and repairs

### R-01 — Governance path drift — FIXED

Several D-001–D-017 references pointed to paths that no longer existed after repository restructuring.

**Repair:** `DECISION_REGISTER.md` was reconciled to the actual repository paths and the 2026-09-16 audit date.

### R-02 — Schema manifest was stale — FIXED

The old manifest described the earlier 56-table baseline and stopped at migration 003 while the repository had evolved substantially.

**Repair:** created `DATABASE_SCHEMA_MANIFEST_2026-09-16.md`, updated governance to use it, and marked the old manifest historical/superseded. At the 2026-09-18 Stage 01 baseline, the physical migration chain extends through 028 and the CI-built PostgreSQL 18.6 public-table baseline is 93.

### R-03 — Canonical role/status terminology drift — FIXED VIA CORRECTION OVERLAY

The contract matrix contained legacy role vocabulary and basket states that could be mistaken for current canonical values.

**Repair:** added `CANONICAL_CONTRACT_MATRIX_CORRECTIONS_2026-09-16.md` as an explicit canonical correction overlay. Canonical roles remain `ADMIN_SUPER`, `OPS_AGENT`, retailer/vendor roles, and field activator; `SUPER_ADMIN`/`OPS_ADMIN` are legacy aliases only. Current basket statuses are those enforced by the database/application contract.

### R-04 — Frontend framework documentation conflict — FIXED

Design decision UX-013 previously left the frontend framework open despite the approved technical architecture specifying Next.js/React and React Native/Expo.

**Repair:** UX-013 now aligns with the approved technical architecture. Framework/version replacement requires a separate architecture decision.

### R-05 — Generated local artifacts tracked in Git — FIXED

Tracked scratch prompts, generated test JSON and a large collection of `research/runs/*/temp/*` files were repository hygiene problems and could mislead agents into treating transient outputs as source material.

**Repair:** removed the tracked scratch/test/temp artifacts and strengthened `.gitignore`.

### R-06 — Overnight vendor operating windows contradicted runtime policy — FIXED

The application policy explicitly handled cross-midnight operating windows while the database constraint rejected them.

**Repair:** migration 020 changes the constraint to permit overnight windows and adds temporal exclusion constraints preventing overlapping effective windows/capacity configurations.

### R-07 — Temporal capacity/window overlap was under-constrained — FIXED

Effective-dated operational configurations could overlap and make the current configuration nondeterministic.

**Repair:** migration 020 adds PostgreSQL GiST exclusion constraints for operating windows and capacity profiles.

### R-08 — Saved-list and consent uniqueness gaps — FIXED

PostgreSQL NULL semantics permitted multiple active global consents, and multiple default saved lists could be created for one retailer.

**Repair:** migration 020 adds partial unique indexes.

### R-09 — RMA refund state was not fully database-enforced — FIXED

Service-level validation required positive refund amounts for refund states, but direct database writes were not equally constrained.

**Repair:** migration 020 adds the database invariant.

### R-10 — Checkout aggregate relationship could be forged — FIXED

The canonical revalidation path needed an explicit guarantee that the allocation plan belonged to the basket being checked out.

**Repair:** standalone canonical revalidation service plus migration 021 trigger enforcing `OrderGroup.basket_id == AllocationPlan.basket_id` and retailer consistency.

### R-11 — Session tenant binding needed database protection — FIXED

The session context required a database-level guarantee that the active organization is an active membership of the session user.

**Repair:** migration 021 adds `trg_validate_session_context`.

### R-12 — Child-order tenant/vendor relationship needed database protection — FIXED

A forged child order could otherwise rely too heavily on application-layer checks.

**Repair:** migration 021 validates child-order retailer against its order group and requires an active vendor organization.

### R-13 — Support/feedback tenant ownership needed database protection — FIXED

Canonical services checked tenant context, but the database did not independently enforce actor-to-tenant ownership.

**Repair:** migration 022 adds support-case and feedback tenant triggers.

### R-14 — Canonical checkout depended on legacy module — FIXED

`checkout_gateway.py` imported the revalidation class from the large legacy `domain_services.py` module.

**Repair:** created `scripts/revalidation_checkout.py` as the canonical transactional checkout service and changed the application-facing gateway to use it directly. The old domain-services implementation remains legacy/historical and must not be exposed as a client-facing route.

### R-15 — Verification baseline was too low — FIXED

Environment verification used a minimum table count that no longer represented the current schema.

**Repair:** verification baseline raised to 90 tables and profile/persona cardinality checks retained.

### R-16 — Design workstream index was incomplete — FIXED

`13_PRODUCT_DESIGN/README.md` did not list the Penpot blueprint, completion plan and Antigravity audit prompt.

**Repair:** design index updated to include all current design-governance artifacts and the repository-audit-first execution sequence.

## Regression coverage added

- `scripts/test_repository_integrity_hardening.py`
- migration-chain integrity remains covered by existing PostgreSQL verification tests
- profile/persona, referral, RMA, reconciliation, notification, allocation and tenant-isolation suites remain part of the verification harness

## Remaining production-applicationization gates

These are **not hidden by this audit** and are intentionally separate from repository/domain correctness:

1. Concrete production HTTP/API runtime is not yet implemented.
2. Production authentication/OTP provider, refresh-token rotation, rate limiting, secret management and session revocation infrastructure are not yet certified.
3. Live SMS/push provider integration and credential certification are not complete.
4. Actual production client UI is not implemented; the current design workstream is specification/prototype stage.
5. Production observability, deployment topology and alerting are not complete.
6. Backup/restore/PITR and migration operations are not production-certified.
7. Legacy `domain_services.py` remains in the repository for compatibility/testing; new client-facing code must not import it directly.

## Design gate

The repository is **structurally ready to enter the Design Completion phase after current-head CI passes**. The next phase must still complete the documented design specification gaps identified by `13_PRODUCT_DESIGN/15_CROSS_PROJECT_DESIGN_AUDIT_2026-09-15.md`, especially Auth/Session, commerce state matrices, RMA/Support, Notifications, localization and telemetry.

This document does not certify the product as production-ready.


## Stage 01 — 2026-09-18 baseline amendment
- Current PR #1 head: `e6484daf9f0926b807577c71477d8f1405c24a3e`.
- Latest completed CI run observed on that head: **Run #333 — FAILED**.
- CI environment/bootstrap step: successful; PostgreSQL 18.6; **93 public base tables**.
- Verification suite: 209 collected, 170 passed, 39 failed, 0 skipped.
- Failed families: Batch 2 RMA/outbox, Batch 3 contract matrix, E2E MVP platform, vendor acceptance timeout.
- This amendment supersedes this document's older 022/90 schema-currentness claim. The document remains an active audit record, not a production-readiness certification.
