#!/usr/bin/env bash
# Sobe Postgres + Redis via infra/compose (portas por defeito 15432 / 16379 no host).
# Depois: exportar DATABASE_URL / REDIS_URL, alembic + dev_seed, uvicorn e ng serve (ver e2e/README.md).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMPOSE="infra/compose/docker-compose.yml"
export POSTGRES_PORT="${POSTGRES_PORT:-15432}"
export REDIS_PORT="${REDIS_PORT:-16379}"

echo "==> Docker Compose: postgres + redis ($COMPOSE)"
docker compose -f "$COMPOSE" up -d postgres redis

echo "==> Aguardar Postgres…"
for i in $(seq 1 40); do
  if docker compose -f "$COMPOSE" exec -T postgres pg_isready -U "${POSTGRES_USER:-fourpro}" -d "${POSTGRES_DB:-fourpro}" &>/dev/null; then
    break
  fi
  sleep 1
  if [[ "$i" -eq 40 ]]; then
    echo "Postgres não ficou pronto a tempo." >&2
    exit 1
  fi
done

PW="${POSTGRES_PASSWORD:-K8mpQ4wxN2vR7sFourProBIdev2026}"
echo ""
echo "==> Base e Redis no host:"
echo "    DATABASE_URL=postgresql+psycopg2://fourpro:${PW}@127.0.0.1:${POSTGRES_PORT}/fourpro"
echo "    REDIS_URL=redis://127.0.0.1:${REDIS_PORT}/0"
echo ""
echo "Próximos passos (exemplo):"
echo "  export DATABASE_URL=postgresql+psycopg2://fourpro:'$PW'@127.0.0.1:${POSTGRES_PORT}/fourpro"
echo "  export REDIS_URL=redis://127.0.0.1:${REDIS_PORT}/0"
echo "  export JWT_SECRET=local-dev-jwt-secret-at-least-32-characters___"
echo "  export UPLOAD_DIR=\"\$PWD/.local_uploads\" && mkdir -p \"\$UPLOAD_DIR\""
echo "  cd apps/api && alembic upgrade head && python -m fourpro_api.dev_seed"
echo "  # Terminal 1: cd apps/api && python -m uvicorn fourpro_api.main:app --host 127.0.0.1 --port 8000"
echo "  # Terminal 2: cd apps/web && npm run start -- --host 127.0.0.1 --port 4200 --proxy-config proxy.conf.ci.json"
echo "  ./scripts/run-e2e-local.sh"
