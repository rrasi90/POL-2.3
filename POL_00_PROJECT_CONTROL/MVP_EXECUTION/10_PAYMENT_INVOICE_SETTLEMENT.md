# 10. Payment / Invoice / Settlement

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 10. Payment / Invoice / Settlement

اصل MVP:
`NON-CUSTODIAL DIRECT`

یعنی POL مالک وجه یا escrow نمی‌شود.

## Payment
- [ ] payment method selection contract
- [ ] direct-transfer evidence API
- [ ] payment evidence upload / metadata
- [ ] payment verification API
- [ ] vendor verification UI
- [ ] payment state timeline
- [ ] mismatch state
- [ ] duplicate evidence handling
- [ ] trusted evidence conflict handling
- [ ] payment reconciliation worker
- [ ] reconciliation exception queue
- [ ] settlement calculation
- [ ] settlement adjustment after dispute
- [ ] direct vendor settlement status
- [ ] retailer-facing payment status

## Invoice
- [ ] invoice list API
- [ ] invoice detail API
- [ ] invoice line access-control
- [ ] invoice generation policy
- [ ] printable/PDF invoice path
- [ ] invoice numbering policy
- [ ] split child-order invoice semantics
- [ ] historical immutability test

## Security / finance
- [ ] never store POL-held customer funds
- [ ] never show wallet/escrow balance
- [ ] no unauthorized financial mutations
- [ ] audit trail for verification/adjustment
- [ ] separation of duties for refund-related actions

---

## Open work
- [ ] payment method selection contract
- [ ] direct-transfer evidence API
- [ ] payment evidence upload / metadata
- [ ] payment verification API
- [ ] vendor verification UI
- [ ] payment state timeline
- [ ] mismatch state
- [ ] duplicate evidence handling
- [ ] trusted evidence conflict handling
- [ ] payment reconciliation worker
- [ ] reconciliation exception queue
- [ ] settlement calculation
- [ ] settlement adjustment after dispute
- [ ] direct vendor settlement status
- [ ] retailer-facing payment status
- [ ] invoice list API
- [ ] invoice detail API
- [ ] invoice line access-control
- [ ] invoice generation policy
- [ ] printable/PDF invoice path
- [ ] invoice numbering policy
- [ ] split child-order invoice semantics
- [ ] historical immutability test
- [ ] never store POL-held customer funds
- [ ] never show wallet/escrow balance
- [ ] no unauthorized financial mutations
- [ ] audit trail for verification/adjustment
- [ ] separation of duties for refund-related actions

## Decisions required
1. روش‌های پرداخت pilot.
2. payment evidence/verification/reconciliation ownership.
3. invoice policy بدون wallet/escrow.

## Dependencies
- [ ] `09_FULFILLMENT_DISPATCH_DELIVERY_POD`
- [ ] `11_DISPUTE_RMA_REFUND`

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
