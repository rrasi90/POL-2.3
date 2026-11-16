# صفحه‌ها و حالت‌های مفقود یا نیازمند تأیید

## اصل تعیین فقدان

نبودن تصویر مستقل در گالری ۱۰ صفحه‌ای، به‌تنهایی اثبات نمی‌کند که یک صفحه در محصول غایب است. وجود کد یا عنوان در ماتریس نیز اثبات نمی‌کند که مسیر runtime قابل‌دسترسی و از نظر بصری کامل است.

هر مورد یکی از این وضعیت‌ها را دریافت کند:
- IMPLEMENTED_AND_REACHABLE: مسیر جاری قابل‌دسترسی و شاهد ثبت شده
- IMPLEMENTED_NOT_VISUALLY_VERIFIED: کد موجود، رندر تأیید نشده
- PARTIAL: بخشی از صفحه یا حالت وجود ندارد
- MISSING_CANONICAL_REQUIREMENT: نیاز کانونی تأیید شده ولی طراحی/پیاده‌سازی غایب است
- PRODUCT_DECISION_REQUIRED: نیاز/رفتار مشخص نشده
- ENVIRONMENT_BLOCKED: امکان اثبات فعلی وجود ندارد
- NOT_APPLICABLE: با منبع و دلیل روشن

## موارد اولویت‌دار برای تأیید

| شناسه | مورد | دلیل بررسی | مدرک لازم |
|---|---|---|---|
| GAP-001 | متن کد چهاررقمی و حالات OTP | JSON متناقض است ولی D-018 و کد چهاررقمی‌اند | رندر OTP، invalid/loading/expiry/resend |
| GAP-002 | مسیر پشتیبانی موبایل | inventory قدیمی می‌گوید wiring باید runtime تأیید شود | مسیر از ناوبری تا Support و برگشت |
| GAP-003 | گروه سفارش والد در موبایل | D-022 سطح والد/فرزند می‌خواهد؛ mapping موبایل بررسی شود | کلیک از سفارش ثبت‌شده تا گروه و سفارش‌های فرزند |
| GAP-004 | ویترین بنکدار و برگشت | کد Retailer آن را دارد؛ state coverage لازم است | default/loaded/empty/error/back |
| GAP-005 | حالت‌های Night برای Retailer | وجود token/context کافی نیست | screenshot واقعی Night برای golden surfaces |
| GAP-006 | بارکد/اسکن native | endpoint/adapter و دوربین native جدا هستند | مجوز، denied/cancel/result؛ در نبود camera، BLOCKED |
| GAP-007 | فاکتور/فعالیت مالی | R-16 فعال است اما نباید کیف پول شود | فهرست واقعی invoice/empty/error و جزئیات موجود |
| GAP-008 | اعلان‌ها/ترجیحات | کد مشترک وجود دارد؛ پوشش بصری لازم است | هر حالت و نتیجهٔ ذخیره در Light/Night |
| GAP-009 | نشست سرد/بازیابی | VQA-M-060 آن را جدا تعریف می‌کند | بستن/بازکردن و وضعیت نشست بدون ادعای mock |
| GAP-010 | صفحه‌های مستقل خانه/دسته/جست‌وجو | Doory تصویر جدا دارد، اپ ممکن است از tab/state مشترک استفاده کند | mapping artifact به route/state واقعی؛ صفحهٔ مستقل را تحمیل نکن |

## حالت‌هایی برای ردیابی بر اساس رفتار واقعی

- Auth: PHONE_ENTRY, PHONE_ERROR, OTP_ENTRY, OTP_ERROR, LOADING.
- Catalog: DEFAULT, LOADING, LOADED, EMPTY, ERROR, SEARCH، و FILTER/SORT فقط اگر در محصول وجود دارد.
- Vendor search/storefront: DEFAULT, LOADED, EMPTY, ERROR.
- Basket: EMPTY, LOADED, MUTATION, ERROR و تغییر/حذف کالا.
- Allocation: LOADING, LOADED, ERROR, PARTIAL مطابق قرارداد.
- Checkout: READY/CONFIRMATION/ERROR و جلوگیری از ارسال تکراری.
- Order: LOADED, TIMELINE, PARTIAL_ACCEPTANCE, DELIVERY, HANDOFF, RETURNS, DISPUTE.
- Support: EMPTY, LOADED, FORM, SEND, ERROR.
- Finance: EMPTY, LOADED, ERROR و جزئیات سند فقط اگر موجود است.
- Account: PROFILE, EDIT, SAVE, ERROR, LOGOUT.
- Notifications/preferences: EMPTY, LOADED, READ/UNREAD, SAVE, ERROR.
- Theme: هر مورد کاربردی در LIGHT و NIGHT.
- Global: empty, error, loading, disabled, long-content و retry در صورت پشتیبانی.

## مواردی که نباید خودکار اضافه شوند

- کیف پول با موجودی ذخیره‌شده؛ D-021 آن را در MVP رد می‌کند.
- خرید اعتباری/BNPL؛ فعال‌بودنش را فرض نکن.
- اپ رانندهٔ کامل؛ D-023 آن را لازم نمی‌داند.
- نوشتن/ویرایش ویترین بنکدار بدون تصمیم و مجوز canonical.
- هوش مصنوعی/توصیه‌گر به‌عنوان قابلیت الزامی MVP.
- تبلیغات، امانی‌سازی وجوه یا تضمین تحویل بدون تصمیم معتبر.

## روش بستن شکاف

برای هر مورد:
1. منبع نیاز و شناسهٔ canonical را اعلام کن.
2. مسیر/کد موجود و شرط نقش را بررسی کن.
3. در صورت وجود runtime، مسیر واقعی را امتحان و تصویر/لاگ بگیر.
4. در نبود runtime، وضعیت ENVIRONMENT_BLOCKED باقی بماند.
5. فقط وقتی نیاز canonical و فقدان هر دو ثابت‌اند، طراحی/پیاده‌سازی جدید پیشنهاد شود.
