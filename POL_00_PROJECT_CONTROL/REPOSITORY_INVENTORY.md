# سیاهه‌برداری و طبقه‌بندی جامع مخزن (POL Repository Inventory & Classification)
## پروژه پُل (POL) — B2B FMCG Platform
**شناسه سند:** `GOV-REP-001`  
**نسخه:** ۱.۰ (تثبیت‌شده بر اساس اسکن فیزیکی مخزن)  
**تاریخ ارزیابی:** سپتامبر ۲۰۲۶  
**وضعیت:** سند حاکمیتی قطعی (Canonical Governance Document)  

---

## ۱. آمار کلان فایل‌های مخزن (High-Level File Counts)

بر اساس اسکن فیزیکی دقیق و تکرارپذیر کل دایرکتوری مخزن (`c:\Star\pol\2.2 - antigravity`):

| نوع فایل (Extension) | تعداد کل | توضیحات و کاربری |
| :--- | :--- | :--- |
| **مستندات مارک‌داون (`.md`)** | **۱۶۹** | اسناد استراتژی، معماری، محصول، دیتا، فرضیات و یادداشت‌های پژوهشی |
| **داده و کانفیگ جیسون (`.json`)** | **۱۷** | دیتاست مرجع مستر اس‌کیو (۵۱.۶۸ مگابایت) و فایل‌های میانی هایپرریسرچ |
| **اسکریپت‌های پایتون (`.py`)** | **۱۵** | ابزارهای ممیزی دیتاست مستر، تحلیل متن و شبیه‌سازی |
| **پایگاه داده اس‌کیولایت (`.db`)** | **۱** | دیتابیس کچ و کش تحقیقاتی هایپرریسرچ |
| **لاگ و خطی جیسون (`.jsonl`)** | **۱** | لاگ ساختاریافته تحلیل کلاسترها |
| **فایل پیکربندی تامل (`.toml`)** | **۱** | پیکربندی ابزار پژوهشی هایپرریسرچ |
| **اسکریپت‌های اس‌کیوال (`.sql`)** | **۰** | کدهای DDL در `Data_Schema.md` درج شده و مایگریشن مستقیم در این فاز ایجاد می‌شود |
| **مجموع کل فایل‌های مخزن** | **۲۰۴** | **مجموع دقیق فیزیکی بدون شمارش فایل‌های موقت** |

---

## ۲. توزیع دایرکتوری‌ها (Directory Breakdown)

| نام پوشه | تعداد فایل | سطح عملکردی و نقش در مخزن |
| :--- | :--- | :--- |
| `POL_00_PROJECT_CONTROL` | ۲ | کنترل حاکمیتی، لاگ تضادها، ممیزی آمادگی ساخت |
| `00_PROJECT_OVERVIEW` | ۴ | مرور کلان پروژه، واژه‌نامه جامع (Glossary)، تز استراتژیک، README |
| `01_RESEARCH` | ۷ | رجیستر فرضیات و تصمیمات، پروتکل‌های مصاحبه میدانی، بنچ‌مارک‌ها |
| `01_RESEARCH/INTERVIEW_PROTOCOLS` | ۳ | پرسشنامه‌های اعتبارسنجی بنکدار، خرده‌فروش و ویزیتور |
| `02_STRATEGY` | ۶ | اسناد استراتژی ورود به بازار، اثر شبکه‌ای و حل مسئله |
| `03_CUSTOMERS` | ۶ | تحلیل سگمنت‌های مشتریان بنکدار و سوپرمارکت |
| `04_VALUE_PROPOSITION` | ۴ | بوم ارزش پیشنهادی دوطرفه پلتفرم |
| `05_BUSINESS_MODEL` | ۷ | مدل درآمدی، کارمزد پلکانی ۱٪-۳٪، اقتصاد واحد و طرح جذب سرمایه |
| `06_PRODUCT` | ۹ | الزامات PRD، چرخه حیات سفارش، معماری فنی، مشخصات آزمون BDD |
| `07_ALGORITHMS` | ۵ | فرمولاسیون ریاضی تخصیص سبد $N$ بنکدار، موتور جستجو و رتبه‌بندی ارگانیک |
| `08_DATA` | ۱۲ | اسکیما PostgreSQL 18، معماری رویدادمحور، مدل کاتالوگ و انبارداری، ممیزی مستر اس‌کیو |
| `09_OPERATIONS` | ۵ | لجستیک سنتی شهرک بنکداران، پشتیبانی، حل اختلاف و تسویه |
| `10_GO_TO_MARKET` | ۵ | استراتژی‌های آنبوردینگ سبک، جذب بنکدار و سوپرمارکت |
| `11_PILOT` | ۸ | تعهدنامه پایلوت ۳ ماهه اهواز، شاخص‌های KPI، شروط اعتبارسنجی |
| `12_ROADMAP` | ۵ | نقشه راه فازبندی، استراتژی سال چهارم آگهی و اعتبارات بانکی توکار |
| `Master SKU` | ۱ | فایل مرجع خام ۶۸,۷۰۷ رکوردی `backup_no_images.json` (۵۱.۶۸ MB) |
| `scripts/catalog` | ۱ | اسکریپت مستقل اعتبارسنجی و ممیزی دیتاست مستر اس‌کیو |
| `research/` و زیرپوشه‌ها | ۱۱۰ | یادداشت‌های بنچ‌مارک خارجی، شیمز و فایل‌های خروجی هایپرریسرچ |

---

## ۳. تاکسونومی استاندارد وضعیت اسناد (Status Taxonomy)

برای تفکیک دقیق اسناد معتبر از پیش‌نویس‌ها و سوابق تاریخی:

1. **`CANONICAL / APPROVED`**: سند مرجع رسمی و قطعی یگانه منبع حقیقت (Single Source of Truth).
2. **`IMPLEMENTABLE`**: سند مشخصات فنی و مهندسی دارای قراردادهای قطعی آماده کدنویسی.
3. **`VALIDATED`**: فرضیاتی که با داده‌های میدانی و شواهد قطعی اثبات شده‌اند.
4. **`WORKING / DRAFT`**: اسناد در حال تکمیل یا ویرایش فعال.
5. **`UNDER_REVIEW`**: اسناد ارسال‌شده برای ارزیابی کیفی و اعتبارسنجی.
6. **`SUPPORTING`**: اسناد کمکی، پیوست‌ها و تحلیل‌های تکمیلی که سند کاننیکال را تقویت می‌کنند.
7. **`HISTORICAL / SUPERSEDED`**: اسناد قدیمی، ایده‌های پیشین یا تصمیماتی که لغو و با تصمیمات جدید جایگزین شده‌اند (جهت حفظ تاریخچه و رد تصمیمات قبلی نگهداری می‌شوند).
8. **`ARCHIVED`**: فایل‌های بایگانی‌شده خارج از چرخه عملیاتی.

---

## ۴. ماتریس اسناد کاننیکال بر اساس حوزه‌ها (Canonical Sources of Truth)

| حوزه دامنه (Domain) | سند کاننیکال یگانه (Canonical Document) | وضعیت | اسناد پیرامونی و تاریخی مرتبط |
| :--- | :--- | :--- | :--- |
| **حاکمیت مخزن و تضادها** | `POL_00_PROJECT_CONTROL/CONTRADICTION_LOG.md` | `CANONICAL` | `REPOSITORY_AUDIT_AND_BUILD_READINESS.md` |
| **تصمیمات استراتژیک** | `01_RESEARCH/Assumptions_and_Hypotheses.md` | `CANONICAL` | `02_STRATEGY/Strategic_Thesis.md` |
| **شواهد و مستندات میدانی** | `01_RESEARCH/Evidence_Register.md` | `CANONICAL` | `Field_Research.md`, `External_Benchmarks_POL_v0.2_FA.md` |
| **الزامات کلان محصول** | `06_PRODUCT/PRD.md` | `CANONICAL` | `MVP_Definition.md`, `Product_Vision.md` |
| **چرخه حیات سفارش** | `06_PRODUCT/Order_Lifecycle.md` | `CANONICAL` | `Exception_Handling.md`, `Test_Specification.md` |
| **معماری فنی و پشته سیستم** | `06_PRODUCT/Technical_Architecture_Spec.md` | `CANONICAL` | `06_PRODUCT/API_Contracts.md` |
| **مدل داده و اسکیما دیتابیس** | `08_DATA/Data_Schema.md` | `CANONICAL` | `migrations/001_initial_schema.sql` |
| **مدل کاتالوگ و مستر کالا** | `08_DATA/CATALOG_PRODUCT_MASTER.md` | `CANONICAL` | `PRODUCT_IDENTIFIER_MODEL.md`, `CATALOG_MATCHING.md` |
| **مدل انبارداری و قیمت** | `08_DATA/INVENTORY_MODEL.md` | `CANONICAL` | `Master_SKU_Import_Audit.md` |
| **معماری رسانه و ذخیره‌سازی** | `08_DATA/PRODUCT_MEDIA_MODEL.md` | `CANONICAL` | `PRODUCT_MEDIA_MODEL.md` |
| **سیستم رویدادمحور** | `08_DATA/Event_Architecture.md` | `CANONICAL` | `Market_Intelligence.md` |
| **تخصیص بهینه سبد خرید** | `07_ALGORITHMS/Future_Cart_Allocation_Research.md` | `CANONICAL` | `Cart_Allocation.md` (Supporting) |
| **مدل مالی و کارمزد** | `05_BUSINESS_MODEL/Commission_Model.md` | `CANONICAL` | `Business_Model.md`, `Unit_Economics.md` |
| **عملیات مالی و تسویه** | `09_OPERATIONS/Payments_and_Settlement.md` | `CANONICAL` | `Wallet.md`, `Support_and_Disputes.md` |
| **طراحی پایلوت اهواز** | `11_PILOT/POL_Pilot_Commitment_and_Validation_Form.md` | `CANONICAL` | `Pilot_Strategy.md`, `Pilot_Design.md` |
| **شاخص‌های کلیدی (KPIs)** | `11_PILOT/KPIs.md` | `CANONICAL` | `Success_Criteria.md` |

---

## ۵. تحلیل فایل‌های نیازمند تکمیل یا بازنگری (Placeholder & Gap Analysis)

1. **`01_RESEARCH/Evidence_Register.md` (اندازه قبلی: ۹۷ بایت):**  
   یک سند تک‌خطی ناقص بود که در جریان این بازسازی به یک رجیستر کامل و سیستماتیک شواهد بنچ‌مارک و مصاحبه میدانی تبدیل می‌شود.
2. **`09_OPERATIONS/Payments_and_Settlement.md` (اندازه قبلی: ۱,۷۹۷ بایت):**  
   نیازمند بسط فنی و تطبیق کامل با مدل‌های پایگاه داده (`payments`, `settlements`, `refunds`) و جداسازی کامل جریان نقدی سنتی بازار از رصد پلتفرم پُل است.
3. **فایل تکراری مخدوش `POL  Project Overview.md`:**  
   به دلیل هم‌پوشانی بایت‌به‌بایت با `00_PROJECT_OVERVIEW/README.md` و نام‌گذاری نامعتبر حذف شد.
4. **نبود فایل مایگریشن فیزیکی SQL:**  
   کلیه ساختارهای DDL در `Data_Schema.md` وجود دارند اما فایل فیزیکی `migrations/001_initial_schema.sql` جهت اجرای عملیاتی ایجاد خواهد شد.
