# دستور اجرای محلی Wave 1 — POL / Cartona handoff
**تاریخ:** 2026-10-27  
**مخزن:** `rrasi90/POL-2.3`  
**شاخهٔ کار:** `fix/pol-wave1-qa-mock-route-docs-20261027`  
**شاخهٔ پایه/هدف PR:** `ui/visual-qa-screen-completion-20261025`  
**PR پیش‌نویس:** https://github.com/rrasi90/POL-2.3/pull/52

این دستور برای ایجنتی است که به محیط محلی واقعی، Python، Node/npm و فایل‌های کامل repository دسترسی دارد. کار اصلی تو اجرای آزمون‌های واقعی، کشف/رفع خطاهای احتمالی در تغییرات Wave 1 و ثبت شواهد است. هیچ PASSای از روی خواندن کد اعلام نکن.

## 1. Sync و حفظ تغییرات

از ریشهٔ repository:

```powershell
git status --short
git branch --show-current
git rev-parse HEAD
git fetch origin --prune
git status -sb
git log -8 --oneline --decorate
```

- اگر تغییرات محلی وجود دارد، قبل از checkout آن‌ها را بازبینی و حفظ کن.
- روی شاخهٔ `fix/pol-wave1-qa-mock-route-docs-20261027` کار کن؛ PR را با شاخهٔ هدف اشتباه نگیر.
- اگر local branch عقب است، فقط در صورت امکان fast-forward امن آن را sync کن.
- `reset --hard`، force-push و پاک‌کردن تغییرات کاربر ممنوع.
- HEAD فعلی را دوباره از GitHub تأیید کن؛ SHA ذخیره‌شده در این سند را حقیقت دائمی فرض نکن.

## 2. هدف تغییرات

این PR شامل این تغییرهای محدود است:

1. حذف ثبت تکراری چهار مسیر مدیریتی از `scripts/api/routes/management.py`؛ canonical handlerها در `scripts/api/routes/admin.py` با `require_roles` باقی مانده‌اند.
2. آزمون جدید `scripts/test_admin_route_registration_uniqueness.py` برای جلوگیری از بازگشت duplicate routes.
3. اصلاح ادعای نادرست اجرای `POST /api/v1/privacy/export`: در router فعلی وجود ندارد؛ قرارداد باید آن را gap/proposed نشان بدهد تا زمانی که endpoint واقعاً پیاده و آزمون شود.
4. mock خرده‌فروش در `mvp/apps/mobile/src/mock/retailerMockTransport.ts` و dispatch بر اساس نقش در `mockTransport.ts`.
5. تست‌های خرده‌فروش در `mvp/apps/mobile/scripts/mock_transport_qa.ts`.
6. مستند اجرا در `analysis/rea/WAVE1_IMPLEMENTATION_NOTES_2026-10-27.md`.

پیش از آزمون، هر فایل را از branch بخوان؛ به توضیحات PR اکتفا نکن.

## 3. آزمون‌های Python — اجرا و رفع واقعی

در PowerShell از repository root:

```powershell
$env:PYTHONPATH = "."
$env:POL_JWT_SECRET = "static-gate-secret-not-for-production"
python scripts/test_admin_route_registration_uniqueness.py
python -m pytest scripts/test_admin_route_registration_uniqueness.py scripts/test_api_boundary_route_inventory.py -q
python scripts/test_api_route_hygiene.py
```

سپس اجرا کن:

```powershell
python -m pytest -q
```

اگر full suite به PostgreSQL یا secrets تستی نیاز دارد، ابتدا راهنمای محیط، `requirements-dev.txt`، `scripts/verify_environment.py` و `scripts/run_verification_suite.py` را بخوان. محیط تست مجزا ایجاد کن؛ دیتابیس توسعه یا تولید را reset نکن.

### بررسی خاص B-01

- تأیید کن `admin.router` چهار مسیر POST/POST/POST/PATCH کانونیکال را دارد.
- تأیید کن `management.admin_router` آن چهار مسیر را ندارد.
- بررسی کن هیچ route دیگری با همان method/path در routerهای mount‌شده تکرار نشده است.
- OpenAPI/runtime inventory و route-hygiene tests باید مطابق شوند.
- اگر رفتار auth در handler canonical ناخواسته تغییر کرده یا یک مسیر مدیریتی بی‌دلیل حذف شده است، اصلاح کن و آزمون مثبت/منفی بنویس.

### بررسی خاص B-02

- `scripts/api/routes/privacy.py` و خروجی واقعی `app.openapi()["paths"]` را بخوان.
- تأیید کن `POST /api/v1/privacy/export` در runtime ثبت نیست.
- تأیید کن این gap در test inventory صریح است و مستندات آن را endpoint آمادهٔ فراخوانی معرفی نمی‌کنند.
- **endpoint را فقط برای سبزکردن آزمون از expected route set حذف نکن.** اگر product/privacy owner تصمیم به پیاده‌سازی داد، یک کار جداگانه شامل schema، auth/ownership, data minimization, audit, contract tests و API docs طراحی و اجرا کن. این PR به‌تنهایی مجوز حذف نیازمندی privacy نیست.

## 4. آزمون‌های Mobile و mock خرده‌فروش

در repository root:

```powershell
Set-Location mvp
npm ci
npm run qa:mock --workspace @pol/mobile
npm run typecheck --workspace @pol/mobile
npm run qa:functional --workspace @pol/mobile
npm run qa:regression --workspace @pol/mobile
```

اگر `npm ci` یا package install به علت محیط، cache یا lockfile شکست خورد، علت دقیق را ثبت و روش امن را امتحان کن؛ `package-lock.json` را بی‌دلیل بازنویسی نکن.

### جریان‌های الزامی retailer mock

تست کن و اگر لازم است اصلاح کن:

1. نقش owner و staff با tokenهای جدا؛ هیچ درخواست خرده‌فروش نباید به fixture یا role فرضی بنکدار route شود.
2. جست‌وجوی کاتالوگ با query فارسی و SKU.
3. basket create → add item → expected version افزایش یابد.
4. ارسال version کهنه باید رد شود.
5. allocation-preview باید تنها برای سبد موجود و باز پاسخ دهد.
6. checkout بدون `Idempotency-Key` یا با allocation کهنه باید رد شود.
7. درخواست checkout تکراری با همان key باید همان group/order را برگرداند و duplicate order نسازد.
8. سفارش جدید باید در list و detail دیده شود؛ items، timeline، delivery، invoices و support shapeها با مصرف‌کنندگان UI هماهنگ باشند.
9. `resetMockState()` باید state هر دو نقش را reset کند؛ ترتیب اجرا نباید نتایج testهای قبلی را آلوده کند.
10. نگاشت progress stepper در `orderProgressStage()` را بررسی کن: `SUBMITTED → 1`، `ACCEPTED/PARTIALLY_ACCEPTED/PREPARING → 2`، `READY/DISPATCHED → 3` و فقط `DELIVERED → 4`. `ARRIVED` متعلق به `delivery_status` است و نباید به‌عنوان `order_status` به مرحلهٔ نهایی تبدیل شود.
11. اصلاح‌های واژه‌گزینی فارسی را در `RetailerMobileScreen.tsx`، `VendorMobileScreen.tsx` و `LoginScreen.tsx` تأیید کن؛ این بررسی ایستا جای screenshot یا تست واقعی RTL را نمی‌گیرد.
10. vendor mock فعلی همچنان green بماند؛ testهای vendor را حذف یا ضعیف نکن.

Mock یک test double است، نه اثبات صحت backend. اگر shape یا semantics با router واقعی فرق دارد، تغییر mock را به قرارداد واقعی نزدیک کن یا drift را مستند کن. منطق تجاری جدید و خارج از قرارداد نساز.

## 5. بررسی Android/config فقط تا حدی که در این PR تغییر کرده

این PR عمداً variant یا build script را تغییر نمی‌دهد. بااین‌حال، پس از سبز شدن تست‌ها اطمینان بگیر:
- `mvp/apps/mobile/package.json` و lockfile دست‌نخورده مانده‌اند.
- app config و build variantها به‌طور تصادفی تغییر نکرده‌اند.
- هیچ `DRIVER` role یا migration جدید به این PR وارد نشده است.

ساخت APK جدید برای این موج ضروری نیست مگر pre-APK gate پروژه آن را لازم بداند. runtime screenshot یا runtime parity را ادعا نکن.

## 6. بازبینی کیفیت و scope

قبل از ثبت نتیجه:

```powershell
git diff --check
git status --short
git diff --stat
git diff -- scripts/api/routes/management.py scripts/test_admin_route_registration_uniqueness.py scripts/test_api_boundary_route_inventory.py
git diff -- mvp/apps/mobile/src/mock/mockTransport.ts mvp/apps/mobile/src/mock/retailerMockTransport.ts mvp/apps/mobile/scripts/mock_transport_qa.ts
git diff -- 06_PRODUCT/API_Contracts.md mvp/MVP_API_MAP.md
```

بررسی کن:
- فقط فایل‌های مرتبط با Wave 1 تغییر کرده باشند؛
- هیچ secret، APK یا corpus خام اضافه نشده باشد؛
- doc ادعای runtime نکند؛
- tests واقعی اجرا شده باشند، با خروجی، exit code و timestamp؛
- هیچ تستی صرفاً برای pass شدن حذف یا کم‌قید نشده باشد.

## 7. ثبت evidence و ادامهٔ PR

در `analysis/rea/WAVE1_IMPLEMENTATION_NOTES_2026-10-27.md` یک بخش **Local Verification Results** اضافه کن و برای هر فرمان ثبت کن:

`command`, `environment`, `start/end time`, `exit code`, `passed/failed/skipped`, `evidence path`, `failure root cause`, `fix commit`.

- اگر تست fail شد، ریشه را پیدا کن، اصلاح کن و تست مربوط را دوباره اجرا کن؛ سپس suite را کامل اجرا کن.
- اگر نیازمند سرویس محلی ناموجود بود، blocker را با خروجی واقعی بنویس و تست‌های مستقل دیگر را ادامه بده.
- تغییرات را به همین branch commit و push کن؛ force-push ممنوع.
- PR #52 را merge نکن. در صورت دسترسی، نتیجهٔ اجرای تست‌ها را در PR comment/body ثبت کن و draft را تا زمان بازبینی باز نگه دار.
- اگر مجبور به ایجاد تغییر اضافی شدی، علت، آزمون و فایل دقیق را در Notes ثبت کن.

## Definition of done

این کار زمانی تکمیل است که:
- تمام آزمون‌های قابل اجرا واقعاً اجرا شده باشند؛
- همهٔ regressionها رفع یا به‌عنوان blocker مستند شده باشند؛
- retailer mock و vendor mock هر دو coverage واقعی داشته باشند؛
- route duplicate regression به‌صورت خودکار در workflow موجود اجرا شود؛
- `privacy/export` دقیقاً به‌عنوان gap یا endpoint پیاده‌شده و آزمون‌شده وضعیت داشته باشد؛
- PR diff بررسی شده، branch همگام است، و شواهد نتایج در گیت‌هاب قابل مشاهده‌اند.

تا آن زمان، وضعیت `IMPLEMENTED_PENDING_LOCAL_VERIFICATION` است؛ آن را PASS اعلام نکن.
