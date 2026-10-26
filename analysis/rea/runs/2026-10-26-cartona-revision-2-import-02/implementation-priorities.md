# Implementation Priorities — POL MVP alignment (Revision 2)

Context: POL mobile (`mvp/apps/mobile`) is Expo SDK 57 / RN 0.86.3 with dual variants (`ir.pol.market` retailer, `ir.pol.vendor` vendor). **Do not** create a new MainActivity or change SDK levels — Expo generates the native entry point via prebuild, already present (`android/`). Priorities below assume retailer app first (mirrors Cartona's retail surface), then vendor flows.

## P0 — Foundation (blocking)
1. **Cart persistence + server sync** (J3a): replace mock cart in `src/utils`/`src/mock` with a persistent store (AsyncStorage or expo-sqlite) and a `/carts` sync endpoint. Cartona proves both local SQLite and server-side cart storage are table-stakes for B2B ordering.
2. **Order lifecycle statuses** (J3e): render the 8-state stepper in `OrderDetailMobileScreen.tsx`; align api-client types with the same enum.
3. **Push notifications** (J6a): add `expo-notifications`; register tokens; order-status pushes.

## P1 — Revenue-critical retailer flows
4. **One-tap reorder** (J3d): reorder action on past orders; Cartona engineered this into its DB schema (`origin_order_id`, `created_via_reorder`) — treat as core, not garnish.
5. **Multi-supplier catalogue + search** (J2a, J2b): supplier list/detail screens and a search screen with MOV/discount filters.
6. **Cart validation before checkout** (J3b): server-side validate call with per-line errors.
7. **Supplier favorites** (J2c): small scope, high retention value.

## P2 — B2B account depth
8. **Multi-branch accounts** (J4a): branch switcher; scope orders to branch.
9. **Guest browsing** (J1b): deferred registration; preserve guest cart.
10. **Order support tickets** (J3g): connect existing `SupportMobileScreen` to order-scoped tickets.
11. **Service-area gate** (J1c): location capture + availability verdict at signup.

## P3 — Strategic
12. **BNPL/Credit** (J5b): partner integration via WebView + postMessage bridge (independent design; Cartona's pattern is reference only).
13. **Wallet** (J5a), **In-app stories** (J6c), **GMV targets** (J6d), **Sub-users** (J4b).
14. **Deep links** (J7b) and **Play Integrity** (J7c) before scaling marketing spend.

## Explicit non-goals from Cartona
- Do not copy AppsFlyer/PostHog/Freshchat vendor choices blindly — evaluate equivalents for the Iranian market (no Google Play services guarantee); Cartona itself ships Huawei AppGallery support for exactly this reason.
- Do not replicate `usesCleartextTraffic=true` — POL should keep TLS-only unless a specific legacy host requires it via network-security-config.
