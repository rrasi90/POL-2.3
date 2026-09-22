# POL MVP

Clean MVP implementation under Master Build Instruction.

## Artifacts (Phase 0 / BUILD GATE 0)

| File | Purpose |
|------|---------|
| [BUILD_PLAN.md](./BUILD_PLAN.md) | Phases, out-of-scope, coverage snapshots |
| [MVP_SCREEN_MATRIX.md](./MVP_SCREEN_MATRIX.md) | Every screen: route, role, APIs, source, status |
| [MVP_API_MAP.md](./MVP_API_MAP.md) | REAL / CONTRACT / MOCK / GAP endpoints + envelope |
| [MVP_KNOWN_GAPS.md](./MVP_KNOWN_GAPS.md) | Conflicts, gaps, blocked_external |

## Layout

```text
mvp/
├── apps/web/       # Next.js 15 (Phase 1–2)
├── apps/mobile/    # Expo (Phase 3)
└── packages/
    ├── tokens/     # Precision Commerce tokens (shared)
    ├── types/      # Domain types from API contract (shared)
    ├── api-client/ # HTTP + envelope (shared)
    ├── config/     # tsconfig / lint (shared)
    └── ui/         # Shared primitives only where semantics+a11y hold
```

**Layer order:** `config/tokens/types → api-client/auth → state/query → feature → ui/page`  
**analytics:** cross-cutting

## Commands

```bash
npm install
npm run typecheck
npm run build
```

## Authority

Master Build Instruction → DECISION_REGISTER → canonical product docs (see MVP_KNOWN_GAPS / SCREEN_MATRIX sources).
