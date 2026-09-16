# POL Component Contracts v3

## Contract format
Every component defines: purpose, anatomy, hierarchy, dimensions, typography, tokens, variants, states, interaction, accessibility, content rules, responsive behavior.

## Button
Anatomy: label + optional leading/trailing icon.
- Primary: blue-600 fill, white text.
- Secondary: white fill, blue-700 text, gray-200 border.
- Tertiary: transparent, gray-900 text.
- Danger: danger-700 fill, white text.
Sizes: 32 / 40 / 48.
Do not use more than one primary CTA in the same local decision region unless actions are independent.

## TextField
Height 40 default; 48 for primary mobile forms.
Label always visible above field; hint below when needed.
Error appears under field and mirrors exact language used in summary.
Never hide the label inside placeholder-only UI.

## SearchField
Primary navigation/search entry; supports recent searches and explicit clear.
On mobile, search receives immediate focus when the task is clearly search-led.

## QuantityStepper
Minimum target 44×44.
Show current quantity and pack context together.
Prevent values that violate known pack/MOQ constraints where possible; otherwise explain before submission.

## ProductRow
Hierarchy: image/identity → pack → MOQ → price → availability → vendor → quantity action.
Compact default for routine ordering.
Image is secondary to recognition text and commercial facts.

## PriceBlock
Price gets strong emphasis but not misleading dominance.
Show currency/unit and pack relationship adjacent to price.
Changed/future price must have visible state label.

## AvailabilityBlock
Never communicate unknown as available.
States: available / low confidence / stale / unknown / unavailable.
State is communicated with label + icon + color, never color alone.

## VendorOffer
One row/card represents one vendor offer.
Show vendor name, pack, price, MOQ/MOV, availability confidence, and action.
Do not add rating/ranking UI without a canonical algorithm.

## BasketLine
Show product, pack, quantity, price, vendor allocation, constraint/error and line total.
Quantity edits remain local and immediate.

## AllocationGroup
Header: vendor identity + subtotal.
Rows: assigned products.
Exception block: changed/unfulfilled lines.
Primary action: continue/review; never expose algorithm internals by default.

## StatusBadge
Use semantic label and optional icon.
Statuses have a single canonical vocabulary across surfaces.
Avoid badges for purely decorative categorization.

## Timeline
Current state must be visually dominant.
Past states visually recede but remain readable.
Future steps should not be presented as completed.

## QueueItem / QueueTable
Priority order: reason/severity → age/SLA → object → owner → next action.
Sortable columns are visibly annotated and keyboard operable.
Interactive controls in rows remain in tab order.

## EmptyState
Must answer: what is empty, why that is okay (if known), and what to do next.
One primary recovery action.

## ErrorSummary
For multi-field validation, appears at top and receives focus. Local field errors repeat the same wording.
Preserve all user input.

## PermissionDenied
Explain the access outcome without pretending it is a validation error.
Provide allowed next action or escalation path.

## EvidenceUploader
Show accepted formats/size before upload.
Progress, success, retry and failure states are mandatory.
Never lose successfully selected files after a recoverable error.

## Responsive rule
Components reflow before typography shrinks. Never solve desktop overflow by pushing text below readable minimums.
