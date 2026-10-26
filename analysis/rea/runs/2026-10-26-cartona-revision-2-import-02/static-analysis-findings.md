# Static Analysis Findings — Cartona v8.4.6 (Revision 2)

## 1. Package identity and integrity

| Fact | Value | Source |
|---|---|---|
| SHA-256 | `e4a0f4d1a3a607ad4e06e73fee70bf296c14205696b1cdc20892b5e893df808c` | `sha256sum` (reconfirmed) |
| Format | XAPK base APK (App Bundle base split) | `xapk_extracted/manifest.json` |
| Package / label | `com.cartona` / «كرتونة» | manifest |
| Version | 8.4.6 (code 70000083) | manifest |
| minSdk / targetSdk / compileSdk | **24 / 36 / 36** | decoded `AndroidManifest.xml` |
| Application class | `com.pairip.application.Application` | decoded manifest |
| Cleartext | `usesCleartextTraffic=true` + `network_security_config.xml` | decoded manifest |

Split APKs (XAPK): `config.armeabi_v7a` (sha256 `d232c761…`, contains all native libs), `config.en`, `config.mdpi`.

## 2. Architecture determination (evidence, not guesswork)

| Check | Result | Evidence |
|---|---|---|
| Flutter | **YES** | `assets/flutter_assets/` (AssetManifest, FontManifest, NOTICES.Z) in base; `libapp.so` + `libflutter.so` in ABI split; `identify_flutter_build` on split returns `flutter_detected=true` (evidence `ev_a197cc6a…`) |
| React Native | No | no `index.android.bundle`, no RN asset layout |
| WebView shell | No | no Cordova/Ionic layout; in-app-webview is a plugin, not the host |
| Dart snapshot | kind 3 FullAOT (Dart 2.14-era) | `inspect_dart_aot` summary (evidence `ev_fff3465f…`), snapshot hash `97ff04a728735e6b6b098bdf983faaba` |
| Engine | build-id `deaf7120f4bf65f07ea2c5505bcf74436d4efd1e`, clang 18.0.1 (r522817), no labeled Dart version (normal for release) | ELF PT_NOTE |
| Kotlin on host side | Yes | `DebugProbesKt.bin` present (coroutines) |
| Integrity/licensing | PairIP + `CHECK_LICENSE` | application class + permission |

`identify_flutter_build` on the **base** APK alone returns `flutter_detected=false` (evidence `ev_8bdc2bfe…`) because AOT payloads live in ABI splits — a documented App Bundle behavior, and the reason v1's inspection under-detected the framework.

## 3. Native host components (decoded manifest)

- 1 app activity: `com.cartona.MainActivity` (Flutter launcher, `singleTop`, `taskAffinity=""`, locale/RTL configChanges, deeplinking meta-data)
- App Links: `https://cartona.com`; OneLink: `https://cartona.onelink.me/8xkB`
- Vendor activities: flutter_inappwebview (5), Freshchat (12 incl. FAQ/bot), Google Sign-In hub, Play Core dialog, PairIP license
- Services: Firebase Messaging (+background), Geolocator, Freshchat, CameraX metadata, GMS measurement, Firebase sessions, Datatransport
- Providers: FreshchatFileProvider, in-appwebview fileprovider, share_plus, image_picker, FirebaseInit, androidx-startup, Picasso
- `<queries>`: sibling Cartona apps (`suppliers`, `delivery_driver_app`, `mandoob`), MaxAB, Fawry B2B, **12+ fake-GPS apps** (spoofing detection)

## 4. Dart snapshot string mining (the real product surface)

Method: byte-level printable-run extraction from extracted `libapp.so` (15,407 runs ≥6 chars) → `analysis-v2/extracted/libapp_strings.txt`. Arabic-pattern runs: **0** (UI translations not embedded in snapshot).

Findings (full lists in `audit-evidence.json`):

- **43 REST endpoint strings** — auth (5), search (18), retail (18), other (7); base URL behind `SERVER_BASE_URL` constant, value not resolved statically
- **24 named routes** — landing, categories, category-products, search, suppliers, orders, order-reorder, order-tracking, wallet, profile, settings, user-management, branch-management, notifications, block/unblock, upload-images, privacy-policy, terms-conditions, ramadan-products, ramadan-quiz, communication_campaign, signup-celebration
- **Local SQLite** `cartona_v0016.sqlite`: `carts` table with reorder/abandonment columns; `search_summarized_product_history_v001`
- **Order lifecycle tokens**: pending, confirmed, processing, shipped, delivered, cancelled, rejected, returned (refunded also present)
- **Cartona Credit (BNPL)**: partner endpoints, consent page, 5 postMessage events, `CARTONA_FINANCE_WEB_APP_BASE_URL`
- **Backends**: Firebase RTDB `cartona-69c1a.firebaseio.com`, PostHog `us.i.posthog.com`, Huawei AppGallery entry, `wa.me/` WhatsApp links
- **Payment provider names**: none found in snapshot (likely server-driven) — recorded as unknown, not absence

## 5. Class inventory (base APK, 12,338 classes)

Top-level `com.cartona` classes: `MainActivity`, `FreshchatFileProvider`, `R` — consistent with a Flutter host. Third-party namespaces observed in decompiled sources: androidx, kotlin(x), okhttp3, retrofit2, io.flutter(+plugins), dev.flutter(+community), com.{appsflyer, baseflow, dexterous, fluttercandies, freshchat, getkeepsafe, google, pichillilorenzo, posthog, scottyab, segment, squareup, tekartik, pairip, …}. Application logic is in Dart (not Java), so Java decompilation yields no product behavior — the correct analysis surface was the Dart snapshot strings, which is what this revision used.
