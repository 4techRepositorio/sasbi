#!/usr/bin/env bash
# Espera pela stack (web + API) e corre Playwright com e2e/.env.e2e.
# Uso típico após: cd infra/portainer && docker compose -f stack-4pro-bi.yml --env-file .env up -d
#
# URLs por omissão alinhadas a infra/portainer/.env (WEB_PUBLISH=8081, API_PUBLISH=6418).
# Sobrescrever: E2E_STACK_WEB_URL, E2E_STACK_API_URL
#
# Variáveis de teste: copiar e2e/.env.example → e2e/.env.e2e (admin + consumer + E2E_RUN=1).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/e2e-env.sh
source "$ROOT/scripts/lib/e2e-env.sh"

API_BASE="${E2E_STACK_API_URL:-http://127.0.0.1:6418}"
WEB_URL="${E2E_STACK_WEB_URL:-http://127.0.0.1:8081}"

wait_http_ok() {
  local url="$1"
  local label="$2"
  local max="${3:-90}"
  local i=0
  while (( i < max )); do
    if curl -sf "$url" >/dev/null 2>&1; then
      echo "==> $label disponível: $url"
      return 0
    fi
    sleep 1
    ((++i)) || true
  done
  echo "==> Timeout à espera de $label ($url)" >&2
  return 1
}

echo "==> À espera da API ($API_BASE) e do web ($WEB_URL)…"
wait_http_ok "$API_BASE/api/v1/health" "API" 120
wait_http_ok "$WEB_URL/" "Web" 120

e2e_load_dotenv "$ROOT"

export PLAYWRIGHT_BASE_URL="${PLAYWRIGHT_BASE_URL:-$WEB_URL}"
export E2E_API_BASE_URL="${E2E_API_BASE_URL:-$API_BASE}"
export E2E_RUN="${E2E_RUN:-1}"

echo "==> Playwright: PLAYWRIGHT_BASE_URL=$PLAYWRIGHT_BASE_URL E2E_API_BASE_URL=$E2E_API_BASE_URL E2E_RUN=$E2E_RUN"

cd "$ROOT/e2e"
npm ci
if [[ "${E2E_SKIP_BROWSER_INSTALL:-0}" != "1" ]]; then
  npx playwright install --with-deps chromium
fi
exec npx playwright test "$@"
