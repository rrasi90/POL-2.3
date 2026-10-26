# User Journey Maps — Cartona v8.4.6 (static evidence; extends revision-2 J1-J7)

Confidence: [V] verified string/schema/manifest - [H] hypothesis - [U] unresolved. Arabic evidence from the 1,494-string UTF-16LE corpus.

## J1 — Onboarding & account activation (enriched)
Signup fields: full name, business name, business type, address, landmark (is_*_filled flags) [V] -> OTP SMS verify [V] -> manual approval step: "تم اعتماد حسابك من فريق كرتونة" + "هنتواصل معاك على رقمك المسجّل علشان نأكد الطلب" (approval then confirmation call) [V strings; flow H] -> /signup-celebration + account_created.png [V]. Guest mode /v3/auth/register/skip/ [V]. Blocked route /block + is_blocked [V]. Service-area gate /v3/public/available-area?lat_lng= [V].

## J2 — Browse & discover (enriched)
Category icons (bakery/cafe/bazzar) [V]; /categories, /category-products, /search, /suppliers [V]; supplier ranking endpoints (new/fast/sponsored/top-relevant) [V]; badges has_fast_delivery, has_free_delivery_offer, has_integration [V]; favorites [V]; offers copy (49 strings) + discount/MOV/MOP filters [V]; ramadan products/quiz + "مفاجأة العيد" [V].

## J3 — Cart, checkout & order lifecycle (enriched)
Local carts (cartona_v0016.sqlite; reorder + abandonment columns) [V]; server sync [V]; validate [V]; quantity label "الكمية:" [V]; 236 order strings [V]; lifecycle tokens pending->delivered (+cancelled/rejected/returned) [V]; reorder [V]; tracking with OSM map plugin + "تابع وصول طلبك معه" (follow your order with him) [V]; delivery domain 44 strings [V].

## J4 — Business account management
Branches: /branch-management + endpoints + 28 strings [V]; multi-address has_multiple_addresses [V]; sub-users /user-management [V route].

## J5 — Wallet, credit & payments (enriched)
Wallet route + 32 strings ("استخدم رصيدك في المحفظة") [V]; "رصيد فوري" [V]; Cartona Credit BNPL web-app postMessage contract [V]; legacy installment states (is_legacy_installment_activated/suspended, is_credit_exhausted) [V]; "إجمالي طلباتك مع كرتونة" + EGP amount "١,٠٠٠ ج" [V]; payment domain 47 strings; provider names not embedded [U].

## J6 — Engagement & support (enriched)
GMV targets: has_active_gmv_target + "يتم احتساب الطلب فقط لو تم خلال فترة الهدف، و بينزلك خلال 48 ساعة من تاريخ تسليم أخر طلبيه" (order counts within target window; credit within 48h of last delivery) [V strings; mechanics H]; cashback eid redemptions [V]; in-app stories/threads [V]; notifications [V]; Freshchat + WhatsApp [V].

## J7 — Integrity/anti-fraud (platform side)
Licensing, fake-GPS/cloner/developer-mode detection flags [V declarations]; enforcement behavior [U].

## Cross-app ecosystem [V]
Supplier app, delivery-driver app, mandoob app queried by manifest; is_cartona_*_app_installed flags drive UX branches.
