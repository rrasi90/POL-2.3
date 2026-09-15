# Prototype & Figma Execution Plan

## Rule
Figma is the visual execution layer; this repository remains the written product/design source of truth.

## Phase 1 Figma structure
Create one POL design-system file containing:
- Foundations
- Tokens
- Components
- Patterns
- Accessibility annotations
- Retailer screens
- Vendor screens
- Ops screens
- Field screens
- Corporate website

## Prototype sequence
### Prototype A — Retailer core loop
Onboarding → home → search → add to basket → multi-vendor allocation → checkout → order tracking → reorder.

### Prototype B — Vendor core loop
Dashboard → order queue → inventory → daily confirmation → referral.

### Prototype C — Ops
Queue → exception detail → action → audit trail.

### Prototype D — Field
Task list → retailer activation → assisted order → follow-up.

### Prototype E — Corporate
Landing → persona selection → value proposition → CTA.

## Prototype fidelity
- Low fidelity first for IA and task flow.
- Mid fidelity for interaction and state validation.
- High fidelity only after component and token rules stabilize.

## Validation gates
A prototype cannot advance because it looks polished. It advances when:
- task flow is coherent;
- edge states are designed;
- accessibility annotations exist;
- content hierarchy is correct;
- canonical backend states map visibly to UI states.

## Figma implementation rule
Use the repository documents to drive Figma; do not let undocumented Figma decisions silently become product requirements. Promote stable visual/product decisions back into this directory.
