# دیکشنری داده‌های انبار و عرضه بنکدار (POL Inventory Data Dictionary)
## مشخصات فنی کالاهای بنکدار، موجودی جنریک، قیمت‌گذاری و ثبت تغییرات
**شناسه سند:** `DATA-DICT-002`  
**وضعیت:** مصوب و نهایی  
**لایه داده‌ای:** PostgreSQL 18 Relational Schema  
**تاریخ انتشار:** سپتامبر ۲۰۲۶  

---

## ۱. بیانیه مرز مفهومی (Vendor Supply Context Boundary)

این زیردامنه مسئول مدیریت پیشنهادهای تجاری فروشندگان (Sellable Commercial Offers)، موجودی فیزیکی و قابل‌فروش بر پایه واحدهای عمومی (Generic Units)، تاریخچه قیمت‌ها و ردیابی حسابرسی تغییرات است.

```text
[products (Identity)] ──(1:N)──> [vendor_products (Sellable Offer)]
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
     [vendor_prices]           [vendor_inventory]        [inventory_audit_log]
   (Current Price 1:1)      (physical, reserved, avail)    (Immutable Audit Trail)
```

---

## ۲. مشخصات موجودیت‌های انبار و عرضه

### ۲.۱. جدول کالای بنکدار (`vendor_products`)
نمایش تجاری و قابل‌فروش یک کالا توسط یک بنکدار با پیکربندی بسته‌بندی معین:
* `id` (`UUID`, PK, `DEFAULT gen_random_uuid()`).
* `vendor_id` (`UUID`, NOT NULL REFERENCES `vendors(id)` ON DELETE CASCADE).
* `product_id` (`UUID`, REFERENCES `products(id)` ON DELETE RESTRICT): برای کالاهای تاییدشده پر است؛ برای کاندیدای پیش‌نویس موقتاً `NULL` است.
* `candidate_id` (`UUID`, REFERENCES `product_candidates(id)` ON DELETE SET NULL).
* `vendor_sku` (`VARCHAR(100)`, NOT NULL): کد کالای اختصاصی بنکدار در سیستم حسابداری خودش.
* `packaging_unit` (`VARCHAR(30)`, NOT NULL DEFAULT 'CARTON'): واحد بسته‌بندی فروش (کارتن، شیرینگ، گونی، بسته، عدد).
* `pack_quantity` (`INTEGER`, NOT NULL DEFAULT 12 CHECK `pack_quantity > 0`): تعداد اقلام مصرفی در این واحد بسته‌بندی.
* `listing_status` (`VARCHAR(30)`, NOT NULL DEFAULT 'ACTIVE' CHECK `listing_status IN ('DRAFT_PENDING_CATALOG', 'ACTIVE', 'INACTIVE', 'OUT_OF_STOCK', 'SUSPENDED')`).
* `is_available` (`BOOLEAN`, NOT NULL DEFAULT TRUE).
* `created_at` (`TIMESTAMPTZ`, NOT NULL DEFAULT CURRENT_TIMESTAMP).
* `updated_at` (`TIMESTAMPTZ`, NOT NULL DEFAULT CURRENT_TIMESTAMP).
* **قیود یکتایی:**
  - `UNIQUE(vendor_id, vendor_sku)`: هر بنکدار نمی‌تواند کد کالای تکراری داشته باشد.
  - `UNIQUE(vendor_id, product_id, packaging_unit, pack_quantity)`: تضمین می‌کند یک بنکدار می‌تواند یک محصول مستر را در چندین بسته‌بندی متفاوت (مثلاً کارتن ۱۲ تایی و کارتن ۲۴ تایی) عرضه کند.

### ۲.۲. جدول قیمت‌های بنکدار (`vendor_prices`)
تاریخچه قیمت‌گذاری و ثبت قیمت جاری:
* `id` (`UUID`, PK, `DEFAULT gen_random_uuid()`).
* `vendor_product_id` (`UUID`, NOT NULL REFERENCES `vendor_products(id)` ON DELETE CASCADE).
* `price_toman` (`BIGINT`, NOT NULL CHECK `price_toman > 0`): قیمت فروش عمده هر واحد بسته‌بندی به تومان.
* `consumer_price_toman` (`BIGINT` CHECK `consumer_price_toman > 0`): قیمت مصرف‌کننده درج‌شده روی کالا.
* `is_current` (`BOOLEAN`, NOT NULL DEFAULT TRUE): نشانگر قیمت فعال جاری.
* `valid_from` (`TIMESTAMPTZ`, NOT NULL DEFAULT CURRENT_TIMESTAMP).
* `valid_to` (`TIMESTAMPTZ`): زمان انقضای قیمت قبلی.
* **قید تضمین تک‌قیمتی جاری در سطح دیتابیس:**
  `CREATE UNIQUE INDEX uq_vendor_product_current_price ON vendor_prices(vendor_product_id) WHERE is_current = TRUE;`

### ۲.۳. جدول موجودی انبار بنکدار (`vendor_inventory`)
مدیریت کمیت فیزیکی، رزروشده و قابل‌فروش بر پایه واحدهای عمومی:
* `id` (`UUID`, PK, `DEFAULT gen_random_uuid()`).
* `vendor_product_id` (`UUID`, UNIQUE NOT NULL REFERENCES `vendor_products(id)` ON DELETE CASCADE).
* `inventory_unit` (`VARCHAR(30)`, NOT NULL DEFAULT 'CARTON' CHECK `inventory_unit IN ('CARTON', 'BOX', 'PACK', 'PIECE', 'KG', 'BUNDLE', 'BAG')`).
* `physical_quantity` (`INTEGER`, NOT NULL DEFAULT 0 CHECK `physical_quantity >= 0`): موجودی فیزیکی در انبار.
* `reserved_quantity` (`INTEGER`, NOT NULL DEFAULT 0 CHECK `reserved_quantity >= 0`): مقدار رزروشده در سفارش‌های تاییدشده.
* `available_quantity` (`INTEGER` GENERATED ALWAYS AS (`physical_quantity - reserved_quantity`) STORED CHECK `available_quantity >= 0`): مقدار قابل‌فروش.
* `moq` (`INTEGER`, NOT NULL DEFAULT 1 CHECK `moq >= 1`): حداقل تعداد سفارش (Minimum Order Quantity).
* `last_stock_check_at` (`TIMESTAMPTZ`, NOT NULL DEFAULT CURRENT_TIMESTAMP).
* `updated_at` (`TIMESTAMPTZ`, NOT NULL DEFAULT CURRENT_TIMESTAMP).

### ۲.۴. جدول لاگ حسابرسی موجودی (`inventory_audit_log`)
ثبت تغییرناپذیر تمام تراکنش‌های موثر بر انبار:
* `id` (`UUID`, PK, `DEFAULT gen_random_uuid()`).
* `vendor_product_id` (`UUID`, NOT NULL REFERENCES `vendor_products(id)` ON DELETE CASCADE).
* `change_reason` (`VARCHAR(50)`, NOT NULL CHECK `change_reason IN ('INITIAL_STOCK', 'MANUAL_COUNT', 'ORDER_RESERVED', 'ORDER_CANCELLED', 'ORDER_DISPATCHED', 'SHORTAGE_ADJUSTED', 'DAMAGED_RETURN')`).
* `quantity_delta` (`INTEGER`, NOT NULL): میزان تغییر (مثبت یا منفی).
* `resulting_physical_quantity` (`INTEGER`, NOT NULL).
* `resulting_reserved_quantity` (`INTEGER`, NOT NULL).
* `actor_user_id` (`UUID`, REFERENCES `users(id)`).
* `notes` (`TEXT`).
* `created_at` (`TIMESTAMPTZ`, NOT NULL DEFAULT CURRENT_TIMESTAMP).

### ۲.۵. جدول اسنپ‌شات‌های رتبه‌بندی بنکدار (`reputation_snapshots`)
ردگیری ممیزی‌پذیر تاریخچه نمرات اعتبار و عملکرد:
* `id` (`UUID`, PK, `DEFAULT gen_random_uuid()`).
* `vendor_id` (`UUID`, NOT NULL REFERENCES `vendors(id)` ON DELETE CASCADE).
* `rating_score` (`DECIMAL(3, 2)`): امتیاز عملکرد (برای بنکدار با صفر سفارش مقدار `NULL` است).
* `confidence_score` (`DECIMAL(3, 2)`, NOT NULL DEFAULT 0.00): ضریب اطمینان بر اساس تعداد فاکتورها.
* `sample_size` (`INTEGER`, NOT NULL DEFAULT 0): تعداد کل سفارش‌های ارزیابی‌شده در پنجره زمانی.
* `window_start` (`TIMESTAMPTZ`, NOT NULL).
* `window_end` (`TIMESTAMPTZ`, NOT NULL).
* `calculation_version` (`VARCHAR(20)`, NOT NULL DEFAULT '1.0').
* `calculated_at` (`TIMESTAMPTZ`, NOT NULL DEFAULT CURRENT_TIMESTAMP).

---

## ۳. انواریانت‌های حاکم بر عرضه و انبار (Inventory Invariants)

1. **یکتایی اسکوپ کد کالا:** مقدار `vendor_sku` صرفاً در سطح همان بنکدار یکتاست؛ دو بنکدار مستقل مجازند کدهای کالای داخلی مشابه داشته باشند.
2. **عدم انحصار در بسته‌بندی:** بنکدار می‌تواند یک کالای خاص را هم به صورت کارتن ۱۲ تایی و هم کارتن ۲۴ تایی به صورت دو پیشنهاد تجاری مجزا ثبت کند.
3. **تضمین دیتابیسی عدم وجود دو قیمت جاری:** به وسیله ایندکس جزئی دیتابیس، هرگز نمی‌توان به طور همزمان دو قیمت با `is_current = TRUE` برای یک کالا فعال داشت.
4. **رفتار پیش‌فرض برای بنکدار جدید:** بنکدار تازه ثبت‌نام‌شده با صفر سفارش هرگز دارای امتیاز ساختگی ۵.۰ نمی‌باشد؛ نمره اعتبار او `NULL` و وضعیتش `NEW` است.
