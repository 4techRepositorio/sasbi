#!/usr/bin/env bash
# Réplica local do workflow e2e-storage-warn-browser-dispatch:
# SQLite (por omissão), API :8765, ng :4200 com proxy, Playwright context-storage-ui.
# Pré-requisitos: deps em apps/web e e2e (npm install / npm ci), Chromium (playwright install).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DEFAULT_DB="sqlite:////tmp/fourpro_e2e_warn_local.db"
export DATABASE_URL="${DATABASE_URL:-$DEFAULT_DB}"
export JWT_SECRET="${JWT_SECRET:-local-browser-storage-warn-jwt-secret-32chars}"
export UPLOAD_DIR="${UPLOAD_DIR:-/tmp/fourpro_uploads_warn_local}"
export PLAYWRIGHT_BASE_URL="${PLAYWRIGHT_BASE_URL:-http://127.0.0.1:4200}"
export E2E_USER_EMAIL="${E2E_USER_EMAIL:-admin@local.dev}"
export E2E_USER_PASSWORD="${E2E_USER_PASSWORD:-changeme}"
export E2E_EXPECT_STORAGE_WARN="${E2E_EXPECT_STORAGE_WARN:-1}"

PY="${ROOT}/apps/api/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="python3"
fi

API_LOG="${TMPDIR:-/tmp}/fourpro-api-local-warn.log"
NG_LOG="${TMPDIR:-/tmp}/fourpro-ng-local-warn.log"
API_PID=""
NG_PID=""

cleanup() {
  if [[ -n "${NG_PID}" ]]; then kill "${NG_PID}" 2>/dev/null || true; fi
  if [[ -n "${API_PID}" ]]; then kill "${API_PID}" 2>/dev/null || true; fi
  DATABASE_URL="$DATABASE_URL" JWT_SECRET="$JWT_SECRET" "$PY" "$ROOT/scripts/cleanup_e2e_storage_seed.py" || true
}
trap cleanup EXIT

mkdir -p "$UPLOAD_DIR"
if [[ "$DATABASE_URL" == "$DEFAULT_DB" ]]; then
  rm -f /tmp/fourpro_e2e_warn_local.db
fi

(
  cd "$ROOT/apps/api"
  "$PY" -m alembic upgrade head
  "$PY" -m fourpro_api.dev_seed
)
"$PY" "$ROOT/scripts/seed_e2e_storage_warn.py"

API_PID=$(
  cd "$ROOT/apps/api"
  nohup "$PY" -m uvicorn fourpro_api.main:app --host 127.0.0.1 --port 8765 >"$API_LOG" 2>&1 &
  echo $!
)

ok=""
for _ in $(seq 1 40); do
  if curl -sf http://127.0.0.1:8765/api/v1/health >/dev/null; then
    ok=1
    break
  fi
  sleep 1
done
if [[ -z "$ok" ]]; then
  echo "API não arrancou (ver $API_LOG)" >&2
  cat "$API_LOG" >&2 || true
  exit 1
fi

if [[ ! -f "$ROOT/apps/web/node_modules/@angular/cli/bin/ng.js" ]]; then
  echo "Instale dependências: cd apps/web && npm ci" >&2
  exit 1
fi

NG_PID=$(
  cd "$ROOT/apps/web"
  nohup node node_modules/@angular/cli/bin/ng.js serve --host 127.0.0.1 --port 4200 \
    --proxy-config proxy.conf.e2e-storage-warn.json >"$NG_LOG" 2>&1 &
  echo $!
)

ok=""
for _ in $(seq 1 90); do
  if curl -sf http://127.0.0.1:4200/api/v1/health >/dev/null; then
    ok=1
    break
  fi
  sleep 2
done
if [[ -z "$ok" ]]; then
  echo "ng serve não respondeu (ver $NG_LOG)" >&2
  cat "$NG_LOG" >&2 || true
  exit 1
fi

(
  cd "$ROOT/e2e"
  npx playwright test tests/context-storage-ui.spec.ts
)
