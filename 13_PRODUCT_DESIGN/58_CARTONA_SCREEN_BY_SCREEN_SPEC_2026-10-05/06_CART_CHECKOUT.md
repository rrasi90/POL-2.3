# 06 — Cart & Checkout

The most instrumented flow in the app (60+ events). Evidence: frame 054 (conflict dialog), frame 060 (cart), ps5 (success sheet), strings.

---

## 6.1 Cart (عربة التسوق) — frame 060

Top→bottom:
1. Header: back + "عربة التسوق"
2. **Items grouped per supplier** (multi-supplier cart): each item = thumbnail, name, per-unit price + pack info, quantity stepper, remove icon
3. **Wallet toggle row:** "✅ استخدم رصيد المحفظة" (checkbox style)
4. Cashback banner slot (`cart_cashback_banner_viewed`, "كاش باك" strings)
5. **Money breakdown block:**
   - إجمالي: 7,726 ج.م
   - رصيد المحفظة المستخدم: 398 ج.م
   - المطلوب كاش بعد الرصيد: 6,094 ج.م
   - كاش باك متوقع: 46 ج.م
6. Sticky bottom bar: blue CTA "تأكيد الطلبية" (إتمام الطلبية) with total

### Cart intelligence (events)
- Lifecycle: `cart_initiated`, `cart_item_added`, `cart_item_quantity_updated`, `cart_item_removed`, `cart_first_supplier_added`
- **Min-requirements engine:** `cart_requirements_status_changed` — live validation per supplier ("راجع متطلبات الحد الأدنى")
- **Auto-adjustment:** quantities auto-tuned to meet minimums — `cart_auto_adjustment_applied` (silent) / `cart_auto_adjustment_clicked` (user accepts suggestion); copy: "والكميات هتتزبط لوحدها لو في فرق عن الحد الأدنى أو الأقصى"
- **Price change handling:** supplier changed a price while in cart → `cart_price_change_seen` + `cart_price_change_action` (accept new price / remove)
- **Unavailable items:** `cart_unavailable_item_viewed` + `cart_unavailable_item_removed2`
- **Unit conflict dialog:** same product from two suppliers with different units → "مبياخدش نفس المنتج بوحدتين مختلفين في الطلب الواحد. لازم تختار وحدة واحدة بس" — `same_product_unit_conflict_viewed/replace_clicked/dismissed` (frame 054 shows "بتأكيد عرض 2 من مختلفين" dialog)
- **Abandoned cart:** after `ABANDONED_CART_TIMEOUT_DURATION_HOURS` → `cart_abandoned` (recovery notifications); carts sync across devices (`CARTS_SYNC_INTERVAL_SECONDS`)

## 6.2 Checkout (إتمام الطلبية)

Sections (each independently collapsed/expandable — `checkout_products_details_expanded/collapsed`):
1. **Address / branch:** "اختر الفرع اللي عايز تطلب عليه" (`checkout_address_viewed`)
2. **Preferred delivery date block** (both delivery modes; flags `DELIVERY_VIA_CARTONA_ENABLE_PREFERRED_DELIVERY_DATE`, `DELIVERY_VIA_SUPPLIER_ENABLE_PREFERRED_DELIVERY_DATE2`): date picker sheet — `checkout_preferred_date_block_viewed/opened/selected`
3. **Payment method block** (`checkout_payment_block_viewed2`): options — كاش (cash), محفظة كرتونة (wallet, toggle + editable amount `checkout_wallet_toggled`/`checkout_wallet_amount_edited2`), تفسيط/دفعات (installments), عند الاستلام; per-supplier acceptance from the payment chips
4. **Notes:** "أي طلبيات خاصة أو ملاحظات للمورد..." (`checkout_notes_submitted`)
5. **Summary:** totals, wallet usage, cashback (`checkout_summary_viewed`)
6. **Confirm CTA:** "إرسال الطلب" → `checkout_confirm_order_clicked` → `checkout_success`
7. Block state: `checkout_blocked` (e.g., supplier unavailable: "آسفين، المورد غير متاح حالياً. ما تقدرش تكمل الطلب دلوقتي. ممكن تطلب من مورد تاني")

## 6.3 Success sheet — ps5

- Bottom sheet: green check circle + "تم طلب الأوردر" + "ادهب إلى طلباتي لمتابعة حالة الطلبات"
- Two buttons: **"طلباتي"** (filled blue) + **"الرئيسية"** (outlined)
- Confetti-class celebration

## 6.4 Design logic for POL

1. **The cart is a negotiation surface**, not a list: auto-adjustment, price-change acceptance, unavailable-item cleanup, min-requirements progress — all inline and reversible.
2. **Wallet is a first-class payment method** with per-order partial usage (toggle + editable amount + "after balance" cash line) — Iranian equivalent: اعتبار/کیف پول تامین‌کننده.
3. **Per-supplier payment acceptance** — a matrix (supplier × method) resolved at checkout.
4. **Preferred delivery date** is a config-gated block per delivery mode — POL should copy the config-gating.
5. Always show the **money math explicitly** (total / wallet used / cash due / expected cashback) — trust in COD-heavy markets depends on it.
