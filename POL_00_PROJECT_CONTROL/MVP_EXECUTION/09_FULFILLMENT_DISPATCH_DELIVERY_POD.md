# 9. Fulfillment / Dispatch / Delivery / POD

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 9. Fulfillment / Dispatch / Delivery / POD

این قسمت یکی از بزرگ‌ترین فاصله‌های domain-to-product فعلی است.

## Backend
- [ ] `dispatch` application-boundary command
- [ ] `deliver` application-boundary command
- [ ] delivery creation semantics
- [ ] carrier/vendor responsibility
- [ ] dispatch state transition
- [ ] delivery state transition
- [ ] POD creation
- [ ] POD actor authorization
- [ ] POD evidence retention
- [ ] delivery timestamps
- [ ] failed/exception delivery path
- [ ] doorstep rejection flow
- [ ] delivery dispute linkage
- [ ] no-duplicate dispatch constraint verification
- [ ] no-duplicate delivery confirmation
- [ ] concurrency tests

## Delivery UX
- [ ] Retailer delivery tracking surface
- [ ] Vendor fulfillment queue
- [ ] Vendor dispatch confirmation
- [ ] Ops exception view
- [ ] POD status view
- [ ] evidence viewer
- [ ] delivery failure recovery
- [ ] deep-link from notification

## Scope rule
- [ ] dedicated POL Driver app NOT required unless a new decision explicitly creates it.
- [ ] physical logistics remains vendor / partner responsibility.
- [ ] no unsupported live ETA promise.

---

## Open work
- [ ] `dispatch` application-boundary command
- [ ] `deliver` application-boundary command
- [ ] delivery creation semantics
- [ ] carrier/vendor responsibility
- [ ] dispatch state transition
- [ ] delivery state transition
- [ ] POD creation
- [ ] POD actor authorization
- [ ] POD evidence retention
- [ ] delivery timestamps
- [ ] failed/exception delivery path
- [ ] doorstep rejection flow
- [ ] delivery dispute linkage
- [ ] no-duplicate dispatch constraint verification
- [ ] no-duplicate delivery confirmation
- [ ] concurrency tests
- [ ] Retailer delivery tracking surface
- [ ] Vendor fulfillment queue
- [ ] Vendor dispatch confirmation
- [ ] Ops exception view
- [ ] POD status view
- [ ] evidence viewer
- [ ] delivery failure recovery
- [ ] deep-link from notification
- [ ] dedicated POL Driver app NOT required unless a new decision explicitly creates it.
- [ ] physical logistics remains vendor / partner responsibility.
- [ ] no unsupported live ETA promise.

## Decisions required
1. مالکیت delivery states.
2. POD و شواهد قابل قبول.
3. delivery exception/doorstep rejection در release gate.

## Dependencies
- [ ] `08_ORDER_LIFECYCLE_VENDOR_RESPONSE`

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
