# Cartona App — Reverse Engineering & Design Logic Reference

**Document ID:** `POL-DESIGN-CARTONA-REF-001`
**Version:** `1.0.0`
**Date:** 2026-10-05
**Status:** REFERENCE (competitive analysis — not canonical POL direction)
**Source:** `cartona app/cartona.apk` (base APK of a split App Bundle, v8.4.6, versionCode 70000083)
**Decompiled output:** `cartona app/decompiled/` (jadx 1.5.3 — resources + Java wrappers)

**Purpose:** فهم کامل منطق طراحی صفحات اپ کارتونا برای استفاده در طراحی POL. این سند از روی APK رسمی کارتونا (پلتفرم B2B کمرچه مصر) استخراج شده است.

**Important limitation (read first):** این فایل، APK پایه (base) از یک App Bundle است. کتابخانه native حاوی کد Dart یعنی `libapp.so` در split معماری (`base__abi`) قرار دارد و در این فایل نیست. بنابراین کد Dart (ویجت‌ها، روت‌ها، مقادیر دقیق token ها) قابل دیکامپایل نبود. همه‌ی آنچه اینجا آمده از ۴ منبع معتبر استخراج شده: (۱) AndroidManifest، (۲) کل asset های Flutter (تصاویر/فونت/SVG/آیکون)، (۳) لیست کامل پکیج‌های Dart از `NOTICES.Z`، (۴) ریسورس‌های اندروید. برای لایه بعدی تحلیل، فایل XAPK کامل یا `split_config.arm64_v8a.apk` لازم است (بخش ۱۰).

---

## 1. App identity

| Field | Value |
|---|---|
| App name | كرتونة (Cartona) |
| Package | `com.cartona` |
| Version | 8.4.6 (70000083) |
| Platform | Flutter (embedding v2), single `FlutterActivity` |
| Min / Target SDK | 24 / 36 (Android 16) |
| Model | B2B marketplace — grocery retailers order from suppliers/brands (Egypt) |
| Companion apps referenced | `com.cartona.suppliers`, `com.cartona.delivery_driver_app`, `com.cartona.mandoob` (sales rep) — plus benchmarking queries against `com.maxab.maxab`, `com.fawry.fawryb2b` |
| Backend traces | Firebase project `cartona-69c1a`, Google Maps API key, AppsFlyer OneLink (`cartona.onelink.me/8xkB`), universal links to `https://cartona.com` |

## 2. Technology stack (from NOTICES.Z — full Dart package inventory)

**Core / architecture**
- Flutter embedding v2, `state_notifier` + `event_bus` (state management), `synchronized`
- Network: `dio` + `pretty_dio_logger` (visible network logging in release — note), `http`, `connectivity_plus`
- Local storage: `sqflite` (structured local cache), `shared_preferences`
- Serialization: `json_annotation`, `equatable`, `freezed`-adjacent toolchain (`checked_yaml`)

**Auth & verification**
- `pinput` + `pin_input_text_field` (OTP boxes), `sms_autofill` (auto-read OTP), `flutter_timer_countdown` (OTP resend countdown)

**Maps & location (dual provider)**
- `google_maps_flutter` AND `flutter_osm_plugin` (+ `routing_client_dart`, `geolocator`) — Google Maps with an OSM fallback/switch

**KYC / documents**
- `camera`, `image_picker`, `file_picker`, `flutter_image_compress` (document capture pipeline for national ID front/back)

**Firebase suite**
- `firebase_core/analytics/crashlytics/messaging/remote_config` — remote config drives UI/feature flags; FCM for order notifications

**Analytics / marketing / anti-fraud**
- `appsflyer_sdk` (attribution, OneLink), `posthog_flutter` + `segment_analytics` (dual product analytics)
- `root_checker_plus`, `android_app_checker` (detects 20+ fake-GPS apps and parallel-space/clone apps — cash-on-delivery fraud defense)
- Google Play Integrity via `com.pairip` (license check + Application wrapper)
- `flutter_fgbg` (foreground/background lifecycle for session security)

**UI toolkit packages (design-system fingerprint)**
- `flex_color_scheme` (theme engine), `flutter_svg`, `lucide_icons`, `ionicons`, `font_awesome_flutter`, `cupertino_icons`
- `flutter_staggered_grid_view` (masonry product grids), `infinite_scroll_pagination` (paged catalog)
- `smooth_page_indicator` (onboarding dots), `dotted_border`, `sliver_tools` (custom scroll surfaces), `spring_animation`, `visibility_detector`, `flutter_confetti` (success celebrations), `timeline_list` (order tracking timeline)
- `flutter_inappwebview` (embedded web — payment/content), `url_launcher`, `share_plus`, `app_links` (deep links)
- `freshchat_sdk` (in-app support chat), `wakelock_plus` (keep screen on — likely delivery/scan flows)

## 3. Design system — extracted primitives

### 3.1 Color
| Token | Value | Evidence |
|---|---|---|
| Brand primary (deep royal blue) | **#15268E** (SVG fills) / **#16268D** (splash bg) | icon SVGs, splash, returning-user interstitial |
| Accent (orange) | **#FF951A** | logo box, app icon |
| Tint surfaces | #F0F4FD, #D2DFF5, #D6E3FA, #EEF2F9 | illustration backgrounds |
| Canvas | #FFFFFF | registration bg |
| Pattern stroke | #15268E @ 20% opacity | `pattern.svg` |

System = primary-blue-dominant with a single warm orange accent used sparingly (logo box, CTAs). Light mode only (no dark tokens found in native layer; Flutter side unknown).

### 3.2 Typography
| Family | Role | Weights available |
|---|---|---|
| **Somar Sans** | Primary Arabic brand face | Regular, Medium, SemiBold, Bold (static) |
| **Rubik** | Latin / numerals | Variable (wght + italic) |
| **Cairo** | Secondary Arabic | Variable (slnt+wght) |
| Icon fonts | MaterialIcons, Lucide, Ionicons, FA (3 cuts), Cupertino | — |

RTL-first: Arabic is the primary locale (`layoutDirection` handled in configChanges; onboarding art contains Arabic signage; app label Arabic).

### 3.3 Iconography
- **Lucide** (stroke-based, 2px) as the functional icon set — confirmed inside `qube.svg` header (`class="lucide lucide-package"`).
- Custom Untitled-UI-style named SVGs: `icon-marker-pin-01/02`, `icon-arrow-up-left`, `icon-clear-circle`, `icon-minus/plus`, `icon-target`, `camera`, `chat`, `phone`, `image` — 24-grid stroke icons, brand-blue fill/stroke.
- Business-category pictograms: flat two-tone (navy #3xxxxx on transparent) filled shapes — see 3.5.

### 3.4 Brand motif — the "Qube" pattern
- Isometric cube grid (a cube drawn as an open box — matches the delivery-box brand story) tiled as an outline pattern.
- Used at high density on the **splash** (white outlines fading to solid #16268D bottom) and at low density (20% opacity) on **auth/registration** backgrounds.
- This is Cartona's signature surface treatment: brand blue + cube texture = "warehouse/box" metaphor carried through every entry surface.

### 3.5 Illustration & imagery system
| Surface | Style | Files |
|---|---|---|
| Onboarding (first run) | Real photography of retail context (shelves, POS payment, delivery man at supermarket) | `onboarding1-3.png` |
| Returning-user interstitial | Dark brand blue + faded product-grid tiles behind centered logo | `returning-user-onboarding8.png` |
| Auth/registration | Flat vector illustration, blue/indigo figure + phone mockup + cube pattern bg | `registration-screen-background.png`, `account_created.png`, `have_account.png` |
| Permission screens | 3D-ish flat illustration (phone + truck + map pin) | `location_permission.png`, `notification-permission-screen-header.png` |
| Business type picker | Flat two-tone navy pictograms, one per vertical | `bakery, cafe, pharmacy, resturant, market, kiosk, retail, hospital, school, university, hotel, gym, factory, mosque, charity, conpany, cenima, playstation, wedding, garden, youth_center, warehouse, supplier, army_place, clean_shop, spice, roaster, bazzar` (26 verticals) |
| KYC | Photo placeholders for national ID front/back | `national_id_front/back_placeholder.jpg` |
| Empty states | Neutral illustration | `no_result.png` |
| Campaign skins | Seasonal: `eid_al_adha_banner_hero`, `world_cup_ball_texture_dark/navy`, ramadan app icons | — |

## 4. Screen inventory & user-flow logic (reconstructed)

Reconstruction basis: asset filenames + plugin fingerprint + manifest. Screen order below is the standard Cartona journey.

```
Splash (brand blue + cube pattern + logo)
  └─ Onboarding (3 photo slides, smooth_page_indicator dots)      [first run]
  └─ Returning-user interstitial (logo over product-grid bg)       [subsequent runs]
       └─ Auth gate
            ├─ Login (have_account)
            ├─ Registration (full-screen illustration bg + form)
            │    ├─ Phone → OTP (pinput + sms_autofill + countdown timer)
            │    ├─ Business identity: shop-type picker (26 pictograms)
            │    ├─ KYC: national ID capture (camera + compress, front/back)
            │    └─ Success: account_created + confetti
            └─ Permission ladder (explicit, illustrated, one-by-one)
                 ├─ Location permission preview → system dialog
                 └─ Notification permission preview → system dialog
       └─ Branch / address setup
            ├─ Map (Google Maps primary, OSM fallback) + marker pins
            └─ Branch details (street image, extra image upload)
       └─ Main app (B2B commerce core)
            ├─ Home / catalog — masonry product grid, infinite pagination,
            │   category tiles (all_products_category), campaign hero banners
            ├─ Product detail → cart (dotted_border price summary patterns)
            ├─ Checkout — incl. embedded webview payment paths
            ├─ Orders — timeline_list order tracking, FCM status notifications
            ├─ Support — Freshchat in-app chat
            └─ Profile / business settings, share_plus referral (OneLink)
```

**Design-logic takeaways (the "why" behind the screens):**

1. **Trust before trade.** Registration is a KYC funnel (phone → business identity → national ID → manual/verified approval), not a lightweight signup. The B2B credit/wholesale pricing model requires verified retailers; the success moment is celebrated (illustration + confetti) because dropping out mid-KYC is the funnel's main risk.
2. **Permission ladder with previews.** Both location and notification get dedicated *pre-permission* screens with explanatory illustrations — asking context-first to maximize grant rate (location is load-bearing for delivery addresses and fraud checks).
3. **Business-type selection is a first-class screen.** 26 verticals as visual pictogram tiles — this segments catalog/pricing per trade and doubles as a personalization commitment early in the journey.
4. **Fraud defense is a product surface.** Fake-GPS app enumeration (20+ packages), clone/parallel-space detection, root checks, Play Integrity — because COD-heavy B2B commerce is defrauded via location spoofing and multi-accounting. POL should treat this as a screen-adjacent requirement (silent checks + graceful blocks).
5. **Dual map providers.** Google Maps embedded with an OSM fallback — cost/licensing hedge; POL's vendor app does the same in spirit.
6. **Deep links as re-engagement.** Universal links (`cartona.com`) + AppsFlyer OneLink route users back into specific order/promo states (deeplinking to Flutter is disabled at the engine level; links handled in Dart via `app_links`).
7. **Campaign-capable home.** Seasonal icon variants (Ramadan) and hero banner assets in the base bundle indicate the home surface is remote-config driven (Firebase Remote Config) — banners, ordering, and skins change without releases.

## 5. Navigation & shell behavior

- Single-activity Flutter shell: `MainActivity extends FlutterActivity`, `singleTop`, `adjustResize`, hardware-accelerated; all routing inside Flutter (route names unknown without `libapp.so`).
- Bottom-tab shell is implied by the commerce model + `sliver_tools` custom-scroll surfaces; no native fragments exist to confirm tabs.
- Deep link entry points: `https://cartona.com/**` (autoVerify) and `https://cartona.onelink.me/8xkB/**`.
- Embedded web (`flutter_inappwebview`) used for payment/hosted content inside the app rather than external browser.

## 6. Operational / quality signals

- `pretty_dio_logger` compiled into release → verbose network logs ship to users (a flaw worth avoiding in POL).
- `usesCleartextTraffic=true` + custom `network_security_config` → some legacy HTTP endpoint is whitelisted.
- Crashlytics + PostHog + Segment + AppsFlyer + Firebase Analytics all active → heavy instrumentation culture; screen_view events likely standard.
- `flutter_native_splash` + `flutter_launcher_icons` tooling present (splash/icon generated from tokens).

## 7. Reusable patterns for POL (actionable)

Mapping to POL's Precision Commerce direction (`56_POL_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM`):

1. **Entry-surface motif rule** — Cartona owns the cube; POL should keep the *pattern* (a single recognizable geometric brand texture on splash/auth surfaces at 2 opacities: hero ~90%, form ~20%) but with POL's own motif.
2. **Photography on onboarding, illustration in-product.** Real retail photography sells the world; calm vector illustrations carry empty states, permissions, and success moments. Both systems in one bundle, clearly separated.
3. **Pre-permission screens** for location & notifications with value-statement illustration — copy the pattern, not the artwork.
4. **KYC as a celebrated milestone** — full-screen success state with motion (confetti-class) before entering the catalog.
5. **Vertical pictogram grid** for business-type onboarding — visual, tappable, single-select; scales to 20+ options without text overload (RTL/Pakistan-language equivalents for POL).
6. **OTP anatomy**: boxed PIN input + SMS autofill + visible resend countdown — all three packages Cartona uses map to a single UX standard POL should match.
7. **Order tracking as a timeline component** (`timeline_list`), not a status label.
8. **Remote-config-driven home** so banners/campaigns don't need releases.

## 8. File map (evidence locations)

```
cartona app/
├── cartona.apk                                  # base APK (42MB)
└── decompiled/
    ├── resources/AndroidManifest.xml            # identity, permissions, deep links, pairip
    ├── resources/res/values/{strings,colors,styles}.xml
    └── resources/assets/flutter_assets/
        ├── AssetManifest.json                   # full asset index
        ├── FontManifest.json                    # families list
        ├── NOTICES.Z                            # gzip; full Dart package inventory
        ├── assets/fonts/                        # SomarSans(4), Rubik(var), Cairo(var)
        └── assets/images/                       # all screens' art referenced above
```

## 9. Verification status

| Claim | Evidence | Confidence |
|---|---|---|
| Flutter app, single activity | Manifest + MainActivity.kt | Certain |
| Tech stack | NOTICES.Z package list | Certain |
| Brand colors #15268E / #FF951A | SVG fills + pixel sampling | Certain |
| Fonts | FontManifest + font files | Certain |
| Screen/flow reconstruction | Asset names + plugins | High (order inferred) |
| Widget-level design tokens, route names, exact layouts | **unavailable** — `libapp.so` not in base APK | — |

## 10. Next steps to complete the reverse-engineering

1. **Provide the full bundle**: the `.xapk`/`.apks` (or at least `split_config.arm64_v8a.apk`) so `libapp.so` is available → then Dart AOT analysis (blutter) can recover class names, routes, widget trees, and hard-coded strings (UI text in Arabic/English, API endpoints).
2. **Provide the screenshots** (user planned to send them) → map each screenshot to the reconstructed flow above and extract pixel-level tokens (spacing, radii, type scale) from real screens.
3. Optional: install the APK on the emulator (`android-emulator` plugin is ready) — note the base APK alone will not install/run without its ABI splits.
