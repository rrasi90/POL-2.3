# 11. Dispute / RMA / Refund

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 11. Dispute / RMA / Refund

## Disputes
- [ ] create dispute HTTP route
- [ ] list/read dispute route
- [ ] evidence upload
- [ ] item/quantity scope
- [ ] dispute deadline enforcement
- [ ] vendor response
- [ ] operator review
- [ ] resolve route
- [ ] settlement adjustment creation
- [ ] tenant isolation
- [ ] dispute does not corrupt order physical state
- [ ] vendor A settlement unaffected by vendor B dispute

## RMA
- [ ] return request HTTP route
- [ ] return item normalization
- [ ] aggregate quantity ceiling
- [ ] return state transitions
- [ ] inspection state where required
- [ ] refund linkage
- [ ] refund approval
- [ ] refund completion
- [ ] two-person separation of duties
- [ ] refund idempotency
- [ ] refund UI
- [ ] evidence/timeline UI

## Final test
- [ ] complete `DELIVERED → issue → dispute/RMA → decision → adjustment/refund → CLOSED` over actual HTTP/UI.

---

## Open work
- [ ] create dispute HTTP route
- [ ] list/read dispute route
- [ ] evidence upload
- [ ] item/quantity scope
- [ ] dispute deadline enforcement
- [ ] vendor response
- [ ] operator review
- [ ] resolve route
- [ ] settlement adjustment creation
- [ ] tenant isolation
- [ ] dispute does not corrupt order physical state
- [ ] vendor A settlement unaffected by vendor B dispute
- [ ] return request HTTP route
- [ ] return item normalization
- [ ] aggregate quantity ceiling
- [ ] return state transitions
- [ ] inspection state where required
- [ ] refund linkage
- [ ] refund approval
- [ ] refund completion
- [ ] two-person separation of duties
- [ ] refund idempotency
- [ ] refund UI
- [ ] evidence/timeline UI
- [ ] complete `DELIVERED → issue → dispute/RMA → decision → adjustment/refund → CLOSED` over actual HTTP/UI.

## Decisions required
1. Issue types و dispute/RMA states.
2. refund و separation of duties.
3. SLA/evidence retention.

## Dependencies
- [ ] `10_PAYMENT_INVOICE_SETTLEMENT`
- [ ] `12_SUPPORT`

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
