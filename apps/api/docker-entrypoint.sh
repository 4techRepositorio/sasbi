#!/bin/sh
set -e
cd /deps/apps/api
alembic upgrade head
if [ "${RUN_SEED:-false}" = "true" ] && [ "${ENVIRONMENT:-}" = "production" ]; then
  echo "fourpro-api: AVISO — RUN_SEED=true com ENVIRONMENT=production. O seed é idempotente, mas após o primeiro bootstrap use RUN_SEED=false (ver infra/portainer/.env.production.example)." >&2
fi
if [ "${RUN_SEED:-false}" = "true" ]; then
  python -m fourpro_api.dev_seed || true
fi
exec "$@"
