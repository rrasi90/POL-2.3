# User Journey Inventory — Cartona v8.4.6 (Revision 2)

Legend: **[V]** verified fact (literal artifact evidence) · **[H]** hypothesis (consistent, unproven) · **[U]** unresolved question.

## J1 — Onboarding & authentication
- Entry: `com.cartona.MainActivity` → Flutter engine → `/landing` route **[V]**
- OTP SMS auth: `/v3/auth/otp/request/sms`, `/v3/auth/otp/verify`, `/v3/auth/register`, token refresh `/v3/auth/access-token` **[V]**
- Guest/skip mode: `/v3/auth/register/skip/` **[V]** — users can browse before registering **[H]**
- Post-signup: `/signup-celebration` route + `account_created.png` asset **[V]**
- Google Sign-In available (SignInHubActivity) **[V]** — used for auth or drive-in **[U]**
- Service-area gate: `/v3/public/available-area?lat_lng=` with geolocator location **[V]** — blocking vs advisory **[U]**

## J2 — Browse & discover
- Routes: `/categories`, `/category-products`, `/search`, `/suppliers`, `/ramadan-products` **[V]**
- Category iconography (bakery, cafe, bazzar…) in flutter_assets **[V]**
- Search API family: products/all, products/bids, suppliers/{all,new,fast,sponsored,top-relevant,fav}, discount filters (max, mov, price, mop), ads, places **[V]**
- Supplier favorites: `/search/v2/suppliers/fav` + `/v3/retail/favorite/suppliers/` **[V]**
- Seasonal: ramadan products/quiz, eid cashback campaigns **[V]**

## J3 — Cart & ordering
- Cart stored locally in `cartona_v0016.sqlite` (carts table) **[V]**; server-side cart sync `/v3/retail/data/storage/carts` **[V]**
- Validation before checkout: `/v3/retail/cart/validate` **[V]**
- Abandoned-cart tracking column `marked_as_abandoned_at` **[V]** — recovery campaign behavior **[H]**
- Reorder: `/order-reorder` route + `origin_order_id`, `created_via_reorder`, `reorder_products_count`, `cart_value_before_reorder` columns **[V]**
- Order history & detail: `/orders` route **[V]**; order-detail screens **[H]** (route-level evidence only)
- Order lifecycle: pending/confirmed/processing/shipped/delivered/cancelled/rejected/returned tokens **[V]**
- Order tracking: `/order-tracking` route; OSM map plugin bundled (`flutter_osm_plugin`) **[V]** — live driver map **[H]**
- Order problems: `/v3/retail/order-support-tickets` + ticket-types (returns/disputes channel) **[V]**

## J4 — Branch & user management (B2B controls)
- `/branch-management` + `/v3/retail/branches{,/change}`: multi-branch retailer accounts **[V]**
- `/user-management` route: sub-users/roles for business accounts **[V]** — role model details **[U]**

## J5 — Wallet, credit & payments
- `/wallet` route **[V]**; wallet API endpoints not found in static strings **[U]** (likely server-driven naming)
- **Cartona Credit BNPL**: partner session endpoints + consent page + embedded web app events (plans ready/selected/resize/unavailable, pay success) **[V]**
- Legacy installment plans: `/v3/retail/legacy/installment/plans` **[V]**
- Payment provider names (valu/fawry/instapay/…): **not found** — recorded unknown **[U]**

## J6 — Notifications & engagement
- FCM push (FlutterFirebaseMessaging) + `/v3/fcm/token` **[V]**
- In-app notifications: `/v3/retail/notifications{,/read}` + `/notifications` route **[V]**
- Campaigns: in-app stories, threads (`/v3/campaigns/communications/…`), `/communication_campaign` route **[V]**
- GMV targets: `/v3/retail/gmv-targets` **[V]** — retailer incentive program **[H]**
- WhatsApp contact: `wa.me/` links **[V]**
- Support: Freshchat SDK (chat, FAQ, bot) **[V]**

## J7 — Anti-fraud & integrity (platform-enforced)
- Fake-GPS detection via manifest queries + `libtoolChecker.so` **[V]** — exact enforcement behavior **[U]**
- PairIP license check activity + `CHECK_LICENSE` **[V]**
- Deep links: App Links cartona.com; AppsFlyer OneLink deferred deep linking **[V]**

## Cross-app ecosystem [V]
Cartona operates a family: `com.cartona.suppliers` (supplier app), `com.cartona.delivery_driver_app`, `com.cartona.mandoob` (delivery agent) — the retailer app queries them. This matches POL's retailer/vendor two-variant model.
