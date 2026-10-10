# 05 — Suppliers & Product Surfaces

Cartona's model: multiple suppliers compete for the retailer's order; the retailer composes one cart across suppliers, respecting each supplier's minimums. Evidence: ps2, ps3, frames 007/010/046/048/056.

---

## 5.1 Suppliers list (الموردين) — ps2

Top→bottom:
1. **Top bar:** hamburger + search icon, title "الموردين"
2. **Trade-level tabs:** `الجملة` (wholesale, default) · `الشركات` (companies) · `جملة الجملة` (mega-wholesale) — audience segmentation
3. **Collections row:** chips linking curated collections, e.g., "توريدات المخابز والكافيهات" (bakery & café supplies), "تجهيزات المحلات" (shop equipment) with a red **"جديد"** badge
4. **Filter & sort button:** "تصفية وترتيب النتائج" + funnel icon → `suppliers_filter_selected`
5. **Supplier cards** (see 5.2 anatomy), infinite scroll

**Events:** `suppliers_list_viewed2`, `suppliers_search_clicked/executed/result_clicked`, `suppliers_filter_selected`.

## 5.2 Supplier card anatomy (from ps2/ps3/frames)

```
┌────────────────────────────────────────────────┐
│ [logo]  شركة X  (ك)verified  ★★★★☆  [🛒 button] │
│ [ادره مجموعه] ← "group-managed" blue pill       │
│ ┌─ dashed border (min-requirements block) ───┐ │
│ │ حد أدنى لمطابقة المجموعة: 3,500 ج.م (was 5,000)│ │
│ │ حد أدنى لعدد المنتجات: 5 منتجات (was 8)     │ │
│ └────────────────────────────────────────────┘ │
│ التوصيل خلال 24 ساعة        (teal SLA line)     │
│ [كاش 💵] [ربح كرتونة] [تفسيط 💳]  payment chips  │
│ [كاش باك 3%]  ← yellow cashback badge            │
└────────────────────────────────────────────────┘
```

- Price strikethroughs show **changing minimums** ("تغيّر الحد الأدنى للطلب: كان …") — the minimums are *dynamic and communicated*.
- Payment chips = per-supplier accepted methods incl. cash, Cartona-profit, installments (تفسيط), cashback.
- Events: `supplier_card_clicked2`, `supplier_card_impression`, `supplier_cart_cta_clicked`.

## 5.3 Supplier page (store inside the marketplace) — frames 046/048/056

Top→bottom:
1. **Supplier header (sticky, flag `ENABLE_SUPPLIER_PAGE_STICKY_HEADER`):** logo + name + verified + star rating + member-since ("اشترك من 4 سنوات") + min-order facts + location ("المنصورة، الدقهلية" with pin) + payment chips
2. **Supplier search bar:** "ابحث عن منتج" (`supplier_search_tapped`)
3. **Horizontal category chips:** الكل، مأكولات، مشروبات، ... (`supplier_category_filter_clicked/scrolled`), with root-category dropdown (`supplier_root_category_dropdown_opened/switched`)
4. **Brand filter** horizontal scroller (`supplier_brand_filter_clicked2/scrolled`, `supplier_all_brands_clicked`)
5. **Offer carousel** (`supplier_offer_carousel_viewed`) + **max-discount card** (`supplier_max_discount_card_viewed/clicked`)
6. **Product grid 2-col** (cards below) with pagination (`supplier_page_pagination_loaded`, `SUPPLIER_PAGE_VERSION` experiment flag)
7. Tabs: default tab can be Offers (`SUPPLIER_PAGE_DEFAULT_TAB_IS_OFFERS`)
8. Favorite toggle (`supplier_favorite_toggled`), all-products view (`supplier_all_products_clicked2`)

## 5.4 Product card (purchasable)

```
┌──────────────┐
│  [image]     │  ← + blue chip "وفر 18 ج" (savings badge)
│ اسم المنتج   │  ← 2 lines
│ متوفر 192    │  ← stock count
│ 615 ج  اقل كميه 6 │ ← price + min-qty
│ [- 1 +]      │  ← inline quantity stepper (adds to cart directly)
└──────────────┘
```

- Two card variants under test: `PURCHASABLE_PRODUCT_CARD_SUPPLIER_SCREEN_VARIANT_VERSION`, `PURCHASABLE_PRODUCT_CARD_SUPPLIER_SHOWCASE_VARIANT_VERSION`
- `SHOW_MAX_QUANTITY_ON_PRODUCT_CARD` flag
- Events: `product_info_impression`, `product_info_clicked`

## 5.5 Product detail + price sheet

- Detail: big image, name, price + savings, stock, tabs row (متوفر عند / مواصفات / ...), supplier comparison entry
- **Price sheet** (bottom sheet): compares the same product across suppliers with quantities — `product_price_sheet_viewed/closed`
- **Product suppliers screen** (`ProductSuppliersScreen`, `product_suppliers_viewed`): all suppliers offering the SKU
- Min/max quantity enforcement strings: "الحد الأدنى للكمية المطلوبة هو …"، "الحد الأقصى للكمية المتاحة هو …"

## 5.6 Sponsored showcase on home

`SupplierShowcaseCard2` + `SupplierShowcaseCartCTA` + list page size flags — supplier ads with direct cart CTA.

## 5.7 Design logic for POL

1. **Supplier = first-class object** with its own storefront, minimums, SLA, payment chips — the marketplace aggregates stores, not just SKUs.
2. **Minimums are shown as a dashed "requirements block" on every card** — never surprise the retailer at checkout.
3. **Dynamic minimums with strike-through history** communicate flexibility ("was 5,000 now 3,500").
4. Category chips + brand chips + offer carousel = 3 parallel navigation systems on one page; keep them horizontally scrollable and sticky.
5. **Inline steppers on product cards** make ordering a one-tap act; the cart bar is always visible.
