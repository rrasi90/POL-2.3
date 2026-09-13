import os

notes_dir = r"research\notes"

tier1_notes_part2 = {
"benchmark-growsari-philippines.md": """---
id: benchmark-growsari-philippines
title: "Benchmark Deep Dive: GrowSari (Philippines) — MSME Super-Platform & Sari-Sari Digitization"
tags:
  - pol-b2b-benchmark-2d6747
  - benchmark-tier1
  - philippines
  - fintech
  - retail-tech
created: 2026-09-03
source: "DealStreetAsia, Tech in Asia, KKR, Tencent, IFC, GrowSari Filings"
tier: institutional
type: note
status: active
utility_score: 17.0
---

# Benchmark Deep Dive: GrowSari (Philippines)

## 1. Executive Summary & Identity
- **Company Name:** GrowSari
- **Country:** Philippines (Luzon, Visayas, Mindanao — nationwide footprint across 400+ municipalities)
- **Founders:** Reymund "ER" Rollan (CEO, ex-Unilever, P&G marketing veteran), Shiv Choudhury (ex-BCG partner)
- **Founded:** 2016
- **Current Status (as of 2026-09-03):** Active, leading B2B retail and fintech platform in the Philippines. Raised $110M+ to $157M in funding from marquee investors including KKR, Tencent, IFC, Pavilion Capital, and Oppenheimer Generations Asia (August 2024). Estimated annual revenue of $25M - $50M. Reached EBITDA breakeven in mature urban operating clusters.
- **Scale:** 100,000+ active *sari-sari* stores (neighborhood micro-convenience kiosks) and small groceries.

## 2. The Core Problem Solved
The Philippines has over 1.1 million *sari-sari* stores representing 60% of total FMCG sales in the country. Key pain points:
1. Micro-scale and fragmentation: Average store is a tiny window in a residential house, operating with low working capital ($50 - $100).
2. Sourcing penalty: Store owners closed their shops for half a day to commute via tricycle or jeepney to wet markets and supermarkets, paying retail or semi-wholesale prices.
3. Lack of banking: Over 70% of sari-sari owners are unbanked or underbanked, with zero access to formal credit lines.
4. Thin product margins: FMCG retail markup is 10-15%, easily eroded by transport and wasted time.

## 3. Product Ecosystem: The 3 Core Lines
1. **SariMart (B2B E-Commerce):** Mobile app offering 1,000+ top-selling FMCG SKUs at manufacturer-direct distributor prices, delivered next-day to the store doorstep with low MOQs.
2. **SariPay (Financial Services & Utility Hub):** The ultimate retention engine. Turns the sari-sari store into a neighborhood digital service hub:
   - *Telco Airtime Load:* Real-time wholesale loading of Globe and Smart mobile credit.
   - *Utility Bill Payments:* Consumers pay electricity, water, and internet bills at the sari-sari store.
   - *Cash-in / Cash-out / Remittance:* Partnering with digital wallets (GCash, Maya).
   - *E-Credit Working Capital:* 7-day revolving micro-credit lines for inventory replenishment.
3. **Tranko (Logistics & Micro-Distribution):** Optimized multi-tier logistics network combining central warehouses with contracted 3PL van and motorcycle couriers.

## 4. Operational Architecture: Hybrid Scaling
- **Fulfillment:** Operates regional distribution centers (DCs) combined with cross-dock hubs. Leverages strong brand relationships (Unilever, Nestlé, P&G, Universal Robina) to purchase at Tier-1 distributor tiers.
- **Micro-Delivery Optimization:** Designed logistics algorithms specifically for high-density, narrow-alley urban barangays where standard delivery trucks cannot enter.

## 5. Phygital Strategy & Retention Driver
- **The "Store as a Bank" Psychology:** While wholesale FMCG delivery provided the entry wedge, SariPay services (telco load and bill payment) became the dominant daily engagement driver. Store owners earn micro-commissions on every consumer bill paid, turning their shop into a recurring community hub.
- **Field Onboarding Champions:** Deployed field agents to conduct intensive handholding during the first 30 days, teaching non-tech-savvy sari-sari mothers ("Nanays") how to navigate digital payments and order stock.

## 6. Unit Economics & Monetization
- **Gross Margins:** Blended 4.5% - 7.0% on FMCG wholesale; 1.5% - 3.0% take-rate on digital financial transactions (bill payments, telco load).
- **Fintech Margin Multiplier:** Working capital micro-loans carry monthly fees of 2.0% - 3.5%, yielding high annual ROIC with low default rates (<2.5%) because delinquent stores are cut off from telco loading and wholesale supplies.
- **AOV:** ~$35 - $60 (lower than Middle East peers, reflecting daily micro-purchasing habits of sari-sari stores), compensated by high order frequency (2 to 3 orders per week).

## 7. Strategic Relevance to POL
- **Ancillary Revenue via Digital Services:** Shows how a B2B platform can transform small retail stores into neighborhood service hubs (خدمات الکترونیک، پرداخت قبوض، شارژ)، dramatically boosting retailer retention and platform stickiness.
- **Category Focus:** GrowSari focused exclusively on the top 20% high-velocity FMCG SKUs that generate 80% of volume, avoiding long-tail inventory drag.
- **The Power of Micro-Credit as a Lock-in:** Micro-credit tied directly to daily restocking creates near-zero churn among active merchants.
""",

"benchmark-shopup-mokam-bangladesh.md": """---
id: benchmark-shopup-mokam-bangladesh
title: "Benchmark Deep Dive: ShopUp / Mokam (Bangladesh) & The SILQ Evolution"
tags:
  - pol-b2b-benchmark-2d6747
  - benchmark-tier1
  - bangladesh
  - logistics
  - silq-group
created: 2026-09-03
source: "TechCrunch, Bloomberg, DealStreetAsia, The Daily Star, ShopUp Filings"
tier: institutional
type: note
status: active
utility_score: 17.5
---

# Benchmark Deep Dive: ShopUp / Mokam (Bangladesh)

## 1. Executive Summary & Identity
- **Company Name:** ShopUp (operating B2B brand **Mokam**); merged with Saudi Arabia's **Sary** in April 2025 to form **SILQ Group**.
- **Country:** Bangladesh (Dhaka, Chittagong, Sylhet, nationwide footprint across 64 districts).
- **Founders:** Afeef Zaman (Group CEO, SILQ Group), Ataur Rahim Chowdhury (COO), Siffat Sarwar.
- **Founded:** 2017 (pivoted to full B2B supply chain in 2019-2020).
- **Current Status (as of 2026-09-03):** Operating as the South Asian pillar of the newly formed **SILQ Group** (cross-regional Gulf-South Asia B2B commerce and embedded finance conglomerate). Reached monthly EBITDA positivity in late 2023. Raised over $220M prior to the 2025 merger from Peter Thiel's Valar Ventures, Prosus, Sequoia Capital India (Peak XV), and Flourish Ventures.
- **Scale:** Over 500,000 neighborhood grocery shops (mudir dokan), processing millions of tons of staple foodstuffs and packaged FMCG annually.

## 2. The Core Problem Solved
Bangladesh has 4.5 million MSMEs, with traditional "mudir dokans" accounting for 98% of retail food and grocery consumption. Challenges:
1. Highly fragmented agricultural and manufactured food supply chain with 5 to 7 layers of middle-tier middlemen (arats, beparis, wholesalers).
2. Acute logistics bottlenecks: Monsoon flooding, river crossings, extreme traffic in Dhaka.
3. Informality: Over 95% of small retailers lacked formal credit access, relying on exploitative local money lenders charging 30-50% annualized interest.
4. Food inflation and quality adulteration in bulk staples (rice, pulses, edible oil, flour).

## 3. The 3 Integrated Engines of ShopUp
1. **Mokam (B2B Sourcing Marketplace):** Sourcing partner for neighborhood grocery stores. Operates directly at the mill and factory level, aggregating bulk food staples and packaged FMCG and delivering directly to mudir dokans.
2. **REDX (Proprietary Logistics Network):** Built the largest tech-driven delivery and 3PL fulfillment network in Bangladesh. Operates automated sorting hubs, regional distribution centers, and a fleet of over 3,000 delivery vehicles, serving both Mokam and third-party e-commerce merchants.
3. **Baki / Onkur (Embedded Financing):** Digital buy-now-pay-later working capital financing platform. Partnered with local commercial banks and financial institutions to disburse micro-loans backed by proprietary AI transaction scoring.

## 4. Operational Architecture: Full-Stack to Cross-Regional Synergy
- **Supply Chain Directness:** Mokam bypassed multiple wholesale tiers by sourcing directly from rice mills, oil refineries, and multinational FMCG plants (Square, Pran, Unilever Bangladesh).
- **Logistics Monetization:** Unlike pure B2B players who treat logistics as a cost center, ShopUp externalized REDX into a standalone, profitable 3PL logistics provider for the broader digital economy in Bangladesh.
- **The 2025 SILQ Merger:** Recognized that standalone B2B e-commerce in a single frontier market has valuation ceilings. Combined with Sary (Saudi Arabia) to build cross-border trade finance, commodity procurement, and digital distribution bridging the Middle East and South Asia.

## 5. Field Force & Phygital Dynamics
- **Market Captains:** Deployed thousands of field reps ("Market Captains") assigned to specific bazaar clusters. Captains onboarded store owners, assisted in daily stock planning, checked shelf availability, and collected digital payments.
- **Trust & Quality Assurance:** In bulk agricultural commodities (rice, wheat), quality variation is the #1 cause of rejection. Mokam established standardized grading and return guarantees at delivery, creating immense brand trust.

## 6. Financial Discipline & Unit Economics
- **Revenue Scale:** Grew from under $5M in 2019 to over $100M+ net revenue run rate by 2023.
- **EBITDA Pathway:** Achieved EBITDA profitability by rationalizing warehouse lease costs, automating REDX sorting hubs, and increasing the share of higher-margin private-label staples and fintech origination fees.

## 7. Strategic Relevance to POL
- **Logistics as an Asset vs Ecosystem:** ShopUp shows that if a platform builds or orchestrates proprietary logistics (REDX), it must achieve hyper-high vehicle utilization and potentially open capacity to 3PL partners to avoid logistics drag.
- **Bulk Staples Drive Volume, Branded FMCG Drives Velocity:** In developing markets, basic food staples (برنج، روغن، قند و شکر، آرد) constitute 60%+ of a grocery store's procurement budget. Mastering staples supply is critical for high GMV density.
- **Fintech Scale via Banking Partnerships:** ShopUp never lent from its own balance sheet at scale; it used bank capital (City Bank, BRAC Bank) with ShopUp providing data underwriting and first-loss default guarantees.
""",

"benchmark-chari-morocco.md": """---
id: benchmark-chari-morocco
title: "Benchmark Deep Dive: Chari (Morocco) — Francophone Africa's Regulated B2B Fintech Leader"
tags:
  - pol-b2b-benchmark-2d6747
  - benchmark-tier1
  - morocco
  - fintech-license
  - karny
created: 2026-09-03
source: "Central Bank of Morocco, TechCrunch, Orange Ventures, SPE Capital, Wamda"
tier: institutional
type: note
status: active
utility_score: 18.0
---

# Benchmark Deep Dive: Chari (Morocco)

## 1. Executive Summary & Identity
- **Company Name:** Chari (Chari.ma)
- **Country:** Morocco (Casablanca, Rabat, Marrakech, Tangier, Fes, Agadir) with pilot footprints in Francophone Africa (Tunisia, Ivory Coast, Senegal).
- **Founders:** Ismael Belkhayat (CEO, ex-BCG, serial entrepreneur), Sophia Alj (COO, ex-McKinsey).
- **Founded:** January 2020.
- **Current Status (as of 2026-09-03):** Active and uniquely positioned as a **regulated financial institution**. In **October 2025, granted a full Payment Institution License by Bank Al-Maghrib (Central Bank of Morocco)** — the first VC-backed tech startup to receive this regulatory status. Concurrently closed a $12M Series A round (October 2025) led by SPE Capital and Orange Ventures, bringing total capital raised to $17M.
- **Scale:** 30,000+ active traditional grocery stores ("hanouts"), 100+ FMCG manufacturing partners.

## 2. The Core Problem Solved
Morocco's FMCG distribution is dominated by over 200,000 neighborhood grocery shops ("hanouts") representing 80% of consumer packaged goods sales. Core challenges:
1. Hanouts spend hours daily dealing with uncoordinated distributor vans parking outside their shops.
2. 99% cash transactions, exposing shopkeepers to theft and accounting errors.
3. Hanouts act as the informal bank for the neighborhood, giving unsecured book credit ("carnet") to local families. When consumers don't pay on time, shopkeepers run out of cash to buy stock.
4. Total financial exclusion from commercial banks due to lack of tax registration and financial statements.

## 3. Product & Ecosystem Architecture: The Super-App
1. **Chari B2B E-Commerce:** Next-day delivery of FMCG goods at competitive wholesale prices with zero delivery fees.
2. **Karny (Acquired 2021):** Standalone digital credit ledger app used by hundreds of thousands of merchants across Morocco and North Africa to record customer credit debts and send automated SMS reminders.
3. **Chari Pay (Regulated Payment Institution):** Following the Oct 2025 Central Bank license:
   - Issues Moroccan IBANs and debit cards to unbanked shopkeepers.
   - Merchant POS acquiring (accepting credit cards and mobile money at the hanout).
   - Domestic and international remittance processing.
   - Utility bill collections and micro-insurance distribution.
4. **Banking-as-a-Service (BaaS):** Whitelabeling its central bank-regulated payment infrastructure to other enterprises and fintechs.

## 5. Operational Architecture: Asset-Light to Micro-Fulfillment
- **Logistics & Warehousing:** Hybrid asset-light model. Uses contracted regional transit hubs and leases micro-warehouses (dark stores) in urban centers, partnered with local 3PL van operators.
- **Inventory Turn:** Hyper-fast inventory turnover (<4 days), operating on a JIT (Just-In-Time) cross-docking arrangement with local FMCG producers (Centrale Danone, Lesieur Cristal, Procter & Gamble).

## 6. Business Model & The Regulatory Moat
- **Low Commerce Take-Rate, High Fintech Margin:**
  - Commerce gross margins: 3.5% to 5.0%.
  - Payment acquiring and bill payment MDR: 1.0% - 1.8% per transaction.
  - Merchant working capital interest and origination fees: 2.5% - 4.0% per 30-day loan cycle.
  - BaaS API licensing fees: Recurring enterprise SaaS fees.
- **Regulatory Barrier to Entry:** The Central Bank Payment Institution License requires strict compliance, audited capital reserves, and AML/KYC protocols. This creates an enormous regulatory moat that prevents generic software competitors or asset-heavy 1P clones from offering native financial services.

## 7. Anti-Disintermediation Mechanics
- **The Central Bank IBAN & Merchant Wallet:** Because Chari manages the store owner's regulated merchant account and digital IBAN, financial transactions settle seamlessly through Chari. Bypassing the app means reverting to physical cash handling and losing the legal merchant status.
- **Karny Bookkeeping Synergy:** Debts collected from consumers via Karny flow directly into the merchant's Chari wallet to pay for upcoming FMCG wholesale replenishment.

## 8. Strategic Relevance to POL
- **The Ultimate Vision for POL in Iran:** Chari demonstrates how a B2B FMCG platform can evolve from simple wholesale ordering into a **licensed financial infrastructure provider** (زیرساخت پرداخت و رگولاتوری مالی).
- **M&A of Bookkeeping Software:** Acquiring or building a free merchant credit ledger (like Karny or Easy Khata) provides an unbeatable low-CAC top-of-funnel acquisition channel.
- **BaaS (Banking-as-a-Service):** Long-term, POL can monetize its transaction data by providing risk scoring and embedded banking interfaces to Iranian banks.
""",

"benchmark-jumbotail-india.md": """---
id: benchmark-jumbotail-india
title: "Benchmark Deep Dive: Jumbotail (India) — New Retail Ecosystem, Kirana Modernization & J24"
tags:
  - pol-b2b-benchmark-2d6747
  - benchmark-tier1
  - india
  - new-retail
  - j24-franchise
  - unicorn
created: 2026-09-03
source: "SC Ventures, LiveMint, Entrackr, Economic Times, Company Announcements"
tier: institutional
type: note
status: active
utility_score: 18.0
---

# Benchmark Deep Dive: Jumbotail (India)

## 1. Executive Summary & Identity
- **Company Name:** Jumbotail Technologies
- **Country:** India (Bengaluru, Karnataka, expanding across Southern and Western India).
- **Founders:** Ashish Jhina (COO, Stanford MBA, ex-BCG), S. Karthik Venkateswaran (CEO, Stanford MBA, ex-eBay, ex-Indian Army).
- **Founded:** November 2015.
- **Current Status (as of 2026-09-03):** Active, capital-efficient unicorn. In **June 2025, raised $120M Series D funding led by SC Ventures (Standard Chartered Plc)**, officially pushing its valuation past the **$1 Billion unicorn threshold**. Concurrently acquired **Solv India** (B2B marketplace incubated by SC Ventures). In March 2026, partnered with **NEC Corporation** to deploy advanced AI retail solutions.
- **Profitability:** Reached city-level operational EBITDA profitability in mature clusters (Bengaluru).
- **Scale:** 250,000+ partner kirana stores, 2,000+ modern J24 franchise stores, 500+ FMCG brands.

## 2. The Core Problem Solved
India's $600B+ grocery retail market is 90% unorganized mom-and-pop "kiranas". Challenges:
1. Multi-layered, unorganized supply chains with high margins captured by speculative wholesalers.
2. Inability of small kiranas to compete with organized supermarket chains (Reliance Fresh, DMart) and quick-commerce dark stores (Blinkit, Zepto).
3. Cluttered, unappealing store layout and poor inventory management.
4. Working capital trap: Capital locked in slow-moving non-staple goods.

## 3. The 4-Pillar Product & Ecosystem Architecture
1. **Jumbotail B2B Marketplace:** Digital procurement platform connecting kiranas with FMCG brands and staple producers for full-catalog next-day delivery.
2. **Jumbotail Logistics Network:** Proprietary tech-driven warehousing and last-mile route-optimized delivery network guaranteeing 98%+ on-time in-full (OTIF) fulfillment.
3. **J24 Modern Retail Franchise (Retail-as-a-Service):** Transforms traditional 400-500 sq ft kirana stores into modern, branded convenience stores. Upgrades store fixtures, lighting, and layout; installs digital billing POS; and manages omnichannel inventory.
4. **GoldenEye Retail OS & Fintech:** Proprietary in-store operating system integrating billing, real-time inventory management, customer loyalty programs, and automated working capital credit lines backed by Non-Banking Financial Companies (NBFCs).

## 4. Operational Architecture: Precision & Capital Discipline
- **Disciplined Geographic Density:** Unlike Udaan, which expanded recklessly to 1,000+ cities burning billions, Jumbotail stayed laser-focused on hyper-dense geographical clusters (Karnataka, Tamil Nadu, Andhra Pradesh), achieving deep route density before expanding.
- **High-Margin Private Labels & Staples:** Built strong staples sourcing directly from agricultural processing hubs, capturing higher gross margins (8-12%) than branded packaged FMCG (3-5%).

## 5. Phygital & J24 Franchise Strategy
- **Franchise Alignment:** J24 store owners retain ownership of their physical shop and real estate while Jumbotail provides brand identity, supply chain automation, and digital POS.
- **Sales Uplift:** Converting an informal kirana to a J24 store typically results in a 30% to 50% increase in store footfall and retail revenue, creating immense loyalty and lock-in.

## 6. Financial Discipline & Strategic Moats
- **SC Ventures & Standard Chartered Integration:** The 2025 Series D and Solv India acquisition integrated Standard Chartered's institutional balance sheet directly into Jumbotail's SME lending infrastructure, providing low-cost debt facilities for kiranas.
- **Enterprise Data & AI (NEC Partnership):** Integrates NEC's computer vision and demand forecasting tools to optimize shelf placement and trade marketing for global FMCG brands.

## 7. Strategic Relevance to POL
- **Franchise Modernization as an Advanced Moat:** Jumbotail's J24 proves that helping small retailers modernize their physical stores creates an unbreakable barrier against disintermediation.
- **Geographic Density over Premature National Expansion:** Jumbotail's path to unicorn status and profitability came from dominating one regional economic cluster (South India) before horizontal expansion. POL must win Tehran/Isfahan before expanding nationally.
- **Full-Stack Operating System (GoldenEye):** When the retailer uses your software to scan barcodes, bill customers, and calculate profits, your platform becomes the indisputable **System of Record**.
""",

"benchmark-tajir-pakistan.md": """---
id: benchmark-tajir-pakistan
title: "Benchmark Deep Dive: Tajir (Pakistan) — Hyper-Lean Logistics & Kiryana Procurement"
tags:
  - pol-b2b-benchmark-2d6747
  - benchmark-tier1
  - pakistan
  - lean-operations
  - yc
created: 2026-09-03
source: "Y Combinator, Kleiner Perkins, Forbes, Menabytes, TechCrunch"
tier: institutional
type: note
status: active
utility_score: 16.5
---

# Benchmark Deep Dive: Tajir (Pakistan)

## 1. Executive Summary & Identity
- **Company Name:** Tajir
- **Country:** Pakistan (Lahore, Punjab region).
- **Founders:** Babar Khan (CEO, ex-Bain & Co), Ismail Khan (CTO, ex-Google software engineer).
- **Founded:** 2018 (graduated Y Combinator W20).
- **Current Status (as of 2026-09-03):** Active, cash-flow-disciplined market player. Raised $1.8M Seed in 2020 and $17M Series A in 2021 led by Kleiner Perkins (its first direct investment in Pakistan). Refused to engage in destructive VC-funded price wars, maintaining a highly conservative burn rate and surviving Pakistan's severe economic crisis while peers collapsed or laid off thousands.
- **Scale:** Tens of thousands of kiryana stores across Lahore and neighboring Punjab districts.

## 2. The Core Problem Solved
Small kiryanas in Pakistan faced constant stock instability. Wholesalers gave better prices to large stores and dumped near-expiry stock on small mom-and-pop retailers. Retailers lost productive selling hours negotiating at the wholesale market and hauling 50-kg sacks of flour and oil on motorcycles.

## 3. Product & Operational Model: Extreme Operational Efficiency
- **Tajir App:** Minimalist, fast, low-bandwidth Android app allowing shopkeepers to compare live prices and order across dozens of categories with guaranteed next-day delivery.
- **Tajir Express:** Dedicated last-mile delivery fleet using small, cost-efficient light commercial vehicles (pickups and three-wheelers) optimized for Lahore's congested streets.
- **Cross-Docking Focus:** Minimized warehouse storage time. Cross-docks fast-moving inventory rapidly from manufacturers and large master distributors, avoiding the heavy capital lockup of multi-week inventory holding.

## 4. Cash Flow & Macroeconomic Resilience
- **No Cash-Burning Subsidies:** Unlike competitors who burned venture capital subsidizing sugar and oil below wholesale cost to inflate GMV, Tajir insisted on selling at market prices plus a sustainable service margin.
- **Surviving the 2022-2024 Macro Shock:** When Pakistan suffered 38% inflation, massive currency devaluation, and acute import restrictions, Tajir survived with minimal layoffs because its unit economics were fundamentally sound and its overhead was lean.

## 5. Strategic Relevance to POL
- **The Virtue of Lean Capital Discipline:** Tajir demonstrates that raising hundreds of millions of dollars is not required to build a viable B2B FMCG distribution business in an emerging market.
- **Founder Background Balance:** Combining Bain strategy discipline (Babar) with Google software excellence (Ismail) created a culture of mathematical logistics optimization and zero fluff.
- **Resisting the GMV Mirage:** A critical cautionary warning for POL: GMV acquired through subsidized pricing disappears the moment subsidies end. Organic retention comes from delivery reliability and transparent availability, not unsustainable discounts.
"""
}

for filename, content in tier1_notes_part2.items():
    path = os.path.join(notes_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Written: {filename}")
