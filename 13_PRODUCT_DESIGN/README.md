# POL Product Design

این پوشه Source of Truth طراحی محصول POL است.

## Workstream order
1. `00_DESIGN_PROGRAM.md`
2. `01_DEEP_RESEARCH_SYNTHESIS.md`
3. `02_DESIGN_SYSTEM.md`
4. `03_BRAND_AND_VISUAL_LANGUAGE.md`
5. `04_NAVIGATION_AND_INFORMATION_ARCHITECTURE.md`
6. `05_LAYOUT_RESPONSIVE_ACCESSIBILITY.md`
7. `06_RETAILER_POL_MARKET_UX.md`
8. `07_VENDOR_UX.md`
9. `08_OPERATIONS_UX.md`
10. `09_FIELD_ACTIVATOR_UX.md`
11. `10_CORPORATE_WEBSITE_UX.md`
12. `11_FRONTEND_IMPLEMENTATION_STRATEGY.md`
13. `12_DESIGN_TOKENS_AND_COMPONENT_INVENTORY.md`
14. `13_PROTOTYPE_AND_FIGMA_PLAN.md`
15. `14_DESIGN_DECISION_REGISTER.md`
16. `15_CROSS_PROJECT_DESIGN_AUDIT_2026-09-15.md`
17. `16_APPLE_DESIGN_CRAFT_ADAPTATION.md`
18. `17_PENPOT_CANONICAL_BLUEPRINT.md`
19. `18_DESIGN_COMPLETION_PLAN.md`
20. `19_ANTIGRAVITY_MASTER_EXECUTION_PROMPT.md`
21. `20_ANTIGRAVITY_REPOSITORY_AUDIT_PROMPT.md`
22. `21_MVP_DESIGN_AND_FRONTEND_READINESS_GATE_2026-09-16.md`
23. `22_UI_UX_PAGE_AND_SECTION_COMPLETION_SPEC_2026-09-16.md`

## Execution rule
`Repository Sync → Repository Audit → Specification Completion → Readiness Gate → Page/Section Completion → Written Design Source of Truth → Figma/Penpot Prototype → Mock-First Frontend → Production Backend Integration`

The readiness gate and page/section specification are the final pre-high-fidelity inputs. They close explicit Auth/Session, commerce-state, RMA/Support, payment/notification, localization, analytics, vendor-comparison, delivery-boundary, screen-contract and page-inventory gaps without overriding canonical business decisions.

### Simplicity rule
Every new screen must justify its existence by a concrete MVP task. Prefer fewer screens, fewer required fields, fewer decisions per step, progressive disclosure, search/reorder/task queues, and contextual recovery over feature-heavy navigation or decorative complexity.

No visual artifact becomes a canonical product requirement until the corresponding written decision is recorded here or in the governing product/engineering documents.
