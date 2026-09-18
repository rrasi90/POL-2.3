# 30. Documentation Cleanup Before MVP Freeze

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 30. Documentation Cleanup Before MVP Freeze

این اسناد باید نسخه جاری implementation را بازتاب دهند:

- [ ] `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`
- [ ] `CURRENT_SOURCE_OF_TRUTH.md`
- [ ] `API_APPLICATION_BOUNDARY.md`
- [ ] `ROUTE_COVERAGE_MATRIX.md`
- [ ] `CAPABILITY_COVERAGE_MATRIX.md`
- [ ] `TEST_VERIFICATION_MANIFEST.md`
- [ ] `TECHNICAL_ENVIRONMENT.md`
- [ ] `GLOBAL_ENGINEERING_AUDIT_2026-09-14.md`
- [ ] `REPOSITORY_COMPLETION_AUDIT_2026-09-16.md`
- [ ] `06_PRODUCT/MVP_Definition.md`
- [ ] `06_PRODUCT/PRD.md`
- [ ] `06_PRODUCT/API_Contracts.md`
- [ ] `06_PRODUCT/Technical_Architecture_Spec.md`
- [ ] `06_PRODUCT/Test_Specification.md`
- [ ] `06_PRODUCT/Order_Lifecycle.md`
- [ ] design index / README
- [ ] pilot KPI documents

قانون:
> یک سند stale نباید بتواند agent یا developer بعدی را به معماری قدیمی هدایت کند.

---

## Open work
- [ ] `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`
- [ ] `CURRENT_SOURCE_OF_TRUTH.md`
- [ ] `API_APPLICATION_BOUNDARY.md`
- [ ] `ROUTE_COVERAGE_MATRIX.md`
- [ ] `CAPABILITY_COVERAGE_MATRIX.md`
- [ ] `TEST_VERIFICATION_MANIFEST.md`
- [ ] `TECHNICAL_ENVIRONMENT.md`
- [ ] `GLOBAL_ENGINEERING_AUDIT_2026-09-14.md`
- [ ] `REPOSITORY_COMPLETION_AUDIT_2026-09-16.md`
- [ ] `06_PRODUCT/MVP_Definition.md`
- [ ] `06_PRODUCT/PRD.md`
- [ ] `06_PRODUCT/API_Contracts.md`
- [ ] `06_PRODUCT/Technical_Architecture_Spec.md`
- [ ] `06_PRODUCT/Test_Specification.md`
- [ ] `06_PRODUCT/Order_Lifecycle.md`
- [ ] design index / README
- [ ] pilot KPI documents

## Decisions required
1. superseded/archive docs.
2. SSoT index.
3. drift prevention.

## Dependencies
- [ ] `03_GOVERNANCE_REVIEW`
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
