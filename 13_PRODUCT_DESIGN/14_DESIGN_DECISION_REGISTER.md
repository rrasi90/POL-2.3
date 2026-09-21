# POL Design Decision Register

| ID | Status | Decision | Rationale |
|---|---|---|---|
| UX-001 | ACTIVE | Design System is shared across all POL surfaces | Prevent fragmented product families and duplicated components |
| UX-002 | ACTIVE | Retailer experience is mobile-first | Routine replenishment happens close to the shop floor; current B2B apps emphasize mobile reorder/status |
| UX-003 | ACTIVE | Retailer home prioritizes operations before promotion | POL is a replenishment workflow, not a media storefront |
| UX-004 | ACTIVE | Multi-Vendor basket remains a single mental model until allocation is required | D-014 requires one retailer basket with deterministic vendor allocation |
| UX-005 | ACTIVE | Vendor UI is queue-first | Operational completion matters more than passive dashboards |
| UX-006 | ACTIVE | Persona changes presentation/workflow, never RBAC | D-017 |
| UX-007 | ACTIVE | Persian RTL is first-class | POL's launch market and user context |
| UX-008 | ACTIVE | Accessibility is component-level | Prevent accessibility regressions across five product surfaces |
| UX-009 | ACTIVE | Mock API may precede HTTP runtime | Enables frontend progress without bypassing canonical application contracts |
| UX-010 | ACTIVE | Figma decisions must flow back into repository docs | Preserve written source-of-truth governance |
| UX-011 | HYPOTHESIS | Retailer home should emphasize reorder/open orders over discovery | To validate in Ahvaz pilot |
| UX-012 | HYPOTHESIS | Visible pack/MOQ/availability will materially reduce order correction | To validate through support/checkout metrics |
| UX-013 | ALIGNED | Frontend implementation follows the approved technical architecture: Next.js/React for web and React Native/Expo for the retailer mobile surface. Any framework/version replacement requires a separate architecture decision. | Removes the previous documentation conflict between `06_PRODUCT/Technical_Architecture_Spec.md` and the design register while keeping framework upgrades under explicit change control |
| UX-014 | OPEN | Native retailer app timing vs responsive PWA/web | Depends on usage/retention evidence and technical constraints; UX remains transport-agnostic until this product-timing decision is made |
| UX-015 | ACTIVE | Operational palette anchors on logo Midnight Navy (#0A1730) with high-conversion Operational Blue (#2563EB/#1D4ED8) for interactive CTA, preserving Champagne Gold (#F7D4B6) for brand logo identity | Approved in co-founder alignment 2026-09-16 based on actual logo asset audit and WCAG 2.2 AA/AAA contrast validation |


| UX-016 | ACTIVE | Every canonical persona has both Web and Android surfaces | Web and Android share backend, identity, organization context, authorization and domain semantics; UX is optimized by context rather than duplicated. |
| UX-017 | ACTIVE | Delegated permissions refine baseline role responsibilities | Organization managers may grant/revoke capability permissions for their own memberships within platform-defined privilege ceilings. Server-side authorization remains authoritative. |
| UX-018 | ACTIVE | Vendor-first and product-first discovery are equivalent entry paths | Retailers can search products or vendors and arrive at the same canonical catalog/inventory/order model. |
| UX-019 | ACTIVE | Multi-vendor checkout is presented as one purchase with vendor-specific invoices | OrderGroup remains the parent mental model; child Orders and invoices are visible beneath it. |
| UX-020 | ACTIVE | Financial Activity is not a Wallet | Payment/refund/invoice/order/authorized settlement visibility may be aggregated in a read surface without creating stored-value balance in MVP. |
| UX-021 | ACTIVE | Delivery Handoff is a restricted capability surface | MVP does not require a full Driver App; delivery handoff uses short-lived restricted capability tokens plus receiver/POD confirmation. |
| UX-022 | ACTIVE | Barcode scanning is a first-class Android operational capability | Scanner is permission-scoped and feeds the existing Match/Candidate/Master Product governance flow. |
| UX-023 | ACTIVE | Product media requires provenance | Manufacturer-source imagery may be imported only through a provenance-aware workflow; public visibility is not treated as automatic reuse permission. |

## Governance
UX decisions cannot override product decisions D-001–D-020. The 2026-09-20 product architecture amendments D-021–D-028 are also canonical and must be reflected in UX decisions. Conflicts must be resolved in `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` first.
