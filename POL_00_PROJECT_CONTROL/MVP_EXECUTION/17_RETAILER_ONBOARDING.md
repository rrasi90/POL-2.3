# 17. Retailer Onboarding

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 17. Retailer Onboarding

- [ ] phone registration
- [ ] OTP
- [ ] profile completion
- [ ] organization/store creation or membership creation
- [ ] store address
- [ ] buyer/contact information
- [ ] consent
- [ ] tutorial/coachmarks
- [ ] first catalog visit
- [ ] first assisted order
- [ ] first independent order
- [ ] reorder flow
- [ ] referral attribution if applicable
- [ ] field activator task linkage
- [ ] onboarding analytics

---

## Open work
- [ ] phone registration
- [ ] OTP
- [ ] profile completion
- [ ] organization/store creation or membership creation
- [ ] store address
- [ ] buyer/contact information
- [ ] consent
- [ ] tutorial/coachmarks
- [ ] first catalog visit
- [ ] first assisted order
- [ ] first independent order
- [ ] reorder flow
- [ ] referral attribution if applicable
- [ ] field activator task linkage
- [ ] onboarding analytics

## Decisions required
1. Retailer onboarding fields.
2. activation و first-order readiness.
3. fallback به ordering سنتی.

## Dependencies
- [ ] Gateهای قبلی سبز باشند.

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
