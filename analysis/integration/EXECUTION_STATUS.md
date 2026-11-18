# POL-2.3 Integration Execution Status

**Date:** 2026-11-18  
**Baseline main:** `fbcdd7448d809a3281cc1ea8c43218d42e8762ca`  
**Working branch:** `integration/pol-2.3-mainline-consolidation-2026-11`  
**Last CI-verified code head:** `4ddaccddc0e25722fac3a835243038a75aacd6d7`  
**Current branch head after follow-up code commits:** `0ed3589c2e20023ae7c1b33842fa7f770f9930a5`  
**State:** `IN PROGRESS — NOT MERGE READY`

## Current integration contents

The integration branch is 88 commits ahead of main and 0 behind. This is a consolidation branch; the 88 commits are not equivalent to 88 independently reviewed source-PR commits.

### Product, governance and documentation
- Ported the D-014 multi-vendor MVP correction from #44.
- Ported selected source-of-truth, API-map and historical-CI corrections from #42.
- Ported only Expo native run scripts from #45 while retaining Expo `~57.0.31` and React `19.2.3` from merged #46.
- Added integration audit/selection/status documents.
- Archived the selected historical evidence from #47 with explicit historical/non-certification labelling.

### Application changes selectively ported
- Mobile motion modules and screen integrations based on #40, retaining #43's stronger current-main TODO-084 fail-closed gate. After exact comparison with #29, also ported #40's unique OfflineBanner SlideIn integration and the x86 QA builder's call to the existing pre-APK QA gate; #29's latest ErrorShake interruption fix is already present, while its older OrderProgress mapping was superseded by the shared lifecycle helper.
- Retailer mock transport, status/progress helpers, notification preference model and selected UI fixes from #52.
- Admin route de-duplication and route-registration uniqueness test from #52.
- Support case message-history endpoint with tenant-bound service path and tests from #51.
- Web refresh-session preservation, responsive viewport metadata and accessibility test fixes.
- Selected Cartona extraction research artifacts from #51, including explicit provenance and observation limits.

### Deliberate exclusions / unresolved reviews
- #29 still needs a complete unique-diff comparison against #40 and current main; no wholesale merge.
- #47's remaining unique security, API/UI traceability and test changes still require file-level review. Historical evidence is not current certification.
- #49/#50 six-digit OTP policy and migration 077 remain blocked. Current D-018 four-digit policy is preserved; no implicit policy change or migration 077 port.
- #51 Cartona artifacts are not a claim of runtime-observed UI. The source audit says 21 retailer screens are STATIC_INFERRED, with no runtime screenshots; supplier/driver coverage is public-listing evidence only. Remaining extraction artifacts and rights/provenance review are still open.
- #52's full privacy lifecycle and role authorization behavior need deeper verification beyond route registration and mock QA.

## CI evidence on exact verified head

GitHub Actions runs associated with `4ddaccddc0e25722fac3a835243038a75aacd6d7`:

| Workflow | Result | Interpretation |
|---|---|---|
| POL Remediation Static Gate (run 44171987024) | Success | Python compilation, route invariants, admin route uniqueness and UI audit regression guards passed |
| POL MVP Mobile Verification (run 44171987123) | Success | Expo typecheck, state-transition QA, regression QA, vendor mock QA, Expo config/export and TODO-084 gate passed; Android APK jobs were skipped by the fail-closed gate |
| POL Browser E2E (TODO-006) (run 44171986906) | Workflow conclusion failure | Typecheck, DB migration/fixture seed and Playwright suite steps passed; Playwright report upload failed |
| POL Independent Verification & Schema Hardening (run 44171987049) | Workflow conclusion failure | Migration chain, bootstrap verifier, full verification suite and failure-inventory/verdict steps passed; evidence artifact upload failed |

The two failed workflow conclusions are artifact-upload failures after their substantive test steps completed successfully. They must not be represented as fully green workflows. The exact test count is not stated here because the current run's test summary was not independently retrieved in this audit.

## Remaining acceptance gates

1. Finish the remaining #29/#40 diff reconciliation (including older non-overlapping history) and inspect all imported motion behavior for reduced-motion, cleanup, interruption, RTL and runtime correctness. The latest #29-only ErrorShake fix is already present; the #29 OrderProgress implementation was not copied because its direct ARRIVED-to-delivered mapping conflicts with the newer shared lifecycle mapping.
2. Complete #47 file-level salvage and refresh all source-backed security/traceability claims.
3. Resolve or formally defer #49/#50 policy/security work; keep migration 077 excluded until challenge lifecycle, recipient-only dispatch, backfill/rollback and PostgreSQL 18 compatibility are demonstrated.
4. Finish #51 Cartona artifact inventory, provenance/rights review and remaining source-backed extraction review. Never upgrade STATIC_INFERRED to RUNTIME_OBSERVED without real captures.
5. Complete #52 authorization/privacy lifecycle review and regression tests.
6. Re-run required workflows after any further commit and obtain successful artifact uploads or document the infrastructure limitation separately.
7. Review current PR body/audit documents for consistency and only then consider Ready-for-review.

## Latest unverified changes after the CI checkpoint\n\nTwo additional commits were added after the CI checkpoint: `OfflineBanner.tsx` now uses the shared `SlideIn` primitive, and `build_qa_x86.mjs` now validates the retailer/vendor argument and invokes `pre_apk_qa.mjs` with QA-only environment flags before building. These changes have **not** yet been tested on the new branch head. The prior CI table applies only to `4ddaccddc0e25722fac3a835243038a75aacd6d7`.\n\n## Merge policy

PR #53 remains Draft. Do not merge to main while any acceptance gate above is open. Do not describe the integration as complete or certified. All test claims must remain attached to the exact SHA and workflow run that produced them.
