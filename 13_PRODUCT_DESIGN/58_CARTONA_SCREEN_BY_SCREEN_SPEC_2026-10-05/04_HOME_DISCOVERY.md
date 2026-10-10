# 04 — Home & Discovery

Evidence: Play Store screenshot ps1 (guest home), ps4 (credit home), video frames, event taxonomy.

---

## 4.1 Home — two variants

### A) Guest / logged-out home (ps1)
Top→bottom:
1. **Top bar (white):** hamburger (menu) — cart pill with count/amount badge (blue, left in RTL) — title "الرئيسية"
2. **Search bar:** "ابحث عن منتج ..." with magnifier icon
3. **Hero banner carousel** (full-width, brand-blue campaign art "السبوع كرتبونة") + page dots → `banner_impression/clicked/swiped2`
4. **Categories section "الاصناف":** 3-column grid of category tiles (real product photos + label: المشروبات الغازية، منتجات الألبان والأجبان، حلويات وسناكس، معجنات ومجمدات، ...) → `home_categories_section_viewed`, `home_category_clicked2`, `home_all_categories_clicked`
5. Cube-pattern watermark at page corner

### B) Logged-in home (ps4) — credit-merchant variant
1. **Dark navy top bar:** hamburger + "كرتونة بالأجل" (Cartona Credit) logo — skin switches per user segment
2. **Credit card widget (white on blue):**
   - "الحد المتاح" (available limit) — masked when not yet approved
   - "المستخدم: 13,690 من 22,500 ج.م" (used vs limit)
   - progress bar
   - inner light-blue card: "رصيد المحفظة: 0 ج.م" + wallet icon + **"شحن المحفظة"** button
3. **Quick actions row** (3 circular icon buttons): sales/orders stats، الطلبات السابقة، الأسئلة المتكررة (FAQ)
4. **"المستحقات" (dues) section** with "المزيد" link: rows of supplier name + payment-status tag + amount + date (e.g., "الاحمد (الفاهرة) — الجزيرة والتوزيع — 1013.73 ج.م — 23 يناير 2024")

**Event-proof:** `home_viewed`, `postlogin_home_viewed2`, `home_orders_section_viewed`, `home_offers_section_viewed`, `goals_widget_clicked`.

## 4.2 Campaign & storytelling surfaces (remote-config driven)

| Surface | Behavior | Events |
|---|---|---|
| In-app story (TikTok-style full-screen) | slides, CTA, dismiss | `communication_campaign_in_app_story_viewed/slide_viewed/cta_tapped/dismissed2` |
| Announcement screen | promo page with CTA | `announcement_screen_viewed/cta_clicked` |
| Sponsored suppliers (home section) | paid placement cards | `sponsored_suppliers_section_viewed/card_clicked/view_all_clicked` |
| Seasonal themes | Ramadan / Eid al-Fitr / Eid al-Adha / World Cup skins + gift scratch cards + quiz | `ENABLE_RAMADAN_THEME2`, `ENABLE_EID_AL_FETR_THEME`, `ENABLE_EID_AL_ADHA_THEME`, `ENABLE_WORLD_CUP_THEME` + `eid_*`, `rmdn_quiz_*` events |

**Home composition is a config experiment platform:** flags `HOME_PAGE_DEFAULT_BANNER`, `HOME_SUPPLIER_CATEGORIES_SECTION_VERSION`, flash-offer limits (`FLASH_OFFERS_PRODUCTS_LIMIT`), supplier-showcase pagination (`SUPPLIER_SHOWCASE_LIST_PAGE_SIZE`, `SUPPLIER_SHOWCASE_PRODUCTS_LIMIT`).

## 4.3 Search

- Entry: search bar tap (`search_field_tapped`)
- Search screen: full-width field + suggestions area ("المقترحات") + keyboard (frame 048)
- Execute (`search_executed`) → results list; result click (`search_result_clicked2`)
- **No-results rescue:** "retailer asks" sheet opens directly from no-results (`retailer_asks_shortcut_from_no_results`) — request-the-product flow instead of a dead end

## 4.4 Notifications center

- List with empty state: "لا توجد إشعارات" / "ستظهر إشعاراتك هنا عند وصولها"
- FCM-driven; tap targets deep-link into orders/suppliers

## 4.5 Design logic for POL

1. Home is a **sectioned feed of remote-controlled modules** (banner, categories, offers, orders, dues, sponsored) — build a module registry, not hardcoded sections.
2. **Money-first header for credit users** (limit widget) vs **catalog-first for guests** — same screen, segmented composition.
3. Search never dead-ends: route misses into a product-request sheet.
4. Category tiles use **real product photography**, not icons.
