# دفتر ثبت یافته‌ها

این دفتر مسائل اثبات‌شده و فرضیه‌های نیازمند رندر را از هم جدا می‌کند. هیچ یافته‌ای فقط با اشاره به ظاهر بسته نمی‌شود؛ اقدام و معیار پذیرش باید ثبت شوند.

| شناسه | اولویت | وضعیت | محدوده | خلاصه | شواهد اولیه | معیار بستن |
|---|---|---|---|---|---|---|
| SRC-001 | P1 | CONFIRMED_STATIC | Design tokens | توکن‌های Doory با Precision Commerce کانونی اختلاف دارند | راهنمای Doory در برابر Doc 56 و .pol-design/tokens/tokens.json | تعارض تعیین تکلیف و نگاشت توکن ثبت؛ Light/Night تطبیق داده شود |
| SRC-002 | P1 | CONFIRMED_STATIC | QA provenance | ادعای ۵۸ سطح و capture inventory قدیمی ۶۰ مورد، منشأ/وضعیت متفاوت دارند | .pol-design/VISUAL_QA.md و فایل‌های capture تاریخی | وضعیت ادعاها به کامیت/محیط/شواهد جاری متصل شود |
| SRC-003 | P1 | CONFIRMED_STATIC | Screen inventory | ۱۲ صفحهٔ JSON شامل ۱۰ صفحهٔ محصول و ۲ صفحهٔ راهنماست | JSON مستر، ۶۷۷ شیء در 390×844 | صفحه‌های محصولی از مستندات/کامپوننت‌ها جدا شوند |
| SRC-004 | P1 | SUPERSEDED_BY_POLICY_AMENDMENT | Auth | تعارض سابق بین متن OTP شش‌رقمی، UI چهاررقمی و D-018 | صفحات ۳/۴ JSON، اصلاحیهٔ D-018، LoginScreen.tsx | قرارداد فعلی شش‌رقمی است؛ UI، متن، error/resend و visual evidence با D-018 همسان و مجدداً QA شوند |
| SRC-005 | P1 | CONFIRMED_STATIC | Basket | سربرگ سبد هر سه کالا را به یک تأمین‌کننده نسبت می‌دهد ولی اقلام از سه تأمین‌کننده‌اند | صفحات فهرست و سبد JSON؛ D-014/D-022 | خلاصه درست، سبد واحد حفظ و گروه‌بندی درون سبد در صورت نیاز |
| SRC-006 | P1 | CONFIRMED_STATIC | Product list | متن کادر قیمت عمدهٔ برنج، ویژگی بسته‌بندی است نه قیمت | صفحهٔ ۸ JSON | قیمت/واحد از منبع معتبر؛ بسته‌بندی در فیلد مستقل |
| SRC-007 | P2 | CONFIRMED_STATIC | Design guide | پنج جفت نمونه/توضیح تایپوگرافی مختصات مشترک دارند | صفحهٔ ۱۱ JSON | کادرها جدا و در بوم 390×844 بدون برخورد/برش رندر شوند |
| SRC-008 | P2 | CONFIRMED_STATIC + RENDER_VERIFY | Typography | تعدادی برچسب ۱۰ پیکسلی در مرجع وجود دارند | JSON صفحات ۱۱/۱۲ و قواعد کانونی | اندازهٔ کمتر از حد استاندارد اصلاح یا استثنا مستند شود و خوانایی روی دستگاه بررسی شود |
| SRC-009 | P2 | CONFIRMED_STATIC + RENDER_VERIFY | Assets | JSON شیء image ندارد؛ تصویرسازی محصول با shape/emoji انجام می‌شود | شمارش اشیای JSON | تصمیم عکس واقعی/تصویرسازی ثبت؛ اگر عکس، مجاز و fallback داشته باشد |
| MOB-001 | P1 | RENDER_VERIFY | Capture | وضعیت بصری Light/Night صفحه‌های موبایل باید از runtime جاری دوباره اثبات شود | Master Mobile Visual Inventory و parity؛ ledger قدیمی است | تصاویر واقعی با manifest، هش و ابعاد ثبت شوند |
| MOB-002 | P1 | RENDER_VERIFY | Support | دسترس‌پذیری مسیر پشتیبانی موبایل باید با رفتار واقعی مسیریابی تأیید شود | VQA-M-029 می‌گوید wiring باید تأیید شود؛ SupportMobileScreen.tsx وجود دارد | از UI مغازه‌دار به پشتیبانی برسد، برگشت کار کند و حالات نمایش داده شوند |
| MOB-003 | P1 | RENDER_VERIFY | Product states | پوشش خالی/لود/خطا/موفقیت باید روی runtime در Light/Night بررسی شود | VQA-M-014…030 و mobile screen matrix | هر حالت قابل‌اعمال شواهد یا عدم‌کاربرد مستند داشته باشد |
| MOB-004 | P2 | RENDER_VERIFY | Navigation icons | JSON Doory در ۷۷ متن‌شیء حاوی ایموجی دارد؛ یکپارچگی icon system در UI اجراشده باید بررسی شود | شمارش متن JSON | آیکون‌های ناوبری/عملیات از خانوادهٔ کانونی استفاده کنند یا استثنا مستند شود |
| MOB-005 | P1 | RENDER_VERIFY | Product imagery | نمایش، وضوح و برش تصویر واقعی کاتالوگ موبایل باید بررسی شود | RetailerMobileScreen.tsx؛ JSON بدون image object | عکس/placeholder با قرارداد کارت محصول در Light/Night سازگار باشد |
| FLOW-001 | P1 | PRODUCT_DECISION/VERIFY | Checkout | خرید چندتأمین‌کننده‌ای باید سبد واحد و تخصیص به سفارش‌های فرزند را حفظ کند | D-014/D-022، R-06/R-07/R-08/R-09 | والد OrderGroup و سفارش‌ها/فاکتورهای فرزند روشن باشند، بدون تغییر منطق |
| FLOW-002 | P1 | RENDER_VERIFY | Order detail | پذیرش جزئی، رهگیری تحویل و POD از نظر وضوح وضعیت/اقدام بررسی شوند | R-09B…R-09E، OrderDetailMobileScreen.tsx | حالت‌ها و بازخورد مطابق قرارداد و نقش باشند |
| FLOW-003 | P1 | RENDER_VERIFY | Returns/disputes | فرم مرجوعی/اختلاف و وضعیت ارسال/موفقیت/خطا باید بررسی شود | R-11، OrderDetailMobileScreen.tsx | مرز owner-only و recovery درست و بدون تغییر مجوز باشد |
| DS-001 | P2 | RENDER_VERIFY | Shared components | اندازهٔ لمس، فوکوس، برچسب‌خوانی و disabled/loading باید در خروجی بررسی شود | component-contracts.md، mobile ui.tsx | حداقل‌های کانونی و دسترس‌پذیری با آزمون اثبات شود |
| MOT-001 | P2 | RENDER_VERIFY | Motion | موشن نباید تأخیر/ابهام یا پرش چیدمان ایجاد کند | Doc 56 و توکن‌های motion | هر حرکت هدف، مدت، reduced-motion و آزمون داشته باشد |
| QA-001 | P1 | BLOCKED_ENV until proven | Screenshot | خروجی تازه از دستگاه واقعی در این مرحله ثبت نشده است | محدودیت محیط این ممیزی | تصاویر واقعی و قابل‌خواندن با dimensions/SHA256 ثبت شوند |

## قواعد اولویت

- P0: مسیر حیاتی خراب/مانع استفاده؛ در این snapshot مورد P0 جدیدی اعلام نشده چون runtime اجرا نشده است.
- P1: مغایرت اطلاعاتی یا شکاف حیاتی آزمون.
- P2: اصلاحات بصری، خوانایی، دارایی و تعامل.
- P3: پرداخت ظریف پس از رفع موارد قبلی.

هر یافتهٔ جدید باید شامل شناسه، کامیت مبنا، منبع/خط/شیء، سطح قطعیت، اقدام، معیار پذیرش و شواهد پس از اصلاح باشد.


**2026-11-24 amendment:** SRC-004's former four-digit recommendation is superseded by the approved six-digit D-018 amendment. Any old screenshot or visual verdict remains historical until new six-cell OTP UI is re-captured and reviewed.
