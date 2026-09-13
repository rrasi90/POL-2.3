# معماری شناسه‌ها و بارکد محصولات (Product Identifier & Barcode Architecture)
## پروژه پُل (POL) — B2B FMCG Platform
**شناسه سند:** `DATA-SPEC-006`  
**وضعیت:** مصوب و نهایی (Canonical Identifier Specification)  
**نسخه:** ۱.۰  
**مرجع تصمیم‌گیری:** بخش‌های ۹ تا ۱۲ و ۳۷ مستر پرامپت  
**تاریخ به‌روزرسانی:** سپتامبر ۲۰۲۶  

---

### ۱. معماری چندشناسه‌ای کالا (Multi-Identifier Architecture)
در تجارت مدرن و صنف FMCG ایران:
* یک کالا ممکن است دارای چندین بارکد و شناسه باشد (بارکد تک‌فروشی قوطی، بارکد شیرینگ ۶ عددی، بارکد کارتن مادر ۲۴ عددی، کد ایران‌کد، یا کد انبارداری داخلی بنکدار).
* در نتیجه، طراحی دیتابیس با یک فیلد ساده `product.barcode` یک خطای مهلک است.
* **راهکار پُل:** جداسازی کامل مفهوم شناسه در جدول مستقل `product_identifiers` با رابطه $1 \to N$ به هر کالا.

```
┌─────────────────────────────────────────────────────────────┐
│                    Master Product (POL)                     │
│ ID: prod_9821af                                             │
│ Canonical Name: مایع دستشویی کرمی اوه ۴۵۰ گرم               │
└─────────────────────────────────────────────────────────────┘
                               │
      ┌────────────────────────┼────────────────────────┐
      ▼                        ▼                        ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Unit Barcode     │  │ Case Barcode     │  │ IranCode (GS1)   │
│ Type: EAN13      │  │ Type: GTIN14     │  │ Type: IRANCODE   │
│ Value:           │  │ Value:           │  │ Value:           │
│ "6260123456789"  │  │ "16260123456786" │  │ "024519800124"   │
│ Scope: PIECE     │  │ Scope: CARTON_24 │  │ Scope: PRODUCT   │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

### ۲. قوانین استانداردسازی و نرمال‌سازی بارکد (Barcode Normalization Rules)

هنگام ورود بارکد از دوربین موبایل بنکدار، فایل اکسل یا ورودی دستی، پایپ‌لاین زیر الزامی است:
1. **قالب متنی محض (`VARCHAR` / `TEXT`):** بارکدها **هرگز نباید به صورت عدد (`BIGINT` / `INTEGER`) ذخیره شوند**؛ زیرا صفرهای آغازین (Leading Zeros) مانند کدهای UPC یا بارکدهای داخلی از بین می‌روند.
2. **حذف فواصل و نشانه‌های غیرضروری:** حذف تمام فاصله‌ها، نیم‌فاصله‌ها، تب‌ها و خط‌های تیره (`-`).
3. **تبدیل اعداد فارسی و عربی به لاتین:** تبدیل کاراکترهای `۰۱۲۳۴۵۶۷۸۹` به `0123456789`.
4. **حفظ حروف بزرگ:** در صورت وجود حروف در شناسه‌های خاص (مانند بارکدهای داخلی)، تمامی حروف به حروف بزرگ انگلیسی (Uppercase) تبدیل می‌شوند.

---

### ۳. اعتبارسنجی بارکد در برابر انطباق کالا (Validation vs Matching)

> **اصل کلیدی:**  
> «اعتبار صوری بارکد (Valid Format) $\neq$ انطباق قطعی با کالا (Definite Product Match)»

* **سطح ۱: اعتبارسنجی فرمت و رقم کنترل (Checksum Validation):**
  - بررسی الگوریتم رقم کنترل استاندارد Modulo 10 برای بارکدهای EAN-13، EAN-8 و UPC-A.
  - رد بلافصل کاراکترهای نامعتبر یا کدهایی با طول غیراستاندارد.
* **سطح ۲: تطابق شناسه با کاتالوگ (Identifier Lookup):**
  - حتی اگر بارکد معتبر باشد، ممکن است در کاتالوگ پُل ثبت نشده باشد (وضعیت `NO_MATCH`) یا به بیش از یک تنوع محصول نسبت داده شده باشد (وضعیت `AMBIGUOUS`).

---

### ۴. انواع شناسه‌های پشتیبانی‌شده در سیستم (Supported Identifier Types)

| کد نوع شناسه | عنوان استاندارد | طول / فرمت | نمونه مقدار | کاربرد در زنجیره توزیع پُل |
| :--- | :--- | :---: | :--- | :--- |
| `EAN13` | بارکد استاندارد اروپایی/جهانی کالا | ۱۳ رقم | `6260123456789` | بارکد چاپی روی بسته‌بندی تکی یا بطری کالا. |
| `EAN8` | بارکد فشرده اقلام کوچک | ۸ رقم | `96385074` | اقلام بسته‌بندی کوچک مانند آدامس یا صابون. |
| `UPC_A` | بارکد استاندارد آمریکای شمالی | ۱۲ رقم | `012345678905` | کالاهای وارداتی و برندی معتبر. |
| `GTIN14` | شناسه جهانی کارتن مادر (ITF-14) | ۱۴ رقم | `16260123456786` | بارکد بزرگ روی کارتن مقوایی انبار بنکدار (بسیار مهم در B2B). |
| `IRANCODE` | کد ملی کالا و خدمات ایران | ۱۶ رقم | `0245198001240001` | استعلام‌های دولتی و اسناد بازرگانی رسمی. |
| `INTERNAL_BARCODE` | بارکد اختصاصی انبار بنکدار | متغیر متنی | `WH-AHV-9012` | برچسب‌های محلی انبار بنکدار در شهرک اهواز. |
| `VENDOR_SKU` | کد اختصاصی سیستم حسابداری بنکدار | متغیر متنی | `PRIL-1L-LMN` | کد کالا در نرم‌افزارهای هلو، شایگان یا راه‌کاران بنکدار. |

---

### ۵. جدول داده‌های پایگاه داده: `product_identifiers`

```sql
CREATE TABLE product_identifiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    identifier_type VARCHAR(30) NOT NULL,
    identifier_value VARCHAR(100) NOT NULL,
    packaging_scope VARCHAR(30) DEFAULT 'UNIT', -- 'UNIT', 'PACK', 'CASE', 'PALLET'
    is_primary BOOLEAN DEFAULT false,
    source_type VARCHAR(30) NOT NULL, -- 'GS1_OFFICIAL', 'VENDOR_SCAN', 'IMPORTED_DATA', 'MANUAL_ENTRY'
    confidence NUMERIC(3, 2) DEFAULT 1.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_product_identifier UNIQUE (identifier_type, identifier_value, packaging_scope)
);

CREATE INDEX idx_product_identifiers_lookup ON product_identifiers(identifier_value, identifier_type);
```
