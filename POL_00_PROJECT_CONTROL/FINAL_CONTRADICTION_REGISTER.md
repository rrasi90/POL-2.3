# رجیستر نهایی رفع تناقضات و ممیزی سیستم (POL Final Contradiction Register)
## Comprehensive Audit of Historical, Architectural & Code-Level Discrepancies
**شناسه سند:** `GOV-CONT-001`  
**وضعیت:** مصوب و نهایی  
**دسته‌بندی شدت:** P0 (تناقض اجرایی/کد) | P1 (تناقض دامنه‌ای/مستنداتی موثر) | P2 (بهبود انشایی/تاریخی)  
**تاریخ انتشار:** سپتامبر ۲۰۲۶  

---

## ۱. جدول جامع ممیزی و رفع تناقضات سیستمی (Resolved Contradictions)

| شناسه | شدت | عنوان تناقض شناسایی‌شده | موقعیت و فایل‌های درگیر | شرح حالت متناقض قبلی | اقدام اصلاحی و وضعیت کانونیکال نهایی | وضعیت |
|:---:|:---:|---|---|---|---|:---:|
| **CR-01** | **P0** | **فیلدهای کارتن‌محور در اقلام سفارش (`order_items`)** | `migrations/001_initial_schema.sql` L428-430 | جدول `order_items` حاوی `quantity_cartons_requested` و `price_per_carton_toman` بود و مانع سفارش‌دهی بر پایه واحدهای دیگر (بسته، عدد) می‌شد. | حذف کامل ستون‌های کارتن‌محور و جایگزینی با `ordered_quantity`, `accepted_quantity`, `delivered_quantity`, `unit_price_toman`, `packaging_unit_snapshot`. | **RESOLVED** |
| **CR-02** | **P0** | **پیلودهای قدیمی کارتن‌محور در قراردادهای API** | `06_PRODUCT/API_Contracts.md` L24, L129, L141 | قراردادهای API در خطاها و بدنه اسکن انبار از `available_cartons`, `requested_cartons`, `price_per_carton_toman` استفاده می‌کردند. | اصلاح به فیلدهای جنریک دامنه‌ای: `quantity`, `unit`, `unit_price_toman`, `packaging_unit`, `physical_quantity`. | **RESOLVED** |
| **CR-03** | **P0** | **مغایرت ساختار ستون‌های `deliveries` و `domain_events_log`** | `Data_Schema.md` در برابر `001_initial_schema.sql` | در `deliveries` و `domain_events_log` اسامی و قیود ستون‌ها بین مستندات و کدهای DDL دچار انحراف بودند. | همگام‌سازی صددرصدی کدهای DDL و مستندات اسکیما؛ انطباق کامل با مشخصات معماری رویدادها. | **RESOLVED** |
| **CR-04** | **P0** | **ادعای تغییر وضعیت سفارش به `DISPUTED` در سند پشتیبانی** | `09_OPERATIONS/Support_and_Disputes.md` L42, L48 | سند عملیات ادعا می‌کرد سیستم وضعیت سفارش را به `DISPUTED` تغییر داده و سپس به `CONFIRMED` بازمی‌گرداند. | بازنویسی کامل بندهای رسیدگی به دعاوی بر پایه اصل استقلال ماشین وضعیت دعاوی (`D-011`)؛ وضعیت سفارش همواره `DELIVERED` می‌ماند. | **RESOLVED** |
| **CR-05** | **P1** | **قید انحصاری تک‌کالایی در سبد خرید (`basket_items`)** | `migrations/001_initial_schema.sql` L339 | قید `UNIQUE(basket_id, product_id)` مانع از آن می‌شد که خریدار یک کالا را در دو بسته‌بندی متفاوت به سبد بیفزاید. | ارتقای قید به `UNIQUE(basket_id, product_id, requested_unit, pack_quantity)` همراه با فیلد `pack_quantity`. | **RESOLVED** |
| **CR-06** | **P1** | **اشاره به Native Android App در دیاگرام PRD** | `06_PRODUCT/PRD.md` L36, L45 | استفاده از عنوان Native Android App در برابر وب واکنش‌گرا باعث ابهام در استک مصوب موبایل شده بود. | تصحیح صریح عنوان به `Android Mobile App (React Native / Expo APK)` مطابق با تصمیم مصوب `D-010`. | **RESOLVED** |
| **CR-07** | **P1** | **ابهام در نقش ادمین عملیات در پرونده‌های دعاوی** | `06_PRODUCT/Roles_and_Permissions.md` L20 | استفاده از برچسب `(DISPUTED)` در شرح وظایف به عنوان وضعیت سفارش. | اصلاح به «داوری و رسیدگی به دعاوی تجاری (ماژول `disputes`)» مطابق با مدل دامنه‌ای. | **RESOLVED** |
| **CR-08** | **P0** | **مغایرت تاریخی جغرافیای پرتاب (تهران در برابر اهواز)** | `Strategic_Thesis_POL_v0.1_FA.md`, اسناد قدیمی | پیشنهادهای اولیه ورود همزمان به تهران در تعارض با استراتژی تمرکز کلاستری بودند. | قفل قطعی لانچ و پایلوت سال اول منحصراً در **اهواز** (`D-001`)؛ رد صریح تهران در اسناد مرجع. | **RESOLVED** |
| **CR-09** | **P0** | **مغایرت دوره پایلوت (۶ الی ۸ هفته در برابر ۳ ماه)** | فرم تعهدنامه LOI قدیمی | ذکر مدت ۶ الی ۸ هفته برای پایلوت. | تصحیح سراسری به **۳ ماه (۱۲ هفته / ۹۰ روز)** مطابق با تصمیم قفل‌شده `D-002`. | **RESOLVED** |
| **CR-10** | **P0** | **سقف هاردکدشده بنکدار (حداکثر ۲ بنکدار)** | اسناد پیشین الگوریتم | وجود عبارت «حداکثر ۲ بنکدار» در منطق تخصیص. | حذف هرگونه سقف هاردکد؛ تعیین تک‌بنکداری برای MVP و معماری کاملاً باز برای N بنکدار (`D-003`). | **RESOLVED** |
| **CR-11** | **P0** | **دوگانگی منبع حقیقت کد کالای بنکدار (`vendor_sku`)** | `product_identifiers` در برابر `vendor_products` | تعریف `VENDOR_SKU` در جدول بارکدها و همزمان در جدول کالای بنکدار. | حذف کامل `VENDOR_SKU` از بارکدها؛ تثبیت منحصربه‌فرد `vendor_products.vendor_sku` با قید یکتایی محلی. | **RESOLVED** |
| **CR-12** | **P0** | **فقدان کلیدهای خارجی صریح در اصلاحات تسویه و استرداد** | `migrations/001_initial_schema.sql` L570, L590 | جداول `settlement_adjustments` و `refunds` فاقد کلید خارجی صریح به `disputes(id)` بودند. | بازتنظیم ترتیب DDL و افزودن کلیدهای صریح `FOREIGN KEY (dispute_id) REFERENCES disputes(id)`. | **RESOLVED** |

---

## ۲. وضعیت نهایی تناقضات مخزن

* **تعداد تناقضات حل‌شده P0:** ۸ مورد
* **تعداد تناقضات حل‌شده P1:** ۴ مورد
* **تعداد تناقضات حل‌شده P2:** ۰ مورد
* **تعداد تناقضات باز (Remaining Open Contradictions):** **۰ (صفر مطلق)**
