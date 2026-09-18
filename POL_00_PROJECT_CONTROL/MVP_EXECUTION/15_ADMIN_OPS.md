# 15. Admin / Ops

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 15. Admin / Ops

## Required operational surface
- [ ] exception dashboard
- [ ] SLA breach queue
- [ ] vendor timeout queue
- [ ] order operational timeline
- [ ] inventory exceptions
- [ ] payment reconciliation exceptions
- [ ] disputes/RMA queue
- [ ] support queue
- [ ] notification failures
- [ ] vendor reliability signals
- [ ] audit-log viewer
- [ ] pilot KPI dashboard

## Admin controls
- [ ] category management
- [ ] vendor activation/onboarding
- [ ] retailer support
- [ ] SLA override if supported
- [ ] audit log access
- [ ] broadcast creation
- [ ] broadcast recipient freeze
- [ ] broadcast dispatch
- [ ] permission matrix
- [ ] operator tenant/job-function restrictions

---

## Open work
- [ ] exception dashboard
- [ ] SLA breach queue
- [ ] vendor timeout queue
- [ ] order operational timeline
- [ ] inventory exceptions
- [ ] payment reconciliation exceptions
- [ ] disputes/RMA queue
- [ ] support queue
- [ ] notification failures
- [ ] vendor reliability signals
- [ ] audit-log viewer
- [ ] pilot KPI dashboard
- [ ] category management
- [ ] vendor activation/onboarding
- [ ] retailer support
- [ ] SLA override if supported
- [ ] audit log access
- [ ] broadcast creation
- [ ] broadcast recipient freeze
- [ ] broadcast dispatch
- [ ] permission matrix
- [ ] operator tenant/job-function restrictions

## Decisions required
1. حداقل Ops surface.
2. canonical operator roles.
3. separation of duties.

## Dependencies
- [ ] `22_SECURITY_HARDENING`
- [ ] `23_OBSERVABILITY`

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
