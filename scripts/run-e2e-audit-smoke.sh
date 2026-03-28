#!/usr/bin/env bash
# Smoke UI: login → /app/tenant-audit (admin, sem MFA).
# O segundo cenário do ficheiro (consumer → redirect) fica em skip sem E2E_CONSUMER_*.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/e2e-env.sh
source "$ROOT/scripts/lib/e2e-env.sh"

e2e_load_dotenv "$ROOT"

if [[ -z "${E2E_USER_EMAIL:-}" || -z "${E2E_USER_PASSWORD:-}" ]]; then
  echo "Erro: defina E2E_USER_EMAIL e E2E_USER_PASSWORD (conta admin, sem MFA)." >&2
  exit 1
fi

export PLAYWRIGHT_BASE_URL="${PLAYWRIGHT_BASE_URL:-http://127.0.0.1:8081}"

echo "==> E2E — smoke auditoria (admin)"
echo "    PLAYWRIGHT_BASE_URL=$PLAYWRIGHT_BASE_URL"

cd "$ROOT/e2e"
npm ci
e2e_install_browsers_if_requested "$ROOT"
npx playwright test tests/tenant-audit.spec.ts "$@"
