# POL-2.3 Vercel QA Transfer Manifest

Baseline: POL-2.3 @ e7e6464 (2026-09-24 verification baseline)

## Purpose

This branch is a safe QA staging source for a one-month Vercel frontend test cycle.

It must not connect to:
- PostgreSQL
- production FastAPI
- production secrets
- real payment systems

## Transfer set for a future standalone repository

Copy these parts from `mvp/`:
- `apps/web/**`
- `packages/config/**`
- `packages/tokens/**`
- `packages/types/**`
- `packages/api-client/**`
- `packages/ui/**`
- `package.json`
- `package-lock.json`
- `tsconfig.base.json`
- `vercel.json`

Do not copy:
- `apps/mobile/**`
- `mvp/` backend code (none is required by the mock web runtime)
- root migrations
- PostgreSQL/bootstrap scripts
- secrets or real environment files

QA-only additions:
- `apps/web/src/app/api/v1/[...path]/route.ts`
- `apps/web/src/app/dev/qa/page.tsx`
- `apps/web/.env.example` with empty API base
- browser QA cookies: `pol.qa.role`, `pol.qa.delay`, `pol.qa.fail`, `pol.qa.dataset`, `pol.qa.unauthorized`

## Vercel configuration

Recommended project root: `mvp`

Environment:
`NEXT_PUBLIC_API_BASE_URL=` (empty)

Do not add a real API URL to this project.

## Main safety rule

`main` was not modified by this QA work. All changes are isolated on the `vercel-qa` branch.
