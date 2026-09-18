# 18. Field Activator

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 18. Field Activator

- [ ] task list
- [ ] task assignment
- [ ] retailer activation task
- [ ] assisted order
- [ ] training task
- [ ] follow-up
- [ ] task completion evidence
- [ ] retailer conversion funnel
- [ ] weak-network behavior
- [ ] retry/idempotency
- [ ] field history
- [ ] role-based access
- [ ] mobile UI

---

## Open work
- [ ] task list
- [ ] task assignment
- [ ] retailer activation task
- [ ] assisted order
- [ ] training task
- [ ] follow-up
- [ ] task completion evidence
- [ ] retailer conversion funnel
- [ ] weak-network behavior
- [ ] retry/idempotency
- [ ] field history
- [ ] role-based access
- [ ] mobile UI

## Decisions required
1. active task types.
2. assisted order audit.
3. completion/evidence.

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
