# مشخصات محیط فنی و پایگاه داده کانونیکال (Technical Environment Specification)
## پروژه پُل (POL) — B2B FMCG Platform

**شناسه سند:** `POL-ENV-SPEC-001`  
**نسخه:** ۱.۱  
**وضعیت:** Canonical Technical Specification  
**آخرین ممیزی:** 2026-09-16  

---

## ۱. تصمیم کانونیکال پایگاه داده

> **PostgreSQL 18 تنها پایگاه داده کانونیکال POL در توسعه، تست ران‌تایم، استیجینگ و پروداکشن است.**

- هدف: ACID OLTP برای هویت، کاتالوگ، موجودی، سفارش، تحویل، تسویه، RMA و transactional outbox.
- SQLite فقط برای unit-testهای کاملاً ایزوله و غیرtransactional-domain مجاز است.

### Extensions actually required by the migration chain

- `uuid-ossp` — migration 001
- `pg_trgm` — migration 001 / catalog-search support
- `btree_gist` — migration 005 / temporal exclusion constraints

مستندات نباید `btree_gin` را به‌عنوان extension الزامی معرفی کنند مگر اینکه یک migration فعال واقعاً به آن وابسته شود.

---

## ۲. محیط‌ها

| محیط | فناوری | محدوده |
|---|---|---|
| Canonical Runtime DB | PostgreSQL 18 | production / staging / runtime verification |
| Local Test DB | PostgreSQL 18 | `pol_test` و تست‌های migration/concurrency/integration |
| Unit Simulation | SQLite in-memory | فقط unit tests کاملاً ایزوله؛ هرگز SSoT دامنه نیست |
| Historical Baseline | PostgreSQL 16 | فقط سوابق تاریخی؛ superseded |

---

## ۳. Driver و Python

- Driver فعلی verification harness: `psycopg2-binary>=2.9.9`.
- Psycopg 3 / async access یک مسیر آینده است و تا زمان تصمیم معماری جدید، SSoT نیست.

---

## ۴. Migration Single Source of Truth

تمام محیط‌های قابل‌اعتماد باید از زنجیره کامل numbered migrations ساخته شوند:

```text
Empty PostgreSQL 18
  → migrations/001_*.sql
  → migrations/002_*.sql
  → ...
  → migrations/028_*.sql
  → 93 canonical public tables + integrity triggers/constraints
```

هیچ تست یا سرویس نباید schema دامنه را با DDL موازی بازتعریف کند.

Migration 020–026 عمدتاً guard/runtime hardening را اضافه می‌کنند؛ migration 027 دو جدول partial-acceptance اضافه می‌کند و migration 028 یک جدول operational-holidays اضافه می‌کند. بنابراین baseline فعلی repository برابر **28 migrations / 93 public base tables** است.

---

## ۵. Verification requirement

قبولی repository فقط با table count تعیین نمی‌شود. حداقل این موارد باید روی PostgreSQL 18 بررسی شوند:

- full migration chain;
- tenant isolation;
- canonical role authorization;
- profile/persona cardinality;
- session-to-membership integrity;
- basket/allocation/order-group relationship;
- inventory reservation invariants;
- temporal pricing/window/capacity constraints;
- RMA/refund state integrity;
- outbox/notification behavior;
- idempotency and replay behavior.
