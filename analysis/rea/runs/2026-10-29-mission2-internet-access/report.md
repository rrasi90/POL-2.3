# Mission 2 — Internet Access Setup (Cloudflare Quick Tunnels) — نتیجه نهایی

Date: 2026-10-30 · Status: **✅ کامل — سرور، وب و هر دو اپ موبایل روی دیتای واقعی سیم‌کارت تأیید شدند**

## وضعیت نهایی سرویس‌ها (همه زنده و تأییدشده)

| سرویس | محلی | عمومی |
|---|---|---|
| Postgres (`pol_test`) | 127.0.0.1:5432 | — |
| API (FastAPI، seed شده: ۲۴ خرده‌فروش/۳ محصول) | 127.0.0.1:8001 | https://monthly-limit-encountered-cartridges.trycloudflare.com |
| Web (Next.js dev) | 127.0.0.1:3000 | https://resort-jimmy-marks-yes.trycloudflare.com |
| Gateway تک‌مبدأ (پروکسی مسیرمحور) | 127.0.0.1:8080 | همان تونل وب |
| APK خرده‌فروش | `mvp/apps/mobile/dist/retailer/POL-Market.apk` (~21MB) | — |
| APK بنکدار | `mvp/apps/mobile/dist/vendor/POL-Vendor.apk` (~21MB) | — |

## تغییر معماری نسبت به گزارش قبلی: Gateway تک‌مبدأ

**مشکل کشف‌شده:** `trycloudflare.com` در Public Suffix List است (خط 12762 لیست عمومی)؛ دو زیردامنه تونل جدا از نظر مرورگر cross-site هستند و کوکی `pol_refresh` با `SameSite=Lax` هرگز در fetch ارسال نمی‌شود → refresh توکن در هر مرورگری شکست می‌خورد.

**راه‌حل (فقط زیرساخت، بدون تغییر محصول):** `dev_gateway.mjs` (در همین پوشه، run dir) روی پورت 8080 اجرا می‌شود: `/api/*` و `/healthz` را به 8001 و بقیه (شامل websocket) را به 3000 می‌فرستد. فقط **یک** تونل روی 8080. وب با `NEXT_PUBLIC_API_BASE_URL=` (خالی → relative، same-origin) اجرا می‌شود → کوکی first-party، CORS حذف. تونل API جدا برای موبایل باقی است (Bearer token، کوکی لازم ندارد).

تونل‌ها با `--protocol http2` اجرا می‌شوند (اتصال QUIC/UDP این شبکه به edge کلادفلر ناپایدار بود و تونل‌های اول مردند).

## باگ محصول کشف و رفع‌شده (مهم‌ترین یافته)

**باگ:** بعد از هر hard-reload صفحه داشبورد، کاربر به لاگین برگردانده می‌شد — در localhost هم.

**ریشه (با performance tracing مرورگر اثبات شد):** `tryRefresh` در `mvp/apps/web/src/lib/auth/api.ts` بعد از refresh موفق، `setSession({ accessToken })` را بدون `user/role` صدا می‌زد؛ `setSession` در store همیشه `persistProfile(user ?? null, role ?? null)` را اجرا می‌کرد → `pol.auth.profile` در localStorage با null بازنویسی می‌شد → `RequireRole` بلافاصله به `/auth/login` برمی‌گشت (بدون پیام خطا). خود refresh کاملاً سالم بود (کوکی ست و ارسال می‌شد، پاسخ 200).

**فیکس (۲ خط، uncommitted در `mvp/apps/web/src/lib/auth/api.ts`):** `tryRefresh` الان `user` و `role` موجود در استور را به `setSession` پاس می‌دهد تا پروفایل بازنویسی نشود.

**تأیید پس از فیکس (از طریق تونل عمومی):** لاگین با `09123456000`/کد `123456` → ورود به `/retailer` → hard-reload کامل `/retailer/catalog` → نشست حفظ شد، پروفایل سالم، ردیرکت انجام نشد → جستجوی «برنج» محصول واقعی seed شده «برنج دانا ۱۰ کیلوگرمی (POL-E2E-1001)» را با برند/دسته/بسته‌بندی از API برگرداند.

## تأییدهای دیگر

- جریان OTP کامل از طریق تونل: `request-otp` → `verify-otp` → کوکی refresh ست و rotate می‌شود؛ `POST /refresh` با curl و از داخل صفحه 200.
- CORS قبلی (دو تونل جدا) هم تأیید شده بود؛ با معماری تک‌مبدأ دیگر لازم نیست.
- **Playwright regression: 37/42 پاس، 5 شکست — همه پیش‌موجود و مستقل از فیکس** (اثبات: delivery-flow بدون فیکس هم دقیقاً همان‌طور شکست خورد):
  - 4× `visual-capture.spec.ts`: assertionهای QA بصری (مثلاً اصطلاح انگلیسی FMCG در متن فارسی `/retailer`).
  - 1× `delivery-flow.spec.ts`: client-side exception در جریان چندشخصیتی — پیش‌موجود، نیاز به بررسی جداگانه دارد.
  - اسکرین‌شات‌های تغییر یافته توسط تست (`.pol-design/evidence/screenshots/*`) به HEAD برگردانده شدند.
- **بازبینی دوم فیکس (درخواست بازبین):** diff فقط ۸ خط در `tryRefresh` است (هیچ مسیر دیگری دست نخورده). تست‌های مرتبط با نشست/احراز هویت با فیکس مجدداً اجرا شد: **26/26 پاس** (login، basket-sync، status-labels، a11y). هیچ commit انجام نشده — منتظر تأیید.
- **نشان قرمز «1 Issue» در سایت:** خطای واقعی hydration mismatch در React است (Recoverable — «server rendered HTML didn't match the client»)، ناشی از خواندن localStorage در مقداردهی اولیه auth store (شاخه SSR/client) — همان مورد TODO-078 مستند در TODO_LIST.md. پیش‌موجود، ربطی به فیکس refresh یا تونل ندارد؛ در dev-tools Next.js فقط به‌صورت نشان نمایش داده می‌شود و صفحه client-side بازیابی می‌شود. رفع کامل آن تغییر محصول جداگانه می‌خواهد (out of scope این مأموریت).

## APKها

هر دو با QA gate پاس شدند (`pre_apk_qa`: HTTPS، غیر-loopback، برندینگ هر variant) و URL تونل جدید در باینری تأیید شد (2 occurrence، URL قدیمی صفر).

## ✅ تست روی گوشی واقعی (انجام شد — 2026-10-30)

**دستگاه:** Huawei P30 Pro (VOG-L29، arm64، Android) — از طریق USB (ابتدا unauthorized؛ پس از تأیید پنجره مجوز و ری‌استارت adb server → device).

**شبکه:** Wi-Fi گوشی با `svc wifi disable` خاموش شد؛ شبکه پیش‌فرض روی **CELLULAR** رفت و اینترنت سیم‌کارت تأیید شد (ping 8.8.8.8 → ~118ms، VoLTE فعال).

### اپ خریدار (پل بازار / ir.pol.market)
1. `adb install -r dist/retailer/POL-Market.apk` → Success
2. لاگین با `09123456000`: درخواست OTP از طریق سیم‌کارت به تونل رسید (رد پای IP سیم‌کارت `2a02:4540:...` در جدول otp_challenges ثبت شد) → کد `123456` → **status = VERIFIED در DB**
3. داشبورد با داده واقعی API پر شد (دسته‌بندی‌های مواد غذایی/نوشیدنی‌ها/بهداشت)

### اپ بنکدار (پل بنکدار / ir.pol.vendor)
1. `adb install -r dist/vendor/POL-Vendor.apk` → Success؛ اجرای اول با نشست باطلِ نصب قبلی خطای «بارگذاری اطلاعات اصلی بنکدار ناموفق بود» داد → `pm clear ir.pol.vendor` → لاگین تمیز
2. لاگین با `09123457000` → OTP → **status = VERIFIED در DB**
3. داشبورد با داده واقعی: «در جریان: ۳»، «کالاها: ۳» (محصولات seed شده بنکدار) — خطای بارگذاری رفع شد

### نکته عملیاتی
- کد OTP فقط ۱۲۰ ثانیه اعتبار دارد؛ در تست اتوماسیون، هر تأخیر بین «دریافت کد» و «تأیید» باعث خطای «داده‌های واردشده معتبر نیستند» می‌شود (مسیر انقضا attempts را هم افزایش نمی‌دهد). توصیه برای لاگین دستی: کد را فوری وارد کنید.
- Wi-Fi گوشی همچنان خاموش است؛ برای بازگرداندن: `adb shell svc wifi enable`.

## محدودیت‌ها و هشدارها

- URLهای quick-tunnel موقتی و عمومی‌اند؛ داده seed شده تا پایان session عمومی است. اگر host/تونل ری‌استارت شود: URL جدید → آپدیت هر دو `.env.local` → ری‌استارت سرویس‌ها → rebuild هر دو APK.
- اگر تونل با QUIC بالا نیامد: `--protocol http2` اضافه کنید.
- تغییرات uncommitted فعلی: `mvp/apps/web/src/lib/auth/api.ts` (فیکس باگ)، `mvp/apps/mobile/package.json` (پیش‌موجود از قبل)، پوشه این run. هیچ‌چیز commit نشده.
- Backend worker (`scripts.worker_runtime`) فقط در production اجرا می‌شود — برای این تست لازم نیست.
