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

`DECISION_REGISTER → canonical product/domain/data/ops docs → design decision register → cross-project audit → design blueprint → Penpot`

Do not invent product rules in the UI.

If two documents conflict:
1. identify both;
2. determine the authority hierarchy;
3. record the reconciliation;
4. do not silently choose.

## 3. REQUIRED SPECIFICATION COMPLETION

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

## 4. RECONCILIATION REQUIRED

Resolve and document:

1. React Native/Expo wording vs open frontend framework decision.
2. PUT vs PATCH API examples.
3. Persona physical table names vs conceptual `PersonaProfile`.
4. Commission UI: D-007 is a 1–3% hypothesis, not final policy.
5. Driver: explicitly record MVP delivery workflow as external/vendor/3PL/phone-based unless a future POL Driver surface is intentionally documented.

Do not manufacture a decision. If owner input is genuinely required, mark it `OPEN` and continue with non-dependent work.

## 5. PENPOT STRUCTURE

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

## 6. EXECUTION ORDER

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

## 7. PENPOT AUTOMATION SAFETY

Use small self-contained scripts.

For each batch:
`Generate → Export → Inspect → Fix → Approve → Next`

Use defensive cleanup when a script fails. Avoid leaving partial duplicate nodes.

Keep the Penpot tab focused during automation if required by the environment.

Use `appendChild`-style hierarchy operations for flex boards where required by the Penpot capability audit.

Do not rely on unverified custom-font loading. Verify workspace font availability first.

## 8. APPLE DESIGN CRAFT LAYER

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

## 9. QUALITY BAR

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

## 10. DESIGN QA CHECKLIST

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

## 11. GIT DISCIPLINE

Do not make unrelated refactors.

After each meaningful batch:
1. run relevant checks;
2. inspect generated artifacts;
3. update the written design source of truth if a design decision changed;
4. commit with a narrow message;
5. push to the same design branch.

Do not rewrite canonical decisions without recording why.

## 12. REPORTING

At the end of every batch report:
- repository HEAD
- files changed
- Penpot pages/boards/components created
- states completed
- unresolved OPEN decisions
- tests/checks run
- visual QA result
- next batch

Do not claim production readiness. The repository audit explicitly keeps HTTP/API runtime, production auth, live providers, client implementation, observability, deployment and recovery as separate productionization gates.

## 13. STOP CONDITIONS

STOP instead of guessing if:
- GitHub cannot be synchronized;
- canonical decision authority is ambiguous and materially affects behavior;
- an irreversible migration/destructive operation is proposed;
- credentials or secrets are required but unavailable;
- Penpot write access is unavailable;
- a design would require inventing a backend capability.

When stopped, report the exact blocker and the minimum decision/input needed.

## 14. FINAL DEFINITION OF DONE

Do not declare the design program complete until:

`Remote sync verified → repository read → gap ledger closed → reconciliations recorded → foundations locked → components complete → shared UX complete → state library complete → retailer complete → vendor complete → operations complete → field activator complete → corporate complete → critical prototypes complete → analytics mapped → design QA passed → contract mapping complete`.
