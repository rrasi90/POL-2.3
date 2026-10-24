# 02 — Auth & Onboarding Screens

Screens before the user is a fully-verified retailer. Evidence: assets (`splash.png`, `onboarding1-3`, `have_account`, `location_permission`, `notification-permission-*`), events, frames.

---

## 2.1 Splash

**هدف:** brand moment + app initialization (remote config fetch, session restore, update check).

**آناتومی:**
- Full-screen brand blue `#16268D`
- Isometric cube pattern (white outlines) fading from dense at top to solid blue at bottom
- Centered logo: white delivery-runner + orange box + "كرتونة" wordmark (on returning-user variant: faded product-grid tiles behind)

**حالت‌ها:** normal → onboarding (first run) | returning-user interstitial | forced-update screen | landing.

**شواهد:** `assets/images/splash.png`, `returning-user-onboarding8.png`; event `newapp_splash_completed`, `newapp_startup_completed`.

---

## 2.2 Landing / interstitial

**هدف:** re-engage returning users / campaigns entry.
**محتوا:** full-screen promo with CTA. Events: `landing_viewed`, `landing_cta_clicked`.
**نکته برای POL:** treat as remote-config driven interstitial with skip; never block >1 tap.

---

## 2.3 Onboarding (first run only)

**هدف:** sell the loop in 3 photo slides — ① your store's shelves ② order & pay ③ delivery to your shop.

**آناتومی (هر اسلاید):**
- Full-bleed real photography (retail context, Arabic signage)
- Slide indicator dots (`smooth_page_indicator`) + skip
- CTA to next slide / start

**اکشن‌ها:** swipe (`onboarding_slide_swiped`), skip (`onboarding_skipped`), complete (`onboarding_completed`).
**قابل بازپخش:** returning-user variant exists (`returning-user-onboarding8.png`).

---

## 2.4 Login — phone step

**هدف:** returning retailers sign in with phone + six-digit numeric OTP (current D-018 policy, revised 2026-10-25).

**آناتومی:**
- Brand-blue header block with logo
- Phone input (with country code, RTL layout)
- Primary CTA "التالي" (Next) — `login_next_clicked`
- **Support row at the bottom: call button + chat button** (`login_contact_call_clicked`, `login_contact_chat_clicked`) — critical for a low-digital-literacy audience
- Language toggle (AR/EN) available in app (locale change via webview action flag `ACTION_LOCALE_CHANGED_BY_WEBVIEW`)

**حالت‌ها:** `login_error_displayed2`, `login_failed` (inline errors), phone validation.

## 2.5 Login — OTP

**آناتومی:** boxed PIN input (`pinput`), auto-read via SMS autofill, resend countdown timer, "التحقق" CTA.
**اکشن‌ها:** `login_otp_screen_viewed`, `login_otp_entered`, `login_otp_resend_clicked`, `login_otp_verification_result2`.
**Success →** location permission pre-screen → home.

---

## 2.6 Permission pre-screens (before system dialogs)

**هدف:** context-first permission asks with illustrated value statements — maximizes grant rate.

### Location pre-screen
- Illustration: phone + truck + map pin (`location_permission.png`)
- Copy explains delivery optimization: "نجمع معلومات الموقع الجغرافي (بإذنك) لتحسين خدمة التوصيل"
- CTA → system dialog; options recorded (`location_perm_option_selected2`); result logged (`location_permission_result`)
- Also handles "تنبيه الموقع" and disabled services state (`LOCATION_SERVICES_DISABLED`)

### Notifications pre-screen
- Illustrated header (`notification-permission-screen-header.png`)
- Value copy: "سماحك بالإشعارات يخلينا نوصلك بكل جديد من طلباتك، التنبيهات المهمة، والخصومات كمان"
- Then the Android 13+ system prompt (`notifications_system_prompt_shown`)

**نکته:** these screens come *after* auth but *before* full home — the app asks at the moment of highest motivation.

---

## 2.7 Forced update screen

**هدف:** block outdated clients.
**محتوا:** illustration + "في إصدار جديد فيه تحسينات ومميزات" + single CTA to store.
**اکشن‌ها:** `forced_update_screen_viewed`, `forced_update_cta_clicked`, `update_install_detected`, `update_redirect_result`.
**Config:** `MINIMUM_APP_VERSION`, `LATEST_APP_VERSION`, `UPDATE_CHECK_INTERVAL_MINUTES` (soft-update nags without a screen), Huawei AppGallery link compiled in (`appgallery.cloud.huawei.com/.../C107487341`) — **POL must do the same for CafeBazaar/Myket**.
