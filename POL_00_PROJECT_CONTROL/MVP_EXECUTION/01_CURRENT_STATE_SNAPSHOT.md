# 1. وضعیت واقعی فعلی — Snapshot

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 1. وضعیت واقعی فعلی — Snapshot

## 1.1 چیزهایی که در هسته سیستم موجود و بسیار جلو رفته‌اند

- [x] معماری اصلی `Retailer → Basket → Allocation → Checkout → Vendor Order → Fulfillment → Delivery → Settlement → Data`
- [x] PostgreSQL 18 به عنوان DB کانونیکال
- [x] زنجیره Migrationهای 001 تا 028
- [x] tenant / organization / membership architecture
- [x] canonical RBAC بر مبنای `organization_memberships.role`
- [x] universal user profile + membership/persona model
- [x] basket versioning
- [x] deterministic allocation
- [x] checkout revalidation
- [x] inventory reservation
- [x] order group / child order model
- [x] vendor accept
- [x] vendor reject
- [x] partial acceptance دوطرفه
- [x] vendor acceptance timeout domain contract
- [x] outbox / integration / provider-delivery architecture
- [x] payment reconciliation foundation
- [x] RMA / refund integrity foundation
- [x] support / feedback foundation
- [x] referral foundation
- [x] daily inventory foundation
- [x] concurrency / tenant-isolation / state-machine tests
- [x] FastAPI transport foundation
- [x] Auth transport foundation
- [x] basket / allocation HTTP routes
- [x] checkout HTTP route
- [x] vendor accept/reject/partial-acceptance HTTP routes

## 1.2 مواردی که هنوز MVP را «کامل» نمی‌کنند

- [ ] Batch 6C-7 را روی یک SHA جدید commit/push و CI-certified کنیم.
- [ ] تمام routeهای کانونیکال باقی‌مانده را از Application Boundary تا HTTP تکمیل کنیم.
- [ ] production Auth/OTP/SMS را واقعی کنیم.
- [ ] refresh-token policy را نهایی کنیم.
- [ ] rate limiting و session/security infrastructure را production-grade کنیم.
- [ ] provider واقعی SMS و Push را certify کنیم.
- [ ] frontend واقعی بسازیم؛ در HEAD فعلی frontend production در repository وجود ندارد.
- [ ] retailer app / vendor web / ops web / field app را به API واقعی متصل کنیم.
- [ ] fulfillment / dispatch / delivery / POD transport را کامل کنیم.
- [ ] payment evidence / payment verification / settlement transport را کامل کنیم.
- [ ] disputes / RMA / support / notifications / inbox / invoice / admin routes را کامل کنیم.
- [ ] deployment و staging environment بسازیم.
- [ ] observability و alerting اضافه کنیم.
- [ ] backup / restore / migration runbook را certify کنیم.
- [ ] catalog و pilot inventory واقعی را seed و validate کنیم.
- [ ] vendor و retailer onboarding عملیاتی را اجرا کنیم.
- [ ] telemetry و KPI dashboard را به داده واقعی متصل کنیم.
- [ ] E2E واقعی از UI تا DB و provider را اجرا و certify کنیم.
- [ ] design / Penpot را به implementation واقعی و QA تصویری متصل کنیم.

---

## Open work
- [ ] Batch 6C-7 را روی یک SHA جدید commit/push و CI-certified کنیم.
- [ ] تمام routeهای کانونیکال باقی‌مانده را از Application Boundary تا HTTP تکمیل کنیم.
- [ ] production Auth/OTP/SMS را واقعی کنیم.
- [ ] refresh-token policy را نهایی کنیم.
- [ ] rate limiting و session/security infrastructure را production-grade کنیم.
- [ ] provider واقعی SMS و Push را certify کنیم.
- [ ] frontend واقعی بسازیم؛ در HEAD فعلی frontend production در repository وجود ندارد.
- [ ] retailer app / vendor web / ops web / field app را به API واقعی متصل کنیم.
- [ ] fulfillment / dispatch / delivery / POD transport را کامل کنیم.
- [ ] payment evidence / payment verification / settlement transport را کامل کنیم.
- [ ] disputes / RMA / support / notifications / inbox / invoice / admin routes را کامل کنیم.
- [ ] deployment و staging environment بسازیم.
- [ ] observability و alerting اضافه کنیم.
- [ ] backup / restore / migration runbook را certify کنیم.
- [ ] catalog و pilot inventory واقعی را seed و validate کنیم.
- [ ] vendor و retailer onboarding عملیاتی را اجرا کنیم.
- [ ] telemetry و KPI dashboard را به داده واقعی متصل کنیم.
- [ ] E2E واقعی از UI تا DB و provider را اجرا و certify کنیم.
- [ ] design / Penpot را به implementation واقعی و QA تصویری متصل کنیم.

## Decisions required
1. موارد snapshot را VERIFIED / PARTIALLY VERIFIED / NOT YET VERIFIED طبقه‌بندی کنیم.
2. هیچ capability جدیدی قبل از applicationization بدون Decision ID وارد نشود.
3. Baseline رسمی migration/table/CI ثبت شود.

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
