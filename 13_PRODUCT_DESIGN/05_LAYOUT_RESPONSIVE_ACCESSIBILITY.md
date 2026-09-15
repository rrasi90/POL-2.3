# POL Layout, Responsive & Accessibility Contract

## Responsive strategy
POL uses one content model with role-appropriate layouts rather than separate product logic per breakpoint.

### Mobile
Optimize for:
- rapid reorder;
- search and quantity entry;
- order status;
- notifications;
- field tasks.

Avoid desktop tables compressed into horizontal scroll unless the table is genuinely unavoidable.

### Tablet
Use split views where they reduce navigation cost: list/detail, order summary/line items, task/context.

### Desktop
Optimize for:
- multi-column catalog operations;
- vendor inventory;
- order queues;
- financial/reconciliation review;
- operational tables;
- admin analytics.

## Layout primitives
- page shell
- top bar
- side navigation
- mobile bottom navigation
- content container
- section header
- filter bar
- list/table region
- detail panel
- sticky action bar where appropriate

## Accessibility baseline
Target WCAG 2.2 AA-oriented implementation. WCAG 2.2 requires at least 24x24 CSS px pointer targets in the normal case; POL should use larger targets where practical because its primary retailer workflow is touch-heavy. citeturn990483search0

Required:
- visible keyboard focus;
- logical focus order;
- semantic labels;
- no color-only status communication;
- sufficient contrast;
- readable text at zoom;
- reduced-motion support;
- accessible authentication interaction;
- preserved form values after validation errors.

WCAG 2.2's accessible-authentication and redundant-entry criteria are directly relevant to OTP and onboarding. citeturn990483search2turn990483search5

## Persian / RTL
- Default UI direction: RTL.
- Numeric strings, SKU, barcode, IDs, URLs and technical values may be LTR islands.
- Bidirectional text must be tested with Persian + Latin + numeric mixed content.
- Icons indicating direction should mirror only when semantic direction changes.
- Tables require deliberate column ordering for RTL.

## Error and recovery
Use explicit, actionable errors. Preserve user-entered values where safe; tell the user what happened and how to fix it. This aligns with established accessible error-message guidance. citeturn990483search1turn990483search9

## Performance UX
Design loading, offline/slow-network and retry states from the first component pass; do not add them after visual design is complete.
