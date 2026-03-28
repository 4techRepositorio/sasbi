#!/usr/bin/env bash
# Estado dos contentores da stack Portainer (infra/portainer).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/infra/portainer"
if [[ -f .env ]]; then
  exec docker compose -f stack-4pro-bi.yml --env-file .env ps "$@"
else
  exec docker compose -f stack-4pro-bi.yml ps "$@"
fi
