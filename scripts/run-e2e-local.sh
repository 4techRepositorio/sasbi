#!/usr/bin/env bash
# Executa Playwright contra web+API já a correr.
# Terminal Angular (após npm ci em apps/web):
#   npm run start -- --host 127.0.0.1 --port 4200 --proxy-config proxy.conf.ci.json
# Terminal API: uvicorn em 8000 com DATABASE_URL, JWT_SECRET, REDIS_URL, UPLOAD_DIR.
# 1) Copie e2e/.env.example → e2e/.env.e2e e confirme URLs/credenciais (após dev_seed com consumer).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/e2e-env.sh
source "$ROOT/scripts/lib/e2e-env.sh"

ENV_FILE="$ROOT/e2e/.env.e2e"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "==> Crie $ENV_FILE (ex.: cp e2e/.env.example e2e/.env.e2e)."
  exit 1
fi

e2e_load_dotenv "$ROOT"

export E2E_RUN="${E2E_RUN:-1}"

missing=()
[[ -z "${PLAYWRIGHT_BASE_URL:-}" ]] && missing+=(PLAYWRIGHT_BASE_URL)
[[ -z "${E2E_USER_EMAIL:-}" ]] && missing+=(E2E_USER_EMAIL)
[[ -z "${E2E_USER_PASSWORD:-}" ]] && missing+=(E2E_USER_PASSWORD)
[[ -z "${E2E_CONSUMER_EMAIL:-}" ]] && missing+=(E2E_CONSUMER_EMAIL)
[[ -z "${E2E_CONSUMER_PASSWORD:-}" ]] && missing+=(E2E_CONSUMER_PASSWORD)
if ((${#missing[@]})); then
  echo "==> Faltam variáveis em e2e/.env.e2e: ${missing[*]}"
  echo "    (admin: login + auditoria; consumer: RBAC upload + auditoria)"
  exit 1
fi

echo "==> Playwright base: $PLAYWRIGHT_BASE_URL"
cd "$ROOT/e2e"
npm ci
if [[ "${E2E_SKIP_BROWSER_INSTALL:-0}" != "1" ]]; then
  npx playwright install --with-deps chromium
fi
exec npx playwright test "$@"
