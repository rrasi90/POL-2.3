# POL-2.3 — VPS Runtime & Post-Deployment Verification Evidence

**Date:** 2026-09-28  
**Repository:** `rrasi90/POL-2.3`  
**Deployment branch:** `deploy/vps-self-hosted-20260928`  
**Deployment environment:** Self-hosted VPS / IP-stage  
**VPS IPv4:** `85.198.50.29`  
**Current reported deployment commit:** `92dfd0b841e14eee75dc426dcea997b3d7befe05`

## Scope

This document records the observed deployment state after the first successful self-hosted VPS deployment and the subsequent deep verification. It is operational evidence for the VPS deployment branch; it does not replace the canonical product decision register and it does not claim HTTPS production cutover.

## Verified stack

- Nginx edge on TCP/80
- Next.js 15 standalone web on internal TCP/3001
- FastAPI/Uvicorn API on internal TCP/8000
- PostgreSQL 18.6 on the internal Docker network with TLS enabled
- Python transactional-outbox worker runtime
- One-shot forward-only production migration runner
- Vercel remains a separate QA target

## Verified deployment state

| Area | Result | Evidence |
|---|---|---|
| Git source | PASS | VPS HEAD matched `origin/deploy/vps-self-hosted-20260928` at reported deployment commit |
| Docker build | PASS | `pol-23-postgres`, `pol-23-migrate`, `pol-23-api`, `pol-23-worker`, `pol-23-web` built successfully |
| PostgreSQL | PASS | PostgreSQL 18.6; container healthy; volume mounted at `/var/lib/postgresql` |
| Migrations | PASS | 76 migration files tracked; migration 076 applied; 108 base tables present |
| API | PASS | FastAPI process remained running; public canonical API smoke returned HTTP 200 |
| Worker | PASS | Long-lived worker runtime remained running without restart loop |
| Web | PASS | Next.js standalone server runs directly from `apps/web/.next/standalone/apps/web/server.js` |
| Nginx | PASS | Port 80 public; `/`, `/healthz`, `/readyz`, and `/api/*` routing verified |
| Health | PASS | Public `/healthz` returned HTTP 200 and `{"status":"ok"}` |
| Readiness | PASS | Public `/readyz` returned HTTP 200 and `{"status":"ready"}` |
| API routing | PASS | `/api/v1/categories` returned HTTP 200 with canonical JSON structure |
| Authentication | PASS | OTP/session/authentication negative and protected-route checks were reported as successful |
| Basket → checkout | PASS | Isolated live business flow reported successful with rollback cleanup |
| Idempotency | PASS | Replay with the same idempotency key returned the stored result rather than creating a duplicate order |
| Outbox → worker | PASS | Test event was processed by the canonical worker path |
| Restart recovery | PASS | API, web, worker, nginx, and PostgreSQL restart checks passed; migrations remained no-op/already-applied |
| Persistence | PASS | Schema and application endpoints survived restart |
| Security baseline | PASS | `.env` not tracked; PostgreSQL/API/Web internal ports not publicly published |
| Vercel separation | PASS | Production runtime is VPS; Vercel remains QA-only |
| HTTPS | PENDING | Real hostname, 443/TLS, and exact HTTPS CORS origin are not yet configured |

## Public HTTP verification

The public IP was reachable from an external Windows client:

- `http://85.198.50.29/healthz` → HTTP 200
- `http://85.198.50.29/readyz` → HTTP 200
- `http://85.198.50.29/api/v1/categories` → HTTP 200
- `http://85.198.50.29/` → HTTP 200 and complete HTML was retrievable

Server-side diagnostics also showed:

- direct Next.js container response = 25,362 bytes
- Nginx/localhost response = 25,362 bytes
- Nginx access logs recorded HTTP 200 with 25,362-byte responses
- no Nginx/Web application error was observed during the diagnostic window

### Network diagnostic note

A repeated Windows download test against the raw IP showed intermittent client-side transfer truncation (several responses ended at 6,798 bytes and one timed out), while direct server-side retrieval remained complete and the same public page also loaded successfully. Packet capture did not show a server-generated FIN/RST for the captured request.

**Interpretation:** this was not reproduced inside Next.js or Nginx and is not currently classified as a POL application failure. It should be rechecked from more than one external network after the HTTPS hostname is attached.

## Current production gate

The VPS runtime is operational at the IP-stage, but the following remain outside this evidence snapshot:

1. Domain DNS cutover for `polmarket.ir`
2. Nginx 443/TLS certificate
3. Exact HTTPS CORS origin
4. Production `ENVIRONMENT=production` gate
5. Final HTTPS end-to-end verification

## Safety boundary

The deployment evidence was obtained without using:

- `scripts/bootstrap_env.py --reset`
- destructive migration reset paths
- `pol_test`
- `docker compose down -v`
- PostgreSQL volume deletion

This document is an evidence snapshot. Future deployments must use the executable deployment operator and generate a new timestamped log/evidence record.
