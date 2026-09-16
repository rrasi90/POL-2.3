# ANTIGRAVITY MASTER EXECUTION PROMPT — POL PRODUCT DESIGN

You are executing the POL Product Design program against the canonical GitHub repository.

## 0. NON-NEGOTIABLE REPOSITORY SYNC

Your local workspace may be stale. Do NOT trust local files merely because they exist.

Before any design or code work:

1. Stop and inspect the current repository state.
2. Fetch from GitHub.
3. Checkout the target branch: `research-hardening-2026-09-14`.
4. Reset the working tree to the remote branch HEAD so local stale edits do not survive.
5. Remove untracked/generated files that are not tracked by the repository and are not explicitly required local secrets/configuration.
6. Verify `git status --short` is clean.
7. Verify `git rev-parse HEAD` and `git rev-parse origin/research-hardening-2026-09-14` match.
8. If remote synchronization cannot be completed, STOP and report it. Do not proceed from a stale local repository.

Never delete `.env`, credentials, or user secrets blindly. Do not commit secrets.

## 1. READ BEFORE EDIT

Read the repository, not only the design folder.

At minimum inspect:
- `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`
- all `POL_00_PROJECT_CONTROL/*` canonical governance documents relevant to design
- `06_PRODUCT/*`
- relevant domain/data/operations/business/GTM/research documents
- `13_PRODUCT_DESIGN/README.md`
- `13_PRODUCT_DESIGN/00_DESIGN_PROGRAM.md` through current files
- `13_PRODUCT_DESIGN/15_CROSS_PROJECT_DESIGN_AUDIT_2026-09-15.md`
- `13_PRODUCT_DESIGN/16_APPLE_DESIGN_CRAFT_ADAPTATION.md`
- `13_PRODUCT_DESIGN/17_PENPOT_CANONICAL_BLUEPRINT.md`
- `13_PRODUCT_DESIGN/18_DESIGN_COMPLETION_PLAN.md`
- `13_PRODUCT_DESIGN/20_ANTIGRAVITY_REPOSITORY_AUDIT_PROMPT.md`
- `13_PRODUCT_DESIGN/21_MVP_DESIGN_AND_FRONTEND_READINESS_GATE_2026-09-16.md`
- `13_PRODUCT_DESIGN/22_UI_UX_PAGE_AND_SECTION_COMPLETION_SPEC_2026-09-16.md`

Then inspect:
- `06_PRODUCT/`
- `07_ALGORITHMS/`
- `08_DATA/`
- `09_OPERATIONS/`
- `10_GO_TO_MARKET/`
- `11_PILOT/`
- `12_ROADMAP/`
- `migrations/`
- `scripts/`
- `.github/workflows/`

Search globally for:
- authentication / OTP / session / device
- profile / membership / persona
- basket / allocation / revalidation / checkout
- order / fulfillment / delivery / POD
- payment / reconciliation / refund
- RMA / return / dispute / evidence
- support / notification / deep link
- inventory / pricing / MOQ / pack / availability
- referral
- field activator
- analytics / telemetry / event
- permission / role / RBAC

Build a gap ledger before making changes.

## 2. AUTHORITY RULE

The authority order is:

`DECISION_REGISTER → canonical product/domain/data/ops docs → design decision register → cross-project audit → readiness gate → page/section specification → design blueprint → visual artifact`

Do not invent product rules in the UI.

If two documents conflict:
1. identify both;
2. determine the authority hierarchy;
3. record the reconciliation;
4. do not silently choose.

Undocumented business behavior is `OPEN`, not a permission to infer.

## 3. AGENT FAILURE-PREVENTION PROTOCOL

Treat the agent as fallible. Optimize for bounded execution, inspectable artifacts and deterministic recovery.

### 3.1 Never use confidence as proof
Do not accept statements such as “this should work”, “the API probably accepts”, “this component likely exists”, or “the backend supports this” as evidence. Verify with repository files, tests, commands or explicit canonical documentation.

### 3.2 Never solve ambiguity by invention
If a missing business rule affects behavior, mark it `OPEN` and continue only with work that does not depend on it. Never invent pricing, ranking, permission, logistics, payment, commission, credit, delivery SLA, refund or allocation policy.

### 3.3 Prevent context drift
At the beginning of every batch, restate:
- current branch/HEAD;
- current batch number;
- exact files allowed to change;
- acceptance criteria;
- known OPEN/BLOCKED items.
At the end of the batch, compare actual changes to that list. Unexpected scope is a stop condition.

### 3.4 One batch, one objective
Do not combine visual design, backend refactor, schema migration and infrastructure changes in one batch. Keep each change set narrow enough to review and revert.

### 3.5 Read before write
Before editing any file, inspect its current contents and its upstream authority. Never overwrite a canonical document from memory or an old context window.

### 3.6 Preserve reversibility
For every meaningful change, create a narrow commit. Never rewrite history. Never force-push. Never amend an unrelated user commit. Prefer additive documentation changes and forward migrations.

### 3.7 Verify before declaring success
A green-looking artifact is not proof. For every batch provide the exact command/check/result used to verify it.

### 3.8 No hidden fallback behavior
Do not add silent fallbacks that change business semantics, including default tenant, default vendor, default role, default price, default quantity, default notification recipient, default payment state or default delivery status.

### 3.9 No UI-only business logic
Do not encode price, stock, allocation, authorization, settlement, order acceptance or state transition rules solely in frontend code. UI renders canonical state and submits canonical commands.

### 3.10 No fake completion
Do not mark incomplete work as done because:
- the screen exists;
- a mock returns `200`;
- a button changes local state;
- a route renders without an API;
- a screenshot looks correct;
- a test only checks that a component mounts.

## 4. REQUIRED SPECIFICATION COMPLETION

Before high-fidelity Penpot work, complete written specifications for:

### A. Authentication/session
Phone, OTP, autofill/paste, incorrect, expired, resend, rate-limit, session expiry/revocation, device management, logout, no active organization, context selection.

### B. Profile/persona
Canonical model:
`UserProfile → MembershipProfile → PersonaProfile → Security → Notifications → Active Tenant Context`

Persona changes presentation/workflow only. They never become an authorization mechanism.

### C. Commerce state machine
Define visual and interaction treatment for every relevant product/basket/allocation/order/delivery/payment state. For each state define meaning, timestamp, next action, forbidden action, actor, source of truth, notification and deep link.

### D. RMA/dispute/support
Define issue creation, issue types, affected quantities, evidence capture, submission, timeline, vendor response, operator clarification, resolution, refund/adjustment and closure. Define support case creation, thread, assignment, escalation, attachment, SLA, resolution and reopen.

### E. Notification system
Inbox, push, SMS, mandatory vs preference-controlled, delivery failure/retry, read state and deep-link target.

### F. Vendor comparison
Vendor identity, price, pack/case, MOQ, availability confidence, commercial constraints and allocation impact.

### G. Commercial data visibility
Effective price, price changed since basket, vendor-specific price, MOQ/MOV, case pack/increment, stock freshness, unavailable/unknown inventory.

### H. Field network behavior
Offline/weak-network indication, unsent action, retry, duplicate prevention, last-sync context, conflict feedback. Do not invent unsupported offline writes.

### I. Localization/content
Persian-first terminology, RTL, mixed RTL/LTR, Persian/Arabic numerals, Toman, dates, phone numbers, SKU/barcode/URL/ID formatting, long labels, pluralization and content-claim governance.

### J. Analytics
Map critical journey events to screens and acceptance metrics.

## 5. RECONCILIATION REQUIRED

Resolve and document:

1. Frontend stack: use approved `Next.js/React` for web and `React Native/Expo` for retailer mobile unless a new architecture decision supersedes it.
2. PUT/PATCH terminology: use the canonical API contract; do not infer from examples.
3. Persona naming: use conceptual `PersonaProfile` in design; do not hard-code physical table names into UI.
4. Commission UI: D-007 is a 1–3% hypothesis, not final policy.
5. Driver scope: MVP delivery workflow is external/vendor/3PL/phone-based unless a later decision introduces a POL Driver product.

Do not manufacture a decision. If owner input is genuinely required, mark it `OPEN` and continue with non-dependent work.

## 6. PENPOT STRUCTURE

Create exactly this top-level page architecture unless a documented canonical decision supersedes it:

```text
00 — Foundations
01 — Components
02 — Shared UX
03 — States & Patterns
04 — Retailer
05 — Vendor
06 — Operations
07 — Field Activator
08 — Corporate
09 — Prototypes & Flows
10 — Design QA
```

Do not use one giant script. Penpot operations are not transactional.

## 7. EXECUTION ORDER

### Batch 1 — Foundations
Brand, semantic tokens, typography, spacing, radius, elevation, icons, grid, breakpoints, RTL, localization, accessibility, content.

### Batch 2 — Components
Build reusable component library and all critical states.

### Batch 3 — Shared UX
Authentication, profile, tenant context, notifications, support, permission/error recovery, network, evidence.

### Batch 4 — States
Build the complete state library before polished flows.

### Batch 5 — Retailer
Onboarding → home → catalog/search → product → comparison → basket → allocation → revalidation → checkout → order → delivery → reorder → RMA/support → notifications/profile.

### Batch 6 — Vendor
Dashboard → catalog → pricing → inventory → daily confirmation → order queue → fulfillment → delivery handoff → RMA → reconciliation → referral → staff/persona.

### Batch 7 — Operations
Queues → order operations → vendor/retailer → exceptions → reconciliation → RMA → support → risk/reliability → audit → analytics.

### Batch 8 — Field Activator
Tasks → activation → assisted ordering → sync/retry → exceptions → history.

### Batch 9 — Corporate
Home → how POL works → retailer/vendor → technology/operating model → trust/security → contact → legal/privacy.

### Batch 10 — Prototypes
Prototype critical happy paths AND failure/recovery branches.

### Batch 11 — QA
Run design QA and contract mapping.

## 8. BOUNDED EXECUTION MODEL

Use the following loop for every batch:

`PLAN → READ → CHANGE → VERIFY → INSPECT → REPORT → COMMIT`

### PLAN
Produce a mini-plan with maximum 5 concrete actions.

### READ
Inspect all files required by those actions. Record authoritative source for each change.

### CHANGE
Make the smallest set of changes that satisfies the batch. Do not opportunistically “clean up” unrelated code.

### VERIFY
Run targeted checks first, then broader checks when appropriate. If a check fails, diagnose before changing more files.

### INSPECT
Inspect the diff, changed-file list, and generated artifacts. Look for duplicated components, accidental reformatting, stale references and unrelated modifications.

### REPORT
Report:
- HEAD before/after;
- files changed;
- decisions used;
- OPEN/BLOCKED items;
- checks and outcomes;
- artifacts created;
- exact next batch.

### COMMIT
Commit only after verification and inspection. Use a narrow message describing the batch.

## 9. PARALLEL SUBAGENT RULES

Antigravity supports parallel agents/subagents. Do not parallelize tasks that edit the same canonical files or shared component definitions.

Safe parallelism:
- research extraction by domain;
- read-only audits of separate surfaces;
- independent accessibility/content reviews;
- independent visual QA of different screens.

Unsafe parallelism:
- two agents editing the same design token file;
- two agents editing the same component;
- concurrent edits to decision registers;
- simultaneous migrations against the same schema area;
- independent agents “deciding” unresolved product rules.

The parent agent must reconcile all subagent outputs before accepting them.

## 10. DESIGN SIMPLICITY RULES

When two designs satisfy the same canonical requirement, choose the one with:
1. fewer required decisions;
2. fewer screens;
3. fewer form fields;
4. fewer navigation transitions;
5. less duplicated information;
6. clearer primary action;
7. better recovery from failure;
8. lower cognitive load.

Do not add tabs, dashboards, charts, cards, modals, filters, badges or animations merely because they are available in a design system.

For retailer flows in particular, prefer:
`Open → Search/Reorder → Decide → Add → Review → Confirm`

over:
`Open → Discover → Browse → Filter → Compare multiple pages → Reconstruct basket → Checkout`.

## 11. PENPOT AUTOMATION SAFETY

Use small self-contained scripts.

For each batch:
`Generate → Export → Inspect → Fix → Approve → Next`

Use defensive cleanup when a script fails. Avoid leaving partial duplicate nodes.

Keep the Penpot tab focused during automation if required by the environment.

Use `appendChild`-style hierarchy operations for flex boards where required by the Penpot capability audit.

Do not rely on unverified custom-font loading. Verify workspace font availability first.

Never fabricate screenshot evidence. If visual export/inspection did not happen, state that explicitly.

## 12. APPLE DESIGN CRAFT LAYER

Apply `16_APPLE_DESIGN_CRAFT_ADAPTATION.md` as a craft/review layer only.

POL is not an Apple clone.

Review every critical screen through:
1. Accessibility
2. Platform Convention
3. Operational Craft
4. Content
5. Restraint

The POL signature operational hierarchy remains:
`Product → Pack → MOQ → Price → Availability → Vendor → Order State → Next Action`.

## 13. QUALITY BAR

A screen is not complete because it looks polished.

It must answer:
- What is this object?
- What is its current state?
- What commercial constraint matters?
- What can the user do now?
- What happens if data changes?
- What happens if the network fails?
- What is the next action?
- Is the wording supported by canonical data?
- Is the action authorized by backend policy rather than UI role inference?

## 14. DESIGN QA CHECKLIST

For every major screen/flow verify:
- canonical state mapped
- loading/empty/error covered
- permission denied covered where relevant
- RTL covered
- mixed direction covered
- Persian typography covered
- Toman/date/phone formatting covered
- long labels/content covered
- responsive variants covered
- accessibility/focus/touch target covered
- notification/deep-link behavior covered
- analytics event mapped
- API/domain contract mapped
- unsupported claim absent
- no wallet/escrow implication
- no UI-only authorization
- no hidden fallback semantics

## 15. GIT DISCIPLINE

Do not make unrelated refactors.

After each meaningful batch:
1. run relevant checks;
2. inspect generated artifacts;
3. inspect `git diff --stat` and changed-file list;
4. update the written design source of truth if a design decision changed;
5. commit with a narrow message;
6. push to the same design branch.

Do not rewrite canonical decisions without recording why.

Do not force-push, reset remote history, or merge `main` into the design branch as an improvised fix.

## 16. REPORTING

At the end of every batch report:
- repository HEAD
- files changed
- Penpot pages/boards/components created
- states completed
- unresolved OPEN/BLOCKED decisions
- tests/checks run
- visual QA result
- contract mapping status
- next batch

Do not claim production readiness. The repository audit explicitly keeps HTTP/API runtime, production auth, live providers, client implementation, observability, deployment and recovery as separate productionization gates.

## 17. STOP CONDITIONS

STOP instead of guessing if:
- GitHub cannot be synchronized;
- canonical decision authority is ambiguous and materially affects behavior;
- an irreversible migration/destructive operation is proposed;
- credentials or secrets are required but unavailable;
- Penpot write access is unavailable;
- a design would require inventing a backend capability;
- a requested change touches more than the allowed batch scope without a new plan;
- verification cannot prove the intended behavior;
- a generated artifact contradicts a canonical document;
- two agents produce conflicting changes to the same canonical artifact;
- the agent is about to “fix” a failing test by weakening/removing the test without first proving the product or contract changed.

When stopped, report the exact blocker and the minimum decision/input needed.

## 18. CURRENT ANTIGRAVITY CUSTOMIZATION MODEL

Prefer repository-local Agent Skills and Rules over giant monolithic prompt repetition.

Recommended workspace locations:
- `.agents/rules/` for persistent constraints;
- `.agents/skills/` for focused repeatable workflows.

Do not depend on legacy Workflows for long-term project governance; Antigravity documentation states that Workflows are deprecated and scheduled for retirement on 2026-11-01. Skills are the preferred replacement.

The repository master prompt remains the high-level orchestration contract; focused Rules/Skills should enforce bounded execution, audit, design batches and verification.

## 19. FINAL DEFINITION OF DONE

Do not declare the design program complete until:

`Remote sync verified → repository read → gap ledger closed → reconciliations recorded → readiness gate passed → foundations locked → components complete → shared UX complete → state library complete → retailer complete → vendor complete → operations complete → field activator complete → corporate complete → critical prototypes complete → analytics mapped → design QA passed → contract mapping complete → verification evidence recorded`.
