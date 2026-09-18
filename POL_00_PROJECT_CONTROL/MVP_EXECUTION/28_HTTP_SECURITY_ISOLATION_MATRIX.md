# 28. HTTP-Level Security / Isolation Matrix

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 28. HTTP-Level Security / Isolation Matrix

فقط domain-level تست کافی نیست.

برای هر endpoint:

- [ ] wrong user
- [ ] wrong organization
- [ ] revoked membership
- [ ] inactive organization
- [ ] wrong role
- [ ] wrong resource owner
- [ ] expired token
- [ ] revoked session
- [ ] invalid idempotency key
- [ ] duplicate idempotency key
- [ ] conflicting payload with same idempotency key
- [ ] invalid state transition
- [ ] stale version
- [ ] stale price
- [ ] stale inventory
- [ ] missing inventory
- [ ] provider failure
- [ ] timeout
- [ ] retry
- [ ] duplicate event

---

## Open work
- [ ] wrong user
- [ ] wrong organization
- [ ] revoked membership
- [ ] inactive organization
- [ ] wrong role
- [ ] wrong resource owner
- [ ] expired token
- [ ] revoked session
- [ ] invalid idempotency key
- [ ] duplicate idempotency key
- [ ] conflicting payload with same idempotency key
- [ ] invalid state transition
- [ ] stale version
- [ ] stale price
- [ ] stale inventory
- [ ] missing inventory
- [ ] provider failure
- [ ] timeout
- [ ] retry
- [ ] duplicate event

## Decisions required
1. negative matrix per endpoint.
2. role/tenant permutations.
3. pass/fail evidence.

## Dependencies
- [ ] `04_DOMAIN_BOUNDARY_HTTP_COVERAGE`
- [ ] `22_SECURITY_HARDENING`

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
