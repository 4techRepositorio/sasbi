#!/usr/bin/env bash
# Para a stack definida em infra/portainer/stack-4pro-bi.yml (sem remover volumes por omissão).
# Limpar também dados: STACK_DOWN_VOLUMES=1 ./scripts/stack-down.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/infra/portainer"

ENV_FILE=".env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "==> Aviso: $ENV_FILE não encontrado — compose usa só defaults do YAML." >&2
  COMPOSE_ENV=()
else
  COMPOSE_ENV=(--env-file "$ENV_FILE")
fi

ARGS=(down)
if [[ "${STACK_DOWN_VOLUMES:-0}" == "1" ]]; then
  ARGS+=(-v)
  echo "==> Atenção: volumes Docker serão removidos (dados Postgres/Redis/MinIO/uploads)."
fi

echo "==> docker compose -f stack-4pro-bi.yml ${COMPOSE_ENV[*]} ${ARGS[*]}"
docker compose -f stack-4pro-bi.yml "${COMPOSE_ENV[@]}" "${ARGS[@]}"
