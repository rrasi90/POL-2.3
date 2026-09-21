# POL — Master Tree Deep Critical Audit & Architecture Upgrade

**Document ID:** `POL-DESIGN-AUDIT-057`  
**Version:** `1.0.0`  
**Date:** 2026-09-21  
**Status:** ACTIVE / DEEP CRITICAL AUDIT / MASTER TREE v4 UPGRADE BASIS  
**Repository:** `rrasi90/POL-2.3`  
**Branch:** `product-architecture-evolution-2026-09-20`

---

# 0. Executive conclusion

The POL Master Tree is **not a sitemap**.

It has evolved into a federated product-design control system connecting:

**strategy → capability → actor/role/persona → experience → journey/flow → screen → section → component → action → state → permission → data → API/boundary → event/audit/notification → prototype → QA → Penpot → frontend/runtime/pilot evidence.**

This direction is fundamentally correct for POL.

However, the current v3.6 Master Tree has reached a point where **adding more content without restructuring the model would reduce reliability**.

The central audit finding is:

> **The Master Tree knows many things, but it does not yet enforce a sufficiently strict distinction between canonical nodes, derived views, evidence, artifacts, aliases, and closure applicability.**

That produces five systemic risks:

1. **Duplicate authority risk** — the same logical screen ID is described more than once.
2. **False closure risk** — the universal closure vector can imply missing work for node types where a dimension is not applicable, or imply completeness from the existence of a frame.
3. **Schema expressiveness risk** — the machine schema represents graph edges, evidence and impact too narrowly for the many-to-many nature of the system.
4. **Artifact traceability risk** — the Master Tree references Penpot conceptually, but does not yet require an immutable artifact binding containing exact page/frame/component/revision evidence.
5. **Source drift risk** — repository side documents can remain stale or contradictory while the Master Tree still looks internally coherent.

The correct next step is therefore **Master Tree v4.0: Kernel + Views + Evidence + Artifacts + Drift Control**.

---

# 1. What POL actually is

The current repository describes POL as a B2B FMCG platform centered on the Ahvaz pilot.

The adopted product architecture is characterized by:

- Ahvaz as the pilot geography;
- a 90-day / 3-month pilot horizon;
- asset-light fulfillment;
- no POL-owned delivery fleet in MVP;
- one unified retailer basket;
- deterministic multi-vendor allocation;
- `Basket → AllocationPlan → OrderGroup → Order → OrderItem`;
- strict separation of Master Product and Vendor SKU;
- non-custodial direct payment in MVP;
- no stored-value wallet in MVP;
- vendor referral as attribution-only MVP;
- universal user profile plus organization membership/persona context;
- server-side organization-scoped authorization;
- Python as production backend runtime;
- FastAPI as thin HTTP transport;
- PostgreSQL 18 as canonical runtime database;
- transactional outbox and asynchronous workers;
- Web + Android client parity for personas;
- lightweight delivery handoff instead of a full Driver App;
- vendor-first and product-first discovery;
- Financial Activity as a read/visibility model, not a wallet;
- barcode scanning and product/media provenance as first-class operational concerns.

The Master Tree is therefore describing a **socio-technical service**, not merely a mobile application.

This distinction matters.

A retailer screen can be visually perfect while the underlying service is impossible to complete.

An operations screen can be absent even though the capability exists.

A route can be documented while the HTTP boundary is not implemented.

A Penpot frame can exist while permissions, state transitions or recovery remain undefined.

Therefore the Tree must preserve these dimensions independently.

---

# 2. What the Master Tree is for

The Master Tree has six legitimate jobs.

## 2.1 Canonical semantic registry

It defines what a concept means in POL.

Examples:

- Role ≠ Persona
- Persona ≠ Surface
- Screen ≠ Capability
- UI State ≠ Domain State
- Payment ≠ Settlement
- Invoice ≠ Order
- OrderGroup ≠ Child Order
- Master Product ≠ Vendor SKU
- Handoff Token ≠ Authenticated Session

This semantic function is already one of the strongest parts of the Master Tree.

## 2.2 Translation layer

It translates product/business truth into design-relevant consequences.

Example:

`D-014`

→ multi-vendor basket

→ AllocationPlan

→ OrderGroup

→ child Orders

→ vendor-specific acceptance

→ partial acceptance

→ separate invoices

→ separate fulfillment

→ unified retailer OrderGroup view.

This is exactly the type of chain a design agent needs.

## 2.3 Design construction specification

It defines what must exist in Penpot:

- foundations;
- components;
- patterns;
- screens;
- states;
- prototypes;
- QA evidence;
- theme variants;
- responsive behavior.

## 2.4 Traceability graph

It links:

`Requirement → Decision → Capability → Domain → Data → API → Design → Frontend → Test → Evidence`

This makes the design inspectable rather than subjective.

## 2.5 Agent context contract

The tree provides bounded context to an AI design agent.

Without it, an agent can generate attractive but semantically incorrect screens.

## 2.6 Drift-control system

The Tree should eventually answer:

> What becomes stale when one canonical source changes?

This is the least mature of the six jobs.

---

# 3. What the Master Tree is NOT

The following distinctions are mandatory.

The Master Tree is not:

- the PRD;
- the database schema;
- the API specification;
- the Penpot file itself;
- the component library;
- the frontend codebase;
- a list of every historical design document;
- a screenshot catalog;
- an approval record;
- a generic AI prompt;
- a business-plan narrative.

Those artifacts can be connected to the Tree, but the Tree must not become a duplicate copy of each one.

---

# 4. Quantitative audit of the current Master Tree

Current v3.6 snapshot:

- approximately **8,273 lines**;
- approximately **918 headings**;
- **105 screen-related heading occurrences**;
- approximately **58 logical screen IDs** at the screen-heading level;
- **47 of those logical IDs appear more than once**.

This means the screen-level representation is already heavily duplicated.

The most important repeated families include:

- RT-01 through many retailer screens;
- VD-01 through VD-18;
- OP-01 through OP-15;
- FA-01 through FA-05.

This is not automatically bad.

The problem is that the file does not yet make the distinction strong enough between:

**canonical node**

and

**derived view of that node**.

A human may understand this.

An agent or validator can still treat both descriptions as independent truth.

That is unsafe.

---

# 5. Major finding P0-01 — Canonical Node vs View Projection

## Current problem

A logical node such as:

`RT-15`

appears as a detailed surface specification and again in a later role/semantic specification.

The same happens for many VD/OP/FA screens.

The current document says the Master Tree is a graph of views, but the file layout still visually resembles multiple independent definitions.

## Why this matters

An agent may:

1. read the first RT-15;
2. read the later RT-15;
3. notice a difference;
4. assume both are legitimate;
5. mutate Penpot using the wrong attribute.

This is classic **multi-authority drift**.

## Required v4 rule

Every logical node has exactly one:

`CANONICAL_IDENTITY_RECORD`

Everything else is a:

`VIEW_PROJECTION`

or:

`DERIVED_INDEX`

or:

`EVIDENCE_RECORD`.

A projection may summarize a node.

A projection may not redefine the node.

### New precedence rule

`CANONICAL_NODE > DERIVED_VIEW > EXPLANATORY_TEXT`

If a projection conflicts with the canonical node, the projection is wrong.

---

# 6. Major finding P0-02 — Universal closure vector is too blunt

The current closure vector is intentionally comprehensive:

`CAPABILITY → OUTCOME → JOURNEY → SCREEN/PATTERN/NON_UI → STATES → ACTION → PERMISSION → DATA → API/BOUNDARY → EVENT/AUDIT/NOTIFICATION → PROTOTYPE → A11Y → RTL → RESPONSIVE → NETWORK → VISUAL → STRUCTURAL → RUNTIME → PILOT`

This is excellent as a **universe of possible closure dimensions**.

It should NOT be interpreted as a requirement that every node satisfy every dimension.

Examples:

A color token does not require:

- API;
- domain event;
- settlement;
- runtime route.

A domain event does not require:

- a screen;
- visual theme;
- responsive layout.

A Penpot component does require:

- anatomy;
- visual tokens;
- variants;
- states;
- accessibility;
- theme;
- responsive behavior where applicable.

Therefore v4 introduces:

`CLOSURE_PROFILE`

A closure profile defines which dimensions are applicable for a node type.

Example:

### CAPABILITY_PROFILE

Expected dimensions:

- CAPABILITY_PRESENT
- OUTCOME
- JOURNEY
- SCREEN_OR_PATTERN or NON_UI
- STATES
- ACTION
- PERMISSION where protected
- DATA
- API_BOUNDARY where implemented/required
- EVENT_AUDIT_NOTIFICATION where applicable
- PROTOTYPE where user-facing
- A11Y where UI exists
- RTL where localized UI exists
- RESPONSIVE where client UI exists
- NETWORK where applicable
- VISUAL where UI exists
- STRUCTURAL where Penpot artifact exists
- RUNTIME where runtime evidence exists
- PILOT where pilot evidence exists

### CMP_PROFILE

Expected dimensions:

- VISUAL
- STRUCTURAL
- A11Y
- RTL
- RESPONSIVE
- NETWORK where interaction depends on network
- PROTOTYPE where interaction is behaviorally significant

API is normally NOT_APPLICABLE.

---

# 7. Major finding P0-03 — Evidence is inherently many-to-many

A canonical node may require:

- one source document;
- two decisions;
- three design screenshots;
- one Penpot revision;
- one test run;
- one runtime verification;
- one pilot observation.

The current schema has a singular conceptual evidence object even though the surrounding model already expects multiple evidence references.

v4 makes evidence an explicit collection:

`EVIDENCE_RECORD[]`

Every evidence record carries:

- evidence ID;
- dimension;
- evidence type;
- source/artifact;
- revision;
- timestamp;
- evaluator;
- result;
- scope;
- notes.

This means:

**Visual evidence is not semantic evidence.**

**Runtime evidence is not design evidence.**

**Pilot evidence is not API evidence.**

The Tree must preserve those distinctions.

---

# 8. Major finding P0-04 — Relationship edges are also many-to-many

A node can:

- depend on many nodes;
- navigate to many nodes;
- trigger many events;
- be authorized by many permissions;
- be audited by many events;
- supersede many aliases.

Therefore the graph model should use:

`RELATIONSHIP_EDGE[]`

Each edge should have:

- edge ID;
- relation type;
- target;
- source context;
- evidence/authority when required.

The old single-edge conceptual form is insufficient as a future machine contract.

---

# 9. Major finding P0-05 — Penpot artifact identity is under-specified

A design record is not proven by the statement:

> “Penpot artifact exists.”

For agentic execution, artifact identity must be exact.

A canonical Penpot binding should include:

- Penpot file identifier;
- page identifier;
- board/frame identifier;
- component identifier where applicable;
- variant identifier where applicable;
- Penpot revision;
- artifact hash/export evidence where available;
- binding status.

Therefore:

`Design Node → Penpot Artifact Binding → Revision Evidence`

becomes a first-class relationship.

A screenshot URL alone is not enough.

---

# 10. Major finding P0-06 — Source authority is not machine-enforced

The repository already contains an excellent authority hierarchy.

However, side documents can still contain stale statements.

Examples identified during this audit:

### Example A — historical single-vendor state

`CONTRADICTION_LOG.md` preserves older single-vendor language around C-003, while `DECISION_REGISTER.md` explicitly says D-014 supersedes D-003.

This is legitimate historical preservation, but the source must be mechanically marked as:

`HISTORICAL / SUPERSEDED`

rather than merely left as prose.

### Example B — vendor acceptance SLA

The Penpot completion matrix still contains a 30-minute SLA reference in its vendor queue row, while the current canonical vendor UI contract and Master Tree require:

**120 working minutes / 2 hours**

and explicitly state that older 30-minute Penpot copy is stale.

This is precisely the kind of drift that the Master Tree should detect automatically.

### Example C — event runtime wording

Older traceability material still contains BullMQ/Redis queue language, while the current architecture direction establishes Python + PostgreSQL transactional outbox and asynchronous workers.

Again:

historical source ≠ active architecture.

### Example D — design token lineage

The repository contains multiple previous token baselines:

- visual refinement;
- research-based Design System v2;
- Final Tokens v3;
- Canonical Tokens v4;
- Precision Commerce v1.

The Tree must declare the authority chain instead of requiring an agent to infer it from dates and document names.

---

# 11. Major finding P0-07 — Theme naming must be normalized

The system previously used:

- Light / Dark
- Light / Night

The new canonical visual direction is:

**Light + Night**

Therefore v4 defines:

`NIGHT`

as canonical terminology.

`DARK`

becomes a legacy alias only.

This avoids future schema ambiguity.

The Night system is semantic theming, not image/filter inversion.

---

# 12. Major finding P0-08 — “Presence” and “Closure” are still too close

The Tree correctly introduced:

- capability present;
- screen defined;
- state complete;
- permission complete;
- contract mapped;
- prototyped;
- visually verified;
- runtime verified;
- pilot verified.

v4 formalizes this as independent maturity axes.

A node can be:

`CAPABILITY_PRESENT = YES`

while:

`SCREEN_DEFINED = YES`

but:

`PENPOT_BUILT = NO`

and:

`RUNTIME_VERIFIED = NO`.

No single overall “complete” flag should override this.

---

# 13. Major finding P1-01 — Design system governance needs token tiers

The current visual direction provides semantic tokens.

v4 adds a strict hierarchy:

`Primitive → Semantic → Component → Pattern`

Example:

`blue.600`

→

`theme.light.brand.primary`

→

`button.primary.background`

→

`commerce.primary-action`

This distinction matters because a component should normally not depend directly on a primitive color.

The Design Tokens Community Group's 2025.10 specification provides a stable exchange format for interoperable tokens; the current specification explicitly supports aliases, groups and context/modifiers such as light/dark themes. urlcite_PLACEHOLDER_DTCG

POL should use that interoperability direction for future Penpot ↔ frontend token exchange, while still keeping POL's own semantic naming authoritative.

---

# 14. Major finding P1-02 — Design release snapshot must become a real contract

The Tree already defines a release snapshot concept.

v4 makes it mandatory.

A Design Release Snapshot must include:

- Master Tree version;
- schema version;
- node registry version;
- repository HEAD;
- Penpot file/revision;
- token baseline;
- component baseline;
- screen inventory hash;
- closure matrix summary;
- open P0/P1 defects;
- waivers;
- contradiction state;
- evidence manifest;
- change-impact set;
- approval record.

This becomes the unit of comparison for design drift.

---

# 15. Major finding P1-03 — Research and measurement are under-modeled

The Tree already has `MET` and references research.

But product discovery and pilot evidence need stronger node types.

v4 adds:

- `HYP` — hypothesis;
- `EVIDENCE` — evidence object;
- `NFR` — non-functional requirement;
- `ANL` — analytics event;
- `RELEASE` — release slice;
- `STORY` — implementation/story slice;
- `WAIVER` — controlled deviation;
- `TERM` — canonical terminology;
- `COPY` — controlled UI copy;
- `CHANGE` — source/change event.

This is important because:

**Domain Event ≠ Analytics Event**

and:

**Product Hypothesis ≠ Product Requirement**

and:

**Historical Copy ≠ Canonical UI Copy**.

---

# 16. Major finding P1-04 — Role/persona/surface is strong, but membership context needs a first-class scope

POL has explicit multi-organization identity.

Therefore a screen's identity tuple should be capable of resolving:

`User → Membership → Organization → Role → Persona → Surface`

not merely:

`User → Role → Screen`.

This is critical for delegated permission UX and tenant switching.

---

# 17. Major finding P1-05 — State architecture needs transition ownership

A state node should not only say:

`SUBMITTED`

It should say:

- owner domain;
- valid predecessor;
- valid successors;
- command that causes transition;
- permission required;
- precondition;
- postcondition;
- side effects;
- domain event;
- notification;
- audit event;
- recovery path;
- concurrency rule.

This is especially important for:

- partial acceptance;
- stale basket;
- allocation expiry;
- payment verification;
- delivery handoff;
- permission grants/revokes;
- scanner matching;
- product candidate approval.

---

# 18. Major finding P1-06 — The Master Tree needs artifact boundaries

The repository contains several classes of artifacts:

### Normative
Defines truth.

### Derived
Summarizes normative truth.

### Evidence
Proves something about truth.

### Historical
Records old truth.

### Experimental
Tests a possible future direction.

### Agent-generated
Produced during execution.

v4 adds explicit source/artifact classification.

Without this, a future AI agent may accidentally treat:

- a screenshot;
- an old audit;
- a marketing page;
- a design exploration;
- a generated artifact

as a current product requirement.

---

# 19. Major finding P1-07 — The Master Tree should optimize agent context

The current 8,000+ line document is valuable for humans but expensive as a default agent context.

The agent should NOT load the whole tree for every mutation.

v4 therefore defines:

`Master Tree Core → Bounded View → Node Source Packet`

A node source packet should contain only:

1. authority;
2. relevant decisions;
3. relevant product/domain/API/data sources;
4. canonical node contract;
5. relevant Penpot structure;
6. known contradictions;
7. acceptance criteria;
8. applicable closure profile;
9. required evidence.

This is consistent with the Penpot AI Kit direction: AI design work should operate on real structured Penpot designs, using reusable components/tokens and explicit system rules rather than a flat one-shot generation prompt. citeturn888822search13

---

# 20. Major finding P1-08 — Fitness functions should become executable

The current Tree has many health metrics.

The next step is to convert critical ones into executable checks.

Minimum v4 fitness functions:

### FT-01 — Orphan Node
Fail if a canonical node lacks an upward authority path.

### FT-02 — Orphan Artifact
Fail if a canonical Penpot artifact cannot be traced back to an active or historical node classification.

### FT-03 — Protected Action
Fail if a protected action lacks an explicit permission.

### FT-04 — Theme Parity
Fail if a production visual node lacks required Night coverage.

### FT-05 — Stale Source
Fail or warn when an active source changes and downstream design has no re-verification record.

### FT-06 — Contract Drift
Fail if a screen action maps to an endpoint with a status incompatible with its declared maturity.

### FT-07 — State Drift
Fail if a UI state exists without a corresponding canonical domain/integration/UI interpretation.

### FT-08 — Alias Collision
Fail if one logical alias points to more than one active canonical node.

### FT-09 — Token Violation
Fail if production components use undeclared raw values where semantic tokens exist.

### FT-10 — Historical Leakage
Fail if a source explicitly marked historical/superseded is the only authority behind an active screen.

### FT-11 — Claim Without Authority
Fail for financial/legal/guarantee copy without a Claim contract.

### FT-12 — Unsupported Offline
Fail if a design represents persisted offline write behavior without canonical runtime support.

Architecture governance literature describes fitness functions as executable tests that evaluate implementation against stated design objectives and as a way to shift governance earlier into the delivery flow. citeturn888822search9

---

# 21. Precision Commerce implication

Precision Commerce should not simply sit next to the Master Tree as a color document.

It becomes the canonical visual layer of the design graph:

`Visual Direction → Token → Component → Pattern → Screen → Evidence`

Every visual node should resolve:

- visual direction;
- semantic token refs;
- theme coverage;
- density profile;
- responsive profile;
- RTL profile;
- accessibility profile;
- artifact binding.

The current Precision Commerce document is therefore elevated from “style guide” to:

**Visual Authority Layer**

---

# 22. New Master Tree v4 architecture

The upgraded conceptual model becomes:

```
POL MASTER TREE v4
│
├── 1. AUTHORITY KERNEL
│   ├── Source Authority
│   ├── Decision Authority
│   ├── Scope
│   ├── Lifecycle
│   ├── Supersession
│   └── Historical Containment
│
├── 2. CANONICAL NODE REGISTRY
│   ├── Identity
│   ├── Ownership
│   ├── Type
│   ├── Scope
│   ├── Capability
│   └── Canonicality
│
├── 3. RELATIONSHIP GRAPH
│   ├── Contains
│   ├── Depends On
│   ├── Navigates To
│   ├── Implements
│   ├── Authorized By
│   ├── Audited By
│   ├── Notifies
│   ├── Derives From
│   ├── Aliases
│   └── Supersedes
│
├── 4. EXPERIENCE VIEWS
│   ├── Strategy
│   ├── IA
│   ├── Journey
│   ├── Flow
│   ├── Service Blueprint
│   └── Surface
│
├── 5. PRODUCT / DOMAIN VIEWS
│   ├── Capability
│   ├── Entity
│   ├── State
│   ├── Permission
│   ├── API
│   ├── Event
│   ├── Audit
│   └── Notification
│
├── 6. DESIGN SYSTEM VIEWS
│   ├── Token
│   ├── Component
│   ├── Pattern
│   ├── Theme
│   ├── Density
│   └── Responsive
│
├── 7. ARTIFACT VIEWS
│   ├── Penpot Page
│   ├── Frame
│   ├── Component Variant
│   ├── Prototype
│   └── Frontend Mapping
│
├── 8. EVIDENCE / MATURITY
│   ├── Source Evidence
│   ├── Design Evidence
│   ├── Structural Evidence
│   ├── Runtime Evidence
│   └── Pilot Evidence
│
└── 9. GOVERNANCE / DRIFT
    ├── Change
    ├── Impact
    ├── Waiver
    ├── Claim
    ├── Fitness Function
    └── Release Snapshot
```

The critical improvement is:

> **These are views over one canonical registry, not nine separate trees with independent authority.**

---

# 23. Canonical identity contract v4

Every node must conceptually resolve:

```
NODE
├── node_id
├── node_type
├── canonical_name
├── canonicality
├── lifecycle_status
├── maturity_level
├── priority_scope
├── authority
├── owner
├── scope
├── source_refs
├── decision_refs
├── parent_refs
├── capability_refs
├── alias_of
├── supersedes
├── view_memberships
├── relationship_edges
├── contract_refs
├── state_refs
├── permission_refs
├── artifact_bindings
├── evidence_records
├── closure_profile
├── closure
├── provenance
├── change_impact
└── open_questions
```

---

# 24. Canonicality model

Allowed values:

- `CANONICAL`
- `DERIVED`
- `VIEW_PROJECTION`
- `ALIAS`
- `HISTORICAL`
- `EXPERIMENTAL`

Only `CANONICAL` nodes may be authoritative.

A `VIEW_PROJECTION` may not override a canonical node.

An `ALIAS` must point to exactly one canonical node.

A `HISTORICAL` node must not be used as the sole authority for an active product surface.

An `EXPERIMENTAL` node must carry explicit scope and expiry/review information.

---

# 25. Source health model

Each source should be classified:

- ACTIVE_CANONICAL
- ACTIVE_SUPPORTING
- REVIEW_REQUIRED
- STALE
- HISTORICAL
- SUPERSEDED
- CONFLICTED
- EXPERIMENTAL

This allows the Master Tree to preserve historical documents without allowing them to silently redefine active behavior.

---

# 26. Design authority chain

For current POL design, the visual authority order is:

1. `DECISION_REGISTER.md` for product decisions;
2. current product/domain/API authorities;
3. current `50_MASTER_TREE`;
4. `56_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM`;
5. executable schema / node schema;
6. current Penpot artifact;
7. historical design documents;
8. exploratory artifacts.

A lower-level artifact may refine presentation but may not override a higher authority.

---

# 27. Required v4 migration

The upgrade should happen in the following order:

### Wave 01 — Kernel
- canonicality;
- source state;
- aliases;
- supersession;
- closure profiles;
- evidence arrays;
- relationship arrays;
- artifact bindings.

### Wave 02 — Registry
- canonical screen ID registry;
- capability registry;
- state registry;
- permission registry;
- token registry.

### Wave 03 — Drift control
- source-health mapping;
- contradiction propagation;
- stale-source checks;
- change impact.

### Wave 04 — Penpot closure
- exact artifact IDs;
- page/frame/component bindings;
- Light/Night verification;
- visual baselines.

### Wave 05 — Execution
- agent source packets;
- fitness functions;
- release snapshots;
- resumable execution.

---

# 28. Critical screens that become Golden References

Precision Commerce Golden Reference set:

- Retailer Home
- Product Search
- Product Detail
- Vendor Search
- Vendor Storefront
- Basket
- Allocation Review
- Checkout
- OrderGroup Detail
- Partial Acceptance
- Financial Activity
- Delivery Handoff
- Vendor Order Queue
- Vendor Inventory
- Vendor Scanner
- Permission Editor
- Operations Exceptions
- Financial Investigation
- Master SKU Candidate Review
- Media Provenance Review
- Corporate Landing

Every applicable Golden Reference requires:

**Light + Night + Mobile + Desktop + critical states + accessibility + RTL + structural persistence evidence.**

---

# 29. Human review findings

The Master Tree should be judged on five questions.

### Q1 — Can a product designer understand what to build?

Current answer:

**Yes, strongly.**

### Q2 — Can an engineer understand what runtime contract supports it?

Current answer:

**Mostly.**

### Q3 — Can an AI agent mutate Penpot safely from it?

Current answer:

**Yes for bounded tasks, but not yet with full machine-enforced canonicality and artifact binding.**

### Q4 — Can an auditor detect source/design drift automatically?

Current answer:

**Partially.**

### Q5 — Can two agents work without accidentally creating two truths?

Current answer:

**Not yet reliably enough.**

This is the central reason for v4.

---

# 30. Final verdict on the current Master Tree

The existing Master Tree is valuable because it has correctly recognized something most product design documents miss:

> **A complex B2B platform cannot be designed as a collection of screens.**

Its strongest achievement is the semantic chain:

`Business Capability → Persona → Surface → Screen → Section → Component → Action → State → Permission → Data → API → Event → Audit → Notification → Prototype → QA`

Its main weakness is that the document has grown faster than its meta-model.

It has become a very large and useful **design encyclopedia**, but it now needs a stronger **registry kernel**.

Therefore:

### v3.6 status

**SEMANTICALLY STRONG  
EXECUTION-AWARE  
TRACEABILITY-RICH  
BUT NOT YET REGISTRY-GRADE**

### v4.0 target

**CANONICAL REGISTRY + FEDERATED VIEWS + APPLICABILITY-AWARE CLOSURE + ARTIFACT EVIDENCE + DRIFT CONTROL + AGENT EXECUTION**

That is the architecture required before using the Master Tree as the long-lived control plane for a large agentic Penpot build.

---

# 31. External research used for this audit

### Penpot AI Kit

Penpot's current AI Kit explicitly treats AI design work as structured Penpot editing with real components, tokens, system rules and iterative control rather than flat image generation. url:https://github.com/penpot/penpot-ai-kit

### Design Tokens Community Group

The Design Tokens Community Group's current stable 2025.10 format provides an interoperability layer for design-token exchange, including aliases and context/modifier concepts relevant to theme-aware systems. url:https://www.designtokens.org/TR/2025.10/format/

### WCAG 2.2

WCAG 2.2 remains the relevant accessibility baseline; its reflow requirement explicitly covers usable presentation down to a 320 CSS-pixel equivalent viewport at 400% zoom for applicable content. url:https://www.w3.org/TR/wcag/

### Architecture fitness functions

Fitness functions are useful for shifting architectural governance from periodic inspection toward executable checks that continuously evaluate implementation against stated design objectives. url:https://martinfowler.com/articles/fitness-functions-data-products.html

---

# 32. Audit conclusion

No new business capability is created by this audit.

The purpose is to make the existing product truth:

- more canonical;
- less ambiguous;
- more machine-checkable;
- more resistant to stale documents;
- safer for AI-agent execution;
- more traceable to Penpot;
- more robust for Light/Night Precision Commerce;
- and more useful as a long-lived design control plane.

The Master Tree should now be upgraded to **v4.0** on this basis.
