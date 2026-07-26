#!/usr/bin/env bash
# Corre pytest API com cobertura (meta ≥90%) e opcionalmente gera relatório Markdown.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VENV_PY="$ROOT/.venv/bin/python"
VENV_PIP="$ROOT/.venv/bin/pip"
if [[ ! -x "$VENV_PY" ]]; then
  python3 -m venv "$ROOT/.venv"
fi
"$VENV_PIP" install -q --upgrade pip
"$VENV_PIP" install -q -r requirements-dev.txt

export DATABASE_URL="${DATABASE_URL:-sqlite:///:memory:}"
export JWT_SECRET="${JWT_SECRET:-ci-jwt-secret-at-least-32-characters-long}"
export ACCESS_TOKEN_EXPIRE_MINUTES="${ACCESS_TOKEN_EXPIRE_MINUTES:-15}"
export REFRESH_TOKEN_EXPIRE_DAYS="${REFRESH_TOKEN_EXPIRE_DAYS:-7}"

COV_DIR="${QA_COV_DIR:-$ROOT/.qa-coverage}"
mkdir -p "$COV_DIR"

echo "==> pytest + coverage (fail_under=90)"
"$VENV_PY" -m pytest apps/api/tests -q --tb=short \
  --cov=fourpro_api \
  --cov-config=.coveragerc \
  --cov-report=term-missing:skip-covered \
  --cov-report=json:"$COV_DIR/coverage.json" \
  --cov-report=html:"$COV_DIR/html" \
  --cov-fail-under=90

echo "==> Cobertura OK. HTML: $COV_DIR/html/index.html"
if [[ "${QA_GENERATE_REPORT:-1}" == "1" ]]; then
  bash "$ROOT/scripts/generate-qa-report.sh"
fi
