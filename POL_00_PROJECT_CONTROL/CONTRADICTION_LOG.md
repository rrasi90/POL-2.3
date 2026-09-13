# دفتر ثبت تضادها و مغایرت‌های مفهومی (Contradiction Log)
## پروژه پُل (POL) — B2B FMCG Platform
**شناسه سند:** `GOV-LOG-001`  
**نسخه:** ۲.۰ (تطبیق کامل با استاندارد بخش ۷۲ مستر پرامپت)  
**وضعیت:** مصوب معمار ارشد و ممیز سیستم  
**تاریخ به‌روزرسانی:** سپتامبر ۲۰۲۶  

> [!WARNING]
> **HISTORICAL / SUPERSEDED**
> 
> This document reflects an earlier POL architecture.
> The current MVP Multi-Vendor architecture supersedes the previous Single-Vendor MVP decision.
> **Current source of truth:** `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`  
> **Current decision:** `D-014`

---

### ۱. مقدمه و فلسفه سند
این سند بر اساس بخش ۷۲ مستر پرامپت تدوین شده و تمامی تضادها، مغایرت‌ها، نسخه‌های موازی یا تصمیمات قدیمی کشف‌شده در مخزن پروژه پُل را با ذکر اسناد متأثر، وضعیت قبلی، وضعیت جدید مصوب و تاریخ حل‌وفصل ثبت می‌نماید تا شفافیت تاریخی مخزن ۱۰۰٪ تضمین شود.

---

### ۲. جدول ماتریس جامع تضادها (Canonical Contradiction Matrix)

| ID | Contradiction | Documents | Old State | New State | Decision | Resolution | Date | Status |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: | :---: |
| **C-001** | **Launch Geography** | `Strategic_Thesis.md`, `Opportunity_Definition.md`, `Cluster_Selection.md` | تهران و مناطق ۲ و ۴ یا وضعیت باز ذکر شده بود. | **اهواز (شهرک بنکداران ۶۱ هکتاری با ۷۰۰ بنکدار فعال)** به عنوان تنها هاب لانچ و پایلوت سال اول تثبیت شد. | `D-001` | تمامی مراجع تهران به عنوان «فاز توسعه سال دوم به بعد» اصلاح یا منسوخ شدند. | 2026-09 | **RESOLVED** |
| **C-002** | **Pilot Duration** | `POL_Pilot_Commitment_and_Validation_Form.md`, `Pilot_Strategy.md` | در فرم LOI و برخی یادداشت‌ها بازه «۶ الی ۸ هفته» درج شده بود. | مدت پایلوت **دقیقاً ۳ ماه (۹۰ روز تقویمی / ۱۲ هفته)** تثبیت شد. | `D-002` | دوره ۳ ماهه برای ثبت ۳ تا ۴ چرخه خرید مجدد و اندازه‌گیری Churn واقعی در فرم و اسناد یکدست شد. | 2026-09 | **RESOLVED** |
| **C-003** | **MVP Basket Allocation** | `PRD.md`, `Cart_Allocation.md`, `Data_Schema.md` | تفکیک سبد میان چند بنکدار از روز اول MVP به عنوان قابلیت فعال مطرح بود. | **در MVP نسخه ۱.۰: تخصیص کاملاً تک‌بنکدار (Single-Vendor MVP)** است. | `D-003` | حذف اصطکاک تحویل چندگانه در MVP؛ تفکیک سبد به فاز تحقیق و توسعه بعد از اثبات پایلوت موکول شد. | 2026-09 | **RESOLVED** |
| **C-004** | **Max Vendor Limit** | `Cart_Allocation.md`, `Technical_Architecture.md` | سقف هاردکد شده «حداکثر ۲ بنکدار» درج شده بود. | سقف بنکدار **هاردکد نیست (OPEN / NOT HARD-CODED)**. | `D-004`<br>`D-005` | سند `Future_Cart_Allocation_Research.md` برای فرمولاسیون ریاضی $N$ بنکدار تدوین شد. | 2026-09 | **RESOLVED** |
| **C-005** | **Pilot Commission** | `Business_Model.md`, `Revenue_Model.md`, `Vendor_LOI.md` | اعمال کارمزد ۲٪ ثابت از روز اول پایلوت فرض شده بود. | **کارمزد پایلوت ۳ ماهه دقیقاً ۰٪ (کاملاً رایگان)** است؛ کارمزد پساپایلوت ۱٪ تا ۳٪ پلکانی است. | `D-006`<br>`D-007` | مدل درآمدی، اکسل مالی و تفاهم‌نامه بنکدار اصلاح شدند تا اصطکاک ورود به صفر برسد. | 2026-09 | **RESOLVED** |
| **C-006** | **Logistics & Fleet Cost** | `Business_Model.md`, `Fulfillment.md`, `Opportunity_Definition.md` | عبارت مبهم «هزینه لجستیک صفر است» این شائبه را ایجاد می‌کرد که حمل بار رایگان است. | **هزینه ناوگان ملکی پُل صفر است (POL-owned Logistics = $0)**؛ هزینه وانت بومی با بازار است. | `D-008` | ادبیات اسناد اصلاح شد: پُل انبار و وانت ندارد؛ هزینه حمل بازار توسط سوپرمارکت یا بنکدار تسویه می‌شود. | 2026-09 | **RESOLVED** |
| **C-007** | **Advertising Roadmap** | `Revenue_Model.md`, `Advertising.md`, `Reputation_System.md` | تبلیغات و بنرهای تجاری به عنوان درآمد زودهنگام MVP مطرح شده بود. | تبلیغات تجاری اکیداً به **نیمه دوم سال چهارم (H2 Year 4)** موکول شد. | `D-009` | تفکیک کامل نمره اعتبار ارگانیک از تبلیغات؛ سند مستقل نقشه راه تبلیغات ایجاد شد. | 2026-09 | **RESOLVED** |
| **C-008** | **Basket Data Coupling** | `Data_Schema.md`, `PRD.md` | اتصال مستقیم جدول Cart به `vendor_id` مانع توسعه به چندبنکداری می‌شد. | سلسله‌مراتب `Basket -> AllocationPlan -> OrderGroup -> Order -> OrderItem`. | `D-010` | بازطراحی ساختار DDL و دیاگرام روابط پایگاه داده به صورت ماژولار و توسعه‌پذیر. | 2026-09 | **RESOLVED** |
| **C-009** | **Currency Standards** | `PRD.md`, `Glossary.md`, `Business_Model_and_Unit_Economics.md` | تداخل و عدم شفافیت در استفاده از مبالغ ریال، تومان و دلار. | رابط کاربری و پیامک‌ها **۱۰۰٪ تومان**؛ اسناد تحلیلی مالی و سرمایه‌گذار به **دلار ($ USD)**. | `D-011` | اصلاح تمامی مشخصات UI، جداول DDL و راهنماهای کاربری. | 2026-09 | **RESOLVED** |

---

### ۳. سیاست ممیزی تداوم و چرخه حیات تضادها (Audit Policy)
هیچ تضادی از تاریخچه این جدول پاک نخواهد شد. در صورت بروز هرگونه مغایرت جدید در طول توسعه نرم‌افزار یا اجرای پایلوت میدانی، تضاد با شناسه `C-010` به بعد در این جدول ثبت و پیش از کدنویسی حل‌وفصل خواهد شد.
