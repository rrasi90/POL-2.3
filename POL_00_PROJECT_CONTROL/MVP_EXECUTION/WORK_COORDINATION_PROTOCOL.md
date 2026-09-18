# POL MVP Execution — Multi-Worker Coordination Protocol

**Status:** CANONICAL / MANDATORY
**Scope:** تمام بخش‌های POL_00_PROJECT_CONTROL/MVP_EXECUTION/

## قانون اصلی
هیچ کاری در مسیر MVP معتبر نیست مگر اینکه در سیستم ثبت کار ثبت شده باشد.

هر worker/agent/developer باید ثبت کند:
- چه کسی و چه نقشی؛
- Section و WORK_ID؛
- وضعیت قبل و بعد؛
- دقیقاً چه تغییراتی؛
- چه فایل‌هایی؛
- چه تصمیمی؛
- چه تستی با چه دستور دقیقی و نتیجه آن؛
- commit/SHA؛
- blocker؛
- قدم بعدی.

نوشتن صرفاً «Done» یا «Tests passed» کافی نیست.

## سه لایه ثبت
1. ACTIVE_WORK_LEDGER.md — چه کسانی همین الان روی چه بخشی کار می‌کنند.
2. WORK_LOGS/SECTION_XX.md — تاریخچه دقیق هر Section.
3. Worker Closing Report — گزارش استاندارد پایان هر Task.

## مالکیت و کار موازی
قبل از شروع task باید Section claim شود و WORK_ID، task، owner، فایل‌های مورد انتظار و blocker احتمالی ثبت شوند.
چند worker روی یک Section مجازند فقط وقتی taskهایشان مستقل و ثبت‌شده باشند؛ مثل implementation / tests / documentation.
دو worker نباید هم‌زمان یک فایل را بدون ثبت ownership تغییر دهند.

## وضعیت‌های مجاز
PLANNED → CLAIMED → IN_PROGRESS → BLOCKED یا READY_FOR_REVIEW → VERIFIED → CLOSED

## فیلدهای اجباری Work Entry
WORK_ID, SECTION_ID, WORKER, ROLE, STARTED_AT, ENDED_AT, STATUS_BEFORE, STATUS_AFTER, TASK, CHANGES, FILES_TOUCHED, DECISIONS, TESTS_RUN, RESULT, COMMIT_SHA, BLOCKERS, NEXT_ACTION

## Evidence rule
نتیجه باید factual باشد. دستور دقیق تست، خروجی، environment و SHA ثبت شود.

## Handoff rule
هر handoff باید آخرین وضعیت، تغییرات، تست‌ها، commit، blockerها و دقیقاً task بعدی را ثبت کند. گزارش شفاهی یا صرفاً داخل Chat کافی نیست.

## Blocker rule
هر blocker باید سبب، اثر، نیازمند تصمیم، راه‌های ممکن، recommendation فعلی، owner رفع و شرط بازبینی بعدی را داشته باشد.

## Decision rule
business rule یا architecture جدید بدون Decision ID اختراع یا پیاده‌سازی نشود.

## File-class rule
هر گزارش باید نوع تغییر را مشخص کند: SOURCE_CHANGED / TEST_CHANGED / DOC_CHANGED / CONFIG_CHANGED / MIGRATION_CHANGED / NO_CHANGE.

## Status synchronization
Status در Section playbook، Section Work Log و Active Work Ledger باید سازگار باشد. اختلاف Status خودش defect است.

## Closing rule
Section فقط وقتی CLOSED است که history ثبت شده، همه work itemها بسته، تصمیم‌ها ثبت، تست/evidence موجود، blocker بحرانی رفع، SHA مشخص و Acceptance Gate پاس شده باشد.

## Minimum closing report
WORK_ID / SECTION_ID / WORKER / ROLE / STATUS_BEFORE / STATUS_AFTER / TASK / CHANGES / FILES_TOUCHED / DECISIONS / TESTS_RUN / RESULT / COMMIT_SHA / BLOCKERS / NEXT_ACTION

## No silent work
هر اثر repository شامل code, SQL, migration, test, documentation, design, config, deployment, data seed و provider configuration باید در Work Log قابل پیدا کردن باشد.