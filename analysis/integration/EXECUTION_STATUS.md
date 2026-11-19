# POL-2.3 Integration Execution Status

**Date:** 2026-11-19
**Baseline main:** `fbcdd7448d809a3281cc1ea8c43218d42e8762ca`
**Working branch:** `integration/pol-2.3-mainline-consolidation-2026-11`
**Historical first verification SHA:** `4994f9d0f656e27d41d84c426cf162b8aa1944c2`
**Current state:** `LOCAL SOURCE VERIFICATION RECORDED ON bfb28cef — MERGE BLOCKED BY CI BILLING / REQUIRED-CHECK / REVIEW GATES; QA APK, STAGING AND RELEASE ALSO BLOCKED SEPARATELY`

## Current remote state refresh — 2026-11-19

- Main baseline remains `fbcdd7448d809a3281cc1ea8c43218d42e8762ca`.
- At the start of this documentation reconciliation, PR #53 / Integration was `b8c80bcec8d76d23a37321ffff7f1a68f0663c49`; the complete local suite evidence is on source SHA `bfb28cefdb2bb13319d8508c8481911cb373fced`.
- GitHub compare confirmed `b8c80bce` is one commit after `bfb28cef` and changes only nine documentation/inventory/control files plus the tracked test-result artifact; no application/runtime source changed. L1–L16 therefore apply to the unchanged application source, but were not rerun on the documentation descendant.
- The remote branch `fix/web-refresh-session-preserve-20261030` advanced from `b4a48801` to `d5ab26bb`. The earlier auth-refresh fix is byte-identical in Integration. The new checkpoint adds six dated REA run-evidence files absent from Integration; Expo `ios`/ `android` script values match Integration. The branch is retained as ARCHIVE_ONLY; these historical reports are not merged or treated as current runtime certification.
- PR #53 remains OPEN/DRAFT/UNMERGED. No merge or force-push was performed.
- The last recorded main protection observation was `main.protected=false` with required checks disabled; branch-protection API access returned 403. Owner/admin action is required to re-check and enable required checks if available.
- The four local verification lanes remain LOCAL evidence only. CI is still blocked before runner allocation by account billing; no APK/device, staging or release certification is inferred.

## Blocking infrastructure fact (root cause, not a code defect)

Every GitHub Actions run since 2026-11-18 fails **before any job starts** with:

> "The job was not started because recent account payments have failed or your
> spending limit needs to be increased. Please check the 'Billing & plans'
> section in your settings"

Verified on runs 44280222841, 44280222836, 44280222830, 44280222842 (PR #53,
SHA `09ef82ce`) and 44285920916 (scheduled Notification Retention on `main`,
SHA `fbcdd744`). The repository is private and the account has zero
self-hosted runners (`GET /repos/rrasi90/POL-2.3/actions/runners` →
`total_count: 0`). No workflow, runner-label or YAML change can repair this;
only an account billing fix (payment method / spending limit) or adding a
self-hosted runner restores CI. This is recorded as the external blocker for
the CI-on-SHA merge gate.

## Local verification evidence on exact SHA `4994f9d0`

Environment: Windows x64, Git Bash, Python 3.11.15 (venv), Node v24.18.0,
local PostgreSQL 18.4 (`127.0.0.1:5432`, trust auth), isolated `pol_test`
database. All commands executed from a dedicated worktree of the integration
branch; canonical CI-equivalent env (`POL_API_DB_NAME=pol_test`,
`POL_API_DB_HOST=127.0.0.1`, canonical non-production `POL_JWT_SECRET`,
`ENVIRONMENT=test`).

| Lane | Command | Result |
|---|---|---|
| Migration chain 001→076 | `python scripts/migration_runner.py` | 76 migrations applied, 107 active tables, exit 0 |
| Environment verifier | `python scripts/verify_environment.py --json` | all checks passed, PostgreSQL 18, 107/107 tables, trigger verified |
| **Full backend suite** | `python scripts/run_verification_suite.py` | **849 passed / 0 failed / 0 skipped**, exit 0, 343.8s, artifact `artifacts/pol-test-results.json` |
| Static gate | `compileall -q scripts`; `test_api_route_hygiene.py`; `test_admin_route_registration_uniqueness.py`; `ui_audit_regression_guards.py` | all PASS (hygiene, admin-route uniqueness, 15/15 source guards) |
| Web typecheck | `npm run typecheck` (mvp/apps/web) | exit 0 |
| Web production build | `scripts/test_web_build_verification.py::test_next_build_exits_zero` (salvaged TODO-078 guard) | next build exits 0, no hydration errors |
| **Browser E2E** | `npx playwright test` (chromium, fa-IR locale, real API+web servers via e2e_serve.py) | **41 passed / 0 failed**, exit 0, 40.5s — includes the full cross-persona delivery flow (checkout → vendor accept/prepare/dispatch → PICKED_UP/IN_TRANSIT/ARRIVED → outbox OTP → POD confirm) |
| Mobile typecheck | `npm run typecheck` (mvp/apps/mobile) | exit 0 |
| Mobile functional QA | `npm run qa:functional` | 28/28 PASS |
| Mobile regression QA | `npm run qa:regression` | 23/23 PASS |
| Mobile mock QA | `npm run qa:mock` | PASS (vendor + retailer mock transports) |
| Pre-APK QA (CI mode) | `POL_RELEASE=0 npm run qa:pre-apk` | PASS, exit 0 |
| TODO-084 prebuild gate | `node scripts/check_prebuild_todo_gate.mjs` | `BLOCKED` (fail-closed as designed; APK jobs skip) |

The backend total grew 804 → 849 between runs: 4 defects were fixed (commit
`1d50fe80`) and 45 behavioral tests were salvaged from PR #47 (commit
`4994f9d0`).

## Defects found and fixed during local verification

1. **`scripts/db_safety.py` fail-open guard** (`1d50fe80`): `resolve_target()`
   or-chained an explicitly empty `host=""` into `POL_API_DB_HOST`/`PGHOST`
   environment defaults, so `test_blocks_missing_host` silently passed the
   loopback guard. Explicit empty values now stay empty and are rejected.
2. **Stale 422 assertions for missing order/order-group** (`1d50fe80`):
   `test_get_order_not_found` / `test_order_group_not_found` still asserted
   the legacy mapping after commits `f51bb426`/`27a62f7e` canonically mapped
   missing resources to `404 NOT_FOUND` (already enforced by this branch's
   `test_http_negative_rbac_matrix.py`). Updated to 404 + envelope code.
3. **Stale stale-plan exception assertion** (`1d50fe80`):
   `test_stale_plan_version_rejected` expected `AllocationIntegrityError`
   after commit `49cf508e` mapped stale basket/plan versions to
   `ConflictError` (`STALE_BASKET_VERSION`, HTTP 409 per G-326).
4. **Stale raw-enum E2E assertion** (`a96d66cd`): the delivery-flow spec's
   vendor arrival step still asserted `وضعیت تحویل: ARRIVED` after commit
   `f864c01b` localized delivery states (`ARRIVED` → `رسیده به مقصد`);
   retailer-side assertions already used localized labels.

All four were invisible to CI because billing blocked every run after these
commits landed.

## Port verification completed (2026-11-19)

| Source | Method | Verdict |
|---|---|---|
| #44 product-vision (1 file) | byte comparison | 1/1 identical in integration branch — port complete |
| #45 Expo run scripts | content comparison | `expo run:ios`/`run:android` present; Expo `~57.0.31` deliberately retained per merged #46 — port complete with documented deviation |
| #42 source-authority reconcile | content comparison | migration-head 076, `application_boundary.py` boundary reference and historical-checkpoint re-labeling all present — port complete |
| #40/#29 motion system | file existence + content + mobile QA suites | all 21 motion files present (INT adds SplashSequence/SuccessCheck/SlideIn), functional 28/28 + regression 23/23 + typecheck green — port complete |
| #47 journey evidence | content comparison + empirical salvage | core ports present (observability, provider-contract, schema-fuzz, reservation-expiry isolation, POD media keys, archived matrices); 3 behavioral test files salvaged 2026-11-19 (below) |
| #51/#52 wave 1 (UI, route hygiene, mock QA) | content comparison + E2E | admin route de-dup + uniqueness gate, runtime inventory correction, retailer mock transport, field/status localization all present; `b4a48801` web-refresh tip is **byte-identical** in this branch; screenshot bulk deliberately excluded (captured against the six-digit branch UI before the i18n wave — stale evidence) |
| `fix/web-refresh-session-preserve-20261030` (no PR) | commit isolation | = OTP chain + ported wave-1 + Cartona phase-2 research + tip fix byte-identical in INT → superseded |
| `research/cartona-uiux-extraction-phase2-20261027` (no PR) | ancestry | contained in the web-refresh chain; INT preserved its own Cartona evidence set with provenance → superseded |
| `agent/pol-2.3-integration-fdx` (no PR) | content comparison | `expo run:` scripts already present; journal entries historical → superseded |
| `agent/pol-2.4-execution-20261006` (#28, merged) | file existence | `build_qa_x86.mjs` present → port complete |
| `fix/web-basket-sync-reuse` (#35, merged), `docs/pol-prebuild-checklist-mainbase` (#34, merged) | ancestry/patch | content in main → obsolete |

## Salvage record (commit `4994f9d0`)

- Ported from #47 with provenance headers, all green on this branch:
  `scripts/test_owasp_api_top10.py` (TODO-131), `scripts/test_resource_limits.py`
  (TODO-132; doc-sync test dropped — `RESOURCE_LIMITS.md` was archived as dated
  evidence), `scripts/test_web_build_verification.py` (TODO-078).
- Deliberately NOT ported from #47: `test_owasp_matrix_doc.py` and
  `test_screen_parity.py` (assert live sync of deliberately archived docs or a
  regenerated `SCREEN_TEST_PARITY.md`; shipping them red would violate
  fail-closed gate discipline). Screen-parity restoration remains TODO-080/TODO-085…136 work; the failing parity details are enumerated in the salvage commit message and journal entry.
- Ported from closed PRs #18/#22 (deploy branch, infra already merged via #25)
  as dated evidence for the still-open TODO-029 staging lane:
  `deploy/VPS_DEPLOYMENT.md`, `deploy/VPS_DEPLOYMENT_AGENT.md`,
  `deploy/VPS_RUNTIME_VERIFICATION_2026-09-28.md`.
- HOLD (documented, not ported): `vercel-qa` branch Vercel-QA proxy
  (`api/v1/[...path]/route.ts`, `pol-vercel-qa.yml`,
  `VERCEL_QA_TRANSFER_MANIFEST.md`) — TODO-025 requires an external Vercel QA
  environment that cannot be verified here; porting would need rework against
  the current `NEXT_PUBLIC_API_BASE_URL` architecture. Not policy-conflicting;
  parked for the TODO-025 owner.
- `ui/retailer-reference-match-20261005` (closed #21): screen styling predates
  the motion/i18n rewrite of the same files; superseded by the later design
  work tracked in merged #48.

## OTP policy dispositions (D-018)

- D-018 remains canonical: **4-digit auth OTP**, 120s TTL, 60s resend,
  3/5min phone+IP rate limit, 5 attempts, 10min lockout, 15-min access token,
  30-day refresh session, rotation explicitly undecided.
- PR #49 and #50 introduce six-digit auth OTP, migration `077`, and
  D-018-register rewrites → **reject and close**; no salvageable
  policy-independent content was found (their E2E helpers hardcode
  `OTP="123456"` and are already superseded by INT's four-digit versions).
- Delivery OTP remains a separate domain concern; no delivery-OTP policy is
  inferred from D-018 anywhere in this consolidation.
- Refresh-token rotation stays described as current implementation behavior
  only, per the 2026-09-18 governance note.

## PR dispositions (final actions, 2026-11-19)

| PR | Final action | Basis |
|---|---|---|
| #53 | Keep Draft; merge candidate after CI restored | L1–L16 locally PASS on source SHA `bfb28cef`; reviewed descendant `b8c80bce` is docs/artifact-only; CI-on-latest-PR-head still unverified and billing-blocked |
| #49 | CLOSE_AS_SUPERSEDED (policy-conflicting) | Six-digit auth OTP contradicts locked D-018; migration 077 rejected |
| #50 | CLOSE_AS_SUPERSEDED (policy-conflicting) | Same as #49 |
| #51 | CLOSE_AS_SUPERSEDED (salvaged into #53) | Route hygiene/mock QA/support endpoint ported; screenshot bulk stale against post-i18n UI |
| #52 | CLOSE_AS_SUPERSEDED (salvaged into #53) | Same; wave-1 content verified present in #53 |
| #47 | CLOSE_AS_SUPERSEDED (salvaged into #53) | Core ports verified + 3 behavioral suites salvaged; doc-sync modules deliberately deferred |
| #40 | CLOSE_AS_SUPERSEDED (ported into #53) | Motion port complete and verified by mobile QA suites |
| #29 | CLOSE_AS_SUPERSEDED (ported into #53) | Superseded by #40's stronger port; unique fixes verified present |
| #45 | CLOSE_AS_SUPERSEDED (ported into #53) | Run scripts present; Expo version deviation documented |
| #44 | CLOSE_AS_SUPERSEDED (ported into #53) | Byte-identical in #53 |
| #42 | CLOSE_AS_SUPERSEDED (ported into #53) | Content verified present |
| #31/#32/#33 | Remain CLOSED (superseded) | Superseded by merged #34 + INT's checklist reconciliation |
| #4, #9, #18, #19, #21, #22 | Remain CLOSED (superseded) | Content evolved beyond; VPS docs salvaged from #18/#22 |

## Remaining acceptance gates

1. **CI restoration (external):** fix account billing or attach a self-hosted
   runner, then re-run all four workflows on the exact merge-candidate SHA and
   require green runs with successful artifact uploads.
2. Merge `main` ← PR #53 only after (1) passes; the merge commit must record
   the CI run IDs that validated the exact pre-merge SHA.
3. Device QA lane (TODO-018…024 chain) stays BLOCKED on the TODO-084
   fail-closed gate and a real Android runtime — unchanged by this
   consolidation by design.
4. TODO-025 Vercel QA lane requires the parked `vercel-qa` work to be reworked
   by its owner against current web architecture.
5. Screen/API parity restoration (TODO-080) requires regenerating
   `MVP_SCREEN_MATRIX.md` entries for `/admin` and `/dev/components` and
   resolving the 12 VERIFIED-without-browser-test rows.

## Merge policy

PR #53 remains Draft until the CI gate passes on the exact merge-candidate
SHA. This document's local evidence is local evidence only: it does not
substitute for CI-on-SHA, device, staging or live-provider certification.
