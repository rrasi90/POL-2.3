# مانیفست کانونیکال اسکیما و زنجیره Migration دیتابیس پلتفرم پُل (POL)

**شناسه سند:** `POL-SCHEMA-MANIFEST-2026`  
**نسخه:** ۲.۲ (Reconciled & Forward-Only)  
**پایگاه داده هدف:** PostgreSQL 18.4 (x86_64)  
**وضعیت:** `CANONICAL / RUNTIME-DERIVED`  
**تعداد کل جداول فعال در اسکیما (`public`):** از روی اجرای واقعی زنجیره Migration محاسبه می‌شود؛ عدد ثابت کانونیکال نیست. آخرین artifact محلی ثبت‌شده: ۱۰۷ جدول.  

---

## ۱. زنجیره کانونیکال مهاجرت پایگاه داده (Canonical Migration Chain)

زنجیره مایگریشن پایگاه داده پلتفرم پُل یک زنجیره forward-only و ترتیبی است و در main فعلی تا migration `077_delivery_otp_six_digit_format.sql` امتداد یافته است:

```text
migrations/001_initial_schema.sql
       ↓ (۳۷ جدول هسته بازرگانی، سفارش، کاتالوگ، انبار، لجستیک و تسویه)
migrations/002_platform_core_schema.sql
       ↓ (۱۹ جدول هسته پلتفرم: سازمان‌ها، عضویت‌ها، نشست‌ها، اعلانات، تیکت‌ها، رزرو موجودی و فاکتور)
migrations/003_contract_reconciliation.sql
       ↓ (تطبیق نقش‌ها و قیود پایه)
migrations/004 … migrations/031
       ↓ (تطبیق‌ها و سخت‌سازی‌های forward-only پیشین)
migrations/032 … migrations/046
       ↓ (integrity، fulfillment، checkout، inventory، notification، candidate/barcode hardening)
migrations/047_delegated_permissions_and_audit.sql
       ↓ (delegated permission grants/revokes + append-only permission audit)
migrations/048 … migrations/076
       ↓ (media, privacy, reservations, financial/dispute hardening, delivery/POD, idempotency and event-template reconciliation)
migrations/077_delivery_otp_six_digit_format.sql
       ↓ (new delivery OTPs are six digits; legacy in-flight codes retain their issued length)

**Authority note:** این مانیفست باید از زنجیره واقعی migrationها عقب نماند؛ تغییرات بعدی باید فقط با migration شماره‌دار جدید ثبت شوند. فهرست جدول‌های legacy این سند ممکن است نیازمند refresh مستقل داشته باشد و نباید آن را به‌عنوان شمارش فعلی جدول‌ها تلقی کرد.
```

> **اصل تغییرناپذیری مایگریشن‌ها:**  
> فایل‌های migration تاریخی پس از اعمال نباید rewrite شوند. کلیه تطبیق‌ها، رفع تناقض‌ها و سخت‌سازی‌های بعدی باید صرفاً از طریق migrationهای forward-only شماره‌دار بعدی (تا `077` در `main` فعلی) اعمال شوند.

---

## ۲. سیاهه‌برداری پایه تاریخی ۵۶ جدول (Legacy Baseline Inventory)

این جدول فقط baseline تاریخی 001+002 را نشان می‌دهد. Migrationهای بعدی جداول و ساختارهای بیشتری اضافه کرده‌اند؛ بنابراین این فهرست به‌تنهایی inventory فعلی schema نیست.

| ردیف | نام جدول | حوزه دامنه‌ای | کلید اصلی (PK) | کلیدهای خارجی و ارجاعات کلیدی |
| :---: | :--- | :--- | :--- | :--- |
| ۱ | `users` | هویت و کاربران | UUID | مستقل |
| ۲ | `retailers` | خرده‌فروشان | UUID | `organization_id`, `user_id` (legacy) |
| ۳ | `vendors` | بنکداران | UUID | `organization_id`, `user_id` (legacy) |
| ۴ | `brands` | برندهای کاتالوگ | UUID | مستقل |
| ۵ | `categories` | دسته‌بندی کالاها | UUID | مستقل |
| ۶ | `subcategories` | زیردسته‌بندی‌ها | UUID | `category_id` -> categories(id) |
| ۷ | `products` | کاتالوگ کالای مرجع | UUID | `brand_id`, `subcategory_id` |
| ۸ | `product_identifiers` | بارکدها و شناسه‌ها | UUID | `product_id`, `vendor_id` |
| ۹ | `product_reference_metadata` | متادیتای مرجع کالا | UUID | `product_id` -> products(id) |
| ۱۰ | `media_assets` | فایل‌ها و تصاویر | UUID | مستقل |
| ۱۱ | `product_media` | نگاشت کالا به عکس | UUID | `product_id`, `media_id` |
| ۱۲ | `vendor_products` | عرضه کالای بنکدار | UUID | `vendor_id`, `product_id` |
| ۱۳ | `product_candidates` | کاندیدای کالای جدید | UUID | `vendor_id`, `matched_product_id` |
| ۱۴ | `vendor_inventory` | انبار و موجودی کالا | UUID | `vendor_product_id` (Generated available_qty) |
| ۱۵ | `vendor_prices` | تاریخچه و نرخ جاری | UUID | `vendor_product_id` (uq_current_price index) |
| ۱۶ | `inventory_audit_log` | لاگ حسابرسی انبار | UUID | `vendor_product_id`, `actor_user_id` |
| ۱۷ | `baskets` | سبد خرید خرده‌فروش | UUID | `retailer_id` -> retailers(id) |
| ۱۸ | `basket_items` | اقلام سبد خرید | UUID | `basket_id`, `product_id` |
| ۱۹ | `allocation_plans` | طرح تخصیص بهینه | UUID | `basket_id` -> baskets(id) |
| ۲۰ | `allocation_items` | اقلام تخصیص‌یافته | UUID | `allocation_plan_id`, `vendor_id` |
| ۲۱ | `order_groups` | سرگروه سفارش تجمیعی | UUID | `basket_id`, `retailer_id`, `allocation_plan_id` |
| ۲۲ | `orders` | سفارش مستقل بنکدار | UUID | `order_group_id`, `retailer_id`, `vendor_id` |
| ۲۳ | `order_items` | اقلام سفارش بنکدار | UUID | `order_id`, `vendor_product_id` |
| ۲۴ | `deliveries` | رهگیری لجستیک بار | UUID | `order_id`, `vendor_id` |
| ۲۵ | `delivery_attempts` | تلاش‌های تحویل بار | UUID | `delivery_id` -> deliveries(id) |
| ۲۶ | `proof_of_delivery` | سند تحویل بار (OTP) | UUID | `delivery_id` -> deliveries(id) |
| ۲۷ | `disputes` | مغایرت‌های تجاری | UUID | `order_id`, `retailer_id`, `vendor_id` |
| ۲۸ | `payments` | سوابق پرداخت مستقیم | UUID | `order_id`, `retailer_id`, `vendor_id` |
| ۲۹ | `payment_attempts` | تلاش‌های پرداخت | UUID | `payment_id` -> payments(id) |
| ۳۰ | `settlements` | تسویه مالی بنکدار | UUID | `order_id`, `vendor_id` |
| ۳۱ | `settlement_adjustments` | تعدیلات تسویه اختلاف | UUID | `settlement_id`, `dispute_id` |
| ۳۲ | `refunds` | بازپرداخت به خرده‌فروش | UUID | `order_id`, `dispute_id` |
| ۳۳ | `reputations` | امتیاز اعتبار بنکدار | UUID | `vendor_id` -> vendors(id) |
| ۳۴ | `reputation_snapshots` | تاریخچه ماهانه امتیاز | UUID | `reputation_id` -> reputations(id) |
| ۳۵ | `outbox_events` | رویدادهای تراکنشی | UUID | مستقل (Transactional Outbox) |
| ۳۶ | `domain_events_log` | لاگ تاریخی رخدادها | UUID | مستقل |
| ۳۷ | `categories` (Hierarchies) | ریشه‌های سلسله‌مراتب | - | ساختار پیش‌فرض کاتالوگ FMCG |
| ۳۸ | `organizations` | مرز سازمان و چندمستأجری | UUID | انواع: `RETAILER`, `VENDOR`, `OPERATOR` |
| ۳۹ | `organization_memberships` | عضویت و نقش کاربران | UUID | مرجع احراز صلاحیت؛ نگاشت به سازمان |
| ۴۰ | `user_devices` | دستگاه‌ها و توکن پوش | UUID | ضدتقلب و ارسال اعلانات همراه |
| ۴۱ | `user_sessions` | نشست‌ها و توکن دسترسی | UUID | حامل کانتکست سازمان فعال (`active_org`) |
| ۴۲ | `otp_challenges` | احراز هویت پیامکی | UUID | سقف ۵ تلاش و قفل به وضعیت `BLOCKED` |
| ۴۳ | `notifications` | اعلانات هسته سیستم | UUID | نگاشت به رویداد، کانال و کاربر |
| ۴۴ | `notification_deliveries` | تلاش‌های ارسال پیام | UUID | وضعیت تحویل به تفکیک دستگاه و ارائه‌دهنده |
| ۴۵ | `user_inbox_items` | صندوق پیام بادوام کاربر | UUID | وضعیت خوانده‌شده و بایگانی |
| ۴۶ | `notification_preferences` | ترجیحات اطلاع‌رسانی | UUID | تنظیمات کاربر به تفکیک رویداد و کانال |
| ۴۷ | `broadcast_messages` | پیام‌های همگانی مدیریت | UUID | پیش‌نویس، تایید ادمین و زمان‌بندی |
| ۴۸ | `broadcast_recipients` | گیرندگان پیام همگانی | UUID | اسنپ‌شات تغییرناپذیر مخاطبان |
| ۴۹ | `support_cases` | تیکت‌های پشتیبانی | UUID | مستقل از دعاوی تجاری (`disputes`) |
| ۵۰ | `support_case_messages` | پیام‌های تیکت پشتیبانی | UUID | مکالمات کاربر با تیم عملیات |
| ۵۱ | `support_case_assignments` | تخصیص تیکت به کارشناس | UUID | رهگیری کارشناس فعال با ایندکس یکتا |
| ۵۲ | `field_tasks` | ماموریت‌های میدانی پُل | UUID | وظایف فعال‌ساز میدانی (`FIELD_ACTIVATOR`) |
| ۵۳ | `inventory_reservations` | رزرو زمانی موجودی | UUID | قفل موقت کالا پیش از تایید بنکدار |
| ۵۴ | `invoices` | سوابق فاکتور رسمی | UUID | سند رسمی تجاری مبادله میان دو سازمان |
| ۵۵ | `invoice_items` | اقلام فاکتور رسمی | UUID | ریز اقلام و مبالغ سطری فاکتور |
| ۵۶ | `admin_audit_logs` | لاگ ممیزی عملیات حساس | UUID | ثبت کنشگر، هویت هدف، وضعیت قبل/بعد |

---

### Remediation additions — migration 048

| تغییر | حوزه | نکته حاکمیتی |
|---|---|---|
| `media_assets.upload_target_type` + `upload_target_id` | Media / Object Binding | target presign در DB به asset متصل می‌شود؛ confirm-upload target mismatch را reject می‌کند |
| `idx_media_assets_upload_target` | Media / Integrity | lookup/index برای target binding جدید؛ nullable برای سازگاری با رکوردهای تاریخی |

### Remediation additions — migration 047

این دو جدول در migration `047_delegated_permissions_and_audit.sql` برای اجرای D-026 / VD-15 اضافه شده‌اند. آن‌ها به inventory تاریخی ۵۶ جدول legacy در بالا الحاق می‌شوند؛ این بخش عمداً شمارش کل فعلی schema را ادعا یا بازتعریف نمی‌کند.

| جدول | حوزه | نکته حاکمیتی |
|---|---|---|
| `delegated_permission_grants` | IAM / Delegated Access | وضعیت فعلی grant برای هر Membership + Permission؛ unique per membership/permission؛ tenant-scoped |
| `permission_audit_events` | IAM / Audit | تاریخچه grant/revoke؛ append-only در DB با trigger؛ actor/reason/client/correlation-independent event fields |

## ۳. قرارداد کانونیکال هویت، چندمستأجری و دسترسی (Canonical IAM Contract)

### منبع یگانه حقیقت صلاحیت (SSoT)
- ساختار مجاز: `User -> Membership -> Organization -> Role`.
- جدول `organization_memberships` تنها مرجع تعیین نقش و دسترسی در زمان اجرا (Runtime Authorization) است.
- نشست کاربر در `user_sessions.active_organization_id` مشخص‌کننده کانتکست عملیاتی کاربر در لحظه است.
- ستون `users.role` در دوران مهاجرت صرفاً جهت سازگاری به گذشته نگهداری شده و **فاقد هرگونه مرجعیت اجرایی و امنیتی است**.

### نقش‌های معتبر کانونیکال:
```text
RETAILER_OWNER
RETAILER_STAFF
VENDOR_OWNER
VENDOR_STAFF
OPS_AGENT
ADMIN_SUPER
FIELD_ACTIVATOR
```
*(نقش‌های `SUPER_ADMIN` و `OPS_ADMIN` صرفاً به‌عنوان نام‌های مستعار میراثی در لایه دیتابیس پذیرفته شده و بلافاصله به معادل‌های کانونیکال خود مپ می‌شوند).*

---

## ۴. قواعد و قیود تحمیل‌شده در سطح دیتابیس (Database-Enforced Invariants)

مایگریشن `003_contract_reconciliation.sql` قواعد پایه IAM و tenant را تضمین می‌کند؛ migrationهای بعدی نیز قیود تخصصی دامنه را به‌صورت افزایشی enforce می‌کنند.

1. **انطباق نقش و نوع سازمان (Trigger `trg_enforce_org_membership_role_invariant`):**
   - نقش‌های `RETAILER_OWNER` و `RETAILER_STAFF` منحصراً در سازمان‌های `RETAILER` مجاز هستند.
   - نقش‌های `VENDOR_OWNER` و `VENDOR_STAFF` منحصراً در سازمان‌های `VENDOR` مجاز هستند.
   - نقش‌های `OPS_AGENT`, `ADMIN_SUPER` و `FIELD_ACTIVATOR` منحصراً در سازمان `OPERATOR` مجاز هستند.
   - هرگونه تلاش برای ایجاد یا ویرایش عضویت مغایر با این قاعده با خطای سطح دیتابیس (`RAISE EXCEPTION`) متوقف و Rollback می‌گردد.
2. **پشتیبانی از سناریوهای چندسازمانی (Multi-Organization Scenarios):**
   - حذف محدودیت‌های تک‌مالکیتی `retailers_user_id_key` و `vendors_user_id_key` در `003`؛ بدین ترتیب یک فرد می‌تواند هم‌زمان مالک چند سوپرمارکت یا چند شعبه پخش باشد.
3. **همگام‌سازی وضعیت‌های طرح تخصیص:**
   - پذیرش وضعیت `SUPERSEDED` در قید `allocation_plans.status` در کنار `PREVIEW`, `OPTIMIZED`, `CONFIRMED`, `EXPIRED`, `REJECTED`.
4. **ایندکس‌گذاری ارجاعات کانونیکال:**
   - ایجاد ایندکس‌های یکپارچه روی `organization_id` در جداول مرتبط با بازیگران تجاری.

---

## ۵. ماتریس وضعیت صحت‌سنجی (Verification Status Taxonomy)

وضعیت ادعاهای مهندسی در کل پلتفرم با استاندارد زیر تفکیک می‌شود:

- `SPECIFIED`: قرارداد در مستندات یا نیازمندی‌ها تعریف شده است.
- `STATIC_VERIFIED`: صحت قرارداد با بازرسی کد، سینتکس یا فایل‌های DDL تأیید شده است.
- `RUNTIME_VERIFIED`: قرارداد با اجرای واقعی اسکریپت بر روی پایگاه‌داده فعال PostgreSQL 18.4 و پاس شدن کامل سوئیت تست اعتبارسنجی شده است.
- `BLOCKED`: تست به علت عدم دسترسی به وابستگی یا محیط اجرا نشده است (هرگز معادل Pass در نظر گرفته نمی‌شود).

> **مرز گواهی Runtime:**  
> گواهی‌های تاریخی ۵۶ جدول متعلق به snapshotهای قدیمی هستند. آخرین artifact محلی ثبت‌شده در repository (2026-09-27) تعداد ۱۰۷ جدول و ۶۵۸/۶۵۸ تست پاس‌شده را روی commit `49c2277a4018f8f1e191f0c249b3d44f7a7ac441` ثبت می‌کند؛ این evidence مربوط به همان محیط/commit است و گواهی اجرای فعلی `main` محسوب نمی‌شود.

---

## ۶. قانون ممانعت از انحراف اسکیما (Rule Against Schema Drift)

هرگونه تغییر در جداول، ستون‌ها، تایپ‌ها، ایندکس‌ها، قیود یا تریگرها باید به‌صورت هم‌زمان در ۳ نقطه ثبت شود:
۱. فایل مایگریشن بعدی (به شیوه افزایشی Forward-only).
۲. این سند کانونیکال (`DATABASE_SCHEMA_MANIFEST.md`).
۳. آزمون‌های خودکار اعتبارسنجی اسکیما (`test_postgres_migrations.py` و `verify_repository_consistency.py`).
هیچ فایلی خارج از این چرخه حق معرفی فیزیک دیتابیس را ندارد.


> **OTP policy migration (merged 2026-11-24):** migration `077_delivery_otp_six_digit_format.sql` is part of `main` through PR #59 (merge commit `f9eca328`). It adds a six-digit default for new delivery OTPs, backfills the actual length of stored codes, and preserves already-issued four-digit codes only for their original in-flight deliveries. PostgreSQL 18 CI successfully applied the full chain 001–077 on tested PR head `dbf0a2284e4f16d0cc1e7568b78e81e11c5352a6` (run `45488346802`).
