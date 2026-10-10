# 07 — Orders, Tracking, Reorder & Support

Evidence: ps5 (orders tabs + success), frame 059/062 (tracking), events `reorder_*`, `ost_*`, strings.

---

## 7.1 Orders (طلباتي) — ps5

1. Header: hamburger + "طلباتي"
2. **Tabs:** `الطلبات الحالية` (current, active) · `طلبات تم تأكيدها` (confirmed) · `الطلبات السابقة` (past)
3. **Order card:**
   - top strip: "متابعة الطلبية 18/01/2024 | تاريخ الطلبية: 18/01/2024" (order date + delivery/tracking date)
   - supplier logo + name (كرتونة)
   - "إجمالي الطلبية: 408 ج.م" + "عدد المنتجات: 3 منتجات"
   - status: "الطلبية قيد المراجعه" (under review)
   - buttons: **"تفاصيل الطلبية"** (filled) + **"تعديل الطلب"** (outlined — editable while in review!)
4. Freshchat entry points on order surfaces (flags `SHOW_FRESHCHAT_ON_ORDER_LIST_CARD`, `SHOW_FRESHCHAT_ON_ORDER_TRACKING_APP_BAR`) — support is embedded *in the order context*

## 7.2 Order tracking (متابعة الطلبية)

- `timeline_list` component — vertical timeline of statuses
- Status vocabulary (from `OrderStatusType` + strings): قيد المراجعة → تم التأكيد → تم التجهيز → تم الشحن → بعد استلام الطلب (delivered) / ملغي
- Complaint window rule (string): orders older than N days — "فمش هنقدر نسجّل عليها شكوى أو طلب جديد" — **complaint eligibility window** drives the OST flow
- Support chat accessible from tracking app bar

## 7.3 Reorder (إعادة الطلب)

- Entry: CTA on past orders (`reorder_cta_clicked`) + from order card
- Flow: `OrderReorderScreen` → confirmation sheet ("إعادة طلب من طلب مكتمل/ملغي") → per-product selection toggles (`reorder_product_selection_toggled`) → results view → **supplier re-selection** (`reorder_supplier_selected`) — because the original supplier may not have the same availability/minimums
- Labels: "إعادة الطلب"، "إعادة طلب من …"، "إجراءات الطلب"

## 7.4 Order Support Ticket — OST wizard (شكوى/مشكلة في الطلبية)

The most complete support flow (12 events):
1. Sheet opens from order (`ost_sheet_viewed`)
2. **Type selection** (`ost_type_selected`; classes `OrderSupportTicketType/RequirementItemType`)
3. **Step 1:** issue details + Next (`ost_step1_next_clicked`)
4. **Step 2:** photo evidence upload (`ost_step2_viewed`, `ost_photo_added`)
5. Submit (`ost_submit_clicked`) → `ost_submitted2` / `ost_failed`
6. Guard rails: cooldown between tickets (`ost_cooldown_shown`), expiry window (`ost_expired_window_shown` — the complaint-window rule), duplicate prevention (`ost_already_submitted2`), success dismiss (`ost_success_dismissed2`)

## 7.5 Retailer asks (اطلب منتج مش موجود)

- Opens from: search no-results (`retailer_asks_shortcut_from_no_results`) or a banner
- Sheet: free-text request, up to 5 suggestions per order ("تقدر تبعت 5 اقتراحات في الطلب الواحد. ابعت الطلب ده وافتح واحد جديد") → `retailer_asks_submitted`
- Response promise copy: "اقتراحات وصلونا وفريقنا هيشتغل عليهم عشانك"
- Config: `RETAILER_ASKS_OVERLAY_VERSION`, `RETAILER_ASKS_BANNER_MIN_QUERY_LENGTH` (only offer after N chars typed), `RETAILER_ASKS_OVERLAY_REGISTRATION_DELAY_DAYS` (only for registered-age accounts)

## 7.6 Design logic for POL

1. **"تعديل الطلب" while under review** — the order is a negotiation until the supplier confirms; POL should allow pre-confirmation edits.
2. **Complaint window is explicit and enforced in-app** — prevents abuse, sets expectations.
3. **OST is a wizard, not a form**: type → details → photo, with cooldowns and dedupe — support quality at scale.
4. **Reorder re-negotiates the supplier** — the marketplace reality that availability changes.
5. **Ask-for-product turns dead ends into demand capture** with a submission quota per order.
