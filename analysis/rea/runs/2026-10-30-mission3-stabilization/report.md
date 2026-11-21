# Mission 3 — Stabilization, Git Hygiene & Persistent Internet Access

Date: 2026-10-30 · Scope: تثبیت و مستندسازی — بدون تغییر منطق کسب‌وکار/API/schema

## مرحله ۱ — وضعیت ثبت‌شده (دست نخورده)

**سرویس‌های زنده (همه بدون تغییر ماندند):**

| سرویس | محلی | عمومی | وضعیت |
|---|---|---|---|
| Postgres `pol_test` | 127.0.0.1:5432 | — | 25 users / 25 orgs / 22 otp_challenges |
| API (e2e_serve, seed E2E) | 127.0.0.1:8001 | https://monthly-limit-encountered-cartridges.trycloudflare.com | `/healthz` ok |
| Web (Next dev) | 127.0.0.1:3000 | https://resort-jimmy-marks-yes.trycloudflare.com (via gateway) | HTTP 200 |
| Gateway تک‌مبدأ | 127.0.0.1:8080 | — (توسط تونل وب پوشش داده می‌شود) | `/healthz` ok |

- هر دو تونل با `--protocol http2` (PIDs 25788→8001، 29208→8080) — **متوقف یا بازسازی نشدند**.
- هیچ APK بازسازی نشد.
- یک سرور Next اضافی/یتیم روی پورت **3001** (node.exe PID 31316) شناسایی شد — تونل ندارد، برای پاکسازی بعدی مستند شد، لمس نشد.
- گوشی (Huawei P30 Pro) در شروع Mission 3 از USB جدا شده بود (`adb devices` خالی) — تأثیری روی سرویس‌ها ندارد.

**Git (ابتدای مأموریت):**
- Branch: `research/cartona-uiux-extraction-phase2-20261027` @ `a219a2bf` (== origin، همگام)
- تغییرات: `mvp/apps/mobile/package.json` (M)، `mvp/apps/web/src/lib/auth/api.ts` (M) + دو پوشه گزارش untracked
- هیچ secret/توکنی در گزارش‌ها یا Git قرار نگرفت (تونل‌های Quick توکن ندارند؛ لاگ‌ها فقط URL عمومی را شامل می‌شوند).

## مرحله ۲ — بررسی اصلاح احراز هویت

**diff دقیق (`mvp/apps/web/src/lib/auth/api.ts`, +9/−1):** فقط داخل `tryRefresh` — پس از موفقیت refresh، اکنون `user` و `role` موجود در استور به `setSession` پاس داده می‌شود. بدون این، `setSession` پروفایل localStorage را با null بازنویسی می‌کرد و `RequireRole` کاربر را به لاگین برمی‌گرداند.

- محدود به حفظ `user`/`role` است؛ هیچ مسیر دیگری (login، logout، api-client، store) تغییر نکرده.
- **تست‌های مرتبط دوباره اجرا شد — 26/26 پاس** (login 6، basket-sync، status-labels، a11y) روی سرورهای ایزوله (8002/3002).
- `.pol-design/evidence/screenshots` پس از اجرا: **0 تغییر** (هر تغییری که تست‌های بصری ایجاد می‌کنند به HEAD برگردانده شد).
- نکته محیطی: اجرای ایزوله بدون `POL_CORS_ORIGINS` هم‌سطح پورت وب باعث ۱۷ شکست کاذب CORS می‌شود (پورت‌های مجاز پیش‌فرض API فقط 3000/3001 است) — برای اجرای ایزوله باید ست شود.

## مرحله ۳ — Git

- **منشأ `mvp/apps/mobile/package.json`:** تغییر `expo start --ios/android` → `expo run:ios/run:android` از قبل موجود است؛ مستند در TODO_LIST.md (خطوط 2292–2320): از شاخه `agent/pol-2.3-integration-fdx` (commit `a8ef7840`)، cherry-pick شده روی `chore/mobile-expo-run-scripts-20261022` به‌عنوان **Draft PR #45**. تصریح ژورنال: جداگانه بررسی شود، merge نشود. **به فیکس احراز هویت نسبت داده نشد و commit نشد.**
- **تفکیک:** پوشه‌های گزارش (`analysis/rea/runs/2026-10-29-*` و `2026-10-30-*`) untracked ماندند و وارد commit محصول نشدند.
- **Commit مستقل:** شاخه جدید `fix/web-refresh-session-preserve-20261030` از HEAD قبلی ساخته شد؛ فقط `api.ts` مرحله‌گذاری و commit شد (`b4a48801`، +9/−1). پیش از commit: `git diff --check` تمیز، اسکن secret منفی، staged diff بازبینی شد.
- **Push:** موفق؛ `LOCAL b4a48801 == REMOTE b4a48801` (تطابق تأیید شد).
- روی `main` هیچ commit یا force-push انجام نشد.
- لینک پیشنهادی PR (باز نشده): https://github.com/rrasi90/POL-2.3/pull/new/fix/web-refresh-session-preserve-20261030
- حالت کارگری باقی‌مانده: `package.json` (M، مستند فوق) + دو پوشه گزارش untracked.

## مرحله ۴ — پنج تست شکسته (هر دو محیط: سرور زنده و ایزوله — شکست‌ها بازتولید شدند)

| # | تست | خطا | علت محتمل | بازتولید |
|---|---|---|---|---|
| 1 | `visual-capture` «capture authenticated retailer golden surfaces» | `/retailer contains internal/English term: FMCG` (قطعی و deterministic) | متن فارسی صفحه `/retailer` شامل اصطلاح لاتین FMCG است («...اقلام ضروری FMCG») و gate QA بصری انگلیسی‌زدایی را رد می‌کند — باگ کپی UI، نه زیرساخت | `npx playwright test tests/visual-capture.spec.ts -g "authenticated retailer"` |
| 2 | `visual-capture` «operations and admin triage surfaces» | Timeout 90s؛ صفحه در لحظه شکست: لاگین با پیام «نشست شما منقضی شده است» | چالش OTP اپراتور (`+989119402598`) در DB ساخته شد ولی هرگز VERIFIED نشد (PENDING) — ورود پرسونای غیر-خرده‌فروش در helper ناتمام می‌ماند؛ نیاز به بررسی helper/login اپراتور با لاگ دسترسی | `npx playwright test tests/visual-capture.spec.ts -g "operations"` |
| 3 | `visual-capture` «field activator golden surfaces» | Timeout 90s؛ همان الگو | چالش OTP میدانی (`+989104320979`) PENDING ماند — همان علت #2 | `... -g "field activator"` |
| 4 | `visual-capture` «seeded product, vendor, checkout…» | Timeout 240s | زنجیره چند-پرسونایی (شامل همان لاگین‌های ناتمام #2/#3) | `... -g "seeded product"` |
| 5 | `delivery-flow` «cross-persona delivery flow» | انتظار دکمه «شروع آماده‌سازی» برآورده نشد (element not found)؛ در اجرای قبلی همان نقطه «Application error: a client-side exception» دیده شد | نقاط شکست ناپایدار در جزئیات سفارش بنکدار — احتمال کرش سمت کلاینت در رندر شرطی صفحه سفارش؛ نیاز به بررسی جداگانه با console مرورگر | `npx playwright test tests/delivery-flow.spec.ts` |

- این ۵ شکست در هر دو تنظیم (سرورهای زنده 3000/8001 و ایزوله 3002/8002) بازتولید شدند → محیطی نیستند. شواهد خام: `mvp/apps/web/test-results/**/error-context.md` + `results.json`.
- **هیچ‌کدام اصلاح نشد** — خارج از مجوز این مأموریت.
- **تحلیل مستقل hydration (TODO-078):** `loadInitial()` در `src/lib/auth/store.ts` در زمان init ماژول (سمت کلاینت) `localStorage` می‌خواند؛ HTML رندر سرور با state اولیه کلاینت فرق می‌کند → hydration mismatch (Recoverable، صفحه بازیابی می‌شود). جهت رفع (پیاده‌سازی نشده — نیازمند scope مستقل): انتقال rehydrate به `useEffect` پس از hydration یا پرچم hydrated. ربطی به فیکس refresh ندارد (فیکس فقط runtime `tryRefresh` است).

## مرحله ۵ — طرح دسترسی پایدار (بدون هزینه، بدون تغییر DNS/Nameserver)

**وابستگی فعلی به URL:**
- وب: فقط URL تونل وب (گیت‌وی) — اپ با `NEXT_PUBLIC_API_BASE_URL` خالی، relative صدا می‌زند؛ عوض شدن URL فقط یعنی باز کردن URL جدید.
- هر دو APK: URL تونل API در زمان build داخل باینری است → هر تغییر URL = rebuild هر دو APK (~4 دقیقه).
- دیتابیس/پنل‌ها/5432/8080 عمومی نیستند (فقط 3000-مثل و 8001 از طریق تونل).

**گزینه‌ها:**

| گزینه | هزینه | پایداری | امنیت | تغییر لازم |
|---|---|---|---|---|
| **A. Named Tunnel کلادفلر (رایگان)** با دامنه موجود روی یک اکانت Cloudflare | 0 | پایدار (hostname ثابت، reconnect خودکار) | بهترین: توکن تونل فقط سمت میزبان؛ می‌توان مسیرهای داخلی را فیلتر کرد | نصب tunnel به‌صورت سرویس ویندوز + ۲ hostname (web/api) + آپدیت `.env.local`ها + rebuild یک‌باره APKها |
| **B. استقرار روی VPS موجود** (`docker-compose.vps.yml` آماده است: nginx:80 + api + web + postgres + worker) | هزینه VPS (اگر موجود نباشد) | بالاترین (برخلاف میزبان شخصی، 24/7) | TLS و server_name باید در `deploy/nginx.conf` تکمیل شود (فعلاً `_`)؛ CORS و URLها env-محور آماده‌اند | ست‌کردن envهای VPS، دامنه، و یک‌بار build ایمیج‌ها |
| **C. Runbook تونل Quick فعلی** (اسکریپت بازسازی URL + آپدیت env + rebuild) | 0 | ضعیف (URL با هر ری‌استارت عوض می‌شود) | ضعیف‌تر: URLهای عمومی بدون احراز هویت | تقریباً هیچ — فقط خودکارسازی |
| D. ngrok/مشابه رایگان | 0 | مشابه C (موقتی) + نیازمند اکانت | مشابه | مشابه C |

**توصیه:** A به‌عنوان گام فوری (رایگان و پایدار، فقط نیازمند لاگین یک‌باره اکانت Cloudflare توسط شما — هیچ توکنی از ما درخواست/چاپ نمی‌شود)، و B به‌عنوان مقصد نهایی برای محیط آزمایشی 24/7. تا تأیید شما هیچ DNS/Nameserver یا اکانتی تغییر نمی‌کند. پیش‌نیازهای A: (1) دامنه روی اکانت Cloudflare، (2) `cloudflared tunnel login` یک‌باره، (3) دو hostname مثل `pol-web.<domain>` و `pol-api.<domain>`، (4) اجرای تونل به‌صورت سرویس، (5) آپدیت دو `.env.local` + rebuild یک‌باره APKها.

## جمع‌بندی
- فیکس احراز هویت: بررسی، تست (26/26)، commit مستقل `b4a48801` و push با تطابق SHA ✓
- تغییر `package.json`: منشأ مستند، جداشده، commit نشده ✓
- ۵ شکست تست + hydration: مستند با شواهد و راه بازتولید، بدون اصلاح ✓
- طرح دسترسی پایدار: ۴ گزینه مقایسه‌شده، توصیه A سپس B، منتظر تأیید شما ✓
