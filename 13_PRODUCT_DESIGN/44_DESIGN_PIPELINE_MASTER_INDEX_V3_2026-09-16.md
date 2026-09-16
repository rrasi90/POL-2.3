# POL Design Pipeline Master Index v3

## Official pipeline
`Research → Principle → Token → Component → Pattern → Screen → Prototype → QA → Handoff`

## Execution order
1. `37_RESEARCH_PRINCIPLES_MATRIX_V1_2026-09-16.md`
2. `38_DESIGN_TOKENS_CANONICAL_V4_2026-09-16.md`
3. `39_COMPONENT_CONTRACTS_CANONICAL_V3_2026-09-16.md`
4. `40_PATTERN_LIBRARY_CANONICAL_V3_2026-09-16.md`
5. `41_SCREEN_COMPOSITION_RULES_V3_2026-09-16.md`
6. existing screen-by-screen specifications `30_*` and `31_*`
7. `42_PROTOTYPE_SPEC_AND_FLOW_MATRIX_V3_2026-09-16.md`
8. `43_DESIGN_QA_PROTOCOL_V3_2026-09-16.md`

## Authority rules
Product/business/domain rules remain above visual artifacts. The pipeline may improve usability and presentation but may not invent authorization, pricing, allocation, custody, inventory or financial rules.

## Penpot implementation sequence
### Pass 1 — Foundations
Build tokens, type specimens, semantic colors, grids, RTL/LTR specimens and accessibility annotations.

### Pass 2 — Components
Build actual reusable components and variants, not screenshot-like duplicates.

### Pass 3 — Patterns
Assemble canonical patterns from components and verify states.

### Pass 4 — Screens
Construct screens only from approved patterns/components; screen-specific exceptions require a documented reason.

### Pass 5 — Prototypes
Connect critical flows and failure branches.

### Pass 6 — QA
Run research, token, component, screen, accessibility, prototype and handoff gates.

## Definition of Done
POL design is ready for frontend implementation only when:
- all required MVP screens exist;
- critical states exist;
- all reusable components use canonical tokens;
- critical flows are prototyped;
- failure/recovery branches are represented;
- accessibility annotations are complete;
- product/domain constraints are visually represented correctly;
- no unsupported business claims appear;
- screen and component IDs are implementation-ready.

## Source set
- `DECISION_REGISTER.md`
- product/domain/API contracts
- `02_DESIGN_SYSTEM.md`
- `17_PENPOT_CANONICAL_BLUEPRINT.md`
- `22_UI_UX_PAGE_AND_SECTION_COMPLETION_SPEC_2026-09-16.md`
- `24_PENPOT_MANUAL_REBUILD_MASTER_SPEC_2026-09-16.md`
- `25_VISUAL_DESIGN_REFINEMENT_AND_PENPOT_STYLE_GUIDE_2026-09-16.md`
- `26_SCREEN_WIREFRAME_SPEC_RETAILER_VENDOR_2026-09-16.md`
- `27_SCREEN_WIREFRAME_SPEC_SHARED_OPS_FIELD_CORPORATE_2026-09-16.md`
- `28_DESIGN_SYSTEM_V2_RESEARCH_BASED_2026-09-16.md`
- `29_SCREEN_DESIGN_EXECUTION_RESEARCH_FIRST_2026-09-16.md`
- `30_RETAILER_SCREEN_BY_SCREEN_SPEC_2026-09-16.md`
- `31_VENDOR_OPS_FIELD_CORPORATE_SCREEN_BY_SCREEN_SPEC_2026-09-16.md`
- `32_FINAL_DESIGN_TOKENS_V3_2026-09-16.md`
- `33_COMPONENT_SPECIFICATION_V2_2026-09-16.md`
- `34_PENPOT_PATTERN_LIBRARY_V2_2026-09-16.md`
- `35_PROTOTYPE_FLOWS_AND_FAILURE_BRANCHES_V2_2026-09-16.md`
- `36_PENPOT_EXECUTION_AND_QA_GATES_V2_2026-09-16.md`
