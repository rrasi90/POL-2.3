# POL Design Completion & Execution Plan

Status: CANONICAL EXECUTION PLAN

Goal: complete every design specification gap identified by the cross-project audit, then execute visual design in controlled batches, then hand stable contracts to frontend/backend productionization.

## Core principle

The repository already contains most product/domain knowledge. The remaining work is primarily specification completion, state coverage, reconciliation, design execution, and controlled agent operation. Do not redesign the product from scratch.

## Agent operating model

Antigravity is treated as a fallible executor, not as a source of product decisions.

Required project-local controls:
- `.agents/rules/00-pol-canonical-safety.md`
- `.agents/skills/pol-batch-execution/SKILL.md`
- `13_PRODUCT_DESIGN/23_ANTIGRAVITY_FAILURE_MODES_AND_AGENT_OPERATING_PROTOCOL_2026-09-16.md`

The master prompt provides orchestration. Persistent Rules enforce invariants. Focused Skills execute bounded tasks. Each batch is independently verified and committed.

## Phase 0 — Repository synchronization and authority lock

Before Antigravity touches the local workspace:

1. Treat GitHub branch `research-hardening-2026-09-14` as the authoritative source for this design work.
2. Fetch remote refs.
3. Stop all local edits/processes that could overwrite the workspace.
4. Preserve a backup only if necessary; do not merge stale local files into the canonical branch.
5. Reset the local repository to the exact GitHub branch/commit specified by the orchestration prompt.
6. Clean untracked/generated files that are not part of the repository.
7. Verify `git status` is clean.
8. Verify the current HEAD and branch.
9. Only then begin reading and editing.

Antigravity must not assume its local copy is current. The prompt must explicitly require remote synchronization.

## Phase 1 — Cross-project specification completion

Read all canonical product, engineering, domain, data, operations, business, GTM, research and design documents before editing.

Produce/maintain a gap ledger with:
- requirement
- source document
- source authority
- current design coverage
- missing state/interaction
- dependency
- decision required?
- canonical owner
- status

Complete these domains:

### 1. Authentication/session
Phone, OTP, paste/autofill, incorrect, expired, resend, rate-limit, session expiry/revocation, devices, logout, organization context, no active organization.

### 2. Identity/profile/persona
Map `UserProfile → MembershipProfile → PersonaProfile → Security → Notifications → Active Tenant Context`. Never duplicate RBAC as presentation logic.

### 3. Commerce states
Product, basket, allocation, revalidation, checkout, order, delivery, payment, settlement, dispute and refund state matrices.

### 4. Returns/RMA/disputes
Issue type, affected item/quantity, evidence, submission, vendor response, operator review, clarification, resolution, adjustment, refund, closure.

### 5. Support
Create case, category, priority, attachments, thread, assignment, escalation, SLA, resolution and reopen states.

### 6. Notifications
Inbox, push, SMS, mandatory notifications, preference-controlled notifications, delivery failure/retry, deep links and read state.

### 7. Vendor comparison
Identity, price, pack/case, MOQ, availability confidence, commercial constraints and allocation impact.

### 8. Vendor operations
Catalog, effective pricing, inventory freshness, reservation, daily confirmation, order queue, acceptance SLA, fulfillment, referral, reconciliation and staff personas.

### 9. Operations
Queue-first workflows, reason codes, severity, ownership, evidence, audit trail, bulk actions and next-action semantics.

### 10. Field Activator
Task-first activation, assisted ordering, weak network, retry, duplicate prevention, sync/conflict feedback without unsupported offline-write claims.

### 11. Corporate
Trust/security/legal/privacy, claim governance, SEO/content governance and responsive public-site behavior.

### 12. Localization/content
Persian terminology, RTL, mixed-direction SKU/barcode/URL/ID handling, Persian/Arabic numerals, Toman, dates, phone numbers, long labels, pluralization and content claims.

### 13. Analytics/measurement
Define critical events and screen acceptance metrics.

## Phase 2 — Reconciliation decisions

Do not invent resolutions. Record each as a decision or open question:

1. Frontend implementation direction is `Next.js/React` for web and `React Native/Expo` for retailer mobile unless superseded by a new architecture decision.
2. API method terminology must follow the canonical API contract rather than examples copied from older documents.
3. Persona naming in design remains conceptual `PersonaProfile`; physical table names stay implementation details.
4. Commission UI: D-007 remains a 1–3% post-pilot hypothesis; do not expose category rates as final policy.
5. Driver: record MVP delivery as external/vendor/3PL/phone-based unless a future POL Driver surface is intentionally approved.

## Phase 3 — Agent safety gate

Before high-fidelity visual generation, confirm:
- persistent POL Rule is loaded;
- batch execution Skill is available;
- failure-mode protocol is read;
- target branch/HEAD is verified;
- batch scope and acceptance criteria are declared;
- no unresolved business decision is hidden in the current batch.

No visual batch starts if these controls cannot be verified.

## Phase 4 — Design system lock

After specification and reconciliation:
- validate semantic color contrast
- validate Persian typography in target workspace
- lock spacing/radius/elevation/motion tokens
- lock RTL/mixed-direction behavior
- lock content formatting rules
- map tokens to component inventory
- apply Apple Design Craft adaptation as a review layer, not as a replacement for POL brand/system

## Phase 5 — Component library

Build the component library before high-fidelity screens.

Each critical component needs default + interactive + disabled + loading + empty + error + long-content + RTL/mixed-content states where applicable.

Prioritize components that express POL's operational status language:
`Product → Pack → MOQ → Price → Availability → Vendor → Order State → Next Action`.

## Phase 6 — Shared UX and state library

Build shared authentication, profile, notification, support, evidence, error, permission, network and context patterns. Then build the canonical state library.

Do not start with polished retailer screens while shared states remain undefined.

## Phase 7 — Product surfaces

Execute in this order:
1. Retailer
2. Vendor
3. Operations
4. Field Activator
5. Corporate

For every surface:
- journey map
- screen inventory
- state inventory
- responsive variants
- RTL variant
- prototype critical flow
- failure branch
- analytics events
- contract mapping

## Phase 8 — Prototype and usability review

Prototype critical journeys and test for:
- speed to correct order
- clarity of commercial constraints
- state comprehension
- recovery from changes/failures
- operational next action
- accessibility
- Persian readability
- unnecessary decision count
- screen count and navigation cost

Document findings; do not silently change canonical product decisions.

## Phase 9 — Design QA

Before frontend handoff, verify:
- every canonical route has a screen or explicit out-of-scope record
- every state has a visual treatment
- every state has allowed/forbidden actions
- every critical screen maps to a contract
- all user-visible claims are supported
- no wallet/escrow/custody implication exists
- persona presentation does not grant permissions
- RTL and long-content cases pass
- notification/deep-link behavior is defined
- analytics events are defined
- the primary task and next action are obvious

## Phase 10 — Frontend handoff

Only after design QA:
- map screens to frontend routes
- map components to implementation components
- map state variants to API/domain states
- provide deterministic fixtures for default/error/empty/loading/edge cases
- identify unresolved backend runtime dependencies

## Phase 11 — Productionization track

Design work does not imply production readiness. Continue separately on:
- HTTP/API runtime
- production authentication/OTP
- live notification providers
- observability
- deployment
- backup/restore/PITR
- migration operations
- real client implementation

## Agent batch protocol

Every significant batch must follow:

`PLAN → READ → CHANGE → VERIFY → INSPECT → REPORT → COMMIT`

Do not use giant one-shot automation for the entire product. Parallelize only independent read-only audits or independent surfaces; do not concurrently edit shared canonical artifacts.

## Exit criteria

The design program is complete only when:

`Repository synced → specification gaps closed → decisions reconciled → agent safety gate passed → foundations locked → components built → states covered → all surfaces designed → critical flows prototyped → QA passed → frontend contract mapping complete → verification evidence recorded`.

If an essential decision is genuinely unknown, record it as `OPEN` rather than inventing a value.
