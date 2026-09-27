---
name: pol-visual-refinement
description: Strict brownfield visual refinement and UI reconstruction skill for POL (پُل) B2B FMCG platform. Enforces visual polish while protecting business and domain invariants.
---

# POL Visual Refinement Skill

## Core Mission
Upgrade the visual quality, UI consistency, UX presentation, accessibility presentation, responsive behavior, component quality, and visual polish of the existing POL MVP without altering any business logic, API contracts, or system semantics.

## Strict Invariants

### 1. NEVER CHANGE
- Business logic or domain rules
- API semantics, endpoints, HTTP methods, or payload shapes
- Permissions, RBAC guards, and session authentication
- Database schema, SQL queries, or migrations
- Pricing calculations, inventory quantities, or allocation logic
- Order state machine transitions and delivery/payment semantics
- Financial calculations, commission, or settlement logic
- Feature scope or MVP workflow meaning

### 2. MAY CHANGE
- CSS stylesheets and Tailwind classes
- Layout, spacing, alignment, and compositional structure
- Typography scale, line heights, and font weights
- Semantic color mapping and surface hierarchy
- Component styling, states (hover, active, focus, disabled, loading)
- Iconography and imagery framing
- Micro-interactions and motion timing (120–240ms)
- Responsive presentation (Mobile, Tablet, Desktop)
- Loading skeletons, empty states, and error presentation
- Accessibility contrast, focus rings, and screen-reader semantics
- Visual information hierarchy and density profiles (D1, D2, D3)

## Required 11-Step Workflow
1. **Inspect**: Examine the route, components, DOM structure, and current presentation.
2. **Understand**: Identify the user's primary task, critical information, and secondary actions.
3. **Establish Visual Thesis**: Determine the appropriate density gear (D1 Retailer, D2 Vendor, D3 Ops) and layout priorities.
4. **Reuse POL System**: Consume `@pol/tokens` and `@pol/ui` components; never introduce arbitrary hex values.
5. **Implement**: Apply precision commerce styling in isolated presentation slices.
6. **Render**: Run the application and view the rendered interface in browser/headless runner.
7. **Compare**: Compare before vs after against Precision Commerce standards.
8. **Audit**: Verify Light and Night parity, RTL layout, contrast, and responsive viewports.
9. **Fix**: Surgically remediate visual defects or regressions.
10. **Verify Behavior**: Confirm zero regression in APIs, form submissions, navigation, or state handlers.
11. **Record Evidence**: Log changes in `VISUAL_CHANGE_LOG.md` and save artifacts.
