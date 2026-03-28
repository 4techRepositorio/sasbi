#!/usr/bin/env bash
# Smoke HTTP: GET /api/v1/health e /api/v1/health/ready via Playwright (sem browser).
# Pré-requisito: API acessível. Defeito: porta em .env API_PUBLISH (7418 dev local) ou E2E_API_BASE_URL.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/e2e-env.sh
source "$ROOT/scripts/lib/e2e-env.sh"
e2e_load_dotenv "$ROOT"

cd "$ROOT/e2e"

_API_PORT="$(fourpro_e2e_api_publish_port "$ROOT")"
export E2E_API_BASE_URL="${E2E_API_BASE_URL:-http://127.0.0.1:${_API_PORT}}"

echo "==> E2E — smoke API (health)"
echo "    E2E_API_BASE_URL=$E2E_API_BASE_URL"
echo "    (sobrepor: export E2E_API_BASE_URL=http://127.0.0.1:6418 para stack Portainer)"

npm ci
npx playwright test tests/smoke-api.spec.ts "$@"
