# مانیفست کانونیکال اسکیما و زنجیره Migration دیتابیس POL

**شناسه سند:** `POL-SCHEMA-MANIFEST-2026`  
**نسخه:** 2.1  
**پایگاه‌داده هدف:** PostgreSQL 18+  
**وضعیت:** `CANONICAL / EVIDENCE-GROUNDED`  

## 1. زنجیره کانونیکال Migration

زنجیره نصب اسکیما اکنون باید به‌ترتیب زیر اجرا شود:

```text
migrations/001_initial_schema.sql
        ↓
migrations/002_platform_core_schema.sql
        ↓
migrations/003_contract_reconciliation.sql
```

Migration شماره 003 لایه سازگارسازی قراردادها و سخت‌سازی IAM است؛ بنابراین 001 و 002 به‌تنهایی «اسکیما نهایی» محسوب نمی‌شوند.

## 2. مرجعیت اسکیما

- `001_initial_schema.sql`: جداول هسته کاتالوگ، فروش، سفارش، fulfillment و مالی.
- `002_platform_core_schema.sql`: tenancy، memberships، sessions، notifications، support، inventory reservations، invoices، audit و hardening.
- `003_contract_reconciliation.sql`: رفع drift در RBAC، role naming، tenant/role invariants و legacy actor constraints.

DDL واقعی داخل زنجیره Migration مرجع فیزیکی دیتابیس است. مستندات دیگر نباید schema متفاوتی را به‌عنوان physical SSoT معرفی کنند.

## 3. Canonical IAM Contract

`organization_memberships` مرجع نقش و مجوز است. نقش‌های فعال عبارت‌اند از:

```text
RETAILER_OWNER
RETAILER_STAFF
VENDOR_OWNER
VENDOR_STAFF
OPS_AGENT
ADMIN_SUPER
FIELD_ACTIVATOR
```

`users.role` در دوره مهاجرت صرفاً برای compatibility نگه داشته می‌شود و **منبع مجوز نیست**. Runtime authorization باید بر مبنای عضویت فعال کاربر در `organization_memberships` و سازمان فعال در `user_sessions.active_organization_id` انجام شود.

`retailers.organization_id` و `vendors.organization_id` مرجع canonical tenant برای actorهای تجاری هستند. `retailers.user_id` و `vendors.user_id` legacy compatibility links هستند و نباید مبنای authorization یا tenant isolation قرار بگیرند.

## 4. Database-enforced invariants

Migration 003 این invariants را در سطح PostgreSQL enforce می‌کند:

1. هر `organization_memberships.role` فقط از مجموعه canonical بالا است.
2. `RETAILER_*` فقط برای `organizations.org_type = RETAILER` مجاز است.
3. `VENDOR_*` فقط برای `organizations.org_type = VENDOR` مجاز است.
4. `OPS_AGENT`، `ADMIN_SUPER` و `FIELD_ACTIVATOR` فقط برای `OPERATOR` مجاز هستند.
5. محدودیت legacy «یک user برای فقط یک retailer/vendor» حذف شده است تا multi-organization membership ممکن باشد.

## 5. Verification Status

این فایل عمداً هیچ ادعای `RUNTIME_VERIFIED` یا `PRODUCTION_READY` را بدون اجرای واقعی تست‌های PostgreSQL مطرح نمی‌کند.

وضعیت ادعاها باید در گزارش‌های تست به تفکیک ثبت شود:

- `SPECIFIED`: قرارداد در مستندات تعریف شده است.
- `STATIC_VERIFIED`: با source/schema/static checks تأیید شده است.
- `RUNTIME_VERIFIED`: با اجرای واقعی PostgreSQL و test suite تأیید شده است.
- `BLOCKED`: تست به‌علت محیط یا dependency اجرا نشده است.

برای صدور گواهی runtime، حداقل migration chain کامل، integration tests مربوط به IAM و concurrency باید واقعاً اجرا شوند.

## 6. Rule Against Schema Drift

هر تغییر جدول، role، status، constraint، index یا FK باید هم‌زمان در این مانیفست و migration chain منعکس شود. هیچ فایل گزارش یا audit نباید صرفاً بر اساس ادعا، وضعیت runtime را `PASS` اعلام کند.
