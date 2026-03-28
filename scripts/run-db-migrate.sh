#!/usr/bin/env bash
# Aplica migrações Alembic contra a base definida em DATABASE_URL.
# Uso típico: Postgres local (compose ou host) com .env na raiz do repositório.
# Em Docker/Portainer, a API já corre `alembic upgrade head` no entrypoint — ver infra/portainer/README.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  . "$ROOT/.env"
  set +a
fi

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "Erro: defina DATABASE_URL (ex.: ficheiro .env na raiz com postgresql+psycopg2://...)" >&2
  exit 1
fi

ALEMBIC=""
for cand in "$ROOT/apps/api/.venv/bin/alembic" "$ROOT/.venv/bin/alembic"; do
  if [[ -x "$cand" ]]; then
    ALEMBIC="$cand"
    break
  fi
done

if [[ -z "$ALEMBIC" ]]; then
  echo "Erro: não encontrei alembic em apps/api/.venv nem .venv." >&2
  echo "Crie a venv e instale deps: python3 -m venv apps/api/.venv && apps/api/.venv/bin/pip install -e packages/contracts -e packages/shared -e apps/api" >&2
  exit 1
fi

echo "==> Alembic upgrade head (DATABASE_URL definido, cwd apps/api)"
cd "$ROOT/apps/api"
exec "$ALEMBIC" upgrade head
