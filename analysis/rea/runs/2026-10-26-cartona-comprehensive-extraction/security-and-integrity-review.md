# Security, Privacy and Integrity Review — Cartona v8.4.6 (static, non-invasive)

Confidence tags: VERIFIED (decoded artifact) / HYPOTHESIS. No exploitation, no bypass, no production calls.

## Network security (VERIFIED)
- Manifest usesCleartextTraffic="true" IS OVERRIDDEN by network_security_config.xml: cleartext permitted only for 10.0.2.2 (emulator loopback). Production = HTTPS-enforced. Corrects the naive manifest reading.
- Firebase RTDB endpoint observed (cartona-69c1a.firebaseio.com); TLS assumed by SDK defaults (HYPOTHESIS).

## Embedded secrets (VERIFIED presence; values withheld)
- Google API key, AIzaSy... pattern, embedded in the Dart snapshot. Value withheld from all committed artifacts (no live credentials in Git). Risk: client-embedded keys are extractable; mitigation depends on Google-side API restrictions (UNVERIFIED).
- AppsFlyer APP_ID/DEV_KEY identifiers present (values withheld). Dev keys are client-visible by design.

## Components and export surface (VERIFIED)
- 5 exported components, all framework-required: MainActivity (launcher), GMS RevocationBoundService, FCM receivers x2, ProfileInstallReceiver. Minimal app-specific export surface.
- Custom permission com.cartona.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION with signature protectionLevel — good practice for dynamic receivers.

## Data-extraction and backup (VERIFIED)
- allowBackup=true; dataExtractionRules + fullBackupContent both exclude AppsFlyer prefs (appsflyer-data, appsflyer-purchase-data) and afpurchases.db from cloud-backup and device-transfer.
- Cart SQLite (cartona_v0016.sqlite) NOT excluded from backup — contains cart/reorder metadata, not credentials (sensitivity HYPOTHESIS; schema VERIFIED).

## Integrity and anti-fraud signals (VERIFIED declarations; enforcement UNVERIFIED)
- PairIP wrapper: application class com.pairip.application.Application + LicenseActivity + CHECK_LICENSE.
- Fake-location detection: manifest queries for 12+ fake-GPS packages; snapshot flags is_mocked, is_any_fake_gps_app_installed.
- App-cloner detection: is_any_app_cloner_installed; cross-app flags: is_cartona_suppliers_app_installed, is_cartona_mandoob_app_installed, is_cartona_delivery_driver_app_installed; Google AppSheet queries present.
- Developer-mode detection: is_developer_mode_enabled; libtoolChecker.so present.
- Declared signals are not proof of enforcement behavior — runtime response UNVERIFIED (bypass testing out of scope).

## Tracking / privacy SDK inventory (VERIFIED namespaces)
AppsFlyer (attribution), PostHog (us.i.posthog.com), Segment (event names), Firebase (Analytics/Messaging/Sessions), GMS measurement/ads (AD_ID), Freshchat (support), Picasso (Freshchat dependency).

## Deep links (VERIFIED)
App Links https://cartona.com (autoVerify) + AppsFlyer OneLink https://cartona.onelink.me/8xkB. assetlinks.json verification status UNVERIFIED (server not contacted).

## Independent requirements for POL
1. Never embed live API keys in client bundles; use restricted keys + server proxying.
2. Mirror positive practices: signature-protected dynamic-receiver permission; backup exclusions for attribution data; cleartext restricted to dev hosts only.
3. Anti-fraud hardening (licensing + spoof detection + cloner detection + integrity SDK) as a later POL phase — design independently.
