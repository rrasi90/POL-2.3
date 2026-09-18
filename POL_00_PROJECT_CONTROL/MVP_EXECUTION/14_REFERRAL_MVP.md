# 14. Referral MVP

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 14. Referral MVP

Referral is explicitly MVP.

- [ ] vendor referral creation route
- [ ] referral-link representation
- [ ] retailer redemption route
- [ ] first-touch attribution
- [ ] immutable attribution rule
- [ ] duplicate redemption behavior
- [ ] tenant isolation
- [ ] onboarding UI
- [ ] referral analytics
- [ ] do not implement financial reward wallet
- [ ] no multi-touch incentive logic in MVP

---

## Open work
- [ ] vendor referral creation route
- [ ] referral-link representation
- [ ] retailer redemption route
- [ ] first-touch attribution
- [ ] immutable attribution rule
- [ ] duplicate redemption behavior
- [ ] tenant isolation
- [ ] onboarding UI
- [ ] referral analytics
- [ ] do not implement financial reward wallet
- [ ] no multi-touch incentive logic in MVP

## Decisions required
1. first-touch attribution.
2. duplicate redemption.
3. عدم reward wallet در MVP.

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
