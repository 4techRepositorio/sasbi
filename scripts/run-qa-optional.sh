#!/usr/bin/env bash
# Gates opcionais além de ./scripts/run-qa-gates.sh:
# 1) Alembic contra Postgres efémero (paridade job CI `alembic-postgres`)
# 2) Playwright browser completo (requer API + `ng serve`; e2e/.env.e2e)
#
# Uso:
#   ./scripts/run-qa-optional.sh
#   E2E_INSTALL_BROWSERS=1 ./scripts/run-qa-optional.sh   # primeira vez / CI self-hosted
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> [opcional] Alembic + Postgres efémero (Docker, paridade CI alembic-postgres)"
ALEMBIC_PG_PORT="${ALEMBIC_PG_PORT:-55432}" bash "$ROOT/scripts/run-alembic-postgres-local.sh"

if [[ ! -f "$ROOT/e2e/.env.e2e" ]]; then
  echo "==> [opcional] E2E browser — omitido (sem e2e/.env.e2e). Copie: cp e2e/.env.example e2e/.env.e2e"
  echo "==> QA opcional concluída (só Alembic)."
  exit 0
fi

echo "==> [opcional] E2E browser (API em \${API_PUBLISH:-7418} + front :4200)"
export E2E_INSTALL_BROWSERS="${E2E_INSTALL_BROWSERS:-0}"
bash "$ROOT/scripts/run-e2e-all-local.sh"

echo "==> QA opcional OK (Alembic Postgres + E2E browser)."
