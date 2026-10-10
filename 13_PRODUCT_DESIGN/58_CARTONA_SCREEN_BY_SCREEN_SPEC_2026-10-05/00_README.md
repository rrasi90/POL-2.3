# Cartona Screen-by-Screen Spec — README

**Document ID:** `POL-DESIGN-CARTONA-SPEC-001`
**Version:** `1.0.0`
**Date:** 2026-10-05
**Status:** REFERENCE — competitive UX recon for building an Iran-market equivalent inside POL
**Companion:** `57_CARTONA_APP_REVERSE_ENGINEERING_DESIGN_LOGIC_2026-10-05.md` (stack & design system)

---

## What changed since doc 57

The base APK alone could not run (missing `libapp.so`). Since then we obtained the complete bundle (XAPK from APKPure, base + `config.armeabi_v7a.apk` + `config.en` + `config.mdpi`) and extracted:

1. **`libapp.so`** (Dart AOT snapshot, 10.9MB) → **248 analytics events** (`newapp_*`) that enumerate every screen, flow branch and micro-interaction in the app; **161 feature flags**; **1,653 Arabic UI strings**; Dart/Flutter 3.9.0.
2. **Official Google Play screenshots** (5, high-res) — straight-on views of home, suppliers list, supplier card, credit dashboard, orders + success sheet.
3. **Three official Cartona YouTube tutorials** → 218 frames → **114 distinct frames** of the real UI in action (suppliers flow, product page, cart, checkout, wallet, order tracking, search, registration).

## The one thing we could not do — and why

Live emulator screenshots of v8.4.6 are **impossible on x86_64 emulators**: the Play bundle ships **armeabi-v7a (32-bit ARM) native libraries only**, and the Android emulator's ARM translator (`libndk_translation`) handles arm64 only. `INSTALL_FAILED_NO_MATCHING_ABIS`. Old versions with multi-ABI builds exist but are cookie-gated on mirrors. Coverage of the funnel is therefore reconstructed from snapshot strings + official imagery instead of a live run.

## Evidence map (all under `cartona app/`)

| Evidence | Path |
|---|---|
| Decompiled base APK (jadx) | `cartona app/decompiled/` |
| Full XAPK + splits | `cartona app/xapk_extracted/` |
| Native libs incl. `libapp.so`, `libflutter.so` | `cartona app/native/lib/armeabi-v7a/` |
| Play Store screenshots (high-res) | `cartona app/evidence/playstore/ps1..ps5.jpg` |
| Tutorial videos (3 official) | `cartona app/evidence/videos/` |
| All video frames | `cartona app/evidence/frames/` (218) |
| Deduplicated frames | `cartona app/evidence/distinct/` (114) |
| Contact sheets (review grids) | `cartona app/evidence/sheet_01..06.jpg` |
| Raw extracted data | `data/` in this folder |

## Document index

| File | Covers |
|---|---|
| `01_MASTER_FLOW_MAP.md` | Complete navigation graph + screen inventory table |
| `02_AUTH_ONBOARDING.md` | Splash, landing, onboarding, login+OTP, permission pre-screens, forced update |
| `03_REGISTRATION_KYC.md` | Full registration funnel incl. shop photos, map, review & activation |
| `04_HOME_DISCOVERY.md` | Home sections, stories, announcements, search, categories |
| `05_SUPPLIERS_PRODUCT.md` | Suppliers list, supplier page, product card/detail, price sheet |
| `06_CART_CHECKOUT.md` | Cart mechanics, conflicts, checkout, payment/wallet, success |
| `07_ORDERS_SUPPORT.md` | Orders tabs, tracking, reorder, support tickets (OST), retailer asks |
| `08_MONEY_GROWTH.md` | Wallet, installments (BNPL), rewards/goals, quizzes, campaigns |
| `09_UI_STRINGS_DICTIONARY.md` | Curated real UI texts (AR) per area |
| `10_FLAGS_AND_CONFIG.md` | All 161 remote-config flags, interpreted |

## How to read each screen doc

Every screen is documented with:

- **هدف** — what the screen is for in the business flow
- **آناتومی (بالا→پایین)** — region-by-region layout (from screenshots/frames)
- **کامپوننت‌ها و حالت‌ها** — components + loading/empty/error states
- **اکشن‌ها و رخدادها** — every interaction, matched to its `newapp_*` analytics event (proof it exists)
- **متن‌های واقعی UI** — actual strings from the binary
- **شواهد** — file references

## Rule for POL usage (clean-room)

Use this as a **flow & UX logic reference**. Do not copy Cartona's Arabic copy, artwork, cube motif, or logo. Build the Iranian equivalent with POL's own brand (Precision Commerce tokens) — same funnel *shapes*, original skin.
