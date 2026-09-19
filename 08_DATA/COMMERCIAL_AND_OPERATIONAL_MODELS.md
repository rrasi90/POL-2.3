# POL — Commercial & Operational Data Models (مدل‌های داده تجاری و عملیاتی پیشرفته)

**Domain:** Data Architecture, Operational Auditability, Commercial Resilience  
**Scope:** Vendor Reliability, Price History, Catalog Identity, Return Operations  
**Implementation State:** DOMAIN_VERIFIED & SCHEMA-ENFORCED (Migrations 001–004)

---

## 1. Declared vs. Observed Data Model: The Vendor Reliability Ledger

یکی از بنیادی‌ترین چالش‌های بازارهای چندبنکداری، تفکیک بین **«ادعای بنکدار» (Declared Data)** و **«واقعیت میدانی مشاهده‌شده» (Observed Truth)** است.

### ساختار ثبتی `vendor_reliability_events`
هر رویداد تجاری که نشان‌دهنده تعهد یا خلف وعده باشد، در دفتری غیرقابل دستکاری (Append-Only Ledger) ثبت می‌شود:

```sql
CREATE TABLE vendor_reliability_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID NOT NULL REFERENCES vendors(id),
    event_type VARCHAR(64) NOT NULL,
    impact_score NUMERIC(5, 2) NOT NULL DEFAULT 0.0,
    reference_entity_type VARCHAR(32), -- ORDER, CONFIRMATION, DISPUTE, DISPATCH
    reference_entity_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### ماتریس رویدادها و ضریب تأثیر (Impact Scores):
| نوع رویداد (`event_type`) | ماهیت | اثر امتیازی | پیامد در سیستم |
|---|---|---|---|
| `DAILY_CONFIRMATION_COMPLETED` | تأیید صبحگاهی موجودی | **+۵.۰** | افزایش ضریب اطمینان در تخصیص سفارش |
| `DAILY_CONFIRMATION_MISSED` | عدم تأیید تا موعد مقرر | **-۱۰.۰** | تنزل وضعیت موجودی به `STALE` |
| `ORDER_FULFILLED_ON_TIME` | ارسال دقیق در بازه SLA | **+۱۰.۰** | ارتقای بنکدار به رتبه «تأمین‌کننده برتر» |
| `ORDER_CANCELLED_BY_VENDOR` | لغو سفارش توسط بنکدار به دلیل کسری | **-۳۰.۰** | جریمه در رتبه‌بندی، بررسی توسط تیم عملیات |
| `DISPUTE_FOUND_VENDOR_FAULT` | اثبات مغایرت یا آسیب بار در حکمیت | **-۲۵.۰** | کسر مستقیم از حساب فروشنده و جریمه امتیازی |
| `INVENTORY_DISCREPANCY_REPORTED`| گزارش مغایرت تعداد بار تحویلی | **-۱۵.۰** | الزام به بازبینی دستی موجودی انبار |

---

## 2. Temporal Price Versioning Model

در نوسانات قیمتی بازار اهواز، هیچ قیمتی نباید روی رکورد قبلی رونویسی (Overwrite) شود. تمام تغییرات قیمت باید دارای برچسب نسخه زمانی (`effective_from`) و نسخه افزایشی (`price_version`) باشند:

```sql
ALTER TABLE vendor_prices 
ADD COLUMN price_version INTEGER NOT NULL DEFAULT 1,
ADD COLUMN effective_from TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- تضمین قطعی تک‌قیمتی بودن در هر لحظه:
CREATE UNIQUE INDEX idx_vendor_prices_single_current 
ON vendor_prices (vendor_product_id) 
WHERE is_current = TRUE;
```

### تضمین‌های معماری:
1. **عدم جعل تاریخچه:** سفارش‌هایی که هفته پیش ثبت شده‌اند، دقیقاً به رکورد قیمتی همان تاریخ با شناسه منحصر‌به‌فرد اشاره دارند (`price_id` در `order_items`).
2. **Revalidation Safety:** در لحظه چک‌اوت، قیمت استعلام‌شده در سبد خرید با آخرین رکورد `is_current = TRUE` بنکدار با قفل مقایسه می‌شود.

---

## 3. Product Identity Lifecycle & Merge Safety Model

در فرآیند افزودن کالاهای بنکداران مختلف، اغلب رکوردهای تکراری برای یک کالای فیزیکی با عناوین کمی متفاوت ساخته می‌شود (مانند «روغن مایع ۸۱۰ لادن» و «روغن آفتابگردان ۸۱۰ گرمی لادن»).

پلتفرم پُل برای حفظ سلامت کاتالوگ و جلوگیری از سردرگمی سوپرمارکت‌داران، فرآیند **ادغام امن (Safe Catalog Merge)** را با جدول `product_identity_lifecycle_logs` تضمین می‌کند:

```sql
CREATE TABLE product_identity_lifecycle_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_type VARCHAR(32) NOT NULL, -- CREATED, MERGED, SPLIT, UNMERGED, DEPRECATED
    master_product_id UUID NOT NULL REFERENCES products(id),
    source_product_id UUID REFERENCES products(id),
    performed_by_user_id UUID NOT NULL REFERENCES users(id),
    reason TEXT,
    snapshot_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### قواعد ادغام:
1. **شناسه بارکد واحد:** کالای مقصد بارکد رسمی و مشخصات استاندارد را حفظ می‌کند.
2. **انتقال خودکار لیستینگ‌ها:** تمام رکوردهای `vendor_products` متصل به کالای مبدأ، به کالای مقصد منتقل می‌شوند بدون اینکه تاریخچه فروش یا نظرات از دست برود.
3. **قابلیت بازگشت (Unmerge Rollback):** شیء `snapshot_data` شامل اطلاعات کامل پیش از ادغام است تا در صورت اشتباه انسانی، امکان لغو ادغام وجود داشته باشد.

---

## 4. Returns & RMA (مدیریت مرجوعی کالا)

فرآیند مرجوعی کالا در تجارت عمده FMCG به دلیل خطای اقلام ارسالی، آسیب دیدگی در مسیر، یا مغایرت تاریخ انقضا اجتناب‌ناپذیر است:

```sql
CREATE TABLE returns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id),
    retailer_id UUID NOT NULL REFERENCES retailers(id),
    vendor_id UUID NOT NULL REFERENCES vendors(id),
    return_status VARCHAR(32) NOT NULL DEFAULT 'REQUESTED',
    reason VARCHAR(64) NOT NULL, -- DAMAGED_GOODS, EXPIRED_GOODS, WRONG_ITEM, SHORTAGE
    evidence_urls JSONB DEFAULT '[]'::jsonb,
    total_refund_toman BIGINT NOT NULL DEFAULT 0,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### چرخه عمر مرجوعی:
`REQUESTED` ➔ `APPROVED` ➔ `COLLECTED` (توسط راننده در سفر بعدی) ➔ `RECEIVED_AT_VENDOR` ➔ `REFUNDED` (بازپرداخت مستقیم فروشنده).
