# Antigravity Failure Modes & Operating Protocol — POL

## Status
`CANONICAL AGENT SAFETY / EXECUTION GUIDANCE`

## Purpose
This document is a companion to `19_ANTIGRAVITY_MASTER_EXECUTION_PROMPT.md`.
It describes the concrete ways a capable but fallible coding/design agent can damage POL when the repository contains many documents, roles, states, contracts and historical artifacts.

The objective is not to make the agent "smarter". The objective is to make incorrect behavior difficult, detectable and reversible.

---

## 1. Primary failure pattern: local optimization

The most dangerous agent behavior is optimizing for the immediate task instead of the canonical system.

Examples:
- making a screen look complete while leaving domain states unmapped;
- implementing an endpoint because a UI needs it even though the application boundary does not support it;
- simplifying a state machine by deleting inconvenient states;
- changing backend semantics to fit a mock;
- duplicating a component because the existing one is difficult to find;
- adding a dependency instead of using the existing stack;
- choosing a missing business rule because it makes the code compile.

Rule:
> Optimize for canonical correctness first, visual polish second, speed third.

---

## 2. Repository hazards

### 2.1 Wrong branch
The agent may open `main` instead of `research-hardening-2026-09-14`.

Protection:
- always print and verify branch + HEAD before work;
- stop if target branch cannot be checked out;
- never infer that the current folder is current.

### 2.2 Historical documents mistaken for current truth
POL contains superseded architecture and historical Single-Vendor decisions.

Protection:
- Decision Register wins;
- historical documents remain evidence, not current requirements;
- every business decision cited in a design artifact must have an authority source.

### 2.3 Duplicate source of truth
The same concept may appear in Product, Data, API, Operations and Design documents.

Protection:
- do not create a new canonical definition when an authoritative one exists;
- link to the authority instead.

---

## 3. Product reasoning hazards

### 3.1 Invented business rules
The agent may infer:
- maximum vendor count;
- final commission rate;
- cheapest-vendor ranking rule;
- driver ETA promise;
- credit policy;
- refund policy;
- payment custody;
- price fallback;
- inventory fallback;
- default tenant;
- default role.

Protection:
`CANONICAL` = explicitly supported
`OPEN` = unresolved business decision
`BLOCKED` = implementation cannot proceed safely

Never convert `OPEN` into a design rule.

### 3.2 Future capability leakage
Database foundations exist for capabilities that are intentionally not active in MVP.

Never surface as active UI:
- wallet/escrow;
- BNPL/credit;
- loyalty/gamification;
- advanced AI recommendation;
- sponsored ads;
- owned logistics;
- advanced trade promotions.

### 3.3 Consumer-app drift
The agent may produce a visually attractive consumer marketplace.

Reject designs dominated by:
- promotional hero areas;
- decorative cards;
- infinite discovery;
- badge clutter;
- generic recommendation modules;
- unnecessary tabs.

The primary retailer loop is:
`Open → Search/Reorder → Decide → Add → Review → Confirm`.

---

## 4. Design-system hazards

### 4.1 Token drift
Never introduce raw colors, arbitrary spacing, one-off radii or local typography outside the token system.

### 4.2 Component duplication
Before creating a component, search the existing component inventory and design files.

### 4.3 State omission
A component is incomplete if only the happy path is represented.

At minimum consider:
`default / loading / disabled / focus / error / empty / success / permission denied / long content / RTL-LTR mixed` where applicable.

### 4.4 Decorative complexity
When two interfaces communicate the same business information, prefer the one with:
- fewer elements;
- fewer decisions;
- fewer transitions;
- clearer next action.

### 4.5 Information hierarchy failure
For commerce surfaces, preserve:
`Product → Pack → MOQ → Price → Availability → Vendor → Order State → Next Action`.

Never bury critical commercial constraints inside hover, tooltip or late checkout validation.

---

## 5. UX state hazards

### Basket
Never collapse:
- unavailable item;
- stale item;
- price changed;
- vendor unavailable;
- revalidation required;
- session expired
into one generic error.

### Allocation
Never hide:
- partial fulfillment;
- unfulfilled lines;
- changed vendor;
- changed price;
- changed inventory.

Explain the business consequence in plain language. Do not expose raw `AllocationPlan` terminology to the retailer unless operationally useful.

### Order
Do not invent state transitions. Use the canonical state machine.

### RMA / Support
Do not reduce exception handling to a single text box. Preserve affected scope, evidence, timeline and resolution status.

---

## 6. API / frontend hazards

### 6.1 Mock becomes fake architecture
Mock adapters must implement the same request/response semantics and state vocabulary as the canonical contract.

Never make the real API conform later to whatever the mock happened to invent.

### 6.2 UI-only authorization
Hiding a button is not authorization.

Server/application boundary remains the authority for tenant, membership, role and command permission.

### 6.3 Optimistic mutation of durable state
Never show an order as successfully created merely because the button was pressed or a local mock returned success.

### 6.4 Contract drift
Before implementing a client call verify:
- endpoint/command;
- request shape;
- response shape;
- error semantics;
- idempotency requirement;
- authorization context.

Do not infer an API from a screenshot.

---

## 7. Data / database hazards

Never:
- edit an already-applied migration to change history;
- create direct transport-to-table writes;
- bypass the canonical application boundary;
- use SQLite to validate PostgreSQL-specific invariants;
- weaken a database constraint merely to make a test pass.

For schema changes:
`new numbered migration → regression test → full migration chain verification`.

---

## 8. Async / integration hazards

The agent may incorrectly call providers synchronously from a client flow.

POL rule:
`transaction → durable state → outbox → worker → provider`

Do not make frontend code depend on provider credentials or provider-specific retry logic.

Notification delivery, payment reconciliation and external delivery providers belong behind explicit worker/adaptor boundaries.

---

## 9. RTL / Persian hazards

A weak agent often treats RTL as text-direction flipping.

It must also handle:
- mixed Persian + Latin strings;
- SKU/barcode/URL/ID islands;
- Toman formatting;
- dates;
- phone numbers;
- numeric alignment;
- icon direction semantics;
- table column order;
- long Persian labels;
- focus order.

Do not validate RTL only on short sample labels.

---

## 10. Accessibility hazards

Do not use:
- color as the only state signal;
- icon-only unlabeled controls;
- hidden focus indicators;
- tiny touch targets;
- inaccessible OTP entry;
- validation that destroys the user's entered values;
- tables whose keyboard behavior is undefined.

Accessibility is a component acceptance condition, not a final polish pass.

---

## 11. Visual automation hazards

Penpot/Figma automation may partially succeed.

Typical failure modes:
- duplicate nodes;
- wrong parent-child hierarchy;
- wrong board/page;
- partial batch creation;
- missing typography;
- stale components;
- broken variants;
- incorrect RTL layout;
- visual regression hidden by successful script exit.

Required protocol:
`Generate → Export → Inspect → Fix → Re-export → Approve`.

A script completing without an exception is not visual verification.

---

## 12. Git hazards

Never:
- force-push;
- reset remote history;
- rewrite user work without inspection;
- merge unrelated branches to "make conflicts disappear";
- commit secrets;
- commit temporary research/build artifacts;
- mix design and unrelated backend refactors.

Each batch should produce a narrow, auditable commit.

---

## 13. Multi-agent hazards

Parallel agents are useful for read-only research and independent reviews, but dangerous for shared canonical artifacts.

Do not concurrently edit:
- decision registers;
- design tokens;
- shared component definitions;
- API contract files;
- migrations in the same domain;
- the same design board.

Parent agent must reconcile subagent outputs before accepting them.

If two agents disagree on a product rule, the result is `OPEN`, not majority vote.

---

## 14. Context-window hazards

The repository is too large to hold safely in one mental context.

Therefore:
- maintain a compact authority map;
- maintain a batch ledger;
- cite exact source files for each major decision;
- re-read critical files before editing them;
- never assume a previous conversation summary is newer than GitHub.

The GitHub repository is the current authority for implementation state.

---

## 15. Verification hazards

A test can be green and still be insufficient.

Distinguish:
- unit correctness;
- domain correctness;
- database integrity;
- application-boundary correctness;
- route completeness;
- visual correctness;
- production readiness.

Never use one category as evidence for another.

Examples:
- a component render test does not prove accessibility;
- a domain test does not prove HTTP runtime readiness;
- a mock API success does not prove production integration;
- a passing historical CI run does not certify the latest HEAD.

---

## 16. Required batch artifact

Every significant agent batch must leave a short machine-readable report containing:

```text
BATCH_ID
BASE_HEAD
FINAL_HEAD
SCOPE
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

If a field cannot be proven, write `UNKNOWN`, not a guess.

---

## 17. Hard stop conditions

Stop immediately when:

1. repository branch/HEAD cannot be verified;
2. an unresolved business decision materially changes behavior;
3. a destructive operation is proposed;
4. credentials/secrets are required but unavailable;
5. the agent would need to invent a backend capability;
6. a migration would rewrite applied history;
7. a test must be weakened to obtain green status;
8. visual automation cannot be inspected;
9. two sources with equal authority conflict;
10. the requested scope exceeds the current batch without a new plan.

A stopped agent should report the blocker and the smallest required decision.

---

## 18. Antigravity-specific operating guidance

Current Google Antigravity supports agent reasoning, tools, artifacts, browser operations, parallel agents and project-level customizations. Use these capabilities to increase verification, not to reduce it.

Prefer project-local:
- `.agents/rules/` for persistent constraints;
- `.agents/skills/` for focused procedures.

Avoid making the project dependent on legacy Workflows because Google documents that Workflows are deprecated and scheduled for retirement on November 1, 2026.

The recommended structure is:

```text
Master Prompt
  ↓
Persistent Rules
  ↓
Focused Skills
  ↓
Bounded Batch
  ↓
Verification
  ↓
Human approval / next batch
```

The agent must remain able to work if any one optional AI customization is unavailable.

---

## 19. Final principle

POL should be built as a controlled system, not as a sequence of impressive-looking agent outputs.

`Correct scope > correct contract > correct state > correct interaction > visual polish > speed`
