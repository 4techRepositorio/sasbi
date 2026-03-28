#!/usr/bin/env bash
# Sobe Postgres (Docker efémero), migra + dev_seed, API e Angular em portas dedicadas (omissão = portas livres).
#
# Portas por omissão: portas TCP livres (evita colisão com 18080/14200/55433 já em uso).
# Sobrescrever: E2E_ONE_SHOT_API_PORT, E2E_ONE_SHOT_WEB_PORT, E2E_ONE_SHOT_PG_PORT
#
# Outras variáveis:
#   E2E_ONE_SHOT_PG_PORT — Postgres no host (omissão = porta livre)
#   E2E_ONE_SHOT_SKIP_ANGULAR=1 — não arranca ng serve
#   E2E_SKIP_WEB_NPM_CI=1 — não corre npm ci em apps/web
#   E2E_INSTALL_BROWSERS=1 — playwright install --with-deps
#   E2E_SKIP_E2E_NPM_CI=1 — não corre npm ci em e2e/ (CI já instalou)
#   E2E_SKIP_PLAYWRIGHT_BROWSER_INSTALL=1 — não corre playwright install (CI já instalou browsers)
#   E2E_WIREFRAME_CAPTURES=1 — grava PNG em docs/assets/wireframes/exports/ (testes wireframe-validation-captures)
#   E2E_EXPECT_STORAGE_WARN=1 — após dev_seed corre scripts/seed_e2e_storage_warn.py (teste opcional data-storage-warn)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VENV_PY="${VENV_PY:-$ROOT/.venv/bin/python}"
if [[ ! -x "$VENV_PY" ]]; then
  echo "Crie .venv: python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt" >&2
  exit 1
fi

if ! docker info &>/dev/null; then
  echo "Docker não disponível — não é possível subir Postgres efémero." >&2
  exit 1
fi

fourpro_free_tcp_port() {
  python3 -c 'import socket; s=socket.socket(); s.bind(("", 0)); p=s.getsockname()[1]; s.close(); print(p)'
}

API_PORT="${E2E_ONE_SHOT_API_PORT:-$(fourpro_free_tcp_port)}"
WEB_PORT="${E2E_ONE_SHOT_WEB_PORT:-$(fourpro_free_tcp_port)}"
PG_NAME="fourpro-e2e-oneshot-$$"
PG_PORT="${E2E_ONE_SHOT_PG_PORT:-$(fourpro_free_tcp_port)}"
PG_PASS="${E2E_ONE_SHOT_PG_PASSWORD:-fourpro_e2e_oneshot_test}"
UPLOAD_BASE="${TMPDIR:-/tmp}/fourpro_e2e_oneshot_$$"
mkdir -p "$UPLOAD_BASE"
PROXY_JSON="$UPLOAD_BASE/proxy-e2e-oneshot.json"

cleanup() {
  [[ -n "${NG_PID:-}" ]] && kill "$NG_PID" 2>/dev/null || true
  [[ -n "${UVICORN_PID:-}" ]] && kill "$UVICORN_PID" 2>/dev/null || true
  [[ -n "${NG_PID:-}" ]] && wait "$NG_PID" 2>/dev/null || true
  [[ -n "${UVICORN_PID:-}" ]] && wait "$UVICORN_PID" 2>/dev/null || true
  docker rm -f "$PG_NAME" &>/dev/null || true
  rm -rf "$UPLOAD_BASE"
}
trap cleanup EXIT

cat > "$PROXY_JSON" <<EOF
{
  "/api": {
    "target": "http://127.0.0.1:${API_PORT}",
    "secure": false,
    "changeOrigin": true,
    "logLevel": "silent"
  }
}
EOF

echo "==> Postgres efémero $PG_NAME (127.0.0.1:${PG_PORT})"
docker run -d --name "$PG_NAME" \
  -e POSTGRES_USER=fourpro \
  -e POSTGRES_PASSWORD="$PG_PASS" \
  -e POSTGRES_DB=fourpro \
  -p "${PG_PORT}:5432" \
  postgres:16-alpine >/dev/null

echo -n "==> Aguardar Postgres "
for _ in $(seq 1 50); do
  if docker exec "$PG_NAME" pg_isready -U fourpro -d fourpro &>/dev/null; then
    echo "OK"
    break
  fi
  echo -n "."
  sleep 0.4
done
if ! docker exec "$PG_NAME" pg_isready -U fourpro -d fourpro &>/dev/null; then
  echo ""
  echo "Postgres não ficou pronto." >&2
  exit 1
fi

export DATABASE_URL="postgresql+psycopg2://fourpro:${PG_PASS}@127.0.0.1:${PG_PORT}/fourpro"
export JWT_SECRET="${JWT_SECRET:-e2e-one-shot-jwt-secret-min-32-chars________}"
export UPLOAD_DIR="$UPLOAD_BASE/uploads"
mkdir -p "$UPLOAD_DIR"
export REDIS_URL="${REDIS_URL:-}"

echo "==> Alembic + dev_seed"
(cd "$ROOT/apps/api" && "$VENV_PY" -m alembic upgrade head && "$VENV_PY" -m fourpro_api.dev_seed)

if [[ "${E2E_EXPECT_STORAGE_WARN:-}" == "1" ]]; then
  echo "==> Seed E2E storage warn (uso ~91% do plano — context-storage-ui opcional)"
  "$VENV_PY" "$ROOT/scripts/seed_e2e_storage_warn.py"
fi

echo "==> Uvicorn 127.0.0.1:${API_PORT}"
(cd "$ROOT/apps/api" && "$VENV_PY" -m uvicorn fourpro_api.main:app --host 127.0.0.1 --port "$API_PORT") &
UVICORN_PID=$!

echo -n "==> Aguardar API /health "
for _ in $(seq 1 50); do
  if curl -sf "http://127.0.0.1:${API_PORT}/api/v1/health" &>/dev/null; then
    echo "OK"
    break
  fi
  echo -n "."
  sleep 0.3
done
if ! curl -sf "http://127.0.0.1:${API_PORT}/api/v1/health" &>/dev/null; then
  echo ""
  echo "API não respondeu." >&2
  exit 1
fi

NG_PID=""
if [[ "${E2E_ONE_SHOT_SKIP_ANGULAR:-0}" != "1" ]]; then
  echo "==> Angular 127.0.0.1:${WEB_PORT} (proxy → :${API_PORT})"
  if [[ "${E2E_SKIP_WEB_NPM_CI:-0}" != "1" ]]; then
    (cd "$ROOT/apps/web" && npm ci)
  fi
  (cd "$ROOT/apps/web" && node node_modules/@angular/cli/bin/ng.js serve --host 127.0.0.1 --port "$WEB_PORT" --proxy-config "$PROXY_JSON") &
  NG_PID=$!

  sleep 2
  if ! kill -0 "$NG_PID" 2>/dev/null; then
    echo "" >&2
    echo "ng serve terminou ao arrancar (ver erros acima ou porta em uso)." >&2
    exit 1
  fi

  echo -n "==> Aguardar front :${WEB_PORT} "
  for _ in $(seq 1 120); do
    if curl -sf "http://127.0.0.1:${WEB_PORT}/" &>/dev/null; then
      echo "OK"
      break
    fi
    echo -n "."
    sleep 2
  done
  if ! curl -sf "http://127.0.0.1:${WEB_PORT}/" &>/dev/null; then
    echo ""
    echo "Angular não respondeu a tempo (primeira build pode demorar)." >&2
    exit 1
  fi
else
  echo "==> E2E_ONE_SHOT_SKIP_ANGULAR=1 — usa PLAYWRIGHT_BASE_URL já definido"
fi

export PLAYWRIGHT_BASE_URL="${PLAYWRIGHT_BASE_URL:-http://127.0.0.1:${WEB_PORT}}"
export E2E_API_BASE_URL="${E2E_API_BASE_URL:-http://127.0.0.1:${API_PORT}}"
export E2E_RUN=1
export E2E_USER_EMAIL="${E2E_USER_EMAIL:-admin@local.dev}"
export E2E_USER_PASSWORD="${E2E_USER_PASSWORD:-changeme}"
export E2E_CONSUMER_EMAIL="${E2E_CONSUMER_EMAIL:-consumer@local.dev}"
export E2E_CONSUMER_PASSWORD="${E2E_CONSUMER_PASSWORD:-changeme}"

if [[ "${E2E_WIREFRAME_CAPTURES:-}" == "1" ]]; then
  mkdir -p "$ROOT/docs/assets/wireframes/exports"
fi

echo "==> Playwright (PLAYWRIGHT_BASE_URL=$PLAYWRIGHT_BASE_URL)"
cd "$ROOT/e2e"
if [[ "${E2E_SKIP_E2E_NPM_CI:-0}" != "1" ]]; then
  npm ci --silent
fi
if [[ "${E2E_SKIP_PLAYWRIGHT_BROWSER_INSTALL:-0}" != "1" ]]; then
  if [[ "${E2E_INSTALL_BROWSERS:-0}" == "1" ]]; then
    npx playwright install --with-deps chromium
  else
    npx playwright install chromium
  fi
fi
npx playwright test "$@"

echo "==> E2E one-shot OK."
