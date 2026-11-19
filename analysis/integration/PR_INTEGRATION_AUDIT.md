# POL-2.3 PR Integration Audit

**Audit date:** 2026-11-17  
**Main baseline:** `fbcdd7448d809a3281cc1ea8c43218d42e8762ca`  
**Integration branch:** `integration/pol-2.3-mainline-consolidation-2026-11`

> This is a live metadata/source audit, not a full local build or runtime certification. The repository is private and the current execution environment could not resolve `github.com` for a direct clone. GitHub API reads and branch writes were available; application tests have not been run in this environment.

## Current PR inventory

| PR | Scope | Initial disposition | Evidence / reason |
|---|---|---|---|
| #29 | Earlier mobile motion and interrupted-animation work | Selective salvage; do not merge wholesale | Draft, non-mergeable/dirty on last observed metadata; overlaps 24 of 46 files with #40. Keep only unique, still-correct fixes after file-level comparison. |
| #40 | Motion system port and mobile QA artifacts | Candidate motion source; selective port | Four PR workflows were successful on its historical head `1c793b5`; it is based on October main and includes an older TODO gate. Current main already contains stronger gate from merged #43. Re-run on integration SHA. |
| #42 | Canonical source-path and historical CI documentation | Ported selectively in this integration branch | Corrections to migration head, absent source paths, and date-bounded CI language are supported by current repository tree. Audit references refreshed to current main SHA. |
| #44 | Product Vision alignment with D-014 | Ported in this integration branch | Main Decision Register and MVP Definition both say D-014 makes multi-vendor basket an MVP capability; old Product Vision contradicted them. |
| #45 | Expo run scripts | Ported selectively in this integration branch | Only `ios`/`android` scripts were copied. Expo `~57.0.24` from #45 was deliberately not copied; current main's `~57.0.31` and React alignment from merged #46 are preserved. |
| #47 | POD, API/UI traceability, security and test evidence | Selective port pending content and regression review | 65 changed files on a stacked base. Contains valuable matrices and tests but broad API/runtime edits must be diffed against post-#46 main and tested. |
| #49 | Six-digit OTP policy/documentation | Compare and extract only; do not merge separately | Competes with #50. Contains policy/decision/documentation changes, but current main still canonically records D-018 as four-digit. Any policy amendment must be made explicit and consistently updated. |
| #50 | Six-digit authentication and delivery OTP implementation | BLOCKED pending lifecycle/security review | Contains migration 077 and client/server changes. Prior independent review flagged delivery OTP storage/rotation/outbox concerns and a test that duplicates rather than imports the implementation. Historical local PASS claims conflict with failed/uninspectable PR CI. |
| #51 | Visual QA captures and Cartona extraction | Selective port pending artifact validation | 214 changed files, including screenshots, research inventories and many UI/source edits; stacked on #50. Verify image provenance, runtime validity, rights metadata and code overlap before importing. |
| #52 | Admin route hygiene, route inventory, retailer mock QA | Selective port pending exact-SHA tests | 23 changed files on top of #51. PR description itself says full backend suite, privacy lifecycle behavior test and current-head CI were not evidenced. |

## Already merged dependencies

| PR | Status | Consequence |
|---|---|---|
| #43 | Merged; merge commit `a7c99a9926c52021baf29887f274ddbf5f23c5a9` | Its stronger TODO-084 fail-closed Android QA gate is present on current main. Do not replace it with the older #40 gate. |
| #46 | Merged; merge commit/current main `fbcdd7448d809a3281cc1ea8c43218d42e8762ca` | Current mobile package uses Expo `~57.0.31` and React `19.2.3`; preserve these instead of copying older dependency pins from #45. |

## Current-main facts verified

- Default branch is `main`; repository is private and current connected GitHub permission includes push/admin.
- Current main SHA is `fbcdd7448d809a3281cc1ea8c43218d42e8762ca`.
- Current main migration files are contiguous from `001` through `076`; there are 76 numbered SQL migrations. Migration 077 is not present on main.
- `POL_00_PROJECT_CONTROL/DATABASE_SCHEMA_MANIFEST.md` also identifies migration 076 as current main head.
- `DECISION_REGISTER.md` marks D-003 historical/superseded and D-014 as the multi-vendor MVP rule.
- `MVP_Definition.md` specifies one unified multi-vendor basket in MVP.
- Current `CURRENT_SOURCE_OF_TRUTH.md` and `MVP_API_MAP.md` still contain old source-path/migration references; #42's corrections were ported and refreshed to current main's SHA.
- The stronger `check_prebuild_todo_gate.mjs` from merged #43 exists on current main.
- Main's mobile package has Expo `~57.0.31`, React `19.2.3`, and old `expo start --ios/android` scripts. Only the native run commands from #45 were ported.

## Integration status

- Completed in this branch: Product Vision D-014 correction; current source-of-truth/migration-path reconciliation; historical CI/source-path wording reconciliation; selective Expo script correction.
- Not yet ported: motion implementation (#40/#29), security and QA content (#47), OTP (#49/#50), Visual QA/Cartona (#51), Wave 1 retailer/admin changes (#52).
- Not merged to main. No application test/build has been run on this branch in this environment.
- The integration must remain a draft until the remaining workstreams are ported, code-reviewed and tested on the exact resulting SHA.

## Evidence limitation

A direct `git clone` attempt failed because this execution environment could not resolve `github.com`. The private repository was accessible through the connected GitHub API, so metadata, file contents, diffs and remote branch writes were available. No claim of local Python/Node/PostgreSQL/Android test execution is made.

## PR disposition principle

PR numbers and dates are not quality signals. Preserve the strongest implementation and every valuable unique fix, but do not accept code with unresolved security, data-integrity, compatibility or test-evidence blockers.
---

## 2026-11-19 Update — dispositions executed and verified

The 2026-11-17 audit above was a metadata-only pass with no test execution ("no claim of local Python/Node/PostgreSQL test execution is made" — correct at that date). That limitation is now closed: on 2026-11-19 the integration branch was fully verified locally on exact SHA `bfb28cef` (backend 849/849, static gate, browser E2E 41/41, mobile suites — see `TEST_EVIDENCE_INDEX.md`), and every disposition in the tables below was executed:

- **Closed with evidence comments (2026-11-19):** #29, #40, #42, #44, #45, #47, #49, #50, #51, #52. Each closure names its verified salvage destination (PR #53 head) or its D-018 policy conflict.
- **Salvage landed:** commit `1d50fe80` (4 contract defects), `a96d66cd` (E2E localization), `4994f9d0` (3 behavioral suites + 3 VPS docs), `bfb28cef` (consolidation records).
- **Machine-readable inventories:** `BRANCH_INVENTORY.csv` (58 branches) and `PR_INVENTORY.csv` (49 PRs) — zero NEEDS_REVIEW rows.
- The earlier "could not resolve github.com" limitation no longer applies: this session used a local clone/worktree plus authenticated `gh` for every operation.
- CI remains pre-start blocked by account billing (runner_id=0, steps=0 on all runs since 2026-11-18); recorded in `TEST_EVIDENCE_INDEX.md` and `RELEASE_READINESS.md` as the merge gate owner action.


---

## 2026-11-19 Sync checkpoint reconciliation — post-inventory correction

- PR #53 remains OPEN / DRAFT / UNMERGED. At the start of the latest CI recheck its head was `e772950d8da1b47561d8554cbbeb5fcf0adbd7db`; the subsequent documentation-only refresh is another child commit. Current head is always authoritative in GitHub PR metadata.
- `e772950d` is nine commits after the locally tested source SHA `bfb28cef`. The compare contains 11 paths, all documentation/inventory/control records or the tracked `artifacts/pol-test-results.json`; no application/runtime source file changed. The L1–L16 local evidence supports the unchanged application source but is not a fresh execution on the PR head.
- The checkpoint branch `fix/web-refresh-session-preserve-20261030` is now at `d5ab26bb5d3ca40e7553f0143ac33014df7496c9`. `b4a48801` (the auth/session fix) is byte-identical in Integration. The d5 checkpoint adds six dated REA run-evidence files that are not present in Integration; the `expo run:ios/android` script values match Integration. The branch is retained as `ARCHIVE_ONLY`; historical tunnel/device reports must not be treated as current staging or release proof.
- The branch inventory comparison baseline is Integration `e772950d`: 183 commits ahead of main and 0 behind; main is 183 behind Integration; checkpoint branch `d5ab26bb` is 7 behind / 262 ahead of main and 190 behind / 262 ahead of Integration. The final inventory commit is a docs-only child and is explicitly excluded from the snapshot.
- The last recorded branch-protection state was `main.protected=false` with required checks disabled. The connected branch-protection endpoint returned 403; no protection setting was changed. The repository owner/admin must re-check the setting.
- CI billing remains an external owner action. The inspected jobs had `runner_id=0` and `steps=0`; no workflow changes can correct account billing. No merge, APK build, staging deploy or production action was performed by this reconciliation.


### Latest Actions evidence on PR-head SHA `e772950d`

- Runs 44558971678 / 44558971582 / 44558971752 / 44558971716 are the latest four PR-triggered workflows returned for the inspected SHA.
- Raw jobs metadata confirms `runner_id=0`, `runner_name=""`, and `steps=[]` for every non-skipped job; Android QA matrix job 135682706494 skipped. Completion was within 1–2 seconds and no job log blob existed. These are pre-runner failures, not executed test failures.
- A live read of `/branches/main` confirmed `protected=false`, `protection.enabled=false`, and required-status-check enforcement `off`. No protection change was made.
