# POL-2.3 Integration Execution Status

**Date:** 2026-11-19
**Baseline main:** `fbcdd7448d809a3281cc1ea8c43218d42e8762ca`
**Working branch:** `integration/pol-2.3-mainline-consolidation-2026-11`
**Historical first verification SHA:** `4994f9d0f656e27d41d84c426cf162b8aa1944c2`
**Current state:** `LOCAL SOURCE VERIFICATION RECORDED ON bfb28cef — MERGE BLOCKED BY CI BILLING / REQUIRED-CHECK / REVIEW GATES; QA APK, STAGING AND RELEASE ALSO BLOCKED SEPARATELY`

## Current remote state refresh — 2026-11-19

- Main baseline remains `fbcdd7448d809a3281cc1ea8c43218d42e8762ca`.
- At the start of this final CI recheck, PR #53 / Integration was `e772950d8da1b47561d8554cbbeb5fcf0adbd7db`; the complete local suite evidence is on source SHA `bfb28cefdb2bb13319d8508c8481911cb373fced`.
- GitHub compare confirmed `e772950d` is nine commits after `bfb28cef` and changes 11 documentation/inventory/control or tracked-artifact paths; no application/runtime source changed. L1–L16 therefore support the unchanged application source, but were not rerun on the documentation descendant.
- The remote branch `fix/web-refresh-session-preserve-20261030` advanced from `b4a48801` to `d5ab26bb`. The earlier auth-refresh fix is byte-identical in Integration. The new checkpoint adds six dated REA run-evidence files absent from Integration; Expo `ios`/ `android` script values match Integration. The branch is retained as ARCHIVE_ONLY; these historical reports are not merged or treated as current runtime certification.
- PR #53 remains OPEN/DRAFT/UNMERGED. No merge or force-push was performed.
- A live branch metadata read on 2026-11-19 confirmed `main.protected=false`, `protection.enabled=false`, and required-check enforcement `off`; the branch-protection endpoint itself returned 403 through connected access. Owner/admin action is required to configure it.
- The four local verification lanes remain LOCAL evidence only. CI is still blocked before runner allocation by account billing; no APK/device, staging or release certification is inferred.

### Latest four workflow runs on `e772950d`

- 44558971678 (Independent Verification), 44558971582 (Mobile), 44558971752 (Static), 44558971716 (Browser E2E) all concluded `failure`.
- Raw Jobs API for every non-skipped job reported `runner_id=0`, empty runner name, and `steps=[]`; they completed within approximately 1–2 seconds. The Android matrix job 135682706494 was `skipped`.
- No runner executed a test. Earlier runs on `bfb28cef` carry the explicit account billing/spending-limit annotation. The latest failures are consistent with the same infrastructure blocker, not code-test failures.

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

## OTP policy dispositions — amended 2026-11-24 (D-018 + D-029)

- D-018 was explicitly superseded by the founder on 2026-11-24: authentication/login and registration OTP is now **six ASCII numeric digits**. The existing 120s TTL, 60s resend interval, 3/5min phone+IP rate limit, 5 attempts, 10min phone lockout, 15-minute access JWT and 30-day refresh session remain unchanged. Refresh-token rotation remains undecided.
- D-029 separately governs newly issued delivery/POD OTPs: exactly six digits, cryptographically secure, recipient-only INBOX outbox event, single-use and separate delivery expiry/attempt handling. D-018 login throttling/expiry semantics are not implicitly copied to delivery.
- Migration 077 is re-authored on the current mainline. It backfills delivery_otp_length from already stored values and does not rotate, clear or re-send any in-flight delivery OTP. Previously issued four-digit delivery codes remain usable only for their original deliveries until terminal completion; all new codes are six digits.
- PR #49 and #50 remain **closed and are not to be merged wholesale**. Their former policy objection has been superseded by the explicit founder amendment, but their old tips are stale (5–16 commits ahead and 200+ behind at audit) and the earlier migration/QA concerns require a clean current-main implementation and fresh evidence. The new selective port is tracked in feat/six-digit-otp-and-social-impact-readme-20261124.
- Refresh-token rotation stays described as current implementation behavior only, per the existing D-018 governance note.

## PR dispositions (final actions, 2026-11-19)

| PR | Final action | Basis |
|---|---|---|
| #53 | Keep Draft; merge candidate after CI restored | L1–L16 locally PASS on source SHA `bfb28cef`; reviewed descendant `b8c80bce` is docs/artifact-only; CI-on-latest-PR-head still unverified and billing-blocked |
| #49 | CLOSED (historical branch not to be merged wholesale) | Original policy objection superseded 2026-11-24; clean implementation is being re-authored on current main |
| #50 | CLOSED (historical branch not to be merged wholesale) | Original policy objection superseded 2026-11-24; legacy delivery-code rotation concerns require the new safe migration |
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


## Post-merge OTP implementation status — 2026-11-25

PR #59 (`feat(auth): standardize six-digit OTP and expand English project README`) is **MERGED** into `main` as `f9eca328b053dfacfe4c42c81c1c9c468fb8b607`.

The exact tested PR head was `dbf0a2284e4f16d0cc1e7568b78e81e11c5352a6`:
- Independent backend verification and PostgreSQL 18 migration chain 001–077: **852 passed, 0 failed, 0 skipped** (four warnings), run [45488346802](https://github.com/rrasi90/POL-2.3/actions/runs/45488346802).
- Browser E2E / Playwright: **41 passed**, run [45488346616](https://github.com/rrasi90/POL-2.3/actions/runs/45488346616).
- Mobile verification: **17/17 Expo/mobile steps** and TODO-084 eligibility gate PASS, run [45488346626](https://github.com/rrasi90/POL-2.3/actions/runs/45488346626). Android APK matrix build remained skipped; no device install is claimed.
- Remediation Static Gate: **11/11 passed**, run [45488346621](https://github.com/rrasi90/POL-2.3/actions/runs/45488346621).

D-018 and D-029 now specify six-digit new authentication and delivery OTPs. Migration 077 preserves already-issued four-digit delivery codes only for their original in-flight delivery until terminal completion. The two original OTP branches and PRs #49/#50 remain closed/unmerged because their old heads are stale; they were not imported wholesale.

This records merge and CI readiness for the OTP change only. Production/release acceptance still requires on-device visual/accessibility evidence, live SMS provider acceptance, security review, staging and owner sign-off.
