# 27. Real-World Pilot Test Protocol

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 27. Real-World Pilot Test Protocol

قبل از Go-Live باید حداقل این سناریوها end-to-end روی environment واقعی staging/pilot اجرا شوند.

## Retailer
- [ ] signup/login
- [ ] OTP failure
- [ ] OTP rate-limit
- [ ] organization context
- [ ] catalog search
- [ ] compare vendor offers
- [ ] add to basket
- [ ] basket modification
- [ ] stale allocation
- [ ] allocation unavailable item
- [ ] price changed
- [ ] insufficient stock
- [ ] MOQ failure
- [ ] MOV failure
- [ ] checkout
- [ ] duplicate checkout
- [ ] order tracking
- [ ] vendor rejection
- [ ] partial acceptance
- [ ] vendor timeout
- [ ] dispatch
- [ ] delivery
- [ ] POD
- [ ] payment evidence
- [ ] dispute
- [ ] RMA
- [ ] refund
- [ ] support
- [ ] notification
- [ ] reorder

## Vendor
- [ ] login
- [ ] catalog edit
- [ ] price edit
- [ ] inventory update
- [ ] daily confirmation
- [ ] accept
- [ ] reject
- [ ] partial proposal
- [ ] proposal race
- [ ] prepare
- [ ] dispatch
- [ ] payment verification
- [ ] dispute response
- [ ] RMA response
- [ ] referral

## Ops
- [ ] timeout queue
- [ ] notification failure
- [ ] support case
- [ ] dispute
- [ ] refund separation-of-duty
- [ ] payment mismatch
- [ ] audit log
- [ ] broadcast
- [ ] vendor onboarding
- [ ] pilot dashboard

---

## Open work
- [ ] signup/login
- [ ] OTP failure
- [ ] OTP rate-limit
- [ ] organization context
- [ ] catalog search
- [ ] compare vendor offers
- [ ] add to basket
- [ ] basket modification
- [ ] stale allocation
- [ ] allocation unavailable item
- [ ] price changed
- [ ] insufficient stock
- [ ] MOQ failure
- [ ] MOV failure
- [ ] checkout
- [ ] duplicate checkout
- [ ] order tracking
- [ ] vendor rejection
- [ ] partial acceptance
- [ ] vendor timeout
- [ ] dispatch
- [ ] delivery
- [ ] POD
- [ ] payment evidence
- [ ] dispute
- [ ] RMA
- [ ] refund
- [ ] support
- [ ] notification
- [ ] reorder
- [ ] login
- [ ] catalog edit
- [ ] price edit
- [ ] inventory update
- [ ] daily confirmation
- [ ] accept
- [ ] reject
- [ ] partial proposal
- [ ] proposal race
- [ ] prepare
- [ ] dispatch
- [ ] payment verification
- [ ] dispute response
- [ ] RMA response
- [ ] referral
- [ ] timeout queue
- [ ] notification failure
- [ ] support case
- [ ] dispute
- [ ] refund separation-of-duty
- [ ] payment mismatch
- [ ] audit log
- [ ] broadcast
- [ ] vendor onboarding
- [ ] pilot dashboard

## Decisions required
1. release-blocking scenarios.
2. authoritative certification environment.
3. شرط Pilot Go.

## Dependencies
- [ ] `28_HTTP_SECURITY_ISOLATION_MATRIX`
- [ ] `29_PERFORMANCE_RELIABILITY_BASELINE`
- [ ] `26_PILOT_OPERATIONS`

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
