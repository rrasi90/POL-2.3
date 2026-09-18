# 36. Release Rule

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 36. Release Rule

**MVP Status vocabulary:**

- `FOUNDATION-VERIFIED` = domain/schema/tests are green.
- `APPLICATIONIZED` = canonical HTTP runtime covers required MVP capabilities.
- `CLIENT-READY` = real clients are integrated.
- `STAGING-READY` = deployment/security/provider/observability green.
- `PILOT-READY` = real pilot users/vendors/data/operations ready.
- `MVP-CERTIFIED` = all critical acceptance gates + final CI + release evidence green.

**Target final state:**

`MVP-CERTIFIED / PILOT-READY`

و نه صرفاً:

`209/209 tests passed`.

## Open work
- [ ] کار باز صریحی در Master ثبت نشده است؛ certification را verify کن.

## Decisions required
1. milestone vocabulary.
2. release evidence + SHA.
3. شرط نهایی Pilot-Ready.

## Dependencies
- [ ] `33_DEFINITION_OF_DONE`
- [ ] `34_FINAL_CRITICAL_REVIEW`

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
