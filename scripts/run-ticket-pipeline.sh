#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

set +u
set -a
[ -f .env ] && . ./.env
set +a
set -u

echo "==> Instalação Python (venv .venv)"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements-dev.txt

echo "==> Subir Postgres + Redis (Compose fundação)"
docker compose -f infra/compose/docker-compose.yml up -d postgres redis

echo "==> Aguardar Postgres..."
for i in $(seq 1 30); do
  if docker compose -f infra/compose/docker-compose.yml exec -T postgres pg_isready -U fourpro -d fourpro &>/dev/null; then
    break
  fi
  sleep 1
done

export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg2://fourpro:K8mpQ4wxN2vR7sFourProBIdev2026@127.0.0.1:5432/fourpro}"
export JWT_SECRET="${JWT_SECRET:-fourpro-bi-dev-jwt-hs256-2026-substituir-em-producao-64chars___}"
export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:6379/0}"
export UPLOAD_DIR="${UPLOAD_DIR:-$ROOT/.pipeline_uploads}"
mkdir -p "$UPLOAD_DIR"

echo "==> Migrações Alembic"
cd apps/api
alembic upgrade head

echo "==> Seed dev"
python -m fourpro_api.dev_seed || true

echo "==> Pytest"
pytest -q

echo "==> Smoke HTTP"
API_PORT="${API_PUBLISH:-6418}"
set +e
H="$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:${API_PORT}/api/v1/health" 2>/dev/null)"
set -e
if [[ "$H" != "200" ]]; then
  echo "(info) API não está em :${API_PORT} — inicie: uvicorn fourpro_api.main:app --port ${API_PORT}"
else
  echo "Health: $H"
fi

echo "==> Pipeline local concluída."
