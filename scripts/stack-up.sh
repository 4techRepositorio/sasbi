#!/usr/bin/env bash
# Sobe a stack Portainer local (build + detached). Ver regra em .cursor/rules/10-container-reset.mdc.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/infra/portainer"

ENV_FILE=".env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "==> Erro: crie infra/portainer/.env (pode copiar de .env.production.example + ajustar)." >&2
  exit 1
fi

exec docker compose -f stack-4pro-bi.yml --env-file "$ENV_FILE" up -d --build "$@"
