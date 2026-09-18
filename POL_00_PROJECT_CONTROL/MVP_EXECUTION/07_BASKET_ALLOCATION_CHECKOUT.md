# 7. Basket → Allocation → Checkout

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 7. Basket → Allocation → Checkout

### Already strong
- [x] basket creation
- [x] item addition
- [x] optimistic versioning
- [x] allocation preview
- [x] deterministic allocator
- [x] allocation persistence
- [x] checkout revalidation
- [x] price/stock/MOQ validation
- [x] reservations
- [x] idempotency/fingerprint
- [x] multi-vendor OrderGroup model

### Remaining
- [ ] production catalog queries feed allocation
- [ ] allocation API returns complete retailer-readable explanation
- [ ] unavailable / stale inventory UX
- [ ] price changed UX
- [ ] MOQ/MOV failure UX
- [ ] allocation expiry UX
- [ ] basket restoration
- [ ] revalidation conflict recovery
- [ ] checkout address/contact confirmation
- [ ] payment-method selection contract
- [ ] final review screen
- [ ] frontend idempotency handling
- [ ] retry-safe checkout UX
- [ ] duplicate submission UI behavior
- [ ] checkout success deep-link to order group

---

## Open work
- [ ] production catalog queries feed allocation
- [ ] allocation API returns complete retailer-readable explanation
- [ ] unavailable / stale inventory UX
- [ ] price changed UX
- [ ] MOQ/MOV failure UX
- [ ] allocation expiry UX
- [ ] basket restoration
- [ ] revalidation conflict recovery
- [ ] checkout address/contact confirmation
- [ ] payment-method selection contract
- [ ] final review screen
- [ ] frontend idempotency handling
- [ ] retry-safe checkout UX
- [ ] duplicate submission UI behavior
- [ ] checkout success deep-link to order group

## Decisions required
1. checkout UI و retry/idempotency contract.
2. UX برای stale plan، price change، stockout و MOQ/MOV.
3. مرز payment selection با checkout.

## Dependencies
- [ ] `05_CATALOG_PRODUCT_DISCOVERY`
- [ ] `06_VENDOR_PRICING_INVENTORY`

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
