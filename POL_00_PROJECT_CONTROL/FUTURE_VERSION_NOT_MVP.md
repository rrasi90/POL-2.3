# POL Future Version Blueprint — NOT MVP

> [!CAUTION]
> **THIS DOCUMENT IS NOT THE MVP SPECIFICATION.**
>
> Nothing in this document is active in the Ahvaz MVP unless a separate canonical decision explicitly promotes it. The existence of a schema/service foundation for a future capability does **not** authorize exposing, pricing, automating, or operating that capability in MVP.

**Status:** FUTURE-ONLY / NON-CANONICAL FOR MVP EXECUTION  
**Applies to:** Post-pilot / later product versions  
**Current MVP reference:** `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`  

---

## 1. Purpose

This file isolates future product evolution from the MVP so that later versions can reuse stable infrastructure without expanding the current pilot surface.

The governing rule is:

```text
MVP = validate repeatable B2B ordering + supply reliability + retailer habit.
FUTURE = monetize, optimize, finance, personalize, and scale after evidence.
```

The future roadmap therefore assumes that the MVP already produced trustworthy transaction, inventory, price, fulfillment, referral, and customer-behavior data.

---

## 2. Explicitly NOT MVP

The following capabilities are **not active in the Ahvaz MVP**:

### P2 — Post-Pilot Optimization
- Personalized retailer-specific pricing.
- Vendor-specific commercial terms with effective dating and approval workflows.
- Quantity discounts / volume pricing.
- Bundles and basket optimization.
- Rule-based replenishment recommendations.
- Vendor health scoring derived from observed fulfillment data.
- Retailer segmentation and lifecycle cohorts.
- Demand forecasting.

### P3 — Monetization / Financial Services
- Take-rate monetization after the free pilot.
- Vendor subscription / SaaS packages.
- Sponsored products / paid placement.
- Payment services revenue.
- Embedded credit.
- BNPL / trade credit.
- Wallet or escrow / custody payment model.

### P4 — Advanced Network and Intelligence
- Advanced recommendation models.
- Predictive stockout prevention.
- Multi-touch referral attribution and incentive optimization.
- Referral rewards, credits, coupons, or vendor-funded acquisition budgets.
- Advanced pricing optimization.
- Cross-vendor promotion optimization.
- Network-level supply-demand forecasting.

### Long-term / Strategic
- Owned warehouses.
- Owned logistics fleet.
- Complex loyalty programs.
- Gamification.
- Social commerce.
- Large-account procurement / quotation workflows.
- Manufacturer-facing commerce and analytics products.
- Advertising marketplace beyond simple sponsored placement.

---

## 3. Vendor Referral: MVP vs Future Boundary

### ACTIVE NOW — MVP
Vendor Referral is part of the MVP under **D-016**.

MVP behavior is intentionally narrow:

```text
Vendor
  -> create referral code/link
  -> share directly with retailer
Retailer
  -> redeem during onboarding/activation
POL
  -> store first-touch attribution
  -> connect attribution to first order
  -> expose attribution for pilot analytics
```

MVP deliberately excludes:
- monetary referral rewards;
- referral wallet balances;
- referral coupons or discounts;
- multi-touch attribution;
- affiliate-style commission settlement;
- referral fraud scoring beyond ordinary risk controls;
- automated referral campaigns.

### FUTURE — AFTER MVP EVIDENCE
Possible future referral system:

```text
Referral Source
 -> invite campaign
 -> identity resolution
 -> first-touch + multi-touch attribution
 -> activation
 -> first order
 -> repeat order
 -> vendor-funded reward eligibility
 -> reward ledger
 -> campaign ROI
```

Future referral activation requires evidence that vendor-led acquisition creates lower acquisition cost and/or higher retention than other channels.

---

## 4. Future Commercial Terms Engine

The MVP may retain data-model foundations, but future activation should support:

- company/location-specific price books;
- customer-specific negotiated price;
- MOQ / MOV rules;
- volume breaks;
- payment terms (e.g. net terms);
- trade promotions;
- vendor-funded discounts;
- effective-dated agreements;
- approval workflows;
- audit trail and rollback.

The commercial layer must remain separate from Master Product identity and Vendor Product identity.

---

## 5. Future Finance / Credit Boundary

No future financial service should be activated by changing only the order status.

A future finance stack needs independent objects for:

```text
Eligibility
 -> Limit
 -> Offer
 -> Acceptance
 -> Draw
 -> Repayment
 -> Delinquency
 -> Recovery
 -> Reconciliation
```

Credit decisions should be based on observed transaction history, repayment behavior and operational risk rather than a static user attribute.

Payment custody and credit are separate capabilities and must remain separate state machines.

---

## 6. Future Recommendation / Replenishment Boundary

The minimum data contract needed now is historical transaction and supply telemetry:

- retailer;
- vendor;
- product;
- quantity;
- effective price;
- order timestamp;
- fulfillment result;
- stock availability;
- substitution / rejection reason;
- reorder interval;
- cancellation / return outcome.

Future recommendation systems may then implement:

1. deterministic reorder reminders;
2. rules-based replenishment;
3. basket completion suggestions;
4. vendor-aware recommendations;
5. personalized recommendations;
6. predictive demand models.

The AI layer must not become the source of truth for inventory, price, order state, or payment state.

---

## 7. Future Analytics / KPI Layer

Future versions should move from basic operational reporting toward cohort and unit-economic analysis:

```text
Acquisition
 -> Activation
 -> First Order
 -> Repeat Order
 -> Frequency
 -> AOV
 -> Contribution / Order
 -> Retention
 -> Vendor Lifetime Value
```

Important future cohort dimensions:
- acquisition channel;
- vendor referral source;
- neighborhood / geography;
- first-order vendor count;
- category mix;
- fulfillment reliability;
- price sensitivity;
- reorder interval.

Every KPI must preserve metric-definition version, source event lineage, cohort rule, timezone and calculation version.

---

## 8. Future Logistics Evolution

POL should remain asset-light unless pilot evidence proves that owned logistics creates superior contribution margin after all capital and operating costs.

Future options:

- 3PL orchestration;
- shared local hub scheduling;
- route optimization;
- dynamic capacity allocation;
- vendor-specific pickup windows;
- cross-dock models;
- later, selective POL-operated logistics where economically justified.

Ownership of logistics assets is a strategic decision, not a default feature upgrade.

---

## 9. Future Product Roadmap

| Horizon | Future capability | Entry condition |
|---|---|---|
| **P2** | Replenishment intelligence | Repeat-purchase evidence exists |
| **P2** | Personalized commercial terms | Sufficient price/order history |
| **P2** | Vendor health scoring | Enough observed fulfillment events |
| **P2** | Bundle / quantity optimization | Stable vendor catalog + demand data |
| **P3** | Take-rate monetization | Proven vendor ROI + contribution economics |
| **P3** | Vendor SaaS / analytics | Vendors repeatedly use operational data |
| **P3** | Sponsored placement | Sufficient marketplace density + trust controls |
| **P3** | Credit / BNPL experiments | Transaction and repayment evidence + risk model |
| **P4** | Advanced AI | High-quality longitudinal data + clear economic gain |
| **P4** | Multi-touch referral rewards | Vendor-led acquisition proven economically |
| **P4** | Owned logistics | Asset-light model demonstrably bottlenecks growth/economics |

---

## 10. Promotion Gate: Future -> Active

A future feature may move into product execution only after all of the following are documented:

1. Product hypothesis and measurable success metric.
2. Pilot or post-pilot evidence supporting the need.
3. Unit-economic impact estimate.
4. Operational risk assessment.
5. Canonical data model and state-machine review.
6. API / client contract review.
7. Security / privacy review where relevant.
8. Explicit decision-record update superseding or adding a canonical decision.
9. Automated regression and cross-domain integration coverage.
10. An explicit owner and rollback / kill criterion.

Until those gates are complete, the capability remains **FUTURE / NOT MVP**.

---

## 11. Non-Negotiable Architecture Invariants for Future Work

Future features must continue to respect:

- PostgreSQL 18 as canonical runtime database.
- Organization/membership as authorization SSoT.
- Basket -> AllocationPlan -> OrderGroup -> Order -> OrderItem separation.
- Transactional domain write -> outbox -> worker boundary.
- No direct provider side effect inside core domain transaction.
- No AI model as source of truth for transactional state.
- No future finance feature silently turning NON_CUSTODIAL_DIRECT MVP payments into custody.
- No future monetization feature compromising price / availability / fulfillment truth.
- Simplicity at the retailer UX surface even when internal machinery becomes sophisticated.

---

## 12. Final Warning

**DO NOT USE THIS FILE TO BUILD MVP FEATURES.**

Use `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` and the current MVP route contracts for MVP implementation.

This document exists specifically to prevent future product ambition from leaking into the Ahvaz pilot and to give later versions a controlled starting point.