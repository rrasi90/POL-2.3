#!/usr/bin/env bash
set -Eeuo pipefail

# POL self-hosted VPS deployment operator.
# Safe-by-default:
# - never drops/removes the PostgreSQL volume
# - never runs destructive bootstrap/reset paths
# - verifies the exact deployment ref before building
# - stops on build, migration, or readiness failure
# - writes an inspectable deployment log

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BRANCH="${POL_DEPLOY_BRANCH:-deploy/vps-self-hosted-20260928}"
COMPOSE=(docker compose --env-file .env -f docker-compose.vps.yml)
LOG_DIR="${POL_DEPLOY_LOG_DIR:-$ROOT_DIR/deploy/logs}"
LOCK_FILE="${POL_DEPLOY_LOCK_FILE:-$ROOT_DIR/deploy/.deploy.lock}"
WAIT_SECONDS="${POL_DEPLOY_WAIT_SECONDS:-180}"
PUBLIC_BASE_URL="${POL_PUBLIC_BASE_URL:-}"

mkdir -p "$LOG_DIR"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[DEPLOY] another deployment is already running: $LOCK_FILE" >&2
  exit 20
fi

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_FILE="$LOG_DIR/deploy-$TIMESTAMP.log"
exec > >(tee -a "$LOG_FILE") 2>&1

on_error() {
  rc=$?
  echo
  echo "[DEPLOY] FAILED rc=$rc"
  echo "[DEPLOY] commit: $(git rev-parse HEAD 2>/dev/null || echo unknown)"
  echo "[DEPLOY] recent service state:"
  "${COMPOSE[@]}" ps || true
  echo "[DEPLOY] recent logs:"
  "${COMPOSE[@]}" logs --no-color --tail=80 api worker web nginx || true
  echo "[DEPLOY] log: $LOG_FILE"
  exit "$rc"
}
trap on_error ERR

die() {
  echo "[DEPLOY] ERROR: $*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing command: $1"
}

echo "[DEPLOY] === POL VPS Deployment Operator ==="
echo "[DEPLOY] root=$ROOT_DIR"
echo "[DEPLOY] branch=$BRANCH"
echo "[DEPLOY] log=$LOG_FILE"

require_cmd git
require_cmd docker
require_cmd flock
require_cmd curl

[[ -f .env ]] || die ".env is missing"
[[ -f docker-compose.vps.yml ]] || die "docker-compose.vps.yml is missing"

echo "[DEPLOY] validating required environment without printing secrets"
for key in POL_DB_USER POL_DB_PASSWORD POL_JWT_SECRET; do
  value="$(grep -E "^$key=" .env | head -n1 | cut -d= -f2- || true)"
  [[ -n "$value" ]] || die "$key is missing/empty in .env"
done

echo "[DEPLOY] fetching exact deployment ref"
git fetch origin "refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"

echo "[DEPLOY] checkout exact remote branch"
git checkout -B "$BRANCH" "origin/$BRANCH"

HEAD="$(git rev-parse HEAD)"
REMOTE_HEAD="$(git rev-parse "origin/$BRANCH")"
[[ "$HEAD" == "$REMOTE_HEAD" ]] || die "local HEAD does not match origin/$BRANCH"

echo "[DEPLOY] HEAD=$HEAD"

echo "[DEPLOY] validating compose configuration"
"${COMPOSE[@]}" config >/dev/null

echo "[DEPLOY] building deployment images"
"${COMPOSE[@]}" build

echo "[DEPLOY] starting PostgreSQL only"
"${COMPOSE[@]}" up -d postgres

echo "[DEPLOY] waiting for PostgreSQL health"
deadline=$((SECONDS + WAIT_SECONDS))
while true; do
  status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' pol-23-postgres-1 2>/dev/null || true)"
  case "$status" in
    healthy)
      echo "[DEPLOY] PostgreSQL healthy"
      break
      ;;
    unhealthy)
      die "PostgreSQL became unhealthy"
      ;;
    exited|dead)
      die "PostgreSQL exited (status=$status)"
      ;;
  esac

  (( SECONDS >= deadline )) && die "timeout waiting for PostgreSQL health"
  sleep 3
done

echo "[DEPLOY] applying forward-only production migrations"
"${COMPOSE[@]}" run --rm migrate

echo "[DEPLOY] starting API/worker/web/nginx"
"${COMPOSE[@]}" up -d api worker web nginx

echo "[DEPLOY] verifying container state"
"${COMPOSE[@]}" ps

echo "[DEPLOY] verifying internal readiness"
curl -fsS --max-time 15 http://127.0.0.1/healthz
printf '\\n'
curl -fsS --max-time 15 http://127.0.0.1/readyz
printf '\\n'
curl -fsSI --max-time 15 http://127.0.0.1/
printf '\\n'

if [[ -n "$PUBLIC_BASE_URL" ]]; then
  echo "[DEPLOY] verifying public URL: $PUBLIC_BASE_URL"
  curl -fsS --max-time 20 "$PUBLIC_BASE_URL/healthz"
  printf '\\n'
  curl -fsS --max-time 20 "$PUBLIC_BASE_URL/readyz"
  printf '\\n'
  curl -fsSI --max-time 20 "$PUBLIC_BASE_URL/"
  printf '\\n'
fi

echo "[DEPLOY] === PASS ==="
echo "[DEPLOY] commit=$HEAD"
echo "[DEPLOY] log=$LOG_FILE"
