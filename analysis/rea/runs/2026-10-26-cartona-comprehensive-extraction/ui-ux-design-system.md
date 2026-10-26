# UI/UX Design System — Cartona (static evidence only)

**Runtime status: BLOCKED.** Install failed with INSTALL_FAILED_NO_MATCHING_ABIS (armeabi-v7a-only libs; Google APIs x86_64 image lacks ARM translation). Nothing below derives from a running app. Per-screen catalog: ui-screen-catalog.csv.

## Typography (VERIFIED from flutter_assets)
Cairo-VariableFont (slnt,wght), Rubik (regular+italic variable), SomarSans (Regular/Medium/SemiBold/Bold) — Arabic-first type system. POL uses Vazirmatn — equivalent choice; no change needed for parity.

## Iconography (VERIFIED)
Custom category icons: bakery, cafe, bazzar, army_place, all_products_category, branch street/extra photos, cartona brand logos (vertical + standard), app-icon + Ramadan variants (seasonal theming). Bundled libraries: Font Awesome, Ionicons, Lucide, Cupertino.

## Color/spacing (NOT AVAILABLE statically)
Colors/spacing live in compiled Dart; requires runtime capture (see prerequisites).

## Localization architecture (VERIFIED)
Flutter gen-l10n; 1,494 Arabic UI strings in snapshot (UTF-16LE); ACTION_LOCALE_CHANGED_BY_WEBVIEW bridge implies locale switching from embedded web surfaces (credit module). RTL: layoutDirection configChanges + values-ldrtl resources; Arabic primary.

## Interaction/behavior evidence (VERIFIED strings; behavior HYPOTHESIS)
- Multi-step business signup (field-state flags).
- Manual account-approval step with confirmation phone call (approval copy).
- Supplier badge-driven cards (fast delivery / free-delivery offer / integration).
- GMV-target window campaigns (48h credit wording).
- Image-load error/retry state string recovered.

## Runtime capture prerequisites (future authorized session)
1. armeabi-v7a-capable device OR x86_64 Google Play image (API 30+) with ARM translation (current Google APIs image does not qualify).
2. Google Play services signed in (PairIP license check + GMS).
3. Valid phone able to receive SMS OTP — no bypass permitted; authenticated screens otherwise UNOBSERVED.
4. Location inside a Cartona-served area (service-area gate); no mock locations.
5. Owner-authorized test account; no real orders or charges.
