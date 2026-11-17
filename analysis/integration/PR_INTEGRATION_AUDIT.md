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