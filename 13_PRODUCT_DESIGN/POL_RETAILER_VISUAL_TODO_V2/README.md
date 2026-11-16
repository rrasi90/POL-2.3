# بستهٔ اجرایی ممیزی و ارتقای رابط کاربری مغازه‌دار پل

**شناسه:** POL-RETAILER-VISUAL-TODO-V2  
**وضعیت:** بستهٔ اجرایی تکمیلی؛ اجرای اصلاحات رابط کاربری نیازمند گیت‌های مندرج در TODO است  
**شاخهٔ مبنا:** main  
**کامیت مبنا هنگام آغاز ممیزی:** 84538fe5b571b8da9f8720835206264348ee0122  
**مسیر:** 13_PRODUCT_DESIGN/POL_RETAILER_VISUAL_TODO_V2/

## هدف و محدودیت

این پوشه بسته‌ای اجرایی و شواهد‌محور برای ممیزی و اصلاح طراحی اپلیکیشن موبایل مغازه‌دار «پل» است. منبع حقیقت محصول یا سیستم طراحی جدیدی ایجاد نمی‌کند؛ بلکه وظایف طراحی را به منابع رسمی، شناسه‌های صفحه، شواهد QA و معیارهای پذیرش وصل می‌کند.

این بسته بر اساس فایل‌های جاری GitHub و بررسی ساختاری JSON/کد تدوین شده است. در این مرحله اجرای محلی اپ، رندر پیکسلی تصاویر PNG، شبیه‌ساز اندروید یا آزمون مرورگری انجام نشده است. هیچ اسکرین‌شات جدیدی ساخته یا ادعا نشده و موارد ساختاری از موارد نیازمند رندر تفکیک شده‌اند.

## سلسله‌مراتب منبع حقیقت

1. POL_00_PROJECT_CONTROL/DECISION_REGISTER.md
2. POL_00_PROJECT_CONTROL/CURRENT_SOURCE_OF_TRUTH.md
3. قراردادهای API، داده، دامنه و مجوز
4. 13_PRODUCT_DESIGN/50_POL_MASTER_PRODUCT_EXPERIENCE_DELIVERY_CONTROL_TREE_SPEC_2026-09-21.md
5. 13_PRODUCT_DESIGN/56_POL_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM_2026-09-21.md
6. mvp/MVP_SCREEN_MATRIX.md و mvp/MVP_API_MAP.md
7. مهارت‌های طراحی و QA موجود و شواهد متصل به کامیت جاری
8. فایل‌های طراحی Doory و تصاویر آن به‌عنوان خط مبنا/شواهد؛ تعارض با منبع بالاتر باید ثبت شود، نه اینکه بی‌صدا حل شود.

منابع اجرایی موجود که باید تکمیل شوند، نه دوباره ساخته شوند: .pol-design/skills/pol-visual-refinement/SKILL.md، .pol-design/VISUAL_QA.md، .pol-design/VISUAL_CHANGE_LOG.md، .pol-design/tokens/tokens.json، .agents/rules/00-pol-canonical-safety.md، .agents/skills/pol-persian-rtl-qa/SKILL.md، mvp/apps/mobile/visual-qa/MASTER_MOBILE_VISUAL_INVENTORY.md، manifest.json و mobile parity matrix.

## نقشهٔ اسناد

| فایل | نقش |
|---|---|
| 00_MASTER_TODO.md | نقطهٔ ورود ایجنت و فهرست اجرای مرحله‌ای |
| 01_RESEARCH_TOOLING_AND_METHODS.md | تحقیق ابزارها و روش‌های طراحی همراه با هوش مصنوعی |
| 02_SOURCE_OF_TRUTH_AUDIT.md | وضعیت منابع، تعارض‌ها و حدود قطعیت |
| 03_SCREEN_AND_STATE_INVENTORY.md | فهرست صفحه‌ها/حالت‌های موبایل مغازه‌دار و وضعیت شواهد |
| 04_USER_FLOWS_AND_NAVIGATION.md | جریان‌های اصلی، مرزهای نقش و مسیرهای برگشت |
| 05_DESIGN_SYSTEM_AND_TOKENS.md | سیستم بصری کانونی، توکن‌ها و قواعد انطباق |
| 06_SCREEN_BY_SCREEN_REMEDIATION.md | اقدام‌های مرتبط با صفحه و سطح محصول |
| 07_MISSING_SCREENS_AND_STATES.md | شکاف‌های احتمالی و روش اثبات فقدان |
| 08_ASSETS_AND_ICONOGRAPHY.md | تصاویر، آیکون‌ها، ایموجی‌ها و دارایی‌ها |
| 09_MOTION_AND_MICROINTERACTIONS.md | مشخصات حرکت و بازخورد |
| 10_RTL_ACCESSIBILITY_AND_RESPONSIVENESS.md | فارسی، RTL، دسترس‌پذیری و نمایشگر |
| 11_VISUAL_QA_AND_REGRESSION.md | ثبت تصویر، اختلاف بصری و رگرسیون |
| 12_AGENT_HARNESS_AND_EXECUTION_PROTOCOL.md | هارنس، ترتیب اجرا، کنترل تغییر و گزارش |
| 13_ACCEPTANCE_CRITERIA.md | معیارهای تکمیل و گیت‌های پذیرش |
| 14_FINDINGS_REGISTER.md | یافته‌های شواهد‌محور با اولویت و معیار بستن |
| 15_EXECUTION_LOG.md | دفتر ثبت اجرا و قالب شواهد |
| 16_AGENT_EXECUTION_PROMPT.md | پرامپت جامع آمادهٔ استفاده برای ایجنت |

## قرارداد وضعیت

- CONFIRMED_STATIC: فایل متنی/ساختاری فعلی شواهد دارد؛ به معنی تأیید رندر نیست.
- RENDER_VERIFY: نیازمند مشاهدهٔ رابط واقعی در محیط اجرا.
- PRODUCT_DECISION: نیازمند ارجاع به تصمیم محصول/دامنه.
- BLOCKED_ENV: وابسته به ابزار یا محیطی که فعلاً تأیید نشده.
- DONE_WITH_EVIDENCE: پس از عبور از معیار پذیرش و ثبت مدرک.
- NOT_APPLICABLE: با دلیل و منبع ثبت شده است.

## محدودیت دامنه

بسته برای POL Market و مسیرهای مشترک احراز هویت/حساب است. صفحات Vendor، Ops، Field و Corporate فقط جایی وارد می‌شوند که پوسته یا جزء مشترک Retailer را تحت‌تأثیر قرار دهند. هیچ قابلیت پیشنهادی بدون اثبات در تصمیمات محصول به دامنه اضافه نشود.
