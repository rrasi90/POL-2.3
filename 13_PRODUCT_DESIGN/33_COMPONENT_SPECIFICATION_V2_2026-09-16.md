# POL — Component Specification v2

Status: CANONICAL COMPONENT BUILD SPEC

## 1. Build rule
A component is complete only when its anatomy, variants, states, content behavior, responsive behavior, accessibility behavior and usage restrictions are defined.

## 2. Buttons
### Primary
Use for the single most important action on a screen.
- height: 44 mobile / 40 desktop
- horizontal padding: 16–20
- radius: 10
- label: 13–14px / 600
- icon gap: 8
States: default, hover, pressed, focus, disabled, loading.

### Secondary
For reversible/supporting actions. Never visually compete with primary.

### Tertiary
Text/button-link treatment for navigation or low-emphasis actions.

### Danger
Use only for destructive/reversible-risk actions. Never use red as decorative accent.

## 3. Fields
Anatomy:
`Label → Hint (optional) → Control → Inline error (optional)`
- label remains persistent; do not rely on placeholder as label.
- default height 44.
- focus uses 2px outline.
- error state preserves value.
- validation occurs at meaningful submission boundary rather than aggressive per-keystroke validation unless research justifies it. GOV.UK explicitly recommends preserving entered values and clear recovery guidance. citeturn218293search0turn218293search1

## 4. Search
Anatomy:
`Search icon → Input → Clear → optional filter/sort`
Retailer mobile search is a primary action, not a tiny utility.
Search suggestions must be compact and keyboard/touch navigable.

## 5. Quantity stepper
Anatomy:
`− | quantity | +`
- 44px minimum control target.
- quantity has explicit unit/pack context.
- disabled state when constraint blocks action.
- show MOQ/pack warning adjacent to the stepper, not hidden in tooltip.

## 6. Product row
Canonical hierarchy:
`Image/recognition → Product → Pack → MOQ → Price → Availability → Vendor → Quantity`
Rules:
- price visually strong but not louder than product identity.
- stale/unknown availability is explicit.
- vendor attribution visible before commit.
- routine ordering uses compact rows rather than oversized cards.

## 7. Product card
Use when imagery assists recognition or comparison. Do not use cards everywhere.
Anatomy:
image, product, pack, price, availability, vendor, primary action.

## 8. Vendor offer
Anatomy:
`Vendor → Price → Pack → MOQ/MOV → Availability freshness → Action`
Never imply “best” unless supported by canonical algorithm and displayed as such.

## 9. Basket line
Anatomy:
`Product identity → pack → quantity → unit/line price → line total → remove`
Secondary metadata is collapsible on mobile.

## 10. Allocation group
Header contains vendor name and subtotal where useful.
Rows are grouped by assigned vendor. Changes after revalidation are visually prominent.
The user should understand who supplies each line without seeing internal object names such as AllocationPlan.

## 11. Status
Every operational status uses three layers:
1. text label
2. optional semantic icon
3. color/accent
Never color alone.

Examples:
- آماده ارسال
- در انتظار تأیید
- موجودی نامشخص
- نیازمند بررسی

## 12. Queue item
Canonical hierarchy:
`Severity/State → Reason → Age/SLA → Owner → Next action`
Avoid KPI-first layouts in work queues.

## 13. Data table
Use tables only when comparing multiple records benefits from aligned columns.
- sortable headers are keyboard-accessible.
- interactive controls inside cells remain in tab order.
- mobile transforms to stacked rows or a focused detail drawer instead of shrinking desktop table indefinitely.
Carbon explicitly specifies keyboard sorting and interactive controls inside data cells. citeturn218293search2turn218293search7

## 14. Empty state
Structure:
`What is empty → Why it matters → Primary action → Optional secondary action`
Avoid decorative illustrations unless they improve comprehension.

## 15. Error pattern
Form validation:
- page-level summary for multi-field errors
- field-level message adjacent to offending field
- preserve all user-entered values
- move focus to summary when appropriate
GOV.UK recommends both an error summary and field-level messages for validation errors. citeturn218293search3

Service error:
- explain what happened
- state what the system will do next
- provide retry/recovery
- preserve work where feasible

## 16. Loading
Use skeletons only when layout is predictable. Otherwise use a focused progress state.
Never block the whole surface when only a local section is loading.

## 17. Notification banner
Reserve for important system-level status, not field validation. Keep aligned to the content width and avoid stacking multiple banners. citeturn218293search11

## 18. Modal / sheet
Use when the user must make a focused decision without losing context.
Avoid using modals for long workflows that deserve a page.
Mobile: bottom sheet preferred for contextual actions.
Desktop: centered modal for confirmation, side drawer for inspection.

## 19. Timeline
Anatomy:
`timestamp → state → actor/source → action/evidence`
Current state is visually dominant; historical entries recede.

## 20. Evidence uploader
Show:
- accepted file types
- size constraint
- selected files
- upload progress
- failure + retry
- submitted state
Never pretend an upload is completed before server confirmation.

## 21. Profile / context
Separate:
`Person → Organization membership → Persona/job context → Security`
UI must not imply permissions that are not enforced by application boundary.

## 22. Component QA checklist
For every component:
- RTL
- long Persian text
- mixed Persian/Latin
- keyboard focus
- disabled
- loading
- error
- empty
- permission denied where relevant
- 200% text scaling
- mobile width
- desktop width
- semantic color contrast
- no state encoded only by color
