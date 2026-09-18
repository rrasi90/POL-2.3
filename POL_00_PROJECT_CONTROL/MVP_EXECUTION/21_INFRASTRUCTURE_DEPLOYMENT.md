# 21. Infrastructure / Deployment

## Purpose
این سند execution contract بخش متناظر در Master است.

## Canonical scope
# 21. Infrastructure / Deployment

## Current repository gap
Deployment artifacts such as `Dockerfile`, `docker-compose.yml`, `pyproject.toml` and production frontend tree are not present in current branch tree.

## Required
- [ ] production backend packaging
- [ ] Python runtime pinning
- [ ] Uvicorn process
- [ ] reverse proxy / TLS
- [ ] environment configuration
- [ ] secret management
- [ ] PostgreSQL 18 deployment
- [ ] Redis deployment if selected
- [ ] worker process
- [ ] scheduler
- [ ] migration job
- [ ] health endpoint
- [ ] readiness endpoint
- [ ] liveness checks
- [ ] staging environment
- [ ] production/pilot environment
- [ ] domain configuration
- [ ] CORS policy
- [ ] request size limits
- [ ] timeout policy
- [ ] connection pooling
- [ ] DB credential rotation
- [ ] TLS certificate renewal
- [ ] deployment rollback path

---

## Open work
- [ ] production backend packaging
- [ ] Python runtime pinning
- [ ] Uvicorn process
- [ ] reverse proxy / TLS
- [ ] environment configuration
- [ ] secret management
- [ ] PostgreSQL 18 deployment
- [ ] Redis deployment if selected
- [ ] worker process
- [ ] scheduler
- [ ] migration job
- [ ] health endpoint
- [ ] readiness endpoint
- [ ] liveness checks
- [ ] staging environment
- [ ] production/pilot environment
- [ ] domain configuration
- [ ] CORS policy
- [ ] request size limits
- [ ] timeout policy
- [ ] connection pooling
- [ ] DB credential rotation
- [ ] TLS certificate renewal
- [ ] deployment rollback path

## Decisions required
1. staging/pilot topology.
2. worker/Redis/runtime topology.
3. deployment/rollback/migration execution.

## Dependencies
- [ ] `03_GOVERNANCE_REVIEW`
- [ ] `22_SECURITY_HARDENING`
- [ ] `23_OBSERVABILITY`

## Acceptance Gate
- [ ] تمام کارهای باز بسته یا با دلیل رسمی NOT APPLICABLE شده‌اند.
- [ ] contradiction باز در این حوزه وجود ندارد.
- [ ] تست/verification مناسب اجرا و evidence ثبت شده است.
- [ ] اگر client-facing است: HTTP + Auth + tenant isolation + failure states تست شده‌اند.
- [ ] commit SHA نهایی قابل اشاره است.

## Execution rules
- business rule جدید بدون Decision ID ممنوع.
- SSoTهای repository از این فایل مقدم‌اند.
- GREEN* domain evidence با production-ready اشتباه نشود.
- failure را با حذف/کاهش تست پنهان نکن.

## Status
NOT STARTED / IN PROGRESS / BLOCKED / VERIFIED / CLOSED
