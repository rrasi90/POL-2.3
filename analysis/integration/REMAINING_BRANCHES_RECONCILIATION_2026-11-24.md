# POL-2.3 — Remaining Branches Reconciliation

**Audit date:** 2026-11-24  
**Main baseline:** `59ac9488b06cb62822f584ef5389f21e0f6dd6f5`  
**Scope:** all remote branches visible at the time of this audit, excluding `main` as the base.  
**Method:** current GitHub branch metadata, commit comparisons against the current main SHA, targeted file-content checks, and the current canonical decision register.

## Executive result

There are eight non-main remote branches. At the start of this reconciliation, before this salvage PR was opened, there were no open pull requests. PR #58 is the resulting selective-salvage review. None of the remaining application-code branches is a safe candidate for a wholesale merge.

One reusable agent workflow asset was salvaged from `penpot-work-2026-09-16`: `.agents/skills/pol-batch-execution/SKILL.md`. It was rewritten for the current repository architecture and branch workflow rather than copied verbatim. The modernized skill is proposed for integration separately.

No schema migration, authentication policy, production deployment configuration, Vercel proxy, or product runtime source was merged as part of this salvage.

## Branch-by-branch disposition

| Remote branch | Current head | Comparison to main | Disposition | Rationale |
|---|---|---:|---|---|
| `backup/feat-mobile-motion-layer-20261022` | `2dfdd26a672c` | 7 ahead / 280 behind; 44 changed paths | **ARCHIVE_ONLY** | Same head as `feat/mobile-motion-layer`. Motion source is already present on main. Targeted SHA checks confirmed the two component files `OfflineBanner.tsx` and `ui.tsx` are identical; the sampled motion components, motion spec, shell, and screen files on main are newer/different from the archived branch versions. Do not revert main to this earlier implementation. |
| `feat/mobile-motion-layer` | `2dfdd26a672c` | 7 ahead / 280 behind; 44 changed paths | **ALREADY_SALVAGED / ARCHIVE_ONLY** | The current main tree contains all 15 motion component files and the motion-system specification. The archived versions are not byte-identical and are generally smaller/older than the current main versions. No duplicate code import is needed. |
| `fix/otp-six-digit-contract-20261025` | `ddeec06b11e8` | 5 ahead / 201 behind; 55 changed paths | **BLOCKED_POLICY** | Includes six-digit OTP policy changes and migration 077. Current `DECISION_REGISTER.md` records D-018 as four-digit OTP with 120-second TTL, a 60-second resend interval, and the existing rate-limit/lockout rules. Do not merge policy, migration, tests, or dependent UI changes without explicit superseding authorization. |
| `fix/otp-six-digit-standard-20261025` | `d49ad86bbda2` | 16 ahead / 201 behind; broad application and documentation changes | **BLOCKED_POLICY** | Also attempts to change the locked D-018 policy and adds a distinct six-digit delivery OTP migration. The scope includes auth, delivery, web/mobile, schema, and test changes. It must remain blocked until a signed decision, threat/lifecycle review, and a consistent migration/contract/test plan exist. |
| `fix/verification-ci-node-install-20261124` | `dbe443ca8db7` | 0 ahead / 1 behind | **ALREADY_MERGED / REDUNDANT REF** | This is the head branch used for PR #57, which has already merged into main as `59ac9488`. The branch adds no unique change relative to main. Do not merge again. |
| `fix/web-refresh-session-preserve-20261030` | `d5ab26bb5d3c` | Historical stacked branch; broad inherited diff | **ARCHIVE_ONLY** | The session-preservation source fix was already included in the consolidated mainline. The six dated REA run-evidence files were salvaged through the post-merge reconciliation PR. Do not merge the stacked branch or stale visual artifacts wholesale. |
| `penpot-work-2026-09-16` | `541b3a1ec03c` | 197 ahead / 1,532 behind; 146 changed paths | **SELECTIVE SALVAGE / ARCHIVE_ONLY** | Most design and implementation guidance is from an older architecture/design phase and is superseded by current mainline design and product records. The branch also contains a deletion of `Master SKU/backup_no_images.json` (a very large retained data artifact), which must not be imported. The old canonical-safety rule is superseded by the expanded rule now on main. Only the bounded batch-execution skill was useful enough to adapt and salvage. |
| `vercel-qa` | `8d3ad01f0d93` | 11 ahead / 1,519 behind; 10 changed paths | **HOLD — TODO-025** | Contains a new Vercel QA workflow, a large web API proxy route, a QA page, environment/config changes, and a transfer manifest. This is a separate QA architecture, not production infrastructure. Keep isolated until TODO-025 explicitly verifies mock-only data, auth and tenant isolation, absence of production credentials/data paths, and deploy-target separation. Do not merge the proxy or workflow before that review. |

## Selective salvage delivered in this PR

### `.agents/skills/pol-batch-execution/SKILL.md`

Source concept: `penpot-work-2026-09-16:.agents/skills/pol-batch-execution/SKILL.md`.

The source skill contained useful bounded-execution concepts but was not safe to copy unchanged: it hard-coded the retired branch `research-hardening-2026-09-14` and referenced old design-program paths. The salvaged v2.0 skill:

- resolves the target branch and SHA from the current task and repository state;
- points to the current decision register, current source of truth, API application boundary, and MVP screen/API/gap maps;
- separates planning, reading, change, verification, inspection, reporting, and commit;
- includes current repository commands for web, mobile, browser E2E, and backend verification;
- preserves TODO-084 and isolated disposable-database safeguards;
- requires explicit OPEN/BLOCKED states, exact-SHA evidence, a rollback path, and a bounded file scope.

The skill does not change application runtime behavior.

## Global safeguards preserved

- D-018 remains the canonical four-digit OTP policy. No six-digit policy or migration was imported.
- The Vercel QA branch remains isolated and on HOLD pending TODO-025.
- Existing mainline motion components were preserved; older component revisions were not copied over them.
- The retained large Master SKU backup file was not deleted.
- No production, staging, or live-provider settings were modified.
- Archive and backup branches were not deleted.

## Verification required for this salvage PR

- Inspect the skill and reconciliation report diff.
- Run the repository static gate.
- Confirm the exact PR head and review any security/scope warnings.
- Keep this documentation/agent-skill salvage separate from any future Vercel proxy or OTP policy work.

## Next integration gates

1. **Vercel QA:** complete TODO-025 isolation and threat review before considering a dedicated implementation PR.
2. **OTP:** require explicit superseding approval for D-018 before revisiting either OTP branch.
3. **Mobile motion:** regenerate current visual QA evidence on the current main SHA; do not import screenshots from the archived branch.
4. **Archive maintenance:** retain branches for recovery until their owners approve deletion; branch cleanup is not part of this merge.
