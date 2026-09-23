# Phase 3 Field-first parity matrix (functional, not pixel)

| ID | Web | Mobile | APIs | Notes |
|----|-----|--------|------|-------|
| F-01 | `apps/web/.../field/page.tsx` VERIFIED | `src/screens/FieldTaskListScreen.tsx` | GET `/field/tasks` | list + search |
| F-02 | `field/tasks/[id]/page.tsx` | `FieldTaskDetailScreen` header/meta | GET `/field/tasks/{id}` | activation context |
| F-03 | task → retailer catalog link | `AssistedOrderScreen` | GET `/catalog/search` | basket/checkout remain retailer web |
| F-04 | same detail PATCH form | `FieldTaskDetailScreen` save | PATCH `/field/tasks/{id}` | status + notes ≤2000 |
| F-05 | offline banner on field list | `components/OfflineBanner.tsx` | healthz retry | MVP = status + retry (rich sync P2) |

QA: `npm run typecheck` from `mvp/` (workspace `@pol/mobile`).
No Driver App (D-023). Barcode D-028 not in Field MVP set.
