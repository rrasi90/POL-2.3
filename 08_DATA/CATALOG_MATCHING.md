# موتور تطبیق کاتالوگ و مدیریت کاندیداهای کالا (Catalog Matching & Candidate Resolution)
## پروژه پُل (POL) — B2B FMCG Platform
**شناسه سند:** `DATA-SPEC-009`  
**وضعیت:** مصوب و نهایی (Canonical Matching Specification)  
**نسخه:** ۱.۰  
**مرجع تصمیم‌گیری:** بخش‌های ۳۰ تا ۳۲ و ۶۳ تا ۶۷ مستر پرامپت  
**تاریخ به‌روزرسانی:** سپتامبر ۲۰۲۶  

---

### ۱. مسئله و هدف موتور تطبیق (Matching Engine Motivation)
هنگامی که بنکدار در شهرک اهواز می‌خواهد کالای خود را وارد سیستم کند، سیستم باید در کسری از ثانیه تشخیص دهد که آیا این کالا قبلاً در مستر کاتالوگ پُل وجود دارد یا خیر.  
**چالش حیاتی:**  
کالاهایی با نام‌های بسیار نزدیک اما با وزن، رایحه یا کاربری متفاوت (مانند *مام رول نیوآ مردانه ۵۰ میل درای ایمپکت* در برابر *مام رول نیوآ مردانه ۵۰ میل فرش اکتیو*) نباید با جستجوی فازی کورکورانه یکی در نظر گرفته شوند (Never Auto-Merge Ambiguous Products).

---

### ۲. سطوح سه‌گانه انطباق و ضریب اطمینان (Match Confidence Tiers)

```mermaid
graph TD
    Input[ورودی بنکدار: بارکد / نام / برند] --> CheckBarcode{آیا بارکد دارد؟}
    
    CheckBarcode -- بله --> BarcodeLookup[جستجوی دقیق بارکد در شناسه‌ها]
    BarcodeLookup --> FoundExact{تطابق ۱۰۰٪ یافت شد؟}
    FoundExact -- بله --> Level1[سطح ۱: EXACT MATCH<br/>ضریب اطمینان ۱۰۰٪<br/>تایید خودکار و اتصال آنی]
    FoundExact -- خیر --> TextSearch[جستجوی متنی نرمال‌شده + فازی]
    
    CheckBarcode -- خیر --> TextSearch
    
    TextSearch --> CandidateScore{ارزیابی امتیاز انطباق [HYPOTHESIS-MATCH-01]}
    CandidateScore -- امتیاز >= ۸۵٪ و یک کاندیدا --> Level2[سطح ۲: HIGH CONFIDENCE<br/>پیشنهاد کاندیدای برتر به بنکدار<br/>نیاز به ۱ کلیک تایید کاربر]
    CandidateScore -- امتیاز بین ۵۰٪ تا ۸۴٪ یا چند کاندیدا --> Level3[سطح ۳: AMBIGUOUS<br/>نمایش لیست ۳ تا ۵ کاندیدای مشابه<br/>انتخاب دستی توسط بنکدار]
    CandidateScore -- امتیاز زیر ۵۰٪ --> Level4[سطح ۴: NO MATCH<br/>کالا یافت نشد<br/>هدایت به ثبت کاندیدای جدید در وضعیت تعلیق]
```

#### ماتریس سطوح انطباق (Initial Matching Threshold Hypothesis):

> [!NOTE]
> مقادیر آستانه زیر فرضیات اولیه الگوریتم تطبیق (`[HYPOTHESIS-MATCH-01]`) هستند و در فاز پایلوت اهواز بر اساس دقت و بازخوانی واقعی کالیبره خواهند شد.

| سطح انطباق | معیار سیستمی | ضریب اطمینان (Hypothesis) | رفتار پلتفرم در رابط کاربری |
| :--- | :--- | :---: | :--- |
| **`EXACT`** | تطابق کامل مقدار بارکد در جدول `product_identifiers` | ۱.۰۰ (۱۰۰٪) | نمایش مشخصات کالا؛ بنکدار قیمت و موجودی فروش خود را تعیین می‌کند. |
| **`HIGH_CONFIDENCE`** | تطابق دقیق برند + مدل + حجم (یا امتیاز سرچ $\ge ۰.۸۵$) | ۰.۸۵ تا ۰.۹۹ | نمایش کارت محصول با دکمه درشت «بله، همین محصول است» (نیاز به ۱ کلیک تایید کاربر). |
| **`AMBIGUOUS`** | وجود چند کالای مشابه با رایحه یا وزن‌های متفاوت | ۰.۵۰ تا ۰.۸۴ | **ممنوعیت اتصال خودکار**؛ نمایش کارت‌های مقایسه‌ای تا کاربر انتخاب کند. |
| **`NO_MATCH`** | عدم یافتن هیچ کالای مشابه در پایگاه داده | کمتر از ۰.۵۰ | ثبت در قرنطینه کاندیدا (`Product Candidate`) جهت بررسی انسانی تیم کاتالوگ. |

#### شاخص‌های ارزیابی عملکرد سیستم تطبیق کاتالوگ (Matching KPIs):
1. **`precision` (دقت تطبیق):** درصد تطابق‌های خودکار که توسط بنکدار یا بررسی انسانی بدون مغایرت تایید می‌شوند (هدف: $\ge ۹۸٪$).
2. **`recall` (پوشش تطبیق):** درصد کالاهای موجود در کاتالوگ مرجع که توسط موتور جستجو با موفقیت بازیابی می‌شوند (هدف: $\ge ۹۵٪$).
3. **`auto_match_rate` (نرخ انطباق خودکار):** نسبت کالاهایی که با بارکد یا ضریب بالای ۸۵٪ بدون مداخله دستی متصل می‌شوند (هدف اولیه: $\ge ۶۰٪$).
4. **`human_review_rate` (نرخ ارجاع به بازبینی انسانی):** نسبت ثبت‌ها که به بررسی تیم کاتالوگ محول می‌شود (هدف: $\le ۱۵٪$).
5. **`false_positive_rate` (نرخ خطای انطباق نادرست):** نسبت کالاهای متصل‌شده به Master SKU اشتباه (سقف بحرانی: $\le ۱٪$).
6. **`latency_p95` (تاخیر موتور تطبیق):** حداکثر زمان پردازش و پیشنهاد کالا در ۹۵٪ درخواست‌ها (هدف: $\le ۵۰۰\text{ ms}$).
7. **`catalog_lead_time` (مدت‌زمان تایید کاندیدا):** زمان تعیین تکلیف کاندیدای معلق تا تبدیل به کالا یا الصاق به کالای موجود (هدف: $\le ۴\text{ ساعت کاری}$).

---

### ۳. مدیریت کاندیداهای کالا و نظارت انسانی (Product Candidates & Human-in-the-Loop)

#### اصل تغییرناپذیر ایمنی کاتالوگ (Catalog Safety Invariant):
> **قانون قطعی:** اگر کالای بنکدار در کاتالوگ مرجع یافت نشود (`NO_MATCH`)، کالا به هیچ عنوان **بلافاصله قابل فروش در مارکت‌پلیس عمومی نیست**.  
> در این حالت یک رکورد `product_candidates` با وضعیت `PENDING_REVIEW` و یک رکورد `vendor_products` با وضعیت `listing_status = 'DRAFT_PENDING_CATALOG'` ثبت می‌شود.  
> این کالا تا زمان تایید یا ادغام توسط تیم کاتالوگ پُل، برای خریداران سوپرمارکت **غیرفعال و غیرقابل خرید** است تا از ورود اقلام اشتباه، قیمت‌های نامعتبر و شلوغی کاتالوگ جلوگیری شود.  
> تصویر آپلودشده بنکدار صرفاً **سند بررسی داخلی (Internal Matching Evidence)** است و رسانه عمومی کاتالوگ محسوب نمی‌شود.

```sql
CREATE TABLE product_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID NOT NULL REFERENCES vendors(id),
    proposed_title VARCHAR(255) NOT NULL,
    proposed_brand VARCHAR(100),
    barcode VARCHAR(100),
    vendor_sku VARCHAR(100),
    photo_asset_id UUID REFERENCES media_assets(id),
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING_REVIEW', -- 'PENDING_REVIEW', 'APPROVED_CANONICAL', 'MERGED_EXISTING', 'REJECTED'
    resolved_product_id UUID REFERENCES products(id),
    reviewed_by_user_id UUID REFERENCES users(id),
    review_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ
);
```

#### فرآیند تایید تیم کاتالوگ (Catalog Ops Workflow):
1. **بررسی روزانه:** کارشناس کاتالوگ پُل لیست کاندیداهای وضعیت `PENDING_REVIEW` را بازبینی می‌کند.
2. **ادغام در کالای موجود (`MERGED_EXISTING`):** اگر کالا قبلاً با نگارش دیگری در کاتالوگ مرجع وجود داشته، کاندیدا به کالای اصلی الصاق شده، `vendor_products.product_id` به‌روزرسانی شده و وضعیت به `ACTIVE` تبدیل می‌شود.
3. **ارتقا به کانونیکال (`APPROVED_CANONICAL`):** اگر کالای جدید واقعی بازار است، مشخصات رسمی تکمیل شده، رکورد جدید در `products` درج می‌گردد، وضعیت به `APPROVED_CANONICAL` تغییر یافته و وضعیت نمایش بنکدار `ACTIVE` می‌شود.
4. **رد کاندیدا (`REJECTED`):** در صورت نقض قوانین یا اطلاعات ناقص/نامعتبر، رکورد رد شده و وضعیت فروشنده به `REJECTED` تغییر می‌کند.

---

### ۴. تاریخچه و قوانین ادغام محصولات (`product_merge_history`)

هنگامی که دو محصول در کاتالوگ ادغام می‌شوند:
* رکورد منبع به وضعیت `MERGED` تغییر وضعیت می‌دهد.
* ارجاع کاتالوگ‌های فروش به محصول کانونیکال مقصد منتقل می‌شود.
* جدول تاریخچه ادغام ذخیره می‌گردد:

```sql
CREATE TABLE product_merge_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_product_id UUID NOT NULL REFERENCES products(id),
    target_product_id UUID NOT NULL REFERENCES products(id),
    merge_reason VARCHAR(255) NOT NULL,
    operator_user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```
