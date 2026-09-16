# POL Screen-Level Wireframe Specification — Shared UX + Ops + Field + Corporate

**Date:** 2026-09-16  
**Status:** CANONICAL VISUAL HANDOFF  
**Scope:** `02 — Shared UX` + `03 — States & Patterns` + `06 — Operations` + `07 — Field Activator` + `08 — Corporate`  

> Visual execution only. No new product/domain/authorization/financial-custody rules are introduced.

## 0. Shared visual contract

### Typography
- `B Lotus`: brand/display hierarchy, major headings, corporate hero messaging, printable/exported documents.
- `Vazirmatn`: controls, form fields, dense operational UI, tables, statuses, numeric/technical values.
- Never use B Lotus below `16px` for dense operational controls.

### Layout
- Mobile reference: `390 × 844`, horizontal padding `20`.
- Desktop reference: `1440 × 1024`, sidebar `248`, content max `1280`.
- Primary action is visually unique per screen.
- Preserve 12–16px gaps between tightly related controls; 24–32px between conceptual sections.

### State communication
No state may depend on color alone. Use at least two of:
`label + icon + color + shape + placement`.

### Navigation
Repeated multi-task surfaces may use persistent navigation; focused end-to-end journeys should reduce navigation and keep the task visible. [1]

---

# 1. 02 — Shared UX

## SH-01 Authentication

### Phone
Frame:
- centered brand mark
- B Lotus title
- short explanation
- phone field
- primary CTA
- support/help link

### OTP
- phone summary
- OTP field
- resend countdown
- edit-number action
- validation area

### Error state
Error block appears directly beneath OTP field; never move the user to a separate generic error page.

### Session states
Dedicated variants:
- expired
- revoked
- rate limited
- no active organization

No unnecessary decorative artwork during recovery states.

## SH-02 Profile & Security

Desktop: summary column + settings content.  
Mobile: stacked grouped sections.

Groups:
1. personal profile
2. active organization/context
3. persona/job context
4. notifications
5. security
6. sessions/devices
7. support

Use SummaryList-like key/value blocks for identity metadata rather than large decorative cards. [2]

## SH-03 Notifications

Header:
- title
- unread count
- filter

List item hierarchy:
`type icon → title → reason → timestamp → read state`

Deep-link CTA must be clear and destination-specific.

## SH-04 Support

Two modes:
- case creation
- case tracking

Case creation uses one focused form. Preserve entered values on recoverable validation errors.

## SH-05 Recovery / Deep Link

States:
- invalid link
- object no longer available
- forbidden
- session expired
- network degraded
- retry

Each state contains:
`What happened → What to do → Primary recovery action`.

---

# 2. 03 — States & Patterns

Create a visual matrix board with columns:
`State | User label | Meaning | Primary action | Secondary | Forbidden | Actor | Source | Notification`

## Product
Use a neutral baseline and progressively stronger treatments for:
- active
- unavailable
- stale
- unknown inventory
- future price
- price changed
- MOQ/MOV constraint

## Basket
Show the difference between:
- user-caused quantity error
- system-caused stale basket
- vendor-unavailability
- revalidation requirement

## Allocation
Always distinguish:
- fully available
- partial
- unfulfilled
- changed after revalidation

## Order
Use one canonical status component across Retailer, Vendor and Ops. Color, icon and text are shared tokens.

## RMA / Dispute
The evidence state must be visually obvious:
`not supplied → submitted → under review → clarification → decided`.

## Payment / settlement
Use explicit non-custodial wording. Never use wallet/escrow terminology in UI.

---

# 3. 06 — Operations / POL Ops

Reference frame: `1440 × 1024`.

## O-01 Overview

Structure:
1. header/context
2. page title
3. critical queue strip
4. SLA/aging summary
5. exception summary
6. provider/system health
7. selected high-level pilot indicators

A dashboard is a monitoring summary, not a replacement for queue work. High-level dashboards are best for frequently updated, high-priority indicators. [3]

## O-02 Unified Queues

Filter bar at top:
- queue type
- severity
- state
- owner
- age/SLA
- date
- search

Table columns:
`Reason | Severity | Age/SLA | Owner | Object | Next action`

Each row has one obvious next action.

Desktop row detail opens as side panel where possible, keeping queue context visible.

## O-03 Object Detail

Header:
- object type
- object ID
- current state
- age/SLA
- owner
- primary action

Body:
- key facts
- timeline
- linked objects
- evidence
- allowed actions

Footer:
- audit summary

## O-04 RMA / Dispute Workbench

Three-column desktop composition:
1. claim queue
2. selected claim summary/evidence
3. decision/action panel

Mobile collapses to:
`queue → claim → evidence → decision`.

Decision panel:
- decision reason
- allowed adjustment
- final action

Never hide required evidence behind a separate navigation route.

## O-05 Support Workbench

Desktop:
- queue 32%
- customer/context 28%
- conversation 40%

Conversation panel:
- case status
- customer context
- thread
- attachments
- response composer
- resolution action

## O-06 Reconciliation

Top filter row. Main table:
`Reference | Amount | Evidence | State | Discrepancy | Action`

Evidence opens in side panel. Reconciliation state uses label + icon + color.

## O-07 Risk / Reliability

Avoid a generic security dashboard.

Show actionable incidents:
- reason code
- severity
- affected scope
- age
- evidence
- owner
- remediation

## O-08 Notification Operations

Use table first:
`Notification | Recipient | Provider | Attempt | State | Next retry | Deep link`

Failed provider state has a clear retry action.

## O-09 Pilot Analytics

Keep only decision-relevant indicators:
- activation
- independent orders
- repeat
- fill rate
- acceptance SLA
- exceptions
- referral attribution

Layout:
- summary metrics top
- one trend chart per key question
- table beneath for drill-down

Avoid chart grids that require visual scanning across many unrelated KPIs. [3]

## O-10 Admin / Context

Sections:
- user
- membership
- persona context
- audit
- approved configuration

Role presentation is a reflection of actual authorization; UI does not grant permission.

---

# 4. 07 — Field Activator

Reference frame: `390 × 844`.

## F-01 Today

Top:
- date/context
- task count

Main list:
`Priority | Retailer | Task | Due | Next action`

Use large tap targets and minimal text.

## F-02 Retailer Activation

Flow:
1. search/find
2. confirm/create basic business context
3. consent
4. organization/membership context
5. profile/persona context
6. first assisted action
7. receipt

Each frame has one primary CTA.

## F-03 Assisted Order

Mobile order flow:
1. retailer context header
2. search/catalog
3. product row
4. quantity
5. basket
6. allocation review
7. submit

The Field user sees the same commercial constraints as the retailer, but the copy can be task-oriented.

## F-04 Follow-up

Task detail:
- retailer
- task reason
- prior action
- note/evidence
- outcome
- next due date/action

## F-05 Weak Network

Persistent but quiet network status indicator.

States:
- connected
- degraded
- action pending
- retrying
- sync conflict

Pending local action must not look like successful server submission.

---

# 5. 08 — Corporate

Reference frame: `1440 × 1200`.

## C-01 Home

Hero structure:
1. logo
2. B Lotus headline
3. one-line value proposition
4. primary CTA
5. supporting proof/operating model

Second section:
- how POL works

Third:
- retailer/vendor value

Fourth:
- pilot proof / evidence where available

No unsupported superlatives.

## C-02 Retailers

Structure:
- problem
- operating flow
- value
- how to start
- FAQ
- CTA

## C-03 Vendors

Structure:
- problem
- digital operating surface
- inventory/order benefits
- operational workflow
- onboarding CTA

## C-04 How POL Works

Use a simple flow diagram:
`Retailer → POL transaction layer → Vendor fulfillment → Direct settlement → Data/visibility`

Do not visually imply that POL owns physical inventory, fleet or retailer funds.

## C-05 Ahvaz Pilot

Use evidence-first layout:
- pilot geography
- participating surface/categories when confirmed
- process
- measurable pilot indicators
- timeline/status

Unknown fields stay explicitly unknown.

## C-06 About

Keep concise:
- mission
- operating model
- team/company information that is verified

## C-07 Contact

Minimal form:
- name
- organization
- contact
- reason
- message
- submit

## C-08 Legal / Privacy / Trust

Use readable long-form text layout.

Here B Lotus may be used for headings and B Lotus/B Lotus Bold for printed/exported versions. Body copy remains in the verified UI/readability font.

---

# 6. Cross-surface component specs

## CS-01 Button

Primary:
- solid brand blue
- high-contrast text
- 44px minimum effective mobile touch target

Secondary:
- outline/neutral

Tertiary:
- text button

Danger:
- semantic danger role, never decorative red.

States:
`default | hover | focus | pressed | disabled | loading`

Focus must be clearly visible and not rely on color alone. [4]

## CS-02 Input

Height:
- mobile target `48`
- desktop `44–48`

Contains:
- label
- field
- supporting text
- error state

Do not replace labels with placeholder-only UI.

## CS-03 Status

Structure:
`icon + short label`

Optional:
`reason + timestamp`

## CS-04 Empty state

Structure:
- state icon/illustration
- heading
- explanation
- primary recovery CTA

## CS-05 Error

Structure:
- concise heading
- what happened
- recovery instruction
- action

Never show only a code such as `ERR_500`.

## CS-06 Timeline

Used for orders, support, disputes and reliability.

Node includes:
- state
- timestamp
- actor/source
- optional evidence

## CS-07 Evidence

Thumbnail/file row:
- filename/type
- timestamp
- uploader/source
- verification/review state
- open/remove where allowed

---

# 7. Accessibility and responsive QA

Every final Penpot screen must demonstrate:

- WCAG AA contrast intent; normal text target `4.5:1` minimum. [4]
- state communicated without color alone
- keyboard focus visible on desktop
- 44px mobile touch targets for primary controls
- long Persian labels without clipping
- LTR treatment for identifiers
- zoom/text expansion stress case
- empty/loading/error state
- narrow mobile state
- desktop wide state

---

# 8. Design research references

[1] GOV.UK Design System — Navigate a service: https://design-system.service.gov.uk/patterns/navigate-a-service/  
[2] GOV.UK Design System — Summary list: https://design-system.service.gov.uk/components/summary-list/  
[3] GOV.UK Brand Guidelines — Dashboards: https://brand.design-system.service.gov.uk/data/dashboards/  
[4] W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
