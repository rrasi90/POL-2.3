# Phase 3 — POL Vendor UX

## Product goal
Digitize the wholesaler's operating desk without turning POL into the wholesaler's warehouse. Vendor owns inventory, pricing and fulfillment; POL provides the digital operating surface.

## Core jobs
- manage catalog and price;
- maintain inventory truth;
- receive and process orders;
- confirm daily inventory state;
- coordinate fulfillment;
- create/use vendor referrals;
- review customers and order history;
- reconcile financial evidence;
- manage staff/persona context.

## Dashboard
Dashboard is queue-first:
- orders requiring action;
- low/uncertain inventory;
- daily inventory confirmation;
- fulfillment exceptions;
- referral activation;
- unresolved support/returns.

KPI cards are secondary to actionable work.

## Catalog and price
Each sellable vendor product must make pack/unit and current price understandable. Effective-date pricing should be presented with effective status, not as hidden history.

## Inventory
Inventory UI must distinguish:
- physical quantity;
- reserved quantity;
- sellable/available quantity where the canonical model supports it;
- last confirmation;
- stale/unknown state.

Do not let the UI imply live accuracy if the vendor has not confirmed or synchronized stock.

## Orders
Vendor order queue:
- new;
- accepted/rejected;
- preparing;
- ready;
- handed off;
- completed;
- exception.

Actions depend on persona. Warehouse focuses preparation; operations focuses fulfillment; finance focuses reconciliation. Authorization remains membership-role based.

## Daily inventory confirmation
The flow should take seconds:
`Review status → confirm / edit exception → submit → receipt`.

Never bury the daily confirmation inside a generic settings page.

## Referral
Vendor Referral MVP needs a simple referral-code/link creation and attribution view. Do not introduce wallet/reward/credit UI because D-016 explicitly excludes these from MVP.

## Staff / persona
Use one design system with persona-specific landing pages:
- Owner: business + overview;
- Sales: customers/orders/referral;
- Warehouse: inventory/confirmation;
- Operations: order/fulfillment queue;
- Finance: invoices/payment/reconciliation;
- Staff: scoped operational tasks.

Cartona publicly describes inventory visibility, order processing and tailored app solutions for retailers, wholesalers and sales teams; POL should adopt the separation of work surfaces while keeping a shared operational data model. citeturn449708view0


---

## 2026-09-20 Dual-Client Vendor Contract

همه personaهای سازمان بنکداری از Web و Android پشتیبانی می‌شوند.

### Owner
- Web: management, catalog, pricing, finance, staff permissions, reporting
- Android: quick operational review, approvals, inventory oversight and exception actions

### Warehouse / Operations
- Web: queue review and bulk operations
- Android: scan, picking, packing, dispatch and exception capture

### Sales / Other Staff
دسترسی بر اساس membership role و delegated permissions تعیین می‌شود. قابلیت‌هایی که کاربر در Web می‌بیند باید از همان authorization boundary در Android نیز تبعیت کنند.

Vendor Storefront مدیریت و نمایش خود را روی همان canonical Vendor/Product/Inventory model انجام می‌دهد.
