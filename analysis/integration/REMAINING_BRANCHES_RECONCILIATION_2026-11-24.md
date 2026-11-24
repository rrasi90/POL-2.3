# POL-2.3 — Remaining Branches Reconciliation

**Audit date:** 2026-11-24  
**Audit baseline:** `59ac9488b06cb62822f584ef5389f21e0f6dd6f5`  
**Post-salvage main:** `e2524df8d8712f535369ae469292541861ea3da7` (PR #58)  
**Scope:** all remote branches visible at the time of this audit, excluding `main` as the base.  
**Method:** current GitHub branch metadata, commit comparisons against the current main SHA, targeted file-content checks, and the current canonical decision register.

## Executive result

At the initial audit snapshot there were eight non-main remote branches and no open PRs. The selective-salvage PR #58 has since merged. The current remote set contains nine non-main refs (including the merged integration branch retained for traceability), and the live PR inventory has 54 records: 33 merged, 21 closed unmerged, and zero open. None of the remaining application-code branches is a safe candidate for wholesale merge.

One reusable agent workflow asset was salvaged from `penpot-work-2026-09-16`: `.agents/skills/pol-batch-execution/SKILL.md`. It was rewritten for the current repository architecture and branch workflow rather than copied verbatim, then merged through PR #58 as part of merge commit `e2524df8`.

No schema migration, authentication policy, production deployment configuration, Vercel proxy, or product runtime source was merged as part of this salvage.

## Branch-by-branch disposition

| Remote branch | Current head | Comparison to main | Disposition | Rationale |
|---|---|---:|---|---|
| `backup/feat-mobile-motion-layer-20261022` | `2dfdd26a672c` | 7 ahead / 280 behind; 44 changed paths | **ARCHIVE_ONLY** | Same head as `feat/mobile-motion-layer`. Motion source is already present on main. Targeted SHA checks confirmed the two component files `OfflineBanner.tsx` and `ui.tsx` are identical; the sampled motion components, motion spec, shell, and screen files on main are newer/different from the archived branch versions. Do not revert main to this earlier implementation. |
| `feat/mobile-motion-layer` | `2dfdd26a672c` | 7 ahead / 280 behind; 44 changed paths | **ALREADY_SALVAGED / ARCHIVE_ONLY** | The current main tree contains all 15 motion component files and the motion-system specification. The archived versions are not byte-identical and are generally smaller/older than the current main versions. No duplicate code import is needed. |
| `fix/otp-six-digit-contract-20261025` | `ddeec06b11e8` | 5 ahead / 201 behind; 55 changed paths | **SUPERSEDED POLICY / DO NOT MERGE WHOLE** | The 2026-11-24 founder amendment now approves six-digit D-018 auth OTP. This branch is stale; selectively re-author against current main and verify migration, API, UI and tests. |
| `fix/otp-six-digit-standard-20261025` | `d49ad86bbda2` | 16 ahead / 201 behind; broad application and documentation changes | **SUPERSEDED POLICY / DO NOT MERGE WHOLE** | D-018 has since been amended to six digits; old PR #50 broad implementation and migration still require a current-main reimplementation and explicit in-flight delivery lifecycle safeguards. |
| `fix/verification-ci-node-install-20261124` | `dbe443ca8db7` | 0 ahead / 6 behind (post-#58 main) | **ALREADY_MERGED / REDUNDANT REF** | This is the head branch used for PR #57, which merged as `59ac9488`. The branch adds no unique change relative to current main. Do not merge again. |
| `integration/selective-salvage-remaining-branches-20261124` | `1f0fe96cbf0b` | 0 ahead / 1 behind | **ALREADY_MERGED / REDUNDANT REF** | PR #58 merged as `e2524df8`; its two documentation files are present in main. Branch retained for traceability; no further merge needed. |
| `fix/web-refresh-session-preserve-20261030` | `d5ab26bb5d3c` | Historical stacked branch; broad inherited diff | **ARCHIVE_ONLY** | The session-preservation source fix was already included in the consolidated mainline. The six dated REA run-evidence files were salvaged through the post-merge reconciliation PR. Do not merge the stacked branch or stale visual artifacts wholesale. |
| `penpot-work-2026-09-16` | `541b3a1ec03c` | 197 ahead / 1,532 behind; 146 changed paths | **SELECTIVE SALVAGE / ARCHIVE_ONLY** | Most design and implementation guidance is from an older architecture/design phase and is superseded by current mainline design and product records. The branch also contains a deletion of `Master SKU/backup_no_images.json` (a very large retained data artifact), which must not be imported. The old canonical-safety rule is superseded by the expanded rule now on main. Only the bounded batch-execution skill was useful enough to adapt and salvage. |
| `vercel-qa` | `8d3ad01f0d93` | 11 ahead / 1,519 behind; 10 changed paths | **HOLD — TODO-025** | Contains a new Vercel QA workflow, a large web API proxy route, a QA page, environment/config changes, and a transfer manifest. Static review found concrete auth-boundary differences: the branch adds `/api/v1` to the Middleware public-prefix list (the current mainline does not), and the QA page writes `pol.session=1` plus a client-selected `pol.role` cookie and mock auth object. The proxy also defines a default retailer role and hard-coded mock datasets. This may be acceptable only inside a separate mock-only QA deployment; it is not safe to merge into the shared production-capable app. Keep on HOLD until TODO-025 verifies an independent deployment target, build-time fail-closed mock flag, no production API fallback/secrets, no cross-environment cookies, and explicit authorization/tenant isolation. Do not merge the proxy, middleware exception, or QA login path before that review. |

## Selective salvage delivered in PR #58

### `.agents/skills/pol-batch-execution/SKILL.md`

Source concept: `penpot-work-2026-09-16:.agents/skills/pol-batch-execution/SKILL.md`.

The source skill contained useful bounded-execution concepts but was not safe to copy unchanged: it hard-coded the retired branch `research-hardening-2026-09-14` and referenced old design-program paths. The salvaged v2.0 skill:

- resolves the target branch and SHA from the current task and repository state;
- points to the current decision register, current source of truth, API application boundary, and MVP screen/API/gap maps;
- separates planning, reading, change, verification, inspection, reporting, and commit;
- includes current repository commands for web, mobile, browser E2E, and backend verification;
- preserves TODO-084 and isolated disposable-database safeguards;
- requires explicit OPEN/BLOCKED states, exact-SHA evidence, a rollback path, and a bounded file scope.

The skill does not change application runtime behavior. It is present on main after PR #58.

## Global safeguards preserved

- **Historical snapshot at the initial branch audit (before the founder's 2026-11-24 amendment):** D-018 was then recorded as a four-digit OTP policy and no six-digit policy/migration had been imported. This statement is superseded by the post-audit update below; current D-018 is six digits.
- The Vercel QA branch remains isolated and on HOLD pending TODO-025.
- Existing mainline motion components were preserved; older component revisions were not copied over them.
- The retained large Master SKU backup file was not deleted.
- No production, staging, or live-provider settings were modified.
- Archive and backup branches were not deleted.

## Verification and merge record

- PR #58 merged on 2026-11-24 as `e2524df8d8712f535369ae469292541861ea3da7`.
- Static Gate passed on the exact PR head and again on the post-merge main SHA.
- Independent Verification on the PR head and post-merge main was still running at the time of this inventory refresh. No full-suite pass is claimed for PR #58 or the merge SHA yet.
- The PR changed only two Markdown files; no runtime, test, schema, credential, or deployment file changed.
- Keep this documentation/agent-skill salvage separate from any future Vercel proxy or OTP policy work.

## Next integration gates

1. **Vercel QA:** complete TODO-025 isolation and threat review before considering a dedicated implementation PR.
2. **OTP:** require explicit superseding approval for D-018 before revisiting either OTP branch.
3. **Mobile motion:** regenerate current visual QA evidence on the current main SHA; do not import screenshots from the archived branch.
4. **Archive maintenance:** retain branches for recovery until their owners approve deletion; branch cleanup is not part of this merge.


## Post-audit update — OTP policy supersession (2026-11-24)

The branch-by-branch table above records the policy and source snapshot at the time of the audit. Later on 2026-11-24, the founder explicitly superseded the former four-digit authentication rule: D-018 is now six digits, and D-029 defines six-digit newly issued delivery/POD codes separately. Therefore, the old BLOCKED_POLICY reason for the two six-digit branches is retired; their branch contents are still not safe for wholesale merge because they are materially behind current main and contain old application, migration and test work.

A clean implementation is being selectively re-authored from the audited current main on:
- feat/six-digit-otp-and-social-impact-readme-20261124

The new migration 077 is not copied from the closed PR #50 tip. It records each existing delivery code's actual length, leaves active in-flight codes untouched, enforces six digits for new records and allows only the already-issued legacy four-digit values to complete their original delivery. New authentication and delivery UI/API flows use six digits. Old PRs #49 and #50 remain closed historical review records; do not reopen or merge their stale heads.

The new branch must pass fresh PostgreSQL 18 migration tests, backend verification, web typecheck/build and browser E2E, mobile QA/typecheck, static gate, plus review of recipient-only delivery OTP behavior before merge. Existing mainline test evidence predates this amendment and is not evidence for the new OTP implementation.


## Final OTP disposition after PR #59 — 2026-11-25

The selective implementation is no longer pending: PR #59 merged to `main` as `f9eca328b053dfacfe4c42c81c1c9c468fb8b607`. Its tested head `dbf0a2284e4f16d0cc1e7568b78e81e11c5352a6` passed backend 852/852, PostgreSQL 18 migrations 001–077, browser E2E 41/41, mobile 17/17 steps and static gate 11/11. See runs 45488346802, 45488346616, 45488346626 and 45488346621.

The two historical branches `fix/otp-six-digit-contract-20261025` and `fix/otp-six-digit-standard-20261025` remain **closed/unmerged**. Their original four-digit D-018 policy objection has been superseded, but the old branch heads remain stale and are not to be merged wholesale. PR #59 contains the clean selective implementation from the current mainline.

The Android QA APK matrix was skipped by TODO-084. No APK build or physical-device validation is claimed by this merge.
