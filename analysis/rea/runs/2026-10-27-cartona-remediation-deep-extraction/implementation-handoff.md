# Implementation Handoff — سه محصول پل (Run 2026-10-27)

این سند برای شروع مستقل فاز پیاده‌سازی نوشته شده است. ایجنت توسعه باید بدون تکرار این تحقیق بتواند از همین‌جا کار را شروع کند. مرجع کامل شواهد: `pol-repository-reality-audit.md` (ممیزی کد)، `pol-api-adaptation-matrix.csv` (مسیر هر قابلیت)، `mvp-priority-backlog.csv` (کارها)، `driver-app-readiness.md` (راننده).

## وضعیت واقعی سه اپ (از ممیزی کد، commit e68d2e45)

| اپ | وضعیت فعلی | شواهد |
|---|---|---|
| پل بازار (خرده‌فروش، `ir.pol.market`) | **واقعی و build می‌شود** — 879 خط، سبد+checkout+سفارش‌ها+invoices، API زنده با Idempotency-Key | RetailerMobileScreen.tsx؛ build_android_variant.mjs [CODE_VERIFIED] |
| پل بنکدار (`ir.pol.vendor`) | **واقعی و کامل‌ترین** — 1536 خط، ~40 فراخوانی API: سفارش‌ها، پذیرش/رد/پارسیال، کاتالوگ، موجودی روزانه، اسکن پیوسته، فاکتور/تسویه، پرسنل/دسترسی‌ها | VendorMobileScreen.tsx [CODE_VERIFIED] |
| پل راننده | **وجود ندارد** — نه نقش DRIVER، نه session، نه صفحه. فقط دیتای راننده در dispatch + delivery stages | permissions.py:38-118؛ migrations/001:19-22 [NOT_FOUND] |

## همین الان قابل استفاده (REUSE_AS_IS / DONE)

- پذیرش/رد سفارش با permission engine و deny-list کارمندی
- پذیرش جزئی دوطرفه (partial-acceptance-proposals) + timeout کارمند ۲ ساعته
- سبد + allocation-preview + checkout idempotent
- تحویل ۶ مرحله‌ای + OTP شش‌رقمی + POD + exceptions
- returns/disputes/refunds/settlements کامل در بک‌اند
- مسیریابی عمدهٔ API (~۱۲۰ endpoint) با تست‌های HTTP (۸۷ فایل test)

## فقط ترجمه/تنظیمات (LOCALIZATION_ONLY / CONFIG_ONLY)

- RTL/فونت فارسی موجود است — فقط ممیزی کیفیت (B-08): رفع نشت متن انگلیسی، screenshot contract
- Deep links (R-22): اضافه‌کردن intentFilters به app.json + assetlinks

## Adapter/UI کوچک (CLIENT_ADAPTER / SMALL_UI_DELTA)

- B-03: mock خرده‌فروش (الان mock فقط vendor است — خرده‌فروش در mock اجرا نمی‌شود)
- B-05: دکمهٔ reorder روی سفارش تحویل‌شده
- B-06: stepper مراحل تحویل در OrderDetail
- B-01/B-02: حذف routeهای admin تکراری + اصلاح اسناد

## نیاز به API/schema/migration (BACKEND_DOMAIN_CHANGE / DB_MIGRATION_REQUIRED)

- B-04: سرویس‌اریا gate (مسیر P1)
- B-07: ثبت device token برای push
- **B-09/B-10/B-12 (اگر اپ راننده در pilot باشد):** نقش DRIVER + مالکیت transitionها + variant سوم — تمام جزئیات در driver-app-readiness.md؛ گرهٔ تصمیم: مدل org راننده (§33.7 پلن) باید product owner امضا کند
- B-11: idempotency برای تحویل (الگو از checkout migration 061)

## شکاف‌های P0 (به‌ترتیب اجرا)

1. **B-01** حذف تکرار routeهای admin (ریسک روتینگ) — XS
2. **B-02** تطبیق اسناد با router (شامل حذف/پیاده‌سازی /privacy/export) — S
3. **B-03** mock خرده‌فروش — S
4. **(شرطی) B-09→B-12** زیرساخت راننده: نقش → مالکیت → idempotency → variant سوم — L مجموع؛ منوط به تصمیم D-01
5. **B-08** پارس RTL — S

هر P0 معیار پذیرش + تست منفی مشخص در backlog دارد.

## ترتیب پیشنهادی work items

هفتهٔ ۱: B-01، B-02، B-03 (بدون هیچ تصمیم محصولی — همان روز شروع می‌شود)
موازی: تصمیم D-01 (مدل org راننده) توسط product owner
هفتهٔ ۲: B-08 + B-05 + B-06 (چهرهٔ خرده‌فروش)
هفتهٔ ۳+: در صورت تأیید راننده: B-09 → B-10 → B-11 → B-12 با تست‌های isolation
P2/Research: wallet/BNPL (B-13)، promotions (B-14)، سرویس‌اریا (B-04 پس از تصمیم پوشش)، deep links (R-22)، integrity (R-23)

## rollback / انتشار امن

- هر migration با فایل down/بازگشتی در migration_runner؛ نقش DRIVER روی invariant trigger (003) اثر می‌گذارد — migration باید trigger را هم به‌روز کند
- variant سوم: pipeline فعلی index.ts را موقتاً بازنویسی می‌کند و در finally برمی‌گرداند — با سه variant این الگو باید به env-switch تمیز تبدیل شود (یادداشت در build script)
- feature flags: از EXPO_PUBLIC_DATA_MODE الگو بگیر؛ برای DRIVER روی backend هم fail-closed بمان

## موارد نیازمند تصمیم کسب‌وکار / مصاحبه

- مدل org راننده (کاربر OPERATOR؟ بنکدار شخص ثالث؟ org جدید CARRIER؟)
- wallet/BNPL: آیا در pilot اهواز اصلاً هست؟ (رفتار Cartona = فین‌تک شریک AMAN — در ایران نیاز به ریل پرداخت داخلی دارد)
- promotions/favorites: اولویت پس از مصاحبهٔ بنکداران
- سرویس‌اریا: شهرهای pilot و فرایند تأیید دستی تا ساخت gate خودکار
