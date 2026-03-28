#!/usr/bin/env bash
# Corre todos os testes Playwright com variáveis de e2e/.env.e2e (se existir).
# - API smoke: E2E_API_BASE_URL (default: API_PUBLISH no .env da raiz, senão 7418)
# - Login / RBAC / auditoria: só correm se credenciais e E2E_RUN estiverem definidos (ver e2e/.env.example)
# Instalar browsers: E2E_INSTALL_BROWSERS=1 ./scripts/run-e2e-all-local.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/e2e-env.sh
source "$ROOT/scripts/lib/e2e-env.sh"

e2e_load_dotenv "$ROOT"

_API_PORT="$(fourpro_e2e_api_publish_port "$ROOT")"
export E2E_API_BASE_URL="${E2E_API_BASE_URL:-http://127.0.0.1:${_API_PORT}}"
export PLAYWRIGHT_BASE_URL="${PLAYWRIGHT_BASE_URL:-http://127.0.0.1:4200}"

echo "==> E2E — suite completa (skips automáticos onde faltam credenciais)"
echo "    E2E_API_BASE_URL=$E2E_API_BASE_URL"
echo "    PLAYWRIGHT_BASE_URL=$PLAYWRIGHT_BASE_URL"

cd "$ROOT/e2e"
npm ci
e2e_install_browsers_if_requested "$ROOT"
npx playwright test "$@"
