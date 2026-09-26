# قراردادهای جامع رابط برنامه‌نویسی نرم‌افزار (POL Canonical API Contracts)
## مشخصات فنی اندپوینت‌ها، کدهای خطا، اعتبارسنجی و کلیدهای هم‌توانی
**شناسه سند:** `API-SPEC-001`  
**نسخه:** ۱.۰ (تثبیت‌شده)  
**وضعیت:** سند مرجع مهندسی نرم‌افزار (Canonical Technical Specification)  

---

## ۱. استانداردهای عمومی و ساختار کانونیکال (API Standards & Conventions)

* **آدرس پایه (Base URL):** `https://api.polmarket.ir/api/v1`
* **فرمت انتقال داده:** `application/json` با کاراکترست `utf-8`.
* **احراز هویت:** هدر استاندارد `Authorization: Bearer <JWT_ACCESS_TOKEN>`.
* **کلید هم‌توانی (Idempotency):** درخواست‌های جهش داده‌ای که ایجاد اثر خارجیِ قابل‌تکرار دارند (مانند ثبت سفارش، درخواست مرجوعی و تخصیص referral) باید idempotency contract مشخص داشته باشند. در مسیرهایی که چنین قرارداد canonicalای تعریف نشده، transport نباید یک هدر idempotency صوری اضافه کند. Checkout از کلید و fingerprint در پایگاه‌داده استفاده می‌کند؛ Redis به‌عنوان SSoT اجرای checkout نیست.
* **الگوی استاندارد پاسخ خطا (Error Response Schema):**
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "موجودی قابل‌فروش این کالا نزد بنکدار کمتر از مقدار درخواستی است.",
    "details": {
      "product_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "available_quantity": 5,
      "requested_quantity": 10,
      "unit": "CARTON"
    },
    "timestamp": "2026-09-11T20:00:00Z"
  }
}
```

---

## ۲. اندپوینت‌های کاتالوگ، بارکد و کاندیدای کالا (Catalog & Barcode APIs)

### ۲.۱. جستجوی فازی محصولات (`GET /products/search`)
* **مجوز:** عمومی / نیازمند لاگین سوپرمارکت یا بنکدار.
* **پارامترهای Query:** `q` (رشته جستجو), `category_id` (اختیاری), `page` (پیش‌فرض ۱), `limit` (پیش‌فرض ۲۰).
* **پاسخ موفق (200 OK):**
```json
{
  "success": true,
  "data": {
    "products": [
      {
        "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        "master_sku": "POL-PRD-004821",
        "canonical_name_fa": "مایع ظرفشویی پریل ۴ لیتری لیمویی",
        "brand_name": "پریل",
        "pack_unit": "CARTON",
        "pack_quantity": 4,
        "primary_image_url": "https://storage.polmarket.ir/products/canonical/pril-4l.webp",
        "lowest_unit_price_toman": 380000,
        "available_vendors_count": 3
      }
    ],
    "pagination": { "page": 1, "limit": 20, "total": 1 }
  }
}
```

### ۲.۲. استعلام فوری بارکد در انبارداری سریع (`POST /products/match-barcode`)
* **مجوز:** نقش بنکدار (`VENDOR_OWNER`, `VENDOR_STAFF`) یا فعال‌ساز میدانی.
* **بدنه درخواست (Request Body):**
```json
{
  "raw_barcode": "6260123456789",
  "scan_source": "CAMERA_CONTINUOUS_SCAN"
}
```
* **پاسخ موفق - انطباق قطعی (200 OK):**
```json
{
  "success": true,
  "match_status": "EXACT",
  "confidence_score": 1.0,
  "product": {
    "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "master_sku": "POL-PRD-004821",
    "canonical_name_fa": "مایع ظرفشویی پریل ۴ لیتری لیمویی",
    "brand_name": "پریل",
    "default_pack_quantity": 4,
    "image_url": "https://storage.polmarket.ir/products/canonical/pril-4l.webp"
  }
}
```
* **پاسخ در حالت عدم انطباق (200 OK با وضعیت NO_MATCH):**
```json
{
  "success": true,
  "match_status": "NO_MATCH",
  "confidence_score": 0.0,
  "suggested_action": "CREATE_PRODUCT_CANDIDATE"
}
```

### ۲.۳. ثبت کاندیدای کالای ناشناخته (`POST /product-candidates`)
* **هدف:** جلوگیری از توقف کار بنکدار هنگام مواجهه با بارکد جدید.
* **بدنه درخواست:**
```json
{
  "proposed_title": "مایع سفیدکننده ۱ لیتری گلرنگ معطر",
  "proposed_brand": "گلرنگ",
  "barcode": "6260987654321",
  "vendor_sku": "GLR-BL-1L",
  "photo_asset_id": "c1f7b810-9dad-11d1-80b4-00c04fd430c9"
}
```
* **پاسخ موفق (201 Created):**
```json
{
  "success": true,
  "candidate_id": "a5c7b810-9dad-11d1-80b4-00c04fd430ca",
  "status": "PENDING_REVIEW",
  "message": "کاندیدا با موفقیت ثبت شد و در کارتابل بررسی تیم کاتالوگ قرار گرفت."
}
```

---

## ۳. اندپوینت‌های انبار و ورود سریع بنکدار (Vendor Inventory APIs)

### ۳.۱. ثبت یا به‌روزرسانی سریع در اسکن پیوسته (`POST /vendors/inventory/continuous-scan`)
* **بدنه درخواست:**
```json
{
  "product_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "vendor_sku": "PRL-4L-LEMON",
  "packaging_unit": "CARTON",
  "pack_quantity": 4,
  "physical_quantity": 50,
  "unit_price_toman": 380000,
  "consumer_price_per_unit_toman": 115000,
  "session_id": "scan_sess_991823"
}
```
* **پاسخ موفق (200 OK):**
```json
{
  "success": true,
  "vendor_product_id": "3d57b810-9dad-11d1-80b4-00c04fd430cb",
  "available_quantity": 50,
  "inventory_unit": "CARTON",
  "unit_price_toman": 380000,
  "freshness_status": "FRESH",
  "updated_at": "2026-09-11T20:05:00Z"
}
```

### ۳.۲. انتشار گروهی اقلام نشست انبارداری (`POST /vendors/inventory/publish`)
* **هدف:** خروج اقلام اسکن‌شده از حالت پیش‌نویس جلسه به وضعیت فعال در مارکت‌پلیس.

---

## ۴. اندپوینت‌های سبد خرید و پیش‌نمایش تخصیص (Commerce APIs)

### ۴.۰. ایجاد سبد خرید (`POST /baskets`)
* **مجوز:** کاربر احراز هویت‌شده با عضویت فعال در یک سازمان خرده‌فروشی (`RETAILER_OWNER`, `RETAILER_STAFF`).
* **بدنه درخواست:** ندارد.
* **پاسخ موفق (201 Created):**
```json
{
  "success": true,
  "data": {
    "basket_id": "7f17b810-9dad-11d1-80b4-00c04fd430cc",
    "version": 1,
    "status": "OPEN"
  }
}
```
> شناسه خرده‌فروش از `ApplicationContext` و عضویت فعال استخراج می‌شود و از کلاینت دریافت نمی‌شود.

### ۴.۱. افزودن قلم به سبد خرید (`POST /baskets/:id/items`)
* **بدنه درخواست:**
```json
{
  "product_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "requested_quantity": 10,
  "pack_quantity": 4,
  "expected_version": 1
}
```
* **قفل همزمانی:** `expected_version` باید با نسخه فعلی سبد برابر باشد؛ در صورت mismatch، تغییر اعمال نمی‌شود و درخواست رد می‌شود.

### ۴.۲. پیش‌نمایش و تولید برنامه تخصیص سبد (`POST /baskets/:id/allocation-preview`)
* **مجوز:** کاربر خرده‌فروش احراز هویت‌شده در tenant فعال.
* **رفتار کانونیکال:** اجرای Allocation Engine روی snapshot نسخه فعلی سبد و ذخیره `allocation_plan` و `allocation_items` کانونیکال. برنامه ایجادشده با lifecycle فعلی `CONFIRMED` ذخیره می‌شود تا مستقیماً برای `POST /orders` قابل checkout باشد؛ این مسیر پرداخت را اجرا نمی‌کند.

* **معماری مرجع:** منطبق با تصمیم مصوب **D-014 (Multi-Vendor Basket in MVP)**.
* **هدف:** ارزیابی بهینه موجودی، قیمت و حداقل سفارش بنکداران شهرک و تولید پیش‌فاکتور تخصیص چندبنکدار.
* **قاعده تخصیص:** در سطح قلم کالا (Line-Item) با کمینه‌سازی خردشدگی سبد؛ عدم شکست تیراژ یک قلم میان چند بنکدار.
* **پاسخ موفق (200 OK):**
```json
{
  "success": true,
  "allocation_plan_id": "7f17b810-9dad-11d1-80b4-00c04fd430cc",
  "strategy": "MULTI_VENDOR_MIN_FRAGMENTATION",
  "vendor_count": 2,
  "allocated_vendors": [
    {
      "vendor_id": "1a27b810-9dad-11d1-80b4-00c04fd430cd",
      "business_name": "بنکداری حاج محمود",
      "subtotal_toman": 6000000,
      "min_order_value_toman": 5000000,
      "mov_satisfied": true,
      "allocated_items_count": 2
    },
    {
      "vendor_id": "2b38c921-8ebe-22e2-91c5-11d15fe541de",
      "business_name": "بنکداری کریمی",
      "subtotal_toman": 8000000,
      "min_order_value_toman": 4000000,
      "mov_satisfied": true,
      "allocated_items_count": 2
    }
  ],
  "summary": {
    "total_items_requested": 5,
    "total_items_allocated": 4,
    "total_items_unfulfilled": 1,
    "total_amount_toman": 14000000,
    "estimated_delivery_cost_toman": 0
  },
  "unfulfilled_items": [
    {
      "product_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6e",
      "requested_quantity": 10,
      "unit": "CARTON",
      "reason_code": "OUT_OF_STOCK"
    }
  ]
}
```

---

## ۵. اندپوینت‌های سفارش و ماشین وضعیت (Order Lifecycle APIs)

### ۵.۱. ثبت نهایی سفارش از برنامه تخصیص (`POST /orders`)
* **هدر الزامی:** `Idempotency-Key: <UUID>`
* **بدنه درخواست:**
```json
{
  "allocation_plan_id": "7f17b810-9dad-11d1-80b4-00c04fd430cc",
  "delivery_address": "اهواز، زیتون کارمندی، خ حجت، نبش زمرد",
  "preferred_payment_method": "POS_DRIVER"
}
```

> **Transport boundary note (Batch 6C-3):** `preferred_payment_method` is accepted as part of the checkout request contract, but the current canonical order schema does not persist a checkout-level payment-method preference. Payment execution/evidence is a separate downstream capability; the HTTP transport must not invent a new persistence field or execute payment as part of checkout.
* **پاسخ موفق (201 Created):** ایجاد گروه سفارش والد (`order_groups`) و سفارش‌های فرزند مستقل (`orders`) به ازای هر بنکدار با وضعیت `SUBMITTED` (وضعیت کانونی مطابق `Order_Lifecycle.md` و قید DDL جدول `orders`؛ وضعیت `PENDING` منسوخ است).
```json
{
  "success": true,
  "order_group_id": "9c1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb7f",
  "group_status": "ACTIVE",
  "total_amount_toman": 14000000,
  "child_orders": [
    {
      "order_id": "ord_1a_uuid",
      "vendor_id": "1a27b810-9dad-11d1-80b4-00c04fd430cd",
      "order_status": "SUBMITTED",
      "subtotal_toman": 6000000
    },
    {
      "order_id": "ord_2b_uuid",
      "vendor_id": "2b38c921-8ebe-22e2-91c5-11d15fe541de",
      "order_status": "SUBMITTED",
      "subtotal_toman": 8000000
    }
  ]
}
```

### ۵.۲. پذیرش کامل سفارش توسط بنکدار (`POST /orders/:id/accept`)
* **مجوز:** بنکدار مقصد در سازمان فعال (VENDOR_OWNER, VENDOR_STAFF). شناسه بنکدار و tenant از ApplicationContext استخراج می‌شود و از کلاینت دریافت نمی‌شود.
* **بدنه درخواست:** ندارد.
* **انتقال وضعیت:** فقط SUBMITTED -> ACCEPTED.
* **پیامد کانونیکال:** همه reservationهای فعال سفارش به CONSUMED منتقل می‌شوند، reserved_quantity به همان میزان کاهش و physical_quantity کسر می‌شود، accepted_quantity اقلام برابر مقدار سفارش می‌شود و برای اعضای فعال سازمان خرده‌فروش رویداد ORDER_ACCEPTED در outbox ایجاد می‌شود.
* **اعلام وضعیت غیرمجاز:** اگر سفارش در وضعیت دیگری باشد، درخواست رد می‌شود و mutation جزئی باقی نمی‌ماند.
* **پاسخ موفق (200 OK):** شامل order_id, order_number, order_group_id, order_status, total_amount_toman, accepted_item_count, reservation_count.

### ۵.۳. رد کامل سفارش توسط بنکدار (`POST /orders/:id/reject`)
* **مجوز:** بنکدار مقصد در سازمان فعال (`VENDOR_OWNER`, `VENDOR_STAFF`). شناسه بنکدار و tenant از `ApplicationContext` استخراج می‌شود.
* **بدنه درخواست:**
```json
{
  "reason": "Out of physical stock"
}
```
* **انتقال وضعیت:** فقط `SUBMITTED -> REJECTED`.
* **پیامد کانونیکال:** همه reservationهای فعال سفارش به `RELEASED` منتقل می‌شوند و `reserved_quantity` به همان میزان کاهش می‌یابد؛ موجودی فیزیکی تغییر نمی‌کند؛ `rejection_reason` روی سفارش ثبت می‌شود و برای اعضای فعال سازمان خرده‌فروش رویداد `ORDER_REJECTED` در outbox ایجاد می‌شود.
* **اعلام وضعیت غیرمجاز:** اگر سفارش در وضعیت دیگری باشد، درخواست رد می‌شود و mutation جزئی باقی نمی‌ماند.
* **پاسخ موفق (200 OK):** شامل `order_id`, `order_number`, `order_group_id`, `order_status`, `total_amount_toman`, `rejection_reason`, `released_reservation_count`.

### ۵.۴. پذیرش با کسری موجودی — پروتکل دوطرفه

پذیرش ناقص مستقیماً توسط بنکدار وضعیت سفارش را تغییر نمی‌دهد. این capability یک پروتکل سه‌مرحله‌ای دارد:

**مرحله ۱ — پیشنهاد بنکدار**
`POST /api/v1/orders/:id/partial-acceptance-proposals`

* **مجوز:** بنکدار مقصد در سازمان فعال (`VENDOR_OWNER`, `VENDOR_STAFF`).
* **Idempotency:** هدر `Idempotency-Key` باید UUIDv4 باشد.
* **بدنه درخواست:**
```json
{
  "items": [
    { "order_item_id": "item_uuid_1", "accepted_quantity": 7, "reason": "SHORTAGE" }
  ]
}
```
* اقلام ذکرنشده در proposal، در زمان approval با مقدار کامل سفارش پذیرفته می‌شوند.
* حداقل یک قلم باید کاهش مقدار داشته باشد و برای هر قلم کاهش‌یافته `reason` الزامی است.
* ایجاد proposal فقط proposal و اقلام proposal را ثبت و رویداد `ORDER_PARTIAL_ACCEPTANCE_PROPOSED` را در outbox ایجاد می‌کند؛ سفارش همچنان `SUBMITTED` و موجودی بدون تغییر باقی می‌ماند.
* در هر سفارش فقط یک proposal با وضعیت `PENDING` می‌تواند وجود داشته باشد.

**مرحله ۲ — تایید خرده‌فروش**
`POST /api/v1/orders/:id/partial-acceptance-proposals/:proposal_id/approve`

* **مجوز:** خرده‌فروش مقصد (`RETAILER_OWNER`, `RETAILER_STAFF`) در سازمان فعال.
* **انتقال وضعیت:** فقط `SUBMITTED -> PARTIALLY_ACCEPTED`.
* **پیامد:** `accepted_quantity` هر قلم از proposal اعمال می‌شود؛ اقلام کاهش‌یافته `SHORTAGE` می‌گیرند؛ `order_items.total_line_amount_toman`، مبلغ `orders` و مبلغ `order_groups` با مقدار پذیرفته‌شده بازمحاسبه می‌شوند.
* **رزرو انبار:** مقدار رزروشده کامل از `reserved_quantity` آزاد و مقدار پذیرفته‌شده از `physical_quantity` کسر می‌شود. `inventory_reservations.status` به `CONSUMED` می‌رود و `consumed_quantity` مقدار واقعی مصرف‌شده را ثبت می‌کند؛ بخش آزادشده از `quantity - consumed_quantity` قابل محاسبه است.
* **خروجی:** رویداد `ORDER_PARTIALLY_ACCEPTED` برای اعضای فعال سازمان خرده‌فروش و بنکدار در outbox ثبت می‌شود.
* بدون تایید خرده‌فروش هیچ تغییر وضعیت سفارش، مبلغ یا موجودی انجام نمی‌شود.

**مرحله ۳ — رد پیشنهاد توسط خرده‌فروش**
`POST /api/v1/orders/:id/partial-acceptance-proposals/:proposal_id/decline`

* **مجوز:** خرده‌فروش مقصد (`RETAILER_OWNER`, `RETAILER_STAFF`).
* **بدنه اختیاری:**
```json
{ "reason": "Need full quantity" }
```
* proposal به `DECLINED` می‌رود؛ سفارش، مبلغ و موجودی بدون تغییر می‌مانند و رویداد `ORDER_PARTIAL_ACCEPTANCE_DECLINED` برای اعضای فعال بنکدار ایجاد می‌شود.
* پس از رد، در صورت باقی‌ماندن سفارش در `SUBMITTED`، proposal جدید با Idempotency-Key جدید مجاز است.

**محدودیت متقابل:** تا وقتی proposal در وضعیت `PENDING` است، full accept و full reject همان سفارش مجاز نیستند.

### ۵.۵. تایم‌اوت سیستمی تایید بنکدار (Worker)
* **محرک:** worker زمانی که `vendor_acceptance_deadline_at` سپری شده باشد.
* **انتقال وضعیت:** فقط `SUBMITTED -> CANCELLED` با `cancellation_reason = VENDOR_TIMEOUT`.
* **شرط زمانی:** دقیقاً ۲ ساعت کاری بر اساس تقویم `AHVAZ_WHOLESALE`; شنبه تا پنج‌شنبه ۰۸:۰۰ تا ۱۸:۰۰، جمعه و تعطیلات فعال در `operational_holidays` خارج از SLA هستند.
* **پیامد:** reservationهای `ACTIVE` آزاد می‌شوند؛ `reserved_quantity` کاهش می‌یابد؛ موجودی فیزیکی تغییر نمی‌کند؛ proposal ناقصِ `PENDING` غیرقابل‌اجرا شده و `DECLINED` با دلیل `VENDOR_TIMEOUT` می‌شود.
* **رویداد و عملیات:** `ORDER_CANCELLED` برای اعضای فعال خرده‌فروش در outbox؛ رکورد `ACCEPTANCE_LATE` با اثر `-0.25` در `vendor_reliability_events`; taskهای `VENDOR_TIMEOUT` برای کاربران فعال `FIELD_ACTIVATOR`/`OPS_ADMIN`/`SUPER_ADMIN`.

### ۵.۶. اعلام خروج و بارگیری وانت (`POST /orders/:id/dispatch`)
* **انتقال وضعیت مجاز:** `READY -> DISPATCHED`.
* **بدنه درخواست:**
```json
{
  "driver_name": "احمد رضایی",
  "driver_phone": "09161112233",
  "vehicle_plate": "14ب256-ایران24",
  "carrier_name": "باربری شهرک بنکداران"
}
```

### ۵.۶. تایید تحویل در مقصد (`POST /orders/:id/deliver`)
* **انتقال وضعیت مجاز:** `DISPATCHED -> DELIVERED`.
* **هدر/فیلد تایید:** کد تایید تحویل (OTP) یا امضای الکترونیک سوپرمارکت‌دار.

### ۵.۷. ثبت فیش واریز / شواهد پرداخت مستقیم (`POST /orders/:id/payments/direct-transfer`)
* **معماری مرجع:** منطبق با مدل **NON_CUSTODIAL_DIRECT (Zero Escrow - عدم نگهداری وجوه توسط پلتفرم)**.
* **مجوز:** خریدار (`RETAILER_OWNER`, `RETAILER_STAFF`).
* **بدنه درخواست:**
```json
{
  "amount_toman": 6000000,
  "payment_method": "DIRECT_BANK_TRANSFER",
  "reference_number": "TX-778899",
  "evidence_media_id": "c1f7b810-9dad-11d1-80b4-00c04fd430c9",
  "notes": "واریز به حساب ملت بنکدار"
}
```
* **وضعیت‌های مجاز پرداخت (Canonical Payment States):**
  * `PENDING`: ثبت فیش، در انتظار تایید بنکدار.
  * `INITIATED`: شروع اعتبارسنجی فیش توسط درگاه یا پرسنل.
  * `SUCCESS`: تایید قطعی وصول وجه توسط بنکدار.
  * `FAILED`: رد فیش به علت عدم تطابق مبلغ یا شماره پیگیری.
  * `CANCELLED`: لغو پیش از تایید.
  * `REFUNDED`: استرداد مستقیم در صورت فسخ.
* **پاسخ موفق (201 Created):** ایجاد رکورد در جدول `payments` با `custody_model = 'NON_CUSTODIAL_DIRECT'` و وضعیت `PENDING`.

### ۵.۸. تأیید وصول وجه توسط بنکدار (`POST /orders/:id/payments/:payment_id/verify`)
* **مجوز:** بنکدار مقصد (`VENDOR_OWNER`).
* **پیامد:**
  * تغییر وضعیت پرداخت به `payment_status = 'SUCCESS'`, ثبت `verified_by = user.id` و `verified_at = now()`.
  * ایجاد رکورد تسویه در جدول `settlements` با وضعیت `CALCULATED` و نرخ کارمزد پایلوت ۰٪ (`commission_rate = 0`).

---

## ۶. اندپوینت‌های دعاوی تجاری و مغایرت (Dispute APIs)

### ۶.۱. ثبت مغایرت یا خرابی بار (`POST /orders/:id/disputes`)
* **شرط اعتبارسنجی:** وضعیت سفارش باید `DELIVERED` باشد و کمتر از ۴ ساعت از تحویل گذشته باشد. وضعیت سفارش به `DISPUTED` تغییر نمی‌کند، بلکه `orders.dispute_status` برابر `OPEN` می‌شود.
* **بدنه درخواست:**
```json
{
  "claimed_amount_toman": 380000,
  "description": "یک کارتن مایع ظرفشویی قوطی‌های آن پاره شده و نشتی داشت.",
  "evidence_media_id": "c1f7b810-9dad-11d1-80b4-00c04fd430c9"
}
```

### ۶.۲. داوری و بستن پرونده مغایرت (`PATCH /disputes/:id/resolve`)
* **مجوز:** نقش داور و پشتیبانی پلتفرم (`OPS_ADMIN`).
* **بدنه درخواست:**
```json
{
  "outcome": "ADJUSTED_SHORTAGE",
  "approved_amount_toman": 380000,
  "reason": "تایید خسارت توسط راننده باربری؛ اعمال بستانکاری در فاکتور بعدی"
}
```
* **پیامد:** ایجاد رکورد در `settlement_adjustments`، محاسبه مجدد خالص دریافتی بنکدار، و انتقال `dispute_status` به `CLOSED`.


---

## ۷. اندپوینت‌های احراز هویت، سازمان و مدیریت سشن‌ها (Identity & Auth APIs)

> **HTTP transport base path:** `/api/v1`. مسیرهای زیر در این بخش به‌صورت نسبی نسبت به این prefix نوشته شده‌اند. اولین transport implementation در `scripts/api/` قرار دارد.

### ۷.۱. درخواست رمز یک‌بار مصرف (`POST /auth/request-otp`)
* **مجوز:** عمومی (محدودیت تعداد درخواست: حداکثر ۳ بار در هر ۵ دقیقه به ازای هر شماره تلفن و آی‌پی — اعمال D-018 فقط برای اهداف `LOGIN` و `REGISTER`؛ اهداف `ORDER_CONFIRMATION` و `DELIVERY_CONFIRM` خارج از سیاست فعلی D-018 هستند).
* **بدنه درخواست:**
```json
{
  "mobile_number": "+989161112233",
  "client_fingerprint": "fp_chrome_win11_a9f1"
}
```
* **پاسخ موفق (200 OK):**
```json
{
  "success": true,
  "data": {
    "otp_request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "expires_in_seconds": 120,
    "resend_interval_seconds": 60
  }
}
```

### ۷.۲. تأیید رمز یک‌بار مصرف و صدور توکن (`POST /auth/verify-otp`)
* **مجوز:** عمومی.
* **قانون ضد Brute-Force:** پس از ۵ بار اشتباه، OTP باطل شده و شماره ۱۰ دقیقه مسدود می‌شود.
* **بدنه درخواست:**
```json
{
  "mobile_number": "+989161112233",
  "otp_code": "7341",
  "device_info": {
    "device_type": "MOBILE_ANDROID",
    "fcm_token": "fcm_dK9sL2...",
    "app_version": "1.0.0"
  }
}
```
* **پاسخ موفق (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "refresh_token": "a1B2c3D4e5F6g7H8i9J0...",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "id": "b2c140a3-f04b-4c22-9218-c2fa5342a781",
      "mobile_number": "+989161112233",
      "full_name": "حسین گلستانی"
    },
    "current_organization": {
      "id": "7d91e843-c03b-4191-87aa-29775089c93a",
      "name": "سوپرمارکت گلستان",
      "type": "RETAILER",
      "role": "RETAILER_OWNER"
    },
    "available_organizations": [
      {
        "id": "7d91e843-c03b-4191-87aa-29775089c93a",
        "name": "سوپرمارکت گلستان",
        "type": "RETAILER",
        "role": "RETAILER_OWNER"
      }
    ]
  }
}
```

### ۷.۳. تازه‌سازی توکن دسترسی (`POST /auth/refresh`)
* **مجوز:** عمومی (نیاز به refresh_token معتبر).
* **Rotation:** هر refresh موفق، refresh token قبلی را مصرف و یک refresh token جدید صادر می‌کند؛ replay توکن قبلی باید fail-closed شود.
* **بدنه درخواست:**
```json
{
  "refresh_token": "a1B2c3D4e5F6g7H8i9J0..."
}
```
* **پاسخ موفق (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "refresh_token": "new-rotated-refresh-token...",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```
* **پاسخ خطا (401):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REFRESH_TOKEN",
    "message": "Refresh token is invalid or expired.",
    "details": {},
    "timestamp": "2026-09-18T12:00:00Z"
  }
}
```
```json
{
  "success": false,
  "error": {
    "code": "SESSION_EXPIRED",
    "message": "Session has expired. Please re-authenticate.",
    "details": {},
    "timestamp": "2026-09-18T12:00:00Z"
  }
}
```
```json
{
  "success": false,
  "error": {
    "code": "SESSION_REVOKED",
    "message": "Session has been revoked.",
    "details": {},
    "timestamp": "2026-09-18T12:00:00Z"
  }
}
```
* **Governance note (D-018):** refresh-token rotation policy هنوز تصمیم‌گیری نشده است. رفتار فعلی implementation این است که refresh token را در هر refresh موفق rotate می‌کند و replay توکن قبلی را fail-closed می‌کند؛ این جمله صرفاً وضعیت runtime فعلی است و به‌عنوان policy نهایی تلقی نمی‌شود.

### ۷.۴. سوئیچ بین سازمان‌ها (`POST /auth/switch-organization`)
* **مجوز:** کاربر احراز هویت شده دارای بیش از یک عضویت فعال.
* **بدنه درخواست:**
```json
{
  "target_organization_id": "7d91e843-c03b-4191-87aa-29775089c93a"
}
```
* **پاسخ موفق (200 OK):** توکن JWT جدید با ادعای `org_id` و `role` سازمان مقصد صادر می‌شود. پیاده‌سازی فعلی در `switch_organization` refresh token را rotate نمی‌کند؛ rotation در endpoint `POST /auth/refresh` انجام می‌شود. سیاست نهایی rotation طبق D-018 هنوز TBD است.
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "token_type": "Bearer",
    "expires_in": 900,
    "session": {
      "id": "uuid",
      "active_organization_id": "target_org_uuid",
      "status": "ACTIVE"
    }
  }
}
```

### ۷.۵. خروج از حساب و ابطال سشن (`DELETE /auth/sessions/current` و `DELETE /auth/sessions/:id`)
* **پاسخ موفق (200 OK):** سشن در جدول `user_sessions` به وضعیت `status = 'REVOKED'` و `revoked_at = now()` درمی‌آید.

---

## ۷.۶ Privacy Export / Account Deletion APIs

### ۷.۶.۱ درخواست دریافت داده شخصی (`POST /api/v1/privacy/export`)
- **مجوز:** فقط کاربر احراز هویت‌شده و فقط داده‌های متعلق به همان `user_id`.
- **رفتار:** snapshot نسخه‌دار از داده‌های مستقیم هویتی، پروفایل، عضویت‌ها، دستگاه‌ها، رضایت‌ها و شمارنده‌های فعالیت بازمی‌گرداند. محتوای snapshot به‌عنوان artifact دائمی در DB نگهداری نمی‌شود؛ فقط SHA-256 درخواست ثبت می‌شود.
- **پاسخ:** `request.status = COMPLETED` و `request.export_sha256` به‌همراه `data`.

### ۷.۶.۲ حذف حساب (`POST /api/v1/privacy/deletion`)
- **مجوز:** فقط کاربر احراز هویت‌شده برای حساب خودش.
- **رفتار:** یک درخواست privacy با lifecycle `REQUESTED → PROCESSING → COMPLETED` ثبت می‌شود؛ سپس PII مستقیم de-identify می‌شود، session/device/consent access revoke می‌شود و سوابق مالی/تجاری/حسابرسی برای حفظ یکپارچگی نگه داشته می‌شوند.
- **قاعده:** hard-delete کاربر انجام نمی‌شود؛ `user_id` برای referential/audit integrity باقی می‌ماند و داده‌های مستقیم شخصی به tombstone تبدیل می‌شوند.

## ۸. اندپوینت‌های تیکت‌ها و پرونده‌های پشتیبانی عمومی (Support Case APIs)

> **قاعده دامنه‌ای:** تیکت‌های پشتیبانی عمومی (`support_cases`) کاملاً مستقل از دعاوی تجاری (`disputes`) هستند. ایجاد تیکت پشتیبانی وضعیت مالی سفارش یا تسویه حساب را متوقف نمی‌کند.

### ۸.۱. ایجاد تیکت پشتیبانی جدید (`POST /support/cases`)
* **مجوز:** تمامی کاربران احراز هویت شده.
* **بدنه درخواست:**
```json
{
  "case_type": "INVOICE_INQUIRY",
  "priority": "NORMAL",
  "subject": "درخواست راهنمایی در خصوص فاکتور رسمی",
  "description": "با سلام، چگونه می‌توانم فاکتور ارزش افزوده این ماه را به صورت PDF تجمیعی دریافت کنم؟",
  "related_order_id": "ord_1a_uuid"
}
```
* **مقادیر مجاز اولویت (`priority`):** `LOW`, `NORMAL`, `HIGH`, `CRITICAL`.
* **مقادیر مجاز نوع تیکت (`case_type`):** `GENERAL`, `TECHNICAL`, `INVOICE_INQUIRY`, `ACCOUNT_ACCESS`, `FEEDBACK`.

### ۸.۲. ارسال پیام در رشته‌گفتگوی تیکت (`POST /support/cases/:id/messages`)
* **بدنه درخواست:**
```json
{
  "message_text": "سلام، از بخش فاکتورها در منوی حساب کاربری می‌توانید دانلود فرمایید.",
  "is_internal": false,
  "attachment_media_id": "c1f7b810-9dad-11d1-80b4-00c04fd430c9"
}
```
* *نکته ۱:* پارامتر `is_internal: true` منحصراً برای کارشناسان `OPS_ADMIN` جهت یادداشت‌های مخفی داخلی مجاز است.
* *نکته ۲:* پیوست‌ها از طریق کلید خارجی `attachment_media_id` به جدول `media_assets` متصل می‌شوند.

### ۸.۳. تخصیص و تغییر وضعیت تیکت (`POST /support/cases/:id/assign` و `PATCH /support/cases/:id/status`)
* **مجوز:** منحصراً `OPS_ADMIN` یا `SUPER_ADMIN`.
* **قانون تخصیص:** با ثبت انتساب جدید در `support_case_assignments`، انتساب‌های قبلی غیرفعال شده (`is_active = FALSE`) و وضعیت تیکت به `IN_PROGRESS` درمی‌آید.

---

## ۹. اندپوینت‌های صندوق اعلان و صندوق پیام کاربر (Notification & User Inbox APIs)

### ۹.۱. دریافت لیست اعلان‌های درون‌برنامه‌ای کاربر (`GET /inbox/items`)
* **پارامترهای Query:** `is_read` (اختیاری: true/false), `category` (اختیاری: ORDERS, DISPUTES, PROMOTIONS, SYSTEM), `limit` (پیش‌فرض ۲۰).
* **پاسخ موفق (200 OK):**
```json
{
  "success": true,
  "data": {
    "unread_count": 2,
    "items": [
      {
        "id": "inb_99182a",
        "title": "سفارش شما تایید شد",
        "body": "بنکداری حاج محمود سفارش شماره POL-ORD-1001 را تایید کرد و در حال جمع‌آوری است.",
        "category": "ORDERS",
        "deep_link": "/orders/ord_1a_uuid",
        "is_read": false,
        "created_at": "2026-09-13T10:15:00Z"
      }
    ]
  }
}
```

### ۹.۲. علامت‌گذاری اعلان به عنوان خوانده‌شده (`PATCH /inbox/items/:id/read` و `PATCH /inbox/items/read-all`)
* **پاسخ موفق (200 OK):** به‌روزرسانی `is_read = TRUE` و بازگشت تعداد خوانده‌نشده‌های باقی‌مانده.

### ۹.۳. مدیریت تنظیمات دریافت اعلان‌ها (`GET /notifications/preferences` و `PUT /notifications/preferences`)
* **امکان‌پذیری:** کاربر می‌تواند پیامک‌های تبلیغاتی را خاموش کند؛ اما اعلان‌های سفارش، تاخیر، مغایرت و فاکتور به دلیل حیاتی بودن غیریقابل غیرفعال‌سازی (Mandatory) هستند.

---

## ۱۰. اندپوینت‌های اعلانات همگانی و برودکست‌ها (Admin Broadcast APIs)

### ۱۰.۱. ایجاد پیش‌نویس برودکست (`POST /admin/broadcasts`)
* **مجوز:** منحصراً `OPS_ADMIN` یا `SUPER_ADMIN`.
* **بدنه درخواست:**
```json
{
  "title": "تعطیلی روز پنج‌شنبه شهرک بنکداران به علت گردوغبار",
  "body": "به اطلاع می‌رساند کلیه تحویل‌های بار روز پنج‌شنبه با ۲۴ ساعت تاخیر انجام خواهد شد.",
  "target_type": "ORGANIZATION_TYPE",
  "target_criteria": {
    "organization_type": "RETAILER",
    "city": "Ahvaz"
  },
  "channel": "INBOX_AND_SMS",
  "priority": "HIGH"
}
```

### ۱۰.۲. منجمدسازی گیرندگان و ارسال همگانی (`POST /admin/broadcasts/:id/dispatch`)
* **فرآیند سیستم:** ثبت رکوردهای گیرنده در `broadcast_recipients`، جلوگیری از ارسال تکراری با Unique Index، و درج متناظر در صندوق اعلان کاربران هدف.

---

## ۱۱. اندپوینت‌های فاکتورها و اسناد مالی (Invoicing APIs)

### ۱۱.۱. دریافت لیست فاکتورهای رسمی سازمان (`GET /invoices`)
* **مجوز:** اعضای مجاز سازمان (`RETAILER_OWNER`, `VENDOR_OWNER`, `SUPER_ADMIN`, `OPS_ADMIN`).
* **قانون چندمستأجری:** فاکتورها بر اساس سازمان فعال کاربر فیلتر می‌شوند:
  * خریدار صرفاً رکوردهای با `retailer_organization_id = user.org_id` را می‌بیند.
  * بنکدار صرفاً رکوردهای با `vendor_organization_id = user.org_id` را می‌بیند.
* **پاسخ موفق (200 OK):**
```json
{
  "success": true,
  "data": {
    "invoices": [
      {
        "id": "inv_88291a",
        "invoice_number": "INV-2026-001",
        "order_id": "ord_1a_uuid",
        "total_amount_toman": 6000000,
        "vendor_name": "بنکداری حاج محمود",
        "status": "ISSUED",
        "issued_at": "2026-09-13T11:00:00Z"
      }
    ]
  }
}
```

### ۱۱.۲. دریافت جزئیات و اقلام فاکتور (`GET /invoices/:id`)
* **شامل:** مشخصات هویتی و کد اقتصادی طرفین، لیست اقلام با قیمت واحد و تخفیف، و جمع مبالغ منطبق با فاکتور رسمی.

---

## ۱۲. اندپوینت‌های نظارت عملیاتی، نقض SLA و لاگ‌های امنیتی (Admin Ops & Audit APIs)

### ۱۲.۱. داشبورد استثنائات عملیاتی (`GET /admin/exceptions/dashboard`)
* **مجوز:** منحصراً `OPS_ADMIN` یا `SUPER_ADMIN`.
* **شاخص‌های خروجی:**
  * سفارش‌های در آستانه انقضای SLA دو ساعته پذیرش.
  * مغایرت‌های باز (`disputes`) فاقد کارشناس داور.
  * رزروهای موجودی معلقِ بیش از ۱۵ دقیقه.
  * بنکداران با نرخ رد سفارش بالاتر از ۲۰٪ در ۲۴ ساعت گذشته.

### ۱۲.۲. تمدید اضطراری زمان SLA سفارش (`POST /admin/sla-overrides`)
* **بدنه درخواست:**
```json
{
  "order_id": "ord_1a_uuid",
  "extension_minutes": 60,
  "reason": "اختلال برق در شهرک بنکداران؛ تماس تلفنی با بنکدار انجام شد."
}
```
* **پیامد:** ثبت تغییر در `orders.sla_deadline` و درج ردیابی حسابرسی در `admin_audit_logs`.

### ۱۲.۳. استعلام وقایع امنیتی و حسابرسی ادمین (`GET /admin/audit-logs`)
* **مجوز:** منحصراً `SUPER_ADMIN`.
* **پارامترها:** `actor_user_id`, `action`, `target_entity_type`, `from_date`, `to_date`.

---

## ۱۳. اندپوینت‌های کاتالوگ و دسته‌بندی کالاها (Category Operations APIs)

### ۱۳.۱. درخت دسته‌بندی کاتالوگ کانونیکال (`GET /categories`)
* **مجوز:** عمومی.
* **ساختار خروجی:** درخت سلسله‌مراتبی دسته‌بندی‌ها (مانند کالاهای اساسی > روغن > روغن خوراکی آفتابگردان) به همراه شناسه، آیکون و شمارش کالاهای فعال.

### ۱۳.۲. ایجاد یا ویرایش دسته‌بندی (`POST /admin/categories` و `PATCH /admin/categories/:id`)
* **مجوز:** منحصراً مدیر ارشد یا مدیر کاتالوگ (`OPS_ADMIN`).

---

## ۱۴. اندپوینت‌های کانونیکال پروفایل کاربری، عضویت و بافت پرسونا (User Profile & Persona APIs — D-017)

> **شفافیت وضعیت ران‌تایم (Runtime Deployment Status):**  
> کلیه مدل‌های داده، مایگریشن‌های اسکیما (`017_canonical_user_profiles_and_persona_context.sql`) و سرویس‌های دامنه برای این اندپوینت‌ها در ماژول پایتون `scripts/user_profiles.py` پیاده‌سازی شده و تحت تست جامع با PostgreSQL 18 قرار دارند. در لایه گیت‌وی وب/HTTP، این اندپوینت‌ها در وضعیت `CONTRACT_SPECIFIED / NOT_YET_DEPLOYED_AT_HTTP` مستند شده‌اند.

### ۱۴.۱. استعلام پروفایل فراگیر کاربر (`GET /api/v1/profile`)
* **آدرس:** `GET https://api.polmarket.ir/api/v1/profile`
* **احراز هویت:** `Authorization: Bearer <JWT_ACCESS_TOKEN>`
* **پاسخ موفق (200 OK):**
```json
{
  "success": true,
  "data": {
    "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "full_name": "احمد رضایی",
    "avatar_url": "https://storage.polmarket.ir/avatars/user_1.webp",
    "preferred_language": "fa",
    "timezone": "Asia/Tehran",
    "created_at": "2026-09-14T08:00:00Z",
    "updated_at": "2026-09-14T08:00:00Z"
  }
}
```

### ۱۴.۲. به‌روزرسانی پروفایل فراگیر کاربر (`PUT /api/v1/profile`)
* **بدنه درخواست (Request Body):**
```json
{
  "full_name": "احمد رضایی دهکردی",
  "avatar_url": "https://storage.polmarket.ir/avatars/user_1_new.webp",
  "preferred_language": "fa"
}
```
* **پاسخ موفق (200 OK):** اطلاعات به‌روزرسانی‌شده پروفایل.

### ۱۴.۳. استعلام درصد تکمیل پروفایل کاربر (`GET /api/v1/profile/completion`)
* **پاسخ موفق (200 OK):**
```json
{
  "success": true,
  "data": {
    "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "completion_percentage": 80,
    "missing_fields": ["avatar_url"],
    "is_complete": false
  }
}
```

### ۱۴.۴. مدیریت پروفایل عضویت در سازمان فعال (`GET` / `PUT /api/v1/membership/profile`)
* **بدنه ویرایش (PUT Request Body):**
```json
{
  "job_title": "مدیر فروش و تامین",
  "notification_preferences": {
    "sms_orders": true,
    "push_inventory_alerts": true
  }
}
```

### ۱۴.۵. دریافت بافت ترکیبی پرسونا و تننت فعال (`GET /api/v1/profile/context`)
* **پاسخ موفق (200 OK):** ساختار کامل ۵ لایه شامل اطلاعات کاربری، عضویت فعال، نقش سازمانی و پروفایل پرسونا (`retailer_profiles`، `wholesaler_profiles` یا `staff_profiles`).
* **قاعده حاکمیت کلیم‌های JWT:** کلیم‌های JWT صرفاً یک کپی مشتق‌شده و کش‌شده از وضعیت دسترسی هستند؛ SSoT اعتبار و نقش همواره جدول `organization_memberships` است.
