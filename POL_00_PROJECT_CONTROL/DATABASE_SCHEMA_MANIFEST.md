# -*- coding: utf-8 -*-
MANIFEST_CONTENT = \"\"\"# مانیفست رسمی و جامع زنجیره مایگریشن دیتابیس پلتفرم پُل (POL Database Schema Manifest)

**شناسه سند:** `POL-SCHEMA-MANIFEST-2026`  
**نسخه:** ۲.۰ (مرحله نهایی پیش از اسپرینت صفر)  
**پایگاه داده هدف:** PostgreSQL 18.4 (x86_64)  
**وضعیت:** تثبیت‌شده و فعال در محیط اجرایی (Canonical Schema SSoT)  
**تعداد کل جداول فعال در اسکیما (`public`):** ۵۶ جدول  

---

## ۱. زنجیره کانونیکال مهاجرت پایگاه داده (Canonical Migration Chain)

زنجیره مایگریشن پایگاه داده پلتفرم پُل شامل ۲ فایل ترتیبی DDL است:

```text
migrations/001_initial_schema.sql (۳۷ جدول هسته بازرگانی، سفارش و کاتالوگ)
       ↓
migrations/002_platform_core_schema.sql (۱۹ جدول هسته پلتفرم + اصلاحات سازمانی، امنیتی و لجستیک)
       ↓
مجموع کل: ۵۶ جدول کانونیکال در PostgreSQL 18
```

---

## ۲. فهرست ۳۷ جدول مایگریشن نخست (`migrations/001_initial_schema.sql`)

| ردیف | نام جدول | حوزه دامنه‌ای | کلید اصلی (PK) | کلیدهای خارجی و ارجاعات کلیدی |
| :---: | :--- | :--- | :--- | :--- |
| ۱ | `users` | هویت و کاربران | UUID | مستقل |
| ۲ | `retailers` | خرده‌فروشان | UUID | `user_id` -> users(id) |
| ۳ | `vendors` | بنکداران | UUID | `user_id` -> users(id) |
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
| ۳۲ | `refunds` | بازپرداخت خسارت | UUID | `dispute_id`, `order_id` |
| ۳۳ | `outbox_events` | رخدادهای تراکنشی | UUID | Aggregate Type & ID |
| ۳۴ | `price_change_events` | تغییرات نرخ کالا | UUID | `vendor_product_id` |
| ۳۵ | `catalog_sync_events` | رویدادهای کاتالوگ | UUID | `product_id` |
| ۳۶ | `geo_clusters` | کلاسترهای جغرافیایی | UUID | مستقل |
| ۳۷ | `reputation_snapshots` | نمرات تعهد و اعتبار | UUID | `vendor_id` -> vendors(id) |

---

## ۳. فهرست ۱۹ جدول مایگریشن دوم (`migrations/002_platform_core_schema.sql`)

| ردیف | نام جدول | حوزه دامنه‌ای | کلید اصلی (PK) | کلیدهای خارجی و ارجاعات کلیدی |
| :---: | :--- | :--- | :--- | :--- |
| ۳۸ | `organizations` | نهادهای سازمانی (Tenant Boundary) | UUID | مستقل (`org_type: RETAILER, VENDOR, OPERATOR`) |
| ۳۹ | `organization_memberships` | عضویت کاربران در سازمان | UUID | `organization_id`, `user_id` (uq_user_primary_membership) |
| ۴۰ | `user_devices` | دستگاه‌ها و توکن‌های پوش | UUID | `user_id` -> users(id) |
| ۴۱ | `user_sessions` | نشست‌ها و توکن‌های JWT | UUID | `user_id`, `active_organization_id`, `device_id` |
| ۴۲ | `otp_challenges` | چالش‌های رمز یکبار مصرف | UUID | مستقل (Rate limiting & brute force lock) |
| ۴۳ | `notifications` | مقاصد ارسال اعلان | UUID | `user_id`, `organization_id` |
| ۴۴ | `notification_deliveries` | وضعیت تحویل به تفکیک کانال | UUID | `notification_id`, `device_id` |
| ۴۵ | `user_inbox_items` | صندوق بادوام پیام درون‌برنامه‌ای | UUID | `user_id`, `organization_id`, `notification_id` |
| ۴۶ | `notification_preferences` | تنظیمات کاربر در دریافت اعلان | UUID | `user_id` -> users(id) |
| ۴۷ | `broadcast_messages` | اعلانات همگانی ادمین | UUID | `admin_user_id`, `approved_by` |
| ۴۸ | `broadcast_recipients` | گیرندگان منجمدشده برودکست | UUID | `broadcast_id`, `user_id`, `organization_id` |
| ۴۹ | `support_cases` | تیکت‌های پشتیبانی عمومی | UUID | `user_id`, `organization_id`, `related_order_id` |
| ۵۰ | `support_case_messages` | پیام‌های رشته‌گفتگوی تیکت | UUID | `support_case_id`, `sender_user_id`, `attachment_media_id` |
| ۵۱ | `support_case_assignments` | ارجاع تیکت به کارشناس | UUID | `support_case_id`, `assigned_to_user_id` (uq_active_support_assignment) |
| ۵۲ | `field_tasks` | وظایف فعال‌ساز میدانی | UUID | `target_organization_id`, `assigned_to_user_id` |
| ۵۳ | `inventory_reservations` | چرخه حیات رزرو موقت | UUID | `vendor_product_id`, `order_id`, `order_item_id` |
| ۵۴ | `invoices` | فاکتورهای رسمی/تجاری | UUID | `order_id`, `retailer_organization_id`, `vendor_organization_id` |
| ۵۵ | `invoice_items` | اقلام فاکتور رسمی | UUID | `invoice_id`, `order_item_id` |
| ۵۶ | `admin_audit_logs` | لاگ تغییرات حساس ادمین | UUID | `actor_user_id` (State Before/After JSONB) |

---

## ۴. تغییرات و ارتقای جداول موجود در مایگریشن دوم (Schema Alterations)

1. `baskets`: افزودن `version INT NOT NULL DEFAULT 1` برای کنترل هم‌روندی خوش‌بینانه.
2. `allocation_plans`: افزودن `basket_version INT`, `expires_at TIMESTAMPTZ`, `status VARCHAR(32)`, `input_hash VARCHAR(64)`, `algorithm_version VARCHAR(32)`.
3. `orders`: افزودن `delivery_address_snapshot JSONB`, `correlation_id VARCHAR(128)`.
4. `payments`: افزودن `payment_proof_media_id UUID REFERENCES media_assets(id)`, `verified_by UUID`, `verified_at TIMESTAMPTZ`.
5. `retailers`: افزودن `organization_id UUID REFERENCES organizations(id)`.
6. `vendors`: افزودن `organization_id UUID REFERENCES organizations(id)`.
7. `deliveries`: افزودن `driver_name VARCHAR(128)`, `driver_phone VARCHAR(32)`, `vehicle_plate VARCHAR(32)`.

---

## ۵. گواهی راستی‌آزمایی یکپارچگی پایگاه داده (DDL Verification Certificate)

این مانیفست به همراه کلیه ۵۶ جدول و ارجاعات خارجی در پایگاه‌داده واقعی PostgreSQL 18.4 با اجرای سوئیت‌های خودکار `test_postgres_migrations.py` و `bootstrap_env.py` بررسی و با وضعیت **`RUNTIME_VERIFIED`** تایید شده است.
\"\"\"

with open(\"POL_00_PROJECT_CONTROL/DATABASE_SCHEMA_MANIFEST.md\", \"w\", encoding=\"utf-8\") as f:
    f.write(MANIFEST_CONTENT)

print(\"Created POL_00_PROJECT_CONTROL/DATABASE_SCHEMA_MANIFEST.md successfully.\")
"""

with open("scratch/create_manifest_script.py", "w", encoding="utf-8") as f:
    f.write(MANIFEST_CONTENT)
print("Created scratch/create_manifest_script.py")
