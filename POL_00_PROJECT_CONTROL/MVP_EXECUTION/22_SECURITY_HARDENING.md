# 22. Security / Production Hardening

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 22. Security / Production Hardening

- [ ] HTTPS everywhere
- [ ] JWT secret in secret manager
- [ ] OTP provider secret outside Git
- [ ] rate limit implementation
- [ ] brute-force lockout
- [ ] session revocation
- [ ] refresh-token policy
- [ ] refresh-token rotation if selected
- [ ] CSRF strategy where applicable
- [ ] CORS allowlist
- [ ] secure headers
- [ ] request validation
- [ ] body size limits
- [ ] file-upload restrictions
- [ ] malicious file/content policy
- [ ] tenant-isolation HTTP audit
- [ ] authorization negative matrix
- [ ] sensitive-action audit log
- [ ] PII handling policy
- [ ] secrets scan
- [ ] dependency vulnerability scan
- [ ] dependency pin/lock strategy
- [ ] logging redaction
- [ ] admin separation of duties
- [ ] production access control

---

## Open work
- [ ] HTTPS everywhere
- [ ] JWT secret in secret manager
- [ ] OTP provider secret outside Git
- [ ] rate limit implementation
- [ ] brute-force lockout
- [ ] session revocation
- [ ] refresh-token policy
- [ ] refresh-token rotation if selected
- [ ] CSRF strategy where applicable
- [ ] CORS allowlist
- [ ] secure headers
- [ ] request validation
- [ ] body size limits
- [ ] file-upload restrictions
- [ ] malicious file/content policy
- [ ] tenant-isolation HTTP audit
- [ ] authorization negative matrix
- [ ] sensitive-action audit log
- [ ] PII handling policy
- [ ] secrets scan
- [ ] dependency vulnerability scan
- [ ] dependency pin/lock strategy
- [ ] logging redaction
- [ ] admin separation of duties
- [ ] production access control

## Decisions required
1. refresh-token rotation.
2. secret management.
3. minimum security controls.

## Dependencies
- [ ] `03_GOVERNANCE_REVIEW`
- [ ] `21_INFRASTRUCTURE_DEPLOYMENT`

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
