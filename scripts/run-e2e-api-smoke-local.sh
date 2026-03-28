#!/usr/bin/env bash
# Sobe a API (SQLite em memória, sem Alembic), corre smoke Playwright: /health e /health/ready, encerra.
# Paridade com e2e-dispatch e tests/smoke-api.spec.ts.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VENV_PY="${VENV_PY:-$ROOT/.venv/bin/python}"
if [[ ! -x "$VENV_PY" ]]; then
  echo "Sem Python em .venv. Correr: python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt" >&2
  exit 1
fi

PORT="${E2E_LOCAL_API_PORT:-18765}"
cleanup() {
  if [[ -n "${UVICORN_PID:-}" ]] && kill -0 "$UVICORN_PID" 2>/dev/null; then
    kill "$UVICORN_PID" 2>/dev/null || true
    wait "$UVICORN_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

export DATABASE_URL="sqlite:///:memory:"
export JWT_SECRET="${JWT_SECRET:-ci-jwt-secret-at-least-32-characters-long}"
export UPLOAD_DIR="${UPLOAD_DIR:-${TMPDIR:-/tmp}/fourpro_e2e_uploads}"
mkdir -p "$UPLOAD_DIR"

echo "==> Uvicorn 127.0.0.1:${PORT} (DATABASE_URL in-memory)"
(cd "$ROOT/apps/api" && "$VENV_PY" -m uvicorn fourpro_api.main:app --host 127.0.0.1 --port "$PORT") &
UVICORN_PID=$!

echo -n "==> Aguardar /api/v1/health e /health/ready "
for _ in $(seq 1 50); do
  if curl -sf "http://127.0.0.1:${PORT}/api/v1/health" >/dev/null &&
    curl -sf "http://127.0.0.1:${PORT}/api/v1/health/ready" >/dev/null; then
    echo "OK"
    break
  fi
  echo -n "."
  sleep 0.25
done
if ! curl -sf "http://127.0.0.1:${PORT}/api/v1/health" >/dev/null ||
  ! curl -sf "http://127.0.0.1:${PORT}/api/v1/health/ready" >/dev/null; then
  echo ""
  echo "API não respondeu a tempo (health ou health/ready)." >&2
  exit 1
fi

export E2E_API_BASE_URL="http://127.0.0.1:${PORT}"
echo "==> Playwright smoke-api (E2E_API_BASE_URL=${E2E_API_BASE_URL})"
cd "$ROOT/e2e"
if [[ "${E2E_SKIP_NPM_CI:-}" != "1" ]]; then
  npm ci --silent
  npx playwright install chromium
fi
npx playwright test tests/smoke-api.spec.ts "$@"

echo "==> Smoke API local OK."
