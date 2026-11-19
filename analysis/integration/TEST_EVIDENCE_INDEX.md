# POL-2.3 Test Evidence Index

**Generated:** 2026-11-19 (UTC times as recorded)
**Exact tested source SHA:** `bfb28cefdb2bb13319d8508c8481911cb373fced` (local execution of L1–L16, 2026-11-19)
**PR #53 descendant reviewed:** `b8c80bcec8d76d23a37321ffff7f1a68f0663c49` (one docs/artifact-only commit after the tested source SHA; no application/runtime source files changed)
**Rule:** every claim below names its exact SHA, environment, command and result. Historical results attached to other SHAs are listed as leads only, never as current certification.

## Evidence classes used in this repository

| Class | Meaning | Current status |
|---|---|---|
| LOCAL | Run on the maintainer's Windows x64 machine, isolated `pol_test` PostgreSQL | Available (this index) |
| CI | GitHub Actions run with a real runner (`runner_id != 0`, steps executed) | **BLOCKED — account billing** |
| DEVICE | Installed APK on emulator/real device | **BLOCKED — TODO-084 fail-closed gate** |
| STAGING | Restricted VPS/staging smoke on exact SHA | Not executed this session |
| LIVE-PROVIDER | Real SMS.ir / object storage / public domain TLS | Not attempted (requires owner credentials) |

## LOCAL evidence — exact source SHA `bfb28cef` (2026-11-19)

The PR head `b8c80bce` is a direct child of this tested SHA. The commit comparison contains nine documentation/inventory/control files plus the tracked test-result artifact; it contains no application/runtime source changes. The results below therefore support the unchanged application source in that descendant, but must not be described as a fresh test run on `b8c80bce`.

Environment: Windows 10.0.26200 x64, Git Bash; Python 3.11.15 (venv); Node v24.18.0; npm clean installs under `mvp/` workspaces; PostgreSQL **18.4** local (`127.0.0.1:5432`, trust auth) — *not* the CI's 18.6; isolated database `pol_test`; `ENVIRONMENT=test`; non-production `POL_JWT_SECRET`; `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001` for E2E. Source tree identical to `bfb28cef` except the regenerated evidence artifact and new docs-only inventory files (recorded by the artifact metadata as `is_dirty: true` with those paths).

| # | Lane | Command (cwd) | Result | Notes |
|---|---|---|---|---|
| L1 | Migration chain | `python scripts/migration_runner.py` (repo root) | 76/76 migrations applied, 107 active tables, exit 0 | chain 001→076 |
| L2 | Environment verifier | `python scripts/verify_environment.py --json` | all checks passed, PG 18 detected, 107/107 tables, trigger verified | |
| L3 | **Backend suite** | `python scripts/run_verification_suite.py` (repo root) | **849 passed / 0 failed / 0 skipped, exit 0, 388.0s** | artifact `artifacts/pol-test-results.json` metadata records `commit=bfb28cef`, summary `PASSED`; artifact is tracked by repo convention (see §Artifact below) |
| L4 | Static compile | `python -m compileall -q scripts` | exit 0 | |
| L5 | Route hygiene | `python scripts/test_api_route_hygiene.py` (`PYTHONPATH=.`) | PASS | |
| L6 | Admin route uniqueness | `python scripts/test_admin_route_registration_uniqueness.py` | PASS (one guarded registration) | |
| L7 | UI audit regression guards | `python scripts/ui_audit_regression_guards.py` | 15/15 PASS | |
| L8 | Web typecheck | `npm run typecheck` (`mvp/apps/web`) | 0 errors, exit 0 | |
| L9 | Web production build | `scripts/test_web_build_verification.py::test_next_build_exits_zero` | `next build` exit 0, no hydration errors | run 2026-11-19, same tree family |
| L10 | **Browser E2E** | `npx playwright test` (`mvp/apps/web`) | **41 passed / 0 failed, exit 0, 46.3s** | chromium, fa-IR locale, real API+web servers via `e2e_serve.py`, includes cross-persona delivery flow with outbox OTP |
| L11 | Mobile typecheck | `npm run typecheck` (`mvp/apps/mobile`) | 0 errors, exit 0 | |
| L12 | Mobile functional QA | `npm run qa:functional` | 28/28 PASS | |
| L13 | Mobile regression QA | `npm run qa:regression` | 23/23 PASS | |
| L14 | Mobile mock QA | `npm run qa:mock` | PASS (vendor + retailer transports) | |
| L15 | Pre-APK QA (CI mode) | `POL_RELEASE=0 npm run qa:pre-apk` | PASS, exit 0 | matches workflow env |
| L16 | TODO-084 gate | `node scripts/check_prebuild_todo_gate.mjs` | `BLOCKED` (fail-closed as designed) | no APK built or claimed |

### Prior LOCAL evidence (SHA-scoped leads, not current certification)

| SHA | What was reported | Scope limit |
|---|---|---|
| `4994f9d0` | 849/849 backend, static gate, 41/41 E2E, mobile suites (previous session) | Artifact metadata recorded `a96d66cd@dirty` (salvage uncommitted at run time); superseded by L1–L16 on `bfb28cef` |
| `58360a5` | 663/663 backend, TODO-061…068/018/019 evidence (2026-10-22, journal) | Older ledger and schema head |
| `1c793b53` | 663/663 backend, 17/17 E2E, mobile 28/28+38/38 (PR #40 CI-era) | Historical CI on pre-consolidation code |

## CI evidence — BLOCKED (account billing)

Runs on `bfb28cef` (2026-11-18T20:56Z): 44396293442 (Mobile), 44396293373 (Static), 44396293335 (Verification), 44396293121 (E2E).

Job metadata (GitHub API `actions/runs/{id}/jobs`): **every job has `runner_id=0`, `runner_name=""`, `steps=0`** — no runner was ever allocated, no step executed. All four runs carry the annotation:

> "The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings"

Additional context: repository is private; `GET /actions/runners` → `total_count: 0` (no self-hosted runners). The last recorded repository state showed `main.protected=false` and required status checks disabled; the branch-protection API returned 403 through the connected access, so no protection change was made. The commit-status query for the subsequently reviewed PR head `b8c80bce` returned no successful statuses; do not infer CI success from the local matrix. Also observed on scheduled run 44285920916 (main) and the 2026-11-18 PR #53 runs 44280222841/22836/22830/22842.

**Conclusion:** pre-start account/infrastructure blocker, not a test failure. Owner actions: restore Actions billing/spending allowance, or attach a properly secured self-hosted runner. No workflow change can resolve it and none was made.

## Artifact provenance note (`artifacts/pol-test-results.json`)

- The file is **tracked** in version control (first tracked in `9d3345b5`, refreshed by `32690b8`; present in `git ls-files` despite `.gitignore:30` listing `artifacts/` — tracked files override ignore rules).
- `bfb28cef` therefore correctly modified it (849/849 run output), and the commit message's "gitignored/local-only" wording was wrong; corrected in the TODO journal 2026-11-19 entry (append-only; history not rewritten).
- Content audit: schema `{metadata, summary, tests}`; no credentials, IPs, tokens or customer data (all policy-word matches are test node IDs); metadata records commit, branch, dirty flag, Python/PostgreSQL versions.
- Repository convention is to keep the tracked artifact refreshed by suite runs; the alternative (CI-uploaded artifact only) is preferable long-term but requires CI to be unblocked.

## What is NOT evidenced

- No successful CI-step execution on the reviewed 2026-11-19 PR candidate; the inspected pre-start-blocked runs were on source SHA `bfb28cef`. The later `b8c80bce` docs/artifact descendant had no successful status reported by the connected status query.
- No QA APK build/install/device verification (TODO-084 fail-closed).
- No staging/VPS smoke, no live SMS.ir, no object storage, no public TLS, no release build.
- No refresh-token-rotation policy approval (D-018 remains explicitly undecided).
