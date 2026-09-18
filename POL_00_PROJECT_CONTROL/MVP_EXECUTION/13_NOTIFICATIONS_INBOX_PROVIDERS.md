# 13. Notifications / Inbox / External Providers

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 13. Notifications / Inbox / External Providers

## Logical notification layer
- [ ] inbox list endpoint
- [ ] mark-read endpoint
- [ ] mark-all-read endpoint
- [ ] notification preferences endpoint
- [ ] mandatory operational notices immune to optional preference suppression
- [ ] deep-link mapping
- [ ] event/template/route matrix coverage

## Integration worker
- [ ] every critical event mapped
- [ ] recipient membership verified
- [ ] unsupported events quarantined
- [ ] retry/backoff
- [ ] terminal FAILED state
- [ ] dedupe
- [ ] correlation_id propagation

## External delivery
- [ ] SMS provider selection
- [ ] SMS.ir credentials provisioned outside Git
- [ ] SMS template approved
- [ ] test OTP delivery
- [ ] push provider selection
- [ ] push credentials/config
- [ ] delivery receipt behavior
- [ ] provider failure recovery
- [ ] provider timeout behavior
- [ ] DLQ/quarantine visibility
- [ ] provider credential rotation process

## Privacy
- [ ] provider-response retention policy
- [ ] PII minimization
- [ ] no OTP/token/secret in logs
- [ ] notification auditability

---

## Open work
- [ ] inbox list endpoint
- [ ] mark-read endpoint
- [ ] mark-all-read endpoint
- [ ] notification preferences endpoint
- [ ] mandatory operational notices immune to optional preference suppression
- [ ] deep-link mapping
- [ ] event/template/route matrix coverage
- [ ] every critical event mapped
- [ ] recipient membership verified
- [ ] unsupported events quarantined
- [ ] retry/backoff
- [ ] terminal FAILED state
- [ ] dedupe
- [ ] correlation_id propagation
- [ ] SMS provider selection
- [ ] SMS.ir credentials provisioned outside Git
- [ ] SMS template approved
- [ ] test OTP delivery
- [ ] push provider selection
- [ ] push credentials/config
- [ ] delivery receipt behavior
- [ ] provider failure recovery
- [ ] provider timeout behavior
- [ ] DLQ/quarantine visibility
- [ ] provider credential rotation process
- [ ] provider-response retention policy
- [ ] PII minimization
- [ ] no OTP/token/secret in logs
- [ ] notification auditability

## Decisions required
1. SMS و Push provider.
2. retry/backoff/DLQ.
3. mandatory در برابر preference-controlled notifications.

## Dependencies
- [ ] `08_ORDER_LIFECYCLE_VENDOR_RESPONSE`
- [ ] `15_ADMIN_OPS`

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
