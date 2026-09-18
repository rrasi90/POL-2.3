# 29. Performance / Reliability Baseline

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 29. Performance / Reliability Baseline

اعداد performance باید قبل از pilot تعریف و ثبت شوند؛ برای مواردی که KPI صریح در repository دارد همان KPI مرجع است.

- [ ] API latency baseline
- [ ] catalog search latency baseline
- [ ] checkout latency baseline
- [ ] DB query baseline
- [ ] worker processing baseline
- [ ] notification delivery latency
- [ ] concurrent checkout test
- [ ] concurrent vendor action test
- [ ] provider timeout simulation
- [ ] DB connection exhaustion test
- [ ] retry storm test
- [ ] outbox backlog recovery test
- [ ] worker restart recovery
- [ ] API restart recovery

---

## Open work
- [ ] API latency baseline
- [ ] catalog search latency baseline
- [ ] checkout latency baseline
- [ ] DB query baseline
- [ ] worker processing baseline
- [ ] notification delivery latency
- [ ] concurrent checkout test
- [ ] concurrent vendor action test
- [ ] provider timeout simulation
- [ ] DB connection exhaustion test
- [ ] retry storm test
- [ ] outbox backlog recovery test
- [ ] worker restart recovery
- [ ] API restart recovery

## Decisions required
1. performance SLOs.
2. load/concurrency baseline.
3. failure simulation.

## Dependencies
- [ ] `21_INFRASTRUCTURE_DEPLOYMENT`
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
