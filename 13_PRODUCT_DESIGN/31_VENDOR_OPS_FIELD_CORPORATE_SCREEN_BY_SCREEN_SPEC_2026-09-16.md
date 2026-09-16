# POL — Vendor / Ops / Field / Corporate Screen Specification

## 1. Vendor

### V-01 Dashboard
Design as a prioritized work queue.
Top band:
- page title
- date/context
- urgent count

Primary work blocks:
1. نیاز به تأیید سفارش
2. تأیید موجودی روزانه
3. موجودی کم/قدیمی
4. استثناهای ارسال
5. مرجوعی/پشتیبانی باز

Secondary KPI strip limited to 3–4 metrics.

Rule: queue before KPI.

### V-02 Orders Queue
Desktop table, 1440×1024.
Columns:
`سفارش | مغازه | مبلغ | سن | وضعیت | استثنا | اقدام`

Toolbar:
- search
- status filter
- date filter
- exception filter

Row action is explicit. Sorting is keyboard accessible.

### V-03 Order Detail
Header:
- order id
- state
- age/SLA
- retailer

Main:
- item lines
- accepted qty
- reject/partial control
- reason selection
- preparation state
- handoff

Side or lower audit section:
- timeline
- evidence

Avoid placing dangerous actions adjacent without confirmation.

### V-04 Catalog
Use searchable data table/list.
Columns on desktop:
`محصول | SKU | بسته | قیمت | وضعیت عرضه | تصویر | آخرین تغییر`

Edit opens contextual form/sheet.

### V-05 Pricing
Show current and future-effective values separately.
Do not merge future price into current price visually.
Use history for audit.

### V-06 Inventory
Top summary:
- last confirmation
- stale warning if needed

Rows:
`محصول | موجودی فیزیکی | رزروشده | قابل فروش | تازگی | اقدام`

Unknown must be distinct from zero.

### V-07 Daily Inventory Confirmation
One task flow:
`مرور → اصلاح/تأیید → ثبت → رسید`

Persistent progress but no unnecessary wizard decoration.

### V-08 Referral
Simple utility surface:
- referral link/code
- copy/share
- attribution count
- redemption state

No wallet or reward balance.

### V-09 Customers
Searchable retailer list.
Click-through summary:
- shop identity
- recent orders
- relationship/referral context

### V-10 Reconciliation / Documents
Use summary list for one-off facts and table for multiple records.

### V-11 Staff / Access
Table/list:
`نام | وظیفه | وضعیت | دسترسی | آخرین فعالیت`

Permission presentation must reflect application authorization; UI must never invent access.

### V-12 Profile
Identity first, configuration second.

## 2. Operations

### O-01 Overview
Work queue first.
Sections:
- critical
- aging
- exceptions
- provider/system health

Avoid wall of charts.

### O-02 Unified Queues
Use consistent queue component across Orders, Support, RMA, Reconciliation and Notifications.
Every row:
`severity/state → reason → age → owner → action`

### O-03 Object Detail
Common shell:
header + summary + timeline/audit + evidence + actions.

### O-04 RMA Workbench
Three-pane desktop where width permits:
1. claim queue
2. claim/object detail
3. evidence/decision

Collapse to stacked layout below desktop threshold.

### O-05 Support Workbench
Conversation remains primary; contextual customer/order data stays visible without forcing navigation away.

### O-06 Reconciliation
Prioritize mismatches and unresolved evidence.
Do not start with charts.

### O-07 Risk / Reliability
Show event severity, reason, evidence and remediation history.

### O-08 Notification Operations
Show delivery attempts and failure reason before retry action.

### O-09 Pilot Analytics
Minimal decision-grade cards plus a small table.
Core metrics:
activation, independent orders, repeat, fill rate, acceptance SLA, exceptions, referral attribution.

### O-10 Admin / Context
Keep infrequent admin controls away from daily work surfaces.

## 3. Field Activator

### F-01 Today
Mobile task list.
Each task:
`what → where → due → next action`

### F-02 Retailer Activation
Progressive form.
Show only fields needed for the next activation decision.
Use receipt/confirmation at completion.

### F-03 Assisted Order
Keep retailer context persistent while searching and building basket.
Use same commerce components as retailer app.

### F-04 Follow-up
Timeline/task pattern:
- current status
- note/evidence
- outcome
- next action

### F-05 Weak Network
Persistent connection status.
For unsent actions:
- local state
- retry
- duplicate prevention
- last sync

Never silently discard entered order information.

## 4. Corporate

### C-01 Home
Structure:
1. clear value proposition
2. problem
3. how POL works
4. asset-light model
5. pilot/evidence
6. CTA

No unsupported market claims.

### C-02 Retailers
Explain operational value with concrete examples.

### C-03 Vendors
Explain inventory, orders and digital operating surface.

### C-04 How POL Works
Use a simple 3–5 step flow:
Discover → Build basket → Allocation → Vendor fulfillment → Settlement/reconciliation.

### C-05 Ahvaz Pilot
Show pilot scope, geography and evidence approach, without implying results that do not yet exist.

### C-06 About
Concise institutional information.

### C-07 Contact
Minimal contact form.

### C-08 Legal / Privacy / Trust
Readable long-form layout using B Lotus where appropriate; maintain accessible line length and contrast.

## 5. Cross-surface consistency

The same state, button, quantity stepper, error, evidence, timeline and identity components must visually match across surfaces.

Role-specific density may differ, but the component language must remain recognizably POL.
