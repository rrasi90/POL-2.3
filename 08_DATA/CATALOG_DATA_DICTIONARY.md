# دیکشنری جامع داده‌های کاتالوگ محصول (POL Catalog Data Dictionary)
## مشخصات فنی موجودیت‌ها، فیلدها، انواریانت‌ها و دامنه‌های کاتالوگ مرجع
**شناسه سند:** `DATA-DICT-001`  
**وضعیت:** مصوب و نهایی  
**لایه داده‌ای:** PostgreSQL 18 Relational Schema  
**تاریخ انتشار:** سپتامبر ۲۰۲۶  

---

## ۱. بیانیه مرز مفهومی (Catalog Context Boundary)

کاتالوگ مرجع در پلتفرم پُل (POL Master Product Catalog) صرفاً متولی **هویت کانونیکال محصولات** است و مطلقاً حامل وضعیت‌های عملیاتی، موجودی لحظه‌ای بنکدار، قیمت روز فروش یا اعتبار تجاری نیست.

```text
[Raw Reference Dataset] ──(Provenance ETL)──> [product_reference_metadata]
                                                      │
[Product Candidates] ──(Ops Verification)──> [products (Canonical Identity)]
                                                      ├── [brands, categories, subcategories]
                                                      ├── [product_identifiers (Scopes)]
                                                      └── [product_media (MinIO/S3)]
```

---

## ۲. مشخصات موجودیت‌های کاتالوگ مرجع

### ۲.۱. جدول برندها (`brands`)
اطلاعات برندهای رسمی ثبت‌شده در کاتالوگ کالاها:
* `id` (`UUID`, PK, `DEFAULT gen_random_uuid()`): شناسه منحصربه‌فرد برند.
* `name_fa` (`VARCHAR(100)`, NOT NULL): نام فارسی برند (مثال: «پریل»، «کاله»).
* `name_en` (`VARCHAR(100)`): نام انگلیسی برند (در صورت وجود).
* `slug` (`VARCHAR(100)`, UNIQUE NOT NULL): اسلاگ استاندارد جهت جستجو و URL.
* `is_verified` (`BOOLEAN`, NOT NULL DEFAULT FALSE): آیا اصالت برند توسط تیم کاتالوگ تایید شده است؟
* `created_at` (`TIMESTAMPTZ`, NOT NULL DEFAULT CURRENT_TIMESTAMP).

### ۲.۲. جدول دسته‌بندی‌های اصلی (`categories`)
* `id` (`UUID`, PK, `DEFAULT gen_random_uuid()`): شناسه دسته.
* `name_fa` (`VARCHAR(100)`, NOT NULL): نام فارسی دسته (شامل ۵ دسته اصلی: بهداشت و شوینده، تنقلات و خشکبار، کالاهای اساسی و خواربار، لبنیات، پروتئینی).
* `slug` (`VARCHAR(100)`, UNIQUE NOT NULL): اسلاگ یکتا.
* `display_order` (`INTEGER`, NOT NULL DEFAULT 0): ترتیب نمایش در اپلیکیشن.
* `created_at` (`TIMESTAMPTZ`, NOT NULL DEFAULT CURRENT_TIMESTAMP).

### ۲.۳. جدول زیردسته‌ها (`subcategories`)
* `id` (`UUID`, PK, `DEFAULT gen_random_uuid()`): شناسه زیردسته.
* `category_id` (`UUID`, NOT NULL REFERENCES `categories(id)`): کلید خارجی به دسته اصلی.
* `name_fa` (`VARCHAR(100)`, NOT NULL): نام فارسی زیردسته (۳۵ زیردسته کانونیکال).
* `slug` (`VARCHAR(100)`, UNIQUE NOT NULL).
* `display_order` (`INTEGER`, NOT NULL DEFAULT 0).
* `created_at` (`TIMESTAMPTZ`, NOT NULL DEFAULT CURRENT_TIMESTAMP).

### ۲.۴. جدول محصولات مرجع کانونیکال (`products`)
هویت پایه هر کالا مستقل از فروشنده:
* `id` (`UUID`, PK, `DEFAULT gen_random_uuid()`): شناسه سراسری کالا.
* `master_sku` (`VARCHAR(50)`, UNIQUE NOT NULL): کد کاتالوگ یکتای پُل (`POL-PRD-XXXXXX`).
* `canonical_name_fa` (`VARCHAR(255)`, NOT NULL): عنوان رسمی و استاندارد کالا.
* `brand_id` (`UUID`, REFERENCES `brands(id)`): ارجاع به برند.
* `category_id` (`UUID`, NOT NULL REFERENCES `categories(id)`): ارجاع به دسته.
* `subcategory_id` (`UUID`, REFERENCES `subcategories(id)`): ارجاع به زیردسته.
* `net_weight_grams` (`INTEGER`): وزن خالص محصول به گرم.
* `default_pack_unit` (`VARCHAR(30)`, NOT NULL DEFAULT 'CARTON'): واحد بسته‌بندی پیش‌فرض.
* `default_pack_quantity` (`INTEGER`, NOT NULL DEFAULT 1): تعداد در بسته پیش‌فرض.
* `status` (`VARCHAR(20)`, NOT NULL DEFAULT 'ACTIVE' CHECK `status IN ('ACTIVE', 'INACTIVE', 'ARCHIVED')`).
* `created_at` (`TIMESTAMPTZ`, NOT NULL DEFAULT CURRENT_TIMESTAMP).
* `updated_at` (`TIMESTAMPTZ`, NOT NULL DEFAULT CURRENT_TIMESTAMP).

### ۲.۵. جدول شناسه‌ها و بارکدهای کالا (`product_identifiers`)
پشتیبانی از ساختار چندبارکدی و دامنه‌بندی شناسه‌ها:
* `id` (`UUID`, PK, `DEFAULT gen_random_uuid()`).
* `product_id` (`UUID`, NOT NULL REFERENCES `products(id)` ON DELETE CASCADE).
* `vendor_id` (`UUID`, REFERENCES `vendors(id)` ON DELETE CASCADE): شناسه بنکدار برای شناسه‌های محلی (`VENDOR_INTERNAL`)؛ برای شناسه‌های سراسری `NULL` است.
* `identifier_type` (`VARCHAR(30)`, NOT NULL CHECK `identifier_type IN ('EAN13', 'GS1_128', 'UPC', 'IRC', 'IVC', 'LOCAL_BARCODE', 'INTERNAL_CODE')`).
* `identifier_value` (`VARCHAR(100)`, NOT NULL): مقدار عددی یا متنی بارکد.
* `identifier_scope` (`VARCHAR(30)`, NOT NULL DEFAULT 'GLOBAL' CHECK `identifier_scope IN ('GLOBAL', 'PACKAGING', 'VENDOR_INTERNAL')`).
* `is_primary` (`BOOLEAN`, NOT NULL DEFAULT FALSE).
* **ایندکس‌های یکتایی:**
  - سراسری: `CREATE UNIQUE INDEX uq_global_identifier ON product_identifiers(identifier_type, identifier_value) WHERE identifier_scope = 'GLOBAL';`
  - بنکدار-محور: `CREATE UNIQUE INDEX uq_vendor_identifier ON product_identifiers(vendor_id, identifier_type, identifier_value) WHERE identifier_scope = 'VENDOR_INTERNAL';`

### ۲.۶. جدول متادیتای خام منبع خارجی (`product_reference_metadata`)
تفکیک کامل داده‌های اسکرپ‌شده و ارجاعی از داده‌های عملیاتی:
* `id` (`UUID`, PK, `DEFAULT gen_random_uuid()`).
* `product_id` (`UUID`, UNIQUE NOT NULL REFERENCES `products(id)` ON DELETE CASCADE).
* `external_source` (`VARCHAR(50)`, NOT NULL DEFAULT 'DIGIKALA_IMPORT').
* `external_source_id` (`VARCHAR(100)`, NOT NULL): شناسه در مبدا (`dkpId`).
* `raw_observed_price_rials` (`BIGINT`): آخرین قیمت مشاهده‌شده در منبع خارجی (ریال).
* `raw_stock_count` (`INTEGER`): موجودی ثبت‌شده در منبع خام.
* `raw_in_stock` (`BOOLEAN`): وضعیت موجودی در منبع خارجی.
* `raw_rating` (`DECIMAL(4, 2)`): امتیاز در مبدا خارجی.
* `raw_reviews_count` (`INTEGER`): تعداد نظرات در مبدا خارجی.
* `source_url` (`TEXT`): لینک منبع خارجی.
* `scraped_at` (`TIMESTAMPTZ`): زمان استخراج داده خام.

### ۲.۷. جدول کاندیداهای کالا (`product_candidates`)
پایپ‌لاین ورود کالای ناشناخته توسط بنکدار یا ویزیتور:
* `id` (`UUID`, PK, `DEFAULT gen_random_uuid()`).
* `vendor_id` (`UUID`, NOT NULL REFERENCES `vendors(id)` ON DELETE CASCADE).
* `proposed_title` (`VARCHAR(255)`, NOT NULL): عنوان پیشنهادی بنکدار.
* `proposed_brand` (`VARCHAR(100)`).
* `barcode` (`VARCHAR(100)`).
* `vendor_sku` (`VARCHAR(100)`).
* `photo_asset_id` (`UUID`, REFERENCES `media_assets(id)`).
* `status` (`VARCHAR(30)`, NOT NULL DEFAULT 'PENDING_REVIEW' CHECK `status IN ('PENDING_REVIEW', 'APPROVED_CANONICAL', 'MERGED_EXISTING', 'REJECTED')`).
* `resolved_product_id` (`UUID`, REFERENCES `products(id)`).
* `reviewed_by_user_id` (`UUID`, REFERENCES `users(id)`).
* `review_notes` (`TEXT`).
* `created_at` (`TIMESTAMPTZ`, NOT NULL DEFAULT CURRENT_TIMESTAMP).
* `resolved_at` (`TIMESTAMPTZ`).

---

## ۳. انواریانت‌های حاکم بر کاتالوگ (Catalog Invariants)

1. **استقلال هویتی از بنکدار:** ایجاد یا ویرایش محصول در جدول `products` هیچ وابستگی به بنکدار خاصی ندارد.
2. **یکتایی منبع حقیقت بارکد سراسری:** هیچ دو کالای مستقلی نمی‌توانند بارکد جهانی یکسان داشته باشند (`uq_global_identifier`).
3. **هم‌زیستی بارکدهای داخلی چند بنکدار:** دو بنکدار متفاوت مجازند بارکدهای داخلی یکسان برای کالاهای متفاوت داشته باشند (`uq_vendor_identifier`).
4. **جداسازی کامل عکس کاندیدا از تصویر عمومی:** تصویر ارسالی در `product_candidates` تا زمان تایید کارشناس کاتالوگ، هرگز به صورت خودکار به `product_media` منتقل نمی‌شود.
