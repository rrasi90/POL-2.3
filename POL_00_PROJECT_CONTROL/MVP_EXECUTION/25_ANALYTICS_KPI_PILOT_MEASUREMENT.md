# 25. Analytics / KPI / Pilot Measurement

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 25. Analytics / KPI / Pilot Measurement

Existing pilot docs define KPIs, but actual operational measurement pipeline must be completed.

- [ ] canonical event dictionary
- [ ] event properties
- [ ] actor/persona
- [ ] screen source
- [ ] success/failure semantics
- [ ] first assisted order
- [ ] first independent order
- [ ] reorder
- [ ] checkout success/failure
- [ ] vendor accept/reject
- [ ] partial acceptance
- [ ] timeout
- [ ] delivery
- [ ] dispute
- [ ] RMA
- [ ] support
- [ ] referral
- [ ] abandonment
- [ ] vendor activation
- [ ] retailer activation
- [ ] catalog quality
- [ ] inventory freshness
- [ ] acceptance SLA
- [ ] fill rate
- [ ] repeat rate
- [ ] self-service rate
- [ ] cost-to-serve
- [ ] CAC realized
- [ ] vendor continuation intent
- [ ] weekly pilot dashboard
- [ ] cohort definition
- [ ] timezone definition
- [ ] metric lineage
- [ ] exportable investor evidence pack

---

## Open work
- [ ] canonical event dictionary
- [ ] event properties
- [ ] actor/persona
- [ ] screen source
- [ ] success/failure semantics
- [ ] first assisted order
- [ ] first independent order
- [ ] reorder
- [ ] checkout success/failure
- [ ] vendor accept/reject
- [ ] partial acceptance
- [ ] timeout
- [ ] delivery
- [ ] dispute
- [ ] RMA
- [ ] support
- [ ] referral
- [ ] abandonment
- [ ] vendor activation
- [ ] retailer activation
- [ ] catalog quality
- [ ] inventory freshness
- [ ] acceptance SLA
- [ ] fill rate
- [ ] repeat rate
- [ ] self-service rate
- [ ] cost-to-serve
- [ ] CAC realized
- [ ] vendor continuation intent
- [ ] weekly pilot dashboard
- [ ] cohort definition
- [ ] timezone definition
- [ ] metric lineage
- [ ] exportable investor evidence pack

## Decisions required
1. KPI definitions/cohort/timezone authority.
2. analytics schema.
3. source of KPI calculation.

## Dependencies
- [ ] `19_FRONTEND_MVP_WORKSTREAM`
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
