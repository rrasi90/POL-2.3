# POL — Project Overview

> **POL (پُل)**  
> Digital Infrastructure for FMCG Distribution

---

# 1. Purpose of This Repository

این Repository، **مرجع مرکزی دانش و تصمیم‌های پروژه پُل** است.

هدف آن این است که تمام اطلاعات مهم پروژه در یک ساختار مشخص نگهداری شود؛ از جمله:

- تحقیقات میدانی (Field Research)
- مصاحبه‌ها
- شواهد و داده‌ها
- تحقیقات خارجی و Benchmarkها
- فرضیه‌ها
- تصمیم‌های استراتژیک
- طراحی محصول
- منطق الگوریتم‌ها
- مدل کسب‌وکار
- عملیات
- Pilot
- Roadmap

این Repository نباید صرفاً مجموعه‌ای از فایل‌های خلاصه باشد.

هر سند باید تا حد امکان:

- مستقل
- قابل استناد
- قابل توسعه
- قابل اصلاح
- قابل استفاده برای تیم آینده

باشد.

---

# 2. What Is POL?

**POL (پُل)** یک پلتفرم و زیرساخت دیجیتال برای کمک به دیجیتال‌سازی و بهینه‌سازی فرآیند سنتی توزیع محصولات **FMCG** است.

مسئله اصلی که پُل از آن شروع می‌کند، وجود فاصله اطلاعاتی و عملیاتی میان بازیگران بازار است.

در ساختار سنتی، بازیگران مختلف بازار اغلب:

- یکدیگر را به‌طور کامل پیدا نمی‌کنند
- اطلاعات مناسبی از قیمت‌ها ندارند
- اطلاعات مناسبی از موجودی ندارند
- کیفیت همکاری طرف مقابل را پیش از تجربه مستقیم نمی‌دانند
- داده کافی درباره رفتار واقعی بازار ندارند

پُل تلاش می‌کند یک **Digital Layer** میان بازیگران بازار ایجاد کند که بتواند:

- افراد را پیدا و به یکدیگر متصل کند
- اطلاعات مناسب را در اختیار آنها قرار دهد
- سفارش و تراکنش را دیجیتال کند
- اعتماد را قابل اندازه‌گیری‌تر کند
- داده‌های عملیاتی و رفتاری بازار را جمع‌آوری کند

---

# 3. The Core Problem

پُل از مشاهده یک مسئله در سیستم سنتی FMCG Distribution شکل گرفته است:

> بازیگران بازار وجود دارند، اما اطلاعات و ارتباطات میان آنها به‌صورت ناکارآمد جریان دارد.

## Retailer

یک Retailer ممکن است:

- Vendor مناسب را نشناسد
- از موجودی واقعی Vendorها اطلاع نداشته باشد
- قیمت‌های مختلف بازار را به‌راحتی مقایسه نکند
- برای پیدا کردن تأمین‌کننده جدید مجبور به پرس‌وجو باشد
- برای ایجاد اعتماد، چندین خرید کوچک انجام دهد

در بسیاری از موارد، Retailer برای خرید یک کالا به Vendor فعلی خود وابسته می‌ماند؛ حتی اگر:

- محصول موردنظر را نداشته باشد
- قیمت بهتری در بازار وجود داشته باشد
- Vendor مناسب‌تری وجود داشته باشد

زیرا Discovery در بازار به‌صورت کارآمد انجام نمی‌شود.

---

## Vendor

Vendor نیز با مشکلات متفاوتی روبه‌رو است.

در سیستم سنتی، Vendor معمولاً برای پیدا کردن و پوشش مشتریان از:

- Visitor
- تماس
- شبکه ارتباطی
- فرآیندهای دستی

استفاده می‌کند.

این مدل می‌تواند باعث ایجاد هزینه‌هایی مانند:

- هزینه نیروی فروش
- هزینه حقوق ثابت
- هزینه مدیریت نیرو
- هزینه پوشش بازار
- هزینه سفارش‌گیری
- هزینه اطلاعات ناقص

شود.

همچنین اطلاعات Vendor ممکن است همیشه به‌روز به مشتری نرسد.

برای مثال:

یک Visitor ممکن است محصولی را به Retailer پیشنهاد دهد، اما:

- موجودی کالا تمام شده باشد
- قیمت تغییر کرده باشد
- شرایط فروش تغییر کرده باشد

در نتیجه، اطلاعات بازار با تأخیر حرکت می‌کند.

---

## Manufacturer

Manufacturer نیز با یک مسئله مهم‌تر روبه‌رو است:

> ممکن است نداند محصولش دقیقاً در بازار چه عملکردی دارد و چرا.

برای مثال، اگر یک محصول فروش نرود، علت واقعی می‌تواند موارد مختلفی باشد:

- قیمت
- عدم دسترسی
- مشکل Distribution
- نبود موجودی
- عملکرد Vendor
- رقابت
- موقعیت محصول
- رفتار Retailer
- تقاضای واقعی بازار

در ساختار سنتی، رسیدن اطلاعات واقعی بازار به Manufacturer ممکن است بسیار کند باشد.

برای مثال، گاهی واکنش واقعی بازار فقط زمانی مشخص می‌شود که:

> سفارش مجدد (Repeat Order) اتفاق بیفتد یا اتفاق نیفتد.

پُل در بلندمدت می‌تواند داده‌ای ایجاد کند که به تحلیل این مسئله کمک کند.

---

# 4. POL's Strategic Role

پُل قرار نیست از روز اول مالک کالا باشد.

همچنین قرار نیست:

- انبار Vendorها را جایگزین کند
- ناوگان حمل‌ونقل همه Vendorها را جایگزین کند
- نقش Vendorهای خوب را حذف کند

مدل اصلی پُل این است:

> **POL connects People + Information + Transactions + Data.**

پُل در مرکز یک لایه دیجیتال قرار می‌گیرد.

---

# 5. POL Ecosystem Architecture

مدل کلی مسئولیت‌ها در اکوسیستم:

## POL

POL مسئول لایه‌های زیر است:

- Data
- Software
- Transaction
- Trust Layer

---

## Vendor

Vendor مسئول موارد زیر است:

- Inventory
- Pricing
- Fulfillment

Vendor همچنان می‌تواند:

- انبار خود را داشته باشد
- قیمت خود را تعیین کند
- فرآیند آماده‌سازی سفارش را انجام دهد
- سیستم تحویل خود را داشته باشد

---

## 3PL

در صورت استفاده:

- Delivery
- Logistics Services

می‌تواند توسط Third-Party Logistics انجام شود.

---

## Bank / Financial Partner

در مراحل آینده می‌تواند مسئول:

- Credit
- Financial Services
- BNPL Infrastructure

باشد.

---

## Manufacturer

Manufacturer مسئول:

- Production
- Product Strategy
- Supply

است.

در مراحل بعدی می‌تواند از خدمات پُل برای:

- Advertising
- Market Intelligence
- Campaigns
- Data Products

استفاده کند.

---

# 6. Core Market Participants

## 6.1 Retailer

در MVP اولیه:

- Supermarket
- Grocery Store

مخاطب اصلی Retailer هستند.

در آینده امکان توسعه به:

- Small Chain Stores
- Specialty Food Stores
- Restaurants
- Cafes
- Hotels

وجود دارد.

---

## 6.2 Vendor

Vendor در پروژه پُل فقط به معنای یک بنکدار سنتی نیست.

Vendor اولیه می‌تواند شامل:

- بنکدار عمده‌فروش FMCG
- Distributor
- شرکت پخش
- Distributor دارای نمایندگی انحصاری

باشد.

---

## 6.3 Manufacturer

Manufacturer در ابتدای MVP، مشتری اصلی محصول نیست.

ورود Manufacturer بعد از شکل‌گیری یک شبکه مناسب از:

- Retailers
- Vendors
- Transactions
- Market Data

برنامه‌ریزی شده است.

اولین محصول درآمدی پیشنهادی برای Manufacturer:

> **Advertising**

است.

بعد از آن می‌تواند شامل:

- Market Intelligence
- Data Products
- Campaign Management
- Distribution Intelligence

شود.

---

## 6.4 Visitor / Field Force

Visitor در سیستم سنتی نقش بسیار مهمی دارد.

پُل نمی‌خواهد از روز اول این نقش را حذف کند.

در مرحله اولیه، Field Force می‌تواند برای:

1. پیدا کردن مشتری
2. نصب و راه‌اندازی App
3. آموزش مشتری
4. کمک به ثبت اولین سفارش
5. پشتیبانی
6. مدیریت برخی روابط
7. حل تعارضات

استفاده شود.

اما هدف بلندمدت:

> کاهش وابستگی سیستم به سفارش‌گیری دستی است.

در آینده Visitor بیشتر می‌تواند نقش:

- Activation
- Education
- Support
- Conflict Resolution

داشته باشد.

---

# 7. Core Product Thesis

Workflow اصلی پُل از یک فرآیند ساده شروع می‌شود:

```text
Retailer
    ↓
Category
    ↓
Subcategory
    ↓
Products
    ↓
Cart
    ↓
Market Options
+
POL Recommendation
    ↓
Retailer Decision
    ↓
Vendor Fulfillment
    ↓
Delivery
    ↓
Acceptance / Issue
    ↓
Transaction Data
    ↓
Learning
```

این چرخه یکی از مهم‌ترین پایه‌های محصول پُل است.

---

# 8. Retailer Value Proposition

مهم‌ترین انگیزه اولیه Retailer برای استفاده از پُل:

## Primary Trigger

> **Speed & Convenience**

سرعت و راحتی سفارش.

## Secondary Trigger

> **Better Price**

قیمت بهتر.

Retailer از طریق پُل می‌تواند:

- محصولات را پیدا کند
- گزینه‌های مختلف را ببیند
- Vendorهای مختلف را پیدا کند
- قیمت‌ها را مشاهده کند
- پیشنهاد پُل را ببیند
- سفارش را دیجیتال ثبت کند

---

# 9. Vendor Value Proposition

Vendor از پُل می‌تواند به‌مرور دریافت کند:

- Customer Acquisition
- دسترسی به مشتری جدید
- کاهش تدریجی هزینه بازاریابی
- کاهش وابستگی به سفارش‌گیری سنتی
- پوشش بهتر بازار
- داده عملیاتی
- Visibility بهتر
- ابزار مدیریت فروش

یک پیام مهم استراتژیک برای Vendor:

> اگر رقبای من بتوانند با هزینه عملیاتی کمتر بازار بیشتری را پوشش دهند، ساختار سنتی من می‌تواند به یک disadvantage تبدیل شود.

---

# 10. Customer Freedom Principle

پُل قصد ندارد Retailer را مجبور کند با یک Vendor مشخص کار کند.

اگر Retailer:

- امروز با Vendor A کار کند
- و بعداً Vendor B را انتخاب کند

پلتفرم مانع او نمی‌شود.

اصل:

> **Freedom creates trust more effectively than forced lock-in.**

هدف پُل ایجاد ارزش است تا مشتری به‌دلیل ارزش واقعی پلتفرم باقی بماند.

---

# 11. Discovery and Recommendation

پُل می‌تواند دو چیز را هم‌زمان نشان دهد:

## Market Options

گزینه‌های موجود در بازار.

## POL Recommendation

پیشنهاد الگوریتم پُل.

Retailer می‌تواند تصمیم بگیرد:

- پیشنهاد پُل را انتخاب کند
- گزینه دیگری را انتخاب کند

این رفتار خود تبدیل به Data می‌شود.

```text
Options
+
Recommendation
+
User Choice
+
Outcome
↓
Learning
```

---

# 12. Cart Allocation

ممکن است یک Cart توسط:

- یک Vendor
- یا چند Vendor

تأمین شود.

اصل اولیه:

> پُل می‌تواند گزینه‌های مختلف را پیشنهاد دهد، اما Retailer تصمیم نهایی را می‌گیرد.

اگر یک Vendor بتواند بخش بزرگی از Cart را تأمین کند، ممکن است برای کاهش پیچیدگی گزینه مناسبی باشد.

اما اگر Split Cart:

- قیمت بهتر
- Coverage بهتر
- شرایط بهتر

ایجاد کند، می‌تواند به‌عنوان پیشنهاد ارائه شود.

منطق دقیق این سیستم باید در بخش Algorithms توسعه و آزمایش شود.

---

# 13. Trust Layer

یکی از مهم‌ترین مسائل بازار:

> Trust

است.

در مدل سنتی، اعتماد معمولاً با:

- ارتباط
- تجربه
- خریدهای کوچک

ساخته می‌شود.

پُل تلاش می‌کند بخشی از این اطلاعات را دیجیتال کند.

Reputation می‌تواند بر اساس رفتار واقعی ساخته شود.

برای مثال:

- Fulfillment Rate
- On-Time Delivery
- Return Rate
- Wrong Shipment
- Damaged Goods
- Discrepancy
- Dispute Resolution

هر رفتار می‌تواند وزن متفاوتی داشته باشد.

هدف:

> کاهش نیاز به آزمون‌وخطای کامل برای شناخت طرف مقابل.

---

# 14. Data Strategy

پُل در بلندمدت فقط یک Ordering App نیست.

هر Interaction می‌تواند Data ایجاد کند.

نمونه داده‌ها:

## Retailer

- سفارش‌ها
- رفتار خرید
- Basket Composition
- Repeat Orders
- انتخاب Vendor
- انتخاب یا رد Recommendation

## Vendor

- Inventory
- Pricing
- Order Acceptance
- Fulfillment
- Delivery Performance

## Transaction

- Order Value
- Payment
- Settlement

## Operational Events

- Wrong Shipment
- Return
- Damaged Goods
- Incomplete Order
- Cancellation
- Delay

این داده‌ها پایه آینده:

> **Market Intelligence**

خواهند بود.

---

# 15. Manufacturer Opportunity

پس از ایجاد شبکه و تراکنش کافی، Manufacturer می‌تواند به یک مشتری مهم پُل تبدیل شود.

اولین مدل درآمدی:

> Advertising

برای مثال:

Manufacturer می‌تواند در یک:

- Category
- Subcategory
- City
- Market Segment

فضای تبلیغاتی داشته باشد.

تبلیغات باید به‌وضوح از:

- Recommendation
- Organic Discovery

جدا باشد.

برای مثال:

> **Sponsored / Advertisement**

باید مشخص باشد.

در بلندمدت Manufacturer می‌تواند از پُل برای پاسخ دادن به سؤال‌هایی مانند:

> چرا محصول من فروش نمی‌رود؟

استفاده کند.

---

# 16. Business Model — Initial Direction

## Retailer

استفاده اولیه برای Retailer:

> Free

است.

---

## Vendor

در Pilot اولیه:

> **POL Commission = 0%**

برای سه ماه.

هدف:

- کاهش Friction
- کاهش مقاومت
- کمک به تغییر رفتار
- جمع‌آوری Evidence واقعی

بعد از Pilot، مدل کمیسیون باید بر اساس:

- Category
- SKU Economics
- Operational Value
- Market Conditions

تعیین شود.

بنابراین:

> یک نرخ ثابت جهانی برای همه کالاها هنوز تصمیم قطعی نیست.

کالاهای اساسی ممکن است کمیسیون پایین‌تری داشته باشند.

برخی کالاها ممکن است کمیسیون بالاتری داشته باشند.

---

# 17. Payments and Settlement — Initial Direction

دو حالت اولیه در مدل وجود دارد:

## Direct Payment

Retailer مستقیماً به Vendor پرداخت می‌کند.

Transaction در سیستم ثبت می‌شود.

---

## Payment Through POL

Retailer پول را به سیستم پرداخت می‌کند.

پس از:

- Delivery
- بررسی سفارش
- عبور از شرایط تعریف‌شده برای Acceptance

Settlement انجام می‌شود.

کمیسیون پُل طبق مدل فعال کسر شده و باقی‌مانده طبق سیستم مالی تعریف‌شده به Vendor اختصاص پیدا می‌کند.

جزئیات قانونی، مالی و رگولاتوری این بخش باید جداگانه بررسی شود.

---

# 18. MVP Philosophy

MVP نباید صرفاً یک Prototype نمایشی باشد.

هدف:

> ساخت یک سیستم واقعی که بتواند Workflow اصلی بازار را اجرا کند.

در عین حال، قابلیت‌هایی که:

- پیچیدگی بسیار زیاد دارند
- نیازمند زیرساخت قانونی ویژه هستند
- برای Validation اولیه ضروری نیستند

می‌توانند به مراحل بعد منتقل شوند.

نمونه:

> BNPL

ممکن است از روز اول اجرا نشود، اما Data Architecture و رفتارهای موردنیاز برای توسعه آینده آن باید در نظر گرفته شوند.

---

# 19. Pilot Philosophy

Pilot برای اثبات اسلایدهای Pitch Deck نیست.

Pilot باید Evidence واقعی تولید کند.

مواردی که باید آزمایش شوند:

- آیا Retailer واقعاً سفارش می‌دهد؟
- آیا دوباره سفارش می‌دهد؟
- آیا Vendor سفارش را به‌درستی Fulfill می‌کند؟
- آیا Field Force می‌تواند مشتری را Activate کند؟
- چه میزان Support لازم است؟
- چه مشکلات عملیاتی رخ می‌دهد؟
- آیا Vendor واقعاً ارزش اقتصادی دریافت می‌کند؟
- آیا رفتار دیجیتال پایدار می‌شود؟

نتایج Pilot باید پایه مرحله بعدی برای:

- Product Improvement
- Unit Economics
- Investor Discussions
- Scaling

باشد.

---

# 20. Research and Evidence Rules

یکی از مهم‌ترین اصول این Knowledge Base:

> **Evidence نباید با Assumption یا Inference مخلوط شود.**

تمام اطلاعات مهم باید تا حد امکان با یکی از برچسب‌های زیر ثبت شوند.

### FIELD EVIDENCE

داده حاصل از:

- مصاحبه
- مشاهده
- تحقیق میدانی
- تجربه مستقیم

---

### EXTERNAL BENCHMARK

داده یا تجربه حاصل از:

- شرکت‌های خارجی
- بازارهای مشابه
- تحقیقات خارجی

---

### INFERENCE

نتیجه‌گیری منطقی از داده‌ها.

Inference هنوز Fact نیست.

---

### DECISION

تصمیم فعلی پروژه.

---

### HYPOTHESIS

فرضیه‌ای که باید آزمایش شود.

---

### OPEN QUESTION

سؤالی که هنوز پاسخ نهایی ندارد.

---

# 21. Knowledge Base Structure

```text
POL/
│
├── 00_PROJECT_OVERVIEW/
├── 01_RESEARCH/
├── 02_STRATEGY/
├── 03_CUSTOMERS/
├── 04_VALUE_PROPOSITION/
├── 05_BUSINESS_MODEL/
├── 06_PRODUCT/
├── 07_ALGORITHMS/
├── 08_DATA/
├── 09_OPERATIONS/
├── 10_GO_TO_MARKET/
├── 11_PILOT/
└── 12_ROADMAP/
```

هر بخش مسئول نگهداری یک حوزه مشخص از دانش پروژه است.

اطلاعات نباید صرفاً برای جلوگیری از تکرار، حذف شوند.

در صورت مرتبط بودن یک موضوع با چند بخش:

- سند اصلی باید مشخص باشد.
- سایر اسناد باید به آن ارجاع دهند.

---

# 22. Current Stage

پُل در مرحله:

> **Research → Product Definition → MVP Design → Pilot Preparation**

قرار دارد.

اولویت فعلی:

1. تکمیل Knowledge Base
2. تثبیت Problem Definition
3. تکمیل Customer Understanding
4. طراحی MVP واقعی
5. طراحی Algorithm Logic
6. ساخت MVP
7. گرفتن Validation و رضایت اولیه از بازیگران بازار
8. اجرای Pilot
9. جمع‌آوری Data و Evidence
10. آماده‌سازی برای Investor Discussions

---

# 23. Long-Term Direction

چشم‌انداز بلندمدت پُل:

```text
Traditional Distribution
        ↓
Digital Transactions
        ↓
Market Visibility
        ↓
Trust Infrastructure
        ↓
Data Network
        ↓
Market Intelligence
        ↓
Advertising & Campaigns
        ↓
Financial Services
        ↓
Digital FMCG Infrastructure
```

هدف نهایی صرفاً ساخت یک Application نیست.

هدف:

> ساخت یک زیرساخت دیجیتال که بتواند جریان اطلاعات، تراکنش و اعتماد را در بازار FMCG به شکل بهتری سازمان‌دهی کند.

---

# Document Status

**Status:** Draft — Based on current validated project knowledge

این فایل باید با پیشرفت پروژه به‌روز شود.

آخرین اصل:

> **Knowledge is preserved. Decisions evolve. Evidence remains traceable.**