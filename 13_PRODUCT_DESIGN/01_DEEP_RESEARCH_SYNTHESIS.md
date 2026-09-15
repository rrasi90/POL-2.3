# POL Deep Research Synthesis — B2B Product UX

## Research scope
Research focuses on B2B wholesale/mobile ordering UX, reusable design-system practices, accessibility, retailer workflow compression, vendor operations, and acquisition websites.

## 1. Strong recurring patterns
### Retailer
- Fast repeat ordering is a core job, not a secondary feature.
- Purchase history and one-click/low-step reorder reduce reconstruction of past baskets.
- MOQ, case-pack/increment and availability should be visible before checkout validation fails.
- Order status, shipping information, returns and support are part of the core buying loop.
- Mobile should prioritize replenishment and status over deep merchandising.

Faire's current retailer app explicitly centers order/shipping visibility, purchase history, reorder, returns and mobile browsing. Its reorder flow also respects brand purchasing restrictions and valid multiples.

Udaan's current App Store description similarly emphasizes quick signup, repeat orders, real-time delivery tracking, returns and mobile purchasing for small businesses.

### Vendor / supplier
- Vendor UX must combine assortment/catalog management, inventory truth and order execution.
- Sales teams and operations need the same underlying order record even when ordering happens through assisted channels.
- Operational dashboards should emphasize exceptions, queues and next actions rather than generic KPI decoration.

Cartona publicly describes retailer ordering/comparison, supplier connection, inventory visibility and order tracking; it also describes separate solutions for retailers, wholesalers and sales teams.

### B2B mechanics
Current wholesale UX research highlights account-specific price, MOQ/case packs, stock honesty, reorder, search by SKU/variant/pack and clear approval/order status as the high-value information architecture.

### Quick-order patterns
Wholesale tooling increasingly supports SKU/barcode-first order entry, saved lists and repeat orders because rebuilding large carts is a high-friction task.

## 2. Design-system findings
- Reusable components are essential for consistency across multiple role-specific surfaces. GOV.UK Design System explicitly treats components as reusable building blocks and pairs them with usage guidance.
- Accessibility must be encoded in components, not left to screen-level review. Carbon's current data-table guidance, for example, builds keyboard interaction into the component itself.
- WCAG 2.2 adds/clarifies focus, target-size, redundant-entry and accessible-authentication requirements that are directly relevant to POL's mobile and OTP flows. Target size has a 24x24 CSS px minimum with exceptions; accessible authentication guidance reduces unnecessary cognitive/transcription burden.
- Error states should tell the user what happened and how to recover while preserving entered data. GOV.UK's validation/error guidance is a strong pattern for POL forms and onboarding.

## 3. POL-specific interpretation
These findings do NOT justify copying competitors. They reinforce decisions already made for POL:
- retailer is task-first and replenishment-oriented;
- Multi-Vendor basket is canonical D-014;
- inventory/pricing truth is operationally central;
- Vendor Referral is a channel capability, not a consumer rewards system;
- profile/persona context should personalize navigation without becoming authorization;
- assisted ordering is a bridge to self-service, not an exception path.

## 4. Design hypotheses to validate in Ahvaz
These remain hypotheses until pilot evidence exists:
1. Retailers will prefer a home screen centered on reorder/current orders over promotional discovery.
2. A fast searchable catalog with visible pack/MOQ/availability will outperform image-heavy browsing for routine FMCG replenishment.
3. Multi-vendor allocation must be summarized in business language before checkout to avoid surprise splits.
4. Vendor referral and assisted ordering will reduce onboarding friction when tied to a recognizable supplier/sales relationship.
5. Order-state transparency will reduce support contacts more than additional merchandising features.

## 5. Anti-patterns to avoid
- consumer-style promotional home page dominating operational tasks;
- hidden MOQ/case pack until submission;
- generic "in stock" indicators unsupported by current inventory data;
- desktop tables squeezed into mobile screens;
- destructive actions adjacent to quantity controls;
- role/persona implemented as duplicated applications with inconsistent components;
- UI-only permission hiding without server authorization;
- repeated manual data entry across onboarding and checkout.

## 6. Primary web sources
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C WCAG 2.2 changes / accessible authentication: https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- W3C accessible authentication guidance: https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html
- GOV.UK Design System components: https://design-system.service.gov.uk/components/
- GOV.UK error messages: https://design-system.service.gov.uk/components/error-message/
- GOV.UK validation pattern: https://design-system.service.gov.uk/patterns/validation/
- Carbon Design System data-table accessibility: https://carbondesignsystem.com/components/data-table/accessibility/
- Faire Retailer App: https://www.faire.com/retailers/app
- Faire reorder guidance: https://www.faire.com/support/articles/8457499998363
- Cartona: https://cartona.com/
- udaan App: https://apps.apple.com/in/app/udaan/id1224098850
- Shopify B2B quick order/reorder examples: https://apps.shopify.com/single-page-order-form and https://apps.shopify.com/orderflow-3
