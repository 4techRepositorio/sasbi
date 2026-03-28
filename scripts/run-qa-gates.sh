#!/usr/bin/env bash
# Replica localmente os jobs `api-tests`, `web-build` e (opcional) e2e de .github/workflows/ci.yml (F5 / TICKET-014).
# O job `alembic-postgres` do CI: `RUN_ALEMBIC_PG_LOCAL=1`, `make qa-alembic` ou `./scripts/run-alembic-postgres-local.sh`.
# Usa .venv na raiz do repo (cria se não existir) para evitar PEP 668 em Python do sistema.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> QA gates (paridade com GitHub Actions CI)"

VENV_PY="$ROOT/.venv/bin/python"
VENV_PIP="$ROOT/.venv/bin/pip"
if [[ ! -x "$VENV_PY" ]]; then
  echo "==> Criar venv .venv (python3 -m venv)"
  python3 -m venv "$ROOT/.venv"
fi
echo "==> Python: pip install (requirements-dev.txt) em .venv"
"$VENV_PIP" install -q --upgrade pip
"$VENV_PIP" install -q -r requirements-dev.txt

export DATABASE_URL="${DATABASE_URL:-sqlite:///:memory:}"
export JWT_SECRET="${JWT_SECRET:-ci-jwt-secret-at-least-32-characters-long}"
export ACCESS_TOKEN_EXPIRE_MINUTES="${ACCESS_TOKEN_EXPIRE_MINUTES:-15}"
export REFRESH_TOKEN_EXPIRE_DAYS="${REFRESH_TOKEN_EXPIRE_DAYS:-7}"

echo "==> Ruff check + format (apps/api)"
"$VENV_PY" -m ruff check apps/api/fourpro_api apps/api/tests
"$VENV_PY" -m ruff format --check apps/api/fourpro_api apps/api/tests

echo "==> pytest apps/api/tests"
"$VENV_PY" -m pytest apps/api/tests -q --tb=short

echo "==> Angular (apps/web)"
cd apps/web
npm ci
npm run typecheck
npm run build

echo "==> Playwright smoke API (uvicorn SQLite efémero — paridade com job ci e2e-api-smoke-local)"
bash "$ROOT/scripts/run-e2e-api-smoke-local.sh"

if [[ "${RUN_ALEMBIC_PG_LOCAL:-}" == "1" ]]; then
  echo "==> Alembic + Postgres local (opcional, paridade job CI alembic-postgres)"
  if command -v docker >/dev/null 2>&1; then
    bash "$ROOT/scripts/run-alembic-postgres-local.sh"
  else
    echo "SKIP: Docker não encontrado (defina RUN_ALEMBIC_PG_LOCAL=0 ou instale Docker)."
  fi
fi

echo "==> QA gates OK."
echo "    (Suite browser completa: ./scripts/run-e2e-local.sh com e2e/.env.e2e ou Actions → E2E manual)"
