# 23. Observability

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 23. Observability

MVP با real users بدون observability ناقص است.

- [ ] structured logs
- [ ] correlation ID propagation
- [ ] request IDs
- [ ] order ID trace
- [ ] outbox event trace
- [ ] worker job trace
- [ ] provider attempt trace
- [ ] API latency metrics
- [ ] API error metrics
- [ ] checkout failure metrics
- [ ] order timeout metrics
- [ ] outbox backlog metric
- [ ] notification FAILED metric
- [ ] worker lag metric
- [ ] payment mismatch metric
- [ ] RMA aging metric
- [ ] support SLA metric
- [ ] DB connection saturation
- [ ] DB slow queries
- [ ] alert thresholds
- [ ] on-call notification
- [ ] incident runbook

---

## Open work
- [ ] structured logs
- [ ] correlation ID propagation
- [ ] request IDs
- [ ] order ID trace
- [ ] outbox event trace
- [ ] worker job trace
- [ ] provider attempt trace
- [ ] API latency metrics
- [ ] API error metrics
- [ ] checkout failure metrics
- [ ] order timeout metrics
- [ ] outbox backlog metric
- [ ] notification FAILED metric
- [ ] worker lag metric
- [ ] payment mismatch metric
- [ ] RMA aging metric
- [ ] support SLA metric
- [ ] DB connection saturation
- [ ] DB slow queries
- [ ] alert thresholds
- [ ] on-call notification
- [ ] incident runbook

## Decisions required
1. metrics/log/trace stack و owner.
2. alert thresholds.
3. retention/incident response.

## Dependencies
- [ ] `21_INFRASTRUCTURE_DEPLOYMENT`
- [ ] `25_ANALYTICS_KPI_PILOT_MEASUREMENT`

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
