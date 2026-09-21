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
24. `23_ANTIGRAVITY_FAILURE_MODES_AND_AGENT_OPERATING_PROTOCOL_2026-09-16.md`
25. `24_PENPOT_MANUAL_REBUILD_MASTER_SPEC_2026-09-16.md`
26. `25_VISUAL_DESIGN_REFINEMENT_AND_PENPOT_STYLE_GUIDE_2026-09-16.md`
27. `26_SCREEN_WIREFRAME_SPEC_RETAILER_VENDOR_2026-09-16.md`
28. `27_SCREEN_WIREFRAME_SPEC_SHARED_OPS_FIELD_CORPORATE_2026-09-16.md`
29. `28_DESIGN_SYSTEM_V2_RESEARCH_BASED_2026-09-16.md`
30. `29_SCREEN_DESIGN_EXECUTION_RESEARCH_FIRST_2026-09-16.md`
31. `30_RETAILER_SCREEN_BY_SCREEN_SPEC_2026-09-16.md`
32. `31_VENDOR_OPS_FIELD_CORPORATE_SCREEN_BY_SCREEN_SPEC_2026-09-16.md`
33. `32_FINAL_DESIGN_TOKENS_V3_2026-09-16.md`
34. `33_COMPONENT_SPECIFICATION_V2_2026-09-16.md`
35. `34_PENPOT_PATTERN_LIBRARY_V2_2026-09-16.md`
36. `35_PROTOTYPE_FLOWS_AND_FAILURE_BRANCHES_V2_2026-09-16.md`
37. `36_PENPOT_EXECUTION_AND_QA_GATES_V2_2026-09-16.md`
38. `37_RESEARCH_PRINCIPLES_MATRIX_V1_2026-09-16.md`
39. `38_DESIGN_TOKENS_CANONICAL_V4_2026-09-16.md`
40. `39_COMPONENT_CONTRACTS_CANONICAL_V3_2026-09-16.md`
41. `40_PATTERN_LIBRARY_CANONICAL_V3_2026-09-16.md`
42. `41_SCREEN_COMPOSITION_RULES_V3_2026-09-16.md`
43. `42_PROTOTYPE_SPEC_AND_FLOW_MATRIX_V3_2026-09-16.md`
44. `43_DESIGN_QA_PROTOCOL_V3_2026-09-16.md`
45. `44_DESIGN_PIPELINE_MASTER_INDEX_V3_2026-09-16.md`
46. `45_REPOSITORY_WIDE_DESIGN_COMPLETENESS_AUDIT_2026-09-16.md`
47. `47_PROJECT_WIDE_BUG_AUDIT_2026-09-16.md`
48. `50_POL_MASTER_PENPOT_UI_UX_TREE_SPEC_2026-09-21.md`
49. `51_POL_MASTER_PENPOT_TREE_GENERATION_PROMPT_2026-09-21.md`
50. `52_POL_PENPOT_AGENTIC_DESIGN_EXECUTION_PROTOCOL_2026-09-21.md`
51. `53_POL_MASTER_TREE_DEEP_SATURATION_AUDIT_2026-09-21.md`
52. `54_POL_MASTER_TREE_EXECUTABLE_SCHEMA_2026-09-21.md` — Version 1.1.0
53. `55_POL_MASTER_TREE_NODE_SCHEMA_2026-09-21.json`
54. `56_POL_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM_2026-09-21.md`

## Current visual direction

**A — Precision Commerce**  
Canonical visual system: `56_POL_PRECISION_COMMERCE_VISUAL_DESIGN_SYSTEM_2026-09-21.md`  
Theme policy: **Light + Night for every applicable canonical UI node**.

## Agent operating assets

- `.agents/rules/00-pol-canonical-safety.md` — persistent project safety constraints.
- `.agents/skills/pol-batch-execution/SKILL.md` — bounded design/frontend execution protocol.

## Official design pipeline
`Research → Visual Direction → Principle → Token → Component → Pattern → Screen → Light/Night Prototype → QA → Handoff`

## Operational index
`44_DESIGN_PIPELINE_MASTER_INDEX_V3_2026-09-16.md`

## Current Master Tree
`50_POL_MASTER_PENPOT_UI_UX_TREE_SPEC_2026-09-21.md` — Version 3.6.0

## Executable Master Tree Schema
`54_POL_MASTER_TREE_EXECUTABLE_SCHEMA_2026-09-21.md`

## Machine-readable Node Schema
`55_POL_MASTER_TREE_NODE_SCHEMA_2026-09-21.json`

The human-readable Master Tree and executable schema are co-equal design-control artifacts: the human document defines semantics; the JSON schema defines machine-checkable structure.

## Agent execution protocol
`52_POL_PENPOT_AGENTIC_DESIGN_EXECUTION_PROTOCOL_2026-09-21.md` — Version 1.3.0

## Latest deep saturation audit
`53_POL_MASTER_TREE_DEEP_SATURATION_AUDIT_2026-09-21.md`

## Latest repository-wide design audit
`45_REPOSITORY_WIDE_DESIGN_COMPLETENESS_AUDIT_2026-09-16.md`

## Execution rule
`Repository Sync → Repository Audit → Specification Completion → Readiness Gate → Page/Section Completion → Agent Safety Gate → Written Design Source of Truth → Figma/Penpot Prototype → Mock-First Frontend → Production Backend Integration`

### Simplicity rule
Every new screen must justify its existence by a concrete MVP task. Prefer fewer screens, fewer required fields, fewer decisions per step, progressive disclosure, search/reorder/task queues, and contextual recovery over feature-heavy navigation or decorative complexity.

### Completeness rule
A screen is not considered complete because it exists. It is complete only when:
`Canonical requirement → research principle → token → component → pattern → screen → state/failure branches → prototype → accessibility/content/contract QA → verified artifact`.

No visual artifact becomes a canonical product requirement until the corresponding written decision is recorded here or in the governing product/engineering documents.
