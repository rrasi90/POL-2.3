# POL MVP Execution Program

این پوشه مسیر اجرایی کامل از وضعیت فعلی repository تا MVP-CERTIFIED / PILOT-READY را نگه می‌دارد.

- 00_MASTER_MVP_COMPLETION_CHECKLIST_2026-09-18.md: Master اصلی.
- 50_STAGE_MASTER_EXECUTION_PLAN_2026-09-18.md: کنترلر اصلی اجرای مرحله‌ای؛ هر `ادامه` مرحله بعدی را اجرا می‌کند و همان فایل evidence/history را نگه می‌دارد.
- فایل‌های 00_ تا 36_: execution contract مستقل برای بخش‌های Master.
- هر section شامل scope، open work، decisions، dependencies و acceptance gate است.

## Multi-Worker Coordination

- WORK_COORDINATION_PROTOCOL.md: قوانین مالکیت، گزارش، handoff و closing.
- ACTIVE_WORK_LEDGER.md: چه کسی الان روی چه بخشی کار می‌کند.
- WORK_LOGS/SECTION_XX.md: تاریخچه دقیق اتفاقات هر Section.
- WORK_LOG_TEMPLATE.md: قالب استاندارد.

هیچ Section بدون Work Log و evidence معتبر قابل بسته‌شدن نیست.
## 50-Stage Sequential Execution

تمام کارهای قابل انجام در محیط فعلی در 50 work package شکسته شده‌اند. مراحل به‌ترتیب اجرا می‌شوند؛ موارد خارج از دسترس با blocker دقیق ثبت می‌شوند و تا قبل از external handoff ادعای Done دریافت نمی‌کنند.
