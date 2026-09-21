# معماری رسانه و مدیریت تصاویر محصولات (Product Media & Object Storage Architecture)
## پروژه پُل (POL) — B2B FMCG Platform
**شناسه سند:** `DATA-SPEC-008`  
**وضعیت:** مصوب و نهایی (Canonical Media Specification)  
**نسخه:** ۱.۰  
**مرجع تصمیم‌گیری:** بخش‌های ۱۹ تا ۲۶ و ۸۰ تا ۸۴ مستر پرامپت  
**تاریخ به‌روزرسانی:** سپتامبر ۲۰۲۶  

---

### ۱. اصل راهبردی معماری رسانه (Media Storage Principles)
1. **پرهیز از ذخیره باینری در پایگاه داده:** هیچ فایل تصویری به صورت باینری (BLOB) در دیتابیس PostgreSQL ذخیره نمی‌شود.
2. **پرهیز از فیلد ساده `image_url` در جدول محصول:** محصولات ممکن است چندین تصویر (بسته‌بندی از جلو، جدول ترکیبات، بارکد پشت کاله، کارتن مادر) با کیفیت‌ها و سطوح تایید مختلف داشته باشند.
3. **ذخیره‌سازی مبتنی بر شیء (S3-Compatible Object Storage):** تمامی فایل‌ها در آبجکت استوریج ابری سازگار با S3 (نظیر MinIO در سرورهای داخلی یا ابر آروان/پارس‌پک) نگهداری می‌شوند.
4. **کلیدهای امن و غیرقابل پیش‌بینی:** نام فایل اصلی کاربر **هرگز** به عنوان کلید ذخیره‌سازی استفاده نمی‌شود.

---

### ۲. الگوی کلیدهای ذخیره‌سازی شیء (Object Key Design)

کلیدهای آبجکت استوریج به صورت کاملاً ساختاریافته و ایزوله تولید می‌شوند:

```text
// تصویر اصلی تاییدشده کاتالوگ:
products/{product_id}/canonical/{uuid}.webp

// تصویر بندانگشتی بهینه‌شده برای لیست و سرچ:
products/{product_id}/thumbnails/{uuid}_150x150.webp

// تصویر ارسالی توسط بنکدار جهت بررسی:
vendors/{vendor_id}/uploads/{date}/{uuid}.webp

// شواهد بار تحویل‌شده و گزارش شکستگی:
disputes/{dispute_id}/evidence/{uuid}.webp
```

---

### ۳. مدل داده‌های رابطه‌ای رسانه (Media Data Schema)

#### جدول دارایی‌های ذخیره‌سازی (`media_assets`):
```sql
CREATE TABLE media_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    storage_provider VARCHAR(30) NOT NULL DEFAULT 'S3_MINIO', -- 'S3_MINIO', 'ARVAN_S3'
    bucket_name VARCHAR(100) NOT NULL,
    object_key VARCHAR(500) NOT NULL UNIQUE,
    mime_type VARCHAR(100) NOT NULL, -- 'image/webp', 'image/jpeg', 'image/png'
    file_size_bytes INTEGER NOT NULL,
    width INTEGER,
    height INTEGER,
    checksum_sha256 VARCHAR(64) NOT NULL,
    uploaded_by_user_id UUID REFERENCES users(id),
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE', -- 'UPLOADING', 'ACTIVE', 'DELETED'
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### جدول نگاشت تصویر به محصول (`product_media`):
```sql
CREATE TABLE product_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    media_asset_id UUID NOT NULL REFERENCES media_assets(id) ON DELETE RESTRICT,
    media_type VARCHAR(30) NOT NULL DEFAULT 'PRIMARY_IMAGE', -- 'PRIMARY_IMAGE', 'PACKAGING', 'BARCODE_PHOTO', 'NUTRITION'
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_primary BOOLEAN NOT NULL DEFAULT false,
    source_provenance VARCHAR(50) NOT NULL, -- 'VENDOR_UPLOADED', 'MANUFACTURER_PROVIDED', 'POL_OWNED', 'USER_UPLOADED'
    approval_status VARCHAR(30) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'APPROVED', 'REJECTED', 'PRIVATE_REFERENCE'
    approved_by_user_id UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_product_media_primary ON product_media(product_id, is_primary) WHERE is_primary = true;
```

---

### ۴. امنیت و اعتبارسنجی تصاویر (Image Security & Validation Pipeline)

فایل‌های آپلودشده ورودی‌های غیرقابل اعتماد (Untrusted Input) محسوب می‌شوند و باید از فیلترهای زیر عبور کنند:
1. **اعتبارسنجی جادویی هدر فایل (Magic Bytes Inspection):** بررسی بایت‌های اولیه فایل جهت اطمینان از نوع واقعی فایل (جلوگیری از تغییر پسوند فایلهای مخرب `exe` یا `php` به `jpg`).
2. **سقف حجم فایل:** حداکثر ۵ مگابایت در آپلود خام؛ فشرده‌سازی در سمت کلاینت موبایل به زیر ۳۰۰ کیلوبایت قبل از ارسال.
3. **حذف متادیتاهای محرمانه و جغرافیایی (EXIF Stripping):** حذف اطلاعات مکانی (GPS)، نوع دوربین و اطلاعات هویتی شخصی از فایل تصویر قبل از ذخیره دائم.
4. **تولید نسخه‌های بهینه‌شده وب‌پوینت (WebP Conversion):** تبدیل خودکار تصاویر به فرمت مدرن WebP با حفظ کیفیت ۸۵٪ جهت کاهش ۷۰ درصدی مصرف پهنای باند.

---

### ۵. بهینه‌سازی برای شبکه ۲G و اینترنت ناپایدار (Low-Bandwidth Optimization)

* **بارگذاری تنبل (Lazy Loading):** در لیست‌های سوپرمارکت، تصاویر تنها هنگام رسیدن به دید کاربر بارگیری می‌شوند.
* **دو کیفیت مجزا:**
  - نسخه سبک لیست (`thumbnail` - ابعاد ۱۵۰x۱۵۰ با حجم کمتر از ۲۰ کیلوبایت).
  - نسخه جزئیات کالا (`detail` - ابعاد ۶۰۰x۶۰۰ با حجم کمتر از ۱۰۰ کیلوبایت).
* **آپلود تاب‌آور (Resumable Upload):** در شرایط قطعی مکرر اینترنت در مناطق حاشیه‌ای اهواز، کلاینت از مکانیزم آپلود چندبخشی (Chunked/Resumable) استفاده می‌کند.


---

## ۶. Manufacturer Source Import & Provenance — Amendment 2026-09-20

برای پشتیبانی از واردسازی ساده تصاویر سازنده بدون وابستگی runtime به وب‌سایت خارجی، product_media باید در صورت استفاده از منبع خارجی، متادیتای provenance کافی داشته باشد.

پیشنهاد مفهومی:

- source_url
- source_type
- source_provenance
- rights_status
- import_method
- imported_at
- verified_at
- verified_by_user_id

### MVP import method

OPERATOR_ASSISTED

یعنی اپراتور مجاز منبع سازنده را ثبت و تصویر مجاز را وارد pipeline می‌کند؛ POL تصویر را در storage داخلی مدیریت می‌کند.

### ممنوع

- hotlink کردن مستقیم تصویر سازنده از داخل کلاینت POL به‌عنوان asset canonical
- crawler عمومی برای جمع‌آوری خودکار تصاویر
- ثبت تصویر بدون provenance
- تبدیل «publicly visible» به «rights cleared»

### هدف آینده

در صورت وجود API/feed رسمی یا مجوز قراردادی، import method می‌تواند به AUTHORIZED_API ارتقا یابد، بدون تغییر در هویت Master Product.
