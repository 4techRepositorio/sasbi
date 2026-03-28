#!/bin/sh
set -e
cd /deps/apps/api
alembic upgrade head
if [ "${RUN_SEED:-false}" = "true" ]; then
  python -m fourpro_api.dev_seed || true
fi
exec "$@"
