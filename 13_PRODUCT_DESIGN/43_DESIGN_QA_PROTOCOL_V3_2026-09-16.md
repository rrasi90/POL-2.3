# POL Design QA Protocol v3

## Gate A — Research fidelity
- Every non-trivial pattern maps to a documented principle or verified user need.
- No screen decision exists solely because it appeared in an earlier design.

## Gate B — Token integrity
- No raw color outside token definitions.
- No arbitrary spacing values.
- Approved typography only.
- B Lotus use follows the typography policy.

## Gate C — Component integrity
- Component uses canonical states.
- Focus/disabled/loading/error states exist where relevant.
- Variants are named consistently.
- No duplicate component for the same semantic job.

## Gate D — Screen integrity
- Primary job obvious within first scan.
- One dominant CTA where a single action is expected.
- Critical commercial constraints visible before commitment.
- Empty/loading/error/recovery states represented.
- Long Persian labels tested.
- Mixed RTL/LTR values render correctly.

## Gate E — Accessibility
- Contrast checked for text and UI boundaries.
- Keyboard order is logical.
- Focus is visible.
- Status does not rely on color alone.
- Touch targets are usable.
- Error summary/focus behavior defined for multi-error forms.

## Gate F — Prototype
- Normal path passes.
- Failure branch passes.
- Back/cancel passes.
- Data is preserved across recoverable errors.
- Terminal state communicates outcome.

## Gate G — Handoff
Every screen must have:
- screen ID
- components used
- token dependencies
- state matrix
- copy source
- analytics event IDs
- responsive behavior
- accessibility annotations
- implementation notes

## Defect severity
P0: business rule or authorization visual contradiction.
P1: critical task cannot be completed/recovered.
P2: usability/accessibility issue in common flow.
P3: visual consistency or minor content issue.
P4: cosmetic refinement.

P0/P1 block design approval.
P2 blocks handoff for the affected flow unless explicitly waived.
P3/P4 may be batched.

## Final rule
A screen that looks polished but fails the research, accessibility, task, or state gates is not complete.
