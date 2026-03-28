#!/usr/bin/env bash
# Logs da stack (docker compose logs -f). Uso: ./scripts/stack-logs.sh [servico...]
# Ex.: ./scripts/stack-logs.sh api web
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/infra/portainer"
if [[ -f .env ]]; then
  exec docker compose -f stack-4pro-bi.yml --env-file .env logs -f "$@"
else
  exec docker compose -f stack-4pro-bi.yml logs -f "$@"
fi
