# POL — Self-Hosted VPS Deployment

Production website hosting is on the POL VPS; Vercel remains a separate QA target.

## Stack

- Nginx edge on port 80.
- Next.js 15 web on internal port 3001.
- FastAPI/Uvicorn on internal port 8000.
- PostgreSQL 18 on the internal Docker network, with TLS enabled.
- Python worker service using the canonical PostgreSQL transactional-outbox model.
- External S3-compatible object storage for media and binary documents.
- Redis is intentionally omitted from the initial stack because it is optional for the canonical MVP.

## First deployment

On the VPS:

```bash
cd /srv/pol/POL-2.3
git fetch origin
git checkout deploy/vps-self-hosted-20260928
git pull --ff-only origin deploy/vps-self-hosted-20260928
cp .env.vps.example .env
nano .env
```

Set real secrets before starting the stack. Never commit the `.env` file.

Validate:

```bash
docker compose --env-file .env -f docker-compose.vps.yml config
```

Build and start:

```bash
docker compose --env-file .env -f docker-compose.vps.yml build
docker compose --env-file .env -f docker-compose.vps.yml up -d
```

The `migrate` service is one-shot and forward-only. It refuses to bootstrap a non-empty database without deployment migration history.

## Verification

```bash
docker compose --env-file .env -f docker-compose.vps.yml ps
docker compose --env-file .env -f docker-compose.vps.yml logs --tail=100 migrate
docker compose --env-file .env -f docker-compose.vps.yml logs --tail=100 api
docker compose --env-file .env -f docker-compose.vps.yml logs --tail=100 worker
curl -fsS http://127.0.0.1/healthz
curl -fsS http://127.0.0.1/readyz
curl -I http://127.0.0.1/
```

Public routing:

- `http://<VPS-IP>/` → Next.js
- `http://<VPS-IP>/api/v1/*` → FastAPI

## HTTPS gate

Do not change `ENVIRONMENT` to `production` until a real hostname is attached and TLS is configured at Nginx.

After DNS points to the VPS, configure Nginx for 443/ACME and set `POL_CORS_ORIGINS` to the exact HTTPS application origin.

FastAPI intentionally emits HSTS only in `ENVIRONMENT=production`.

## Object storage

Keep product images, invoice binaries, POD images, payment evidence, and dispute/support attachments in S3-compatible object storage rather than the VPS root disk.

## Safety boundary

Do not use `scripts/bootstrap_env.py --reset`, the destructive reset path in `scripts/migration_runner.py`, or `pol_test` for this deployment.

The production migration service is `python -m scripts.migrate_prod`.
