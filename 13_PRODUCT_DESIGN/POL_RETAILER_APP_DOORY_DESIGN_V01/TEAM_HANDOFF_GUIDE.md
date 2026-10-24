# 🚀 راهنمای جامع دسترسی و تحویل تیم به طراحی رابط کاربری اپلیکیشن مغازه‌داران «پل»
### (Team Handoff & Access Guide - POL Retailer App UI/UX V1.0)

این سند برای تمام اعضای تیم **«پل»** (مدیران محصول، طراحان محصول، توسعه‌دهندگان فرانت‌اند/موبایل و تیم کنترل کیفیت) تدوین شده است تا بتوانند به سادگی به تمامی فایل‌های طراحی، تصاویر باکیفیت، کدهای ساختاری، مستندات سیستم دیزاین و اسکریپت‌های پروژه در گیت‌هاب دسترسی داشته باشند.

---

## 📌 ۱. خلاصه اقدامات انجام‌شده در این نسخه

در این نسخه، رابط کاربری کامل اپلیکیشن موبایل مغازه‌داران «پل» (پلتفرم B2B خرید عمده خرده‌فروشان) بر اساس نیازهای واقعی بازار FMCG ایران طراحی و پیاده‌سازی شده است:

1. **طراحی ۱۰ صفحه کامل و عملیاتی اپلیکیشن:**
   - 📱 صفحه ۱: شروع و خوش‌آمدگویی (`01_splash_welcome`)
   - 📱 صفحه ۲: ارزش پیشنهادی و معرفی پل (`02_onboarding_features`)
   - 📱 صفحه ۳: ورود با شماره موبایل (`03_login_phone`)
   - 📱 صفحه ۴: تأیید شماره و کد یک‌بارمصرف (`04_verify_otp`)
   - 📱 صفحه ۵: انتخاب شهر و استان فعالیت (`05_city_selection`)
   - 📱 صفحه ۶: خانه، ویترین محصولات و بنرهای تأمین‌کنندگان (`06_home_feed`)
   - 📱 صفحه ۷: دسته‌بندی‌های کالاها و سلسله‌مراتب عمده‌فروشی (`07_categories`)
   - 📱 صفحه ۸: فهرست و فیلتر پیشرفته محصولات (`08_product_list`)
   - 📱 صفحه ۹: جزئیات کالا، قیمت پلکانی، واحد فروش و انتخاب کارتن (`09_product_detail`)
   - 📱 صفحه ۱۰: سبد خرید عمده، تخفیف، هزینه باربری و صورت‌حساب (`10_cart_checkout`)

2. **۲ صفحه تکمیلی سیستم طراحی و مرجع کامپوننت‌ها:**
   - 🎨 صفحه ۱۱: راهنمای سیستم طراحی پل (`11_design_system_guide`)
   - 🧩 صفحه ۱۲: اجزای مرجع، اتم‌ها و مولکول‌های قابل استفاده مجدد (`12_reference_components`)

3. **بوم پرزنتیشن نمای کلی (Master Overview Canvas):**
   - 🖼️ بوم اختصاصی در ابعاد `۲۲۰۰ × ۱۴۵۰` پیکسل با پس‌زمینه تیره و چیدمان شکیل ده صفحه کنار یکدیگر جهت بررسی کلان جریان کاربر (User Flow).

4. **تضمین ۱۰۰٪ اصول زبان فارسی و راست‌به‌چپ (RTL):**
   - حذف کامل حروف عربی («ي» و «ك») و جایگزینی با حروف اصیل فارسی («ی» و «ک»).
   - تبدیل تمامی اعداد به ارقام رسمی فارسی (۰ تا ۹).
   - رعایت دقیق نیم‌فاصله‌ها و اصطلاحات اصیل صنف بازار عمده‌فروشی ایران.
   - پاس شدن کامل لینتر اختصاصی `pol-persian-rtl-qa` با **۰ خطا**.

---

## 📂 ۲. ساختار پوشه‌ها و دسترسی مستقیم در گیت‌هاب

تمام خروجی‌های این پروژه در مسیر زیر در ریپازیتوری آنلاین قرار دارند:
👉 **[مشاهده پوشه طراحی در گیت‌هاب](https://github.com/rrasi90/POL-2.3/tree/main/13_PRODUCT_DESIGN/POL_RETAILER_APP_DOORY_DESIGN_V01)**

```text
13_PRODUCT_DESIGN/POL_RETAILER_APP_DOORY_DESIGN_V01/
├── README.md                      # معرفی و مشخصات فنی پروژه
├── TEAM_HANDOFF_GUIDE.md          # همین راهنمای دسترسی تیم
├── docs/                          # اسناد تحلیلی، سیستم دیزاین و گزارش‌ها
│   ├── 01_سند_نقد_و_بررسی_طرح_اولیه.md
│   ├── 02_سند_سیستم_طراحی_پل.md
│   ├── 03_گزارش_تحویل_ده_صفحه_طراحی.md
│   └── 04_فهرست_اسکیلهای_پروژه.md
├── images/                        # خروجی‌های تصویری با کیفیت بالا (Retina PNG)
│   ├── pol_retailer_app_overview_10_screens.png   # نمای کلی ده صفحه (۲۲۰۰×۱۴۵۰)
│   ├── page_01_splash_welcome.png
│   ├── page_02_onboarding_features.png
│   ├── page_03_login_phone.png
│   ├── page_04_verify_otp.png
│   ├── page_05_city_selection.png
│   ├── page_06_home_feed.png
│   ├── page_07_categories.png
│   ├── page_08_product_list.png
│   ├── page_09_product_detail.png
│   └── page_10_cart_checkout.png
├── json/                          # ساختار داده‌ای استاندارد Doory و کانواس
│   ├── pol_retailer_master_12pages.json           # سند ۱۲ صفحه‌ای کامل
│   ├── pol_retailer_overview_canvas.json          # بوم پرزنتیشن نمای کلی
│   └── pages/                                     # فایل‌های JSON تک‌به‌تک هر صفحه
│       ├── page_01_splash_welcome.json
│       ├── page_02_onboarding_features.json
│       ├── page_03_login_phone.json
│       ├── page_04_verify_otp.json
│       ├── page_05_city_selection.json
│       ├── page_06_home_feed.json
│       ├── page_07_categories.json
│       ├── page_08_product_list.json
│       ├── page_09_product_detail.json
│       ├── page_10_cart_checkout.json
│       ├── page_11_design_system_guide.json
│       └── page_12_reference_components.json
└── scripts/                       # اسکریپت‌های اتوماسیون، اعتبارسنجی و ایمپورت
    ├── design_builder_tokens.py                   # توکن‌های گرافیکی و المان‌ساز
    ├── generate_pol_screens.py                    # جنریتور معماری صفحات
    ├── import_pol_to_doory.py                     # اسکریپت ادغام مستقیم در دیتابیس Doory
    ├── pol_persian_rtl_qa_linter.py               # لینتر کیفیت فارسی، ارقام و RTL
    └── capture_doory_screenshots.py               # استخراج خودکار تصاویر رتینا با Playwright
```

---

## 👁️ ۳. نحوه مشاهده تصاویر و پیش‌نمایش‌ها (بدون نیاز به ابزار خاص)

اعضای تیم که می‌خواهند صفحات را به صورت تصویری مشاهده کنند، کافی است روی لینک‌های زیر کلیک کنند تا مستقیماً در مرورگر باز شوند:

| ردیف | نام صفحه | کاربرد در اپلیکیشن مغازه‌داران | لینک مشاهده مستقیم در گیت‌هاب |
| :---: | :--- | :--- | :---: |
| 🌟 | **نمای کلی ۱۰ صفحه** | تصویر پرزنتیشن با پس‌زمینه تیره و چیدمان کنار هم | [مشاهده تصویر نمای کلی](https://github.com/rrasi90/POL-2.3/blob/main/13_PRODUCT_DESIGN/POL_RETAILER_APP_DOORY_DESIGN_V01/images/pol_retailer_app_overview_10_screens.png) |
| ۱ | **شروع و خوش‌آمدگویی** | بارگذاری اولیه و شناسایی هویت بصری «پل» | [مشاهده صفحه ۱](https://github.com/rrasi90/POL-2.3/blob/main/13_PRODUCT_DESIGN/POL_RETAILER_APP_DOORY_DESIGN_V01/images/page_01_splash_welcome.png) |
| ۲ | **معرفی ارزش‌ها** | معرفی خرید کارتنی، قیمت دست اول و ارسال باربری | [مشاهده صفحه ۲](https://github.com/rrasi90/POL-2.3/blob/main/13_PRODUCT_DESIGN/POL_RETAILER_APP_DOORY_DESIGN_V01/images/page_02_onboarding_features.png) |
| ۳ | **ورود با موبایل** | لاگین با کیبورد عددی و کد اعتبارسنجی | [مشاهده صفحه ۳](https://github.com/rrasi90/POL-2.3/blob/main/13_PRODUCT_DESIGN/POL_RETAILER_APP_DOORY_DESIGN_V01/images/page_03_login_phone.png) |
| ۴ | **تأیید پیامکی** | دریافت کد ۴ رقمی و امکان ویرایش شماره | [مشاهده صفحه ۴](https://github.com/rrasi90/POL-2.3/blob/main/13_PRODUCT_DESIGN/POL_RETAILER_APP_DOORY_DESIGN_V01/images/page_04_verify_otp.png) |
| ۵ | **انتخاب شهر** | فیلتر تأمین‌کنندگان و باربری‌های فعال در شهر مقصد | [مشاهده صفحه ۵](https://github.com/rrasi90/POL-2.3/blob/main/13_PRODUCT_DESIGN/POL_RETAILER_APP_DOORY_DESIGN_V01/images/page_05_city_selection.png) |
| ۶ | **خانه و ویترین** | جستجوی سریع، بنر کارخانجات و تخفیف‌های ویژه | [مشاهده صفحه ۶](https://github.com/rrasi90/POL-2.3/blob/main/13_PRODUCT_DESIGN/POL_RETAILER_APP_DOORY_DESIGN_V01/images/page_06_home_feed.png) |
| ۷ | **دسته‌بندی‌ها** | دسته‌بندی مواد شوینده، خوراکی، سلولزی و بهداشتی | [مشاهده صفحه ۷](https://github.com/rrasi90/POL-2.3/blob/main/13_PRODUCT_DESIGN/POL_RETAILER_APP_DOORY_DESIGN_V01/images/page_07_categories.png) |
| ۸ | **فهرست کالاها** | لیست کارتنی با امکان سورت براساس حاشیه سود | [مشاهده صفحه ۸](https://github.com/rrasi90/POL-2.3/blob/main/13_PRODUCT_DESIGN/POL_RETAILER_APP_DOORY_DESIGN_V01/images/page_08_product_list.png) |
| ۹ | **جزئیات محصول** | جدول قیمت پله‌ای عمده و حداقل تیراژ خرید | [مشاهده صفحه ۹](https://github.com/rrasi90/POL-2.3/blob/main/13_PRODUCT_DESIGN/POL_RETAILER_APP_DOORY_DESIGN_V01/images/page_09_product_detail.png) |
| ۱۰ | **سبد خرید** | محاسبه کرایه باربری، سود ناخالص و پیش‌فاکتور رسمی | [مشاهده صفحه ۱۰](https://github.com/rrasi90/POL-2.3/blob/main/13_PRODUCT_DESIGN/POL_RETAILER_APP_DOORY_DESIGN_V01/images/page_10_cart_checkout.png) |

---

## 💻 ۴. راهنمای توسعه‌دهندگان فرانت‌اند و موبایل (React Native / Flutter)

توسعه‌دهندگان می‌توانند از توکن‌های استاندارد استخراج‌شده در این طراحی استفاده کنند:

### توکن‌های رنگی (Color Tokens)
- **رنگ اصلی برند (Primary Blue):** `#246BFD` (کنتراست عالی برای دکمه‌های اصلی و اقدامات مهم)
- **رنگ ثانویه / تأیید (Success Green):** `#10B981` (وضعیت موجودی در انبار، تخفیف‌ها و نشان‌های موفقیت)
- **رنگ هشدار / تخفیف (Warning Orange):** `#F59E0B` (پیشنهادات ویژه و پله‌های تخفیف تعدادی)
- **رنگ خطر / اتمام موجودی (Danger Red):** `#EF4444` (حذف از سبد و کالاهای ناموجود)
- **طیف خاکستری و متن‌ها (Grayscale):**
  - متن تیتر و اصلی: `#111827`
  - متن توضیحات و راهنما: `#6B7280`
  - خطوط جداکننده و بوردرها: `#E5E7EB`
  - پس‌زمینه کارت‌ها: `#F9FAFB` و `#FFFFFF`

### تایپوگرافی و ابعاد صفحه (Typography & Layout)
- **فونت پیشنهادی اپلیکیشن:** `IRANSansX` یا `Vazirmatn` با رعایت دقیق ZWNJ (نیم‌فاصله).
- **عرض پایه طراحی موبایل:** ۳۹۰ پیکسل در ۸۴۴ پیکسل (مبنای استاندارد iPhone 13/14 و صفحه‌نمایش‌های مدرن اندروید).
- **ارتفاع دکمه‌های لمسی:** حداقل ۴۸ تا ۵۲ پیکسل جهت سهولت کاربری با یک دست برای مغازه‌داران.

---

## 🎨 ۵. راهنمای طراحان محصول (ویرایش در Doory محلی)

اگر می‌خواهید لایه‌ها، متن‌ها یا المان‌ها را در محیط ویرایشگر Doory باز و ویرایش کنید:

1. **ایمپورت خودکار با اسکریپت پروژه:**
   با اجرای اسکریپت آماده در ترمینال سیستم، کل ۱۲ صفحه و بوم نمای کلی وارد دیتابیس لوکال Doory می‌شود:
   ```bash
   python 13_PRODUCT_DESIGN/POL_RETAILER_APP_DOORY_DESIGN_V01/scripts/import_pol_to_doory.py
   ```
2. **آدرس‌های دسترسی در مرورگر (پس از اجرای Doory لوکال):**
   - مستر ۱۲ صفحه‌ای: `http://localhost:5173/design/e0000000-0000-4000-8000-000000000001`
   - بوم نمای کلی پرزنتیشن: `http://localhost:5173/design/e0000000-0000-4000-8000-000000000002`
   - صفحات تک‌به‌تک: `http://localhost:5173/design/d1000000-0000-4000-8000-000000000001` الی `...0010`
   - قالب گالری: در تب **قالب‌ها (Templates)** با عنوان «الگوی پایه اپلیکیشن موبایل پل».

---

## 🧪 ۶. کنترل کیفیت و اعتبارسنجی خودکار

تمامی فایل‌های طراحی با اسکریپت `pol_persian_rtl_qa_linter.py` ارزیابی شده‌اند:
- بررسی کاراکترهای عربی: **۰ مورد (تأیید شد)**
- بررسی ارقام انگلیسی در رابط کاربری: **۰ مورد (تأیید شد)**
- بررسی سازگاری چیدمان با استانداردهای RTL: **تأیید شد**

همچنین تست با اسکریپت Playwright مستقیماً روی بستر وب انجام شده و پیش‌نمایش‌های بدون خطا و با کیفیت کامل استخراج شده‌اند.

---
**تیم پل — تحول در زنجیره تأمین B2B خرده‌فروشی ایران** 🇮🇷
