## User Prompt (VERBATIM — gospel)

Research current B2B SaaS UI/UX design patterns and best practices for 2025-2026. Focus on:

1. **B2B SaaS dashboard design patterns** - What are the best practices for operational dashboards? How should KPIs be displayed? What's the ideal information hierarchy?

2. **RTL/Persian UI design patterns** - Best practices for right-to-left interfaces. How do leading B2B platforms handle RTL? What are common pitfalls?

3. **Multi-vendor marketplace UI patterns** - How do platforms like Shopify, Amazon Business, or B2B marketplaces display vendor information? How should vendor storefronts work?

4. **Data-dense table design** - Best practices for tables with many columns, status badges, actions, pagination. How to handle mobile table responsive design?

5. **Order lifecycle UI patterns** - How should complex order state machines be displayed to users? Timeline vs stepper vs status badge approaches?

6. **Form design for B2B** - Best practices for complex forms (checkout, order creation, dispute filing). Multi-step vs single-page approaches?

7. **Color systems for B2B** - What color palettes work best for operational/enterprise apps? Semantic color usage for statuses?

8. **Typography for Persian/Farsi** - Best web fonts for Persian text? Font stack recommendations?

Search the web for: "B2B SaaS UI design patterns 2025", "operational dashboard design", "RTL UI best practices", "multi-vendor marketplace UX", "data table design patterns", "enterprise form design"

Return actionable design recommendations with specific examples where possible.

## Run Config

- vault_tag: b2b-saas-ui-patterns-4e1498
- query_file_path: research/runs/b2b-saas-ui-patterns-4e1498/query.md
- modality: collect (enumerative coverage across 8 distinct UI/UX domains)

## Modality Classification Rationale

The query asks for best practices across 8 distinct UI/UX domains. Each domain requires independent enumeration of patterns, examples, and recommendations. This is a collect-type query: enumerative coverage with per-domain sections.

## Tier Rationale

Classified as `light` + `structured`. The query asks for best practices across 8 distinct UI/UX domains — this is a bounded multi-entity survey with clear enumerated asks. Each domain has a clear, answerable scope ("what are the best practices for X"). No deep synthesis, conflicting-evidence adjudication, or defended thesis is required. The structured response format provides scannable subsections across all 8 domains with tables and bullet points. Light tier is appropriate: ~30-40 min, single-pass drafting, no adversarial critics needed.

## Wrapper Requirements

None specified. Standard output at research/notes/final_report_b2b-saas-ui-patterns-4e1498.md.
