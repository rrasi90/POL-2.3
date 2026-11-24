# POL — A Multi-Vendor B2B Commerce and Supply-Chain Platform

**POL (پُل, “bridge”)** is a technology platform being built to connect independent retailers, wholesalers, distributors and FMCG suppliers through a shared digital procurement and operations network. It is designed to make everyday trade more transparent, coordinated and measurable — from product discovery and multi-vendor ordering to vendor fulfilment, delivery confirmation, invoices, support and operational reconciliation.

POL is not merely an online shop. It is a large, multi-domain commerce and supply-chain system intended to digitise the workflow between thousands of small commercial actors while preserving the role of existing wholesalers, distributors and local trade relationships.

> **Project status and evidence boundary:** POL is an actively developed software and product programme. This repository contains substantial product specifications, backend services, database migrations, web and mobile applications, design assets, tests and operational tooling. Source code, a passing test suite or a designed screen does not by itself mean the service is live, commercially deployed, legally approved or certified for a production pilot. All readiness claims must be tied to a specific commit, environment and evidence record.

- **Repository:** https://github.com/rrasi90/POL-2.3
- **Primary product domain:** FMCG and general-trade B2B wholesale procurement
- **Initial pilot context in the product documentation:** Ahvaz, Iran
- **Product language and interaction priority:** Persian-first, right-to-left (RTL), mobile-accessible
- **Primary commercial model:** asset-light, multi-vendor marketplace; POL does not own the products it lists
- **Payment boundary:** non-custodial direct settlement between commercial parties; POL is not a stored-value wallet or escrow operator

---

## 1. Why POL matters

Independent neighbourhood retailers are essential to local economies. They keep everyday products accessible near homes and workplaces, sustain small-business livelihoods, and create the last-mile retail network through which manufacturers and distributors reach consumers. Yet in many markets, their procurement still depends on fragmented supplier relationships, phone calls, paper notes, manual stock checks, opaque discounts, repeated data entry and limited visibility into order status.

These frictions have consequences beyond convenience:

- **Retailer productivity:** owners spend time calling suppliers, comparing offers, reconciling invoices and chasing deliveries instead of serving customers and managing their stores.
- **Working capital:** excess buffer stock, uncertain replenishment and limited purchasing information can tie up cash that small businesses need for wages, rent and day-to-day operations.
- **Supplier reach:** small wholesalers and regional distributors can struggle to reach retailers efficiently or receive reliable demand signals.
- **Price transparency:** inconsistent access to current offers and promotions makes it harder for independent stores to compare supply options.
- **Operational accountability:** without durable order histories, delivery evidence and traceable exceptions, disagreements over quantity, price, quality or fulfilment can be difficult to resolve.
- **Digital inclusion:** many traditional retailers are underserved by enterprise software even though they form a critical part of the consumer-goods economy.

POL is designed to address these structural problems by providing a shared digital workflow rather than trying to replace every participant in the value chain. A retailer should be able to discover products and compare supplier offers in one place. A wholesaler should be able to manage its own catalogue, prices, stock and orders. Both parties should be able to see a consistent order record, a traceable fulfilment timeline and the relevant invoice or exception evidence.

### Intended community value

If adopted successfully and operated responsibly, POL could help:

1. **Strengthen small retailers.** Reduce the administrative burden of replenishment, improve access to supplier offers and provide reliable records of purchases and deliveries.
2. **Support local wholesalers and distributors.** Give smaller suppliers a structured route to retailer demand without forcing them to build an expensive consumer-facing digital channel.
3. **Improve supply-chain efficiency.** Coordinate order consolidation, vendor allocation, stock reservation, delivery stages and exception handling.
4. **Improve price and promotion visibility.** Make current supplier offers and approved commercial terms easier to compare.
5. **Create better operational data.** Build auditable procurement histories that may support better planning and, subject to separate legal and credit-risk approval, could help eligible businesses demonstrate trading activity to financial institutions.
6. **Improve downstream availability.** More reliable replenishment may help neighbourhood stores keep essential goods available to the communities they serve.

These are **intended impact pathways, not proven POL outcomes**. POL must measure them in a real pilot before making claims about retailer income, consumer prices, stock losses, employment, market share or financial inclusion.

---

## 2. What international platforms teach us

POL is being designed in a global category with important examples across emerging markets. These cases show how digital procurement, distribution coordination, transparent pricing and transaction data can support small businesses. Their numbers are reported by the companies, investors, development institutions or public agencies named below; they are not independent evaluations of POL and should not be interpreted as causal proof.

| Platform and market | Reported model and scale | Relevant lesson for POL |
|---|---|---|
| **Cartona — Egypt** | TechCrunch reported in July 2024 that Cartona served more than 180,000 retailers, 4,500 suppliers and over 40,000 SKUs across 17 Egyptian cities. The article also reported that 30–40% of partner suppliers’ sales came through the platform, according to the founder. | Digitised ordering and supplier connectivity can become meaningful commercial infrastructure for a fragmented FMCG market. The same article also highlights the difficult economics of B2B commerce; distribution efficiency and sustainable unit economics matter as much as user growth. |
| **Twiga Foods — Kenya** | Twiga uses mobile technology and logistics to connect smallholder farmers with retailers. An IFC project assessment identifies anticipated benefits including guaranteed market off-take for smallholder farmers, improved access to supply for small vendors and lower post-harvest losses. It estimated a target of 5% losses versus 30% in traditional markets; these are anticipated project impacts, not independently measured results. | Digitisation can improve both sides of a supply chain when it is paired with reliable logistics, predictable procurement and fairer market access — not just an ordering interface. |
| **udaan — India** | udaan describes an eB2B trade platform spanning FMCG, staples, produce and other categories, with nationwide retailer and supplier networks. It also describes udaanCapital as a working-capital finance offering for small businesses. | Procurement data and supplier relationships can create a foundation for adjacent financial services, but financing should be a separately governed product with underwriting, consumer-protection and regulatory controls. |
| **TradeDepot — Nigeria and other African markets** | Novastar Ventures describes TradeDepot as connecting more than 100,000 small shops, kiosks and retailers with wholesalers and major consumer brands, with real-time pricing, routed fulfilment and embedded working-capital services. | A platform can strengthen the existing distribution chain by improving retailer access, order routing and supplier visibility instead of assuming it must own all stock and logistics assets. |
| **ONDC DigiDukaan — India** | India's Press Information Bureau reported on 30 October 2026 that DigiDukaan had connected more than 21,000 retailers with over 450 brands across Hyderabad, Jaipur and Mumbai. The government release cited 73–78% monthly repeat ordering in Hyderabad and an initial survey in which 40% of surveyed retailers reported lower inventory holdings for products procured through the initiative. | Open digital infrastructure can help digitise traditional retail procurement while strengthening existing distributor networks. The reported inventory result is an initial survey finding, not a universal or independently established causal effect. |

### What the broader development evidence says

The International Finance Corporation (IFC), part of the World Bank Group, explains that integrating traditional retailers and distributors into digital supply-chain finance networks can support SME growth and employment, improve access to finance, reduce distribution costs and potentially benefit consumers. The IFC also cautions that distribution chains are complex and that many traditional retailers still have limited access to the technology and financial services needed to participate fully.

POL takes these lessons as design hypotheses:

- Digitise the existing trade network rather than unnecessarily displacing it.
- Make the retailer workflow simple enough for busy store owners and staff.
- Make supplier operations measurable and auditable.
- Use accurate transaction data to improve coordination, not to make unsupported credit or pricing promises.
- Prove impact through pilot metrics and transparent reporting.

### Research sources

- [Cartona — TechCrunch, 30 July 2024](https://techcrunch.com/2024/07/30/egypts-cartona-raises-8-1m-even-as-investors-pull-back-from-b2b-e-commerce-in-africa/)
- - [Twiga Foods — IFC project disclosure](https://disclosures.ifc.org/project-detail/SII/41195/twiga-foods)
- [udaan — About the company](https://udaan.com/about-us)
- [TradeDepot — Novastar Ventures portfolio profile](https://www.novastarventures.com/companies/tradedepot/)
- [ONDC DigiDukaan — Government of India Press Information Bureau, 30 October 2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2330634&lang=1&reg=3)
- [IFC — Technology and Digitization in Supply-Chain Finance Handbook](https://www.ifc.org/en/insights-reports/2020/digitization-scf-handbook)

---

## 3. Product model and principal users

POL is a multi-vendor B2B marketplace. It does not take ownership of the products listed by vendors. A retailer creates one purchasing intent; the platform evaluates eligible vendor offers and allocates the basket into vendor-specific commitments.

### User groups

| User group | Main jobs in POL |
|---|---|
| **Retailer owner** | Discover products, compare vendor offers, build a basket, submit orders, review vendor allocations, follow delivery, confirm receipt, view invoices and contact support. |
| **Retailer staff** | Perform authorised purchasing, receiving and store operations within delegated permissions. |
| **Vendor owner** | Manage the business profile, catalogue, prices, inventory, staff permissions, customer relationships and fulfilment operations. |
| **Vendor staff** | Review assigned orders, update inventory, prepare orders, dispatch deliveries and handle operational tasks within granted permissions. |
| **Field activator** | Support retailer onboarding, verify store details, record visits and help retailers complete initial workflows. |
| **Operations and administrators** | Govern catalogue quality, manage users and organisations, monitor exceptions, review support cases, oversee platform controls and audit sensitive actions. |
| **Background workers** | Process durable outbox events, notification delivery, reconciliation, reservation expiry, retention and scheduled operational tasks. |

### Commercial model

- POL operates as an asset-light platform and does not need to own the inventory listed by suppliers.
- Vendors remain responsible for their product offers, prices, stock and fulfilment commitments.
- The retailer sees one unified shopping and checkout journey, while the platform creates vendor-specific child orders according to the approved allocation model.
- Payment, invoice, refund and settlement records are coordinated and made visible according to the commercial contract between the parties.
- POL does not operate a stored-value wallet, hold customer money or promise escrow-like settlement guarantees in the MVP.
- Credit, BNPL, wallet, advertising and advanced loyalty features are not part of the current MVP unless formally approved through the project decision process.

---

### Vision, ecosystem and long-term scale

POL's starting wedge is FMCG procurement for independent neighbourhood retailers in a dense local cluster in Ahvaz, Iran. The long-term direction is a multi-city, multi-category and potentially multi-market B2B commerce network—but expansion should follow local retailer density, reliable supply, regulatory feasibility and positive unit economics, not a calendar-only rollout.

The opportunity is not simply to put a wholesaler catalogue online. It is to make fragmented offline distribution more discoverable, measurable and dependable while allowing retailers, wholesalers, regional distributors, local carriers and manufacturers to keep performing the roles they are best equipped to perform. POL is intended to be the software, transaction-coordination, data and trust layer—not an inventory-owning wholesaler.

**How the marketplace works**

1. **Retailers create demand:** an owner or authorised staff member discovers products and vendor offers, compares price and availability, builds one basket and confirms an allocation.
2. **Wholesalers fulfil supply:** each vendor controls its offers, prices and inventory, accepts or partially accepts its allocated order, prepares the goods and provides dispatch information.
3. **POL coordinates the transaction:** the platform manages discovery, basket allocation, order state, notification, evidence, exceptions, support and reconciliation. One retailer basket can produce several vendor-specific orders.
4. **The supply network performs delivery:** the wholesaler's vehicle or an agreed third-party logistics provider (3PL) handles physical delivery. POL coordinates and tracks the workflow without needing to own warehouses or a fleet.
5. **Settlement remains direct:** the initial non-custodial model keeps payment between retailer and the relevant wholesaler. POL records evidence and supports reconciliation; it is not a wallet or custodian of customer funds.

The governing principle is **digitise and strengthen the existing trade network, not disintermediate it**. Retailers should gain better procurement and visibility; wholesalers should gain lower order-acquisition friction, more demand and better operating information.

**Stakeholder ecosystem and value exchange**

| Stakeholder | Role | Intended value from POL | Boundary |
|---|---|---|---|
| Independent retailers, supermarkets and local shops | Demand-side buyers | Compare vendor offers, place multi-vendor orders, reorder, track fulfilment, document discrepancies and maintain purchase history | Remain independent businesses and buy from the relevant vendors |
| Wholesalers, distributors and regional stockists | Initial supply-side sellers | Digital storefront, product/price/stock management, order intake, fewer manual errors, retailer demand, fulfilment coordination and reporting | Retain ownership of goods, inventory, prices and fulfilment commitments |
| Manufacturers and consumer brands | Upstream supply and future intelligence partners | Later-stage product availability signals, regional sell-out visibility, campaign measurement and trade promotions | Direct manufacturer-to-retailer selling is not the initial model; local wholesalers remain fulfilment partners |
| Local carriers, drivers and 3PL operators | Physical delivery capacity | Structured dispatch, pickup/drop information, status, proof of delivery and clearer exception handling | Provide physical delivery under agreed commercial terms; delivery is not assumed to be cost-free |
| Banks, payment providers and licensed fintech partners | Regulated payment and future finance infrastructure | Structured transaction evidence, reconciliation interfaces and possibly partner-led credit origination | POL does not lend from its own balance sheet or assume bank credit risk |
| Field activators and local commercial teams | Trust-building and onboarding | Retailer/vendor mapping, assisted onboarding, catalogue verification, training and first-order support | Assisted onboarding should move users toward self-service, not become a permanent substitute for usable software |
| POS, ERP, accounting and technology partners | Integration ecosystem | Product identifiers, invoice exchange, inventory synchronisation and interoperability | Use documented APIs and permissioned data; do not create a competing source of truth |
| Platform operations and support | Neutral network operator | Catalogue governance, SLA monitoring, dispute handling, abuse review, reconciliation and auditability | Decisions must be traceable, role-based and consistent |
| End consumers | Indirect beneficiaries | Potentially better product availability and more reliable neighbourhood replenishment | Not the initial transacting customer of the B2B platform |

**Manufacturer relationship: a three-party model**

Manufacturers and brands are strategically important, but they are not the first customer segment in the Ahvaz MVP. Early direct-to-retailer manufacturer sales could make wholesalers perceive POL as a channel designed to remove them, weakening the supply side before the network has earned trust.

The intended later-stage model is:
- Manufacturers provide products, brand programmes, trade promotions and upstream supply.
- Participating wholesalers remain the local commercial and fulfilment partners, holding stock where appropriate and serving retailers through established local operations.
- POL provides digital demand signals, transaction coordination, campaign measurement and aggregated market intelligence.

Clearly labelled sponsored campaigns, co-funded promotions, product sampling and aggregated dashboards are roadmap opportunities—not claims that advertising or a manufacturer dashboard is already live. Manufacturer entry should follow meaningful retailer density (existing strategy documents use approximately 500–1,000 active retailers as a planning threshold), protected wholesaler participation and lawful data permissions. Paid placement must never distort organic vendor reliability, fulfilment scores or best-value allocation.

**Revenue model and unit economics**

The monetisation plan is staged and remains subject to field validation, commercial contracts and regulatory review.

| Horizon | Revenue stream | Working assumption | Readiness condition |
|---|---|---|---|
| Pilot | No platform commission | 0% during the documented three-month pilot | Measure adoption, repeat orders, service cost, fulfilment quality and vendor value |
| Post-pilot marketplace | Transaction commission | Category-sensitive 1%–3% working range; approximately 2% blended hypothesis | Validate retailer savings, vendor economics, contribution per completed order and collection mechanics |
| Network expansion | Optional vendor SaaS | Subscription for advanced inventory, staff, reporting and workflow tools | Demonstrable recurring software value beyond access to orders |
| Mature network | Manufacturer trade marketing / retail media | Disclosed sponsored campaigns and co-funded promotions | Retailer density, campaign measurement and separation from organic ranking |
| Mature network | Market intelligence | Aggregated and privacy-protected analytics for brands/suppliers | Data quality, lawful basis, consent/contract rights and aggregation safeguards |
| Partner-led finance phase | Credit referral or embedded-finance fees | Fees shared with regulated banking/lending partners | Transaction history, partner underwriting, legal approval and explicit user consent |

Asset-light does not mean the supply chain has no costs. Goods, storage, delivery, payment processing, returns and customer support all cost money. The design goal is to keep inventory ownership, warehouse capital, fleet ownership and lending risk outside POL's balance sheet while transparently recording costs borne by vendors, retailers and delivery partners.

Working business-model assumptions—including take-rate hypotheses, average order value (AOV) and cost-to-serve scenarios—are documented in:
- `05_BUSINESS_MODEL/Business_Model_and_Unit_Economics.md`
- `05_BUSINESS_MODEL/Revenue_Model.md`
- `05_BUSINESS_MODEL/Commission_Model.md`
- `05_BUSINESS_MODEL/Vendor_Economics.md`

These documents distinguish hypotheses from field observations. A spreadsheet assumption is not a realised financial result until supported by reconciled transactions.

**Long-term financial ambition**

The long-term strategic ambition is **US$100 million in annual recognised platform revenue**, with **US$300 million as a stretch scenario**. These are aspirations—not a forecast, valuation, fundraising claim or current run-rate. No achievement date should be promised before pilot retention, contribution margin and expansion economics are demonstrated.

Keep the financial measures distinct:
- **GMV:** value of goods ordered through the network.
- **Platform revenue:** commission and other revenue recognised by POL.
- **Contribution:** platform revenue less variable cost of serving the transaction.
- **Net profit:** what remains after the full operating, financing, tax and other costs.

At a 2% blended transaction take rate, transaction-only revenue of US$100 million would require approximately **US$5 billion in annual GMV**; US$300 million would require about **US$15 billion**. These are arithmetic scenarios, not predictions. SaaS, trade marketing and partner services must not be counted until launched, contracted and measured.

**International financial scale reference points**

Indian B2B commerce businesses show that large trade networks can reach several-hundred-million-dollar reported revenue scale. They are not direct financial comparables to POL's planned commission-led, non-custodial model.

| Company | FY / measure | Reported result | Approximate USD equivalent | Context |
|---|---|---:|---:|---|
| Udaan | FY2025 operating revenue | ₹4,561.4 crore | ~US$491m | Reported FY2025 net loss of ₹1,055.4 crore; the company refocused on essentials and FMCG |
| ElasticRun | FY2025 operating revenue | ₹2,653 crore | ~US$286m | Reported FY2025 net loss of ~₹145.1 crore; reporting described a focus on regional brands, private labels and improving gross margin |
| Jumbotail + Solv | Network reach announced June 2025 | 500,000+ kiranas and MSMEs served, according to the company | Not a revenue figure | A reach metric, not 500,000 monthly active or transacting stores |

*Approximate currency conversion uses ₹92.93 per US dollar on 24 November 2026; INR amounts remain the source figures. Udaan and ElasticRun have operated models that include product sales, distribution, logistics and other services. Their reported operating revenue may include gross/product-sale components that POL would not recognise as net commission revenue. Their reported losses also show why scale alone is not a success metric.*

Sources: [Udaan FY2025 results — ET Retail](https://retail.economictimes.indiatimes.com/amp/news/e-commerce/e-tailing/udaans-fy25-losses-narrow-to-1055-cr-revenue-at-4561-cr/128148547); [ElasticRun FY2025 results — Business Standard](https://www.business-standard.com/companies/news/elasticrun-fy25-loss-narrows-revenue-grows-private-labels-logistics-125112000736_1.html); [Jumbotail / Solv June 2025 announcement](https://jumbotail.com/jumbotail-raises-120m-series-d-funding/); [USD/INR historical rate, 24 November 2026 — Wise](https://wise.com/us/currency-converter/usd-to-inr-rate/history/24-11-2026).

**Growth sequence and measurable gates**

1. **Ahvaz beachhead:** recruit committed wholesalers, activate a dense retailer cluster and validate completed orders, repeat behaviour, price competitiveness, fulfilment, discrepancies and cost-to-serve. The initial three-month pilot is documented as commission-free.
2. **Khuzestan cluster expansion:** expand only after repeat ordering, reliable vendor acceptance, predictable fulfilment and positive or clearly improving contribution per completed order.
3. **Adjacent city clusters:** use local wholesaler and 3PL partnerships rather than importing a warehouse-and-fleet cost base.
4. **Manufacturer and brand layer:** introduce trade marketing and aggregated insights only after sufficient active retailer coverage and trusted wholesaler participation.
5. **Partner finance and broader markets:** consider regulated partner-led finance and new geographies only with reliable transaction history, governance and sustainable unit economics.

Working acquisition goals in planning documents include 10 wholesaler design partners, an initial 25 pilot retailers and a 200-retailer year-one ambition. These are **planning targets, not achieved traction**. Success measures should prioritise completed and fulfilled orders, active/repeat retailers, active vendors, GMV and recognised revenue, contribution per order, retailer and wholesaler economics, fill rate, on-time delivery, cancellations, discrepancies, disputes, CAC payback and concentration risk. High GMV with poor retention, heavy subsidies or negative contribution is not a healthy marketplace.

**Strategic non-goals**

To preserve focus and capital discipline, POL is not intended to:
- Buy and resell inventory as its default operating model.
- Build or own a large warehouse network or delivery fleet.
- Replace wholesalers with direct manufacturer-to-shop distribution in the initial market.
- Finance retailer/wholesaler credit from POL's own balance sheet.
- Sell identifiable retailer, vendor or consumer data.
- Optimise GMV at the expense of contribution, trust, fulfilment or retention.
- Add AI features merely for marketing; each must solve a measured user or operational problem.

## 4. Product design and application areas

The product is designed as a set of connected workspaces sharing the same product, order, identity and permission contracts. Each surface has a distinct operational purpose; the design should not force every user into the same dashboard.

### A. Public website and acquisition experience

The public site introduces POL to retailers, wholesalers, partners and other stakeholders. Its intended areas include:

- **Home:** clear explanation of the platform, its value proposition, product categories and entry points for retailer and vendor onboarding.
- **Retailer landing page:** how to source products, compare offers, place multi-vendor orders and track fulfilment.
- **Vendor landing page:** how to publish offers, manage stock, receive orders and serve more retailers through a digital channel.
- **How it works:** a clear workflow from account creation through purchasing, allocation, fulfilment and delivery.
- **Pilot information:** pilot geography, operating principles and contact details without overstating launch readiness.
- **Legal and commercial terms:** platform boundaries, data/privacy statements and clear non-custodial payment language.
- **Contact and support:** structured contact and support request pathways.

### B. Identity and authentication

The sign-in experience is mobile-first and based on phone verification.

- Phone-number entry with E.164 normalisation.
- Exactly **six ASCII numeric digits** for login and registration OTP under D-018.
- Persian and Arabic numeral input should be normalised safely to ASCII before API submission.
- Six-digit code entry supports paste and operating-system one-time-code autofill.
- Clear expiry and resend timing, validation errors, loading states and recovery paths.
- Authentication must be enforced by the server and active organisation membership, not by client-side role selection.
- The six-digit requirement does not change the existing D-018 TTL, resend interval, rate limit, attempt cap, lockout or token lifetimes.

### C. Retailer workspace — web and Android

The retailer workspace is designed around the shortest correct replenishment journey:

**Discover → Compare → Add → Review → Confirm → Track → Receive**

Principal areas include:

1. **Retailer home:** recently ordered items, categories, frequently purchased products, important order status and clear next actions.
2. **Catalogue and search:** Persian-first product names, category navigation, brand and barcode information, product images and search.
3. **Vendor offers:** supplier-specific price, unit/packaging, minimum order quantity, available stock and vendor information.
4. **Unified basket:** one basket across multiple vendors, quantity editing, price visibility and validation before checkout.
5. **Allocation and checkout review:** vendor grouping, minimum-order validation, stock revalidation, delivery information and final confirmation.
6. **Order group and child orders:** a single parent transaction with vendor-specific orders, supplier-level invoices and independent fulfilment status.
7. **Order timeline:** submitted, accepted, preparing, ready, dispatched, picked up, in transit, arrived and terminal delivery/exception states where applicable.
8. **Delivery and proof of delivery:** recipient confirmation, delivery OTP, item quantities, damage/shortage reporting and evidence capture.
9. **Invoices and financial activity:** invoices, payments, refunds and order-linked settlement visibility; this is not a wallet balance.
10. **Support, dispute and RMA:** issue reporting, evidence, case history and resolution status.
11. **Notifications and inbox:** durable order and operational messages with read/unread state.
12. **Profile and organisation context:** user identity, active organisation, permitted memberships and delegated capabilities.

### D. Vendor workspace — web and Android

The vendor workspace is an operational control centre for the wholesaler, designed to reduce missed orders and improve daily execution.

- **Vendor dashboard:** actionable counts for new orders, fulfilment work, stock exceptions and tasks.
- **Order inbox:** new orders, order details, accept/reject decisions and permitted partial acceptance.
- **Preparation and fulfilment:** picking/packing tasks, ready status, dispatch information, delivery progression and proof-of-delivery visibility.
- **Catalogue:** vendor product mapping, product information, catalogue candidates and media provenance.
- **Pricing:** vendor-specific price maintenance, price history and approved commercial terms.
- **Inventory:** physical, reserved and available stock, daily inventory confirmation, stale-data alerts and audit history.
- **Customer and staff management:** retailer relationships, vendor staff and role-scoped delegated permissions.
- **Invoices and settlements:** order-linked invoice records, payment evidence and authorised settlement information.
- **Referral and acquisition:** vendor referral attribution where enabled by the approved MVP model.
- **Support and exceptions:** damaged goods, shortages, order issues and support-case follow-up.

### E. Operations, administration and field activation

Platform operations require a different interface from a retailer or vendor. These surfaces focus on governance, consistency and exception resolution.

- Organisation and membership management, role assignment and delegated permissions.
- Tenant-scoped catalogue governance and product-candidate review.
- Vendor and retailer onboarding oversight.
- Support queues, dispute and RMA review, and case assignment.
- Operational task and field-activation management.
- Audit trails for sensitive actions and permission changes.
- Monitoring of outbox, notifications, worker state, migration and integration health.
- Exception reporting for inventory, fulfilment, order and financial reconciliation.

Protected operations must be enforced by the server with organisation-scoped permissions and deny-by-default behavior.

### F. Shared design system and UX principles

The design direction is a practical, high-density commerce interface rather than a decorative consumer shopping experience.

- **Persian-first RTL:** layout, alignment, number handling, dates, prices and mixed Persian/Latin identifiers must be tested.
- **Responsive web and mobile:** the same product capabilities should be available on both clients where the approved permission and screen matrix requires parity.
- **Light and Night themes:** common tokens and reusable components should keep visual behavior consistent.
- **Accessibility:** meaningful labels, visible focus, keyboard support, contrast, screen-reader semantics and touch targets appropriate for real shop use.
- **Self-hosted Persian typography:** the web app bundles the same Vazirmatn Regular, SemiBold and Bold font assets used by mobile and loads them locally at build time; builds do not need to fetch Google Fonts.
- **Progressive disclosure:** show the decision-critical information first; reveal detailed operational data only when needed.
- **State fidelity:** every major workflow must account for loading, empty, error, offline, expired, disabled, permission-denied, retry and success states.
- **Commercial clarity:** price, unit, quantity, MOQ, vendor, delivery and order state must be visible before confirmation.
- **Truthful UI:** the interface must not promise inventory, credit, payment or delivery capabilities that have not been approved and implemented.
- **Reusable components:** catalogue cards, offer rows, quantity controls, order state indicators, timelines, forms, tables, modals, banners and exception views should use shared contracts and design tokens.

The screen matrix and visual QA records are the authoritative guides for scope and verification. Older screenshots or historic “PASS” labels must not be treated as proof of the current screen after a material design or policy amendment.

---

## 5. Core domain and workflow architecture

The canonical commercial entity hierarchy is:

**Basket → AllocationPlan → OrderGroup → Order → OrderItem**

- The **Basket** captures retailer demand before a commercial commitment exists.
- The **AllocationPlan** distributes requested products across eligible vendors under the approved allocation rules.
- The **OrderGroup** represents the parent retailer transaction.
- Each **Order** is a vendor-specific commitment with its own acceptance, fulfilment and exception lifecycle.
- Each **OrderItem** tracks the product, quantity and fulfilment detail at the lowest commercial unit.

The high-level request and event flow is:

    Web / Android clients
            |
            v
    FastAPI HTTP transport
            |
            v
    Authentication and active tenant context
            |
            v
    POL application boundary
            |
            v
    Canonical Python domain services
            |
            v
    PostgreSQL transaction
            |
            +----> transactional outbox events
                         |
                         v
                 Python background workers
                         |
              +----------+-----------+
              |          |           |
              v          v           v
          Notifications  Reconciliation  Scheduled jobs

Key engineering principles:

1. PostgreSQL is the canonical database; schema changes are ordered and forward-only.
2. Tenant and membership boundaries are security invariants, not UI-only conventions.
3. The application boundary is the authoritative route into business operations.
4. Business-state changes and outbox events must remain transactionally consistent.
5. External SMS, push and object-storage providers remain behind adapters.
6. Idempotency, constraints, concurrency control and audit records protect sensitive workflows.
7. A test result applies only to the exact code SHA and environment recorded with its evidence.

---

## 6. Technology stack

| Layer | Technology |
|---|---|
| Backend runtime | Python 3.11 |
| HTTP API | FastAPI and Uvicorn |
| Database | PostgreSQL 18 |
| Database driver | psycopg2 |
| Web | Next.js 15, React 19, TypeScript |
| Styling and state | Tailwind CSS, Zustand, shared POL UI packages |
| Mobile | Expo / React Native |
| JavaScript runtime in CI and development | Node.js 22 |
| Backend tests | pytest and repository verification scripts |
| Browser E2E | Playwright |
| Data persistence and async events | PostgreSQL transactional outbox and Python workers |
| Media | S3-compatible object storage adapter |
| Deployment | Docker Compose and Nginx |

Provider adapters, mobile SDK versions and package versions must remain aligned with the committed lockfiles and canonical environment documentation. Do not independently upgrade core Expo, React Native or React dependencies without a compatibility review.

---

## 7. Repository scale and organisation

POL is a large product-engineering repository, not a single-page application or a small API sample. It combines software, product design, commercial rules, data governance, operational workflows, tests, deployment and agent execution guidance.

A Git-tree snapshot taken on 24 November 2026, before this six-digit OTP amendment, contained:

- **964 tracked files** across source, tests, design, specifications, operations and evidence.
- **More than 200 Python files** covering API, domain services, workers, migrations support and verification.
- **More than 130 TypeScript / TSX files** across the web application, mobile application and shared packages.
- **76 numbered PostgreSQL migrations** on the mainline baseline before the proposed migration 077 in the OTP feature branch.
- Multiple product workspaces, shared packages, design-system assets, integration ledgers and CI workflows.

These figures describe the size of the repository snapshot, not the number of deployed services, active customers, production transactions or employees.

### Repository map

    POL-2.3/
    ├── .github/workflows/           # GitHub Actions verification and release gates
    ├── .agents/                     # Agent rules and execution skills
    ├── 00_PROJECT_OVERVIEW/         # Product and project overview
    ├── 01_RESEARCH/                 # Market and product research
    ├── 02_STRATEGY/                 # Strategy
    ├── 03_CUSTOMERS/                # Customer and segment knowledge
    ├── 04_VALUE_PROPOSITION/        # Value proposition
    ├── 05_BUSINESS_MODEL/           # Business model
    ├── 06_PRODUCT/                  # Product scope, API and architecture contracts
    ├── 07_ALGORITHMS/               # Allocation and domain algorithms
    ├── 08_DATA/                     # Data models and schema documentation
    ├── 09_OPERATIONS/               # Fulfilment and operational processes
    ├── 10_GO_TO_MARKET/             # Onboarding and acquisition
    ├── 11_PILOT/                    # Pilot strategy and metrics
    ├── 12_ROADMAP/                  # Roadmap
    ├── 13_PRODUCT_DESIGN/           # Master UX tree, design specs and visual QA
    ├── POL_00_PROJECT_CONTROL/      # Canonical decisions and source of truth
    ├── analysis/integration/        # Branch, PR, test and release evidence
    ├── migrations/                  # Ordered PostgreSQL migrations
    ├── scripts/
    │   ├── api/                     # FastAPI application and routes
    │   └── ...                      # Domain services, workers, tests and tooling
    ├── mvp/
    │   ├── apps/
    │   │   ├── web/                 # Next.js web workspace
    │   │   └── mobile/              # Expo / React Native workspace
    │   ├── packages/                # Shared API client, config, types, tokens and UI
    │   ├── BUILD_PLAN.md
    │   ├── MVP_API_MAP.md
    │   ├── MVP_KNOWN_GAPS.md
    │   └── MVP_SCREEN_MATRIX.md
    ├── deploy/                      # Docker, Nginx and self-hosted deployment files
    ├── docker-compose.vps.yml
    ├── requirements.txt
    └── requirements-dev.txt

### Recommended reading order

| Need | Start here |
|---|---|
| Product and system overview | POL_00_PROJECT_CONTROL/MASTER_SYSTEM_ARCHITECTURE.md |
| Governing product decisions | POL_00_PROJECT_CONTROL/DECISION_REGISTER.md |
| Current source-of-truth hierarchy | POL_00_PROJECT_CONTROL/CURRENT_SOURCE_OF_TRUTH.md |
| Database schema and migration status | POL_00_PROJECT_CONTROL/DATABASE_SCHEMA_MANIFEST.md and migrations/ |
| API application boundary | POL_00_PROJECT_CONTROL/API_APPLICATION_BOUNDARY.md |
| MVP implementation and build plan | mvp/BUILD_PLAN.md |
| Screen inventory | mvp/MVP_SCREEN_MATRIX.md |
| API contract map | mvp/MVP_API_MAP.md |
| Known gaps and blockers | mvp/MVP_KNOWN_GAPS.md |
| Integration and release evidence | analysis/integration/PR_INVENTORY.md, BRANCH_INVENTORY.md, TEST_EVIDENCE_INDEX.md and RELEASE_READINESS.md |

When documents disagree, the canonical decision register and current source-of-truth hierarchy take precedence. Historical audit material is dated evidence, not a new product requirement.

---

## 8. Getting started

### Prerequisites

- Python 3.11
- Node.js 22.13 or later and npm
- PostgreSQL 18
- Git
- Docker and Docker Compose for containerised services
- Playwright browser binaries for browser E2E checks

### Install Python dependencies

From the repository root:

    python -m venv .venv

Activate the environment:

    # macOS / Linux
    source .venv/bin/activate

    # Windows PowerShell
    .venv\Scripts\Activate.ps1

Install dependencies:

    python -m pip install --upgrade pip
    python -m pip install -r requirements-dev.txt

### Install JavaScript workspaces

From the monorepo root:

    cd mvp
    npm ci

Use the committed package lockfile. Do not install a newer version ad hoc or update package versions to work around a failing command.

### Backend API

The FastAPI application is exposed from scripts.api.main:app.

Configure an isolated PostgreSQL database and the required environment variables. Configuration includes:

- POL_API_DB_NAME
- POL_API_DB_HOST
- POL_API_DB_PORT
- POL_API_DB_USER
- POL_API_DB_PASSWORD
- POL_API_DB_SSLMODE
- POL_JWT_SECRET
- POL_CORS_ORIGINS
- ENVIRONMENT

Start the API from the repository root:

    uvicorn scripts.api.main:app --host 127.0.0.1 --port 8000

Non-production environments expose OpenAPI documentation at /docs and /openapi.json. Health and readiness endpoints are:

- GET /healthz — process health.
- GET /readyz — readiness check, including the database connection.

A healthy process is not necessarily a ready application; readiness requires the dependencies expected by the endpoint.

### Background worker

The canonical asynchronous worker entry point is:

    python -m scripts.worker_runtime

It requires production-mode configuration and a valid database/provider environment. Start it only when the intended worker services and credentials are configured; an API process being healthy does not prove the worker is running.

### Web application

From the repository root:

    cd mvp
    npm run dev --workspace=@pol/web

Common web checks:

    npm run typecheck --workspace=@pol/web
    npm run lint --workspace=@pol/web
    npm run build --workspace=@pol/web
    npm run test:e2e --workspace=@pol/web

### Mobile applications

The mobile workspace includes separate retailer and vendor entry points:

- mvp/apps/mobile/AppRetailer.tsx
- mvp/apps/mobile/AppVendor.tsx

Start Expo from mvp/:

    npm start --workspace=@pol/mobile

Mobile QA commands from mvp/:

    npm run typecheck --workspace=@pol/mobile
    npm run qa:functional --workspace=@pol/mobile
    npm run qa:regression --workspace=@pol/mobile
    npm run qa:mock --workspace=@pol/mobile
    npm run qa:pre-apk --workspace=@pol/mobile

Physical-device installation, camera/barcode behaviour, release signing and production endpoint configuration are separate acceptance gates. A mock QA pass is not proof of live-provider or device acceptance.

---

## 9. Database, migrations and OTP policy

### PostgreSQL migrations

The mainline baseline used for the 24 November 2026 audit contained a contiguous numbered chain from 001 through 076. This OTP amendment proposes migration 077 on the dedicated feature branch. Do not treat 077 as part of main until that branch is reviewed and merged.

Migration changes are forward-only. Historical migration files should not be rewritten to change already-applied schema history.

**Critical safety rule:** scripts/migration_runner.py is a destructive test-database tool. It resets the public schema in its selected test database before applying the chain. Use it only against an isolated, disposable database such as pol_test. Never run it against shared, staging or production data.

For deployment-oriented migrations, use the guarded production migration path documented in deploy/VPS_DEPLOYMENT.md and the repository's migration operations guide. Do not use test reset scripts as a production deployment mechanism.

### Authentication OTP — D-018

The superseding founder instruction recorded on 24 November 2026 sets the authentication OTP contract to:

- Exactly six ASCII numeric digits; preserve leading zeroes.
- 120-second validity.
- 60-second resend interval.
- Maximum 3 requests per 5 minutes per phone number and IP.
- Maximum 5 verification attempts per challenge.
- 10-minute phone lockout after 5 failed attempts.
- 15-minute access-token lifetime.
- 30-day refresh-session lifetime.
- Refresh-token rotation remains an explicitly undecided policy item; do not infer product policy from current implementation behaviour.

### Delivery / proof-of-delivery OTP — D-029

Newly issued delivery/POD codes are also six digits but are a separate domain capability:

- Generated with a cryptographically secure random source.
- Bound to one delivery and delivered only to the authorised retailer recipient through the existing inbox/outbox event.
- Single-use and checked against the correct delivery and tenant.
- Governed by the delivery lifecycle and attempt accounting, not by automatically copying login TTL or lockout rules from D-018.
- Never returned in the vendor dispatch response or exposed in logs.

**Legacy in-flight compatibility:** a delivery code issued as four digits before migration 077 may remain valid for that original in-flight delivery until it reaches a terminal state. Migration 077 records the actual stored code length without rotating, clearing or re-sending it. This is a temporary data-compatibility exception, not permission to issue new four-digit codes. New authentication and delivery codes are six digits.

---

## 10. Automated verification

Verification results apply only to the exact tested SHA and environment. Run the relevant checks for each changed surface and retain the logs and generated artifacts.

### Backend suite

With an isolated PostgreSQL 18 test database and the required CI-style environment:

    python scripts/migration_runner.py
    python scripts/verify_environment.py --json
    python scripts/run_verification_suite.py

The migration runner is destructive to its target test database. Verify the configured target before running it.

### Web suite

From mvp/ after npm ci:

    npm run typecheck --workspace=@pol/web
    npm run lint --workspace=@pol/web
    npm run build --workspace=@pol/web
    npm run test:e2e --workspace=@pol/web

### Browser E2E

From mvp/apps/web/:

    npx playwright install chromium
    npx playwright test

Use the repository's Playwright configuration and the documented API/web test setup. Do not replace an API-integrated E2E test with a mock-only test and report it as equivalent.

### Mobile suite

From mvp/:

    npm run typecheck --workspace=@pol/mobile
    npm run qa:functional --workspace=@pol/mobile
    npm run qa:regression --workspace=@pol/mobile
    npm run qa:mock --workspace=@pol/mobile
    npm run qa:pre-apk --workspace=@pol/mobile

The pre-APK gate is fail-closed and must not be bypassed. APK creation, emulator validation and physical-device testing are distinct evidence.

### CI evidence

The repository's main verification workflow runs the Python verification suite, migration chain and environment verifier, and uploads SHA-specific evidence such as:

- artifacts/pol-test-results.json
- artifacts/failure_inventory.txt
- a final certification JSON containing the tested commit and workflow run

Review the executed job steps, actual test totals, skipped count, tested SHA and artifact upload. A workflow that fails before runner steps does not constitute an executed test failure or a successful test pass.

**Pre-amendment baseline:** the main branch's 24 November 2026 independent verification run reported 849 passed, 0 failed and 0 skipped on SHA f4ac2b81948b0ee1f1221b541783e152b3e3a41a. That run predates the six-digit OTP changes. It is baseline evidence only and does not certify this feature branch.

---

## 11. Configuration and secrets

Use .env.vps.example as a reference for self-hosted configuration. It contains placeholders, not working credentials.

Configuration categories include:

| Category | Examples |
|---|---|
| Runtime | ENVIRONMENT |
| Database | POL_DB_USER, POL_DB_PASSWORD, POL_API_DB_*, POL_PG_DSN |
| Authentication | POL_JWT_SECRET |
| Web/API | NEXT_PUBLIC_API_BASE_URL, POL_CORS_ORIGINS |
| Object storage | POL_S3_ENDPOINT_URL, POL_S3_ACCESS_KEY_ID, POL_S3_SECRET_ACCESS_KEY, POL_S3_BUCKET |
| SMS | POL_SMS_PROVIDER and provider-specific environment variables |
| Push | Provider adapter endpoint and token environment variables |
| Workers | POL_WORKER_INTERVAL_SECONDS, POL_WORKER_BATCH_SIZE |

Keep real credentials in an authorised secret manager or deployment environment. Never commit secrets, paste production credentials into issue reports, or include tokens, OTP values, private user data or full payment evidence in logs, screenshots or generated artifacts.

---

## 12. Deployment and operations

The repository contains a self-hosted Docker Compose deployment model including:

- PostgreSQL 18
- One-shot migration service
- FastAPI application
- Python background worker
- Next.js web application
- Nginx reverse proxy

The primary deployment definition is docker-compose.vps.yml. Read deploy/VPS_DEPLOYMENT.md and inspect the target environment before deploying.

Validate configuration:

    docker compose --env-file .env -f docker-compose.vps.yml config

The deployment script is:

    bash deploy/vps_deploy.sh

A successful Compose validation is not a production deployment, and a successful container start is not a complete pilot-readiness assessment. Production launch requires backup/restore validation, secret management, monitoring, domain/TLS, provider acceptance, security checks, operational runbooks, support coverage and a successful staging smoke test on the exact release SHA.

---

## 13. Security, privacy and trust boundaries

- Authentication and authorisation are server-side. Client-side role selection is never an authorisation boundary.
- User data and commercial records are tenant-scoped to active organisation membership.
- Sensitive actions require explicit permission and auditable state transitions.
- OTPs, tokens, passwords, provider secrets and unnecessary personal data must not be logged.
- Delivery OTPs are recipient-only, single-use and bound to the intended delivery.
- File uploads require authorised target binding, media provenance, validation and controlled access.
- Payment and settlement records do not mean that POL holds customer funds.
- Mock or QA deployments must be isolated from production data, credentials, cookies and APIs.
- Destructive tests and migration resets must run only against disposable databases.
- Security-sensitive changes require code review and fresh evidence; do not weaken tests to obtain a green workflow.

---

## 14. Social impact measurement

POL should report measured outcomes, not just registrations or gross merchandise value. A credible pilot should track, where data collection is lawful and proportionate:

| Impact area | Possible measures |
|---|---|
| Retailer productivity | Median time to place a replenishment order, repeat-order rate, support contacts per order |
| Procurement quality | Price visibility, fill rate, order acceptance rate, supplier offer coverage |
| Inventory and working capital | Stock-out frequency, days of inventory held, cancellations due to unavailable stock |
| Fulfilment reliability | On-time delivery, first-attempt completion, quantity discrepancies and proof-of-delivery disputes |
| Supplier inclusion | Active local wholesalers, regional suppliers onboarded, share of suppliers receiving repeat orders |
| Small-business resilience | Retailer retention, order continuity, time to resolve disputes and access to transaction records |
| Consumer availability | Availability of essential categories and observed stock-out frequency at participating stores |

Metrics need clear definitions, baselines, sample sizes, time windows and comparison methods. Where possible, use pre/post measurement and appropriate comparison groups. Report limitations and avoid implying that any observed change was caused by POL without a defensible evaluation design.

---

## 15. Contributing and working with AI agents

POL uses canonical documents and repository-specific execution rules to keep product work coherent across developers and AI agents.

Before starting a task:

1. Read the Decision Register and Current Source of Truth.
2. Read the relevant product, domain, API, data and design contracts.
3. Inspect the current implementation and neighbouring tests before editing.
4. Work from the latest approved main SHA or an explicitly approved feature branch.
5. Declare a narrow objective, allowed file scope, dependencies and acceptance criteria.
6. Verify the complete diff and run relevant tests before committing.
7. Report the exact base SHA, final SHA, changed files, commands, results, risks and remaining blockers.

The POL Batch Execution skill is available at .agents/skills/pol-batch-execution/SKILL.md. It supplements, but never overrides, the repository's canonical safety rule and decision register.

Do not:
- Merge a historical branch merely because it contains more commits.
- Import large stale branches or delete archive branches without explicit approval.
- Change commercial, identity, payment, inventory or security policy through UI-only edits.
- Make an unapproved schema or API contract change.
- Claim tests passed when they were skipped, never started or executed on a different SHA.
- Mark a screen visually verified without current screenshots and inspection.
- Turn mocks into silent production fallbacks.
- Commit secrets, private data, local build artifacts or unreviewed user files.

---

## 16. Current readiness boundaries

POL's repository maturity and project scale should not be confused with production readiness. The source contains substantial product, backend, frontend, mobile, data and QA work, but some acceptance gates depend on external credentials, real providers, environment configuration, physical devices, legal decisions and pilot operation.

Before any pilot or production claim, verify at minimum:

- Exact-SHA backend and migration verification.
- Web typecheck, build and browser E2E.
- Mobile typecheck, functional/regression QA and device installation.
- OTP security and SMS provider template acceptance.
- Tenant isolation and role/permission tests.
- Object-storage upload and access lifecycle.
- Payment/reconciliation and invoice workflows.
- Backup/restore, monitoring, incident response and deployment rollback.
- Legal terms, commercial agreements and pilot operating procedures.
- Current release-readiness ledger and explicit owner approvals.

**POL's ambition is to become dependable digital infrastructure for everyday trade. Its measure of success will be the real improvement it can demonstrate for retailers, suppliers, distributors and the communities they serve — not the size of its codebase or the number of features represented in the repository.**


## License and third-party assets

Review the applicable license and attribution requirements for each source directory, third-party dependency, font, image and design asset before redistribution. A license file in one subdirectory does not automatically grant rights to every asset in the repository.

## Maintainer notes

This repository is both a software codebase and a long-lived product knowledge base. Keep executable implementation, contracts, architectural decisions and audit evidence aligned. When documenting a feature or claiming that a gate passed, include enough context for another maintainer to verify it: source path, exact commit SHA, command or workflow, environment, result and known limitations.

For project-specific questions, start with the canonical control documents rather than relying on historical chat summaries or old handoff notes.
