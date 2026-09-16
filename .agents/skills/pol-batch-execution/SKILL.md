---
name: pol-batch-execution
description: Executes one bounded POL design or frontend batch using canonical source-of-truth checks, explicit scope, verification and rollback-safe reporting.
---

# POL Batch Execution Skill

Use this skill whenever the requested work modifies POL design artifacts, frontend code, mock adapters, shared components or implementation contracts.

## Required preflight

1. Verify the Git branch is `research-hardening-2026-09-14`.
2. Fetch remote refs and verify the working HEAD.
3. Read the relevant canonical decision and contract files before editing.
4. Read `13_PRODUCT_DESIGN/23_ANTIGRAVITY_FAILURE_MODES_AND_AGENT_OPERATING_PROTOCOL_2026-09-16.md`.
5. Declare a batch objective and file scope.
6. List acceptance criteria.

## Execution loop

`PLAN → READ → CHANGE → VERIFY → INSPECT → REPORT → COMMIT`

### PLAN
Maximum five concrete actions. Identify dependencies and stop conditions.

### READ
Read authoritative sources, existing implementations and neighboring components. Do not build from screenshots or assumptions.

### CHANGE
Prefer the smallest reversible change. Reuse existing tokens/components/contracts.

### VERIFY
Run targeted tests/checks. For UI, render and inspect affected states. For contract changes, compare request/response semantics and error behavior.

### INSPECT
Review changed files, diff, duplicate nodes/components, accidental formatting, stale references and unrelated edits.

### REPORT
Produce:

```text
BATCH_ID
BASE_HEAD
FINAL_HEAD
OBJECTIVE
FILES_CHANGED
DECISIONS_USED
OPEN_ITEMS
BLOCKED_ITEMS
TESTS_RUN
VISUAL_CHECKS
CONTRACT_CHECKS
RISKS
NEXT_BATCH
```

Use `UNKNOWN` where evidence is missing.

### COMMIT
Only after verification and inspection. Use a narrow commit message. Never force-push.

## Design-specific rules

When designing a screen, verify:
- one primary job;
- one dominant primary action;
- critical commercial information visible before failure;
- all material states mapped;
- loading/empty/error/permission/network states;
- RTL and mixed-direction content;
- long Persian text;
- accessibility/focus/touch targets;
- analytics event mapping;
- API/domain contract mapping;
- no unsupported claim.

For retailer workflows optimize the shortest correct loop:
`Open → Search/Reorder → Decide → Add → Review → Confirm`.

## Frontend-specific rules

Use approved web/mobile directions:
- Next.js / React for web;
- React Native / Expo for retailer mobile.

Keep layers separate:
`UI → feature/page → state/query → API adapter → auth/session → tokens → analytics`.

Do not move business rules into UI-only code. Mocks must mimic canonical contracts and be removable.

## Parallelism

Parallel read-only reviews are allowed. Do not run concurrent edits against the same canonical file, shared token set, shared component, migration domain or design board.

## Stop

Stop instead of guessing when an unresolved business decision materially affects the batch or when verification cannot establish the intended result.
