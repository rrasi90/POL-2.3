# POL — Executable Master Tree Schema & Closure Contract

**Document ID:** `POL-DESIGN-SCHEMA-001`  
**Version:** `1.0.0`  
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

The human-readable Master Tree remains the semantic authority. This schema exists so an agent, validator or CI job can detect incomplete closure instead of inferring completeness from prose.

## 2. Canonical node record

Every canonical node should resolve to the following conceptual structure:

`NODE_ID + NODE_TYPE + AUTHORITY + OWNERSHIP + SCOPE + RELATIONSHIPS + CONTRACTS + STATES + EVIDENCE + CLOSURE`

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
13. an offline/queued state is represented without canonical runtime support.

## 12. Scope rule

This schema does not create new product capabilities.

It only makes existing product/design/engineering truth explicit and machine-checkable.

For POL, the authoritative business behavior remains the Repository Source of Truth and Decision Register.
