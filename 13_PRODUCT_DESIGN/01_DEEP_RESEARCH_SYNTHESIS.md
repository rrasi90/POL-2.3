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

Faire's current retailer app explicitly centers order/shipping visibility, purchase history, reorder, returns and mobile browsing. Its reorder flow also respects brand purchasing restrictions and valid multiples. citeturn658986view0 citeturn984598search3

Udaan's current App Store description similarly emphasizes quick signup, repeat orders, real-time delivery tracking, returns and mobile purchasing for small businesses. citeturn449708view1

### Vendor / supplier
- Vendor UX must combine assortment/catalog management, inventory truth and order execution.
- Sales teams and operations need the same underlying order record even when ordering happens through assisted channels.
- Operational dashboards should emphasize exceptions, queues and next actions rather than generic KPI decoration.

Cartona publicly describes retailer ordering/comparison, supplier connection, inventory visibility and order tracking; it also describes separate solutions for retailers, wholesalers and sales teams. citeturn449708view0

### B2B mechanics
Current wholesale UX research highlights account-specific price, MOQ/case packs, stock honesty, reorder, search by SKU/variant/pack and clear approval/order status as the high-value information architecture. citeturn614457search2turn614457search3

### Quick-order patterns
Wholesale tooling increasingly supports SKU/barcode-first order entry, saved lists and repeat orders because rebuilding large carts is a high-friction task. citeturn984598search2turn984598search8turn984598search16

## 2. Design-system findings
- Reusable components are essential for consistency across multiple role-specific surfaces. GOV.UK Design System explicitly treats components as reusable building blocks and pairs them with usage guidance. citeturn990483search4
- Accessibility must be encoded in components, not left to screen-level review. Carbon's current data-table guidance, for example, builds keyboard interaction into the component itself. citeturn990483search6
- WCAG 2.2 adds/clarifies focus, target-size, redundant-entry and accessible-authentication requirements that are directly relevant to POL's mobile and OTP flows. Target size has a 24x24 CSS px minimum with exceptions; accessible authentication guidance reduces unnecessary cognitive/transcription burden. citeturn990483search0turn990483search2turn990483search5
- Error states should tell the user what happened and how to recover while preserving entered data. GOV.UK's validation/error guidance is a strong pattern for POL forms and onboarding. citeturn990483search1turn990483search3turn990483search9

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
