# POL Screen-Level Wireframe Specification — Retailer + Vendor

**Date:** 2026-09-16  
**Status:** CANONICAL VISUAL HANDOFF  
**Scope:** `04 — Retailer` + `05 — Vendor`  
**Purpose:** Convert the page/section inventory into directly drawable Penpot layouts.

> This document defines visual structure, hierarchy, components, states and responsive behavior. It does not create business rules. Product, domain, authorization, payment-custody and commercial rules remain governed by the canonical POL decision/product/API documents.

## 0. Research-backed visual rules

1. One primary task per screen; navigation should not compete with the task. GOV.UK recommends simplifying the journey before adding navigation, and using task-oriented structures for clear transactional journeys. [1]
2. Use summary blocks for key facts, but do not turn tabular information into decorative cards. GOV.UK explicitly distinguishes summary lists from tables and task lists. [2]
3. Keep dashboards operational and high-level rather than becoming a wall of charts. [3]
4. Keep text contrast at or above WCAG AA targets: normal text 4.5:1, large text 3:1. Status cannot rely on color alone. [4]
5. Persian UI is RTL by default. Numbers, SKUs, URLs, phone numbers and technical identifiers use controlled LTR spans.
6. `B Lotus` is a POL display/document font, used for hero titles, major headings, printable documents and selected brand moments. `Vazirmatn` is the operational UI font for dense tables, controls, numbers, labels and form fields. This hybrid rule avoids sacrificing small-size UI legibility while preserving the requested Persian visual character.

---

# 1. Global Penpot layout tokens

## 1.1 Mobile

Reference frame: `390 × 844`.

- outer horizontal padding: `20`
- content width: `350`
- section gap: `24`
- component gap: `12`
- compact data gap: `8`
- bottom safe area: `16`
- sticky action bar height: `72–84`

## 1.2 Desktop

Reference frame: `1440 × 1024`.

- app shell left/right content padding: `32`
- max content width: `1280`
- page section gap: `32`
- card gap: `16`
- table row target height: `56`
- compact row target height: `48`
- sidebar: `248`

## 1.3 Type scale

### B Lotus display
- Display XL: `36 / 44`, weight regular/bold depending on specimen
- Display L: `30 / 38`
- Heading 1: `26 / 34`
- Heading 2: `22 / 30`
- Heading 3: `18 / 26`

### Vazirmatn UI
- Body L: `16 / 26`
- Body: `14 / 22`
- Body compact: `13 / 20`
- Caption: `12 / 18`
- Numeric KPI: `24 / 30` with tabular figures where supported

Minimum production body text: `14px` in operational desktop UI; `15–16px` for primary mobile copy. Avoid `9–11px` body text.

## 1.4 Color roles

Use semantic roles, not raw hex in component specs.

- `surface.canvas`: warm near-white
- `surface.card`: white
- `surface.elevated`: white
- `surface.dark`: Midnight Navy `#0A1730`
- `brand.primary`: Blue `#2563EB`
- `brand.primary-strong`: `#1D4ED8`
- `accent.gold`: `#F7D4B6`
- `text.primary`: deep navy/charcoal
- `text.secondary`: muted slate
- `border.subtle`: cool light neutral
- `state.success`: accessible green role
- `state.warning`: amber role
- `state.danger`: red role
- `state.info`: blue role

Status pattern: icon + label + color + optional short reason.

---

# 2. Retailer — POL Market

## R-01 Onboarding

### R-01-A Welcome
Frame composition:
1. compact POL Market logo top center
2. B Lotus hero line
3. one-sentence value proposition
4. product image/illustration area, not carousel
5. primary CTA: `شروع کنید`
6. secondary text link: support/help

Do not show pricing or marketing claims here.

### R-01-B Phone
1. title
2. explanatory one-liner
3. phone field with Iran formatting
4. primary CTA: `ادامه`
5. inline validation region

### R-01-C OTP
1. title
2. destination phone summary
3. 6-digit OTP field
4. resend state
5. edit phone action
6. error region

### R-01-D Shop context
Use a summary card with:
- نام فروشگاه
- نام مالک/مخاطب
- شهر/ناحیه
- organization/context
- primary `تأیید و ادامه`

### R-01-E Activation success
Show:
- success indicator
- what is now possible
- one next action: `اولین خرید را شروع کنید`

---

## R-02 Home

**Primary job:** decide the next operational action.

Vertical order:
1. top bar: logo + shop context + notification
2. greeting using B Lotus at `22–26px`
3. `امروز` action strip: tasks requiring action
4. open-order summary cards
5. `خرید مجدد` recent rows
6. saved lists
7. search/category entry
8. optional evidence-backed promotion block

Do not use a hero carousel.

Mobile bottom nav:
`خانه | خرید | سفارش‌ها | سبد | حساب`

Primary home CTA is contextual, not a permanent giant button.

---

## R-03 Search / Catalog

Top-to-bottom:
1. sticky search field
2. recent searches row if available
3. category shortcuts
4. filter/sort control row
5. result count + query
6. compact ProductRow list

ProductRow visual hierarchy:
- left: product image/avatar
- center: product name + pack
- secondary: vendor/availability
- price and MOQ grouped
- right/bottom: QuantityStepper + add action

No-result state:
- restate query
- suggest alternative spelling/category
- CTA `نمایش همه محصولات`

---

## R-04 Product Detail

Mobile structure:
1. product image
2. product name + pack
3. price block
4. availability/freshness
5. MOQ/MOV constraint
6. quantity stepper
7. vendor offers accordion/list
8. `افزودن به سبد` sticky action
9. saved/reorder tertiary action

Important: commercial constraints are visible before quantity commitment.

Desktop companion layout: two-column, image/identity left; commercial decision panel right.

---

## R-05 Vendor Comparison

Use a comparison table/list, not vendor profile cards.

Header:
- product summary
- requested quantity

Each vendor row:
`Vendor | Price | Pack | MOQ/MOV | Availability | Allocation impact | Select`

Selected row gets a structural selection treatment, not only color.

Avoid labels such as "best vendor" unless backed by canonical ranking logic.

---

## R-06 Basket

Order of sections:
1. page title + item count
2. basket line groups
3. vendor allocation summary
4. changed/unavailable items
5. vendor subtotals where useful
6. final total summary
7. contact/address
8. primary CTA `ادامه و بررسی`

BasketLine:
- product identity
- pack
- qty stepper
- unit/line price
- vendor
- state
- remove/save

Sticky mobile total bar contains only total + primary CTA.

---

## R-07 Allocation Review

Purpose headline: `نحوه تأمین سفارش را بررسی کنید`.

Each AllocationGroup contains:
- vendor identity
- assigned lines
- subtotal
- availability note
- changed-price warning where applicable

Unfulfilled lines receive a separate warning group.

Primary actions:
- `تأیید و ادامه`
- secondary `اصلاح سبد`

Do not expose internal AllocationPlan terminology to the retailer.

---

## R-08 Checkout / Confirmation

Use one primary review page where possible.

Sections:
1. order summary
2. delivery/contact
3. direct settlement method
4. evidence upload if applicable
5. final total
6. confirmation checkbox only when legally/business required
7. `ثبت سفارش`

Use a sticky footer on mobile.

Error recovery must preserve all previously entered values.

---

## R-09 Order Group

Parent screen:
1. order-group ID
2. overall state
3. total
4. vendor child-order cards
5. major exception banner
6. timeline summary

Child order detail:
- vendor
- items
- accepted/rejected qty
- milestones
- POD/delivery evidence
- settlement evidence
- return/issue CTA

Use compact summary lists for metadata and tables only where actual tabular comparison is necessary. [2]

---

## R-10 Reorder

Entry points should converge on the same reorder pattern.

Header:
- original order date
- original vendor context

Line list:
- old pack
- old price
- current price
- availability
- quantity
- changed-item marker

Primary CTA: `افزودن موارد قابل خرید به سبد`

Before checkout, show historical changes inline.

---

## R-11 Returns / Disputes

Flow frames:
1. select order
2. select issue type
3. select items + quantity
4. evidence upload
5. review submission
6. submitted
7. tracking
8. vendor response
9. operator review when needed
10. final resolution

Each step has a single primary action.

---

## R-12 Support

Three-pane concept on desktop; stacked on mobile.

Mobile:
- category
- case title
- description
- attachment
- submit

Thread view:
- status chip
- message stream
- attachment previews
- reply field
- resolution block

---

## R-13 Account

Sections:
1. profile summary
2. shop information
3. addresses
4. notification preferences
5. security/session management
6. active organization
7. help/usage guide

Use grouped sections with short headings, not one giant form.

---

# 3. Vendor — POL Vendor

Reference desktop frame: `1440 × 1024`.

## V-01 Dashboard

Structure:
1. global header/context
2. page title + date/context
3. critical work queue block
4. SLA/aging strip
5. inventory confirmation prompt
6. selected operational KPIs
7. secondary trend summary

Never build the screen as a wall of unrelated KPI cards. High-level dashboards should summarize rather than force interpretation of many charts. [3]

Queue item hierarchy:
`Severity/State → Reason → Age → Owner → Next action`

---

## V-02 Orders Queue

Layout:
- page header
- search
- filter bar
- saved filter state
- queue table
- pagination/load more

Columns:
`Order | Retailer | Age/SLA | Amount | State | Exception | Next action`

Row height `56px` default.

Mobile: convert each row to a structured OrderCard with the next action visible.

---

## V-03 Order Detail

Header strip:
- order ID
- state
- age/SLA
- retailer
- total
- next action

Main body two columns:
- left: line items and quantities
- right: action panel

Below:
- delivery/handoff
- evidence
- timeline/audit

Partial accept interaction must visually distinguish accepted, rejected and pending quantities.

---

## V-04 Catalog

Top:
- search
- category/filter
- add/edit action

Main table/list:
`Product | Vendor SKU | Pack | Price | Listing status | Image | Edit`

Image column stays small; operational fields remain dominant.

---

## V-05 Pricing

Header summary:
- current effective price
- next effective price
- last change

Main section:
- editable price field
- effective date/time
- validation message

History appears below, using a compact timeline/table.

---

## V-06 Inventory

Top summary:
- inventory freshness
- last confirmation
- number of stale items

Main table:
`Product | Physical qty | Reserved | Available/sellable | Freshness | Last confirmation | Action`

Stale/unknown state must include explicit text, not only a colored dot.

---

## V-07 Daily Inventory Confirmation

Single focused workflow:
1. review
2. edit exceptions
3. confirm
4. receipt

Avoid side navigation inside the flow.

Confirmation screen shows:
- count of changed items
- count unchanged
- warnings
- timestamp
- operator/persona context

---

## V-08 Referral

Use a focused card:
- referral code/link
- share/copy
- attributed retailers
- redemption state

Do not show reward balance, wallet, credit or payout mechanics.

---

## V-09 Customers

Desktop split:
- left list/search
- right customer summary

Customer summary:
- shop identity
- relationship context
- order history
- referral context

Use summary lists for key facts rather than over-cardization. [2]

---

## V-10 Reconciliation / Documents

Top filters:
- order/invoice reference
- status
- date range

Main table:
`Reference | Amount | Evidence | Reconciliation state | Exception | Action`

Evidence viewer opens as side panel on desktop.

---

## V-11 Staff / Access

Main table:
`Name | Job function | Membership | Status | Last active | Action`

Invite flow:
1. person
2. function/persona
3. context
4. review
5. invite

Permission labels are descriptive and must reflect actual backend authorization.

---

## V-12 Vendor Profile

Sections:
- business identity
- operating context
- notification preferences
- security
- sessions

Keep profile editing separate from operational inventory/pricing workflows.

---

# 4. Component placement rules for Penpot

## ProductRow
Minimum visual order:
`image → product → pack → MOQ → price → availability → vendor → quantity`

## QueueItem
Minimum visual order:
`state/severity → reason → age → owner → action`

## SummaryList
Use for key-value facts such as order ID, vendor, dates, current status. Do not use for real tables. [2]

## Sticky mobile action bar
Use only when the user's primary task is blocked without an obvious next action. Never use it for more than one primary CTA.

## Warning treatment
Warning block includes:
- icon
- heading
- reason
- consequence
- recovery action

## Empty state
Always contain:
- what is empty
- why that is normal/known if appropriate
- one recovery action

## Error state
Always contain:
- what happened
- what can be done now
- retry/edit action
- preserve entered values where possible

---

# 5. Penpot construction order

For each screen:
1. Draw frame.
2. Place shell/navigation.
3. Place page title and primary task statement.
4. Place critical decision component.
5. Place secondary information.
6. Place primary CTA.
7. Add one representative success state.
8. Add one representative error/empty state.
9. Add responsive annotation.
10. Convert repeated elements into components/variants.

Do not polish iconography or imagery before hierarchy is stable.

---

# 6. Sources

[1] GOV.UK Design System — Navigate a service: https://design-system.service.gov.uk/patterns/navigate-a-service/  
[2] GOV.UK Design System — Summary list: https://design-system.service.gov.uk/components/summary-list/  
[3] GOV.UK Brand Guidelines — Dashboards: https://brand.design-system.service.gov.uk/data/dashboards/  
[4] W3C WCAG 2.2 — Contrast Minimum: https://www.w3.org/TR/WCAG22/#contrast-minimum
