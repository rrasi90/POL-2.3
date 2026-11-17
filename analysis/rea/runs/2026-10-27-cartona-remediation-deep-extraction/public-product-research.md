# Cartona Public Product Research — Three Products

**Research run:** Public product research for B2B wholesale marketplace analysis (run 2026-10-27-cartona-remediation-deep-extraction)
**Access date for all sources:** 2026-10-27 (all fetches performed in this session)
**Method:** Public web pages only — Google Play listings, Apple iTunes public lookup API, company marketing sites, and press coverage. No production API was probed, no login attempted, nothing bypassed.
**Evidence-level legend:**
- `PUBLIC_STORE_SCREENSHOT` — visible on a public app-store listing
- `PUBLICLY_DOCUMENTED` — stated in press/coverage or public technical records
- `MARKETING_CLAIM` — self-reported company marketing; not proof of internal behavior

> **Known limitation of this run:** the Play Store pages fetched in this session returned listing text and metadata but did not render screenshot imagery, so no screenshot-by-screenshot visual description was possible. Nothing below describes screenshots that were not actually observed. This is recorded as a gap in Section D.

---

## 1. Cartona retailer app — `com.cartona`

| Field | Value | Evidence |
|---|---|---|
| Listing URL | https://play.google.com/store/apps/details?id=com.cartona | — |
| App name | كرتونة Cartona | PUBLIC_STORE_SCREENSHOT |
| Developer | Cartona Technologies (registered entity: **Cartona B.V.**, Kabelweg 57, 1014 BA Amsterdam, Netherlands; Egyptian ops phone +20 10 06343820) | PUBLIC_STORE_SCREENSHOT |
| Category | Shopping; Rated for 3+ | PUBLIC_STORE_SCREENSHOT |
| Android installs | **500K+** | PUBLIC_STORE_SCREENSHOT |
| Last updated (Android) | **Oct 18, 2026**; "What's new": "Added more improvements" | PUBLIC_STORE_SCREENSHOT |
| Android version number | Not shown on the public page fetched | — |
| iOS cross-reference | iTunes lookup (id1481935260): version **8.4.29**, released **2026-10-19**, min iOS 15.0, seller "Cartona BV", 66 ratings, ~3.42 avg — https://itunes.apple.com/lookup?id=1481935260&country=eg | PUBLICLY_DOCUMENTED |
| Contacts | cartona.com; hello@cartona.com / support@cartona.com; privacy policy cartona.com/privacy-policy/ | PUBLIC_STORE_SCREENSHOT |

**Description (translated from Arabic; key claims, quoting the listing):** targeted at "owners of a market, restaurant, kiosk or cafe" ("لو صاحب ماركت أو مطعم أو كشك او كافيه"). Tagline "السوق في كرتونة" ("The market is in Cartona") and "متقولش معنديش وانت عندك كرتونة" ("Never say you don't have it when you have Cartona"). Claimed features:

- Access to **"أكتر من 2000 مورد و50,000 منتج"** — "more than 2,000 suppliers and 50,000 products," with price comparison before purchase. (`MARKETING_CLAIM` — listing self-description; the 2,000-supplier figure on Play and the "4 suppliers" figure on cartona.com (below) are mutually inconsistent.)
- **Credit / installment purchasing**: "البضاعة تحضر مع كرتونة بالآجل بخطط سداد متنوعة" — "goods arrive with Cartona on credit with varied repayment plans." (`MARKETING_CLAIM`)
- **Group ordering** to lower minimum order quantities: "اطلب براحتك بحد أدنى أقل."
- Offers, discounts, and **cashback**.
- Customer support available anytime.

**Data safety declaration:** may share Location, Personal info and 3 other types with third parties; collects personal info; encrypted in transit; data deletion supported. (`PUBLIC_STORE_SCREENSHOT`)

---

## 2. Cartona suppliers app — `com.cartona.suppliers` ("بنکدار/vendor" side)

| Field | Value | Evidence |
|---|---|---|
| Listing URL | https://play.google.com/store/apps/details?id=com.cartona.suppliers | — |
| App name | كرتونة الموردين (Cartona Suppliers) | PUBLIC_STORE_SCREENSHOT |
| Developer | Cartona Technologies / Cartona B.V. (same record as retailer app; phone +20 100 441 1629 also listed) | PUBLIC_STORE_SCREENSHOT |
| Category | Business; Rated for 3+; in-app purchases available | PUBLIC_STORE_SCREENSHOT |
| Installs | **10K+** | PUBLIC_STORE_SCREENSHOT |
| Last updated | **Jul 14, 2026**; "What's new": "تحسين اداء التطبيق و حل المشاكل" (performance improvements and bug fixes) | PUBLIC_STORE_SCREENSHOT |
| Version | Not shown on the public page fetched | — |

**Description:** "يسمح تطبيق كرتونة للموردين إدارة الطلبيات بكل سهولة وكذلك تعديل أسعار المنتجات والمخزون وعرض التقارير المختلفة" — the Cartona suppliers app lets suppliers easily manage orders, edit product prices and inventory, and view various reports. Feature bullets (translated): **order management; adding/coding new products; creating special offers on products; viewing reports and financial account details.** Closing line: "the app allows a Cartona supplier to manage their products and orders."

**Interpretation (clearly marked as analysis, not source claim):** this is a seller-side console — catalog, pricing, stock, offers, orders, and receivables reporting — i.e., the supplier operates as a **first-party seller on Cartona's marketplace with meaningful self-serve control**, not merely a passive content feed.

**Data safety:** shares personal info, app activity, app info and performance with third parties; encrypted in transit; deletion supported. (`PUBLIC_STORE_SCREENSHOT`)

---

## 3. Cartona Express driver app — `com.cartona.delivery_driver_app`

| Field | Value | Evidence |
|---|---|---|
| Listing URL | https://play.google.com/store/apps/details?id=com.cartona.delivery_driver_app | — |
| App name | كرتونة إكسبريس - السائق (Cartona Express – Driver) | PUBLIC_STORE_SCREENSHOT |
| Developer | Cartona Technologies / Cartona B.V. (same record) | PUBLIC_STORE_SCREENSHOT |
| Category | Productivity; Rated for 3+ | PUBLIC_STORE_SCREENSHOT |
| Installs | **500+** | PUBLIC_STORE_SCREENSHOT |
| Last updated | **Jul 22, 2026** | PUBLIC_STORE_SCREENSHOT |
| Version | Not shown on the public page fetched | — |

**Description (English listing, quoted):** tagline "Greater efficiency and safety in delivering orders." Hook: "Is your work interrupted and you are waiting for orders for long periods?" — the app targets **freelance/idle drivers**, promising to "easily increase your profits by making delivery trips and transporting goods **between wholesalers and retailers**."

Feature bullets (quoted from listing):
1. "Ease of use and joining: The application is simple and fast, making it easy for you to follow up on **daily orders**."
2. "Efficiency: the **fastest ways to deliver orders**, to save your time and effort."
3. "An **advanced system to confirm the receipt of orders** safely and professionally." (Arabic: "نظام آمن: بنظام متطور لتأكيد استلام الطلبيات بأمان واحترافية")
4. "Orders are well-organized and **paired with optimal routes** to save time and effort."
5. "Easily manage your orders and effortlessly **track your profits** with an intuitive interface."
6. A specialized Cartona Express **support team** "ready to help you at any time."

**Driver-workflow signals publicly revealed:**
- **Assignment model:** daily orders pushed to the driver; trips connect wholesaler→retailer legs (the driver is a last-mile/first-mile capacity layer, not the owner of inventory). (`MARKETING_CLAIM`)
- **Proof of delivery:** a "secure system to confirm receipt of orders" — implies digital delivery confirmation; the exact POD mechanics (photo, signature, OTP, cash reconciliation) are **not** disclosed. (`MARKETING_CLAIM`)
- **Navigation/routing:** "optimal routes" supplied by the platform. (`MARKETING_CLAIM`)
- **Earnings:** in-app profit tracking; no commission structure, payout schedule, or per-trip rates disclosed. (`MARKETING_CLAIM`)
- **Joining/onboarding:** described as "simple and fast" — suggests low-friction driver signup; no vehicle or license requirements are stated on the listing. (`MARKETING_CLAIM`)
- **Data safety:** collects **location** and personal info; notably, this listing states "Data can't be deleted" — unlike the other two Cartona listings which support deletion. (`PUBLIC_STORE_SCREENSHOT`)

---

## 4. Cartona official website — https://cartona.com/

**Positioning:** "Egypt's fastest-growing B2B E-commerce marketplace… Bringing the marketplace online, Cartona connects buyers and sellers across the supply chain" with an explicitly **asset-light** stance: "empower the marketplace rather than disrupt it." (`MARKETING_CLAIM`)

**Three user roles described on the homepage:**
- **Retailers:** browse, compare, and order merchandise "24/7," saving "time, money, and effort."
- **Companies (FMCG producers/brands):** salesforce and transport efficiency, expanded user base and orders, "real-time data insights and performance tracking," targeted promotional tools.
- **Wholesalers:** "aggregate the demand of thousands of buyers 24/7," manage inventory via an **ERP system with real-time stock visibility**, and receive/track/complete orders. (`MARKETING_CLAIM`)

**Finance:** embedded finance, cashless payments, and **BNPL (buy now, pay later)** financing "to promote financial inclusion." No delivery-timeframe promises appear on the homepage. (`MARKETING_CLAIM`)

**On-page stats (quoted exactly):** "150 RETAIL USERS," "4 SUPPLIERS," "300 COMPANIES PARTNERSHIPS," "50 PRODUCTS," "18 CITIES."
⚠️ **Reliability caveat:** these figures are almost certainly animated count-up counters captured before animation, and directly contradict both the Play listing (500K+ downloads) and 2024 press coverage ("over 188,000 retailers across 17 cities" — https://assiyaq.com/cartona-raises-8-1-million-in-series-a-extension). Treat the homepage numbers as **unreliable rendering artifacts**, not as company claims. (Cross-checked `PUBLICLY_DOCUMENTED` vs `MARKETING_CLAIM`.)

**News/funding section on site:** July 2024 $8.1M Series A extension; June 2024 partnership with **AMAN Holding** (Egyptian fintech, Raya subsidiary); January 2024 partnership with **Talabat** for restaurant supply procurement. Corroborated by press: $12M Series A (Jul 2022, led by Silicon Badia) — https://waya.media/cartona-egypts-b2b-e-commerce-platform-raises-12m-in-a-series-a-round; $4.5M pre-Series A (Sep 2021) — https://techcrunch.com/2021/09/21/cartona-gets-4-5m-pre-series-a-to-connect-retailers-with-suppliers-in-egypt; $8.1M extension led by Algebra Ventures (Aug 2024) — https://nextbillion.net/news/egypts-cartona-raises-8-1-million-even-as-investors-pull-back-from-b2b-e-commerce-in-africa. (`PUBLICLY_DOCUMENTED`)

**Team:** Mahmoud Talaat (Co-founder & CEO), Rami Essam (COO), Waseem Naguib (CCO), Hamdy Khalil (VP Engineering), Rafik Zaher (Co-founder). Address: 23 Mesadak Street, Dokki, Giza, Egypt. All navigation is single-page anchors (`#retailers`, `#companies`, `#wholesalers`, `#productSolution`, …); no dedicated /retailers page exists (404 on https://cartona.com/retailers, verified this session).

---

## 5. Cartona Enterprise — https://enterprise.cartona.com/en

**Service:** a **sourcing/supply service for large operations** — "Cartona Enterprise is our arm for large operations: the same network and buying power, tailored to your scale." Tagline: "**The trusted supplier behind Egypt's biggest apps**." Target customers explicitly include **delivery apps** that need bulk FMCG supply. (`MARKETING_CLAIM`)

**How it works (3 steps, quoted):**
1. "**Request products**" — send product names/quantities or "your full list as-is" (form accepts Excel, PDF, or a **photo** of the list).
2. "**We source the price**" — comparison and negotiation, reply "**within 24 hours**."
3. "**We deliver on time**" — to any branch or warehouse, across "every governorate of Egypt."

**Promised terms (verbatim):** "Best price, guaranteed"; "**100% on-time delivery**"; "Delivery Within 48h"; "Any product — we source it"; dedicated account manager "with you from the first order"; "Your data is safe — we never share it with anyone." Example shown: mineral water at EGP 120 vs EGP 136 (12% saving); sample order of EGP 686 with "14% savings." (`MARKETING_CLAIM`)

**Notably absent:** no credit terms, no API/app integration, no SLA documentation — this is a lead-gen funnel (form → 24h pricing quote), not a self-serve platform. Several displayed stats (products available, on-time rate) rendered as placeholder zeros on fetch.

---

## 6. Competitor comparators

### 6a. Gumla (Egypt) — https://www.gumla.com/en (accessed 2026-10-27)

- **Model:** "a B2B platform connecting retailers directly with suppliers," monetizing both sides of the marketplace. (`MARKETING_CLAIM`)
- **Roles:** retailers ("One-Stop-Shop," claimed "10,000+ Traders"), suppliers ("Direct ERP integration," "**Guaranteed collection, zero risk**," analytics dashboard), brands/fintech partners ("50+ Global Brands"). (`MARKETING_CLAIM`)
- **Delivery ownership:** "**We Deliver with Our Own Fleet**" — same-day and next-day delivery claimed across **all 27 Egyptian governorates**. This is a first-party-logistics model, in contrast to Cartona's asset-light marketplace + Express driver layer. (`MARKETING_CLAIM`)
- **Credit/BNPL:** "Cash, mobile wallet, bank transfer, and flexible credit options"; "**Pay Later up to 60 days**"; demo app screen shows available credit of EGP 5,000. (`MARKETING_CLAIM`)
- **Apps:** retailer app on Play (`com.gumla`, per site footer link — note: direct fetch of that Play URL returned 404 this session; recorded as a finding) and App Store id1592330301. iTunes lookup: **Gumla v1.6.1**, released **2026-10-10**, seller "GUMLA FOR DISTRIBUTION," 11 ratings, ~4.73 — description mentions Egyptian payment-gateway integration and **fulfillment services** (https://itunes.apple.com/lookup?id=1592330301&country=eg). (`PUBLICLY_DOCUMENTED`)

### 6b. MaxAB (Egypt; now MaxAB–Wasoko) — Play listing + press

- **⚠️ Website status finding:** https://maxab.io (and www.maxab.io) currently serves a page whose footer reads verbatim: "**Static demo rebuild — not affiliated with or endorsed by Maxab**." The official site content could not be verified this session; all MaxAB model claims below therefore come from the Play listing and press. (Finding, recorded 2026-10-27.)
- **Play listing** (https://play.google.com/store/apps/details?id=com.maxab.maxab, accessed 2026-10-27): app "MaxAB," developer "MaxAB Technologies / MAXAB FOR E COMMERCE, Cairo, Egypt," **1M+ installs**, updated **Oct 14, 2026**. Features: one-click full-shop ordering, "Offers & Bundles," "**Fastest delivery service & Fulfillment**," and **MaxAB Payments** (fintech since 2021: bill payments, e-wallets, recharge — branded "Max Pay"). Credit is **not mentioned** in the listing. (`PUBLIC_STORE_SCREENSHOT`)
- **Model/roles (Play description):** B2B e-commerce linking food and daily-essentials retailers with suppliers in Egypt and Morocco; small merchants compare prices and restock from their phones. (`PUBLIC_STORE_SCREENSHOT`)
- **Corporate context:** MaxAB merged with Wasoko (Kenya) — preliminary terms Dec 2023, finalized Aug 2024, all-stock; combined entity across Egypt, Morocco, Kenya, Tanzania, Rwanda, Nigeria; post-merger pivot from GMV growth to **profitability and fintech**, with Morocco e-commerce wound down in mid-2025 (https://lucidityinsights.com/news/maxab-merges-with-wasoko, accessed via search 2026-10-27). (`PUBLICLY_DOCUMENTED`)
- No supplier or driver companion apps are referenced in MaxAB's public listing.

### 6c. (Context) Cartona Enterprise as Cartona's own B2B "supplier-of-record" arm
Treated in Section 5; functionally comparable to a contract-wholesale offering rather than a marketplace, which is itself a competitive data point: the marketplace also sells supply directly to apps.

---

# Analysis

## A. Feature classification by role

Legend: **CATEGORY_EXPECTATION** = generic B2B wholesale expectation · **CARTONA_SPECIFIC_EVIDENCE** = specifically evidenced for Cartona from a cited source · **POL_MARKET_HYPOTHESIS** = plausible for the Iranian market but unverified.

### Retailer role
| Feature | Class | Note |
|---|---|---|
| Multi-supplier catalog with price comparison | CARTONA_SPECIFIC_EVIDENCE — "2,000+ suppliers, 50,000 products," compare prices (Play listing) | |
| Credit / installment purchasing (آجل) with repayment plans | CARTONA_SPECIFIC_EVIDENCE — "بالآجل بخطط سداد متنوعة" (Play) | |
| Group ordering to lower MOQs | CARTONA_SPECIFIC_EVIDENCE — Play listing | |
| Cashback, offers, discounts | CARTONA_SPECIFIC_EVIDENCE — Play listing | |
| BNPL/embedded finance framing | CARTONA_SPECIFIC_EVIDENCE — cartona.com | |
| Cart/cart-based ordering, order history, reorder | CATEGORY_EXPECTATION | Universal in B2B apps; not itemized on Cartona's listing |
| Category browse, search, favorites | CATEGORY_EXPECTATION | |
| In-app support chat / order tracking | CATEGORY_EXPECTATION (support is claimed; tracking only implied by "orders arrive") | |
| Pharmacy/consumables-specific assortments (Iranian wholesale norms) | POL_MARKET_HYPOTHESIS | |
| Cash-on-delivery + ledger book (دفتر دستی) digitization | POL_MARKET_HYPOTHESIS | Iranian retailers commonly run روزه/دفتر credit; a ledger view would mirror Cartona's آجل plans |

### Supplier role
| Feature | Class | Note |
|---|---|---|
| Order management inbox | CARTONA_SPECIFIC_EVIDENCE — Play listing bullet | |
| Product coding/catalog creation | CARTONA_SPECIFIC_EVIDENCE — Play listing bullet | |
| Price and inventory editing | CARTONA_SPECIFIC_EVIDENCE — Play listing | |
| Special offers/promotions self-serve | CARTONA_SPECIFIC_EVIDENCE — Play listing bullet | |
| Reports + financial account (receivables) view | CARTONA_SPECIFIC_EVIDENCE — Play listing bullet | |
| ERP integration / real-time stock sync | CARTONA_SPECIFIC_EVIDENCE — cartona.com claims wholesalers manage inventory "via an ERP system with real-time stock visibility" (supplier-side ERP is claimed for wholesalers; whether the app itself integrates ERP is unverified) | |
| Fulfillment/slab-splitting, pick-pack workflow | CATEGORY_EXPECTATION | Not mentioned publicly |
| Negotiated price lists per retailer tier | CATEGORY_EXPECTATION | |
| Iranian-specific: bulk/pack breakdown (کارتن/بسته/عدد), weight-based items | POL_MARKET_HYPOTHESIS | |

### Driver role
| Feature | Class | Note |
|---|---|---|
| Daily order assignments | CARTONA_SPECIFIC_EVIDENCE — "follow up on daily orders" (Play) | |
| Optimized routing | CARTONA_SPECIFIC_EVIDENCE — "paired with optimal routes" (Play) | |
| Delivery confirmation / POD system | CARTONA_SPECIFIC_EVIDENCE — "advanced system to confirm the receipt of orders" (Play); mechanics undisclosed | |
| Earnings/profit tracking | CARTONA_SPECIFIC_EVIDENCE — "track your profits" (Play); payout terms undisclosed | |
| Idle-capacity recruitment ("boost income between trips") | CARTONA_SPECIFIC_EVIDENCE — the listing's entire hook | Implies gig/freelance driver model, not employed fleet |
| Support channel | CARTONA_SPECIFIC_EVIDENCE — dedicated Cartona Express support team | |
| Photo/signature POD, cash collection & reconciliation, exception reporting, offline mode | CATEGORY_EXPECTATION | None publicly evidenced (see D) |
| GPS location streaming during active trips | CARTONA_SPECIFIC_EVIDENCE (weak) — Data safety declares **location collection** (Play) | |
| Offline-first delivery for poor connectivity | POL_MARKET_HYPOTHESIS | Relevant to Iranian intercity wholesale routes |
| Motorcycle-courier norms (moped POD, helmet photo) | POL_MARKET_HYPOTHESIS | Iranian urban delivery culture differs from Egypt's van/pickup wholesale legs |

## B. Driver workflow deep-dive (Cartona Express)

Everything publicly knowable, with source and confidence:

1. **Who drivers are:** independent drivers with idle capacity ("Is your work interrupted and you are waiting for orders for long periods?") who earn by "delivery trips and transporting goods between wholesalers and retailers." The driver is a **capacity layer bridging Cartona's wholesale supply to retail demand**, recruited gig-style. (`MARKETING_CLAIM`, Play listing, accessed 2026-10-27)
2. **Assignment:** orders arrive as a **daily order list** to follow; the framing is reactive queue ("follow up on daily orders") rather than scheduled shifts. (`MARKETING_CLAIM`)
3. **Routing:** platform-optimized routes per order set ("optimal routes to save time and effort") — i.e., the app suggests sequencing; whether it deep-links to Google Maps or has embedded navigation is **unknown**. (`MARKETING_CLAIM` + gap)
4. **Proof of delivery:** exists as a concept — "an advanced system to confirm the receipt of orders safely and professionally"; Arabic stresses "تأكيد استلام الطلبيات" (confirming receipt of the orders). The listing does **not** say whether POD is photo, signature, OTP, or cash-receipt based. (`MARKETING_CLAIM` + gap)
5. **Earnings:** "track your profits with an intuitive interface" — per-trip or aggregate earnings visibility; payout method/cycle and commission split **not disclosed**. (`MARKETING_CLAIM` + gap)
6. **Support:** in-app access to a dedicated Cartona Express support team "at any time." (`MARKETING_CLAIM`)
7. **Telemetry:** the data-safety section declares **location collection** and states data "can't be deleted" — consistent with trip tracking, and unusual relative to Cartona's other two apps. (`PUBLIC_STORE_SCREENSHOT`)
8. **Maturity signal:** only **500+ installs** and a Jul 22, 2026 update — a young, small-scale operation relative to the retailer app's 500K+. (`PUBLIC_STORE_SCREENSHOT`)

**Driver-app readiness read-across (for a separate driver product):** the publicly evidenced minimal feature set is *assignment list → routed trip → delivery confirmation → earnings view → support*. Any readiness assessment should treat photo-POD, cash reconciliation, exception flows, and offline mode as unproven for Cartona and table stakes in the category — competitors in adjacent markets (e.g., any last-mile driver app) standardize on these even when Cartona doesn't advertise them.

## C. Egypt vs Iran market differences relevant to wholesale distribution

Only sourced claims are stated; speculation is labeled.

1. **Credit culture is formalizing via BNPL in Egypt.** Cartona sells "آجل" credit "with varied repayment plans" (Play listing) and BNPL/embedded finance with a fintech partner, **AMAN Holding** (cartona.com news, June 2024; `MARKETING_CLAIM`+`PUBLICLY_DOCUMENTED`). Gumla similarly offers "Pay Later up to 60 days" (`MARKETING_CLAIM`). *Hypothesis (unverified):* Iranian wholesale runs on deep informal مذاکره/چک (post-dated check) cycles; a POL product would need check-and-ledger reconciliation rather than fintech BNPL rails, since domestic card-based BNPL infrastructure and cross-border fintech partnerships don't map 1:1.
2. **Delivery ownership diverges by model, not country.** Cartona is explicitly asset-light (cartona.com: "empower the marketplace rather than disrupt it") with a gig-driver Express layer; Gumla claims **its own fleet** with 27-governorate same/next-day delivery (gumla.com). MaxAB claims "Fastest delivery service & Fulfillment" (Play). *Hypothesis (unverified):* in Iran, intercity wholesale legs are dominated by existing باربری (freight/urban goods transport) networks; a marketplace likely partners with them rather than builds a fleet.
3. **Wholesale role structure:** Egypt's model distinguishes **retailer / wholesaler / FMCG company** with suppliers operating ERP-backed stock (cartona.com); Cartona Enterprise even serves other **apps** as buyers. *Hypothesis (unverified):* Iran's traditional trade has a stronger hierarchical بنکدار → عمده‌فروش → خرده‌فروش chain with regionally bounded benkdar territories, so a supplier-side app needs territory/exclusive-region logic that Egyptian listings never mention.
4. **Units & packaging:** no public Cartona source documents unit-of-sale handling (cartons/cases vs units) beyond generic "50,000 products." *Hypothesis (unverified):* Iranian wholesale pricing is heavily unit-graded (کارتن، بسته، شانه، عدد) with daily price volatility; Egyptian listings don't surface this complexity, so a POL spec should not assume parity.
5. **Scale benchmarks:** Cartona ~188K retailers / 17 cities (press, 2024 — assiyaq.com/nextbillion.net), 500K+ Play installs; MaxAB 1M+ installs across Egypt/Morocco pre-wind-down; Gumla claims 10K+ traders. These are comparable single-country trade marketplaces, not multi-country rails like Wasoko.

## D. Gaps — what could NOT be learned from public sources

1. **Screenshots:** Play Store pages fetched in this session did not render screenshot imagery for any of the three Cartona apps; no visual UI description is possible from this run. (Recorded limitation; re-run with a rendering fetcher or device install would be needed.)
2. **Android version numbers:** not displayed on any of the three Play pages fetched; only the iOS retailer build (8.4.29, 2026-10-19) is publicly verifiable via Apple's lookup API. iOS versions exist for Cartona retailer (id1481935260) and Gumla (id1592330301); no iOS counterparts of the Cartona suppliers or driver apps were identified.
3. **Driver mechanics:** POD method (photo/signature/OTP/cash), cash-handling and reconciliation, exception/failed-delivery flows, offline behavior, payout cycle, commission structure, vehicle requirements, and onboarding/KYC steps — none disclosed.
4. **Supplier economics:** commission rates, who owns pricing authority (supplier vs Cartona), fulfillment responsibility (supplier ships vs Cartona picks up), and returns/claims workflow — not disclosed.
5. **Retailer economics:** actual credit limits, interest/fee structure of "آجل" plans, cashback percentages, delivery SLA and minimum order values — not disclosed anywhere public.
6. **Ratings:** star ratings/review counts for the Android listings were not rendered in fetched pages (only iOS: 3.42★/66 for retailer).
7. **Cartona Express operational footprint:** cities served by Express, driver counts, and whether the driver layer covers Cartona Enterprise's 48h warehouse deliveries — unknown.
8. **MaxAB official web presence:** maxab.io is currently a disclaimed "static demo rebuild"; original site content could not be verified, limiting model-level sourcing to its Play listing and press.
9. **Gumla Play listing:** the site-linked URL `com.gumla` returned 404 at fetch time (package may have changed); app status verified only via iOS lookup.

---

## Source register

| # | Source | Publisher | Access date | Evidence level |
|---|---|---|---|---|
| 1 | https://play.google.com/store/apps/details?id=com.cartona | Google Play / Cartona Technologies | 2026-10-27 | PUBLIC_STORE_SCREENSHOT |
| 2 | https://play.google.com/store/apps/details?id=com.cartona.suppliers | Google Play / Cartona Technologies | 2026-10-27 | PUBLIC_STORE_SCREENSHOT |
| 3 | https://play.google.com/store/apps/details?id=com.cartona.delivery_driver_app (+&hl=ar) | Google Play / Cartona Technologies | 2026-10-27 | PUBLIC_STORE_SCREENSHOT |
| 4 | https://itunes.apple.com/lookup?id=1481935260&country=eg | Apple iTunes public lookup | 2026-10-27 | PUBLICLY_DOCUMENTED |
| 5 | https://cartona.com/ | Cartona | 2026-10-27 | MARKETING_CLAIM |
| 6 | https://enterprise.cartona.com/en | Cartona | 2026-10-27 | MARKETING_CLAIM |
| 7 | https://www.gumla.com/en | Gumla | 2026-10-27 | MARKETING_CLAIM |
| 8 | https://itunes.apple.com/lookup?id=1592330301&country=eg | Apple iTunes public lookup | 2026-10-27 | PUBLICLY_DOCUMENTED |
| 9 | https://play.google.com/store/apps/details?id=com.maxab.maxab | Google Play / MaxAB Technologies | 2026-10-27 | PUBLIC_STORE_SCREENSHOT |
| 10 | https://maxab.io / https://www.maxab.io/ | (unofficial static demo) | 2026-10-27 | Finding — not official |
| 11 | https://lucidityinsights.com/news/maxab-merges-with-wasoko | Lucidity Insights | 2026-10-27 (via search) | PUBLICLY_DOCUMENTED |
| 12 | https://nextbillion.net/news/egypts-cartona-raises-8-1-million-even-as-investors-pull-back-from-b2b-e-commerce-in-africa | NextBillion | 2026-10-27 (via search) | PUBLICLY_DOCUMENTED |
| 13 | https://assiyaq.com/cartona-raises-8-1-million-in-series-a-extension | Assiyaq | 2026-10-27 (via search) | PUBLICLY_DOCUMENTED |
| 14 | https://waya.media/cartona-egypts-b2b-e-commerce-platform-raises-12m-in-a-series-a-round | Waya | 2026-10-27 (via search) | PUBLICLY_DOCUMENTED |
| 15 | https://techcrunch.com/2021/09/21/cartona-gets-4-5m-pre-series-a-to-connect-retailers-with-suppliers-in-egypt | TechCrunch | 2026-10-27 (via search) | PUBLICLY_DOCUMENTED |

**Key findings recap:** (1) Cartona runs a three-app public footprint — 500K+-install retailer marketplace app (updated Oct 2026), 10K+-install supplier console, and a very early 500+-install driver app (Jul 2026) whose listing reveals assignment→routing→POD→earnings as the core loop but nothing about POD mechanics, cash handling, or offline. (2) Cartona's positioning is explicitly asset-light marketplace + BNPL with an AMAN fintech partnership, plus an Enterprise arm that sources and 48h-delivers bulk supply to other apps. (3) The strongest competitor contrast is Gumla's first-party-fleet model vs Cartona's gig-driver layer; MaxAB's site is currently an unofficial demo rebuild (recorded as a finding), with app data sourced from its 1M+-install Play listing.