# معماری و مشخصات سیستم رویدادمحور (Event-Driven Architecture Spec)
## پروژه پُل (POL) — B2B FMCG Platform
**شناسه سند:** `DATA-SPEC-002`  
**وضعیت:** مصوب و نهایی  
**نسخه:** ۱.۰  
**تاریخ به‌روزرسانی:** 2026-09-18  

---

### ۱. هدف و استراتژی رویدادها (Event Strategy)
در پلتفرم پُل، تمامی رخدادهای کلیدی دامنه کسب‌وکار (Business Events)، تغییرات وضعیت، رفتارهای کاربر در اپلیکیشن و خطاهای سیستمی به صورت رویدادهای غیرقابل تغییر (Immutable Events) ثبت و منتشر می‌شوند. این معماری تضمین می‌کند که:
1. **لاگ حسابرسی کامل (Audit Trail):** هیچ رویدادی بدون ثبت هویت عامل، زمان میلی‌ثانیه‌ای و سابقه تغییر وضعیت ناپدید نمی‌شود.
2. **جداسازی تراکنش اصلی از پردازش‌های جانبی (Decoupling):** فرآیندهایی نظیر ارسال پیامک، بازمحاسبه نمره اعتبار بنکدار (SLA)، و تحلیل‌های هوش تجاری به صورت ناهمگام (Asynchronous) توسط Consumerها اجرا می‌شوند و درخواست‌های HTTP کاربر را مسدود نمی‌کنند.
3. **پایه‌گذاری هوش بازار آینده (Market Intelligence):** داده‌های رفتاری خام، سنگ‌بنای درآمدهای سال چهارم پلتفرم از تحلیل فروش و رفتار مصرف (Sell-Out Analytics) برای برندهای بزرگ FMCG خواهند بود.

---

### ۲. قرارداد ساختاری رویداد استاندارد (Canonical Event Schema)

تمامی رویدادها در سامانه پُل از اسکیما استاندارد زیر پیروی می‌کنند (JSON Schema / TypeScript Interface):

```typescript
export interface DomainEvent<T = Record<string, any>> {
  /** شناسه منحصربه‌فرد رویداد (UUID v4) */
  event_id: string;
  
  /** نام استاندارد رویداد با فرمت: <object>_<past-tense-action> */
  event_name: string;
  
  /** نسخه اسکیما برای مدیریت تغییرات رو به جلو */
  event_version: string; // e.g., "1.0"
  
  /** برچسب زمانی دقیق رویداد با منطقه زمانی UTC (ISO 8601) */
  timestamp: string; // e.g., "2026-09-11T12:00:00.000Z"
  
  /** اطلاعات بازیگر رخداد (کاربر یا سیستم) */
  actor: {
    actor_id: string; // UUID کاربر یا "SYSTEM"
    actor_role: 'RETAILER_OWNER' | 'VENDOR_OWNER' | 'VENDOR_STAFF' | 'FIELD_ACTIVATOR' | 'OPS_ADMIN' | 'SYSTEM';
    ip_address?: string;
    client_type: 'ANDROID_APP' | 'WEB_PWA' | 'ADMIN_PORTAL' | 'CRON_WORKER';
  };
  
  /** موجودیت هدف رویداد */
  entity: {
    entity_type: 'order' | 'basket' | 'vendor' | 'retailer' | 'catalog_item' | 'dispute' | 'payment';
    entity_id: string; // UUID موجودیت
  };
  
  /** داده‌های متنی و تغییرات بار رویداد */
  payload: T;
  
  /** فراداده‌های فنی برای ردیابی توزیع‌شده */
  metadata: {
    correlation_id: string; // جهت ردیابی کل زنجیره درخواست در میکروسرویس‌ها
    cluster_id: string;    // e.g., "ahvaz_bonakdaran"
    environment: 'production' | 'staging' | 'pilot';
  };
}
```

---

### ۳. استاندارد نام‌گذاری رویدادها (Naming Conventions)
نام تمامی رویدادها باید دقیقاً از الگوی **`<object>_<past-tense-action>`** (موجودیت به شکل مفرد + فعل در زمان گذشته انگلیسی) پیروی کند:

| رده رویداد | نام رویداد استاندارد | شرح رویداد | صادرکننده (Producer) | دریافت‌کنندگان (Consumers) |
| :--- | :--- | :--- | :--- | :--- |
| **سبد خرید** | `basket_created` | ایجاد سبد خرید جدید توسط سوپرمارکت | Cart Service | مانیتورینگ قیف فروش (Funnel Analytics) |
| **سبد خرید** | `basket_item_added` | افزودن یا ویرایش کالا در سبد | Cart Service | تحلیل تقاضا و محاسبه تجمیعی سبد |
| **تخصیص** | `allocation_preview_generated` | پیش‌نمایش تخصیص سبد به بنکدار بهینه | Allocation Engine | رابط کاربری خریدار (نمایش پیش‌فاکتور) |
| **تخصیص** | `allocation_plan_created` | ثبت و تایید نهایی برنامه تخصیص سبد | Allocation Engine | Order Creation Service |
| **سفارش** | `order_created` | ایجاد ساختار سفارش از برنامه تخصیص | Order Service | لاگ حسابرسی، سیستم رزرو موجودی |
| **سفارش** | `order_submitted` | ارسال قطعی سفارش به بنکدار جهت بررسی | Order Service | نوتیفیکیشن فوری پیامک بنکدار، شروع تایمر SLA |
| **سفارش** | `order_accepted` | تایید کامل اقلام توسط بنکدار | Vendor Portal | سرویس پیامک خریدار، حواله خروج انبار |
| **سفارش** | `order_partially_accepted` | تایید سفارش با کسری برخی اقلام | Vendor Portal | نوتیفیکیشن تایید کسری به سوپرمارکت |
| **سفارش** | `order_rejected` | رد سفارش توسط بنکدار با ذکر دلیل | Vendor Portal | سیستم جریمه SLA، اطلاع فوری به خریدار |
| **سفارش** | `order_preparing` | شروع بسته‌بندی در انبار بنکدار | Vendor Staff App | به‌روزرسانی پنل پیگیری سفارش خریدار |
| **سفارش** | `order_ready` | بسته‌بندی آماده تحویل به وانت | Vendor Staff App | هماهنگی با باربری شهرک بنکداران |
| **سفارش** | `order_dispatched` | بارگیری و خروج وانت از شهرک | Vendor Portal | پیامک مشخصات راننده به سوپرمارکت |
| **سفارش** | `order_delivered` | تایید تخلیه و دریافت کالا پای مغازه | Retailer App / Driver | آغاز مهلت بررسی مغایرت، صدور پیش‌نویس تسویه |
| **سفارش** | `order_cancelled` | لغو سفارش در مراحل مجاز | Order Service / Worker | آزادسازی موجودی رزروشده، گزارش تحلیلی |
| **دعاوی تجاری** | `dispute_opened` | ثبت ادعای کسری، مغایرت یا آسیب بار | Retailer App | توقف موقت تسویه، کارتابل بازرسی پشتیبانی |
| **دعاوی تجاری** | `dispute_resolved` | داوری اختلاف و تعیین میزان تعدیل مالی | Support Dashboard | ماژول تعدیل تسویه (`settlement_adjustments`) |
| **دعاوی تجاری** | `dispute_closed` | بسته شدن قطعی پرونده اختلاف | Support Dashboard | لاگ حسابرسی و بایگانی سابقه |
| **پرداخت** | `payment_attempted` | ثبت اقدام به پرداخت توسط سوپرمارکت | Payment Service | لاگ تلاش‌های پرداخت و اعتبارسنجی |
| **پرداخت** | `payment_completed` | تایید نهایی پرداخت فاکتور (نقد/پوز/حساب) | Delivery / Vendor | موتور تسویه حساب، تغییر وضعیت تسویه |
| **پرداخت** | `payment_failed` | ثبت عدم موفقیت یا مغایرت پرداخت | Delivery / Vendor | کارتابل پیگیری مالی و اخطار به خریدار |
| **تسویه مالی** | `settlement_created` | صدور صورت‌حساب ناخالص و خالص بنکدار | Settlement Engine | پنل مالی بنکدار، لاگ حسابداری پلتفرم |
| **تسویه مالی** | `settlement_completed` | تایید نهایی تسویه حساب سفارش | Settlement Worker | بایگانی پرونده مالی سفارش |
| **استرداد وجه** | `refund_created` | ثبت طلب خریدار ناشی از مغایرت تاییدشده | Finance Module | بازپرداخت مستقیم فروشنده یا حساب بانکی |
| **کاتالوگ** | `product_created` | ایجاد محصول مستر جدید در کاتالوگ مرجع | Ops / Admin Portal | ایندکس سرچ تری‌گرام، کشینگ کاتالوگ |
| **کاتالوگ** | `product_barcode_scanned` | اسکن بارکد توسط بنکدار یا ویزیتور | Vendor App / Scanner | سرویس تطبیق کاتالوگ (Matching Engine) |
| **کاتالوگ** | `product_match_confirmed` | تایید تطبیق بارکد اسکن‌شده با مستر کالا | Vendor App / Ops Portal | ایجاد نگاشت Vendor SKU به Master SKU |
| **کاتالوگ** | `product_candidate_created` | ثبت کاندیدای کالای ناشناخته (عدم تطبیق) | Vendor App / Field App | صف بررسی و اعتبارسنجی اپراتور ادمین |
| **کاتالوگ** | `product_candidate_approved` | تایید نهایی کاندیدا و ارتقا به Master Product | Ops Admin Portal | اطلاع به بنکدار ثبت‌کننده، انتشار کاتالوگ |
| **انبار و قیمت** | `inventory_item_created` | ثبت اولیه موجودی یک کالا توسط بنکدار | Vendor Portal / Continuous Scan | ایجاد رکورد انبار و قیمت‌گذاری |
| **انبار و قیمت** | `inventory_quantity_updated` | تغییر تعداد موجودی (فروش، فاکتور، اسکن) | Vendor App / Order Service | به‌روزرسانی موجودی قابل‌فروش (`sellable_quantity`) |
| **انبار و قیمت** | `inventory_price_updated` | تغییر قیمت واحد کالا توسط بنکدار | Vendor App / Portal | بی‌اعتبارسازی کش، انطباق سبدهای در جریان |
| **انبار و قیمت** | `inventory_published` | انتشار و فعال‌سازی کالای بنکدار در مارکت‌پلیس | Vendor App / Portal | قابل رویت شدن برای سوپرمارکت‌ها در سرچ |
| **رسانه و تصویر**| `product_media_uploaded` | آپلود و بهینه‌سازی وب‌پی تصویر کالا | Upload Worker / S3 | اتصال تصویر به مستر یا بنکدار، تولید تامبنیل |

---

### ۴. پشته فنی انتقال و الگوی پیام‌رسانی مطمئن (Transactional Outbox Pattern)

#### ۴.۱. الگوی Transactional Outbox (جلوگیری از خطای دوگانه شبکه و دیتابیس):
برای تضمین اینکه هیچ رویدادی در اثر crash یا قطع شبکه از بین نرود:
1. در زمان اجرای هر تراکنش کسب‌وکار، هم‌زمان با رکوردهای تجاری، یک رکورد در جدول `outbox_events` داخل **همان تراکنش ACID پایگاه داده PostgreSQL** درج می‌شود.
2. Python worker کانونیکال رکوردهای `PENDING` را مستقیماً از PostgreSQL با `FOR UPDATE SKIP LOCKED` claim می‌کند، پردازش لازم را انجام می‌دهد و transition نهایی را در PostgreSQL ثبت می‌کند.
3. workerهای provider/payment برای side effectهای طولانی‌مدت از leaseهای PostgreSQL استفاده می‌کنند؛ بنابراین crash worker قابل بازیابی است.
4. در صورت شکست یا crash، PostgreSQL همچنان منبع حقیقت است و work بعدی از همان state قابل claim مجدد خواهد بود.

```\n┌─────────────────────────────────────────────────────────────┐\n│                 PostgreSQL 18 ACID Transaction              │\n│  INSERT INTO orders (...)                                   │\n│  INSERT INTO outbox_events (..., status='PENDING')         │\n└──────────────────────────────┬──────────────────────────────┘\n                               │ commit\n                               ▼\n              [Python Outbox / Integration Worker]\n                               │\n             ┌─────────────────┴─────────────────┐\n             ▼                                   ▼\n [notifications / deliveries]       [reconciliation / ops workers]\n             │                                   │\n             └──────────── PostgreSQL 18 ────────┘\n```

#### ۴.۲. تفکیک رویدادهای حسابرسی از رویدادهای تحلیلی (Audit vs. Analytics Events):
* **رویدادهای حسابرسی (Audit Events):** رویدادهای قطعی مالی و حقوقی نظیر تغییر وضعیت سفارش، پذیرش بار، ثبت مغایرت، تغییر قیمت و تسویه حساب. این رویدادها دارای تضمین ۱۰۰٪ ذخیره دائمی در جدول `domain_events_log` هستند و هرگز منقضی یا حذف نمی‌شوند.
* **رویدادهای تحلیلی (Analytics Events):** رفتارهای پرحجم کاربر می‌توانند بعداً به یک pipeline تحلیلی جداگانه منتقل شوند، اما این pipeline نباید منبع حقیقت رویدادهای دامنه باشد. در MVP، صحت و recovery رویدادهای کسب‌وکار به PostgreSQL وابسته است، نه Redis.

            ▼                           ▼
      (ارسال SMS کاوه‌نگار)       (جدول بازرسی / هوش تجاری)
```

#### ۴.۲. مدیریت خطا و صف بن‌بست (Dead Letter Queue - DLQ):
* اگر پردازش یک side effect مانند ارسال پیامک شکست بخورد:
  1. `ProviderDeliveryWorker` با lease و retry schedule روی همان رکورد `notification_deliveries` دوباره claim می‌کند.
  2. در failure نهایی، رکورد در وضعیت `FAILED` باقی می‌ماند و provider-attempt audit trail حفظ می‌شود.
  3. quarantine/failed state و re-drive از PostgreSQL انجام می‌شود؛ Redis DLQ منبع حقیقت نیست.

---

### ۵. سیاست نسخه‌بندی و سازگاری رو به عقب (Versioning Policy)
* هر رویداد دارای فیلد `event_version` است (مثلاً `"1.0"`).
* تغییرات فیلدها در بار رویداد (Payload) بر اساس قوانین سفت‌وسخت سازگاری رو به عقب (Backward Compatibility) مدیریت می‌شود:
  - **تغییرات جزئی (Minor):** اضافه شدن یک فیلد اختیاری جدید $\to$ نسخه از `"1.0"` به `"1.1"` ارتقا یافته و تمام Consumerهای قبلی بدون تغییر کار می‌کنند.
  - **تغییرات بنیادین (Major):** تغییر نام فیلد یا حذف فیلد اجباری $\to$ انتشار رویداد با نسخه `"2.0"`. در این حالت، Producer تا زمان بازنویسی تمام Consumerها موظف است هر دو نگارش رویداد را به طور موازی ارسال کند.

---

### ۶. ساختار تفصیلی بار رویدادهای کاتالوگ، انبار و رسانه (Domain Event Payload Schemas)

#### ۶.۱. رویداد اسکن بارکد و تطبیق کاتالوگ (`product_barcode_scanned`, `product_match_confirmed`, `product_candidate_created`)

```typescript
// رویداد اسکن بارکد در جریان ثبت سریع انبار
export interface ProductBarcodeScannedPayload {
  raw_barcode: string;           // "6260123456789"
  normalized_barcode: string;    // "6260123456789"
  barcode_type: 'EAN13' | 'EAN8' | 'UPC_A' | 'GTIN14' | 'IRANCODE' | 'INTERNAL_BARCODE';
  vendor_id: string;             // UUID بنکدار اسکن‌کننده
  scan_session_id: string;       // شناسه جلسه Continuous Scan
  matched_status: 'EXACT' | 'HIGH_CONFIDENCE' | 'AMBIGUOUS' | 'NO_MATCH';
  matched_product_id?: string;   // در صورت انطباق دقیق
  candidate_product_ids?: string[]; // در صورت ابهام (چندین تطبیق ممکن)
}

// رویداد ثبت کاندیدای کالای جدید (در حالت عدم تطبیق یا محصول ناشناخته)
export interface ProductCandidateCreatedPayload {
  candidate_id: string;          // UUID رکورد کاندیدا
  vendor_id: string;
  submitted_name_fa: string;     // نام وارد شده توسط بنکدار
  submitted_barcode?: string;
  submitted_brand_name?: string;
  category_id?: string;
  source_type: 'VENDOR_APP_SCAN' | 'VENDOR_PORTAL' | 'FIELD_AGENT';
  image_urls?: string[];
  status: 'PENDING_REVIEW';
}

// رویداد تایید کاندیدا و ارتقا به Master Product
export interface ProductCandidateApprovedPayload {
  candidate_id: string;
  promoted_product_id: string;   // UUID محصول مستر جدید
  master_sku: string;            // شناسه نمایشی مثل POL-PRD-004821
  approved_by_admin_id: string;
  target_canonical_name: string;
}
```

#### ۶.۲. رویدادهای تغییرات انبار و قیمت بنکدار (`inventory_quantity_updated`, `inventory_price_updated`, `inventory_published`)

```typescript
// رویداد به‌روزرسانی موجودی انبار
export interface InventoryQuantityUpdatedPayload {
  vendor_id: string;
  product_id: string;
  vendor_sku: string;
  previous_quantity: number;
  new_quantity: number;
  reserved_quantity: number;
  sellable_quantity: number;     // new_quantity - reserved_quantity
  change_delta: number;          // مثبت یا منفی
  reason: 'VENDOR_MANUAL_ENTRY' | 'CONTINUOUS_SCAN_UPDATE' | 'ORDER_RESERVED' | 'ORDER_DELIVERED' | 'DISPUTE_RETURN';
  reference_id?: string;         // e.g. order_id or scan_session_id
}

// رویداد تغییر قیمت واحد کالا توسط بنکدار
export interface InventoryPriceUpdatedPayload {
  vendor_id: string;
  product_id: string;
  vendor_sku: string;
  previous_price_toman: number;
  new_price_toman: number;
  previous_consumer_price?: number;
  new_consumer_price?: number;   // قیمت مصرف‌کننده درج‌شده روی جلد (تومان)
  tier_pricing?: Array<{ min_quantity: number; unit_price: number }>;
}

// رویداد انتشار و همگام‌سازی کالای بنکدار در مارکت‌پلیس
export interface InventoryPublishedPayload {
  vendor_id: string;
  vendor_product_id: string;
  product_id: string;
  is_active: boolean;
  published_at: string;
}
```

#### ۶.۳. رویداد بارگذاری و پردازش رسانه کالا (`product_media_uploaded`)

```typescript
// رویداد پردازش و آپلود رسانه کالا در MinIO/S3
export interface ProductMediaUploadedPayload {
  media_id: string;              // UUID مدیا در جدول media_assets
  product_id?: string;           // UUID محصول مستر (در صورت اتصال مستقیم)
  vendor_id?: string;            // بنکدار بارگذاری‌کننده (در صورت وجود)
  storage_bucket: string;        // e.g. "pol-media"
  storage_key: string;           // "products/{product_id}/canonical/{uuid}.webp"
  mime_type: string;             // "image/webp"
  file_size_bytes: number;
  width: number;
  height: number;
  is_thumbnail: boolean;         // تامبنیل ۱۵۰x۱۵۰ برای شبکه‌های ضعیف
  provenance: 'VENDOR_UPLOADED' | 'MANUFACTURER_PROVIDED' | 'POL_OWNED';
}
```
