# Executive Summary — Cartona APK Deep Analysis → POL Gap Audit (Revision 2)

**Date**: 2026-10-26 · **APK**: `C:/Star/pol-2.4/cartona.apk` · **SHA-256**: `e4a0f4d1…df808c`
**Toolchain**: REA v6.7.0 (MCP + CLI), JADX headless 0.7.1 (pinned JAR), apktool decode (pre-existing), Python string mining

## Headline correction

The first audit concluded Cartona was a native Android app whose only recoverable entry point was a bare `MainActivity.<init>()`. **That conclusion was wrong.** Deep analysis proves Cartona v8.4.6 is a **Flutter application**: the base APK carries `assets/flutter_assets/` (106 assets) while the ABI split (`config.armeabi_v7a.apk`) carries `libapp.so` — a 10.9 MB Dart AOT snapshot (kind-3 FullAOT layout, snapshot hash `97ff04a7…`) — and `libflutter.so` (engine build-id `deaf7120…`, clang 18.0.1 / r522817). The bare `MainActivity` is the standard Flutter launcher stub. The real product lives in the Dart snapshot, and its strings were recoverable.

## What the Dart snapshot revealed

- **43 REST endpoints** (auth, supplier/product search, retail operations) plus 24 named Flutter routes (`/orders`, `/order-reorder`, `/order-tracking`, `/wallet`, `/branch-management`, …)
- **OTP SMS authentication** with guest mode (`/v3/auth/register/skip/`)
- **Cartona Credit** — an embedded BNPL web app wired via postMessage events (`cartona:credit:plans:ready`, `cartona:credit:pay:success`)
- **Abandoned-cart + reorder** engineered into local SQLite (`cartona_v0016.sqlite`, carts table with `marked_as_abandoned_at`, `origin_order_id`, `created_via_reorder`)
- **Cashback campaigns** (Eid al-Adha / Eid al-Fetr redemption endpoints), GMV targets, in-app stories, order support tickets
- **Anti-fraud posture**: manifest queries 12+ fake-GPS apps and sibling apps (`com.cartona.suppliers`, `com.cartona.delivery_driver_app`, `com.cartona.mandoob`), PairIP license enforcement, `CHECK_LICENSE`

## Manifest facts (corrected)

minSdk **24** (v1 said 26), targetSdk **36** (v1 said 33), compileSdk 36, application class `com.pairip.application.Application`, App Links `https://cartona.com` + AppsFlyer OneLink, cleartext traffic allowed with a network-security-config override.

## POL comparison

POL (`mvp/apps/mobile`, branch `ui/visual-qa-screen-completion-20261025`, commit `89d07617`) is **Expo SDK 57 / React Native 0.86.3 / React 19** with a dual-variant build (`ir.pol.market` retailer / `ir.pol.vendor` vendor) and Persian-first i18n. POL already mirrors Cartona's two-sided marketplace concept but has 9 screens vs Cartona's evidenced ~24-route surface. The gap matrix in this revision replaces the v1 four-row matrix with capability-level rows backed by exact Cartona evidence and exact POL file paths.

## Highest-confidence findings

1. Cartona = Flutter AOT; native host is a stub (evidence: libapp.so ELF symbols, flutter_assets).
2. Product domain = B2B retail ordering from multiple suppliers, with cashback, credit/BNPL, reorder, and support tickets (evidence: 43 endpoint strings + sqlite schema).
3. Cart persistence and cart-server sync exist (`/v3/retail/data/storage/carts` + local carts table).
4. Order lifecycle ≥ {pending, confirmed, processing, shipped, delivered, cancelled, rejected, returned} (evidence: status tokens in snapshot).
5. Deep links and cross-app ecosystem (supplier app, driver app, mandoob) are first-class (evidence: App Links intent-filter, package queries).

Phase classification: see `limitations-and-unknowns.md` § Phases. All evidence artifacts live under `analysis-v2/`.
