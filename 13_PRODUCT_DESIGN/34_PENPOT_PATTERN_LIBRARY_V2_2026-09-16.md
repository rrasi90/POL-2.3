# POL — Penpot Pattern Library v2

Status: CANONICAL VISUAL PATTERN LIBRARY

## Purpose
This file defines reusable page compositions so the Penpot file does not become a collection of unrelated screens.

## P-01 Retailer commerce
Use for search/catalog/product flows.
Structure:
1. compact top context bar
2. page title or search
3. filter/sort row
4. result list
5. sticky basket summary when items exist
6. bottom navigation

Rule: the user's next action must be visible without scrolling through promotional content.

## P-02 Retailer home
Order of attention:
1. urgent/needed today
2. open orders
3. reorder
4. saved list
5. browse/search
6. optional evidence-backed promotion

No carousel as the primary hero.

## P-03 Product detail
Top:
image + product identity
Then:
pack → price → availability → MOQ → vendor offers
Bottom sticky action: add to basket.
Secondary information opens progressively.

## P-04 Basket
Top summary + line items + allocation preview + final total + checkout action.
Changed/unavailable lines appear directly next to the affected item.

## P-05 Allocation review
Use grouped vendor sections rather than a technical allocation diagram.
Each group:
vendor identity → supplied lines → subtotal → commercial constraint notes.
A top summary states whether review is required.

## P-06 Order detail
Header: order ID + state + vendor/parent group.
Then timeline, line items, delivery/POD, settlement evidence, issue/return.
Next action is visually isolated from historical information.

## P-07 Vendor operational dashboard
Use queue-first composition:
left/main: actionable queue
right/secondary: selected KPIs
Avoid dashboard wall of equal-sized cards.

## P-08 Vendor table/detail
Desktop: table + right drawer/detail.
Mobile: list → focused detail page.

## P-09 Ops workbench
Three-zone model where width allows:
queue | detail | evidence/context
On smaller desktop, queue and detail share screen; evidence opens in drawer.

## P-10 Field mobile task
One task per screen.
Top: context and progress.
Middle: current task.
Bottom: one dominant next action.

## P-11 Corporate editorial page
Wide hero → concise value proposition → proof → workflow illustration → stakeholder sections → pilot evidence → CTA → footer.
Use B Lotus selectively for brand/editorial display.
Do not use decorative gradients as a substitute for evidence.

## P-12 Form / onboarding
One major question/action per screen where possible.
Persistent progress when multi-step.
Avoid asking for data already known from context.

## P-13 Error recovery
Summary/error → affected component → retained user input → repair action → retry/continue.
Do not clear the form after recoverable errors. citeturn218293search0turn218293search1

## P-14 Empty state
Explain the absence and present the next useful action. Keep illustration secondary.

## P-15 Dense operations
Use:
- compact row heights
- strong column alignment
- pinned header where needed
- restrained color
- explicit state labels
- keyboard focus
- inline actions

Carbon's data-table guidance supports aligned, efficient data presentation with keyboard-accessible sorting and controls. citeturn218293search2

## P-16 Evidence review
Evidence thumbnail/list + metadata + source + status + action.
Never let the attachment itself become the only source of truth; show associated object and state.

## P-17 Notification / confirmation
Use inline success for local actions; notification banner for important system conditions; toast only for lightweight transient confirmation.

## P-18 Navigation
Retailer: bottom nav on mobile.
Vendor/Ops: persistent sidebar on desktop.
Field: task-first bottom nav.
Corporate: compact global header.

## Pattern rules
- Patterns are not components.
- Every pattern must reference canonical components.
- Do not create a new pattern when an existing one can be reused without harming comprehension.
- Never hide a critical commerce constraint to make the screen look cleaner.
