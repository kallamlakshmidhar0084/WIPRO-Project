#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$PROJECT_ROOT"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

fail() {
  log "ERROR: $*"
  exit 1
}

if [ -f "$PROJECT_ROOT/backend/.env" ]; then
  log "Loading backend/.env..."
  set -a
  # shellcheck disable=SC1091
  source "$PROJECT_ROOT/backend/.env"
  set +a
else
  fail "Missing backend/.env. Create it before starting Docker services."
fi

command -v docker >/dev/null 2>&1 || fail "Docker is not installed or not available on PATH."
docker compose version >/dev/null 2>&1 || fail "Docker Compose is not available. Install Docker Desktop or the docker compose plugin."

log "Starting Docker services: Postgres and pgAdmin..."
log "Postgres will be available at localhost:${DB_PORT:-5432}"
log "pgAdmin will be available at http://localhost:5050"

if ! docker compose --env-file backend/.env up postgres_db pgadmin; then
  log "Docker Compose startup failed. Recent service logs:"
  docker compose --env-file backend/.env logs --tail=120 postgres_db pgadmin || true
  fail "Could not start Postgres and pgAdmin."
fi
