#!/usr/bin/env bash
# Sobe Postgres + Redis + MinIO (Compose) e mostra comandos para API + Angular em modo dev.
# Portas: ver .env na raiz (host partilhado — não usa 5432/6379/6418 por defeito).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

set +u
set -a
[[ -f .env ]] && . ./.env
set +a
set -u

POSTGRES_PORT="${POSTGRES_PORT:-15432}"
REDIS_PORT="${REDIS_PORT:-16379}"
MINIO_PORT="${MINIO_PORT:-17291}"
MINIO_CONSOLE_PORT="${MINIO_CONSOLE_PORT:-17292}"
API_PUBLISH="${API_PUBLISH:-7418}"
UPLOAD_DIR="${UPLOAD_DIR:-$ROOT/.dev_uploads}"

echo "==> Docker Compose (postgres, redis, minio)"
docker compose -f infra/compose/docker-compose.yml up -d

echo "==> Aguardar Postgres (${POSTGRES_USER:-fourpro} / ${POSTGRES_DB:-fourpro})..."
for _ in $(seq 1 45); do
  if docker compose -f infra/compose/docker-compose.yml exec -T postgres \
    pg_isready -U "${POSTGRES_USER:-fourpro}" -d "${POSTGRES_DB:-fourpro}" &>/dev/null; then
    break
  fi
  sleep 1
done

mkdir -p "$UPLOAD_DIR"

echo ""
echo "--- Infra (host) ---"
echo "  Postgres : 127.0.0.1:${POSTGRES_PORT}"
echo "  Redis    : 127.0.0.1:${REDIS_PORT}"
echo "  MinIO    : 127.0.0.1:${MINIO_PORT}  (consola ${MINIO_CONSOLE_PORT})"
echo ""
echo "--- API + front (dois terminais) ---"
echo "  Terminal A — API (reload):"
echo "    cd $ROOT/apps/api && set -a && . ../../.env && set +a && \\"
echo "      export UPLOAD_DIR=$UPLOAD_DIR && \\"
echo "      $ROOT/.venv/bin/uvicorn fourpro_api.main:app --reload --host 0.0.0.0 --port ${API_PUBLISH}"
echo ""
echo "  Terminal B — Angular (proxy /api → API):"
echo "    cd $ROOT/apps/web && npm run start -- --host 0.0.0.0 --port 4200"
echo ""
echo "--- URLs ---"
echo "  App   http://127.0.0.1:4200"
echo "  API   http://127.0.0.1:${API_PUBLISH}  (health: /api/v1/health)"
echo ""
echo "Migrações (uma vez ou após pull):"
echo "  cd $ROOT/apps/api && set -a && . ../../.env && set +a && $ROOT/.venv/bin/alembic upgrade head"
echo ""
echo "QA (paridade CI):  $ROOT/scripts/run-qa-gates.sh"
