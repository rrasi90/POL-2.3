# 12. Support

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 12. Support

Application boundary methods already exist, but the product surface is not complete.

- [ ] create case HTTP
- [ ] read case HTTP
- [ ] list cases
- [ ] send message
- [ ] assign
- [ ] transition state
- [ ] active-tenant context enforcement
- [ ] operator scope enforcement
- [ ] case SLA/age
- [ ] reopen
- [ ] attachments/evidence policy
- [ ] end-user support UI
- [ ] operator support inbox
- [ ] notification when reply arrives
- [ ] deep-link to case
- [ ] no cross-tenant support leakage
- [ ] HTTP negative tests

---

## Open work
- [ ] create case HTTP
- [ ] read case HTTP
- [ ] list cases
- [ ] send message
- [ ] assign
- [ ] transition state
- [ ] active-tenant context enforcement
- [ ] operator scope enforcement
- [ ] case SLA/age
- [ ] reopen
- [ ] attachments/evidence policy
- [ ] end-user support UI
- [ ] operator support inbox
- [ ] notification when reply arrives
- [ ] deep-link to case
- [ ] no cross-tenant support leakage
- [ ] HTTP negative tests

## Decisions required
1. Support role model و tenant scope.
2. SLA و escalation.
3. attachment/evidence/reply notification.

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
