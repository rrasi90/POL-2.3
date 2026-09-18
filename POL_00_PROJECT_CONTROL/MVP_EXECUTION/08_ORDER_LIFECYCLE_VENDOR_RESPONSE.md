# 8. Order Lifecycle — Vendor Response

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 8. Order Lifecycle — Vendor Response

### Already implemented
- [x] accept
- [x] reject
- [x] partial acceptance proposal
- [x] partial acceptance approve
- [x] partial acceptance decline
- [x] timeout cancellation
- [x] reservation release
- [x] reliability ledger
- [x] tenant-scoped notifications

### Remaining
- [ ] vendor order list API
- [ ] vendor order detail API
- [ ] retailer order/group list API
- [ ] retailer order detail API
- [ ] order timeline API
- [ ] order state timestamps
- [ ] state-specific action availability
- [ ] notification deep-links
- [ ] timeout visibility
- [ ] pending proposal visibility
- [ ] cancellation reason rendering
- [ ] vendor acceptance SLA timer in UI
- [ ] operational queue for timed-out orders
- [ ] full negative HTTP matrix
- [ ] idempotent vendor actions from HTTP
- [ ] concurrent vendor action test through HTTP transport

---

## Open work
- [ ] vendor order list API
- [ ] vendor order detail API
- [ ] retailer order/group list API
- [ ] retailer order detail API
- [ ] order timeline API
- [ ] order state timestamps
- [ ] state-specific action availability
- [ ] notification deep-links
- [ ] timeout visibility
- [ ] pending proposal visibility
- [ ] cancellation reason rendering
- [ ] vendor acceptance SLA timer in UI
- [ ] operational queue for timed-out orders
- [ ] full negative HTTP matrix
- [ ] idempotent vendor actions from HTTP
- [ ] concurrent vendor action test through HTTP transport

## Decisions required
1. order states قابل‌نمایش.
2. SLA UI در برابر hard timeout.
3. timeline/deep-link contract.

## Dependencies
- [ ] `07_BASKET_ALLOCATION_CHECKOUT`
- [ ] `09_FULFILLMENT_DISPATCH_DELIVERY_POD`

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
