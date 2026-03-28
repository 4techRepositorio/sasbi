#!/usr/bin/env bash
# Smoke RBAC: consumer acede a /app/upload → redirect + banner.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/e2e-env.sh
source "$ROOT/scripts/lib/e2e-env.sh"

e2e_load_dotenv "$ROOT"

export E2E_RUN="${E2E_RUN:-1}"
if [[ "$E2E_RUN" != "1" ]]; then
  echo "Erro: E2E_RUN deve ser 1 para este teste." >&2
  exit 1
fi

if [[ -z "${E2E_CONSUMER_EMAIL:-}" || -z "${E2E_CONSUMER_PASSWORD:-}" ]]; then
  echo "Erro: defina E2E_CONSUMER_EMAIL e E2E_CONSUMER_PASSWORD (e2e/.env.e2e ou export)." >&2
  exit 1
fi

export PLAYWRIGHT_BASE_URL="${PLAYWRIGHT_BASE_URL:-http://127.0.0.1:4200}"

echo "==> E2E — RBAC upload (consumer)"
echo "    PLAYWRIGHT_BASE_URL=$PLAYWRIGHT_BASE_URL"

cd "$ROOT/e2e"
npm ci
e2e_install_browsers_if_requested "$ROOT"
npx playwright test tests/rbac-upload-banner.spec.ts "$@"
