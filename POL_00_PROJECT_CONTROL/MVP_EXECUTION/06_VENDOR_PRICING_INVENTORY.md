# 6. Vendor Pricing / Inventory — یکی از اصلی‌ترین MVP gates

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 6. Vendor Pricing / Inventory — یکی از اصلی‌ترین MVP gates

## Pricing
- [ ] vendor current price API
- [ ] price create/update HTTP
- [ ] effective-date validation
- [ ] overlap rejection
- [ ] historical price visibility
- [ ] price freshness in checkout
- [ ] vendor-side UI
- [ ] audit history

## Inventory
- [ ] physical inventory update API
- [ ] reserved quantity view
- [ ] available quantity view
- [ ] continuous scan flow
- [ ] inventory publish flow
- [ ] stale/unknown state
- [ ] atomic reservation behavior
- [ ] reservation release
- [ ] reservation consume
- [ ] reservation expiry worker
- [ ] daily confirmation UI
- [ ] missed-confirmation state
- [ ] reminder flow
- [ ] responsibility routing
- [ ] vendor-side inventory dashboard
- [ ] inventory reconciliation view

## Pilot Data
- [ ] each pilot vendor uploads agreed SKU set
- [ ] price list loaded
- [ ] inventory loaded
- [ ] freshness timestamps validated
- [ ] sample orders created against real catalog

---

## Open work
- [ ] vendor current price API
- [ ] price create/update HTTP
- [ ] effective-date validation
- [ ] overlap rejection
- [ ] historical price visibility
- [ ] price freshness in checkout
- [ ] vendor-side UI
- [ ] audit history
- [ ] physical inventory update API
- [ ] reserved quantity view
- [ ] available quantity view
- [ ] continuous scan flow
- [ ] inventory publish flow
- [ ] stale/unknown state
- [ ] atomic reservation behavior
- [ ] reservation release
- [ ] reservation consume
- [ ] reservation expiry worker
- [ ] daily confirmation UI
- [ ] missed-confirmation state
- [ ] reminder flow
- [ ] responsibility routing
- [ ] vendor-side inventory dashboard
- [ ] inventory reconciliation view
- [ ] each pilot vendor uploads agreed SKU set
- [ ] price list loaded
- [ ] inventory loaded
- [ ] freshness timestamps validated
- [ ] sample orders created against real catalog

## Decisions required
1. SLA/freshness policy موجودی.
2. روش canonical inventory update.
3. قاعده stale/unknown inventory و price conflict.

## Dependencies
- [ ] `05_CATALOG_PRODUCT_DISCOVERY`
- [ ] `07_BASKET_ALLOCATION_CHECKOUT`

## Acceptance Gate
- [ ] تمام کارهای باز بسته یا با دلیل رسمی NOT APPLICABLE شده‌اند.
- [ ] contradiction باز در این حوزه وجود ندارد.
- [ ] تست/verification مناسب اجرا و evidence ثبت شده است.
- [ ] اگر client-facing است: HTTP + Auth + tenant isolation + failure states تست شده‌اند.
- [ ] commit SHA نهایی قابل اشاره است.

## Execution rules
- business rule جدید بدون Decision ID ممنوع.
- SSoTهای repository از این فایل مقدم‌اند.
- GREEN* domain evidence با production-ready اشتباه نشود.
- failure را با حذف/کاهش تست پنهان نکن.

## Status
NOT STARTED / IN PROGRESS / BLOCKED / VERIFIED / CLOSED
