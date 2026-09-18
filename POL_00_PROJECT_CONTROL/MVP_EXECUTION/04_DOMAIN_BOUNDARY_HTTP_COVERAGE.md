# 4. PASS 2 — Domain → Boundary → HTTP Coverage Review

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 4. PASS 2 — Domain → Boundary → HTTP Coverage Review

## 4.1 Auth / Identity

### موجود
- [x] request OTP route
- [x] verify OTP route
- [x] refresh route
- [x] organization switch
- [x] session revoke
- [x] ApplicationContext

### باقی‌مانده
- [ ] production OTP provider
- [ ] real secret management
- [ ] JWT secret rotation policy
- [ ] OTP abuse/rate-limit runtime
- [ ] device/session management UI
- [ ] refresh-token rotation decision طبق D-018
- [ ] refresh-token reuse detection در صورت انتخاب rotation
- [ ] session revocation end-to-end
- [ ] cross-device/session negative tests از HTTP واقعی
- [ ] 401/403 semantics در تمام transport routes
- [ ] security audit of auth middleware
- [ ] production logging بدون leakage از OTP/token/PII

### Delivery OTP
درباره OTP تحویل، D-018 policy آن را از login OTP جدا کرده است.

- [ ] تصمیم canonical برای delivery OTP digits / lifetime / retry / lockout
- [ ] implement در صورت استفاده
- [ ] transport + UI + tests
- [ ] در غیر این صورت delivery confirmation را با روش دیگری canonical کنیم.

---

## Open work
- [ ] production OTP provider
- [ ] real secret management
- [ ] JWT secret rotation policy
- [ ] OTP abuse/rate-limit runtime
- [ ] device/session management UI
- [ ] refresh-token rotation decision طبق D-018
- [ ] refresh-token reuse detection در صورت انتخاب rotation
- [ ] session revocation end-to-end
- [ ] cross-device/session negative tests از HTTP واقعی
- [ ] 401/403 semantics در تمام transport routes
- [ ] security audit of auth middleware
- [ ] production logging بدون leakage از OTP/token/PII
- [ ] تصمیم canonical برای delivery OTP digits / lifetime / retry / lockout
- [ ] implement در صورت استفاده
- [ ] transport + UI + tests
- [ ] در غیر این صورت delivery confirmation را با روش دیگری canonical کنیم.

## Decisions required
1. فهرست قطعی routeهای MVP مشخص شود.
2. SSoT، actor، tenant context و error semantics هر route ثبت شود.
3. ارتقای GREEN* به GREEN production criteria شود.

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
