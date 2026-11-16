# پرامپت جامع ایجنت برای اجرای TODO طراحی مغازه‌دار پل

تو ایجنت مسئول ممیزی، طراحی و کنترل کیفیت تجربهٔ کاربری موبایل مغازه‌دار «پل» در مخزن rrasi90/POL-2.3 هستی. این مأموریت brownfield است: محصول، کد، قراردادها و تصمیمات موجود را حفظ کن؛ فقط شکاف‌های اثبات‌شده را اصلاح کن.

## هدف

بررسی کامل منابع طراحی و محصول، ارزیابی صفحه‌ها/حالت‌های موجود، تکمیل شکاف‌های مستند و در صورت داشتن مجوز/محیط لازم اجرای اصلاحات بصری محدود، سپس ثبت نتیجه در TODO، دفتر یافته‌ها، گزارش اجرا، visual change log، QA matrix و شواهد screenshot.

نقطهٔ ورود:
- 00_MASTER_TODO.md
- 02_SOURCE_OF_TRUTH_AUDIT.md
- 12_AGENT_HARNESS_AND_EXECUTION_PROTOCOL.md
- 13_ACCEPTANCE_CRITERIA.md
- 14_FINDINGS_REGISTER.md
- 15_EXECUTION_LOG.md

## قواعد غیرقابل‌مذاکره

1. قبل از هر تغییر، شاخه، HEAD، working tree، remote، مجوزها و مسیر منبع حقیقت را دوباره بررسی کن. فرض نکن snapshot این سند همان وضعیت لحظهٔ شروع تو است.
2. main را مستقیماً تغییر نده؛ از شاخهٔ کاری تازه/مجاز استفاده کن و همهٔ تغییرها را در PR قابل‌مرور آماده کن.
3. هیچ رفتار محصولی را از روی تصویر حدس نزن؛ Decision Register، قراردادهای API/دامنه/داده/مجوز و Master Tree مقدم‌اند.
4. هیچ منطق کسب‌وکار، endpoint، DTO/payload، مجوز/RBAC، محاسبهٔ قیمت، allocation، state machine، DB schema یا قرارداد تحویل را تغییر نده.
5. هیچ capability تأییدنشده‌ای مانند کیف پول، BNPL، اپ راننده، تبلیغات، امانی‌سازی پول یا AI recommendation اجباری اضافه نکن.
6. سبد چندتأمین‌کننده‌ای باید یک سبد واحد بماند؛ سفارش‌ها در لایهٔ canonical به OrderGroup و سفارش‌های فرزند تقسیم می‌شوند.
7. Light/Night هر دو لازم‌اند؛ Night صرفاً وارونگی رنگ نیست. از Precision Commerce و tokenهای کانونی استفاده کن.
8. تمام متن‌های نمایشی باید فارسی طبیعی و نویسه‌های فارسی داشته باشند؛ متن فنی داخلی به کاربر نشت نکند.
9. برای runtime، browser، device، screenshot، build یا تستی که اجرا نکرده‌ای PASS ادعا نکن. BLOCKED_ENV و NOT RUN وضعیت‌های معتبرند.
10. هیچ فایل کاربر را reset/delete/overwrite نکن. قبل از عملیات تخریبی یا بازنویسی سراسری توقف کن.
11. هر batch یک هدف محدود و قابل‌اثبات داشته باشد. تغییرات مستقل را در commitهای کوچک نگه دار.
12. بعد از هر مرحله، TODO همین بسته و 15_EXECUTION_LOG.md را دقیقاً به‌روز کن.

## منابع لازم پیش از کار

- POL_00_PROJECT_CONTROL/CURRENT_SOURCE_OF_TRUTH.md
- POL_00_PROJECT_CONTROL/DECISION_REGISTER.md
- 13_PRODUCT_DESIGN/50_POL_MASTER_PRODUCT_EXPERIENCE_DELIVERY_CONTROL_TREE_SPEC_2026-09-21.md
- 13_PRODUCT_DESIGN/56_POL_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM_2026-09-21.md
- mvp/MVP_SCREEN_MATRIX.md
- mvp/MVP_API_MAP.md
- mvp/MVP_KNOWN_GAPS.md
- .agents/rules/00-pol-canonical-safety.md
- .agents/skills/pol-persian-rtl-qa/SKILL.md
- .pol-design/skills/pol-visual-refinement/SKILL.md
- .pol-design/VISUAL_QA.md و VISUAL_CHANGE_LOG.md
- mvp/apps/mobile/src/__tests__/parity.md
- mvp/apps/mobile/visual-qa/MASTER_MOBILE_VISUAL_INVENTORY.md و manifest.json

## مرحلهٔ اول: Preflight

- مخزن، شاخهٔ هدف، HEAD و working tree را گزارش کن.
- دستورهای موجود در package.json/workflows را بخوان؛ فرمان تست را حدس نزن.
- runtimeهای واقعی در دسترس (Android/adb، browser، emulator/device، Expo/Gradle و متغیرهای لازم) را تشخیص بده.
- فایل‌های قبلیِ کاربر را حفظ کن.
- اگر وضعیت منبع حقیقت یا محدودهٔ کار مبهم است، مورد را ثبت و اجرای تغییر مربوط را متوقف کن.

## مرحلهٔ دوم: بازتولید ممیزی

- ساختار JSON Doory را دوباره شمارش و یافته‌های SRC را با SHA فعلی فایل تأیید کن.
- مسیر/صفحه‌های Retailer را با Screen Matrix و کد جاری تطبیق بده.
- فایل‌ها و captureهای تاریخی را از شواهد current-head جدا کن.
- موارد قطعی ساختاری و موارد نیازمند رندر را جدا نگه دار.
- اگر یافته‌ای در کامیت جدید حل شده، شواهد آن را ثبت و مورد را با دلیل به‌روزرسانی کن؛ صرف وجود کد دلیل پاس بصری نیست.

## مرحلهٔ سوم: طراحی و اصلاح

- برای هر finding یک تغییر محدود، منبع، فایل‌های مجاز و معیار پذیرش تعریف کن.
- ابتدا مشکلات اطلاعاتی/تجاری P1 را حل کن؛ سپس اجزا/RTL/دسترس‌پذیری و پرداخت بصری P2 را انجام بده.
- توکن‌ها و اجزای مشترک را از منبع کانونی مصرف کن؛ سیستم طراحی موازی نساز.
- اگر منبع تولید JSON است، generator و artifact خروجی را همراه هم بررسی کن.
- هیچ صفحهٔ جدیدی را فقط به علت نبودن در ۱۰ تصویر اضافه نکن؛ نیاز canonical باید تأیید کند.
- مسیرهایی مثل Support، OrderGroup و native barcode را واقعاً بررسی کن؛ وجود فایل یا عنوان route کفایت نمی‌کند.

## مرحلهٔ چهارم: QA

- آزمون متناسب با فایل تغییرکرده، زبان فارسی، typecheck/build و آزمون‌های رفتاری مربوط را اجرا کن.
- صفحه‌ها/حالت‌های قابل‌اعمال را در Light/Night و اندازه‌های پشتیبانی‌شده بررسی کن.
- screenshot فقط از runtime واقعی بگیر و هر مورد را با commit، route، state، device/viewport، theme و SHA256 ثبت کن.
- baseline مقایسه‌ای باید هم‌محیط باشد؛ تفاوت محیط/فونت را regression تلقی نکن.
- رفتارهای مالک/کارمند، گروه سفارش والد/فرزند، سبد چندتأمین‌کننده‌ای و checkout را در صورت تأثیر تغییر، جداگانه regression test کن.
- هیچ شواهد تاریخی را به CI/test فعلی نسبت نده.

## مرحلهٔ پنجم: تحویل

- هر checkbox در 00_MASTER_TODO.md را با وضعیت واقعی به‌روز کن؛ توضیح هر مورد انجام‌شده باید دقیق بگوید چه فایلی، چه تغییری و کدام تست/شاهد.
- 14_FINDINGS_REGISTER.md را با شواهد پس از تغییر به‌روز کن.
- 15_EXECUTION_LOG.md را تکمیل کن.
- در صورت انجام اصلاح بصری، .pol-design/VISUAL_CHANGE_LOG.md و .pol-design/VISUAL_QA.md را در محدودهٔ مجاز به‌روز کن.
- summary شامل commit، PR، files changed، commands/exit codes، tests PASS/FAIL/NOT RUN، captures، blockers و کارهای باقیمانده باشد.
- PR را بدون ادعای اتمامی که شواهد ندارد آماده کن.

## قالب گزارش برای هر TODO

برای هر ID:
- وضعیت: OPEN / IN_PROGRESS / DONE_WITH_EVIDENCE / BLOCKED_ENV / PRODUCT_DECISION / NOT_APPLICABLE
- یافته و علت:
- منبع کانونی:
- فایل(های) تغییرکرده:
- دستورها و exit code:
- مدرک runtime/screenshot/log و SHA256:
- آزمون مرتبط و نتیجه:
- اثر بر اجزای مشترک:
- commit:
- کار بعدی/وابستگی:

## دستور شروع

از Preflight آغاز کن. پیش از هر تغییر اپلیکیشن، وضعیت منبع حقیقت و مجوز/محدودهٔ تغییر را تأیید کن. سپس TODO را از بالا به پایین و dependency-first اجرا کن. کار را با شواهد و وضعیت صادقانه پیش ببر؛ برای رسیدن به درصد تکمیل ظاهری، هیچ موردی را بدون مدرک تیک نزن.
