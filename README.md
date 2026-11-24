# POL — Multi-Vendor B2B Commerce Platform

POL (پُل) is a B2B commerce and operations platform designed to connect FMCG retailers with wholesalers through a shared digital marketplace. It brings product discovery, multi-vendor procurement, inventory coordination, order fulfilment, proof of delivery, payment evidence, support, and platform operations into one system.

This repository contains the product and architecture knowledge base, Python API and domain services, web and mobile applications, database migrations, automated verification, and deployment tooling.

> **Project status:** This repository is actively developed. A feature represented in a product model, API contract, UI, or test suite is not automatically certified for production use. Check the current release-readiness and integration records before deploying or making operational commitments.

- **Repository:** [rrasi90/POL-2.3](https://github.com/rrasi90/POL-2.3)
- **Primary branch:** `main`
- **Product domain:** B2B FMCG wholesale and retail commerce
- **Primary pilot context in product documentation:** Ahvaz, Iran

---

## 1. Product scope

POL is designed for a multi-vendor purchasing model. A retailer can prepare a unified basket while the platform allocates requested products to eligible vendors and manages the resulting vendor-specific orders.

### Main user groups

| User group | Main responsibilities |
|---|---|
| Retailer owners and staff | Discover products, maintain a basket, submit orders, track deliveries, confirm receipt, provide payment evidence, and contact support |
| Vendor owners and staff | Manage product offers, prices, and inventory; review and fulfil orders; provide dispatch and delivery information |
| Platform operations and administrators | Manage catalog quality, monitor operational exceptions, support users, resolve disputes, and oversee platform configuration |
| Field activators | Register retailer leads, verify store information, support onboarding, and record field visits |
| Background workers | Process outbox events, notifications, retention, reconciliation, reservation expiry, and other scheduled or asynchronous work |

### Business capabilities

- **Catalog and merchandising:** product catalog, categories, brands, identifiers, vendor offers, and product-candidate review.
- **Vendor pricing and inventory:** vendor-specific prices, price history, inventory availability, and reservations.
- **Unified basket and allocation:** multi-vendor basket management, allocation plans, vendor minimums, and checkout revalidation.
- **Orders and fulfilment:** order groups, vendor orders, acceptance and timeout rules, packing, dispatch, delivery tracking, and proof of delivery.
- **Payments and financial operations:** direct retailer-to-vendor payment flows, payment evidence, reconciliation, invoices, settlements, disputes, and refunds.
- **Notifications and inbox:** durable in-app inbox records, user preferences, asynchronous SMS/push delivery, retry handling, and retention.
- **Support and field operations:** support cases, assignments, field tasks, and operational follow-up.
- **Administration and audit:** role-based access, tenant boundaries, exception queues, audit events, and operational reporting.

POL's documented payment model is **non-custodial direct settlement**: the platform coordinates commerce and records evidence; it is not designed as a wallet that holds customer funds.

---

## 2. Architecture at a glance

The backend follows a layered request and domain flow:

~~~text
Web / Mobile Client
       |
       v
FastAPI HTTP API
       |
       v
Authentication, Session and Tenant Context
       |
       v
Application Boundary
       |
       v
Canonical Domain Services
       |
       v
PostgreSQL Transaction
       |
       +----> Domain / Outbox Events
                    |
                    v
             Background Workers
                    |
          +---------+----------+
          |         |          |
          v         v          v
        SMS/Push  Reconciliation  Other async jobs
~~~

### Architectural principles

1. **PostgreSQL is the canonical data store.** The current mainline migration chain contains ordered SQL migrations `001` through `076`. PostgreSQL 18 is the documented canonical database target.
2. **Tenant isolation is a security boundary.** Business data is scoped to organizations. API and database operations must enforce the active organization context and relevant membership permissions.
3. **The application boundary owns business operations.** HTTP routes should remain transport-focused and delegate to canonical application/domain services rather than duplicating business rules.
4. **Transactional state changes and event publication are coordinated.** Outbox records are written with business changes; background workers handle external delivery and asynchronous processing.
5. **External providers are isolated.** SMS, push, and S3-compatible object storage are configured through adapters and environment settings. Provider failures must not silently corrupt core commerce transactions.
6. **Integrity is enforced at multiple levels.** Validation, idempotency, foreign keys, check constraints, uniqueness rules, tenant ownership, and concurrency controls protect important state transitions.
7. **Evidence is SHA-specific.** A passing test result applies to the exact source revision and environment recorded with that evidence. It must not be presented as blanket certification of later commits.

### Important domain boundaries

| Domain | Typical responsibilities |
|---|---|
| Identity and membership | Users, organizations, memberships, sessions, authentication, and role/permission checks |
| Catalog | Products, categories, brands, identifiers, vendor products, and product media |
| Pricing and inventory | Vendor price versions, stock availability, inventory history, and reservations |
| Commerce | Baskets, allocation, checkout, order groups, orders, and invoices |
| Fulfilment | Vendor acceptance, delivery state, driver information, proof of delivery, and delivery OTP |
| Finance and trust | Payment evidence, reconciliation, settlements, disputes, and refunds |
| Platform services | Notifications, inbox, support, field tasks, audit, and operational monitoring |

---

## 3. Technology stack

| Layer | Technology used in the repository |
|---|---|
| Backend language | Python 3.11 runtime in the API container |
| HTTP API | FastAPI and Uvicorn |
| Database | PostgreSQL 18 |
| Python database driver | psycopg2-binary |
| Web application | Next.js 15, React 19, TypeScript |
| Web state and styling | Zustand and Tailwind CSS |
| Mobile application | Expo SDK 57, React Native 0.86, React 19 |
| Web browser testing | Playwright |
| Python testing | pytest and repository verification scripts |
| Reverse proxy / deployment | Nginx, Docker Compose |
| Media storage integration | S3-compatible object storage |
| Background processing | Python worker processes and scheduled jobs |

The web monorepo requires Node.js `>=22.13.0`. The mobile workspace uses versions pinned in `mvp/apps/mobile/package.json`; do not independently upgrade React, React Native, or Expo without checking the compatibility matrix and lockfile.

---

## 4. Repository layout

This repository intentionally contains both executable software and its product/engineering knowledge base.

~~~text
POL-2.3/
├── .github/workflows/           # GitHub Actions workflows
├── .agents/                     # Agent rules and repository skills
├── 00_PROJECT_OVERVIEW/         # Product and project overview
├── 01_RESEARCH/                 # Market and product research
├── 02_STRATEGY/                 # Strategy
├── 03_CUSTOMERS/                # Customer and segment knowledge
├── 04_VALUE_PROPOSITION/        # Value proposition
├── 05_BUSINESS_MODEL/           # Business model
├── 06_PRODUCT/                  # Product scope, contracts, architecture
├── 07_ALGORITHMS/               # Allocation and domain algorithms
├── 08_DATA/                     # Data and domain models
├── 09_OPERATIONS/               # Operational model
├── 10_GO_TO_MARKET/             # Go-to-market
├── 11_PILOT/                    # Pilot planning
├── 12_ROADMAP/                  # Product roadmap
├── 13_PRODUCT_DESIGN/           # UX, design system and implementation specs
├── POL_00_PROJECT_CONTROL/      # Canonical decisions, controls and source of truth
├── analysis/integration/        # PR, branch, test and release evidence
├── migrations/                  # Ordered PostgreSQL SQL migrations
├── scripts/
│   ├── api/                     # FastAPI application and route modules
│   └── ...                      # Domain services, workers, tests and tooling
├── mvp/
│   ├── apps/
│   │   ├── web/                 # Next.js web application
│   │   └── mobile/              # Expo / React Native applications
│   ├── packages/
│   │   ├── api-client/
│   │   ├── config/
│   │   ├── tokens/
│   │   ├── types/
│   │   └── ui/
│   ├── BUILD_PLAN.md
│   ├── MVP_API_MAP.md
│   ├── MVP_KNOWN_GAPS.md
│   └── MVP_SCREEN_MATRIX.md
├── deploy/                      # Dockerfiles, Nginx and deployment scripts
├── docker-compose.vps.yml        # Self-hosted stack
├── requirements.txt              # Python runtime dependencies
└── requirements-dev.txt           # Python development/test dependencies
~~~

### Where to start reading

| Question | Recommended document |
|---|---|
| What is the platform and how is it structured? | `POL_00_PROJECT_CONTROL/MASTER_SYSTEM_ARCHITECTURE.md` |
| Which decisions are authoritative? | `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md` |
| What is the current source of truth? | `POL_00_PROJECT_CONTROL/CURRENT_SOURCE_OF_TRUTH.md` |
| What is the database schema and migration head? | `POL_00_PROJECT_CONTROL/DATABASE_SCHEMA_MANIFEST.md` and `migrations/` |
| What is in the MVP? | `mvp/BUILD_PLAN.md` |
| Which screens are covered? | `mvp/MVP_SCREEN_MATRIX.md` |
| Which API endpoints are real, contractual, mocked, or missing? | `mvp/MVP_API_MAP.md` |
| What gaps remain? | `mvp/MVP_KNOWN_GAPS.md` |
| What is the current integration history? | `analysis/integration/PR_INVENTORY.md` and `BRANCH_INVENTORY.md` |
| What test evidence and release gates exist? | `analysis/integration/TEST_EVIDENCE_INDEX.md` and `RELEASE_READINESS.md` |

When documents disagree, follow the repository's canonical decision and source-of-truth records. Historical audit reports should be read as dated evidence, not as current implementation instructions.

---

## 5. Prerequisites

For local development, prepare:

- Python 3.11 or a compatible later version for local tooling.
- Node.js 22.13 or later and npm.
- PostgreSQL 18 for database-backed development and verification.
- Git.
- Docker and Docker Compose for containerized deployment or isolated service testing.
- Playwright browser binaries when running browser E2E tests.

The API, worker, web, and mobile clients require their respective configuration and dependencies. Do not point local test or migration tooling at a shared, staging, or production database.

---

## 6. Install dependencies

### Python

From the repository root:

~~~bash
python -m venv .venv
~~~

Activate the virtual environment:

~~~bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
~~~

Install runtime and development dependencies:

~~~bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
~~~

### JavaScript workspaces

Install all JavaScript workspace dependencies from the monorepo root:

~~~bash
cd mvp
npm ci
~~~

Use the committed lockfile. Avoid ad hoc package installation or changing dependency versions to make a local command pass.

---

## 7. Local development

### Backend API

The FastAPI application is exposed from `scripts.api.main:app`.

Before starting it, configure a reachable PostgreSQL database and the application environment. The API reads its database configuration from variables including:

- `POL_API_DB_NAME`
- `POL_API_DB_HOST`
- `POL_API_DB_PORT`
- `POL_API_DB_USER`
- `POL_API_DB_PASSWORD`
- `POL_API_DB_SSLMODE`
- `POL_JWT_SECRET`
- `POL_CORS_ORIGINS`
- `ENVIRONMENT`

Use a local development database and a non-production signing secret. Never commit real credentials.

Start the API from the repository root:

~~~bash
uvicorn scripts.api.main:app --host 127.0.0.1 --port 8000
~~~

In non-production environments, FastAPI exposes its OpenAPI documentation at `/docs` and `/openapi.json`. The API also exposes:

- `GET /healthz` — process health.
- `GET /readyz` — database-backed readiness check.

The readiness endpoint requires a valid database connection; a successful process health check alone does not prove that the application is ready to serve requests.

### Background worker

The worker runtime is started with:

~~~bash
python -m scripts.worker_runtime
~~~

The worker entry point explicitly requires `ENVIRONMENT=production` and an appropriate database/provider configuration. It is responsible for asynchronous processing; do not run multiple workers with unreviewed configuration or assume an external provider is connected merely because the worker starts.

### Web application

From the repository root:

~~~bash
cd mvp
npm run dev --workspace=@pol/web
~~~

The web application uses shared workspace packages and the API base URL configured for the selected environment.

Useful web commands:

~~~bash
npm run typecheck --workspace=@pol/web
npm run lint --workspace=@pol/web
npm run build --workspace=@pol/web
npm run test:e2e --workspace=@pol/web
~~~

### Mobile applications

The mobile workspace contains separate retailer and vendor entry points:

- `mvp/apps/mobile/AppRetailer.tsx`
- `mvp/apps/mobile/AppVendor.tsx`

Start Expo from the monorepo root:

~~~bash
cd mvp
npm start --workspace=@pol/mobile
~~~

Native development commands:

~~~bash
npm run ios --workspace=@pol/mobile
npm run android --workspace=@pol/mobile
~~~

The mobile package also defines retailer/vendor APK and AAB build commands. Release builds are subject to the repository's fail-closed pre-build and device-QA gates. Do not bypass TODO-084 or treat an old APK in the repository as a current release artifact.

---

## 8. Database and migrations

The current mainline database migration chain is numbered `001` through `076`. Migrations are ordered, forward-only changes to the canonical PostgreSQL schema.

### Important safety rule

`python scripts/migration_runner.py` is a **test-database tool**. It targets `pol_test` by default and resets that database's public schema before applying the discovered migration chain. Use it only against a disposable, isolated test database. Never point it at a shared, staging, or production database.

For production-style deployments, the Compose migration service runs:

~~~bash
python -m scripts.migrate_prod
~~~

The production migration path is forward-only and has separate safeguards. Do not use test bootstrap/reset scripts as a production migration mechanism.

After preparing an isolated test database, the environment verifier can be run with:

~~~bash
python scripts/verify_environment.py --json
~~~

---

## 9. Automated verification

The repository has multiple verification layers. Run the relevant layers for the code you change and record the exact commit SHA and environment.

### Python verification suite

~~~bash
python scripts/run_verification_suite.py
~~~

This suite exercises backend contracts, database integrity, route behavior, permissions, concurrency, and other repository-level invariants. It requires a working isolated PostgreSQL test environment and the test configuration expected by the scripts.

### JavaScript workspace checks

From `mvp/` after `npm ci`:

~~~bash
npm run typecheck
npm run lint
npm run build
npm run test
~~~

### Browser end-to-end tests

From `mvp/apps/web/`:

~~~bash
npx playwright install chromium
npx playwright test
~~~

Use the repository's Playwright configuration and its documented API/web test setup. Do not substitute mocked tests for a test that is intended to exercise the real API.

### Mobile checks

From `mvp/`:

~~~bash
npm run qa:functional --workspace=@pol/mobile
npm run qa:regression --workspace=@pol/mobile
npm run qa:mock --workspace=@pol/mobile
npm run qa:pre-apk --workspace=@pol/mobile
~~~

The live API preflight is a separate lane and requires an explicitly configured environment. Mock QA is not evidence of live-provider, staging, or physical-device acceptance.

### Evidence and artifacts

The main backend verification runner writes `artifacts/pol-test-results.json`. The GitHub Actions verification workflow also publishes a SHA-specific evidence report and failure inventory when those outputs are available.

A CI result is meaningful only when the runner actually executed the job steps. Review the run summary, job steps, tested SHA, and uploaded artifacts; do not treat a workflow with no runner execution as a successful test.

---

## 10. Configuration and secrets

Use `.env.vps.example` as a reference for the containerized VPS configuration. It contains placeholders, not usable credentials.

Configuration categories include:

| Category | Example variables |
|---|---|
| Runtime mode | `ENVIRONMENT` |
| Database | `POL_DB_USER`, `POL_DB_PASSWORD`, `POL_API_DB_*`, `POL_PG_DSN` |
| Authentication | `POL_JWT_SECRET` |
| Web/API routing | `NEXT_PUBLIC_API_BASE_URL`, `POL_CORS_ORIGINS` |
| Object storage | `POL_S3_ENDPOINT_URL`, `POL_S3_ACCESS_KEY_ID`, `POL_S3_SECRET_ACCESS_KEY`, `POL_S3_BUCKET` |
| SMS | `POL_SMS_PROVIDER`, `POL_SMS_ENDPOINT`, `POL_SMS_TOKEN` |
| Push | `POL_PUSH_PROVIDER`, `POL_PUSH_ENDPOINT`, `POL_PUSH_TOKEN` |
| Worker tuning | `POL_WORKER_INTERVAL_SECONDS`, `POL_WORKER_BATCH_SIZE` |

Store real secrets in an authorized secret manager or deployment environment. Never place credentials in source code, tracked environment files, logs, screenshots, test artifacts, or README examples. Do not print secret values when diagnosing configuration problems.

---

## 11. Deployment

The repository includes a self-hosted Docker Compose deployment:

- PostgreSQL 18
- One-shot migration service
- FastAPI application
- Background worker
- Next.js web application
- Nginx reverse proxy

The deployment definition is in `docker-compose.vps.yml`; the operational guide is `deploy/VPS_DEPLOYMENT.md`.

Validate a configured deployment before starting it:

~~~bash
docker compose --env-file .env -f docker-compose.vps.yml config
~~~

The repository's deployment script is:

~~~bash
bash deploy/vps_deploy.sh
~~~

Read the deployment guide and review the exact target environment before using either command. The example environment file contains placeholder credentials and must be completed securely.

### Production and staging gates

A successful image build or container startup is not production certification. Before a production deployment, independently verify:

- Exact commit SHA and current migration state.
- Database backup and recovery procedure.
- Strong credentials and encrypted database connections.
- Real domain, HTTPS/TLS, and exact CORS origins.
- Object storage access and media lifecycle.
- SMS/push provider credentials and acceptance tests.
- API, worker, and web readiness.
- Staging smoke, security checks, and rollback procedure.
- Required owner, business, and operational approvals.

Vercel-related material in this repository is a separate mock/QA workstream. It must not be treated as a production deployment path or connected to production data unless its isolation and authorization have been independently reviewed.

---

## 12. Security and data-integrity rules

- Enforce organization/tenant ownership for every tenant-scoped operation.
- Apply authorization at the application boundary; do not trust client-supplied role or organization identifiers.
- Keep authentication, session, refresh-token, and OTP behavior aligned with the canonical decision register.
- Preserve idempotency for checkout, payment, fulfilment, and asynchronous delivery operations.
- Keep money and order state transitions transactional and auditable.
- Use the outbox pattern for external side effects; do not send provider requests inside a business transaction.
- Store binary media in configured object storage and persist its metadata/provenance in the application.
- Treat audit and inventory history as controlled records; do not bypass append-only or retention rules.
- Never run destructive test or bootstrap commands against a non-test database.
- Never commit secrets, production data, private user information, or unreviewed generated artifacts.

Security and architecture decisions are maintained in `POL_00_PROJECT_CONTROL/DECISION_REGISTER.md`, the canonical contract documents, and the migration history. Update those sources when a decision changes; do not silently introduce a competing contract in a feature branch.

---

## 13. Branch and contribution workflow

Before creating or merging a change:

1. Read the current source-of-truth and decision-register documents relevant to the change.
2. Inspect open pull requests and the branch inventory to avoid duplicating work that has already been merged, superseded, or intentionally archived.
3. Keep changes focused and preserve the canonical architecture and API contracts.
4. Add or update tests for behavior, security, tenant isolation, state transitions, and migrations affected by the change.
5. Run the relevant local verification layers and record the tested SHA.
6. Review CI job steps and artifacts. A failed job with missing prerequisites is not a passing check; a job that never ran provides no test evidence.
7. Do not delete retained backup, archive, or policy-blocked branches without checking their documented disposition and recovery evidence.

For database changes, add a new forward-only migration. Do not edit an already released migration to change historical behavior unless the repository's migration policy explicitly permits it.

For policy changes, update the decision register, contracts, implementation, test expectations, and relevant documentation together.

---

## 14. Current readiness and known limitations

The project deliberately separates implementation progress from release authorization. The following evidence categories must remain distinct:

- **Automated tests:** backend, static, web, mobile, and browser suites on a specific SHA.
- **Device QA:** installed retailer/vendor builds tested on supported physical devices or emulators.
- **Staging:** exact-SHA deployment with database, API, worker, web, and integration smoke tests.
- **Live-provider acceptance:** real SMS, push, object storage, and other external service checks.
- **Business/legal readiness:** operational policies, payment terms, contracts, and pilot approvals.

Consult `analysis/integration/RELEASE_READINESS.md` and `analysis/integration/TEST_EVIDENCE_INDEX.md` for the dated, SHA-scoped evidence and unresolved gates. Those documents are audit records; refresh them when new evidence is generated. Do not infer current certification from an older passing run.

---

## 15. License and third-party assets

Review the applicable license and attribution requirements for each source directory, third-party dependency, font, image, and design asset before redistribution. A license file in one subdirectory does not automatically grant rights to every asset in the repository.

---

## 16. Maintainer notes

This repository is both a software codebase and a long-lived product knowledge base. Keep the executable implementation, contracts, architectural decisions, and audit evidence aligned.

When documenting a feature or claiming that a gate has passed, include enough context for another maintainer to verify the statement: source path, exact commit SHA, command or workflow, environment, result, and known limitations.

For project-specific questions, start with the canonical control documents rather than relying on historical chat summaries or old handoff notes.
