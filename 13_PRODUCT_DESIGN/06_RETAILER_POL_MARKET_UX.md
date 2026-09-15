# Phase 2 — POL Market Retailer UX

## Product goal
Turn routine FMCG replenishment into a fast, trustworthy workflow while preserving assisted ordering for pilot users.

## Primary retailer journey
Onboarding → home → search/browse → product/pack decision → basket → multi-vendor allocation review → revalidation → checkout → order group → order detail → fulfillment tracking → reorder.

## Onboarding
1. Phone/auth initiation.
2. Retailer identity and shop context.
3. Active organization/membership resolution.
4. Guided first catalog interaction.
5. Assisted order path when needed.

Do not make the retailer repeat shop information already known in the same process. WCAG 2.2 explicitly addresses redundant entry. citeturn990483search2

## Home
Priority order:
1. Open orders / actions needed today.
2. Reorder from recent/past purchases.
3. Saved lists.
4. High-confidence product/category entry points.
5. Promotions only when relevant and evidence-backed.

## Search and catalog
Search should support product names, common Persian terms, SKU/barcode when available, pack/variant distinctions and category browsing.

Product row/card should make visible when available:
- product identity;
- vendor context where relevant;
- selling unit / case pack;
- current price;
- availability status;
- MOQ / quantity increment;
- quantity control.

The goal is a correct order on first submission, not maximum catalog browsing time.

## Basket
Basket is the operational heart of POL.

For D-014 Multi-Vendor MVP, the UI should preserve one unified retailer basket while clearly explaining vendor allocation before final checkout. Vendor splits must not feel like unexpected extra orders.

Display:
- line items;
- vendor allocation summary;
- per-vendor subtotal where useful;
- constraints that require adjustment;
- final payable total;
- delivery/settlement information per the canonical payment model.

## Checkout
Stages:
1. Basket validation.
2. Allocation/revalidation result.
3. Address/contact confirmation.
4. Direct payment method/evidence path according to canonical model.
5. Final confirmation.

The UI cannot calculate a replacement for server-side allocation, price or inventory truth.

## Orders
Retailer needs a clear order-group view plus child-order status when multiple vendors are involved.

Order detail should expose:
- status;
- vendor;
- items;
- amounts;
- fulfillment milestones;
- delivery/POD state;
- invoice/payment evidence when applicable;
- issue/return action.

## Reorder
Reorder is a first-class journey. Faire's current retailer flow exposes purchase history and explicit reorder entry points, with purchasing restrictions enforced as part of the reorder path. citeturn658986view0turn984598search3

POL should support:
- Buy again from order;
- reorder from saved list;
- quantity adjustment before validation;
- clear explanation when historical lines are unavailable or changed.

## Profile / account
Use the canonical five-layer model from D-017. Retailer UI can expose personal profile, shop/organization context, preferences, notification settings and security; it must not expose role editing.

## Empty / exception states
Must cover:
- no products found;
- product unavailable;
- MOQ not satisfied;
- allocation conflict;
- price changed;
- inventory changed;
- vendor unavailable;
- order partially progressed;
- return requested;
- network timeout.

Every exception state requires recovery guidance, not only a red label.
