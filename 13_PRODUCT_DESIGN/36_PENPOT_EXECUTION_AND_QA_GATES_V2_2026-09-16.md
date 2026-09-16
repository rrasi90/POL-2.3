# POL — Penpot Execution & QA Gates v2

Status: CANONICAL PENPOT PRODUCTION CHECKLIST

## Phase 1 — Foundations
Create and lock:
- colors
- typography
- spacing
- radius
- elevation
- grid
- RTL/LTR behavior
- accessibility annotation
- content rules

Gate 1: no screen design begins until the token board and typography specimen are complete.

## Phase 2 — Real components
Create actual reusable components/variants for:
- buttons
- fields
- search
- quantity stepper
- product row/card
- vendor offer
- basket line
- allocation group
- order status
- queue item/table
- feedback/error
- evidence
- navigation

Gate 2: no repeated visual pattern is allowed to remain detached if it can be represented as a reusable component.

## Phase 3 — Pattern library
Build P-01 through P-18 from the canonical pattern library.

Gate 3: each pattern references components and tokens; no hidden raw styles.

## Phase 4 — Core retailer
Build R-01 through R-13, starting with the transactional loop:
R-03 → R-04 → R-06 → R-07 → R-08 → R-09.

Gate 4: transaction path is visually coherent before secondary screens are polished.

## Phase 5 — Vendor
Build V-01 through V-12. Prioritize dashboard, order queue/detail, inventory, daily confirmation.

Gate 5: operational user can identify reason, age, owner and next action at a glance.

## Phase 6 — Ops
Build O-01 through O-10. Prioritize queue → detail → evidence → action → audit.

Gate 6: queues are functional compositions, not decorative KPI walls.

## Phase 7 — Field
Build F-01 through F-05.

Gate 7: weak-network and retry paths are represented.

## Phase 8 — Corporate
Build C-01 through C-08.

Gate 8: every claim is backed by approved evidence and copy rules.

## Phase 9 — Prototypes
Create critical flows from `35_PROTOTYPE_FLOWS_AND_FAILURE_BRANCHES_V2_2026-09-16.md`.

Gate 9: every critical happy path has a realistic failure branch.

## Phase 10 — Accessibility QA
Check:
- keyboard focus visibility
- logical tab order
- target size
- contrast
- non-color status cues
- screen-reader naming annotations
- long Persian text
- mixed direction
- zoom/text scaling
- reduced motion behavior

For dense tables, sortable headers and controls inside data cells must remain keyboard-operable, matching Carbon guidance. citeturn218293search2

## Phase 11 — Content QA
Check:
- no lorem ipsum
- no unexplained English jargon
- no fake claims
- no generic errors
- no clipped Persian
- Toman/currency format consistent
- product pack/unit language consistent

## Phase 12 — Visual QA
Check at:
- 360×800
- 390×844
- 768×1024
- 1024×768
- 1440×1024

Check:
- alignment
- whitespace rhythm
- visual hierarchy
- state visibility
- component consistency
- image crop consistency
- card density
- shell balance

## Phase 13 — Design-to-build QA
For every screen document:
- route/surface
- frame name
- components
- token usage
- state variants
- events/analytics
- backend source of truth
- authorization assumption
- responsive behavior

## Final gate
A screen is DONE only when it is:
1. structurally complete;
2. visually coherent;
3. componentized;
4. responsive;
5. accessible;
6. state-complete;
7. content-complete;
8. domain-consistent;
9. prototype-connected where required;
10. implementation-ready.

A visually beautiful screen that fails one of these is not DONE.
