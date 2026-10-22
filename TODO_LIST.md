# TODO LIST — POL-2.3

**آخرین بازبینی زندهٔ GitHub:** 2026-10-22  
**مبنای `main`:** `d9505cfa62c953546b479f4ca8aec1997ca57fbc` (در این بازبینی)  
**مخزن هدف:** `rrasi90/POL-2.3`  
**شاخهٔ ویرایش این فهرست:** `agent/todo-061-source-baseline-20261022` — [PR #41](https://github.com/rrasi90/POL-2.3/pull/41)، Draft و ادغام‌نشده  
**شاخهٔ تغییرات Motion/CI:** `agent/mobile-motion-port-20261022` — [PR #40](https://github.com/rrasi90/POL-2.3/pull/40)، Draft و ادغام‌نشده  
**SHA آخرین CI کامل PR #40:** `1c793b5363efda1fd6db0c32bf098472a6e9a6f9`  
**وضعیت شواهد روی همان SHA:** Static PASS؛ Browser E2E `17/17`؛ Mobile functional `28/28` و regression `38/38`؛ backend/schema `663/663`. این نتیجه فقط به همان SHA مربوط است و به معنی merge، تست دستگاه، live SMS، domain/TLS یا آمادگی release نیست.  
**وضعیت QA APK:** گیت `TODO-084` در آخرین run، `82/82` پیش‌نیاز را تأییدنشده گزارش کرد؛ هر چهار job ساخت APK عمداً Skip شدند. هیچ APK جدیدی برای SHA بالا ادعا نمی‌شود.

## قواعد استفاده از این فهرست

- `[ ] OPEN` یعنی کار انجام‌نشده یا تأییدنشده و باید پیگیری شود.
- `[ ] REVALIDATE` یعنی در سند قدیمی ثبت شده، اما نباید بدون تست روی SHA فعلی باگ فعال فرض شود.
- `[ ] BLOCKED_EXTERNAL` یعنی بستن مورد به دسترسی، کلید واقعی، تأیید بیرونی یا اقدام عملیاتی نیاز دارد.
- شواهد قبلی مانند 663/663 فقط به SHA و run ثبت‌شدهٔ خود مربوط‌اند؛ برای هر تغییر کد یا workflow، نتیجهٔ CI باید با SHA دقیق همان تغییر تطبیق داده شود. PASS روی PR باز نیز به‌تنهایی به معنی ادغام، آزمون دستگاه یا آمادگی release نیست.
- هیچ موردی را فقط با تغییر وضعیت فایل مستندات نبندید؛ برای موارد فنی، شواهد تست و SHA را ثبت کنید.

## پروتکل اجباری اجرای زنجیره‌ای و همکاری ایجنت‌ها

این بخش برای **تمام ایجنت‌ها، توسعه‌دهندگان و ابزارهای خودکار** الزامی است. این فهرست فقط مجموعه‌ای از چک‌باکس‌ها نیست؛ باید زنجیرهٔ قابل‌ردیابیِ «وضعیت فعلی → کار → تست → مدرک → تحویل به نفر/ایجنت بعدی» را حفظ کند.

### 1) زنجیرهٔ اجرا و وابستگی‌ها

1. هر کار باید شناسهٔ یکتا داشته باشد (`TODO-001` و به‌ترتیب). شناسه پس از ایجاد عوض یا برای کار دیگری استفاده نشود.
2. هر کار باید `Blocked by / Depends on` داشته باشد. کارهای وابسته فقط بعد از بسته‌شدن و تأیید پیش‌نیازها اجرا شوند؛ ترتیب را از روی وابستگی‌ها تعیین کنید، نه از روی ترتیب سطرهای فایل.
3. مسیر پیش‌فرض: **بازخوانی منبع حقیقت و وضعیت → بازتولید مشکل → اصلاح حداقلی → تست واحد/قرارداد → تست رگرسیون و امنیت → CI → استیجینگ → تست دستگاه/محیط واقعی در صورت نیاز → مستندسازی و تحویل**. مرحله‌ای را صرفاً به‌دلیل کمبود وقت سبز فرض نکنید.
4. اجرای موازی فقط وقتی مجاز است که مالک‌ها ثابت کرده باشند کارها روی فایل‌ها، قراردادها، schema، API یا state machine مشترک هم‌پوشانی ندارند. در غیر این صورت کارها زنجیره‌ای اجرا شوند. برای کار موازی یک نفر مسئول یکپارچه‌سازی معرفی شود.
5. اگر پیش‌نیاز مسدود است، کار وابسته باید `BLOCKED_INTERNAL` یا `BLOCKED_EXTERNAL` شود و علت/مالک/اقدام رفع مانع ثبت شود؛ با دور زدن پیش‌نیاز وضعیت را جلو نبرید.

### 2) مالکیت و هماهنگی پیش از شروع

1. هر TODO دقیقاً **یک مالک پاسخ‌گو** دارد. سایر ایجنت‌ها می‌توانند همکار باشند، اما مالک نهاییِ نتیجه و handoff مشخص است.
2. ایجنت ورودی باید گزارش آخرین ایجنت/توسعه‌دهندهٔ آن بخش را بخواند، branch/commit و وضعیت واقعی فایل‌ها را بررسی کند و سپس با همان مالک یا ایجنت قبلی هماهنگ شود. کار انجام‌شده را از ابتدا تکرار نکند مگر اینکه مدرک نشان دهد نتیجه نامعتبر یا stale است.
3. پیش از ویرایش، ایجنت باید این موارد را ثبت کند: TODO-ID، مالک، ایجنت قبلی/وابستگی، repository، branch/worktree، SHA شروع، فایل‌ها/ماژول‌های مورد انتظار و معیار پذیرش.
4. دو ایجنت هم‌زمان یک فایل یا یک ماژول مشترک را ویرایش نکنند مگر اینکه مرز کار و روش ادغام از قبل روشن شده باشد. قبل از تغییر، وضعیت تغییرات محلی و commitهای تازه را بررسی کنید تا کار دیگری overwrite نشود.
5. همهٔ ایجنت‌ها از منبع حقیقت کانونیکال، قراردادهای فعلی، `DECISION_REGISTER` و وضعیت واقعی Git پیروی کنند. دستور یا ادعای یک ایجنت، بدون مدرک، جای کد، تست، تصمیم رسمی یا وضعیت GitHub را نمی‌گیرد.

### 3) گزارش اجباری هر ایجنت: «دقیقاً چه کردی و الان کجایی؟»

**پیش از توقف، تغییر ایجنت، handoff یا پایان هر نشست، گزارش باید در بخش «Agent Handoff Journal» انتهای همین فایل ثبت شود.** گزارش کلی مثل «در حال انجام»، «تقریباً تمام شد» یا «همه‌چیز سبز است» کافی نیست.

هر گزارش باید تمام موارد زیر را دقیقاً پوشش دهد:

- **هویت و زمان:** نام/شناسهٔ ایجنت یا عامل، زمان با timezone و TODO-IDهای درگیر.
- **مبدأ و محل کار:** repo، branch، worktree/directory، SHA شروع و SHA پایانی؛ اگر روی PR است شماره و URL آن؛ اگر artifact ساخته شده مسیر دقیق و لینک آن.
- **کار واقعاً انجام‌شده:** فایل و مسیر دقیق، تغییر رفتاری/فنی دقیق، بخش یا تابع/route/migration/test درگیر. کار برنامه‌ریزی‌شده را به‌عنوان کار انجام‌شده ننویسید.
- **کار ایجنت قبلی:** چه چیزی را از نفر/ایجنت قبلی تحویل گرفتید، چه چیزی را بررسی و تأیید کردید، چه چیزی را اصلاح/رد کردید و بر اساس کدام شواهد.
- **تست و مدرک:** command کامل، محیط/نسخهٔ DB یا دستگاه، تعداد PASS/FAIL/SKIP، exit code، لینک CI، log یا artifact. صرفاً «تست شد» قابل قبول نیست.
- **وضعیت باقیمانده:** چه چیزی باز است، چه چیزی فقط پیاده شده ولی تست نشده، چه چیزی fail کرده و آیا تغییر commit/push شده است.
- **مانع و مالک بعدی:** مانع دقیق، فرد/ایجنت یا تیمی که باید آن را رفع کند، اقدام بعدی مشخص، TODO-ID وابسته و معیار شروع ایجنت بعدی.
- **وضعیت workspace:** تغییرات commitنشده، فایل‌های untracked، هرگونه تغییر خارج از scope، و اینکه branch/worktree آمادهٔ تحویل است یا نه.

گزارش قبلی را بازنویسی یا حذف نکنید؛ برای اصلاح گزارش قدیمی، ورودی جدیدی با ارجاع به ورودی قبلی ثبت کنید تا زنجیرهٔ تصمیم و شواهد از بین نرود.

### 4) قالب اجباری ثبت گزارش و handoff

هر ایجنت این قالب را کپی و تکمیل کند؛ فیلد نامشخص باید صریحاً `UNKNOWN`/`NOT VERIFIED` باشد، نه حدس:

```text
### [YYYY-MM-DD HH:MM TZ] Agent: <agent-id> — TODO-###
- State: IN_PROGRESS | BLOCKED_INTERNAL | BLOCKED_EXTERNAL | DONE_CODE_UNVERIFIED | DONE_VERIFIED
- Incoming handoff: <agent + journal entry + summary of work already done>
- Repository / branch / worktree: <exact location>
- Start SHA -> End SHA: <sha> -> <sha or NOT COMMITTED>
- Files and symbols changed: <exact paths + functions/routes/tests>
- Work completed in this session: <concrete facts only>
- Work inherited from previous agent and verified: <details + evidence>
- Commands/tests/environment: <full commands, DB/device/runtime versions>
- Results: <PASS/FAIL/SKIP, exit code, CI/log/artifact links>
- Not done / known risks: <precise list>
- Blocker and responsible owner: <exact blocker, who must act, what is needed>
- Next TODO-ID / next agent: <ID, agent/owner, prerequisite, exact first action>
- Working tree: <clean/dirty + uncommitted/untracked files>
- Handoff accepted by: <next agent or PENDING>
```

### 5) تعریف وضعیت‌ها و قانون بستن کار

- `OPEN`: هنوز شروع نشده یا نتیجه‌ای ندارد.
- `IN_PROGRESS`: مالک و قدم بعد مشخص است و کار فعالانه در جریان است.
- `BLOCKED_INTERNAL`: مانع داخل کد/مخزن/محیط تحت کنترل تیم وجود دارد.
- `BLOCKED_EXECUTION_ENVIRONMENT`: ایجنت فعلی checkout یا مجوز/اتصال لازم برای اجرای کار را ندارد؛ این برچسب به‌خودی‌خود به معنی باگ در سورس پروژه نیست و باید با handoff به یک محیط دارای دسترسی رفع شود.
- `BLOCKED_EXTERNAL`: دسترسی، credential، provider، دستگاه یا اقدام شخص/تیم بیرونی لازم است؛ secret واقعی را در این فایل ننویسید.
- `OPEN_DECISION`: تصمیم رسمی محصولی، مالی، حقوقی یا امنیتی لازم است؛ ایجنت حق اختراع تصمیم را ندارد.
- `REVALIDATE`: فقط از سند/گزارش قدیمی شناخته شده و باید روی SHA جاری دوباره بررسی شود.
- `DONE_CODE_UNVERIFIED`: کد تغییر کرده ولی آزمون/شواهد کافی موجود نیست؛ کار بسته محسوب نمی‌شود.
- `DONE_VERIFIED`: معیار پذیرش پاس شده، مدرک قابل‌دسترسی ثبت شده و SHA مدرک با SHA مورد ادعا یکی است.
- `OUT_OF_SCOPE`: فقط با ارجاع به تصمیم یا محدودهٔ canonical؛ مورد را بی‌صدا حذف نکنید.

**قانون چک‌باکس:** فقط `DONE_VERIFIED` اجازه دارد با `[x]` نمایش داده شود. `DONE_CODE_UNVERIFIED`، تست محلی بدون CI لازم، mock، screenshot بدون runtime واقعی، یا PASS مربوط به SHA قدیمی مجوز بستن نیست. در صورت شکست، وضعیت، علت و اقدام بعدی را ثبت کنید و چک‌باکس را باز نگه دارید.

### 6) کنترل تغییرات و ایمنی مخزن

1. پیش از تغییر، SHA، branch، وضعیت workspace و مالکیت فایل‌ها را بررسی کنید؛ پس از کار، همان‌ها را دوباره ثبت کنید.
2. یک تغییر باید کوچک، محدود به scope و دارای تست regression مرتبط باشد. تغییر API، schema، تصمیم کسب‌وکار یا state machine بدون مدرک و تصمیم معتبر انجام نشود.
3. هیچ ایجنتی حق ندارد secret/token/password را در TODO، commit، screenshot یا log قرار دهد.
4. force-push، reset مخرب، حذف artifact/گزارش تاریخی، تغییر production یا merge کردن PR بدون مجوز صریح و الزامات پروژه ممنوع است.
5. موفقیت محلی، CI، staging و production چهار نوع evidence متفاوت‌اند؛ در گزارش مشخص کنید دقیقاً کدام سطح بررسی شده است.
6. پس از هر کار، TODO مربوط و handoff log را همان نشست به‌روزرسانی کنید. گزارش را به «آخر کار» موکول نکنید.

### 7) گیت اجباری قبل از ساخت اپلیکیشن و گیت جداگانهٔ قبل از انتشار

ساخت اپلیکیشن باید مرحله‌ای باشد؛ «Build سبز شد» به‌معنی سالم‌بودن سیستم نیست. ترتیب اجباری:

1. **Pre-build qualification:** تست‌های کد، وابستگی‌ها، پایگاه داده، API/قراردادها، امنیت، منطق کسب‌وکار، backend، web، پیکربندی Expo و export جاوااسکریپت؛ پیش از ساخت APK/AAB.
2. **QA-only build:** فقط پس از عبور از Pre-build qualification، APK آزمایشی برای نصب و آزمایش runtime/device ساخته شود. این خروجی انتشار نهایی نیست و امضای انتشار/انتقال به کاربران از آن نتیجه‌گیری نمی‌شود.
3. **Post-build device verification:** نصب روی Emulator یا دستگاه واقعی و اجرای login، navigation، API، RTL، permission، offline/weak-network، lifecycle، media و تمام stateهای ضروری. این دسته طبیعتاً به QA build نیاز دارد و باید قبل از release build انجام شود.
4. **Release build:** فقط پس از رفع یافته‌های QA، اجرای مجدد تست‌های مرتبط روی SHA جدید و تکمیل شواهد، APK/AAB انتشار ساخته و hash/artifact آن ثبت شود. هر تغییری بعد از گیت، گیت مربوط را باطل می‌کند و نیازمند اجرای مجدد است.

هیچ ایجنتی حق ندارد تست device را با unit test یا export موفق جایگزین کند؛ همچنین نبود device، کلید واقعی یا provider باید `BLOCKED_EXTERNAL` بماند و به‌عنوان PASS ثبت نشود. تست‌های live با دادهٔ ساختگی، mock و محیط production باید از هم جدا باشند.

### 8) معیار پذیرش handoff

ایجنت بعدی باید ورودی قبلی را بخواند، وضعیت Git و artifact را مستقل بررسی کند و سپس `Handoff accepted by` را تکمیل کند. اگر SHA/تست/فایل با گزارش قبلی نمی‌خواند، کار را کورکورانه ادامه ندهد؛ تناقض را به‌عنوان blocker/revalidation ثبت کند. **مسئولیت فقط با ارسال پیام منتقل نمی‌شود؛ تحویل زمانی کامل است که محل کد، شواهد، وضعیت باقی‌مانده و قدم بعدی روشن و قابل‌بازتولید باشند.**

---

## Agent Handoff Journal — گزارش ترتیبی ایجنت‌ها

این بخش دفتر وقایع append-only همین TODO است. هر ایجنت پس از شروع/تغییر معنی‌دار/پایان کار یک ورودی طبق قالب بالا اضافه کند. ورودی‌های قدیمی حذف یا بازنویسی نشوند. برای ثبت پیشرفت تازه، ابتدا آخرین SHA و آخرین ورودی مرتبط را بخوانید.

---

## نقشهٔ زنجیره و ترتیب اجرای TODOها — نسخهٔ اجرایی 2026-10-22

این نقشه بر ترتیب ظاهری شناسه‌ها اولویت دارد. بعضی کارها مستقل‌اند و می‌توانند موازی اجرا شوند؛ به‌ویژه تست‌های mock/local و کارهای تجاری نباید منتظر credential پیامک واقعی بمانند. وابستگی‌های پایین، ترتیب مرجع handoff را مشخص می‌کنند.

| مرحله | TODOها | هدف و معیار خروج |
|---|---|---|
| 0 — هم‌ترازی مبنا و اسناد مرجع | `TODO-061`، `TODO-049…053`، یافته‌های منبع حقیقت | SHA، PRها، working tree محلی و اسناد canonical مشخص شوند. اختلاف migration head `048` در سند منبع حقیقت در برابر `071/076` در شواهد دیگر، مسیر مفقود `POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md` و ارجاع‌های شاخهٔ قدیمی در API map باید با tree واقعی بررسی و رفع/توضیح داده شوند. این‌ها نباید بی‌صدا حدس زده شوند. |
| 1 — محیط بازتولیدپذیر و سلامت هسته | `TODO-062…068` | نصب از lockfile، جداسازی env، lint/typecheck، migration صفر تا head، transaction/integrity و full verification روی PostgreSQL 18؛ خروجی همان SHA ذخیره شود. |
| 2 — API، امنیت و منطق backend | `TODO-069…077`، `TODO-131…135`، `TODO-147` | route/contract inventory، OTP/session، tenant/RBAC، state machine، idempotency/concurrency، file/media، outbox/worker، abuse/rate-limit، fuzz/property-based، contract drift و load test در محیط ایزوله. OTP باید با provider تستی/outbox بررسی شود؛ SMS زنده شرط اجرای این مرحله نیست. |
| 3 — وب، journeys و پوشش feature | `TODO-078…080`، `TODO-085…136`، `TODO-144…145`، همچنین معیارهای high-level در `TODO-012…017` | Bug reproduction و regression، Feature × Journey × Test matrix، Retailer/Vendor/Ops/Field، loading/empty/error/success، browser E2E، fault recovery، accessibility وب و Core Web Vitals. تست‌های 12–17 باید با evidence زیرمجموعه‌های دقیق این بخش trace شوند؛ وجود تست به‌تنهایی کافی نیست. |
| 4 — Mobile و بررسی ایستای پیش از APK | `TODO-081…083`، `TODO-138`، بخش ایستای `TODO-139`، `TODO-144`، `TODO-145`، `TODO-149` | typecheck، Expo config هر دو variant، export/assets، Android manifest/permission/package/privacy، dependency/license/security scan و provenance ایستای build. در production هیچ HTTP/cleartext یا test credentialی را صرفاً برای عبور QA مجاز نکنید. |
| 5 — گیت رسمی پیش‌ساخت | `TODO-084` | آخرین گیت قبل از ساخت QA APK؛ فقط پس از تکمیل تمام subsetهای PRE-BUILD تعریف‌شده در خود TODO-084، گزارش با SHA واحد، بدون P0/P1 unresolved و با شواهد قابل بازبینی. این گیت bypass نمی‌شود. |
| 6 — QA APK و آزمون runtime | `TODO-009`، `TODO-018…024`، `TODO-137`، `TODO-140…143`، `TODO-146`، `TODO-151…152` | ساخت artifact QA برای Retailer و Vendor پس از TODO-084؛ سپس نصب، package/signature/hash، flow واقعی دستگاه، Motion lifecycle، تمام screen/stateها، RTL، permission، TalkBack، privacy، upgrade/resume و mobile E2E. نبود emulator یا دستگاه واقعی blocker است، نه PASS. |
| 7 — استیجینگ دامنه‌ندار و سرویس‌های زیرساختی | `TODO-029…033`، `TODO-027…028`، `TODO-148`؛ `TODO-025` به‌صورت موازی | VPS/staging محدود با IP/private access و env مستقل؛ object storage واقعی و امنیت فایل؛ smoke استیجینگ با test OTP/outbox؛ backup/restore، runbook و monitoring. **این مرحله به دامنهٔ عمومی یا SMS واقعی وابسته نیست.** هر محدودیت شبکهٔ Android باید با محیط QA محدود/تست adapter حل شود، نه با شل‌کردن سراسری امنیت production. |
| 8 — تصمیم‌های محصول/مالی/عملیاتی و پایلوت | `TODO-034…048`، `TODO-035…040`، `TODO-059…060` | LOI و blockerهای حقوقی، مسیر رسید پرداخت مستقیم، منبع اعتماد reconciliation، سیاست refresh-token، زمان invoice، لغو متقابل و حفظ مدل `NON_CUSTODIAL_DIRECT`. کارهای تجاری مستقل می‌توانند زودتر موازی شروع شوند، ولی Go/No-Go نهایی تا بسته‌شدنشان صادر نمی‌شود. |
| 9 — آخرین ادغام‌های بیرونی | `TODO-153` سپس `TODO-026` و `TODO-058` | **ابتدا DNS/domain و HTTPS عمومی؛ سپس ارسال و verify واقعی SMS.ir** با template/API credential مصوب؛ در پایان live-provider acceptance. این‌ها بعد از تکمیل کد، تست‌های mock، QA APK و staging انجام می‌شوند. |
| 10 — Release/Go-live | `TODO-054…060`، به‌خصوص `TODO-055`، `TODO-056`، `TODO-057…060` | اجرای مجدد suite روی SHA release-candidate، staging E2E با QA artifacts، live integration acceptance، بستن P0 و تعیین تکلیف P1ها و در نهایت ساخت/امضای release APK/AAB. هر اصلاح پس از gate، SHA جدید و اجرای مجدد gateهای متاثر را لازم دارد. |

### قواعد صریح اجرای بدون دامنه و بدون SMS واقعی

1. تمام کد، منطق محصول و تست‌های unit/integration/API/browser باید ابتدا با DB ایزوله و محیط test/QA انجام شوند. برای احراز هویت از provider تستی یا outbox قابل‌خواندن در محیط test استفاده شود؛ **اعتبارسنجی OTP، انقضا، مصرف‌شدن، سقف تلاش و rate-limit غیرفعال نمی‌شوند** و هیچ fallback پیامک آزمایشی نباید در production فعال باشد.
2. می‌توان staging را موقتاً با IP/شبکهٔ محدود و config جدا اجرا کرد. برای تست Android در صورت نیاز از emulator loopback/tunnel یا build QA محدود استفاده شود؛ سیاست network security در production به خاطر QA تضعیف نشود.
3. Object Storage واقعی یک وابستگی بیرونی مستقل است و باید پیش از live SMS/domain در staging آزموده شود؛ تا قبل از آن mock آن فقط برای تست منطقی پذیرفته است و قبولی mock به‌جای upload/download زنده ثبت نمی‌شود.
4. `TODO-011` مربوط به secretهای workflow **Notification Retention** (`DATABASE_URL`/`POL_PG_DSN`) است؛ با SMS.ir یا OTP واقعی یکی نیست و نباید مانع تست‌های مستقل در DB ایزوله شود. بااین‌حال خودش باید جداگانه بسته شود.
5. TODO-084 باید fail-closed بماند. اگر معیار جدید PRE-BUILD اضافه شد، علاوه بر همین فهرست باید checker `mvp/apps/mobile/scripts/check_prebuild_todo_gate.mjs` هم به‌روزرسانی و CI آن اجرا شود.
6. برای هر مورد، نتیجه فقط با `DONE_VERIFIED` و SHA/command/log/artifact مشخص بسته می‌شود. CI سبز روی PR Draft به معنی merge یا تأیید دستگاه نیست. هیچ TODO از روی پیشرفت یک کار مشابه به‌صورت خودکار بسته نمی‌شود.

**وضعیت جاری که در این ترتیب لحاظ شده است:** PR #40 روی SHA `1c793b5363efda1fd6db0c32bf098472a6e9a6f9` همهٔ چهار workflow لازم را پاس کرده (Static؛ Browser `17/17`؛ Mobile `28/28` functional و `38/38` regression؛ backend `663/663`)، اما PR همچنان Draft و ادغام‌نشده است. گیت APK روی همان SHA، `82/82` پیش‌نیاز تأییدنشده گزارش کرده و هر چهار job ساخت APK را Skip کرده است. بنابراین هیچ APK تازه‌ای از آن SHA موجود/تأییدشده ادعا نمی‌شود.

**قاعدهٔ واگذاری:** گزارش هر ایجنت باید در handoff journal بگوید آخرین TODO تکمیل‌شده کدام است، مورد بعدی دقیقاً کدام است، از چه branch/SHA شروع می‌شود، و کدام evidence به آن اجازهٔ شروع می‌دهد. شناسه‌ها را جابه‌جا یا دوباره مصرف نکنید.

---

## P0 — وضعیت فعلی GitHub و گواهی کد

- [x] `TODO-001` **DONE_VERIFIED — وضعیت نهایی PR #30 و CI:** PR #30 در `2026-10-11T22:47:42Z` ادغام شد؛ merge commit در `main`: `2cd6588206c8b3bddc5ae13aad461bc61f90338f`. PR head قبل از ادغام `45ff1e3d6498568596a42b01d9b69d827a49777d` بود و GitHub merge-candidate SHA `83485b25a7042999150daf487dd99c140642a827` را تست کرد. **Tree SHA merge-candidate و `main` پس از ادغام دقیقاً یکسان است:** `3b14029235ba0c5d61dfe19dee0708a87b75bfe5`. سه workflow سبز بودند: [Static Gate](https://github.com/rrasi90/POL-2.3/actions/runs/38130308723)، [Mobile Verification + Retailer/Vendor QA APK](https://github.com/rrasi90/POL-2.3/actions/runs/38130308664)، [Independent Verification](https://github.com/rrasi90/POL-2.3/actions/runs/38130308606). | مالک: ایجنت نگهدارندهٔ TODO | پیش‌نیاز: بدون پیش‌نیاز
- [x] `TODO-002` **DONE_VERIFIED — full verification روی همان tree که اکنون در `main` است:** CI برای merge-candidate SHA `83485b25a7042999150daf487dd99c140642a827` گزارش `artifacts/pol-test-results.json` را تولید کرد؛ PostgreSQL 18.6، `663 collected / 663 passed / 0 failed / 0 skipped`, exit code `0`, مدت `199.01s`, working tree clean. Tree این SHA با `main` پس از squash merge برابر `3b14029235ba0c5d61dfe19dee0708a87b75bfe5` است؛ بنابراین این شواهد روی همان snapshot کد `main` اعمال می‌شود، هرچند SHAهای commit متفاوت‌اند. Artifact: [Independent Verification CI](https://github.com/rrasi90/POL-2.3/actions/runs/38130308606) (artifact ID `11698943848`). این مدرک تست روی گوشی واقعی یا release certification بیرونی نیست.
- [x] `TODO-003` **DONE_VERIFIED — بستهٔ شواهد کامل ایجاد و محتوای ZIP بررسی شد:** اجرا [38182998940](https://github.com/rrasi90/POL-2.3/actions/runs/38182998940)، artifact `pol-verification-evidence` ID `11718750722`, digest `sha256:1269a62a7c66e5deca74a7fca07e6c7380ca5209a2a1505fc11d53e5f12b82d2`. در ZIP هر سه فایل `pol-test-results.json`, `failure_inventory.txt`, `final_certification_adde20b1d47595efa71547ae9397ce10de464aab.json` موجودند. تست: `663 collected / 663 passed / 0 failed / 0 skipped`, exit `0`, مدت `199.02s`, PostgreSQL `18.6`; failure inventory می‌گوید هیچ خطای فعالی نیست؛ verdict گزارش `AUTOMATED_TESTS_PASSED`, ولی `release_or_pilot_certification=NOT_CLAIMED`. Tested commit `adde20b1d47595efa71547ae9397ce10de464aab` و PR head `6015442f630bfc60275e0521ba0c339ed82a8b56` **tree یکسان** دارند (`7017974ddb715076c8054f554f481c093a9cc21a`). هر تغییر بعدی در سورس یا workflow باید دوباره CI شود؛ مستندات/گزارش جدیدی که SHA را تغییر می‌دهد نیز باید با CI نهایی تأیید شود. | مالک: نگهدارندهٔ TODO | پیش‌نیاز: TODO-002
- [x] `TODO-004` **DONE_VERIFIED — تست ضد OTP بین tenantها:** در artifact CI با SHA تست‌شدهٔ `83485b25a7042999150daf487dd99c140642a827`، تست `scripts/test_http_proof_of_delivery.py::TestOTPAttemptCap::test_other_retailer_cannot_consume_victim_otp_attempts` دارای نتیجه `passed` است. مدرک: [Independent Verification CI](https://github.com/rrasi90/POL-2.3/actions/runs/38130308606). | پیش‌نیاز شواهد: TODO-002 (خروجی همان suite هر دو آزمون را دربر دارد).
- [x] `TODO-005` **DONE_VERIFIED — سقف ۵ تلاش OTP:** در artifact CI با SHA تست‌شدهٔ `83485b25a7042999150daf487dd99c140642a827`، تست `scripts/test_http_proof_of_delivery.py::TestOTPAttemptCap::test_otp_attempt_limit` دارای نتیجه `passed` است. مدرک: [Independent Verification CI](https://github.com/rrasi90/POL-2.3/actions/runs/38130308606). | پیش‌نیاز شواهد: TODO-002 (خروجی همان suite این نتیجه را دربر دارد).
- [x] `TODO-006` **DONE_VERIFIED — browser E2E واقعی سبد خرید اجرا و سبز شد:** کد اصلاح سبد از [PR #35](https://github.com/rrasi90/POL-2.3/pull/35) با merge commit `9fd6e7dcd90f044ceb3b94099db5bbb3f5cb99ff` پیش‌تر در `main` ادغام شده بود؛ اکنون پوشش رفتاری مرورگر با Playwright اضافه شده است (`mvp/apps/web/tests/`، ۱۶ سناریو: لاگین E.164، sync اولیه، کلیک مکرر (فقط یک سبد)، Retry پس از 500، سبد خالی، باطل‌شدن سبد قدیمی پس از ویرایش، بازیابی 404، گیت 401/شبکه/503 بدون سبد جایگزین، خطای item-write و جلوگیری از checkout، بازیابی پاسخ ازدست‌رفته، allocation preview). زیرساخت: `scripts/e2e_seed.py`، `scripts/e2e_serve.py`، `scripts/e2e_db.py`، `mvp/apps/web/playwright.config.ts`، workflow جدید `.github/workflows/pol-browser-e2e.yml`. سه باگ واقعی که همین تست‌ها کشف کردند رفع شد: شمارهٔ فقط-رقمی در لاگین (422 VALIDATION_ERROR)، دوباره‌کلیکِ review که دو سبد OPEN می‌ساخت، و سکوت کامل هنگام انقضای نشست. شواهد: ۴ اجرای محلی پشت‌سرهم 16/16 سبز، `npm run typecheck` OK، گارد منبع 15/15، `npm ci` تمیز و schema تازه (۷۶ migration / ۱۰۷ جدول)؛ CI روی head `ac28036025b79677422589b7f4b1427c56d2f057` چهار workflow (Static Gate، Browser E2E، Independent Verification، MVP Mobile) همگی success — run‌های 38324242236 / 38324242184 / 38324242187 / 38324242215. ریسک باقی‌مانده: item-write ناموفق می‌تواند سبد ناقص OPEN بگذارد (قرارداد تراکنشی bulk-sync وجود ندارد)؛ release APK و TODO-011 و TODO-007 خارج از این TODO. | مالک: Web QA | پیش‌نیاز: TODO-005
- [x] `TODO-007` **DONE_VERIFIED — تست runtime مسیر تحویل در browser (cross-persona) سبز است:** سناریوی کامل با Playwright روی محیط واقعی dev (Next.js + FastAPI + PostgreSQL) اجرا شد: ورود خرده‌فروش → سبد → checkout (سفارش `SUBMITTED`) → ورود بنکدار → پذیرش → آماده‌سازی → آماده → dispatch با مشخصات راننده → `picked-up` → `in-transit` → `arrived` (gate منفی POD قبل از `ARRIVED` هم تأیید شد) → OTP از outbox `DELIVERY_OTP_GENERATED` → `/deliver` با نام گیرنده + کد → تأیید نهایی و نمایش «تأییدشده با کد OTP» و «این سفارش قبلاً تحویل داده شده است.». گواهی اجرا: `npx playwright test` = **17/17 passed (36.3s)** شامل `tests/delivery-flow.spec.ts`؛ `npm run typecheck` EXIT=0؛ `ui_audit_regression_guards.py` **15/15**؛ `test_api_route_hygiene.py` OK. در همین TODO چهار باگ واقعی UI رفع شد: (1) دکمه‌های مرحله‌ای تحویل و فرم راننده در صفحهٔ سفارش بنکدار غایب بود و «ثبت تحویل» از `DISPATCHED` به `/deliver` می‌زد (برای بنکدار 403) — با شاخه‌بندی مرحله‌ای جایگزین شد؛ (2) POD خرده‌فروش بدون گیت `ARRIVED`/نام گیرنده/OTP فعال بود؛ (3) برچسب‌های `PICKED_UP`/`ARRIVED` خام نمایش داده می‌شدند؛ (4) باگ واقعی checkout: پس از `clearBasket()`، effect دوباره اجرا شده و صفحهٔ تأیید را با خطای «سبد خرید خالی است.» جایگزین می‌کرد (سفارش ساخته می‌شد ولی UI خطا نشان می‌داد) — با guard `if (result) return;` رفع شد. اسکریپت‌های E2E هم تقویت شدند: `e2e_seed.py` release کردن residual reservationها (مهاجرت 057) + `vendor_phone` در fixture؛ `e2e_db.py` دستور `otp <order_id>` و `reset` مقاوم در برابر FK سبد/سفارش (اجرای مجدد پس از شکست جزئی). بُعد device/emulator (نصب APK روی دستگاه) خارج از این TODO و همچنان باز است (TODO-018…TODO-024). | مالک: Web QA | پیش‌نیاز: TODO-006
- [x] `TODO-008` **DONE_VERIFIED — اعتبارسنجی هر دو workflow اندروید:** در [Mobile Verification run 38130308664](https://github.com/rrasi90/POL-2.3/actions/runs/38130308664)، validate تنظیمات Expo، Pre-APK QA و ساخت APK هر دو variant موفق بود. Artifact خرده‌فروش: [POL-retailer-QA-APK](https://api.github.com/repos/rrasi90/POL-2.3/actions/artifacts/11699665187) (ID `11699665187`, SHA-256 `3de49ab14a2082e386e1821c8e1ebed4907feb3975c67c057704651d8a6c4325`); artifact بنکدار: [POL-vendor-QA-APK](https://api.github.com/repos/rrasi90/POL-2.3/actions/artifacts/11698984486) (ID `11698984486`, SHA-256 `395f51c408124ea05ef9212770c87ba858a014b42796aa9701f5c4cb38a9321b`). این فقط موفقیت build/artifact است؛ نصب و تست روی دستگاه واقعی همچنان باز است.
- [ ] `TODO-009` **OPEN — ساخت و انتشار artifactهای QA (نه Release):** workflow موبایل فقط پس از تکمیل `TODO-061`…`TODO-083`، `TODO-085`…`TODO-130` و موارد PRE-BUILD منتخب (`TODO-131`…`TODO-136`، `TODO-138`، بخش ایستای `TODO-139` و `TODO-144`، `TODO-145`، `TODO-147`، بخش ایستای `TODO-149`) و عبور گیت نهایی `TODO-084` روی همان SHA، APK آزمایشی هر دو variant را بسازد و به‌عنوان artifact قابل دریافت ذخیره کند؛ نتیجهٔ build و شناسه/لینک artifact ثبت شود. مسیرهای high-level TODO-012…017 باید یا مستقل DONE_VERIFIED شوند یا evidence آن‌ها به تست‌های جزئی پایین‌دستی trace و با تأیید reviewer پذیرفته شود. ساخت QA APK با release build فرق دارد. این خروجی فقط برای device QA است و جای release build را نمی‌گیرد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-008؛ TODO-012…017 باید DONE_VERIFIED یا به evidence دقیق TODO-074…080 و TODO-092…124 trace شده و توسط reviewer مستقل پذیرفته شوند؛ سپس TODO-061…083، TODO-085…130، subset PRE-BUILD مقرر و TODO-084
- [ ] `TODO-010` **REVALIDATE — GitHub Actions YAML:** workflowهای تغییرکرده را parse/lint کنید و مطمئن شوید کلیدهای تکراری `env` یا expressionهای اشتباه مثل `\${{ ... }}` باقی نمانده‌اند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-009 باید تعیین تکلیف شود
- [ ] `TODO-011` **BLOCKED_EXTERNAL — notification retention workflow:** این مانع مستقل از SMS واقعی است. اگر workflow هنوز شکست می‌خورد، بررسی کنید secretهای موردنیاز `DATABASE_URL` و/یا `POL_PG_DSN` در محیط GitHub Actions تنظیم شده باشند؛ secret را در repo یا log قرار ندهید و workflow را دوباره اجرا کنید. | مالک: تعیین‌نشده | پیش‌نیاز: بدون وابستگی به TODO-009؛ مستقل از زنجیرهٔ کد/test و از SMS.ir

## P0 — تست پذیرش end-to-end محصول

- [ ] `TODO-012` **OPEN — مسیر کامل Retailer:** ورود با OTP در محیط test از test provider/outbox (بدون SMS.ir) → مشاهدهٔ کاتالوگ و آفرها → افزودن به سبد → allocation → checkout → مشاهدهٔ order group و سفارش‌های فروشندگان → timeline → تحویل/POD → وضعیت پرداخت → support یا dispute/RMA. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-063، TODO-070، TODO-075 و TODO-079؛ با provider تستی/outbox، بدون نیاز به SMS زنده
- [ ] `TODO-013` **OPEN — مسیر کامل Vendor:** ورود → مدیریت catalog/price/inventory → دریافت سفارش → accept/reject/partial accept → fulfillment → dispatch/handoff → مدرک/وضعیت پرداخت → invoice، dispute/RMA و support. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-012
- [ ] `TODO-014` **OPEN — تست منفی HTTP/RBAC:** برای هر endpoint مهم، unauthenticated، نقش نامعتبر، tenant دیگر، membership غیرفعال، resource ناموجود و state transition نامعتبر؛ نتیجه‌های 401/403/404/409/422 مطابق قرارداد واقعی بررسی شوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-013
- [ ] `TODO-015` **OPEN — تست idempotency و هم‌زمانی:** checkout/submit، اقدامات Vendor، dispatch/تأیید تحویل، پرداخت و refund تکراری؛ رقابت دو درخواست برای آخرین موجودی؛ عدم ایجاد سفارش، پرداخت، رزرو یا تأیید تکراری. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-014
- [ ] `TODO-016` **OPEN — تست چرخهٔ تحویل/POD:** نقش مجاز، سفارش و delivery state درست، OTP معتبر/نامعتبر/مصرف‌شده، سقف تلاش‌ها، شکست تحویل، evidence media آماده و متعلق به همان tenant، عدم نشت OTP تحویل در dispatch/logs. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-015
- [ ] `TODO-017` **OPEN — تست اتصال قراردادهای API به UI:** مسیرهای واقعی را از `mvp/MVP_API_MAP.md` و صفحات را از `mvp/MVP_SCREEN_MATRIX.md` به سناریوهای اجراشده وصل کنید؛ هر سناریوی فاقد تست یا نتیجه را ثبت کنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-016

## P0 — Android: build، نصب و تصویربرداری بصری

- [ ] `TODO-018` **OPEN — آماده‌سازی Runtime واقعی:** فراهم‌کردن Android SDK/ADB، Emulator یا دستگاه فیزیکی و ثبت مدل دستگاه، نسخهٔ Android/SDK، رزولوشن و معماری CPU؛ اطمینان از اینکه runtime واقعاً قابل دسترس است و `adb devices` دستگاه را می‌بیند. نبود runtime را `BLOCKED_EXTERNAL` ثبت کنید، نه PASS. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-009 و TODO-017
- [ ] `TODO-019` **OPEN — اصلاح/تأیید application IDs:** شناسه‌های مورد انتظار `ir.pol.market` و `ir.pol.vendor` را با config و APK واقعی تطبیق دهید؛ در گزارش قبلی `com.anonymous.polmobile` مشاهده شده بود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-018
- [ ] `TODO-020` **OPEN — نصب و smoke test دو APK آزمایشی:** نصب هر دو variant روی Android واقعی یا emulator؛ package ID، signature، version/build number، cold start/relaunch، login/session، navigation، deep links، API base URL، permission prompt، keyboard/safe-area و خروج/بازگشت بررسی شود. تغییر شبکه Wi-Fi/mobile/offline، timeout/retry، background/resume، force close و session expiry را نیز بیازمایید. این فقط QA build است؛ release package هنوز ممنوع است. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-019
- [ ] `TODO-021` **OPEN — تصویربرداری از تمام صفحات و stateها:** inventory تاریخی ۶۰ مورد داشت؛ ابتدا آن را با `MVP_SCREEN_MATRIX.md` فعلی تطبیق دهید و شمار واقعی را ثبت کنید. از هر صفحه/state لازم screenshot بگیرید و نام صفحه، نقش، state، fixture data، دستگاه/OS، SHA/APK version، نتیجه و bug ID را ثبت کنید. screenshot از mock باید واضحاً mock-label داشته باشد و به‌جای live flow پذیرفته نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-020
- [ ] `TODO-022` **OPEN — بررسی دسترسی واقعی به `SupportMobileScreen.tsx`:** رسیدن به صفحه از navigation واقعی اپ و حالت‌های loading/empty/error/success را اثبات کنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-021
- [ ] `TODO-023` **OPEN — تست Motion System و lifecycle:** transition/animationها را روی دستگاه اجرا کنید؛ navigation سریع، back/deep-link، background/resume، force close، درخواست شبکه هم‌زمان و stateهای loading/error را بیازمایید تا state گم یا دوباره ثبت نشود. reduced-motion setting و انیمیشن‌های وابسته به gesture نیز بررسی شوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-022
- [ ] `TODO-024` **OPEN — مقایسهٔ بصری، responsive و accessibility:** متن فارسی/RTL، overflow، safe-area، keyboard، دستگاه/رزولوشن کوچک، dark/light، loading/empty/error/success/disabled، contrast، اندازهٔ متن، touch targets، focus/navigation و labels/screen-reader را در محدودهٔ پشتیبانی‌شده ثبت کنید. هر ایراد باید bug ID، شدت، screenshot و گام بازتولید داشته باشد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-023
- [ ] `TODO-025` **OPEN — Vercel QA با دادهٔ mock:** مسیر ابتدا Vendor و سپس Retailer را در `rrasi90/POL-2.3-Vercel-QA` یا محیط QA تعیین‌شده بررسی کنید؛ mock data باید از دیتابیس اصلی/تولید کاملاً جدا باشد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-063 و TODO-079؛ مسیر Vercel/hosted mock می‌تواند مستقل از device QA اجرا شود

## P1 — وابستگی‌ها و آمادگی پایلوت

- [ ] `TODO-026` **BLOCKED_EXTERNAL — SMS.ir واقعی:** این کار آخرین فاز live integration است: قالب پیامک و API key/template ID معتبر را می‌توان از قبل درخواست/تأیید اداری کرد، اما ارسال و verify واقعی را فقط پس از TODO-153 و آماده‌شدن staging انجام دهید؛ rate-limit/lockout/خطای provider را هم تست کنید. پیش از این مرحله همهٔ OTPها با test provider/outbox آزموده می‌شوند. اسرار فقط در secret manager/environment باشند؛ هیچ secret واقعی در این TODO نوشته نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-153، TODO-030، TODO-033 و TODO-070؛ پیامک زنده فقط در مرحلهٔ نهایی
- [ ] `TODO-027` **BLOCKED_EXTERNAL — Object Storage واقعی:** باکت S3-compatible واقعی و credentials امن را در staging تنظیم کنید؛ upload/download واقعی برای تصاویر کالا، رسید مالی، POD و مدرک dispute را بررسی کنید. این ادغام پس از آزمون کد و staging اما پیش از DNS عمومی و SMS زنده انجام می‌شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-029، TODO-063 و TODO-077؛ storage واقعی پس از آماده‌شدن staging و تست‌های media
- [ ] `TODO-028` **OPEN — تست امنیت فایل در storage زنده:** hash/checksum، MIME و magic bytes، سقف حجم، نام/مسیر امن، دسترسی tenant، رسانهٔ `READY`، جلوگیری از Path Traversal و عدم دسترسی غیرمجاز به فایل دیگران. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-027 و TODO-077
- [ ] `TODO-029` **REVALIDATE — اتصال و deploy روی VPS:** دسترسی SSH، نسخهٔ runtime، environment/secrets، PostgreSQL و migration، process supervisor، reverse proxy داخلی یا دسترسی محدود، CORS مخصوص QA، health/readiness/liveness و restart/rollback را روی سرور واقعی تأیید کنید. این مورد فقط staging بدون دامنهٔ عمومی است؛ DNS/domain و HTTPS عمومی صریحاً به TODO-153 منتقل شده‌اند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-009، TODO-063، TODO-065، TODO-075 و TODO-084؛ staging محدود با IP/private access، بدون public domain/TLS (TODO-153)
- [ ] `TODO-030` **OPEN — تست smoke استیجینگ دامنه‌ندار روی SHA دقیق:** bootstrap/login، کاتالوگ، basket/checkout، پذیرش Vendor، تحویل، media upload، پرداخت مستقیم و notification از test outbox/provider؛ پیامک زنده یا دامنهٔ عمومی پیش‌نیاز این smoke نیست. نتیجه، زمان و SHA را نگه دارید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-029، TODO-028 و TODO-076؛ OTP از test provider/outbox، نه SMS.ir
- [ ] `TODO-031` **OPEN — خودکارسازی backup:** گزارش قبلی backup/restore دستی موفق را ثبت کرده است؛ backup زمان‌بندی‌شده، retention، هشدار شکست و restore drill مستند را تکمیل کنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-029 و TODO-065
- [ ] `TODO-032` **OPEN — Runbook عملیات و بازیابی:** دستورهای deploy/rollback، migration، restore، rotate secret، بازگردانی worker و بررسی `/readyz` را مستند کنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-029 و TODO-031
- [ ] `TODO-033` **OPEN — Monitoring:** لاگ ساختاریافته و correlation ID را به سیستم monitoring/log aggregation انتخاب‌شده وصل کنید؛ هشدار برای API، DB، worker، queue/outbox، retention و provider failure تعریف شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-029 و TODO-076
- [ ] `TODO-034` **BLOCKED_EXTERNAL — قراردادهای پایلوت:** وضعیت فعلی LOI/قراردادهای رسمی با بنکداران هدف را به‌روز کنید؛ این کار تجاری می‌تواند موازی با تست فنی شروع شود، گزارش 2026-09-27 امضای توافق با ۵ بنکدار را blocker ثبت کرده بود. فقط قرارداد/LOI امضاشده را انجام‌شده علامت بزنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-008؛ می‌تواند موازی با QA فنی پیش برود؛ برای Go/No-Go نهایی باید تعیین تکلیف شود

## P1 — پرداخت، تصمیم‌ها و قراردادهای باقی‌مانده

- [ ] `TODO-035` **OPEN — مسیر مدرک پرداخت مستقیم:** پیاده‌سازی و/یا ثبت نتیجهٔ تست endpoint `POST /orders/{id}/payments/direct-receipt` را در برابر قرارداد canonical بررسی کنید؛ در آخرین بررسی این مسیر کامل تأیید نشده بود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-074 و TODO-101؛ به امضای LOI یا SMS زنده وابسته نیست
- [ ] `TODO-036` **OPEN — منبع اعتماد و reconciliation پرداخت:** مالکیت منبع حقیقت برای تأیید پرداخت، تعارض شواهد، پردازش reconciliation feed و ثبت audit trail را مشخص و تست کنید. برای پایلوت، تطبیق بانکی خودکار را می‌توان از مسیر دستی تأیید رسید جدا نگه داشت، مشروط به ثبت صریح این محدودیت. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-035
- [ ] `TODO-037` **OPEN_DECISION — D-018:** سیاست refresh-token rotation/reuse و متن رسمی تصمیم را با رفتار runtime همگام و تأیید کنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-070 و TODO-120
- [ ] `TODO-038` **OPEN_DECISION — زمان صدور invoice:** تأیید مالی/حسابداری برای صدور invoice در زمان `ACCEPTED` یا زمان دیگر و ثبت تصمیم canonical. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-101 و TODO-110
- [ ] `TODO-039` **OPEN_DECISION — شرایط لغو متقابل:** متن و شرایط حقوقی/عملیاتی لغو متقابل را نهایی کنید؛ رفتار کد به‌تنهایی جای تصمیم و توافق حقوقی را نمی‌گیرد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-102 و TODO-110
- [ ] `TODO-040` **REVALIDATE — مرز مسئولیت مالی:** مطمئن شوید مدل همچنان `NON_CUSTODIAL_DIRECT` است و POL وجوه مشتری را نگه نمی‌دارد؛ هرگونه تغییر مالی باید audit، تفکیک وظایف و idempotency داشته باشد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-036 و ثبت رسمی D-015/D-019/D-020 در منبع حقیقت

## P1 — Gap Register قدیمی که باید روی SHA فعلی دوباره ارزیابی شود

> این موارد در رجیستر قدیمی `LEGACY_REVALIDATE` بودند؛ آن‌ها را باگ قطعی یا مجوز پیاده‌سازی خودکار فرض نکنید. برای هر مورد تست/API evidence فعلی بگیرید و سپس `RESOLVED` یا `ACTIVE` تعیین کنید.

- [ ] `TODO-041` **REVALIDATE — G-003:** تفاوت مسیر مستند `/products/search` با مسیر واقعی `/catalog/search`؛ همهٔ clientها و تست‌های زنده باید مسیر canonical واقعی را مصرف کنند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-040 باید تعیین تکلیف شود
- [ ] `TODO-042` **REVALIDATE — G-004:** تفاوت قرارداد قدیمی `/inbox/items` با `/notifications`؛ قرارداد، route و client را تطبیق دهید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-041 باید تعیین تکلیف شود
- [ ] `TODO-043` **REVALIDATE — G-009/G-010:** Vendor Customers API و Vendor Staff/delegated permissions API را در برابر نیاز MVP و Decision Register بررسی کنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-042 باید تعیین تکلیف شود
- [ ] `TODO-044` **REVALIDATE — G-011:** admin broadcasts، SLA و category admin را از نظر contract، route واقعی و نیاز MVP بررسی کنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-043 باید تعیین تکلیف شود
- [ ] `TODO-045` **REVALIDATE — G-012/G-013:** Basket GET/list و Global Returns list را با route inventory و نیاز واقعی screens تطبیق دهید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-044 باید تعیین تکلیف شود
- [ ] `TODO-046` **REVALIDATE — G-021:** مشاهدهٔ لیست Partial Acceptance Proposal را بررسی کنید و مشخص کنید آیا timeline فعلی طبق قرارداد کافی است یا endpoint جدا لازم است. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-045 باید تعیین تکلیف شود
- [ ] `TODO-047` **REVALIDATE — D-028:** پیاده‌سازی barcode/inventory scan را با تصمیم رسمی و مسیرهای واقعی موبایل تطبیق دهید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-046 باید تعیین تکلیف شود
- [ ] `TODO-048` **REVALIDATE — G-137/G-212:** ارجاع‌های تاریخی ناقص را در رجیستر/منبع canonical پیدا و تعیین تکلیف کنید؛ تا یافتن evidence، حذف یا بستن فرضی انجام نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-047 باید تعیین تکلیف شود

## P2 — همگام‌سازی اسناد و ردیابی تست

- [ ] `TODO-049` **OPEN — `mvp/BUILD_PLAN.md`:** موارد باز را با SHA و شواهد فعلی reconcile کنید؛ این فایل برنامهٔ کار است، اما چک‌باکس‌های قدیمی بدون re-test معیار وضعیت امروز نیستند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-048 باید تعیین تکلیف شود
- [ ] `TODO-050` **OPEN — `mvp/MVP_KNOWN_GAPS.md`:** گپ‌های پرداخت/رسید و هر مورد باز دیگر را با implementation و تست فعلی sync کنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-049 باید تعیین تکلیف شود
- [ ] `TODO-051` **OPEN — `TEST_VERIFICATION_MANIFEST.md`:** نسخهٔ PostgreSQL، زنجیرهٔ migration، test modules، مسیر اجرا و SHA مرجع را با کد فعلی تطبیق دهید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-050 باید تعیین تکلیف شود
- [ ] `TODO-052` **OPEN — `mvp/MVP_API_MAP.md` و `mvp/MVP_SCREEN_MATRIX.md`:** همهٔ endpointها و screen/stateها را به تست یا وضعیت صریح `BLOCKED_EXTERNAL`/`OUT_OF_SCOPE` متصل کنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-051 باید تعیین تکلیف شود
- [ ] `TODO-053` **OPEN — ثبت شواهد:** برای هر مورد بسته‌شده، نام تست، command، SHA، تاریخ، خروجی و artifact را ثبت کنید؛ PASS تاریخی، mock یا screenshot بدون runtime به‌جای آزمون واقعی استفاده نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-052 باید تعیین تکلیف شود

---

## معیار نهایی بستن TODO List

- [ ] `TODO-054` PR و تمام checkهای مربوط به SHA نهایی تعیین تکلیف شده باشند؛ هیچ failure ناشناخته‌ای باقی نماند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-053 و بررسی PR/CI روی SHA دقیق candidate؛ PR Draft یا CI مربوط به SHA قدیمی باید صریحاً ثبت شود
- [ ] `TODO-055` verification suite روی SHA انتشار با **۰ failure و ۰ skip غیرموجه** تمام شود و artifactها همان SHA را نشان دهند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-054؛ full verification و artifact باید روی همان SHA final candidate باشند
- [ ] `TODO-056` فقط در آخرین مرحله و پس از تکمیل تست‌های software/device، آماده‌شدن DNS/TLS و SMS/storage live و تصویب Go/No-Go؛ پس از عبور Pre-build gate (`TODO-061`…`TODO-083`، `TODO-085`…`TODO-130`، موارد PRE-BUILD منتخب (`TODO-131`…`TODO-136`، `TODO-138`، بخش ایستای `TODO-139` و `TODO-144`، `TODO-145`، `TODO-147`، بخش ایستای `TODO-149`) و گیت نهایی `TODO-084`) و موفقیت QA دستگاهی (`TODO-018`…`TODO-024`) و تست‌های POST-QA (`TODO-137`، `TODO-140`…`TODO-143`، `TODO-146`، `TODO-148`، `TODO-150`…`TODO-152`)، release APK/AAB هر دو variant با package IDهای canonical ساخته شوند؛ نصب و smoke test نهایی انجام شود و تصویربرداری هر ۶۰ مورد بسته یا blocker آن مستند شود. Build نهایی باید از SHA تأییدشده باشد؛ artifact، checksum، تنظیمات امضا بدون افشای secret و لینک‌ها ثبت شوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-009، TODO-055، TODO-084، TODO-018…TODO-024، TODO-137، TODO-140…TODO-143، TODO-146، TODO-148، TODO-150…TODO-152، TODO-153، TODO-026، TODO-058، TODO-059 و TODO-060
- [ ] `TODO-057` مسیر staging Retailer-to-Vendor، fulfillment/delivery/POD و پرداخت مستقیم با QA build یا browser و test OTP/outbox اجرا و ثبت شود؛ این تست باید قبل از public domain و SMS واقعی هم قابل انجام باشد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-009، TODO-020، TODO-030 و TODO-101؛ QA/staging E2E با test OTP/outbox، قبل از دامنه و SMS زنده
- [ ] `TODO-058` گیت نهایی provider: دامنه/TLS عمومی، ارسال/verify واقعی SMS.ir و storage زنده برای فیش/POD/مدرک dispute روی محیط موردنظر با شواهد تأیید شوند. mock به‌جای live PASS نیست؛ تعویق فقط با تصمیم مکتوب مجاز است. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-026، TODO-027، TODO-028، TODO-153 و TODO-057؛ هیچ live integration با mock به‌عنوان PASS ثبت نشود
- [ ] `TODO-059` blockerهای کسب‌وکاری/حقوقی و تصمیم‌های باز با مسئول و تصمیم مستند تعیین تکلیف شوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-034، TODO-037…040 و TODO-058
- [ ] `TODO-060` هیچ P0 باز نماند؛ موارد P1 باقی‌مانده دارای مالک، دلیل، تصمیم و تاریخ پیگیری باشند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-054، TODO-055، TODO-057، TODO-058، TODO-059 و همهٔ یافته‌های P0/P1 مربوط به PRE/POST-QA

---

## گیت اجباری قبل از ساخت اپلیکیشن — Pre-build Qualification

**هدف:** پیش از ساخت APK/AAB، با تست‌های قابل‌بازتولید ثابت شود سورس، backend، database، API، امنیت و web/mobile configuration در همان SHA آمادهٔ ورود به QA build هستند. این بخش از تاریخچهٔ گواهی قدیمی جداست و باید روی SHA جاری اجرا شود.

**قانون اجرا:** `TODO-061` از بعد از `TODO-008` شروع می‌شود. ابتدا `TODO-061` تا `TODO-083` و `TODO-085` تا `TODO-130`، سپس موارد دارای برچسب `PRE-BUILD` در `TODO-131` تا `TODO-152` (فقط subset مشخص‌شده در بخش قوانین ترتیب) و در آخر گیت تجمیعی `TODO-084` اجرا می‌شوند. موارد `POST-QA-APK` پس از نصب APK آزمایشی و پیش از release build اجرا می‌شوند. شناسهٔ TODO-084 به دلایل traceability تغییر نکرده، اما به لحاظ dependency باید آخر باشد. تا وقتی همهٔ پیش‌نیازها شواهد دارند و `TODO-084` با `DONE_VERIFIED` بسته نشده، QA APK ممنوع است؛ هر استثنا نیاز به waiver مکتوب و دلیل فنی دارد. برای release APK/AAB، علاوه بر این بخش، گیت نصب و تست دستگاهی نیز باید سبز باشد.

### G1 — Source baseline, clean install و reproducibility

- [ ] `TODO-061` **OPEN — تثبیت مبنای تست:** branch، SHA، وضعیت working tree، PR، فایل‌های تغییرکرده و آخرین گزارش ایجنت را ثبت کنید؛ مبنای remote فعلی `main` برابر `d9505cfa62c953546b479f4ca8aec1997ca57fbc` است؛ تصمیم‌های canonical، `CURRENT_SOURCE_OF_TRUTH`، `DECISION_REGISTER`، API map، screen matrix و known gaps را بخوانید. اختلاف migration head و ارجاع API boundary مفقود را ثبت کنید، اما تا مشاهدهٔ tree/migration manifest اصلاح حدسی نکنید. وضعیت worktree محلی در این session در دسترس نیست و باید در محیط دارای checkout تکمیل شود. هر گزارش قدیمی را با SHA جاری تطبیق دهید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-008؛ working tree محلی باید توسط محیط دارای checkout بررسی شود
- [ ] `TODO-062` **OPEN — بازتولید محیط پاک:** روی worktree تمیز، نسخه‌های Python/Node/npm/Expo/PostgreSQL/Android tooling را ثبت کنید؛ نصب dependencyها از lockfileها را اجرا کنید (`npm ci` در صورت وجود `package-lock.json`). نبود یا ناسازگاری lockfile، اختلاف dependency یا نیاز به نصب دستی ثبت شود؛ آن را پنهانی با `npm install` دور نزنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-061
- [ ] `TODO-063` **OPEN — پیکربندی و جداسازی محیط:** تمام env varهای لازم را با schema/نمونهٔ بدون secret بررسی کنید؛ development/test/QA/staging/production نباید ناخواسته به یک DB یا API مقصد وصل شوند. startup باید برای متغیر ضروریِ غایب خطای روشن بدهد و هیچ credential در repo، artifact یا log قرار نگیرد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-062

### G2 — کیفیت کد و سلامت پایگاه داده

- [ ] `TODO-064` **OPEN — lint، typecheck و syntax:** Python compile/import/static checks، تست‌های lint و typecheck پروژهٔ TypeScript، و parse/validation فایل‌های config/workflow را اجرا کنید. فرمان کامل، exit code و خروجی را ثبت کنید؛ هیچ error یا هشدار blocker بدون تعیین تکلیف باقی نماند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-063
- [ ] `TODO-065` **OPEN — migration از صفر و upgrade:** روی PostgreSQL مورد تأیید پروژه، DB خالی را با تمام migrationهای canonical موجود تا tip فعلی بسازید و DB دیگری را از baseline پشتیبانی‌شده upgrade کنید؛ duplicate execution، ترتیب نامعتبر، trigger/index/FK failure و drift را بررسی کنید. شمارهٔ نهایی migration را از مخزن جاری کشف کنید؛ عدد تاریخی را hardcode نکنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-064
- [ ] `TODO-066` **OPEN — یکپارچگی DB و transaction rollback:** constraints، FK، unique/idempotency constraints، triggerها، append-only auditها، reservation invariants و رفتار rollback را تست کنید. در صورت امکان queryهای reconciliation برای رکورد orphan/duplicate اجرا و نتیجه را ثبت کنید؛ تعداد جداول/تریگرها را از همان DB و SHA بخوانید، نه از گزارش قدیمی. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-065
- [ ] `TODO-067` **OPEN — کل verification suite:** `python scripts/run_verification_suite.py` یا فرمان canonical ثبت‌شده در manifest را از ابتدا اجرا کنید. نتیجه باید به SHA جاری مربوط باشد؛ `PASS/FAIL/SKIP/ERROR`, total collected، زمان، نسخهٔ DB و artifactها ثبت شوند. هیچ skip بی‌توجیه یا fail حل‌نشده با ادعای 658/658 قدیمی پوشانده نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-066
- [ ] `TODO-068` **OPEN — پوشش و طبقه‌بندی تست‌ها:** فهرست test modules و coverage موجود را گزارش کنید؛ هر دامنهٔ حیاتی که test نداشت شناسایی شود. درصد جدیدی به‌عنوان معیار اجباری اختراع نکنید؛ threshold از تنظیمات canonical پروژه پیروی کند و نبود threshold به‌عنوان تصمیم/نقص ثبت شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-067

### G3 — API، احراز هویت، امنیت و منطق دامنه

- [ ] `TODO-069` **OPEN — API inventory و قراردادها:** route inventory واقعی، OpenAPI/route registration، `mvp/MVP_API_MAP.md` و API contract tests را با هم مقایسه کنید؛ مسیرهای deprecated/نامعتبر، schema request/response، envelope خطا، pagination، versioning و status codeها بررسی شوند. هر endpoint مصرف‌شده در UI باید route واقعی و contract test داشته باشد یا صریحاً خارج از MVP/مسدود باشد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-068
- [ ] `TODO-070` **OPEN — Auth/session/OTP:** OTP صحیح، غلط، منقضی، مصرف‌شده و تکراری؛ rate-limit/lockout؛ session revoke؛ refresh/reuse طبق تصمیم ثبت‌شده؛ token expiry و پاسخ‌های 401/403 را روی HTTP واقعی تست کنید. سیاست‌هایی که هنوز `OPEN_DECISION` هستند نباید توسط ایجنت حدس زده شوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-069
- [ ] `TODO-071` **OPEN — tenant isolation و RBAC adversarial:** Retailer/Vendor/Ops، owner/staff، membership غیرفعال، سازمان A در برابر B، resource متعلق به tenant دیگر، IDOR و مسیرهای مدیریتی/مالی را پوشش دهید. تلاش‌های غیرمجاز نباید counter، داده یا وضعیت قربانی را تغییر دهند؛ ماتریس مجوزها به نتیجهٔ تست قابل استناد متصل باشد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-070
- [ ] `TODO-072` **OPEN — state machine و قواعد دامنه:** انتقال مجاز و غیرمجاز برای basket/allocation/checkout/order/partial acceptance/inventory reservation/fulfillment/delivery/POD/payment/dispute/RMA/refund/support را تست کنید. تست‌ها باید مسیرهای boundary، expiry، conflict و rollback را پوشش دهند و هیچ وضعیت پایانی به‌صورت مستقیم دور زده نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-071
- [ ] `TODO-073` **OPEN — concurrency و idempotency:** دو checkout هم‌زمان، آخرین موجودی، درخواست تکراری با کلید یکسان و متفاوت، vendor action دوباره، dispatch/delivery confirmation، payment evidence و refund را تست کنید. انتظار: بدون oversell، duplicate financial record یا transition تکراری؛ خطاهای race باید قابل‌پیش‌بینی و قابل‌بازتولید باشند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-072
- [ ] `TODO-074` **OPEN — HTTP integration و خطاهای شبکه:** از API واقعی محلی با auth واقعی تست کنید؛ timeout، connection failure، malformed payload، validation errors، 401/403/404/409/422، retry policy و عدم retry روی mutation غیرidempotent را بررسی کنید. client نباید envelope یا خطا را بی‌صدا به success تبدیل کند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-073
- [ ] `TODO-075` **OPEN — E2E backend قبل از ساخت app:** مسیر API واقعی Retailer → basket → catalog/offer → allocation → checkout → vendor response → fulfillment/delivery/POD → payment status را با دادهٔ تست ایزوله اجرا کنید؛ مسیرهای fail/cancel/partial fulfillment و خواندن timeline را نیز پوشش دهید. تست باید از HTTP عبور کند و DB state نهایی با پاسخ API مطابقت داشته باشد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-074
- [ ] `TODO-076` **OPEN — outbox/workers/notifications:** تولید event در همان transaction، fan-out به اعضای مجاز، dedupe، retry/backoff، permanent failure/quarantine، worker restart و retention را تست کنید. نبود credential بیرونی نباید با mock به‌عنوان delivery واقعی گزارش شود؛ status mock/live را جدا ثبت کنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-075
- [ ] `TODO-077` **OPEN — media/file security:** upload/download محدودشده به نوع فایل و اندازه، magic bytes/MIME، checksum، نام تصادفی، path traversal، فایل ناسالم، media state `READY`, upload target mismatch، tenant ownership و URL/object access را در تست انجام دهید. اگر storage واقعی متصل نیست، contract/mock tests را ثبت و live storage را `BLOCKED_EXTERNAL` نگه دارید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-076

### G4 — Web app، frontend و اتصال به API

- [ ] `TODO-078` **OPEN — کیفیت build وب:** lockfile install، `typecheck`, lint، unit/component tests و production build را برای web اجرا کنید. خطاهای hydration، client/server boundary، importهای runtime، route compilation و missing env را رفع یا مستند کنید؛ QA با mock نباید backend test واقعی را جایگزین کند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-077
- [ ] `TODO-079` **OPEN — browser E2E و stateهای UI:** برای نقش‌های Retailer و Vendor، login، لیست/جزئیات، basket، فرم‌ها، خطاهای API، loading/empty/error/success/disabled، refresh/back/deep-link و session expiry را در browser اجرا کنید. در QA mock، منبع mock و جداسازی کامل از DB اصلی اثبات شود؛ در محیط متصل، API base URL و قرارداد واقعی تأیید شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-078
- [ ] `TODO-080` **OPEN — screen/API parity:** هر screen/state ضروری در `MVP_SCREEN_MATRIX.md` به route، نقش، permission و تست مرتبط متصل شود. صفحهٔ طراحی‌شده اما unreachable، action بدون API، API بدون مصرف‌کنندهٔ موردنیاز یا placeholder مخفی نباید به‌عنوان کامل گزارش شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-079

### G5 — Mobile/Expo checks پیش از native build

- [ ] `TODO-081` **OPEN — mobile static readiness:** داخل `mvp/apps/mobile` نصب dependency از lockfile، TypeScript typecheck، lint، unit/component tests و `npx expo-doctor` یا معادل سازگار با نسخهٔ نصب‌شده را اجرا کنید. خطای native module، mismatch نسخهٔ Expo/React Native یا import unresolved باید قبل از APK حل شود. خروجی هشدارها و نسخهٔ ابزارها ثبت شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-080
- [ ] `TODO-082` **OPEN — Expo config برای هر variant:** retailer و vendor را جداگانه اعتبارسنجی کنید: application ID، app name/icon/splash، scheme/deep links، Android permissions، network security/cleartext، API base URL، environment selection، version/build number و signing configuration. مقدارها را از config واقعی استخراج کنید؛ `com.anonymous.polmobile` یا placeholder فقط در صورت اثبات مجاز پذیرفته شود. هیچ secret/keystore password در فایل یا log ثبت نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-081
- [ ] `TODO-083` **OPEN — bundle/export و asset integrity:** برای هر دو variant دستور canonical Expo export/export:embed را طبق نسخهٔ فعلی اجرا کنید؛ هر دو bundle باید بدون unresolved asset/module و بدون config نامعتبر ساخته شوند. فونت Persian/Vazirmatn، RTL، آیکون‌ها، تصاویر، Android adaptive icon، splash، فایل‌های محلی، permissions و مسیرهای navigation بررسی شوند. Export موفق به‌تنهایی build موفق APK یا تست device نیست. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-082

### G6 — Security/dependency scan و تصمیم صدور مجوز QA build

- [ ] `TODO-084` **OPEN — Pre-build gate report (از نظر اجرا، آخرین گیت):** secret scan، dependency vulnerability audit و license/pinning checks را اجرا کنید؛ یافته‌های critical/high را رفع یا با استثنای رسمی ثبت کنید. گزارش نهایی باید SHA، فرمان‌ها، PASS/FAIL/SKIP، نتایج `TODO-061`…`TODO-083`، `TODO-085`…`TODO-130` و تمام موارد PRE-BUILD مشخص‌شده در بخش قوانین ترتیب TODO-131…TODO-152، coverage matrix، BUG-IDهای باز، ریسک‌ها و تأیید مالک فنی را شامل شود. فقط وقتی هیچ P0/P1 حل‌نشده و failure امنیتی/قراردادی وجود ندارد و همهٔ پیش‌نیازها `DONE_VERIFIED` یا waiver رسمی معتبر دارند، QA-only APK مجاز است. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-083 و TODO-130؛ به‌علاوهٔ موارد PRE-BUILD مقرر در TODO-131…TODO-136، TODO-138، TODO-139 (بخش ایستا)، TODO-144 (بخش وب/کامپوننت)، TODO-145، TODO-147 و بخش static/pre-build از TODO-149


## گیت افزودهٔ دیباگینگ، مسیرهای کاربری و پذیرش ویژگی‌ها — قبل از ساخت QA APK

این بخش برای پوشش خلأ میان «سبز بودن unit/integration suite» و «واقعاً قابل استفاده بودن محصول» اضافه شده است. این آزمون‌ها بر کد و سرویس‌های در دسترس، API واقعی در محیط تست، تست‌های کامپوننت و browser/E2E وب اجرا می‌شوند؛ اگر جریان فقط روی دستگاه قابل اثبات است، آن آزمون پس از ساخت QA-only APK و طبق `TODO-018` تا `TODO-024` انجام می‌شود و نباید قبل از آن PASS فرض شود.

### قوانین اختصاصی Debugging و Feature QA

1. هر bug ابتدا با گام‌های بازتولید دقیق ثبت شود: `BUG-ID`، TODO مرتبط، نقش، محیط، branch/SHA، دادهٔ اولیه، فرمان/route، گام‌ها، نتیجهٔ مورد انتظار، نتیجهٔ واقعی، frequency، log/correlation ID و تصویر/ویدئو در صورت وجود.
2. باگ را با کمترین fixture قابل تکرار بازتولید کنید. قبل از fix، یک regression test که رفتار غلط را ثابت کند بنویسید؛ بعد از fix همان تست باید قبل از بقیهٔ suite پاس شود و تست‌های اطراف نیز اجرا شوند.
3. شدت باگ باید بر اساس اثر تعیین شود: `P0` فساد داده/نشت tenant/ریسک مالی یا امنیتی بحرانی؛ `P1` شکستن مسیر اصلی خرید/سفارش/تحویل/پرداخت یا از کار افتادن نقش اصلی؛ `P2` نقص محدود با workaround؛ `P3` ایراد ظاهری/کم‌اثر. شدت بر اساس مدرک ثبت شود، نه سلیقه.
4. برای هر Feature حداقل مسیر موفق، ورودی نامعتبر، مجوز ناکافی، دادهٔ خالی، خطای سرور، timeout/قطع شبکه، تکرار درخواست و حالت مرزی مربوطه پوشش داده شود. حالتی که برای یک Feature معنی ندارد با توضیح مستند `N/A` شود، نه اینکه بی‌صدا حذف شود.
5. تست هر مسیر باید assertion قابل‌اندازه‌گیری داشته باشد: پاسخ API، وضعیت DB، state ماشین وضعیت، audit/outbox، متن/وضعیت UI یا عدم انجام mutation غیرمجاز. مشاهدهٔ ظاهری یا باز شدن صفحه به‌تنهایی معیار قبولی نیست.
6. mock و live جدا هستند. تست mock امکان بررسی UI و حالت‌های شکست را می‌دهد، اما اصالت اتصال به API/DB/provider واقعی را اثبات نمی‌کند. در گزارش، نوع محیط و منبع داده باید مشخص باشد.
7. هر fix کد، قرارداد API، fixture، schema، پیکربندی یا تصمیم را تغییر دهد، تست‌های وابسته و زنجیره‌ای که ممکن است باطل شده باشد دوباره اجرا شوند؛ قبولی قبل از fix به SHA جدید منتقل نمی‌شود.

### D1 — Debugging، قابلیت ردیابی و روش بازتولید

- [ ] `TODO-085` **OPEN — راه‌اندازی Bug Reproduction Log:** یک قالب/فهرست واحد برای BUG-ID بسازید؛ برای هر یافته نقش کاربر، build/branch/SHA، محیط، دادهٔ seed، پیش‌شرط، گام‌های بازتولید، expected/actual، frequency، شدت، log/correlation ID، screenshot/trace، مالک، fix commit و regression test را ثبت کنید. در نبود شواهد، مورد `UNCONFIRMED` بماند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-083
- [ ] `TODO-086` **OPEN — تست logging و correlation:** درخواست وب/UI را تا API، application boundary، DB transaction و outbox با correlation/request ID قابل ردیابی کنید؛ در خطای عمدی باید IDهای مرتبط در log باشند، ولی OTP، token، password، فیش کامل یا PII غیرضروری نباید ظاهر شوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-085
- [ ] `TODO-087` **OPEN — تست خطاهای پردازش‌نشده:** در محیط تست، rejection کنترل‌نشدهٔ Promise، API exception، parsing error، render exception و پاسخ خراب را به‌صورت ایمن شبیه‌سازی کنید؛ برنامه نباید بی‌صدا خراب شود، صفحه سفید بدهد یا موفقیت جعلی نشان دهد. error boundary/global handler باید خطای قابل‌فهم و correlation ID ارائه دهد و جزئیات حساس را پنهان کند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-086
- [ ] `TODO-088` **OPEN — دیباگ API client و شبکه:** DNS/connection refused، timeout، قطع اتصال میان درخواست، HTTP error، JSON خراب، envelope نامعتبر، 204/empty response و cancellation را شبیه‌سازی کنید؛ timeout/retry فقط مطابق سیاست endpoint باشد و mutation غیرidempotent بی‌کلید دوباره ارسال نشود. UI باید بین خطای شبکه، مجوز، conflict و خطای سمت سرور تفاوت بگذارد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-087
- [ ] `TODO-089` **OPEN — Regression suite برای باگ‌های شناخته‌شده:** باگ‌های PR #30 را به تست‌های تکرارپذیر وصل کنید: شکست sync سبد و توقف checkout، سقف شمارنده OTP، ایزولاسیون OTP بین tenantها، stateهای تحویل و مجاز بودن مرحلهٔ بعد، Pre-APK gate برای هر دو variant و معتبر بودن expressionهای workflow. روی SHA جاری اجرا و نتیجهٔ هر مورد جداگانه ثبت شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-088
- [ ] `TODO-090` **OPEN — fixture، seed و پاکسازی تست:** seedها deterministic و ایزوله باشند؛ تست مستقل با ترتیب متفاوت یا اجرای دوباره نتیجهٔ یکسان بدهد؛ teardown داده‌های تست را پاک کند بدون اینکه DB دیگری را هدف بگیرد. داده‌های شناسه‌دار تست نباید با seed/staging/production مخلوط شوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-089
- [ ] `TODO-091` **OPEN — ایمنی تست مخرب و جداسازی محیط:** در اجرای migration، delete/cleanup، load و fault injection نام DB، host و environment را assert کنید؛ در صورت مقصد ناشناخته یا production، اجرای عملیات مخرب fail-closed شود. تست کنید QA credentials امکان تغییر DB اصلی را ندارند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-090

### D2 — پوشش قابلیت‌ها و مسیرهای کاربری Retailer

- [ ] `TODO-092` **OPEN — ماتریس Feature Acceptance:** از `MVP_SCREEN_MATRIX.md`، `MVP_API_MAP.md`، قراردادهای canonical و Decision Register، فهرست featureهای داخل MVP استخراج کنید. برای هر feature ثبت شود: persona/permission، UI surface، API/route، boundary/service، DB/event اثرگذار، مسیر موفق، مسیر منفی، تست خودکار، evidence و وضعیت. قابلیت خارج از scope را به تصمیم/سند وصل کنید؛ قابلیت را بر اساس حدس اضافه نکنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-091
- [ ] `TODO-093` **OPEN — Retailer onboarding و auth:** مسیر کاربر جدید/موجود، درخواست OTP، OTP اشتباه/منقضی/مصرف‌شده، retry و lockout، session refresh/revoke، انتخاب سازمان/پرسونا و خروج را از HTTP/UI موجود تست کنید. کاربر بدون عضویت معتبر یا tenant فعال نباید وارد dashboard یا دادهٔ خرید شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-092
- [ ] `TODO-094` **OPEN — کشف کاتالوگ و جست‌وجو:** جست‌وجوی دقیق/جزئی، فارسی/فاصله/کاراکترهای معمول، دسته‌بندی و فیلترهای واقعاً پشتیبانی‌شده، صفحه‌بندی، نتیجهٔ خالی، خطای API، آفر غیرفعال، قیمت تاریخ‌دار و موجودی stale را تست کنید. UI نباید محصول/قیمت/موجودی ساختگی را در حالت API failure نشان دهد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-093
- [ ] `TODO-095` **OPEN — جزئیات محصول و مقایسهٔ آفر:** SKU/barcode در صورت وجود، واحد/بسته‌بندی، MOQ/MOV، بنکدار، قیمت، زمان تازگی موجودی و وضعیت availability را با منبع API تطبیق دهید. تغییر قیمت یا موجودی بین مشاهدهٔ کالا و افزودن به سبد باید درست بازتاب یابد؛ داده‌های دو Vendor با هم مخلوط نشوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-094
- [ ] `TODO-096` **OPEN — رفتار کامل سبد خرید:** افزودن، افزایش/کاهش تعداد، حذف، سبد خالی، بازیابی پس از refresh/login، نسخهٔ قدیمی سبد، دو tab/device، item ناموجود، قیمت تغییرکرده و شکست sync سرور را آزمایش کنید. هر UI optimistic update باید با پاسخ واقعی reconcile شود؛ sync ناموفق نباید checkout را شروع کند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-095
- [ ] `TODO-097` **OPEN — Allocation و پیشنهاد چندبنکداری:** چند محصول/چند Vendor، MOQ/MOV، موجودی ناکافی، stale inventory، inactive offer، split به چند سفارش، کاهش مقدار و عدم تخصیص کامل را با دادهٔ قابل پیش‌بینی تست کنید. مقدار و قیمت نهایی، دلایل تخصیص/عدم تخصیص، reservation و وضعیت conflict در UI/API/DB باید با هم تطبیق داشته باشند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-096
- [ ] `TODO-098` **OPEN — Checkout و ثبت سفارش:** address/contact/اطلاعات لازم، مرور نهایی، اعتبارسنجی مجدد قیمت/موجودی، دو بار کلیک، refresh، timeout بعد از ارسال، response گم‌شده و retry را پوشش دهید. درخواست تکراری نباید OrderGroup، child order یا reservation تکراری بسازد؛ موفقیت فقط وقتی اعلام شود که نتیجه از سرور/DB تأیید شده باشد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-097
- [ ] `TODO-099` **OPEN — فهرست، جزئیات و timeline سفارش:** پس از checkout، Retailer باید سفارش گروهی و سفارش‌های فرزند را ببیند؛ accept/reject/partial-acceptance/timeout/cancelled، علت رد/لغو، timestamps و پیشنهاد در انتظار باید درست نمایش داده شوند. refresh/deep-link/ورود مجدد نباید دادهٔ stale یا متعلق به کاربر دیگر نشان دهد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-098
- [ ] `TODO-100` **OPEN — مسیر تحویل و POD از دید Retailer:** ASSIGNED → PICKED_UP → IN_TRANSIT → ARRIVED → DELIVERED/FAILED را بر اساس state canonical تست کنید؛ OTP صحیح/غلط/تکراری/منقضی مطابق سیاست مصوب، رسید/تصویر آماده، رد درب منزل و مسیر استثنا را پوشش دهید. Retailer نباید اقدام Vendor را اجرا کند و برعکس؛ failure نباید تحویل موفق ثبت کند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-099
- [ ] `TODO-101` **OPEN — پرداخت مستقیم، رسید و فاکتور:** انتخاب روش پرداخت مجاز، بارگذاری مدرک، پیگیری شناسه، وضعیت pending/verified/rejected/mismatch، رسید تکراری، دسترسی به فاکتور و نمایش تسویه را بررسی کنید. ادعای پرداخت از سوی Retailer نباید معادل تأیید Vendor/Ops شود؛ مسیر واقعی `direct-receipt` و منبع اعتماد reconciliation طبق قرارداد جاری تست شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-100
- [ ] `TODO-102` **OPEN — Dispute، RMA و refund از دید Retailer:** ثبت مشکل در پنجره/شرایط مجاز، انتخاب قلم و تعداد، افزودن مدرک، مشاهدهٔ بررسی/تصمیم، نتیجه و وضعیت refund/adjustment را تست کنید. درخواست تکراری، deadline منقضی، تعداد بیش از خرید، دخالت در سفارش غیرخودی و تأیید مالی غیرمجاز باید رد شوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-101
- [ ] `TODO-103` **OPEN — Support، inbox و اعلان‌های Retailer:** ایجاد/دیدن case، ارسال پیام، پاسخ اپراتور، خوانده‌شدن/نخوانده‌شدن، preferences، deep-link، دریافت اعلان و رویداد تکراری را تست کنید. اعلان یک کاربر نباید به عضویت/tenant دیگر برسد؛ لینک منقضی/غیرمجاز باید به مسیر امن هدایت شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-102

### D3 — پوشش قابلیت‌ها و مسیرهای کاربری Vendor، Ops و Field

- [ ] `TODO-104` **OPEN — Vendor onboarding و دسترسی:** انتخاب context سازمان، عضویت owner/staff، پروفایل، session و dashboard را تست کنید؛ staff مجاز به عملیات owner-only مثل تأییدهای حساس یا تغییر مالی نباشد مگر ماتریس مجوز رسمی اجازه دهد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-103
- [ ] `TODO-105` **OPEN — Vendor catalog management:** ایجاد/ویرایش/فعال‌سازی/غیرفعال‌سازی listing، اتصال SKU/barcode، بسته‌بندی و نمایش در کاتالوگ Retailer را تست کنید. ورودی تکراری/ناقص، محصول نامعتبر، تغییر بدون permission و نشت فیلدهای داخلی به client باید پوشش داده شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-104
- [ ] `TODO-106` **OPEN — Vendor pricing:** ایجاد و تغییر قیمت، effective dates، جلوگیری از بازه‌های هم‌پوشان در صورت منع قرارداد، قیمت آینده/منقضی و اثر قیمت جدید بر basket و checkout را تست کنید. تاریخچه قیمت نباید دستکاری شود و checkout باید قیمت canonical و معتبر را دوباره بررسی کند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-105
- [ ] `TODO-107` **OPEN — Vendor inventory و تأیید روزانه:** ثبت مقدار، reserved/available، publish، freshness، stale/unknown، daily confirmation، یادآوری و آزادسازی/مصرف/انقضای reservation را تست کنید. مقدار available منفی، oversell، تأیید تکراری یا دسترسی به موجودی Vendor دیگر نباید رخ دهد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-106
- [ ] `TODO-108` **OPEN — Vendor order response:** صف سفارش‌های ورودی، جزئیات و timeline؛ accept، reject با علت، پیشنهاد partial acceptance، تأیید/رد پیشنهاد، timeout و اقدامات تکراری را تست کنید. فقط actor و state مجاز می‌توانند transition ایجاد کنند و notification/outbox و reservation با نتیجه هماهنگ باشند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-107
- [ ] `TODO-109` **OPEN — Vendor fulfillment، dispatch و handoff:** مراحل آماده‌سازی و تحویل به مسئول حمل، timestampها، اقلام/مقادیر، تأیید مجدد و خطای dispatch را تست کنید. dispatch یا delivery confirmation تکراری نباید ثبت شود؛ Vendor نباید stateهای خارج از اختیارش را دور بزند و Retailer نباید مسیر داخلی Vendor را ببیند مگر قرارداد مجاز بداند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-108
- [ ] `TODO-110` **OPEN — Vendor مالی، invoice و dispute:** مشاهدهٔ وضعیت رسید/تأیید پرداخت، فاکتور، تسویه، مغایرت و پاسخ Vendor به dispute/RMA را تست کنید؛ Vendor A نباید داده، رسید یا settlement مربوط به Vendor B را ببیند یا تغییر دهد. عملیات حساس باید audit و idempotency داشته باشند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-109
- [ ] `TODO-111` **OPEN — Ops/Admin exception flows:** فقط قابلیت‌های ثبت‌شده در screen/API matrix را پوشش دهید: جست‌وجو و context سفارش، exception/timeout queue، inventory/payment discrepancy، dispute/RMA، support، category/vendor/user operation و audit. آزمون کنید که دسترسی elevated نیازمند نقش درست است و هیچ عملیات admin به‌صورت پنهانی یا بدون audit اجرا نمی‌شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-110
- [ ] `TODO-112` **OPEN — Field tasks و عملیات onboarding در صورت وجود در scope:** task list، فعال‌سازی بنکدار/خرده‌فروش، آموزش، اولین سفارش و ثبت evidence را فقط در صورت وجود در canonical screen matrix/API map تست کنید. اگر خارج از MVP یا هنوز اجرا نشده، تصمیم/Gap را ثبت کنید؛ feature جدید از روی چک‌لیست تاریخی اختراع نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-111
- [ ] `TODO-113` **OPEN — تطبیق نقش، منو، صفحه و API:** برای هر persona شامل Retailer owner/staff، Vendor owner/staff و Ops/Admin، منوها، صفحه‌ها، دکمه‌ها و APIها را با permission matrix مقایسه کنید. کنترل UI تنها کافی نیست؛ endpoint هم باید permission را enforce کند. Direct URL، تغییر ID، deep-link و API دستیِ غیرمجاز را امتحان کنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-112

### D4 — کیفیت فرم، stateها، مسیر حرکت و تجربهٔ کاربر

- [ ] `TODO-114` **OPEN — اعتبارسنجی فرم و بومی‌سازی فارسی:** شماره موبایل طبق قرارداد، OTP چهاررقمی، فیلد اجباری/اختیاری، فاصله و نویسهٔ نامعتبر، فارسی/لاتین، اعداد و قالب پول، جداکننده‌ها و خطای server validation را بررسی کنید. مقدار نمایش‌داده‌شده با مقدار ارسالی/ذخیره‌شده یکی باشد؛ قوانین بیزینسی در frontend به‌تنهایی enforce نشوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-113
- [ ] `TODO-115` **OPEN — پوشش stateهای هر صفحه:** برای تمام screen/stateهای موردنیاز، loading، skeleton در صورت وجود، empty, success, error, retry, disabled, unauthorized, stale, conflict و submit-in-progress را بررسی کنید. دکمهٔ submit نباید mutation موازی ایجاد کند؛ صفحه نباید با خطای API، اطلاعات قدیمی را به‌عنوان تازه جا بزند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-114
- [ ] `TODO-116` **OPEN — navigation و بازگشت به جریان:** back/forward، refresh، tab duplication، deep-link، ورود به صفحه از notification، redirect پس از login، session expiry، route ناموجود و شروع دوبارهٔ جریان را در browser/component tests بررسی کنید. هنگام بازگشت به checkout/فرم مالی، state و idempotency باید امن بماند و route خصوصی با session باطل نمایش داده نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-115
- [ ] `TODO-117` **OPEN — انیمیشن، motion و lifecycle در کد قابل‌آزمون:** ترتیب transition، پایان animation، gesture interruption، navigation سریع و unmount در حین request را در تست component/automation بررسی کنید. animation نباید state را قفل کند، دوبار submit انجام دهد یا focus را گم کند؛ reduced-motion پشتیبانی‌شده را نیز تست کنید. تست روی دستگاه واقعی طبق TODO-023 جداگانه لازم است. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-116
- [ ] `TODO-118` **OPEN — offline/weak network و recovery مسیر:** در تست client/service worker یا browser، اتصال ضعیف، قطع و وصل، timeout، پاسخ دیررس، دو پاسخ خارج از ترتیب، cache stale و retry را کنترل کنید. UI باید وضعیت pending/conflict/retry را روشن نشان دهد و هیچ سفارش/پرداخت تکراری یا گم‌شدن تغییر محلی رخ ندهد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-117
- [ ] `TODO-119` **OPEN — raceهای تعاملی کاربر:** double click، چند بار tap، submit با Enter، back حین ارسال، refresh حین checkout، چند tab برای یک basket و دو کاربر روی آخرین موجودی را آزمایش کنید. کنترل UI با قفل/disable باید با idempotency و transaction سمت سرور تکمیل شود؛ تست frontend نباید جای concurrency تست DB/API را بگیرد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-118
- [ ] `TODO-120` **OPEN — امنیت client و داده‌های حساس:** token/session storage، logout و پاک‌سازی context، screenshot/log redaction، open redirect، deep-link spoofing، external URL، injection در text fields و نمایش خطای backend را بررسی کنید. از ثبت token، OTP، شمارهٔ کامل حساس یا محتوای مدرک در log و analytics جلوگیری شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-119
- [ ] `TODO-121` **OPEN — رفتار اعلان تا مقصد:** برای هر event بحرانی، outbox → inbox/provider status → notification click → destination screen را با نقش‌های متفاوت تست کنید. deep-link باید login/context لازم را حفظ کند، مقصد غیرمجاز را مسدود کند و event/notification تکراری به action یا record تکراری منجر نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-120
- [ ] `TODO-122` **OPEN — visual regression و responsive قبل از native build:** در browser QA از viewportهای پشتیبانی‌شده screenshot baseline بگیرید؛ overflow، table/card، dialog/drawer، keyboard، RTL، فونت فارسی، متن طولانی، loading/error/empty و dark/light موجود را مقایسه کنید. اختلاف معنی‌دار با screenshot مرجع باید به BUG-ID وصل شود؛ baseline را برای پنهان‌کردن defect خودکار به‌روزرسانی نکنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-121
- [ ] `TODO-123` **OPEN — browser E2E برای هر دو نقش و حالت backend:** جریان‌های اصلی Retailer/Vendor را روی web واقعی اجرا کنید؛ در یک run به mock صریح و در run دیگر به backend تستی متصل شوید. base URL، حساب‌های تست، fixtures و DB مقصد باید در report معلوم باشد. نتیجه mock و live در یک PASS ادغام نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-122

### D5 — مسیرهای سراسری، fault injection و امضای پذیرش

- [ ] `TODO-124` **OPEN — E2E cross-persona برای یک سفارش واحد:** با Retailer و Vendor جداگانه، یک سفارش تست را از ایجاد basket تا fulfillment/delivery و payment-status دنبال کنید؛ هر persona فقط view/action مجاز خود را داشته باشد و تغییر state در client دیگر پس از refresh به‌روز شود. شناسه‌های سفارش، eventها، زمان‌ها و state DB با timeline API تطبیق داده شوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-123
- [ ] `TODO-125` **OPEN — fault injection و graceful recovery:** برای dependencyهای تحت کنترل، DB transaction rollback، API 5xx/timeout، provider unavailable، outbox worker stop/restart، media unavailable و failure پس از commit را تست کنید. اثبات شود retry باعث duplicate side effect نمی‌شود، عملیات ناقص یا reconcile می‌شود یا وضعیت شکست آشکار دارد؛ secret واقعی و تولید در تست fault استفاده نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-124
- [ ] `TODO-126` **OPEN — regression scope بعد از هر fix:** برای هر BUG-ID تغییرکرده، لیست تست‌های مستقیم و وابسته را تعیین کنید (unit → component/contract → integration → E2E → security/concurrency). با تغییر source/schema/API/config، نتیجهٔ قبلی باطل‌شده مشخص شود و تست‌ها روی SHA جدید اجرا شوند؛ هیچ bug fix بدون regression evidence بسته نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-125
- [ ] `TODO-127` **OPEN — baseline کارایی و پایداری جریان‌های اصلی:** زمان پاسخ و خطای APIهای critical، زمان render و startup قابل‌سنجش در محیط فعلی، تعداد queryهای مشکوک و رفتار با صفحه‌بندی/دادهٔ بزرگ را baseline کنید. threshold را از SLO/تصمیم موجود بگیرید؛ اگر وجود ندارد نتیجه را اندازه‌گیری و تصمیم لازم ثبت کنید، نه اینکه حد عددی اختراع شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-126
- [ ] `TODO-128` **OPEN — accessibility و ورودی‌های دستگاه‌محورِ قابل‌تست پیش از build:** keyboard navigation، focus visibility، labels، semantic controls، screen-reader metadata، zoom/font scaling و reduced motion در browser/component tests را بررسی کنید. مواردی مثل permission prompt، safe-area واقعی، IME و lifecycle دستگاه در TODO-018…TODO-024 پس از QA build بررسی می‌شوند و اینجا PASS تلقی نمی‌شوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-127
- [ ] `TODO-129` **OPEN — Bug Bash و triage مشترک:** با یک reviewer مستقل، مسیرهای Retailer/Vendor/Ops و همهٔ featureهای `TODO-092` را از روی acceptance matrix بررسی کنید؛ یافته‌های جدید BUG-ID بگیرند، severity/owner/repro/evidence داشته باشند و P0/P1 تا رفع و rerun باز بمانند. فقط نگاه چشمی بدون ثبت step-by-step کافی نیست. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-128
- [ ] `TODO-130` **OPEN — گزارش پوشش Feature × User Journey × Test:** برای هر feature داخل MVP، مسیر موفق/منفی، نقش/مجوز، stateها، route، API/DB evidence، تست خودکار یا blocker دلیل‌دار را در ماتریس پذیرش درج کنید. هر feature بدون تست یا تصمیم صریح `OPEN` می‌ماند. مالک فنی باید بررسی کند هیچ مسیر P0/P1 بدون پوشش/تصمیم باقی نمانده باشد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-129

## تست‌های افزوده‌شده پس از مقایسه با استانداردها و راهنماهای عمومی صنعت

**نتیجهٔ تحقیق در تاریخ 2026-10-12:** چک‌لیست موجود از قبل پوشش گسترده‌ای برای verification suite، API/HTTP، tenant isolation، ماشین‌های وضعیت، concurrency/idempotency، debugging، user journeys، fault injection، تست مرورگر، baseline کارایی و accessibility داشت. با این حال، چند مورد استانداردی یا به شکل صریح ماتریس‌دار نبودند، یا نیاز به تستی داشتند که فقط پس از ساخت و نصب APK ممکن است. موارد زیر برای تکمیل پوشش اضافه شده‌اند؛ تکرارهای صرفاً لفظی به‌عنوان تست جدید شمرده نشده‌اند.

### نتیجهٔ مقایسه: چه پوشش‌هایی کامل‌تر شد؟

| مرجع | پوشش مورد انتظار از مرجع | پوشش قبلی TODO | افزوده/شفاف‌سازی‌شده |
|---|---|---|---|
| OWASP API Security Top 10 | object/property/function authorization، authentication، resource exhaustion، business-flow abuse، misconfiguration، inventory و third-party API safety | tenant/RBAC و Auth وجود داشتند؛ نه تمام دسته‌ها به‌عنوان یک ماتریس پذیرش مستقل | TODO-131 تا TODO-133 |
| OWASP MASVS/MASTG | امنیت ذخیره‌سازی محلی، transport، permission، platform interaction، privacy و دادهٔ حساس در log/backup/notification/screenshot | چند مورد عمومی امنیت موبایل وجود داشت؛ بررسی ساختاریافتهٔ MASVS و شواهد runtime صریح نبود | TODO-137 تا TODO-139 |
| Android Core App Quality | پیمایش تمام صفحات/جریان‌ها، app switcher، sleep/lock/resume، interruptions، connectivity، permission و device coverage، performance | برخی از این موارد داخل TODO-018…024 بودند اما به‌عنوان ماتریس رسمی شرایط دستگاه و lifecycle تفکیک نشده بودند | TODO-140 تا TODO-142 و TODO-146 |
| Expo و Maestro | unit/component تست به‌علاوهٔ E2E روی app/device واقعی؛ snapshot به‌تنهایی برای UI acceptance کافی نیست | unit و browser E2E پوشش داشتند؛ E2E black-box روی binary موبایل نیازمند گیت واضح بود | TODO-143 |
| Playwright | تست رفتار قابل‌مشاهدهٔ کاربر، ایزوله‌بودن تست‌ها، assertionهای مقاوم و پرهیز از وابستگی به زمان‌بندی شکننده | مرورگر E2E و seed وجود داشت؛ سیاست flakiness و شواهد شکست CI صریح‌تر شد | TODO-123 و TODO-136 |
| W3C WCAG 2.2 | ارزیابی سیستماتیک keyboard، focus، labels، contrast و interaction/accessibility | accessibility به‌طور کلی وجود داشت؛ معیارهای پذیرش و ثبت خروجی automated + manual صریح نبود | TODO-144 (web/components)، TODO-151 (mobile device) |
| Core Web Vitals | اندازه‌گیری LCP/INP/CLS، با هدف‌های خوب در صدک 75 و تفکیک mobile/desktop | baseline کارایی عمومی وجود داشت؛ سنجه‌ها و آستانه‌های وب کانونیکال نبودند | TODO-145 |
| NIST SSDF و تست‌های performance/recovery | تکرارپذیری، تست امن در زنجیرهٔ توسعه، load/recovery و کنترل artifact | recovery/backup و load به‌طور کلی در checklist قدیمی دیده می‌شد، اما شواهد current SHA و حدود بار مشخص نبود | TODO-147 تا TODO-150 |

**تفکیک حیاتی:** `PRE-BUILD` یعنی تست روی source، API/DB test environment، browser یا config قابل‌بررسی قبل از تولید APK. `POST-QA-APK` یعنی تستی که نیازمند binary نصب‌شده، دسترسی Android/ADB، permission dialog یا رفتار واقعی سیستم‌عامل است. مورد دوم را نباید به‌عنوان PASS پیش از ساخت گزارش کرد؛ فقط باید پیش از release build تکمیل شود.

### R1 — API Security و robustness تکمیلی

- [ ] `TODO-131` **OPEN · PRE-BUILD — ماتریس صریح OWASP API Security Top 10:** برای endpointهای واقعی MVP ماتریس endpoint × persona × resource × property × allowed action تهیه کنید. دست‌کم BOLA/IDOR، property-level authorization و mass assignment، broken function-level authorization، authentication، security misconfiguration، inventory/version drift و unsafe consumption of third-party responses را تست کنید. SSRF فقط در صورت وجود endpoint ورودی URL/webhook/fetch بررسی شود؛ اگر feature در scope نیست، دلیل عدم کاربرد را ثبت کنید. برای هر مورد تست منفی HTTP و evidence لازم است. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-071 و TODO-069
- [ ] `TODO-132` **OPEN · PRE-BUILD — محدودیت منابع و سوءاستفاده از جریان حساس:** OTP، login، جست‌وجو، pagination، ایجاد basket/order، آپلود مدرک و عملیات پرهزینهٔ provider را از نظر rate limit، سقف body/page size، هزینهٔ SMS، درخواست‌های خودکار و تکرار سریع بررسی کنید. تست load/abuse فقط روی محیط مجاز و DB ایزوله اجرا شود؛ هر سقف باید از policy/SLO ثبت‌شده بیاید و عدد تجاری جدید اختراع نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-131 و TODO-070
- [ ] `TODO-133` **OPEN · PRE-BUILD — صحت مصرف APIها و configuration exposure:** تنظیمات CORS/TLS/headers، URLهای محیطی، endpointهای deprecated یا فراموش‌شده، timeoutهای provider، اعتبارسنجی پاسخ provider و fail-closed در پاسخ نامعتبر/غیرمنتظره را بررسی کنید. URL fetching/SSRF و callback verification را فقط در نقاطی آزمایش کنید که از نظر کد واقعاً وجود دارند؛ گزارش false-positive ایجاد نکنید. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-131
- [ ] `TODO-134` **OPEN · PRE-BUILD — fuzz/property-based و تست مرزی:** برای schemaها و منطق محاسباتی، ورودی‌های صفر/منفی/بسیار بزرگ، decimal/rounding، quantity overflow، رشتهٔ Unicode/فارسی، control character، مقادیر null/حذف‌شده، آرایهٔ خالی، pagination boundary، timestamp/time-zone، payload اضافی و JSON خراب را بررسی کنید. از property-based/fuzz tooling موجود استفاده کنید یا کمبود ابزار را ثبت کنید؛ invariantهای قیمت، مقدار، tenant، وضعیت و idempotency نباید شکسته شوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-072
- [ ] `TODO-135` **OPEN · PRE-BUILD — API contract drift و backward compatibility:** OpenAPI/response schema واقعی را با `MVP_API_MAP.md`، client types و تست‌های قرارداد مقایسه کنید؛ تفاوت ناخواستهٔ required fields، enum، status code، envelope، pagination و error shape را fail کنید. سازگاری تغییرات با clientهای پشتیبانی‌شده و نسخه‌های migration را بررسی کنید؛ اختلاف intentional باید با تصمیم/نسخه‌گذاری ثبت شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-069
- [ ] `TODO-136` **OPEN · PRE-BUILD — flakiness، استقلال و قابلیت تشخیص شکست CI:** suiteهای مرتبط را حداقل در اجرای مستقل/تکراری و ترتیب متفاوت بررسی کنید؛ تست‌های وابسته به زمان ثابت، sleepهای بی‌دلیل، seed مشترک و order-dependent state را پیدا کنید. برای browser tests از locatorهای قابل‌دسترسی و assertionهای auto-retry استفاده کنید؛ retry نباید شکست اولیه را پنهان کند. شکست باید trace/log/screenshot و seed قابل‌بازتولید داشته باشد و CI result روی همان SHA ثبت شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-067 و TODO-123

### R2 — امنیت بستهٔ Android و privacy

- [ ] `TODO-137` **OPEN · POST-QA-APK — MASVS/MASTG: دادهٔ حساس در runtime:** روی APK نصب‌شده بررسی کنید که OTP/token/session، اطلاعات تماس، فیش و مدرک تحویل در logcat، clipboard، keyboard cache، local storage، app backup، notification preview و screenshot صفحهٔ Recent Apps افشا نمی‌شوند. اگر اطلاعات حساس در background قابل مشاهده است، defect ثبت و اصلاح شود؛ این تست بدون APK/runtime قابل PASS نیست. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-009، TODO-138 و TODO-139
- [ ] `TODO-138` **OPEN · PRE-BUILD — بازبینی ایستای بسته و تنظیمات امنیت Android:** configهای Expo/Gradle/Manifest را برای package ID هر variant، debug/release flag، cleartext traffic، exported component، deep link/app link، permissions، backup rules، signing config و endpoint مقصد بازبینی کنید. secrets نباید داخل JavaScript bundle، source map، native resources یا artifact نهایی باشند. فقط تنظیمات موردنیاز محصول فعال بمانند؛ هر تغییر native بعد از prebuild با config قابل‌بازتولید sync باشد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-082 و TODO-083
- [ ] `TODO-139` **OPEN · PRE-BUILD — third-party SDK و permission/privacy inventory:** تمام SDKها و کتابخانه‌هایی که داده جمع‌آوری/ارسال می‌کنند، permissions درخواست‌شده، کاربردشان، data destinations و license/vulnerability status را فهرست کنید. permission غیرضروری حذف شود؛ permission حساس فقط برای جریان لازم درخواست شود. برای هر دادهٔ شخصی، مسیر UI → storage/log/analytics/provider و دلیل جمع‌آوری را مستند کنید. بخش runtime این ممیزی در TODO-137 و TODO-141 دوباره بررسی شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-082 و TODO-083

### R3 — تست‌های نیازمند APK آزمایشی و دستگاه واقعی

- [ ] `TODO-140` **OPEN · POST-QA-APK — install/upgrade/uninstall lifecycle:** نصب تمیز هر دو variant، به‌روزرسانی از آخرین نسخهٔ پشتیبانی‌شده، اجرای مجدد پس از update، logout/login، reinstall و رفتار دادهٔ محلی/backup را تست کنید. downgrade فقط اگر رسماً پشتیبانی می‌شود آزمایش شود. package ID، نسخه، signature، schema/data compatibility و نتیجهٔ حفظ یا پاک‌سازی داده ثبت شوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-009 و TODO-138
- [ ] `TODO-141` **OPEN · POST-QA-APK — Android lifecycle و interruption matrix:** از صفحه‌های مختلف Home/Recents، جابه‌جایی بین اپ‌ها، قفل/خواب و بیداری، process kill/recreate، notification/call interruption، permission grant/deny/revoke، orientation/keyboard، battery saver/Doze و قطع/وصل Wi‑Fi/mobile data را آزمایش کنید. بعد از resume باید session، form/basket state و وضعیت عملیات درست باشد؛ action مالی/سفارشی نباید دوباره اجرا شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-009 و TODO-140
- [ ] `TODO-142` **OPEN · POST-QA-APK — device/form-factor compatibility:** ماتریس نمایندهٔ نسخه‌های Android، رزولوشن/density، اندازهٔ فونت، دستگاه کم‌منبع و شبکهٔ ضعیف را مطابق user base هدف تعریف کنید. حداقل روی یک emulator و یک دستگاه واقعی در صورت دسترسی اجرا شود؛ latest supported Android نیز بررسی گردد. فهرست دقیق دستگاه/OS و موارد خارج از پوشش ثبت شود؛ نبود دستگاه باید blocker بماند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-009 و TODO-141
- [ ] `TODO-143` **OPEN · POST-QA-APK — black-box mobile E2E:** برای APK واقعی Retailer و Vendor، flowهای ورود، search/catalog، basket/order، vendor accept/fulfillment، error/retry و logout را با Maestro یا ابزار سازگار دیگر اجرا کنید. locatorهای پایدار/accessibility testID استفاده شوند؛ test run باید package ID را هدف بگیرد و trace/screenshot/خطای مرحله را artifact کند. Expo export یا component test جای این آزمون نیست. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-009 و TODO-142
- [ ] `TODO-144` **OPEN · PRE-BUILD — آزمون accessibility/WCAG 2.2 برای وب و componentها:** UI قابل‌آزمون پیش از APK با keyboard-only، focus order/visibility، labels، error identification، contrast و semantic roles بررسی شود. ابزار خودکار به‌تنهایی کافی نیست؛ manual test و موارد استثنا باید ثبت شود. آزمون TalkBack، font scaling و هدف‌های تعاملی روی APK در TODO-151 ثبت می‌شوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-128
- [ ] `TODO-145` **OPEN · PRE-BUILD — Web Core Web Vitals و بودجهٔ کارایی:** در build تولیدی وب و محیط آزمون با viewport موبایل و دسکتاپ، LCP/INP/CLS را اندازه‌گیری کنید. معیار مرجع «خوب» در صدک 75: LCP ≤ 2.5 ثانیه، INP ≤ 200 میلی‌ثانیه و CLS ≤ 0.1؛ در آزمایشگاه INP واقعی همیشه قابل‌اندازه‌گیری نیست، پس TBT را فقط به‌عنوان proxy آزمایشگاهی ثبت کنید. گزارش per-route و artifact حفظ شود؛ هدف محصولی متفاوت باید مستند تصویب شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-076 و TODO-122
- [ ] `TODO-146` **OPEN · POST-QA-APK — عملکرد و پایداری Android:** زمان cold/warm startup، پاسخ UI، scroll/jank فهرست‌های بزرگ، مصرف حافظه، crash/ANR، resume و رفتار دستگاه کم‌منبع را اندازه بگیرید. برای loading طولانی feedback روشن نشان داده شود؛ عددهای هدف پروژه از SLO/product decision بیایند. regression روی device/build SHA متفاوت قابل مقایسه ثبت شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-009 و TODO-142

### R4 — بار، بازیابی و سازگاری انتشار

- [ ] `TODO-147` **OPEN · PRE-BUILD — performance/load test جریان‌های واقعی API:** روی staging یا محیط تست ایزوله، ابتدا smoke، سپس load/stress/spike و در صورت امکان soak اجرا کنید؛ جریان‌های OTP (با mock/provider قابل‌کنترل)، search, basket, allocation, checkout, vendor actions و timeline را با concurrency و data volume نزدیک به سناریوی موردانتظار pilot بررسی کنید. قبل از اجرا تعداد کاربر/درخواست مورد انتظار و آستانهٔ latency/error تعیین شود؛ تست هرگز روی production و بدون سقف هزینه/نظارت provider اجرا نشود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-075، TODO-127 و TODO-132
- [ ] `TODO-148` **OPEN · PRE-RELEASE — backup/restore و recovery drill:** در محیط غیرتولیدی backup پایگاه داده را restore کنید و تعداد/قیود کلیدی، دادهٔ نمونه، سلامت migration، `/readyz`, worker/outbox و قابلیت ورود/خواندن یک سفارش را بعد از recovery راستی‌آزمایی کنید. خرابی DB/worker را کنترل‌شده شبیه‌سازی کنید؛ زمان restore و دادهٔ قابل‌از‌دست‌رفتن اندازه‌گیری و در runbook ثبت شوند. اگر زیرساخت/credential لازم نیست، تست محلی کافی نیست؛ محیط هدف هم باید در مرحلهٔ استیجینگ بررسی شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-027، TODO-029، TODO-031، TODO-032 و TODO-033؛ به SMS زنده نیاز ندارد
- [ ] `TODO-149` **OPEN · PRE-BUILD — build provenance و supply-chain evidence (بخش source/config):** برای هر variant نسخهٔ dependency، lockfile، SBOM در صورت پشتیبانی tooling، vulnerability/license report، source SHA، native config، package ID، environment endpoint و تنظیمات signing را پیش از gate ثبت کنید. source/bundle قابل‌بررسی نباید secret، test account/data یا endpoint تست ناخواسته داشته باشد. signing key/secret را در فایل TODO یا log ننویسید. بررسی hash و signature واقعی APK به TODO-152 مربوط است. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-083 و TODO-138
- [ ] `TODO-150` **OPEN · POST-QA-APK / PRE-RELEASE — ماتریس سازگاری app/API/DB و migration:** مشخص کنید appهای Retailer/Vendor کدام schema/endpoint contract را انتظار دارند؛ سناریوی migration، restart و deployment را در محیط غیرتولیدی، با APK آزمایشی متصل به API و DB سازگار، اجرا کنید. API/DB rollout نباید client پشتیبانی‌شده را به‌طور خاموش بشکند؛ backward-incompatible change نیازمند نسخه‌گذاری، تصمیم رسمی و تست/پلن rollout است. rollback/forward-fix امن و readiness پس از migration اثبات شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-009، TODO-065، TODO-135 و TODO-148

- [ ] `TODO-151` **OPEN · POST-QA-APK — mobile accessibility روی دستگاه:** روی APK نصب‌شدهٔ هر دو variant، TalkBack و ترتیب خواندن، برچسب کنترل‌ها، پیام خطاها، بزرگ‌نمایی/اندازهٔ فونت، targetهای تعاملی، فوکوس و حرکت‌های ضروری را آزمایش کنید. جریان‌های اصلی سفارش باید بدون اتکا به رنگ/آیکون تنها قابل‌فهم و تکمیل باشند؛ نقص‌ها با screenshot و گام بازتولید ثبت شوند. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-009، TODO-144 و TODO-142
- [ ] `TODO-152` **OPEN · POST-QA-APK — راستی‌آزمایی artifact آزمایشی واقعی:** برای APK آزمایشی هر دو variant ساخته‌شده در TODO-009، package/application ID، versionCode/versionName، signature، hash، manifest/permissions، endpoint مقصد، نبود debug flag و نبود secret/test account/data را با ابزارهای مناسب بررسی کنید. hash/signature و SHA سورس باید قابل‌ردیابی باشند؛ صرف موفقیت Gradle یا Expo build کافی نیست. بررسی نهایی release artifact نیز در TODO-056 ثبت شود. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-009، TODO-138 و TODO-149

### قوانین ترتیب برای تست‌های استانداردی جدید

- `TODO-131`…`TODO-136`، `TODO-138`، `TODO-139`، `TODO-144`، `TODO-145`، `TODO-147` و `TODO-149` باید پیش از نهایی‌کردن `TODO-084` شواهد داشته باشند.
- `TODO-137`، `TODO-140`…`TODO-143`، `TODO-146`، `TODO-150`…`TODO-152` نیازمند APK نصب‌شده‌اند؛ `TODO-148` و `TODO-150` به استیجینگ/بازیابی نیز نیاز دارند. این موارد باید پس از `TODO-009` و پیش از release/pilot بسته شوند و نباید به‌عنوان PASS در گزارش pre-build gate نوشته شوند.
- تست مستقل/غیرقابل‌کاربرد فقط با دلیل مستند و تأیید مالک فنی می‌تواند `N/A` شود؛ نبود ابزار یا دستگاه `BLOCKED_EXTERNAL` است نه PASS.

### گیت نهایی pre-build (شناسهٔ تاریخی TODO-084)

`TODO-084` یک شناسهٔ موجود است و برای حفظ traceability تغییر نمی‌کند، اما **از نظر وابستگی در آخر اجرا می‌شود**: فقط پس از `TODO-061`…`TODO-083`، `TODO-085`…`TODO-130` و موارد PRE-BUILD لازم از `TODO-131`…`TODO-136`، `TODO-138`، `TODO-139`، `TODO-144`، `TODO-145`، `TODO-147` و `TODO-149`. این gate باید نتیجهٔ debugging، تمام user journeyها، ماتریس featureها، تست‌های رگرسیون و triage را در یک گزارش واحد جمع‌بندی کند. سپس فقط در صورت عبور معیارهای پذیرش، `TODO-009` می‌تواند QA-only APK بسازد.


### تست‌هایی که عمداً بعد از QA-only build ولی قبل از Release build هستند

این موارد به APK نصب‌شده نیاز دارند؛ بنابراین مرحلهٔ قبل از build نمی‌تواند جایگزین‌شان شود. آن‌ها در شناسه‌های زنجیرهٔ زیر پوشش داده شده‌اند و باید قبل از release package تکمیل شوند:

- `TODO-018` تا `TODO-020`: runtime، نصب، هویت package/signature، cold start، relaunch، login/session، deep links، permissions، API base URL، keyboard/safe-area، network transition، offline/timeout/retry، background/resume، force close و session expiry.
- `TODO-021` تا `TODO-024`: تطبیق inventory واقعی با screen matrix، capture تمام stateهای ضروری، motion/lifecycle، RTL، responsive، dark/light و accessibility؛ هر defect با گام بازتولید و evidence ثبت شود.
- `TODO-025`: browser/Vercel QA باید از DB اصلی/production کاملاً جدا بماند؛ mock status به‌وضوح ثبت شود.
- بعد از هر fix، regression مرتبط و گیت‌های بی‌اعتبارشده را دوباره روی SHA جدید اجرا کنید. release APK/AAB فقط از SHA تأییدشده ساخته شود؛ artifact و checksum نهایی در `TODO-056` ثبت شود.

## آخرین گیت بیرونی پس از تکمیل تست‌ها

- [ ] `TODO-153` **OPEN · FINAL EXTERNAL GATE — دامنه، DNS و HTTPS عمومی:** فقط پس از قبولی software tests، QA APK/device tests و آماده‌شدن staging، رکوردهای DNS را در registrar/CDN اعمال کنید؛ delegation/NS، A/AAAA/CNAME، propagation، TLS certificate، redirect/renewal، CORS allowlist، API base URL برای هر دو variant، deep-link/app-link و endpointهای callback را روی محیط هدف تأیید کنید. health/readiness، لاگ بدون secret، firewall و rollback را بررسی کنید. هیچ credential در TODO ثبت نشود. تست‌های قبلی باید دامنه‌ندار باقی بمانند و این مرحله نباید بهانه‌ای برای جلو انداختن SMS زنده باشد. | مالک: تعیین‌نشده | پیش‌نیاز: TODO-018…TODO-024، TODO-029، TODO-030، TODO-032، TODO-033، TODO-054، TODO-137، TODO-140…TODO-143، TODO-146، TODO-151…TODO-152 و آمادگی staging

## منابعی که در این تجمیع بررسی شدند

- `mvp/BUILD_PLAN.md` — مرجع برنامهٔ باقی‌ماندهٔ MVP (وضعیت بازیابی‌شده در یادداشت‌های سپتامبر).
- `mvp/MVP_KNOWN_GAPS.md` — گپ‌های شناخته‌شده، از جمله مسیر رسید پرداخت/reconciliation.
- `POL_MVP_Master_Checklist_2026-09-18.md` — چک‌لیست قدیمی و گسترده؛ فقط برای کشف نواحی نیازمند revalidation استفاده شد، نه به‌عنوان وضعیت جاری همهٔ موارد.
- `POL_2.3_MASTER_GAP_REGISTER_2026-09-26_V2.md` — رجیستر gapها؛ برخی موارد صراحتاً `LEGACY_REVALIDATE` هستند.
- `Pasted markdown(20260926-125152).md` و گزارش‌های certification مورخ 2026-09-27 — سابقهٔ remediation و قبولی تاریخی 658/658، به‌همراه محدودیت‌های بیرونی/تصمیمی.
- `mvp/PHASE5_DELIVERY_REPORT.md`، `mvp/MVP_API_MAP.md`، `mvp/MVP_SCREEN_MATRIX.md` و `TEST_VERIFICATION_MANIFEST.md` — باید با SHA جاری دوباره تطبیق داده شوند.
- `scripts/test_http_proof_of_delivery.py`، `scripts/run_verification_suite.py`، تست‌های tenant-isolation/security/concurrency و workflowهای CI — مسیرهای اجرای verification.
- PR #30 و CI آن — شاخهٔ remediation مورخ 2026-10-11؛ وضعیت نهایی CI در آخرین دسترسی قابل تأیید نبود.
- **مقایسهٔ اینترنتی استانداردها/راهنماها (دسترسی 2026-10-12):**
  - OWASP API Security Top 10 (2023): https://owasp.org/API-Security/editions/2023/en/0x00-header/ — برای ماتریس امنیت endpointها، authorization، resource consumption و third-party API safety.
  - OWASP MASVS: https://mas.owasp.org/MASVS/ و OWASP MASTG test catalog: https://mas.owasp.org/MASTG/tests/ — برای storage، crypto، auth، network، platform, code, resilience و آزمون داده‌های حساس موبایل.
  - Android Core App Quality: https://developer.android.com/docs/quality-guidelines/core-app-quality — برای lifecycle/interruptions، permissions، پوشش device/form-factor و عملکرد/پایداری.
  - Expo Unit Testing: https://docs.expo.dev/develop/unit-testing/ — برای unit/component testing؛ خود مستندات Expo توصیه می‌کنند UI acceptance تنها به snapshot test متکی نباشد و E2E نیز در نظر گرفته شود.
  - Maestro React Native + Android: https://docs.maestro.dev/get-started/supported-platform/react-native و https://docs.maestro.dev/get-started/supported-platform/android — برای black-box E2E روی device/emulator و testIDهای پایدار.
  - Playwright Best Practices: https://playwright.dev/docs/best-practices و Assertions: https://playwright.dev/docs/test-assertions — برای user-visible behavior، test isolation و auto-retrying assertions.
  - W3C WCAG 2.2 Quick Reference: https://www.w3.org/WAI/WCAG22/quickref/ — برای معیارهای keyboard accessibility و الزامات دسترس‌پذیری.
  - Google Web Vitals: https://web.dev/articles/vitals — آستانه‌های «good» برای LCP ≤ 2.5s، INP ≤ 200ms و CLS ≤ 0.1 در صدک 75 و تفکیک mobile/desktop؛ این‌ها معیار وب هستند، نه معیار مستقیم native Android.
  - NIST Secure Software Development Framework (SSDF): https://csrc.nist.gov/pubs/sp/800/218/final — برای تکرارپذیری، secure SDLC و ادغام تست امنیت در روند توسعه.

**محدودیت:** این مقایسه فهرست تست‌های لازم را توسعه می‌دهد؛ به‌تنهایی ممیزی کامل استاندارد یا گواهی انطباق رسمی OWASP/Google/W3C نیست. TODOهای تازه همه باز هستند تا شواهد روی SHA/نسخهٔ واقعی ثبت شود.

### [2026-10-12 17:00 Asia/Tehran] Agent: ChatGPT — TODO-LIST-PROTOCOL
- State: DONE_VERIFIED
- Incoming handoff: Existing TODO_LIST.md and prior audit context; existing tasks and statuses retained.
- Repository / branch / worktree: Local generated artifact `/mnt/data/TODO_LIST.md`; GitHub branch sync not verified because GitHub connector calls failed in this session.
- Start SHA -> End SHA: NOT AVAILABLE LOCALLY -> NOT COMMITTED
- Files and symbols changed: `TODO_LIST.md`; added execution chain rules, owner/handoff rules, required per-agent progress template, status taxonomy, evidence/checkbox criteria, safety rules, and append-only journal instructions.
- Work completed in this session: Added governance for sequential dependency-aware execution and an auditable handoff between agents.
- Work inherited from previous agent and verified: Retained existing task inventory; no task was marked complete based on this edit.
- Commands/tests/environment: Validated the Markdown file is readable and has the intended protocol section; not a code test.
- Results: File edit saved locally. GitHub upload/push is NOT VERIFIED.
- Not done / known risks: Current PR #30 and live CI status still require a successful GitHub check; this entry does not certify code/test results.
- Blocker and responsible owner: GitHub connector access must recover before syncing this file to the repository; repo owner/agent with GitHub write access to perform sync.
- Next TODO-ID / next agent: `TODO-001` — determine PR #30 and current CI, then sync this protocol file through a normal reviewed commit/PR.
- Working tree: Local output only; repository workspace status is UNKNOWN.
- Handoff accepted by: PENDING

### [2026-10-12] Agent: ChatGPT — PREBUILD-TEST-GATES
- State: DONE_VERIFIED
- Incoming handoff: Existing `/mnt/data/TODO_LIST.md`, its 60-item task inventory, agent protocol, and historical POL-2.3 QA/staging artifacts; preserved existing task IDs and their prior status.
- Repository / branch / worktree: Local artifact `/mnt/data/TODO_LIST.md`; repository push/sync remains NOT VERIFIED.
- Start SHA -> End SHA: NOT AVAILABLE LOCALLY -> NOT COMMITTED
- Files and symbols changed: `TODO_LIST.md`; added pre-build vs QA-build vs release-build rules, tasks `TODO-061` through `TODO-084`, revised chain map, `TODO-009` QA-only build gate, and `TODO-056` release build criteria.
- Work completed in this session: Added staged test requirements for reproducible environment, code quality, PostgreSQL migrations/invariants, full suite, API contracts, auth, tenant/RBAC, state machines, concurrency/idempotency, backend E2E, outbox/workers, media security, web build/browser tests, Expo/mobile configuration/export, security/dependency scans, and final gate report.
- Work inherited from previous agent and verified: Existing 60 TODO entries and handoff journal retained; old 658/658 evidence remains explicitly historical and does not certify current SHA.
- Commands/tests/environment: Read and edited `/mnt/data/TODO_LIST.md`; checked task IDs and modified chain references. This validates the checklist artifact, not the application source or its runtime.
- Results: Local markdown updated. No application test was executed by this documentation change. GitHub upload/push is NOT VERIFIED.
- Not done / known risks: All new tasks `TODO-061`…`TODO-084` remain open until actual commands and evidence are run. Live provider tests still need credentials; device verification requires emulator or physical Android device.
- Blocker and responsible owner: Repo synchronization requires GitHub write access; Android device tests require working Android runtime. Owners must be assigned before executing each task.
- Next TODO-ID / next agent: `TODO-001` to determine current PR/SHA and CI; then follow the explicit dependency graph `TODO-061`…`TODO-084` before `TODO-009` QA-only APK build.
- Working tree: Local output file updated; repository workspace status UNKNOWN.
- Handoff accepted by: PENDING


### [2026-10-12 17:00 Asia/Tehran] Agent: ChatGPT — DEBUGGING-USER-JOURNEYS-FEATURE-QA
- State: DONE_VERIFIED
- Incoming handoff: `/mnt/data/TODO_LIST.md`, existing IDs TODO-001…TODO-084 and the prior request to expand pre-build qualification.
- Repository / branch / worktree: Local artifact `/mnt/data/TODO_LIST.md`; GitHub synchronization NOT VERIFIED.
- Start SHA -> End SHA: NOT AVAILABLE LOCALLY -> NOT COMMITTED
- Files and symbols changed: `TODO_LIST.md`; added feature/debugging/user-journey acceptance section `TODO-085`…`TODO-130`, testing rules for reproducibility/severity/mock-vs-live, and changed dependency wording so the stable ID `TODO-084` is the final pre-build gate.
- Work completed in this session: Added regression/debugging and logging coverage, deterministic fixtures and environment safety, Retailer journeys from onboarding/catalog/basket/allocation/checkout/orders/delivery/payment/RMA/support, Vendor onboarding/catalog/pricing/inventory/orders/fulfillment/finance, Ops/Admin/Field scope checks, form/RTL/UI state/navigation/motion/offline/race/security/notifications, browser E2E, cross-persona E2E, fault injection, retest, performance baseline, accessibility and feature acceptance matrix.
- Work inherited from previous agent and verified: Existing tasks and status values retained; no application test is marked complete by this document update.
- Commands/tests/environment: Read and edited local Markdown; verified insertion markers and TODO ID ranges with text checks. Application code and CI were not executed.
- Results: Local artifact updated; GitHub push/sync is NOT VERIFIED.
- Not done / known risks: TODO-085…TODO-130 remain OPEN pending execution and evidence. QA APK build must wait until pre-build dependencies and final gate TODO-084 are verified. Device-only tests remain post-QA-build.
- Blocker and responsible owner: GitHub synchronization requires a working authenticated connector or repository worktree; task owners must be assigned before running tests.
- Next TODO-ID / next agent: TODO-001 for current PR/SHA/CI status; then follow TODO-061…TODO-083 → TODO-085…TODO-130 → final gate TODO-084 → QA build TODO-009 → installed-device checks TODO-018…TODO-024.
- Working tree: Local output file updated; repository worktree status UNKNOWN.
- Handoff accepted by: PENDING


### [2026-10-12] Agent: ChatGPT — INDUSTRY-STANDARD-TEST-GAP-REVIEW
- State: DONE_CODE_UNVERIFIED
- Incoming handoff: `TODO_LIST.md` با TODO-001…TODO-152 و قواعد زنجیره‌ای قبلی.
- Repository / branch / worktree: فایل محلی `/mnt/data/TODO_LIST.md`; GitHub sync not verified.
- Start SHA -> End SHA: NOT AVAILABLE -> NOT COMMITTED
- Files and symbols changed: `TODO_LIST.md`; اضافه‌شدن مقایسهٔ پوشش موجود با OWASP API Top 10، OWASP MASVS/MASTG، Android Core App Quality، Expo/Maestro، Playwright، WCAG 2.2، Core Web Vitals و NIST SSDF؛ افزوده‌شدن TODO-131…TODO-152 با جداسازی PRE-BUILD و POST-QA-APK؛ به‌روزرسانی dependency گیت TODO-084 و release gate.
- Work completed in this session: تحقیق اینترنتی از منابع رسمی/اولیه، تعیین خلأهای نسبت به لیست موجود و افزودن تست‌های امنیت API، fuzz/property-based، contract drift، flakiness، بررسی بسته و privacy موبایل، lifecycle/device coverage، mobile E2E، accessibility، Web Vitals، performance/load، recovery و سازگاری app/API/DB.
- Work inherited from previous agent and verified: TODO-001…TODO-130 حفظ شد؛ قبولی تاریخی 658/658 هنوز به‌عنوان evidence مربوط به SHA قدیمی باقی است و به وضعیت PASS جاری تبدیل نشد.
- Commands/tests/environment: مرور منابع رسمی وب و ویرایش محلی Markdown؛ با بررسی جست‌وجوی شناسه‌ها و ساختار بخش‌ها. هیچ تستی روی source code یا runtime برنامه اجرا نشد.
- Results: فایل محلی به‌روزرسانی شد. GitHub upload/commit/PR به‌روزرسانی‌شده NOT VERIFIED.
- Not done / known risks: تمام TODO-131…TODO-152 باز هستند؛ کنترل واقعی باید روی SHA جاری انجام شود. Device/runtime tests نیازمند APK و emulator/دستگاه هستند؛ تست‌های provider/live و restore نیازمند محیط مناسب‌اند.
- Blocker and responsible owner: مالک فنی پروژه باید مالک اجرای TODOها را تعیین کند؛ sync به مخزن نیازمند GitHub write path سالم و ثبت commit/PR است.
- Next TODO-ID / next agent: `TODO-001` برای تثبیت PR/SHA/CI؛ سپس زنجیرهٔ فعلی را دنبال کنید. پیش از TODO-084 موارد PRE-BUILD استانداردی را اجرا کنید؛ پس از TODO-009، موارد POST-QA-APK را پیش از release ببندید.
- Working tree: تغییرات در فایل محلی؛ وضعیت worktree مخزن UNKNOWN.
- Handoff accepted by: PENDING


### [2026-10-12] Agent: ChatGPT — INDUSTRY-STANDARD-TEST-GAP-REVIEW-STRUCTURE-CHECK
- State: DONE_CODE_UNVERIFIED
- Incoming handoff: گزارش قبلی `INDUSTRY-STANDARD-TEST-GAP-REVIEW` و فایل `TODO_LIST.md` پس از مقایسهٔ استانداردها.
- Repository / branch / worktree: فایل محلی `/mnt/data/TODO_LIST.md`; GitHub sync not verified.
- Start SHA -> End SHA: NOT AVAILABLE -> NOT COMMITTED
- Files and symbols changed: `TODO_LIST.md`; تفکیک شفاف بخش PRE-BUILD از POST-QA-APK، افزودن `TODO-151` برای accessibility موبایل روی دستگاه و `TODO-152` برای بازرسی artifact واقعی، و اصلاح گیت‌های TODO-084/TODO-009/TODO-056 تا تست‌های نیازمند APK مانع نادرست pre-build نشوند.
- Work completed in this session: شماره‌گذاری TODOها از 001 تا 152 کنترل شد؛ declaration یکتای تمام 152 مورد تأیید شد؛ وابستگی تست‌های دستگاهی از pre-build gate جدا شد.
- Work inherited from previous agent and verified: منابع رسمی پژوهش و TODO-131…TODO-150 حفظ شدند؛ موارد 151 و 152 به‌عنوان وظایف باز اضافه شدند.
- Commands/tests/environment: بازخوانی/ویرایش Markdown و scriptهای محلی برای کنترل شناسه‌ها و ساختار. هیچ تستی روی کد، backend یا APK اجرا نشد.
- Results: فایل محلی با 152 شناسهٔ یکتا به‌روزرسانی شد؛ sync/commit به GitHub NOT VERIFIED.
- Not done / known risks: TODO-131…TODO-152 همچنان باز هستند تا اجرا و evidence روی SHA واقعی ثبت شود.
- Blocker and responsible owner: مالک فنی پروژه باید ایجنت‌ها/مسئولان را تعیین کند؛ ثبت فایل در repo نیازمند اتصال write معتبر GitHub و PR/commit است.
- Next TODO-ID / next agent: `TODO-001` برای تثبیت SHA/CI؛ پس از پیش‌نیازها موارد PRE-BUILD را اجرا کنید، `TODO-084` را ببندید، سپس `TODO-009` و آزمون‌های POST-QA-APK را اجرا کنید.
- Working tree: artifact محلی؛ وضعیت worktree مخزن UNKNOWN.
- Handoff accepted by: PENDING

### [2026-10-12] Agent: ChatGPT — EXECUTION-RESUME-ATTEMPT
- State: BLOCKED_INTERNAL
- Incoming handoff: آخرین دستور ادامهٔ اجرای TODOها؛ نقطهٔ شروع مقرر `TODO-001` برای تعیین وضعیت زندهٔ PR #30 و CI بود.
- Repository / branch / worktree: فایل محلی `/mnt/data/TODO_LIST.md`; checkout محلی `rrasi90/POL-2.3` در محیط جاری پیدا نشد. آخرین شاخهٔ مستندشده در فایل `fix/audit-remediation-20261011` است، اما وضعیت فعلی GitHub در این نشست قابل خواندن نیست.
- Start SHA -> End SHA: UNKNOWN -> UNKNOWN / NOT COMMITTED
- Files and symbols changed: `TODO_LIST.md`; وضعیت `TODO-001` از `OPEN` به `BLOCKED_INTERNAL` تغییر کرد و دلیل موقتِ عدم دسترسی ثبت شد؛ هیچ شناسه یا checkboxی حذف یا به حالت complete تبدیل نشد.
- Work completed in this session: ممیزی ساختاری فایل TODO اجرا شد؛ 152 شناسهٔ یکتا، هیچ شناسهٔ گمشده، 209 یال وابستگی صریح، 0 ارجاع وابستگی ناشناخته، 0 چرخهٔ وابستگی و 0 کار علامت‌خورده به‌عنوان کامل ثبت شد. وضعیت اولیهٔ workflow و PR نیز برای خواندن زنده بررسی شد، اما connector خطای داخلی برگرداند.
- Work inherited from previous agent and verified: ترتیب TODO-001 به‌عنوان دروازهٔ تعیین PR/SHA/CI و قاعدهٔ عدم علامت‌زدن بدون evidence حفظ شد؛ تمام کارهای اپلیکیشن همچنان باز هستند.
- Commands/tests/environment: اسکریپت محلی Python برای شمارش IDها و بررسی گراف وابستگی‌ها؛ نتیجه: `152 IDs, 0 missing, 209 dependency edges, 0 unknown dependencies, 0 cycles, 0 checked tasks`. این فقط اعتبارسنجی فایل TODO است؛ هیچ تست کد، DB، API، CI یا APK اجرا نشده است. فراخوانی‌های GitHub MCP (`fetch_file`, `fetch_pr`, `list_repositories`, و `fetch_workflow_run_jobs`) در این نشست با خطای داخلی برگشتند؛ دریافت مستقیم صفحات GitHub نیز با DisabledError شکست خورد.
- Results: فایل محلی به‌روزرسانی شد. وضعیت زندهٔ PR #30، checkها و SHA جاری NOT VERIFIED؛ sync/commit/push به GitHub NOT VERIFIED.
- Not done / known risks: اجرای `scripts/run_verification_suite.py`، تست OTP tenant isolation/cap، تست regression basket، Android delivery-state tests و هرگونه CI/device test همچنان اجرا نشده/تأییدنشده‌اند. ادعای تاریخی 658/658 همچنان مربوط به SHA قدیمی است و برای PR کنونی اثبات نیست.
- Blocker and responsible owner: دسترسی GitHub در محیط اجرا باید احیا شود یا ایجنتی با دسترسی معتبر و checkout فعلی مخزن تحویل بگیرد؛ پس از بازیابی، ابتدا PR #30/head SHA/all checks بررسی شوند.
- Next TODO-ID / next agent: `TODO-001` — با GitHub connector سالم یا checkout محلی، وضعیت PR #30 و head SHA را تثبیت کند؛ سپس `TODO-002` را فقط روی همان SHA اجرا کند.
- Working tree: checkout مخزن در این محیط موجود نیست؛ فقط فایل خروجی محلی `/mnt/data/TODO_LIST.md` تغییر کرده است.
- Handoff accepted by: PENDING



### [2026-10-12 17:20 Asia/Tehran] Agent: ChatGPT — EXECUTION-BLOCKER-RECOVERY
- State: BLOCKED_EXECUTION_ENVIRONMENT
- Incoming handoff: آخرین journal ورودی `EXECUTION-RESUME-ATTEMPT`; TODO-001 منتظر تثبیت PR #30/head SHA/checks بود.
- Repository / branch / worktree: checkout مخزن در محیط فعلی موجود نیست؛ مسیر artifact: `/mnt/data/TODO_LIST.md`; ابزار کمکی: `/mnt/data/POL_TODO_PREFLIGHT.ps1`.
- Start SHA -> End SHA: UNKNOWN -> NOT COMMITTED.
- Files and symbols changed: `TODO_LIST.md`؛ طبقه‌بندی TODO-001 از مانع عمومی `BLOCKED_INTERNAL` به `BLOCKED_EXECUTION_ENVIRONMENT` دقیق‌تر شد؛ تعریف وضعیت جدید افزوده شد. فایل کمکی `POL_TODO_PREFLIGHT.ps1` ساخته شد.
- Work completed in this session: دوباره تلاش شد GitHub connector از طریق `fetch_file`, `fetch_pr`, `search`, و `list_repositories` استفاده شود؛ همه با internal error برگشتند. فراخوانی مستقیم `git ls-remote` در محیط فعلی به علت `Could not resolve host: github.com` شکست خورد و checkout محلی پیدا نشد. برای ادامه روی ماشین/agent دارای checkout، preflight script ساخته شد تا branch/SHA/status، origin (با ماسک‌کردن credential در گزارش)، remote reachability، PR #30/checks (با `gh` یا API عمومی)، scripts وب/موبایل و در صورت انتخاب compileall/full suite را ثبت کند. اسکریپت هیچ checkout/reset/stash/commit/push انجام نمی‌دهد.
- Work inherited from previous agent and verified: 152 TODO IDهای موجود و قواعد عدم علامت‌زدن بدون evidence حفظ شدند؛ وضعیت قبولی تاریخی 658/658 همچنان فقط مدرک SHA قدیمی است.
- Commands/tests/environment: `find /mnt/data /workspace /home/oai/share /tmp -maxdepth 4 -type d -name .git` هیچ checkout قابل استفاده‌ای نشان نداد؛ `git ls-remote https://github.com/rrasi90/POL-2.3.git HEAD` خروجی `Could not resolve host: github.com` داد. فقط تست اتصال/دسترسی اجرا شد؛ هیچ تست کد/DB/API/CI/device اجرا نشده است. PowerShell script در کانتینر Linux اجرا/parse-test نشده و باید در Windows PowerShell 5.1+ به‌صورت محلی بررسی شود.
- Results: ابزار بازیابی محلی ساخته شد و به‌صورت artifact قابل دریافت است. به‌روزرسانی GitHub هنوز ناممکن/تأییدنشده است؛ هیچ سورس اپلیکیشن در این نشست اصلاح یا merge نشد.
- Not done / known risks: وضعیت واقعی PR #30، نتیجهٔ CI، و اینکه PR هنوز روی همان SHA است یا نه UNKNOWN است. تست‌های backend، mobile, database و build اجرا نشده‌اند.
- Blocker and responsible owner: یک ایجنت محلی دارای clone فعلی و دسترسی GitHub باید در ریشهٔ repo اجرا کند: `& .\POL_TODO_PREFLIGHT.ps1 -FetchRemote -RunPythonCompile`; بعد SHA خروجی را با PR head تطبیق دهد؛ فقط پس از این تطبیق suite را اجرا کند.
- Next TODO-ID / next agent: `TODO-001` — اجرای preflight بالا روی ماشین دارای clone؛ بررسی وضعیت PR #30/head SHA/all checks، سپس `TODO-002` روی SHA تأییدشده. اگر PR head با checkout فرق دارد، بدون reset/checkout مخرب گزارش و توقف کند.
- Working tree: تغییر فقط روی فایل‌های artifact خروجی `/mnt/data`; repository working tree status UNKNOWN.
- Handoff accepted by: PENDING

### [2026-10-12 UTC] Agent: ChatGPT — GITHUB-SYNC-AND-CI-VERIFICATION-RECOVERY
- State: DONE_VERIFIED (GitHub synchronization and evidence review only; not a claim that all app tests are complete)
- Incoming handoff: `EXECUTION-BLOCKER-RECOVERY`; local artifacts `/mnt/data/TODO_LIST.md` and `/mnt/data/POL_TODO_PREFLIGHT.ps1`; PR #31 was a Draft containing placeholders because the previous write path had only partially succeeded.
- Repository / branch / worktree: `rrasi90/POL-2.3`, branch `docs/todo-list-and-preflight-20261012`, PR #31.
- Start SHA -> End SHA: branch head before restoration `933e2ecbdaa8abad18fe6812f0e5b68dadf7715f` -> last file update commit `0c31d71fb6a7ece62c340f405dd420b4e81363c5`; verify latest PR head separately from branch head before merge.
- Files changed: `TODO_LIST.md` restored to the complete 152-item checklist; `POL_TODO_PREFLIGHT.ps1` restored to the full 160-line helper.
- Work completed in this session: Reconnected to GitHub; confirmed repo write permission; re-read local artifacts via Files; updated each existing GitHub file on branch `docs/todo-list-and-preflight-20261012`; independently fetched both files back from GitHub and compared exact text. `TODO_LIST.md`: 97,259 characters / 587 lines, has TODO-152 and Agent Handoff Journal, no placeholder notice. `POL_TODO_PREFLIGHT.ps1`: 8,320 characters / 160 lines, contains the actual preflight code, not placeholder content.
- CI/evidence verified: PR #30 remains open and unmerged; head SHA `45ff1e3d6498568596a42b01d9b69d827a49777d`, base SHA `26e9b8b7766d871cefdd8e7257439646f5b9f399`. Workflow runs: static `38130308723` success; mobile `38130308664` success including retailer/vendor pre-APK QA and both QA APK builds; independent verification `38130308606` success. Artifact JSON from the independent verification run reports 663 passed, 0 failed, 0 skipped, exit code 0, 199.01 seconds, PostgreSQL 18.6, tested CI merge-candidate SHA `83485b25a7042999150daf487dd99c140642a827`. Both OTP regression tests appear in artifact with outcome `passed`.
- Commands/tests/environment: Read complete local artifacts; verified exact local-to-GitHub content equality after write. Parsed `/mnt/data/pol-test-results.json`: 663 tests, all passed. Verified specific OTP test nodeids. Queried GitHub PR metadata and job summaries. PowerShell script parsing/execution on Windows was not available here; do not claim it has been runtime-tested.
- Results: Both full files are on GitHub branch `docs/todo-list-and-preflight-20261012`; links: [TODO_LIST.md](https://github.com/rrasi90/POL-2.3/blob/docs/todo-list-and-preflight-20261012/TODO_LIST.md), [POL_TODO_PREFLIGHT.ps1](https://github.com/rrasi90/POL-2.3/blob/docs/todo-list-and-preflight-20261012/POL_TODO_PREFLIGHT.ps1). PR #31 remains Draft and unmerged; this is intentional until PowerShell validation on Windows and final PR review.
- Not done / known risks: TODO-003 remains open because CI artifact fetched contains `pol-test-results.json`, but `failure_inventory.txt` and final certification report were not independently verified in that artifact. TODO-006 and TODO-007 still require specific web basket-sync regression and exact mobile delivery-state assertions. QA APK artifacts were built in CI, but device installation, screenshot capture and physical-device verification remain unverified. External SMS/S3 credentials and policy/financial decisions remain separate blockers.
- Next TODO-ID / next agent: Continue at `TODO-003`; validate whether CI generated and persisted `artifacts/failure_inventory.txt` and final certification output for the same tested SHA. Then execute TODO-006 and TODO-007 specific regression coverage; validate `POL_TODO_PREFLIGHT.ps1` under Windows PowerShell/PowerShell 7; review PR #31 before marking ready.
- Working tree: local files and branch files are synchronized by exact text comparison; no repository code was changed by this documentation recovery.
- Handoff accepted by: PENDING

### [2026-10-12 UTC] Agent: ChatGPT — POST-MERGE-VERIFICATION-AND-BRANCH-CLEANUP
- State: DONE_VERIFIED (merge/CI/workflow synchronization; not a claim that all application QA is complete)
- Incoming handoff: `GITHUB-SYNC-AND-CI-VERIFICATION-RECOVERY`; PR #30 was open with green CI, PR #31 contained complete files but its branch still had the obsolete duplicate-`env` static workflow inherited from old `main`.
- Repository / branch / worktree: `rrasi90/POL-2.3`; base `main`; docs branch `docs/todo-list-and-preflight-20261012`.
- Start SHA -> End SHA: PR #30 head `45ff1e3d6498568596a42b01d9b69d827a49777d` -> merged `main` commit `2cd6588206c8b3bddc5ae13aad461bc61f90338f`; docs branch commit after workflow alignment `1f1fc25c1dce58a5aeabafc32796e0f6aeda98f8` (later TODO document update may move this branch again).
- Files/workflows changed: PR #30 code fixes merged to `main`; `.github/workflows/pol-remediation-static.yml` on docs branch was aligned to canonical current-main blob `48adc16b0ceb58d365faa0bef8eedaadb5c46ca7`, removing duplicate `env` from the branch's own push-workflow definition.
- Work completed: Confirmed PR #30 had no review submissions or unresolved review threads; all three PR workflows completed success. Merged PR #30 using squash and expected-head SHA guard. Compared Git tree SHA of tested merge candidate `83485b25a7042999150daf487dd99c140642a827` with post-merge `main`; both equal `3b14029235ba0c5d61dfe19dee0708a87b75bfe5`, establishing the tested code tree matches main. Verified the independent test artifact: 663/663 pass, 0 fail, 0 skip; both OTP regression tests were passed. Confirmed the two QA APK artifacts existed in the CI run. Restored `.github/workflows/pol-remediation-static.yml` on docs branch to the fixed canonical file, so it no longer carries the old duplicate `env` version.
- Tests/evidence: Static run `38130308723` success; Mobile run `38130308664` success (Expo typecheck, functional and regression QA, both variant pre-APK gates, retailer APK and vendor APK); Independent Verification run `38130308606` success; artifact `11698943848`, PostgreSQL 18.6, 663 passed, 199.01 seconds, exit 0. Source-of-truth tree comparison performed through GitHub API.
- Results: PR #30 merged. Complete `TODO_LIST.md` and `POL_TODO_PREFLIGHT.ps1` were previously fetched back from GitHub and matched exact local contents. PR #31 remains Draft/unmerged; the branch now aligns the static workflow with current main.
- Not done / known risks: PowerShell script has not been executed/parsed by Windows PowerShell or PowerShell 7 in this environment. TODO-003 remains open because `failure_inventory.txt` and final certification report were not independently confirmed in the downloadable CI artifact. TODO-006 basket sync regression and TODO-007 exact mobile delivery-state assertions remain open; device installation/screenshots and external/live integrations also remain open.
- Next TODO-ID / next agent: TODO-003 — retrieve/verify failure inventory and certification report for the same code tree; then TODO-006 and TODO-007. Run `POL_TODO_PREFLIGHT.ps1` on Windows/PowerShell 7 from a current main checkout, then review/resolve PR #31. Do not mark APK device checks complete just because CI produced APK artifacts.
- Working tree: remote GitHub docs branch; no app code changes after PR #30 merge. Local file updated; remote TODO file must be synchronized after this journal entry.
- Handoff accepted by: PENDING

## وضعیت آخرین بررسی و کارهای باقی‌مانده

- **GitHub:** اتصال فعال است؛ متن کامل `TODO_LIST.md` و `POL_TODO_PREFLIGHT.ps1` روی شاخهٔ `docs/todo-list-and-preflight-20261012` قرار دارد و از راه GitHub دوباره خوانده شده است.
- **PR #30:** ادغام‌شده در `main`؛ merge commit `2cd6588206c8b3bddc5ae13aad461bc61f90338f`. تمام سه workflow موفق بودند و tree آزمایش‌شده دقیقاً با tree فعلی main برابر است.
- **PR #31:** Draft و ادغام‌نشده؛ فایل‌ها کامل‌اند و workflow branch با `main` همگام شده است. اجرای PowerShell روی Windows/PowerShell 7 و review نهایی همچنان باقی است.
- **شواهد تست:** 663/663 مربوط به CI روی merge-candidate SHA `83485b25a7042999150daf487dd99c140642a827` است؛ tree آن با `main` بعد از merge برابر است. این نتیجه تست دستگاه واقعی نیست.
- **کارهای باقی‌ماندهٔ مشخص:** TODO-003 (تأیید `failure_inventory.txt` و final certification report)، TODO-006 (تست اختصاصی sync سبد خریدار)، TODO-007 (assertionهای state تحویل موبایل)، PowerShell runtime validation و نصب/QA روی دستگاه واقعی. بقیهٔ TODOها فقط با evidence جداگانه بسته شوند.
- **ادامهٔ زنجیره:** TODO-003 → TODO-006 → TODO-007 سپس بر اساس dependency map؛ موارد PRE-BUILD باز باید پیش از گیت TODO-084 تعیین تکلیف شوند، تست‌های دستگاهی بعد از QA APK و قبل از release انجام می‌شوند.

### [2026-10-12 UTC] Agent: ChatGPT — REGRESSION-GUARD-AND-EVIDENCE-AUDIT
- State: PARTIAL_VERIFIED / FIX_APPLIED_PENDING_RETEST
- Incoming handoff: `POST-MERGE-VERIFICATION-AND-BRANCH-CLEANUP`; PR #30 is merged, full local TODO and PowerShell helper are on GitHub, PR #31 was superseded/closed and PR #32 became the review candidate.
- Repository / branch / worktree: `rrasi90/POL-2.3`, branch `docs/todo-list-and-preflight-final-20261012`; most recent commit at time of entry: `1a6a943eb7557e0a401dd1f55e100bbdde82ef4a`.
- Work completed and verified:
  - Downloaded and inspected CI artifact `pol-verification-evidence` ID `11718298226` from run [38182246509](https://github.com/rrasi90/POL-2.3/actions/runs/38182246509). Artifact contains `pol-test-results.json`, `failure_inventory.txt`, and `final_certification_65b826d5e5a0d1df2d861e4638301aca65e5cdf7.json`. That tested commit reports 663/663 PASS, 0 failures, 0 skips, exit 0, PostgreSQL 18.6; report verdict `AUTOMATED_TESTS_PASSED`, `release_or_pilot_certification=NOT_CLAIMED`. This proves the evidence-generation workflow works for that run/SHA.
  - Windows helper check [38182246464](https://github.com/rrasi90/POL-2.3/actions/runs/38182246464) passed the Windows PowerShell 5.1 parser, safe preflight and Python compileall. Its log confirms `adb` and `emulator` were not available; device QA is still open.
  - Added source-contract guards for the exact web basket-sync failure path and the mobile delivery transition path; an independent JS inspection of the current source verified all 14 corresponding invariants are present. These source checks are not browser/device E2E tests.
- New failure found:
  - Run [38182442225](https://github.com/rrasi90/POL-2.3/actions/runs/38182442225) failed 1 of 663 tests: `scripts/test_pytest_collection_guard.py::test_every_test_file_collects_at_least_one_test`. Cause: the new stand-alone source-guard runner was named `scripts/test_ui_audit_regressions.py`, so the repository's pytest collection guard treated it as a test module with no test functions.
  - Corrective change applied: renamed the runner to `scripts/ui_audit_regression_guards.py` and updated the static and Windows workflows to execute the new path explicitly. The old `test_*.py` file was deleted on this branch. This avoids changing pytest's test-file inventory while preserving the manual guard.
- What is still NOT verified:
  - The renamed runner and the latest workflow versions have not yet completed a new GitHub Actions run. The failed run above is for the pre-rename SHA and is not evidence about the corrected version.
  - TODO-003 stays OPEN until a post-fix exact-SHA run generates and validates all three evidence files.
  - TODO-006/TODO-007 stay OPEN until the regression guard runs green and real behavior-level browser/mobile QA is added; source assertions alone do not prove user-visible behavior.
  - Physical-device APK install/screenshots, live SMS, live object storage, payment reconciliation, unresolved policy decisions and legal/operational pilot gates remain open.
- Commands/tests/environment: Inspected the downloaded ZIP and parsed all three artifacts; re-read current web/mobile source through GitHub; evaluated 14 source conditions against current source; reviewed CI failure inventory. No local Android device/emulator exists in the runner.
- Next TODO-ID / next agent: trigger a fresh PR CI run from the latest renamed-runner commit; require all three workflows green; inspect new artifact and test inventory; only then update TODO-003 and review/merge the documentation/test PR.
- Handoff accepted by: PENDING

## Latest execution snapshot — 2026-10-12
- PR #30: merged to `main` at `2cd6588206c8b3bddc5ae13aad461bc61f90338f`; CI-tested code tree equals post-merge main tree.
- TODO-003: still OPEN pending successful post-fix exact-SHA run.
- Regression runner filename: `scripts/ui_audit_regression_guards.py`; it is called by the static and Windows workflows and intentionally does not match pytest's `test_*.py` discovery convention.
- PR #31: closed as superseded. PR #32: draft review candidate; do not merge until latest CI validates the rename and new runner.
- Next action: finish fresh CI on the corrected branch/PR; don't mark UI behavior or device QA complete on source checks alone.


### [2026-10-12 UTC] Agent: ChatGPT — CURRENT-SHA-EVIDENCE-AND-REGRESSION-CLOSEOUT
- State: DONE_VERIFIED for automated evidence bundle and source-regression guards; browser/device QA explicitly remains OPEN.
- Repository / branch / PR: `rrasi90/POL-2.3`, branch `docs/pol-prebuild-checklist-mainbase-20261012`, PR #34; base main `2cd6588206c8b3bddc5ae13aad461bc61f90338f`.
- Tested CI head: PR branch SHA `6015442f630bfc60275e0521ba0c339ed82a8b56`; Independent Verification tested merge-candidate commit `adde20b1d47595efa71547ae9397ce10de464aab`. **Their tree SHA is identical:** `7017974ddb715076c8054f554f481c093a9cc21a`.
- Independent Verification: run `38182998940` passed. Full suite `663/663 PASS`, 0 failed, 0 skipped, exit 0, 199.02 seconds; PostgreSQL 18.6. Artifact `11718750722`, digest `sha256:1269a62a7c66e5deca74a7fca07e6c7380ca5209a2a1505fc11d53e5f12b82d2`; ZIP independently inspected; three files present: results JSON, failure inventory and final verdict. Failure inventory has no active failures; verdict `AUTOMATED_TESTS_PASSED`; release/pilot certification not claimed.
- Static Gate: run `38182998731` passed, including `scripts/ui_audit_regression_guards.py` **11/11 PASS**.
- Windows preflight: run `38182998742` passed PowerShell 5.1 parsing, safe preflight, Python compileall and 11 source guards.
- Fix discovered from prior run: pytest collection had failed because guard script filename began `test_`; renamed to `scripts/ui_audit_regression_guards.py`, updated both workflows and removed the old file. The failing run was pre-fix; current runs above pass.
- TODO status: TODO-003 now DONE_VERIFIED; TODO-006 and TODO-007 remain OPEN because source guards do not constitute browser E2E, live API behavior or installed-device QA.
- Remaining risks: physical-device APK installation/screenshots/accessibility, actual browser E2E for Retailer checkout, live SMS/storage, financial reconciliation and operations/legal pilot requirements remain open in their dedicated TODOs. Do not mark the app release-ready.
- Important: this edit updates the checklist after successful CI and therefore changes the docs branch SHA. The pull request CI will rerun on the resulting commit; do not merge until those post-edit checks also pass.
- Next owner/action: verify all checks on the newest PR #34 head; if green, mark ready, review the exact diff, merge PR #34 and confirm the merged main tree equals the tested tree. Keep device/browser QA status open.
- Handoff accepted by: pending final merge review.


### [2026-10-12 UTC] Agent: ChatGPT — WEB-BASKET-SYNC-REUSE-AND-RETRY-FIX
- State: DONE_CODE_UNVERIFIED — implementation committed to a feature branch; feature-branch CI and browser behavior still require verification.
- Incoming handoff: `CURRENT-SHA-EVIDENCE-AND-REGRESSION-CLOSEOUT` and merged PR #34. The evidence bundle for PR #34 verified 663/663 automated tests, Windows PowerShell 5.1 parsing/preflight, and static gates; none of those establishes browser/device QA.
- Repository / branch / worktree: `rrasi90/POL-2.3`, feature branch `fix/web-basket-sync-reuse-20261012`, based on post-merge `main` commit `dba2bc30ba3e49c3c91c24f347089e77a9542482`.
- Start SHA -> End SHA: `dba2bc30ba3e49c3c91c24f347089e77a9542482` -> source commits `5a179ea43808918c2c072bcae94b286253f1243f` (web basket fix) and `e565aa04f2fab92ad0ddd85243011841e2b5f41f` (regression guard update); final branch SHA must be reread after the TODO journal commit.
- Files and symbols changed: `mvp/apps/web/src/app/(dashboard)/retailer/basket/page.tsx` (`pushToServer`, ErrorState retry handler); `scripts/ui_audit_regression_guards.py` (basket store invalidation, repeated sync and retry assertions); this TODO journal.
- Work completed in this session: source review proved every call to `POST /api/v1/baskets` creates a new OPEN server basket, while web `pushToServer` had unconditionally created one on every click. Added an early return when `serverBasketId` is already set. The Zustand basket store clears `serverBasketId` whenever a local line is added, edited or removed, so changed contents still force a fresh sync. Changed the sync error retry to call `reviewAndCheckout()`, so a successful retry proceeds to checkout. Added three source-contract guards for reuse, invalidation-on-mutation and retry navigation; guard suite now contains 14 assertions.
- Work inherited from previous agent and verified: PR #34 merged as `dba2bc30ba3e49c3c91c24f347089e77a9542482` with tree `dcce8552735b3add3d1da9f59c64326dcb1c9589`; its static, Windows preflight and independent verification workflows passed before merge. The full independent run generated all three evidence files and reported 663 passed, 0 failed, 0 skipped, with release/pilot certification explicitly not claimed.
- Commands/tests/environment: source reviewed via GitHub; exact-string guards confirmed insertion points and remote read-back confirmed updated files on the feature branch. The 14-assertion guard suite has not yet been executed on the feature branch; CI is required for the authoritative result. No local browser runner/device was available in this connector-only workspace.
- Results: code changes are pushed to `fix/web-basket-sync-reuse-20261012`; feature PR and CI pending at time of this entry. TODO-006 remains OPEN because source guards are not browser E2E; TODO-007 remains OPEN for real API/runtime and installed-device QA.
- Not done / known risks: a failed item write after basket creation can still leave a partial OPEN basket because the current API has no transactional bulk-sync/idempotent create contract; do not claim that partial-failure orphan cleanup is solved. Browser-level success/failure/retry testing, Android installation/screenshots/accessibility, live SMS/storage, payment reconciliation and legal/operational pilot checks remain open.
- Blocker and responsible owner: Web QA / next agent must execute browser tests against the real web app and test backend, covering initial successful sync, repeated click/retry (exactly one new basket), empty basket, failed item request (checkout blocked), and editing lines after sync (new sync required). Add a supported browser automation fixture/dependency or use the project’s established CI environment; do not mark source assertions as behavioral PASS.
- Next TODO-ID / next agent: TODO-006 — open a PR from this feature branch, inspect latest PR SHA and all required CI checks, then merge only with expected-head SHA protection if green. After merge, build browser E2E coverage and test TODO-006 on runtime. TODO-007 then needs installed-device or emulator QA; its source guards alone are insufficient.
- Working tree: no local checkout used; remote feature branch contains committed updates. Main was not modified by these code changes.
- Handoff accepted by: PENDING


### [2026-10-12 UTC] Agent: ChatGPT — STALE-BASKET-ID-VALIDATION-REFINEMENT
- State: CODE_UPDATED — the refinement is committed on the existing PR #35 feature branch; the previous CI runs belong to the prior branch head and must not be used to certify this newer version.
- Reason for refinement: a persisted `serverBasketId` can outlive an OPEN basket on the server. Blindly reusing the ID would block checkout after server-side expiry. An idempotent UI retry must also not hide authentication, route or network errors by treating every failure as “basket missing.”
- Implementation: `pushToServer` now queries `GET /api/v1/baskets/current`, and reuses the returned basket only if it is OPEN and its item count, product IDs, requested quantities and pack quantities match the current local cart. If the API returns the specific 404/NOT_FOUND message `No OPEN basket exists for the active retailer organization.`, the persisted basket ID is cleared and sync may create a fresh basket. Other errors are surfaced without silently creating a replacement basket. Error-state Retry still uses `reviewAndCheckout()`.
- Regression evidence: expanded `scripts/ui_audit_regression_guards.py` from 14 to 15 source-contract assertions, including active-basket content match and controlled stale-ID invalidation. The prior 14/14 run passed only for the previous head `24dc802c2b61e701f949e9fdf76f4c5b8013d741`; 15/15 has not yet been established. Require CI on the latest branch SHA.
- Known risk not closed: if a POST creates a basket and only some item writes succeed, that partial OPEN basket may remain; the current API does not provide a transactional bulk-sync or delete contract. A separate reconciliation/resume design and real browser test are still needed.
- TODO status: TODO-006 remains OPEN pending runtime browser E2E for initial sync, repeat-click idempotence, 404 recovery, failed item-write/checkout blocking and local cart edits. TODO-007 remains OPEN pending runtime/API and emulator or installed-device QA. Source guards are not behavior-level certification.
- Next action: verify the current PR #35 head SHA and rerun all required workflows after this commit; merge only with expected-head SHA protection once green. Do not cite the earlier successful workflows as certification for the new SHA.
- Handoff accepted by: PENDING


### [2026-10-12 UTC] Agent: ChatGPT — CURRENT-BASKET-RECONCILIATION-EXTENSION
- State: CODE_UPDATED — the sync path has been broadened; previous runs on SHA `388fff229d9731a85d13b52657e20a780978d6c0` do not certify this latest source revision.
- Finalized reconciliation behavior: before creating a new server basket, `pushToServer` always queries `GET /api/v1/baskets/current`. If the active OPEN basket has the exact same product IDs, item count, requested quantities and pack quantities as the local cart, the UI records/reuses that basket and continues. This also recovers if all item writes reached the server but the client lost the response before persisting `serverBasketId`. If no OPEN basket exists (recognized `NOT_FOUND` / `No OPEN basket exists` response), the saved ID is cleared and a new sync may start. Other API failures remain visible and do not trigger a duplicate create attempt.
- Code commit for this extension: `b8650ec613867ee39088a721841e5781da1bdab3`. Current guard suite has 15 checks; the last observed 15/15 run was on source commit `c76a936d18fa1aad40ba881edec52535a78c5e17` before this refinement and must not be used as final evidence.
- Remaining risk: a partial basket whose items differ from the local cart is not resumed transactionally; a new basket may be created while the partial one remains OPEN. Runtime browser testing is still required for repeat clicks, lost responses, stale ID recovery, 404 behavior, API outage behavior and checkout gating. TODO-006 remains OPEN; TODO-007 remains OPEN pending API/runtime and emulator or installed-device QA.
- Next action: re-read the latest branch SHA after this journal commit, verify all PR #35 workflows on that exact SHA, inspect the final diff, and merge with expected-head SHA protection only after all checks pass.
- Handoff accepted by: PENDING


### [2026-10-12 UTC] Agent: ChatGPT — PR35-MERGE-AND-EVIDENCE-READBACK
- State: DONE_VERIFIED for PR #35 merge and pre-merge automated CI evidence; documentation update committed; post-merge SHA-specific CI and TODO-006 browser E2E / TODO-007 device QA remain OPEN.
- Incoming handoff: PR #35 current-head audit, including exact-head CI run `38186170942` with evidence artifact `11720360108`; source and TODO file were re-read from the feature branch before merging.
- Repository / branch / worktree: `rrasi90/POL-2.3`, PR #35 head `b04aabd32ecd3121002ca9bac0257d14ae49867f` into `main` based on `dba2bc30ba3e49c3c91c24f347089e77a9542482`.
- Start SHA -> End SHA: PR head `b04aabd32ecd3121002ca9bac0257d14ae49867f` -> merge commit `9fd6e7dcd90f044ceb3b94099db5bbb3f5cb99ff`; merge used expected-head SHA protection and GitHub returned merged=true.
- Files and symbols changed: `mvp/apps/web/src/app/(dashboard)/retailer/basket/page.tsx` (query current OPEN basket before creating, reuse only exact matching contents, handle only recognized missing-basket 404 as recoverable, Retry uses `reviewAndCheckout()`); `scripts/ui_audit_regression_guards.py` (source guards); `TODO_LIST.md` (this handoff entry plus TODO-006 evidence update).
- Work completed in this session: re-read the PR diff and all 4 jobs, inspected the independent verification ZIP, verified `pol-test-results.json`, `failure_inventory.txt` and final certification JSON, and merged PR #35 after all four workflows succeeded. The artifact reports 663 passed, 0 failed, 0 skipped, exit 0, PostgreSQL 18.6, verdict `AUTOMATED_TESTS_PASSED` and `release_or_pilot_certification=NOT_CLAIMED`. Both QA APK artifacts exist: retailer ID `11719722722`, vendor ID `11719976988`; artifact existence/build success is not a claim that either was installed or tested on a device.
- Next TODO-ID / next agent: TODO-006 — check whether post-merge CI has run on `9fd6e7dcd90f044ceb3b94099db5bbb3f5cb99ff`; then implement/run browser E2E for initial sync, repeated click, stale/missing basket, API outage, partial item-write failure, cart edit invalidation and checkout gating. Next TODO-007: device/emulator delivery-flow verification.
- Working tree: no local checkout used; PR #35 is merged. The handoff/docs update is being normalized in this commit; current TODO blob before update: `69562e9a674e51e4c71416ea5f927371367b5911`.
- Handoff accepted by: PENDING


### [2026-10-12 UTC] Agent: opencode - TODO-006-BROWSER-E2E-AND-WEB-FIXES
- State: DONE_VERIFIED for TODO-006 browser E2E and three web fixes; verified both locally and by required CI on the final head.
- Repository / branch / worktree: `rrasi90/POL-2.3`, branch `agent/pol-2.4-e2e-20261013` off `main` at `419d578bb01dc623407480be44d5828ebbe17ca3`, worktree `C:\Users\rrasi_oorj8fq\AppData\Local\Temp\opencode\pol-agent\pol-2.4`.
- Start SHA -> End SHA: `419d578bb01dc623407480be44d5828ebbe17ca3` -> `ac28036025b79677422589b7f4b1427c56d2f057` (3 commits: `13982c4` fixes, `7d7d653` E2E suite, `ac28036` static-guard order fix). PR #36 opened against `main`.
- Files and symbols changed: `mvp/apps/web/src/lib/auth/phone.ts` (new `toE164`); `mvp/apps/web/src/app/auth/login/page.tsx` (E.164 normalization, session-expired notice on mount); `mvp/apps/web/src/lib/auth/store.ts` (`sessionExpired` + mark/consume); `mvp/apps/web/src/lib/auth/api.ts` (onUnauthorized marks expiry); `mvp/apps/web/src/app/(dashboard)/retailer/basket/page.tsx` (`syncInFlight` ref guard in `pushToServer`); `scripts/e2e_seed.py`, `scripts/e2e_serve.py`, `scripts/e2e_db.py` (new); `mvp/apps/web/playwright.config.ts`, `mvp/apps/web/tests/{helpers,login.spec,basket-sync}.spec.ts` (new, 16 specs); `.github/workflows/pol-browser-e2e.yml` (new); `mvp/apps/web/package.json`, `mvp/package-lock.json` (Playwright deps), `.gitignore` (E2E artifacts).
- Bugs found by the real browser run and fixed: (1) login sent digits-only `9891...` while `scripts/api` requires E.164, so every login got 422 - now normalized in `lib/auth/phone.ts`; (2) repeated review clicks raced past React state and created two OPEN baskets - now guarded by an in-flight ref (Static Guard assertion 14 kept intact by keeping `setSyncing(false)` first in `finally`); (3) a 401 during sync dropped the user on the login screen with no message - the login page now shows a session-expired notice.
- Evidence: local `npm ci` clean; fresh schema via `python scripts/e2e_serve.py --reset --prepare` = 76 migrations / 107 tables; `npx playwright test` green in 4 consecutive runs (16/16; 19.2s warm, 29-31s cold start with Playwright booting API + Next); `npm run typecheck` OK; `python scripts/ui_audit_regression_guards.py` 15/15. CI on head `ac28036025b79677422589b7f4b1427c56d2f057`: POL Remediation Static Gate, POL Browser E2E (TODO-006), POL Independent Verification & Certification CI, POL MVP Mobile Verification - all `success` (runs 38324242236 / 38324242184 / 38324242187 / 38324242215).
- Not done / known risks: a failed item write after `POST /baskets` can still leave a partial OPEN basket (API has no transactional bulk-sync contract - pre-existing, unchanged); OTP rate limit is 3 per phone+IP per 5 minutes, so parallel workers are isolated by phone pool (login tests use `parallelIndex`, basket tests `parallelIndex + 12`); `accessToken` lives only in memory, so specs navigate client-side after login instead of reloading; release APK remains BLOCKED_EXTERNAL (signing key/production endpoint); TODO-011 notification retention remains BLOCKED on secrets; TODO-007 device QA remains OPEN.
- Next TODO-ID / next agent: merge PR #36 if `main` has not moved and no conflicts; then decide PR #29 (Draft, head `fix/mobile-motion-audit-20261011`) only if its CI is green and conflict-free. Remaining open work: TODO-007 device/emulator delivery QA, TODO-011 secrets, release APK signing.
- Handoff accepted by: PENDING


### [2026-10-13 UTC] Agent: opencode - TODO-006-MERGE-COMPLETION
- State: DONE_VERIFIED — PR #36 is merged and `main` is green at the merge commit.
- Start SHA -> End SHA: PR #36 head `9be4c10e63887587986747d2b029bb3906931db1` -> merge commit `ecf3d05177630498c3ec06f13b70c6db99db5735` (merge commit, expected-head protection not applicable: no branch protection on this free private repo).
- Post-merge CI on `main` at `ecf3d05177630498c3ec06f13b70c6db99db5735`: POL Remediation Static Gate (38326498911), POL MVP Mobile Verification (38326498981), POL Independent Verification & Certification CI (38326499062), POL Browser E2E (TODO-006) (38326499012) — all `success`. The only red run is the scheduled `POL Notification Retention` (38230815473, 2026-10-12), which is TODO-011 blocked on action secrets and unrelated to this merge.
- PR #29 (Draft, head `fix/mobile-motion-audit-20261011`) was NOT merged: GitHub reports `mergeable=CONFLICTING` / `mergeStateStatus=DIRTY` against the updated `main`, and it is still a Draft. The mission allows merging it only with green CI and zero conflicts, so it stays open.
- Next TODO-ID / next agent: TODO-007 device/emulator delivery QA; TODO-011 secrets for notification retention; release APK remains BLOCKED_EXTERNAL (signing key / production endpoint). Browser E2E for the basket flow is landed; extend it rather than re-deriving it.
- Handoff accepted by: PENDING

### [2026-10-13 UTC] Agent: opencode - TODO-007-RUNTIME-DELIVERY-E2E
- State: DONE_VERIFIED — browser E2E for the full delivery flow is green and the four UI defects found during scoping are fixed.
- Start SHA -> End SHA: `463d780fc74ade31f01cfc13a4a22124c3f891b9` -> merge commit `4e1daa39a8c9d27f2fff93fa43116db24a71ccab` (PR #38, branch `agent/pol-2.4-todo007-delivery-e2e`, head `1ad3b41`, merged only after all four workflows passed on the PR head).
- Post-merge CI on `main` at `4e1daa39a8c9d27f2fff93fa43116db24a71ccab`: POL Remediation Static Gate (38392667118), POL MVP Mobile Verification (38392667176), POL Browser E2E (TODO-006) (38392667249), POL Independent Verification & Certification CI (38392667116) - all `success`. The only red run remains the scheduled `POL Notification Retention` (38377807571), which is TODO-011 blocked on action secrets and unrelated to this merge.
- PR #29 (Draft, head `fix/mobile-motion-audit-20261011`) was NOT merged: it is still a Draft and previously reported `mergeable=CONFLICTING` against `main`; the mission allows merging it only with green CI and zero conflicts.
- Scope executed: TODO-007 as scoped this session = runtime (browser) verification of the cross-persona delivery chain, NOT device/emulator QA (still TODO-018...TODO-024) and not release APK (still BLOCKED_EXTERNAL).
- What ran (local, this session, all re-run after final edits):
  - `npx playwright test` in `mvp/apps/web` -> **17/17 passed (36.3s)**, including the new `tests/delivery-flow.spec.ts` (checkout -> vendor chain -> arrival -> OTP -> POD, with the negative POD gate before `ARRIVED`).
  - `npm run typecheck` -> EXIT=0.
  - `python scripts/ui_audit_regression_guards.py` -> **15/15 passed** (source-contract guards, delivery guards target the mobile screens).
  - `PYTHONPATH=. python scripts/test_api_route_hygiene.py` -> OK; `python -m compileall -q scripts` -> OK.
  - `npm run lint` -> the only error is the pre-existing `ops/permissions/page.tsx:36:33` (out of scope); no new errors from this change set.
- Defects fixed inside this TODO (evidence in diff):
  1. Vendor web order page had no driver form and no `picked-up` / `in-transit` / `arrived` stage buttons; the DISPATCHED "ثبت تحویل" button called `/deliver` which is retailer-only (403 for vendor). Replaced with staged dispatch + delivery actions plus a live `وضعیت تحویل` chip fed by `GET /orders/{id}/delivery`.
  2. Retailer POD submit was enabled regardless of delivery state; now gated on `order_status===DISPATCHED && deliveryStatus===ARRIVED && recipientName && otp`, with a `role=status` hint and a "already delivered" message.
  3. `DELIVERY_STATUS_LABEL/TONE` lacked `PICKED_UP` (`جمع‌آوری‌شده`) and `ARRIVED` (`رسیده به مقصد`) -> raw values were rendered.
  4. Checkout confirmation effect re-ran after `clearBasket()` and replaced the success screen with "سبد خرید خالی است." while the order was actually created (order `a23c6368-8c71-48a4-822e-c9249d246754` was SUBMITTED) -> guarded with `if (result) return;`.
- Harness hardening (why the first three runs failed, and the fixes): seed now releases residual `inventory_reservations` (migration 057 deferred invariant), fixture now carries `vendor_phone`, `e2e_db.py` gained an `otp <order_id>` command reading the outbox, and `reset` deletes only baskets NOT referenced by `order_groups` (FK `order_groups.basket_id` has no ON DELETE action; detaching via NULL tripped the allocation-context trigger) so CI retries after a partial run start clean.
- Remaining open: device/emulator delivery QA (TODO-018...TODO-024), TODO-011 notification retention secrets, release APK signing (BLOCKED_EXTERNAL), PR #29 still Draft/CONFLICTING.
- Handoff accepted by: PENDING


### [2026-10-13 UTC] Agent: ChatGPT — GITHUB-SYNC-AND-OPEN-WORK-RECONCILIATION
- State: DONE_VERIFIED for remote GitHub status reconciliation and documentation sync; no application code was changed in this audit. TODO-061 is the next eligible task and has not yet been executed.
- Incoming handoff: opencode report for PRs #36–#39 and TODO-007 completion; independently re-read GitHub PR metadata, current main, TODO_LIST.md, browser/mobile workflow runs, branch search results, and the existing task dependency definitions.
- Repository / branch: `rrasi90/POL-2.3`; default branch `main`. Baseline main SHA at audit start: `e6e039145921303277f569fdafc287290969dcef` (PR #39 merge commit). The current `main` after this snapshot commit is a documentation-only descendant; application-code baseline remains the same unless subsequent code changes are recorded.
- Confirmed merged PR chain: #36 (TODO-006 web basket E2E/fixes) -> merge `ecf3d05177630498c3ec06f13b70c6db99db5735`; #37 (TODO-006 merge evidence) -> `463d780fc74ade31f01cfc13a4a22124c3f891b9`; #38 (TODO-007 cross-persona delivery E2E/UI fixes) -> `4e1daa39a8c9d27f2fff93fa43116db24a71ccab`; #39 (TODO-007 documentation/handoff) -> `e6e039145921303277f569fdafc287290969dcef`. All four PRs are closed and merged on GitHub.
- TODO-006 verified done: the merged Playwright suite has 16 browser scenarios covering retailer login/E.164, basket sync/retry, repeated click, stale/missing basket handling, API failures, item-write failure, checkout gating and allocation preview. The recorded post-merge CI for #36 on merge SHA `ecf3d05177630498c3ec06f13b70c6db99db5735`: Static `38326498911`, Mobile `38326498981`, Independent Verification `38326499062`, Browser E2E `38326499012`; each workflow run concluded success.
- TODO-007 verified done for browser-runtime delivery E2E (not physical device QA): Playwright `17/17 PASS` (36.3s), TypeScript typecheck exit 0, source guards `15/15`, route hygiene OK and Python compileall OK. Four post-merge workflow runs on code merge SHA `4e1daa39a8c9d27f2fff93fa43116db24a71ccab`: Static `38392667118` success, Mobile `38392667176` success, Browser E2E `38392667249` success, Independent Verification `38392667116` success. Important nuance: within the successful post-merge Mobile workflow, the matrix Android QA APK build job was `skipped`; this does not constitute a fresh post-merge APK build. PR #38's PR-head CI had all four required workflows green (`38391078239`, `38391078263`, `38391078196`, `38391078108`).
- PR #39 head check: Static Gate `38393366851` and Independent Verification `38393366824` both succeeded. PR #39 is documentation-only and merged at `e6e039145921303277f569fdafc287290969dcef`.
- Current checklist accounting at the start of this audit: 144 unchecked TODO rows and 8 checked TODO rows in `TODO_LIST.md` (IDs TODO-001 through TODO-008 are the checked sequence; tasks after that remain individually governed by their documented dependencies). TODO-006 and TODO-007 are `[x] DONE_VERIFIED`; TODO-008 records historical CI builds for both QA APKs. The earlier artifacts are not a replacement for the fresh QA rebuild required by TODO-009.
- Main outstanding failure/blocker: recorded `POL Notification Retention` run `38377807571` failed in `archive-expired-inbox`, tracked as TODO-011 (`BLOCKED_EXTERNAL` in the project record). The documented dependency is `DATABASE_URL` and/or `POL_PG_DSN` configured as protected GitHub Actions secrets/environment values. No credentials were changed, exposed, or fabricated in this audit. PR #39's latest recorded required checks passed; I did not claim the scheduled secret-dependent job was repaired.
- Next eligible chain: start TODO-061 now (its only listed prerequisite is TODO-008, which is DONE_VERIFIED), then follow `TODO-062`…`TODO-083`, `TODO-085`…`TODO-130`, the explicitly selected PRE-BUILD tasks among TODO-131…TODO-152, final gate TODO-084, then TODO-009 to rebuild fresh QA APKs for both Retailer and Vendor. Do not skip TODO-084 or infer completion from the old TODO-008 artifacts.
- Dependency-blocked work: TODO-012…TODO-017 are gated behind TODO-011 by the current dependency map. TODO-010 remains REVALIDATE. TODO-018…TODO-024 require emulator/device runtime; the handoff reports Android SDK/ADB/Java unavailable on the agent workstation, which was not independently probed on a local device from this GitHub-only session. TODO-026 live SMS.ir, TODO-027 live object storage, TODO-029…TODO-034 VPS/staging/monitoring and LOI/pilot commitments, and TODO-035…TODO-060 payment/policy/gap/release gates remain open or externally dependent as each task states. TODO-085 and onward also remain open unless individually evidenced.
- PR #29 remains OPEN, Draft and non-mergeable/conflicting (`fix/mobile-motion-audit-20261011`); it was not merged or modified. Branch search confirms old merged-PR branches `agent/pol-2.4-e2e-20261013` and `docs/todo006-merge-evidence` still exist. The #38/#39 feature branches were not returned by branch searches. The two remaining branches were deliberately left untouched because no branch deletion was requested.
- Local workspace note: the handoff reports local `main` at `e6e0391`, equal to `origin/main`, with a clean working tree before this documentation sync. This session independently verified the remote GitHub state but did not have access to the user's local filesystem, so local cleanliness remains an agent-reported fact rather than a direct verification here.
- Next TODO-ID / next agent: TODO-061 — capture the exact current main SHA after this documentation-only commit, run safe preflight and source-of-truth review, then proceed in dependency order. Record all tests/artifacts on the SHA actually tested. Do not start TODO-012 while its TODO-011 precondition remains blocked.
- Handoff accepted by: PENDING

### [2026-10-22 UTC] Agent: ChatGPT — TODO-061 REMOTE BASELINE / SOURCE-AUTHORITY AUDIT
- State: PARTIAL / BLOCKED_LOCAL_WORKTREE — `TODO-061` remains OPEN and unchecked. The canonical task requires recording working-tree status; this session has GitHub repository access but no local checkout or direct access to the user's worktree, so it would be incorrect to claim a clean/dirty result.
- Repository and remote baseline: `rrasi90/POL-2.3`, default branch `main`; verified baseline commit `d9505cfa62c953546b479f4ca8aec1997ca57fbc` from the active PR #40 base and current GitHub source links. Remote status is authoritative for this audit; local status is UNKNOWN, not assumed clean.
- Active engineering line: PR #40 `agent/mobile-motion-port-20261022`, base `d9505cfa62c953546b479f4ca8aec1997ca57fbc`, current audited head `e158a04c5ada4e1d203ef936ea8a28f49823ccc4`, OPEN / Draft / mergeable. The PR contains 29 changed files (motion primitives and integrations, mobile regression guards, QA APK scripts/workflow, design spec, and the existing append-only TODO journal). New required CI runs on `e158a04` were QUEUED at the time of this journal entry; results from earlier SHA `ab8e4882420d8f953cd21dd73dde4e51d9f634bc` are not promoted to the new head.
- Separate stale line: PR #29 `fix/mobile-motion-audit-20261011`, head `f4fcf5a92c8c6bfa331c9c2d73017a3ef4a34b89`, remains OPEN / Draft / non-mergeable. No merge, branch deletion, or rewrite was performed.
- Canonical sources read from `main`:
  - `POL_00_PROJECT_CONTROL/CURRENT_SOURCE_OF_TRUTH.md` blob `54c2fd7b0c3df1c9ac036d1f0ab934db9d4b911b` (245 lines).
  - `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` blob `d7b344e61f817a57e8619414d36698a3474c9aea` (317 lines).
  - `mvp/MVP_API_MAP.md` blob `1ed563a1180fedcc5fd72d602ca546daf361d9b3` (312 lines).
  - `mvp/MVP_SCREEN_MATRIX.md` blob `a302cc93e8c7c379696e13e0bc81a6e4b97e880e` (285 lines).
  - `mvp/MVP_KNOWN_GAPS.md` blob `0759d570e5e632f3b007f95fbb99b2fcd380c21f` (1,012 lines).
  - `mvp/BUILD_PLAN.md` blob `6c906b5e8aeb3af39014703babf5776fa021d499` (349 lines), `mvp/apps/mobile/README.md` blob `fc78b6dc365b0aa08916de8c4c55f02a1744a752` (73 lines), `mvp/apps/mobile/src/__tests__/parity.md` blob `0397891572a674a0ba858c36677e9b1d8ff08cc4` (86 lines), and `.agents/rules/00-pol-canonical-safety.md` blob `32ea6baaac844d4365fba78d2e9f85dded7a24d3` (116 lines).
- Authority confirmed: Decision Register governs D-001…D-028; current product decisions include multi-vendor basket (D-014), PostgreSQL 18 (D-015), four-digit OTP policy (D-018), Python production runtime (D-019), and FastAPI transport boundary (D-020). Mobile parity/source status is separate from device certification; native barcode/camera and full screen-by-screen Night visual verification remain runtime/device gates.
- Material source-of-truth drift found (not silently repaired in this task):
  1. `CURRENT_SOURCE_OF_TRUTH.md` line 49 says migration head `048` on the remediation branch; `mvp/BUILD_PLAN.md` line 17 describes the contiguous chain through `076`; `mvp/MVP_KNOWN_GAPS.md` references migration `071`. The canonical schema-head statement needs reconciliation against the actual file tree/migration manifest before a gate relies on it.
  2. `CURRENT_SOURCE_OF_TRUTH.md` contains mutually stale remediation snapshots: line 187 says the remediation branch was integrated into main, while lines 216–237 describe remediation as isolated on older branch heads and say fresh CI steps were unavailable. Those dated checkpoint notes must not override current live GitHub refs or current-head CI.
  3. `mvp/MVP_API_MAP.md` describes actual FastAPI sources on the historical `research-hardening-2026-09-14` branch and says contract-only endpoints were promoted on a remediation branch; current route/API reality must be re-audited at the active `main` SHA before the API map is used as current runtime proof.
  4. The authority files reference `POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md`, but fetching that exact path returns 404 and exact filename search found no repository result. `scripts/application_boundary.py` exists; do not treat it as a file-equivalent document without an explicit source-of-truth correction.
  5. `mvp/BUILD_PLAN.md` and mobile parity documents still contain checkpoint claims that fresh CI was blocked before useful steps. Those statements are historical unless refreshed against exact current run IDs/SHA; they are not in themselves proof of present failure.
- Latest available evidence when this entry was prepared: on earlier PR #40 head `ab8e488`, Static Gate and Independent Verification succeeded; backend suite reported `663 passed, 0 failed, 0 skipped`; browser E2E reported `17 passed`; mobile functional QA `28/28`, mobile regression QA `36/36`, typecheck and Expo Android export passed. On that SHA the TODO-084 evaluator reported `BLOCKED` because 82 required pre-build rows were not `DONE_VERIFIED`, so both standard and x86_64 APK jobs were skipped. These results are evidence for `ab8e488` only, not the new current head `e158a04`.
- Not done / blocker: no local `git status`, local HEAD, uncommitted diff or local runtime versions could be verified; current-head CI for `e158a04` was queued. `TODO-061` therefore remains open until the active worktree is checked or the task owner explicitly accepts a remote-only baseline record.
- Next action: obtain the actual local checkout/worktree status; reconcile the API boundary document reference and migration-head statement in a dedicated source-authority task; then re-run current-head CI and continue TODO-062… in dependency order. Do not mark TODO-061 done based on remote metadata alone, do not promote prior-SHA evidence, and do not bypass the TODO-084 QA APK gate.
- Working-tree status: NOT AVAILABLE IN THIS SESSION — no claim of clean/dirty state.
- Handoff accepted by: PENDING


### [2026-10-22 UTC] Agent: ChatGPT — MOTION-BRANCH DIVERGENCE / CURRENT-HEAD CI FOLLOW-UP
- State: PARTIAL / IN_PROGRESS — TODO-061 remains OPEN; no source branch was merged and no TODO checkbox was promoted.
- Exact remote comparison: `feat/mobile-motion-layer` tip `2dfdd26a672c3bec44b6a00685a833d0fa7d0090` versus main `d9505cfa62c953546b479f4ca8aec1997ca57fbc`: `status=diverged`, `ahead_by=7`, `behind_by=22`, merge base `26e9b8b7766d871cefdd8e7257439646f5b9f399`. This corrects the stale local handoff's opposite/ahead-behind numbers; it is a remote fact, not a claim about the user's local worktree.
- Preservation proof: created `backup/feat-mobile-motion-layer-20261022` from the original feature branch and compared the two refs; they are identical at `2dfdd26a672c3bec44b6a00685a833d0fa7d0090`. Original source branch was not modified.
- Content reconciliation: fetched the original feature branch and the current PR #40 port for AppShell, OfflineBanner, shared UI, all motion primitives and mobile screens. Core motion screens/components (OfflineBanner, shared UI, login, retailer, vendor, token/hook set) mostly match source intent; the port contains deliberate current-main changes for startup failure recovery, cancelled-animation cleanup, success timing, finite Pulse replay and delivery fallback. OrderDetail retains current-main delivery status/actions rather than overwriting current behavior from a stale line-for-line snapshot.
- Scope exclusion: the original feature branch's diff includes 21 `motion_smoke_*.png` files and unrelated branch additions such as Cartona reverse-engineering materials, a vendor interview DOCX, ignore entries and workspace Metro configuration. The 21 capture PNGs and branch-only competitive/reference payloads were not blindly copied to PR #40; capture provenance is not yet current-SHA-certified. The `metro.config.js` present in both branch and port resolves identically, so it is not an extra port-only addition.
- PR #40 current head at this checkpoint: `1c793b5363efda1fd6db0c32bf098472a6e9a6f9`, base `d9505cfa62c953546b479f4ca8aec1997ca57fbc`, OPEN/Draft/mergeable. No merge was performed.
- Current-head CI: four fresh runs were created for this head: Static Gate `39697848982`, Browser E2E `39697848996`, Mobile Verification `39697848991`, Independent Verification `39697848994`. Browser E2E had reached setup/Node install at the last poll; other runs were queued. Results must be polled after this journal entry, because this document change itself creates a new PR #40 head and invalidates source-SHA claims.
- Browser CI issue found and repaired in the current branch: run `39697247200` failed before running tests because `npx playwright install --with-deps chromium` invoked apt and received HTTP 403 from `packages.microsoft.com`. Changed `.github/workflows/pol-browser-e2e.yml` to `npx playwright install chromium`, avoiding the optional package-list refresh. This fix is committed in PR #40 at `1c793b5363efda1fd6db0c32bf098472a6e9a6f9`; the new browser run must prove the workaround actually works.
- QA APK policy remains fail-closed: in earlier CI SHA `ab8e4882420d8f953cd21dd73dde4e51d9f634bc`, the pre-build gate reported 82/82 TODO rows not `DONE_VERIFIED`, so all four APK jobs were correctly skipped. Pre-gate artifacts previously built on `8200f397` are stale and are not accepted as current deliverables. Do not bypass TODO-084.
- Next action: poll all four runs for the newest PR #40 head; if browser succeeds with the no-apt install, preserve that evidence. Then append a final journal entry with the final CI SHA/results and artifact gate status. Keep PR #40 and #41 Draft; leave PR #29 untouched pending evidence-based supersession. Local checkout status remains unavailable and must not be inferred.
- Handoff accepted by: PENDING


### [2026-10-22 UTC] Evidence intake — user-provided `pol-verification-evidence.zip`
- Container path: `/mnt/data/pol-verification-evidence.zip`; ZIP contents were inspected directly.
- Files: `pol-test-results.json`, `failure_inventory.txt`, and `final_certification_b69798659beedb782cc3969268bb5f12d5efe01d.json`.
- JSON provenance: tested commit/workflow SHA `b69798659beedb782cc3969268bb5f12d5efe01d`; GitHub Actions run `38186170942`, attempt `1`; PostgreSQL 18.6; Python 3.11.17; result `663 collected / 663 passed / 0 failed / 0 skipped`, 203.26 seconds; verdict `AUTOMATED_TESTS_PASSED`.
- The machine-readable evidence expressly says release/pilot certification is NOT claimed and excludes physical-device visual QA, live SMS, live object storage, banking reconciliation and operational pilot readiness.
- Classification: real, machine-readable **historical** evidence for SHA `b697986...`, not current-head evidence for PR #40 at `1c793b5363efda1fd6db0c32bf098472a6e9a6f9`. The old report cannot replace the currently running independent test suite.
- No APK was present in this ZIP. User-reported local APK claims remain LOCAL-ONLY and unavailable for independent hashing/signature validation in this session.


### [2026-10-22 UTC] Final current-head evidence — PR #40
- Tested source SHA: `1c793b5363efda1fd6db0c32bf098472a6e9a6f9`; base: `d9505cfa62c953546b479f4ca8aec1997ca57fbc`; PR #40 remains OPEN / Draft / not merged.
- Static Gate run `39697848982`: SUCCESS.
- Browser E2E run `39697848996`: SUCCESS, 17/17 Playwright tests. Chromium installation succeeded with `npx playwright install chromium` after removing `--with-deps`'s apt metadata refresh that returned HTTP 403 from packages.microsoft.com.
- Mobile verification run `39697848991`: SUCCESS — typecheck, 28/28 functional checks, 38/38 regression checks, deterministic Vendor mock QA, both Expo configs, both static pre-APK gates, Node syntax checks of the QA/x86 and manifest/gate scripts, and Expo Android export passed.
- Independent Verification run `39697848994`: SUCCESS — 663 passed, 0 failed, 0 skipped; PostgreSQL 18.6 / Python 3.11.17. Raw log shows one Starlette/httpx deprecation warning only.
- Artifact provenance: current-SHA verification evidence ZIP id `12392005802`, SHA-256 `11489fdabda258b299eac48c30c0954b10e2f528cf177d2b07373daaec27eed1`, URL `https://api.github.com/repos/rrasi90/POL-2.3/actions/artifacts/12392005802/zip`, expires 2026-11-21. Browser report ZIP id `12391324089`, SHA-256 `c96cac177374726e331c0e03df8563f904f36990a1424f04baf3731110592f74`, URL `https://api.github.com/repos/rrasi90/POL-2.3/actions/artifacts/12391324089/zip`, expires 2026-11-05.
- QA APK eligibility run is part of mobile run `39697848991`: SUCCESS as a policy evaluator but result is BLOCKED — 82/82 required pre-build rows are not `DONE_VERIFIED`. Both standard and x86_64 APK matrices were SKIPPED by design. No APK, package ID, signing result, file SHA or size is claimed for current SHA.
- Prior SHA `ab8e488...`'s 663/663 + 17/17 + 36/36 evidence and user-provided ZIP tested on `b697986...` remain valid only for those older SHAs; the current-head evidence above supersedes them for automated software checks, not for device or live-provider acceptance.
- PR #29 remains OPEN / Draft / non-mergeable and was not modified or closed. Original `feat/mobile-motion-layer` SHA `2dfdd26a672c3bec44b6a00685a833d0fa7d0090` is preserved by an identical backup branch. PR #40 keeps its code-only current-main motion port, excludes 21 un-re-certified historical motion screenshots, and remains Draft/not merged.
- Remaining blockers: TODO-061 local worktree status remains unavailable in this GitHub-only runtime; TODO-084 remains open and blocks all QA APK construction; physical emulator/device visual QA and package/signature/hash checks of newly built APKs remain open; DNS/domain, public TLS and real SMS remain deferred per user's instruction.
- Handoff accepted by: PENDING


### [2026-10-22 UTC] Agent: ChatGPT — TODO-LIST-EXECUTION-ORDER-AND-DEPENDENCY-REFRESH
- State: DOCUMENTATION_UPDATED / REVIEW_REQUIRED — modified on branch `agent/todo-061-source-baseline-20261022`; PR #41 remains Draft and unmerged. This is a proposed documentation update only; no task has been marked complete by this update.
- Current `main` baseline observed: `d9505cfa62c953546b479f4ca8aec1997ca57fbc`. PR #40 head `1c793b5363efda1fd6db0c32bf098472a6e9a6f9` has green Static, Browser E2E (`17/17`), Mobile Verification (functional `28/28`, regression `38/38`, typecheck/export), and Independent Verification (`663/663`) runs. PR #40 remains Draft/unmerged; its TODO-084 check reported `82/82` required rows unverified, and both standard/x86_64 APK matrices were skipped. The checklist now states these constraints explicitly.
- Updated top-of-file provenance, replaced the old serial waterfall with a dependency-aware execution plan, added domainless/test-OTP rules, distinguished TODO-011 Notification Retention GitHub secrets from SMS.ir, reworked dependencies for TODO-012…040 and TODO-054…061/148, reworked the release gates TODO-056…060, and added `TODO-153` as the final public DNS/domain/TLS stage. The live SMS task `TODO-026` now explicitly depends on TODO-153 and is reserved for the final provider-validation phase.
- The intended progression is: source-of-truth/worktree → reproducible env and schema → backend/auth/security/API → web journeys/feature coverage → mobile static checks → TODO-084 → QA APKs → device/runtime tests → staging by IP/private access, object storage, backup/runbook/monitoring → final domain/DNS/HTTPS → real SMS.ir → Go/No-Go and signed release artifact.
- Before domain/SMS, all auth behavior must continue to be tested against a test OTP provider or controlled outbox; verification policy/rate limits are never disabled. Storage live tests remain a separate external dependency that can be completed before the final domain/SMS stage.
- Remaining open blockers are deliberately still open: local worktree status cannot be independently read from this GitHub-only runtime; canonical migration-head/API-boundary references require evidence-based reconciliation; TODO-084 is still blocked; QA APK/device artifacts do not yet exist on current PR #40 head; domain/TLS and SMS live tests have not been run.
- Changed only `TODO_LIST.md` on the documentation branch; no app logic, migration, credential, or deployment setting was changed. Existing historical handoff entries were retained.
- Next action: review/merge PR #41's checklist only after verifying the dependency edits, then continue TODO-061 in an environment with the actual local checkout and re-evaluate the pre-build gate. Do not merge PR #40 solely because its CI is green; code/design review and current-main integration are still required.
- Handoff accepted by: PENDING
