# مشخصات محیط فنی و پایگاه داده کانونیکال (Technical Environment Specification)
## پروژه پُل (POL) — B2B FMCG Platform

**شناسه سند:** `POL-ENV-SPEC-001`  
**نسخه:** ۱.۱  
**وضعیت:** `CANONICAL`  
**تاریخ بازبینی:** سپتامبر ۲۰۲۶  

## ۱. پایگاه داده کانونیکال

پایگاه داده رسمی پُل در توسعه، تست تراکنشی، استیجینگ و پروداکشن **PostgreSQL 18** است. نسخه دقیق runtime برای هر محیط باید از خود سرور ثبت شود؛ در آخرین CI evidence ثبت‌شده، PostgreSQL **18.6** اجرا شده است.

SQLite فقط برای تست‌های واحد ایزوله و سریع مجاز است و جایگزین گیت‌های PostgreSQL نیست.

## ۲. درایور

درایور کانونیکال فعلی Python: `psycopg2-binary>=2.9.9`. مسیر مهاجرت آتی به Psycopg 3 می‌تواند در اسپرینت‌های بعدی بررسی شود، اما تا آن زمان قرارداد فعلی حفظ می‌شود.

## ۳. زنجیره Migration

ساخت دیتابیس باید از زنجیره مرتب و کامل migrationها انجام شود:

```text
001_initial_schema.sql
        ↓
002_platform_core_schema.sql
        ↓
003_contract_reconciliation.sql
        ↓
004_operational_intelligence.sql
        ↓
N (هر migration جدیدی که با ترتیب عددی به زنجیره افزوده شود)
```

Runner رسمی (`scripts/migration_runner.py`) migrationهای SQL را به‌صورت پویا و ترتیبی کشف و اجرا می‌کند. بنابراین هیچ سندی نباید زنجیره را به 001→003 محدود کند.

## ۴. وضعیت فعلی اسکیما

آخرین verification artifact موجود در repository، اجرای زنجیره تا migration 004 را با **62 جدول پایه** ثبت کرده است. Migration 004 شش جدول جدید اضافه می‌کند:

- `daily_inventory_confirmations`
- `daily_inventory_confirmation_items`
- `feedback_submissions`
- `vendor_reliability_events`
- `product_identity_lifecycle_logs`
- `returns`

همچنین ستون‌های freshness/confidence موجودی و version/effective-date قیمت را توسعه می‌دهد.

بنابراین اعداد **56 جدول** یا **زنجیره پایان‌یافته در migration 003** در اسناد قدیمی، current schema نیستند.

## ۵. محیط‌ها

| محیط | فناوری | نقش |
|---|---|---|
| Canonical Runtime | PostgreSQL 18 | SSoT تراکنش‌های واقعی |
| CI Runtime | PostgreSQL 18 (`postgres:18-alpine`) | اجرای migration و verification مستقل |
| Local Runtime | PostgreSQL 18 | توسعه و تست تراکنشی |
| Fast Unit Tests | SQLite in-memory | فقط تست‌های ایزوله غیرتراکنشی |
| Historical | PostgreSQL 16 | صرفاً اسناد/مقایسه‌های قدیمی و منسوخ |

## ۶. آخرین شواهد CI ثبت‌شده

Workflow run `34818313995` روی commit `f3a65a3060d2f09ca7bf9cbd1b270b13f539ca2f` با PostgreSQL 18.6، تعداد 62 جدول پایه و 47 تست از 47 تست پاس‌شده ثبت شده است. این evidence فقط همان commit آزمایش‌شده را certify می‌کند؛ commitهای بعدی باید دوباره CI شوند.

## ۷. اصل حاکم

هر ادعای «runtime verified»، «MVP implementation ready» یا «production ready» باید دقیقاً به commit، محیط و دامنه تست خود ارجاع دهد. موفقیت migration/domain tests به‌تنهایی معادل production readiness کل Android/PWA/API و سرویس‌های خارجی نیست.
