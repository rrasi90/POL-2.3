# 3. PASS 1 — Repository / Governance Review

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 3. PASS 1 — Repository / Governance Review

این پاس بررسی می‌کند آیا برنامه با SSoT و Decision Register سازگار است یا نه.

## 3.1 Governance Sync

- [ ] `DECISION_REGISTER.md` همچنان تنها مرجع تصمیم‌های D-001 تا D-020 باشد.
- [ ] D-019 (Python production runtime) در تمام docs همگام شود.
- [ ] D-020 (FastAPI) در تمام docs همگام شود.
- [ ] هر سندی که هنوز NestJS/Fastify را runtime نهایی معرفی می‌کند اصلاح یا archive شود.
- [ ] هر سندی که Python را فقط test runtime می‌داند اصلاح شود.
- [ ] `GLOBAL_ENGINEERING_AUDIT` قدیمی با architecture فعلی sync یا به‌عنوان historical علامت‌گذاری شود.
- [ ] `CAPABILITY_COVERAGE_MATRIX.md` از وضعیت قدیمی NestJS/19 migration/90-table به وضعیت فعلی repository sync شود.
- [ ] `TEST_VERIFICATION_MANIFEST.md` از baselineهای قدیمی (56 table / migrationهای قدیمی) به baseline فعلی sync شود.
- [ ] اسناد architecture/runtime فعلی یک precedence واضح داشته باشند.
- [ ] contradiction log بعد از sync مجدداً اجرا شود.

## 3.2 Queue / Worker Architecture Contradiction

در architecture فعلی دو گزاره همزمان دیده می‌شوند:

- Python runtime به عنوان runtime authoritative.
- BullMQ بر Redis به عنوان queue engine.

BullMQ یک runtime/library وابسته به Node است و با «single Python runtime / no Node-Python dual runtime» بدون تصمیم تکمیلی سازگار نیست.

- [ ] تصمیم صریح برای worker/queue runtime ثبت شود.
- [ ] یکی از این دو مسیر انتخاب شود:
  - [ ] Python-native worker + Redis
  - [ ] PostgreSQL outbox polling + scheduler بدون queue جداگانه در MVP
  - [ ] یا هر گزینه دیگری با Decision ID صریح.
- [ ] BullMQ به عنوان dependency اجرایی ناخواسته باقی نماند.
- [ ] worker ownership و retry/DLQ semantics بعد از این تصمیم دوباره certify شود.

---

## Open work
- [ ] `DECISION_REGISTER.md` همچنان تنها مرجع تصمیم‌های D-001 تا D-020 باشد.
- [ ] D-019 (Python production runtime) در تمام docs همگام شود.
- [ ] D-020 (FastAPI) در تمام docs همگام شود.
- [ ] هر سندی که هنوز NestJS/Fastify را runtime نهایی معرفی می‌کند اصلاح یا archive شود.
- [ ] هر سندی که Python را فقط test runtime می‌داند اصلاح شود.
- [ ] `GLOBAL_ENGINEERING_AUDIT` قدیمی با architecture فعلی sync یا به‌عنوان historical علامت‌گذاری شود.
- [ ] `CAPABILITY_COVERAGE_MATRIX.md` از وضعیت قدیمی NestJS/19 migration/90-table به وضعیت فعلی repository sync شود.
- [ ] `TEST_VERIFICATION_MANIFEST.md` از baselineهای قدیمی (56 table / migrationهای قدیمی) به baseline فعلی sync شود.
- [ ] اسناد architecture/runtime فعلی یک precedence واضح داشته باشند.
- [ ] contradiction log بعد از sync مجدداً اجرا شود.
- [ ] تصمیم صریح برای worker/queue runtime ثبت شود.
- [ ] یکی از این دو مسیر انتخاب شود:
  - [ ] Python-native worker + Redis
  - [ ] PostgreSQL outbox polling + scheduler بدون queue جداگانه در MVP
  - [ ] یا هر گزینه دیگری با Decision ID صریح.
- [ ] BullMQ به عنوان dependency اجرایی ناخواسته باقی نماند.
- [ ] worker ownership و retry/DLQ semantics بعد از این تصمیم دوباره certify شود.

## Decisions required
1. مرجع نهایی runtime/HTTP و تعارض‌های Python/Node و FastAPI/NestJS حل شود.
2. queue/worker runtime تصمیم‌گیری شود.
3. اسناد stale archive/superseded شوند.

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
