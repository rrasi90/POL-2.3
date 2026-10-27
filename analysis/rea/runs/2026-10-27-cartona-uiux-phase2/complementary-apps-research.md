# Complementary Apps Research — CP7

**Date:** 2026-10-27 · Sources: official Play Store listings fetched fresh today (register S6, S7 + driver listing S8). APK access status decided below. Extends (does not replace) `2026-10-27-cartona-remediation-deep-extraction/public-product-research.md`.

## Access status

| App | Package | APK obtainable legally? | Status |
|---|---|---|---|
| Cartona retail | `com.cartona` | **YES — local APK on disk** (v8.4.6, this run's analysis subject) | AVAILABLE |
| Cartona Suppliers | `com.cartona.suppliers` | Play listing exists but the app is business-gated (supplier onboarding required); no legal sideload channel; no local APK | **UNAVAILABLE** (BLOCKED_AUTH-class: listing public, app gated) |
| Cartona Xpress – Driver | `com.cartona.delivery_driver_app` | Driver onboarding required; no local APK | **UNAVAILABLE** |

No anonymous downloaders or modified packages used (mission §30). Evidence below is therefore listing-derived (MARKETING_CLAIM / PUBLICLY_DOCUMENTED), never runtime-verified.

## Cartona retail — refreshed facts (listing fetched 2026-10-27)

- 500K+ installs, 3.2★ (~2.18K reviews), updated 2026-10-18, developer Cartona Technologies (Cartona B.V.).
- Positioning: B2B marketplace — 2,000+ suppliers, 50,000+ products, price comparison.
- **Credit/BNPL ("بالآجل") with installment plans** — headline feature; consistent with the snapshot's wallet/BNPL literals found in CP6 (`/legacy/wallet/top-up`, `/installment2`, `/pay/authorize/`, `/tabs/payment-gateways`).
- **Group ordering to bypass minimum-order requirements** — listing-described business mechanic (no runtime evidence).
- Offers/discounts/cashback; reviews mention delivery-tracking gap — matches prior run's finding that POD mechanics are in the driver app, not retail.

## Cartona Suppliers — refreshed facts

- 10K+ installs, updated 2026-07-14.
- Listing-described capabilities: order management, product catalog creation/coding, price & inventory editing, special offers, reports/financial account (receivables, account statements).
- Maps to POL بنکدار (`ir.pol.vendor`) — POL's vendor app already covers orders/inventory/finance (verified in repo exploration); the notable Cartona-side pattern POL lacks is **in-app special-offer creation** and **account-statement reporting**.

## Cartona Xpress – Driver — refreshed facts

- 500+ downloads, updated 2026-07-22, category Productivity.
- Listing-described loop: shipment assignments between wholesalers and retailers → organized orders with **optimal routes** → **proof-of-delivery confirmation system** → earnings tracking.
- Consistent with prior run: POD mechanics undisclosed; this app is the missing leg of Cartona's 3-sided model. POL has **no driver role/app** (verified) — adopt decisions here are REQUIRES_PRODUCT_DECISION per the prior handoff (D-01 gate), unchanged by this run.

## Confidence labels used in the capability matrix

- `LISTING_CLAIM` — official store text (marketing; not runtime-verified)
- `STATIC_VERIFIED` — verbatim in analyzed APK payload (retail app only)
- `UNAVAILABLE` — no artifact access
