# POL — Executable Master Tree Schema & Closure Contract

**Document ID:** `POL-DESIGN-SCHEMA-001`  
**Version:** `2.0.0`  
**Date:** 2026-09-21  
**Status:** ACTIVE / MACHINE-CONSUMABLE DESIGN GOVERNANCE  
**Repository:** `rrasi90/POL-2.3`  
**Branch:** `product-architecture-evolution-2026-09-20`

---

## 1. Purpose

The POL Master Tree is now governed by a machine-consumable contract in addition to the human-readable specification.

This document defines the canonical record shape for:

- Master Tree nodes
- multidimensional closure
- evidence
- command/mutation contracts
- change impact
- claims/promises

The human-readable Master Tree remains the semantic authority. In v4 this document defines the registry kernel so an agent, validator or CI job can detect canonicality, source drift, closure applicability, graph integrity and artifact drift instead of inferring completeness from prose.

## 2. Canonical node record

Every canonical node should resolve to the following conceptual structure:

`NODE_ID + NODE_TYPE + CANONICALITY + AUTHORITY + OWNERSHIP + SCOPE + RELATIONSHIPS + CONTRACTS + STATES + ARTIFACTS + EVIDENCE + CLOSURE`

### Mandatory identity

- `id`
- `type`
- `name`
- `lifecycle_status`
- `priority_scope`

### Mandatory traceability

- `source_refs`
- `decision_refs` where a decision exists
- `parent_refs`
- `relationship_edges`
- `capability_refs`

### Mandatory behavior for actionable nodes

- `outcome`
- `actions`
- `permissions`
- `preconditions`
- `state_refs`
- `contract_refs`

### Mandatory evidence

- `evidence_refs`
- `evidence_level`
- `closure`

## 3. Multidimensional closure

A node is not complete because a single status says COMPLETE.

The canonical closure vector is:

`CAPABILITY_PRESENT → OUTCOME → JOURNEY → SCREEN/PATTERN/NON_UI → STATES → ACTION → PERMISSION → DATA → API/BOUNDARY → EVENT/AUDIT/NOTIFICATION → PROTOTYPE → A11Y → RTL → RESPONSIVE → NETWORK → VISUAL → STRUCTURAL → RUNTIME → PILOT`

Each dimension is independently recorded.

### Closure states

- `NOT_APPLICABLE`
- `OPEN`
- `DEFINED`
- `VERIFIED`
- `BLOCKED`
- `WAIVED`

A `WAIVED` dimension requires a waiver reference and review/expiry condition.

## 4. Command contract

Every critical write action resolves to:

`INTENT → PRECONDITION → AUTHORIZATION → VALIDATION → MUTATION → EXPECTED_STATE → SIDE_EFFECTS → POSTCONDITION → EVIDENCE`

Required fields:

- `intent_id`
- `action_id`
- `preconditions`
- `permission_refs`
- `expected_state_transition`
- `idempotency_policy`
- `concurrency_policy`
- `postconditions`
- `audit_required`
- `notification_effects`
- `navigation_effect`
- `rollback_reference`

## 5. Evidence contract

Evidence is classified as:

- `SOURCE_VERIFIED`
- `DESIGN_VERIFIED`
- `STRUCTURAL_VERIFIED`
- `VISUAL_VERIFIED`
- `RUNTIME_VERIFIED`
- `PILOT_VERIFIED`
- `INFERRED`
- `OPEN_DECISION`

Evidence records should include:

- evidence ID
- source/artifact reference
- captured revision
- captured timestamp
- evaluator
- verification scope
- result
- notes

A historical screenshot, stale CI run or successful tool return cannot substitute for current evidence.

## 6. Data freshness / provenance contract

Decision-critical data may carry:

- `owner`
- `source`
- `observed_at`
- `valid_until` or `freshness_class`
- `confidence`
- `transformation`
- `stale_policy`

Raw provenance is not necessarily user-facing. It governs which label, warning, confidence state or mutation restriction the UI must render.

## 7. Agent execution contract

Every design mutation must have:

- `run_id`
- `wave_id`
- `step_seq`
- `mutation_intent_id`
- `context_id`
- `repo_head`
- `penpot_revision_before`
- `penpot_revision_after`
- `expected_delta`
- `rollback_reference`
- `approval_required`
- `semantic_evidence`
- `structural_evidence`
- `visual_evidence`

## 8. Change impact contract

A source change produces a bounded dependency set:

`SOURCE → CAPABILITY → ENTITY → API → SCREEN → COMPONENT → STATE → PROTOTYPE → QA`

Each affected node receives:

- `impact_level`: `NONE | LOW | MEDIUM | HIGH | CRITICAL`
- `reverification_required`
- `reverification_scope`
- `owner`

## 9. Claim / Promise contract

Public or high-risk operational copy must resolve:

`CLAIM_ID → TEXT → SOURCE → AUTHORITY → VALID_TIME → AUDIENCE → SURFACE → RISK → REVIEW_OWNER`

This prevents GTM pitch, pilot language, historical examples or stale documentation from silently becoming canonical UI claims.

## 10. Closure rule

A node may be called:

### DESIGN_DEFINED

when the semantic and structural specification exists.

### PENPOT_BUILT

when the Penpot artifact exists and structural persistence is proven.

### PROTOTYPED

when the intended interaction path and critical failure branches exist.

### IMPLEMENTATION_READY

when contract, states, permissions, data and responsive/accessibility requirements are mapped.

### VERIFIED

only after the applicable evidence dimensions are present.

### RUNTIME_VERIFIED

only when the real runtime boundary confirms the behavior.

### PILOT_VERIFIED

only when pilot evidence confirms it.

Never collapse these stages.

## 11. Validation rules

A validator should fail closure when:

1. a canonical node has no source;
2. a protected action has no permission;
3. a write action has no preconditions;
4. a stateful mutation has no expected transition;
5. a critical node has no recovery definition;
6. a Penpot mutation has no persistence proof;
7. a critical checkpoint has no semantic/structural/visual evidence;
8. a `WAIVED` closure dimension has no waiver;
9. a source change has affected nodes but no re-verification set;
10. a public claim has no authority source;
11. a capability is marked closed while a mandatory closure dimension remains `OPEN` or `BLOCKED`;
12. a CONTRACT_ONLY API is represented as runtime-verified;
13. an offline/queued state is represented without canonical runtime support;
14. an applicable visual node has no theme parity declaration;
15. an applicable visual node is marked visually closed from Light-only evidence;
16. a visual node bypasses semantic token usage without a documented waiver;
17. an invalid density profile is assigned to a surface;
18. a Night theme is represented as a naive inversion/filter rather than semantic theme tokens.

## 12. Precision Commerce visual contract

Canonical visual authority: `13_PRODUCT_DESIGN/56_POL_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM_2026-09-21.md`.

For visual node types `SCR`, `SEC`, `CMP`, `PATTERN` and `PEN`, the node should resolve the following additional fields:

- `visual_direction` = `PRECISION_COMMERCE`
- `theme_coverage` = `LIGHT_AND_NIGHT` unless explicitly `THEME_NOT_APPLICABLE`
- `density_profile` appropriate to the owning surface
- `visual_token_refs` for semantic token traceability

Visual closure must not be inferred from screenshot existence alone.

Night theme is a first-class variant. It must preserve behavior and component anatomy while using the Night semantic token layer.

## 12. Scope rule

This schema does not create new product capabilities.

It only makes existing product/design/engineering truth explicit and machine-checkable.

For POL, the authoritative business behavior remains the Repository Source of Truth and Decision Register.



## 13. Master Tree v4 registry contract

### 13.1 Canonicality

Allowed values:

- CANONICAL
- DERIVED
- VIEW_PROJECTION
- ALIAS
- HISTORICAL
- EXPERIMENTAL

Only CANONICAL nodes can act as active authority.

### 13.2 Source health

Allowed values:

ACTIVE_CANONICAL, ACTIVE_SUPPORTING, REVIEW_REQUIRED, STALE, HISTORICAL, SUPERSEDED, CONFLICTED, EXPERIMENTAL.

Source health is separate from lifecycle.

### 13.3 Aliases and supersession

An ALIAS resolves to exactly one canonical node.

Superseded nodes retain replacement references and downstream impact.

### 13.4 Closure profiles

The closure vector is global, but applicability is node-type specific.

Every canonical node receives a closure profile that declares which closure dimensions are mandatory, optional or not applicable.

The validator must never interpret NOT_APPLICABLE as a failure.

### 13.5 Evidence cardinality

Evidence is a collection.

A node may have zero-to-many evidence records.

Each record resolves:

dimension, evidence_type, reference, revision, timestamp, evaluator, scope and result.

### 13.6 Relationship cardinality

Relationship edges are a collection.

A node may have zero-to-many typed edges.

No edge may be inferred from textual proximity alone.

### 13.7 Artifact binding

Penpot-backed nodes require explicit artifact bindings when artifact identity is material.

At minimum the binding should preserve:

Penpot file → page → frame/component/variant → revision → persistence status → verification evidence.

### 13.8 Maturity

Maturity and lifecycle are independent:

L0_CONCEPT → L1_SPECIFIED → L2_MAPPED → L3_DESIGNED → L4_PROTOTYPED → L5_CONTRACTED → L6_IMPLEMENTED → L7_VERIFIED → L8_PILOT_OBSERVED → L9_SUPERSEDED_OR_DEPRECATED.

A Penpot frame alone cannot establish runtime or pilot maturity.

### 13.9 Visual contract

For SCR, SEC, CMP, PATTERN and PEN nodes, the machine contract requires:

visual_direction = PRECISION_COMMERCE

theme_coverage = LIGHT_AND_NIGHT unless explicitly theme-not-applicable

density_profile = surface-appropriate profile

visual_token_refs = semantic token references

artifact_bindings = persisted Penpot evidence where applicable.

### 13.10 Fitness functions

The v4 validator should support at least:

FT-01 Orphan Node
FT-02 Orphan Artifact
FT-03 Protected Action
FT-04 Theme Parity
FT-05 Stale Source
FT-06 Contract Drift
FT-07 State Drift
FT-08 Alias Collision
FT-09 Token Violation
FT-10 Historical Leakage
FT-11 Claim Without Authority
FT-12 Unsupported Offline

### 13.11 Token interoperability

POL semantic token governance should remain compatible with the Design Tokens Community Group 2025.10 exchange format for future tool/code interoperability.

The external token format is an interchange mechanism; POL semantic names and authority remain project-owned.

### 13.12 Release snapshot

A design release must bind:

Master Tree version + node schema version + repository HEAD + Penpot revision + token baseline + component baseline + closure summary + open defects + waivers + contradiction state + evidence manifest + approval record.

