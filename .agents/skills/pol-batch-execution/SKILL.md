---
name: pol-batch-execution
description: Executes one bounded POL product-design, UX, frontend, mock-contract, or implementation batch using the current canonical source of truth, explicit scope, test evidence, and rollback-safe reporting.
license: MIT
metadata:
  version: 2.0.0
  category: engineering-workflow
  domain: pol
  tags: [pol, batch-execution, design, frontend, contracts, verification, repository-safety]
---

# POL Batch Execution Skill

Use this skill when a task changes POL design artifacts, user journeys, frontend code, mock adapters, shared UI components, screen contracts, or implementation documentation.

This skill supplements (and never overrides) the repository-level canonical safety rule at `.agents/rules/00-pol-canonical-safety.md`.

## 1. Required preflight

Before modifying files:

1. Resolve the repository, target branch, and exact HEAD from the current task and GitHub. Never assume an old branch name or a local checkout is current.
2. Confirm the working branch starts from the latest approved `main` unless an explicitly approved integration task requires another base. Record the base SHA.
3. Read the relevant current sources of truth:
   - `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`
   - `POL_00_PROJECT_CONTROL/CURRENT_SOURCE_OF_TRUTH.md`
   - `POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md`
   - the relevant domain/data/operations contracts
   - `mvp/MVP_SCREEN_MATRIX.md`
   - `mvp/MVP_API_MAP.md`
   - `mvp/MVP_KNOWN_GAPS.md`
4. Inspect the actual implementation and neighboring components. Treat screenshots, old branch contents, agent outputs, and historical reports as evidence to verify, not as authority.
5. Declare a single batch objective, allowed file scope, dependencies, acceptance criteria, verification plan, rollback path, and known OPEN/BLOCKED items.
6. Confirm the working tree is clean or explicitly reconcile all pre-existing changes. Do not overwrite unreviewed user work.

## 2. Authority and conflict resolution

Use this authority order:

`DECISION_REGISTER → CURRENT_SOURCE_OF_TRUTH → canonical product/domain/data/operations contracts → API application boundary → MVP screen/API/gap maps → design decision records → implementation specifications → visual artifacts`

If two sources conflict:

1. Identify both sources and the conflicting statements.
2. Apply the authority hierarchy and check whether a later superseding decision exists.
3. Preserve the discrepancy in the batch report.
4. Leave unresolved behavior marked `OPEN`; do not invent a compromise.

Never infer authorization, pricing, inventory, allocation, settlement, fulfilment, refund, commission, credit, logistics, or delivery guarantees from UI appearance.

## 3. Execution loop

Follow:

`PLAN → READ → CHANGE → VERIFY → INSPECT → REPORT → COMMIT`

### PLAN

- Keep the batch to one objective and a reviewable file set.
- Use no more than five concrete execution actions in a single batch plan.
- Identify dependencies, security/privacy implications, data-contract changes, and stop conditions.
- Do not combine visual redesign with unrelated backend, schema, deployment, or infrastructure work.

### READ

- Read complete relevant files and their imports/callers before editing.
- Check the canonical API shape, error envelope, domain states, and authorization boundary.
- Inspect the existing design tokens, shared components, routing, locale, RTL behavior, and accessibility patterns.
- Check whether the feature is already implemented elsewhere before adding a duplicate.

### CHANGE

- Prefer the smallest reversible implementation.
- Reuse existing design tokens, shared components, state models, API clients, and canonical contracts.
- Keep UI, feature/page, state/query, API adapter, authentication/session, and analytics responsibilities separated.
- Do not move business truth into UI-only state.
- Mocks must follow the canonical API request/response and error shapes and remain removable.
- Do not introduce fallback behavior that silently changes tenant, role, permission, price, quantity, inventory, allocation, payment, or order state.
- Do not upgrade dependencies or alter the lockfile unless dependency work is part of the declared batch.

### VERIFY

Choose tests based on the changed surface; record exact commands and results.

**Web / shared JavaScript workspaces** (from `mvp/`, after `npm ci`):

```bash
npm run typecheck
npm run lint
npm run build
```

**Browser E2E** (from `mvp/apps/web/`, with the documented API/web test setup):

```bash
npx playwright test
```

**Mobile checks** (from `mvp/`):

```bash
npm run typecheck --workspace=@pol/mobile
npm run qa:functional --workspace=@pol/mobile
npm run qa:regression --workspace=@pol/mobile
npm run qa:mock --workspace=@pol/mobile
npm run qa:pre-apk --workspace=@pol/mobile
```

**Backend / database behavior** (repository root, only with an isolated disposable test database):

```bash
python scripts/run_verification_suite.py
```

Do not run the destructive test migration runner against shared, staging, or production data. Do not bypass the fail-closed TODO-084 Android pre-build gate. A mock pass is not live-provider acceptance; a successful build is not device QA or release certification.

### INSPECT

Before committing:

- Review the full diff and changed-file list.
- Check for accidental generated files, secrets, private data, large unrelated artifacts, stale paths, and duplicate components.
- Verify RTL, Persian/Latin mixed text, numerals, long strings, focus states, touch targets, reduced motion, loading/empty/error/disabled/permission-denied states, and narrow/wide viewports when relevant.
- Verify that visible actions map to real, authorized API/domain operations.
- Confirm all changed files fall within the declared batch scope.
- Verify the exact commit SHA tested and distinguish current results from historical evidence.

### REPORT

Use the report structure in Section 5. Use `UNKNOWN` where evidence is unavailable. Never claim that a job passed if it did not execute, or that CI passed when it only has a queued/in-progress state.

### COMMIT

Commit only after verification and diff inspection. Use a narrow descriptive commit message. Do not rewrite history, force-push, amend unrelated commits, or merge directly to `main` unless the task explicitly authorizes that action and the applicable merge gates are satisfied.

## 4. Design and UX acceptance criteria

For each screen or workflow, check the applicable criteria:

- One primary job and one dominant primary action.
- Progressive disclosure and minimal required input.
- Critical commercial information is visible before confirmation or failure.
- All material states and valid/forbidden actions are mapped.
- Loading, empty, error, offline, retry, permission-denied, and session-expired states are represented where relevant.
- RTL layout and mixed-direction numbers, IDs, prices, dates, and Latin terms are correct.
- Long Persian content does not break layout or hide critical actions.
- Keyboard/focus behavior, screen-reader labels, contrast, and touch targets are usable.
- Motion is brief, non-essential, and respects reduced-motion preferences.
- Analytics events and API/domain contracts are mapped where required.
- User-facing content does not promise capabilities or operational guarantees that are not approved.

For retailer ordering, optimize the shortest correct loop:

`Open → Search/Reorder → Decide → Add → Review → Confirm`

For vendor and operations surfaces, optimize task queues, exception clarity, state fidelity, and safe next actions rather than decorative density.

## 5. Required batch report

Every completed or blocked batch must report:

```text
BATCH_ID
REPOSITORY
BASE_BRANCH
BASE_SHA
WORKING_BRANCH
FINAL_SHA
OBJECTIVE
FILES_CHANGED
DECISIONS_AND_CONTRACTS_USED
OPEN_ITEMS
BLOCKED_ITEMS
SECURITY_AND_DATA_IMPACT
TESTS_RUN
VISUAL_CHECKS
CONTRACT_CHECKS
ROLLBACK_PATH
RISKS
NEXT_BATCH
```

Use `NOT_RUN`, `NOT_APPLICABLE`, `UNKNOWN`, or `BLOCKED` explicitly rather than implying success.

## 6. Parallelism and stop conditions

- Parallel read-only reviews are allowed.
- Do not run concurrent edits against the same canonical file, shared token set, shared component, API contract, migration domain, or design board.
- Stop when a material business decision is missing, an irreversible/destructive action is proposed, credentials are unavailable, a backend capability would need to be invented, tests must be weakened, visual evidence cannot be inspected, or canonical sources cannot be reconciled.
- When blocked, preserve work in a focused branch and report the exact dependency. Do not bypass the guard or silently broaden scope.
