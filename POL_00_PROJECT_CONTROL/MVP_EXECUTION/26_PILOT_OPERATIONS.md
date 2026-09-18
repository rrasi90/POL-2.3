# 26. Pilot Operations

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 26. Pilot Operations

Repository pilot documents already define the basic operating model. Execution remains outside the codebase.

## Vendor side
- [ ] 5–10 pilot vendors identified
- [ ] 1–2 anchor vendors selected
- [ ] LOI signed
- [ ] catalog supplied
- [ ] price supplied
- [ ] inventory supplied
- [ ] operational contact nominated
- [ ] acceptance SLA agreed
- [ ] dispatch process agreed
- [ ] payment method agreed
- [ ] dispute/RMA process agreed
- [ ] staff trained
- [ ] sandbox/test order completed
- [ ] live-readiness checklist signed

## Retailer side
- [ ] target cohort identified
- [ ] geography constrained
- [ ] retailers contacted
- [ ] validation evidence collected
- [ ] pilot participation confirmed
- [ ] onboarding slots scheduled
- [ ] field activator assigned
- [ ] assisted order completed
- [ ] independent order observed

## Operational fallback
- [ ] traditional ordering remains valid fallback during early pilot
- [ ] support channel exists
- [ ] outage procedure exists
- [ ] provider failure procedure exists
- [ ] inventory mismatch procedure exists
- [ ] order rejection procedure exists
- [ ] delivery issue procedure exists
- [ ] payment mismatch procedure exists

---

## Open work
- [ ] 5–10 pilot vendors identified
- [ ] 1–2 anchor vendors selected
- [ ] LOI signed
- [ ] catalog supplied
- [ ] price supplied
- [ ] inventory supplied
- [ ] operational contact nominated
- [ ] acceptance SLA agreed
- [ ] dispatch process agreed
- [ ] payment method agreed
- [ ] dispute/RMA process agreed
- [ ] staff trained
- [ ] sandbox/test order completed
- [ ] live-readiness checklist signed
- [ ] target cohort identified
- [ ] geography constrained
- [ ] retailers contacted
- [ ] validation evidence collected
- [ ] pilot participation confirmed
- [ ] onboarding slots scheduled
- [ ] field activator assigned
- [ ] assisted order completed
- [ ] independent order observed
- [ ] traditional ordering remains valid fallback during early pilot
- [ ] support channel exists
- [ ] outage procedure exists
- [ ] provider failure procedure exists
- [ ] inventory mismatch procedure exists
- [ ] order rejection procedure exists
- [ ] delivery issue procedure exists
- [ ] payment mismatch procedure exists

## Decisions required
1. pilot cohort.
2. anchor vendors/readiness.
3. fallback operating model.

## Dependencies
- [ ] `16_VENDOR_ONBOARDING`
- [ ] `17_RETAILER_ONBOARDING`
- [ ] `18_FIELD_ACTIVATOR`

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
