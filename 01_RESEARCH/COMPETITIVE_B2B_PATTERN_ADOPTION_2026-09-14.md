# POL Competitive B2B Pattern Adoption — 2026-09-14

## Purpose

This note records external operating patterns that were reviewed against POL's known domain gaps. External patterns are evidence for design direction, not proof that POL should copy a competitor.

## 1. Cartona — Egypt

Cartona publicly describes an **asset-light** model, a **user-friendly** retailer/supplier network, an ERP experience for wholesalers with **real-time stock visibility**, and order tracking/completion. It also describes data/performance tracking and customized solutions for retailers, suppliers and sales teams.

POL adoption:
- Keep the asset-light decision locked for the Ahvaz pilot.
- Treat inventory freshness and supplier reliability as first-class operational data.
- Keep the retailer/vend​or workflow low-friction and mobile-first.
- Add explicit vendor operating windows/capacity foundations so availability can become a fulfillment promise rather than a raw stock number.

Source: https://cartona.com/

## 2. Cartona Enterprise

Cartona Enterprise exposes a deliberately simple three-step procurement flow: request products, source/compare price, deliver on schedule. It explicitly accepts product lists in common forms and promises a clear sourcing turnaround for larger buyers.

POL adoption:
- Preserve a simple normal path and progressive disclosure.
- Add saved/reorder lists for recurring FMCG replenishment.
- Keep future quote/procurement flows separate from the retailer pilot checkout rather than making the MVP form-heavy.

Source: https://enterprise.cartona.com/en

## 3. Udaan — India

Udaan's public buyer materials emphasize transparent pricing, reduced seller cancellations, seller reliability, buyer protection, refunds, communication without endless calls, doorstep delivery, and commercial constructs such as MOQ/assortment/payment terms. Its seller material also emphasizes minimum necessary onboarding information, logistics cutoffs/timing and order visibility.

POL adoption:
- Strengthen checkout allocation integrity so client-provided allocations cannot bypass server-side basket/product/MOQ/MOV checks.
- Preserve the Vendor Reliability Ledger and extend it with operational evidence rather than a single black-box score.
- Add payment evidence/reconciliation foundations while keeping the MVP payment custody model NON_CUSTODIAL_DIRECT.
- Add a future-ready Commercial Terms foundation; do not activate credit/BNPL during the pilot.

Sources:
- https://udaan.com/pages/buy-on-udaan
- https://udaan.com/pages/sell-on-udaan

## 4. Wasoko — Africa

Wasoko describes ordering through mobile app and SMS, same-day doorstep delivery, digital tracking, route optimization, mobile payments, support access and a staged trade-credit model based partly on transaction history. Its terms also describe collecting store location data for delivery and service operations.

POL adoption:
- Maintain Android/mobile-first operation as a core POL invariant.
- Keep SMS as a fallback channel for operational notifications where appropriate.
- Separate inventory availability from delivery capability by introducing vendor operating windows/capacity data.
- Formalize structured retailer locations, geo confidence and delivery notes.
- Keep any financing feature future-gated and evidence-driven rather than activating it in MVP.

Sources:
- https://wasoko.com/press/empowering-informal-retailers-the-impact-of-wasokos-last-mile-delivery-network/
- https://wasoko.com/information-hub/
- https://wasoko.com/wasoko-customer-app-terms-of-service/

## 5. MaxAB — Egypt / MENA

MaxAB publicly positions one retailer app across a broad catalog and a marketplace connecting retailers to wholesalers/suppliers, with ordering, delivery and financial services unified around the retailer.

POL adoption:
- Preserve the unified multi-vendor basket as a central value proposition.
- Keep the complexity hidden from the retailer: one basket, system-generated vendor child orders.
- Treat payment/finance as an adjacent capability with explicit lifecycle boundaries rather than coupling it to order creation.

Source: https://www.maxab.io/

## 6. Shopify B2B as a general B2B data-model reference

Shopify's public B2B documentation separates company, company location, buyer/contact permissions, catalogs, pricing and payment terms. Locations can carry distinct shipping addresses, pricing and terms.

POL adoption:
- Keep the organization/membership model as the identity SSoT.
- Add a structured retailer_locations foundation without changing the Ahvaz pilot's single-store UX.
- Keep commercial terms separable from Master Product and Vendor Product.
- Use future company/location complexity only when pilot telemetry justifies it.

Sources:
- https://help.shopify.com/en/manual/b2b/companies-and-customers/creating-companies
- https://help.shopify.com/en/manual/b2b/catalogs/index

## 7. Patterns deliberately NOT copied into POL MVP

- Escrow/custody payments: Udaan-like buyer protection is informative, but POL MVP remains NON_CUSTODIAL_DIRECT per canonical decision.
- BNPL/trade credit: Cartona/Udaan/Wasoko show that embedded finance can become strategically important, but it remains future-gated in POL.
- Asset-owning fleet/warehouse models: incompatible with POL's asset-light pilot constraint.
- Heavy procurement workflows: Cartona Enterprise-style large-account quoting is useful future architecture, not a reason to burden small Ahvaz retailers now.

## 8. Engineering conclusions applied in migration 005

The research and red-team audit produced these concrete foundations:

1. Database-enforced checkout idempotency.
2. Database-enforced inventory reservation invariant.
3. Non-overlapping effective price windows.
4. Vendor operating windows and cutoffs.
5. Vendor capacity profiles.
6. Structured retailer locations and geo confidence.
7. Commercial terms as a future-ready, inactive foundation.
8. Payment evidence and reconciliation cases for non-custodial payments.
9. Saved/reorder lists for low-friction FMCG replenishment.
10. Explicit consent records.
11. Risk/abuse evidence ledger.
12. KPI metric lineage and calculation versioning.
13. Experiment assignment foundation.
14. Server-side allocation integrity checks before canonical checkout.
15. Deterministic checkout replay through the same idempotency key.

Migration: `migrations/005_competitive_operational_hardening.sql`
Policy module: `scripts/operational_policies.py`
Checkout boundary: `scripts/checkout_gateway.py`
Regression tests: `scripts/test_competitive_operational_hardening.py`
