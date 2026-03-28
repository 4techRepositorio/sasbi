#!/usr/bin/env bash
# Paridade com o job CI `alembic-postgres`: Postgres 16 efémero em Docker + `alembic upgrade head`.
# Requisitos: Docker; venv com Alembic (apps/api/.venv ou .venv na raiz).
# Variáveis opcionais: ALEMBIC_PG_PORT (host fixo, ex. 55432); se omitido, Docker escolhe porta livre (-p 0:5432).
# SKIP_DOCKER_CLEANUP=1 — não remover o contentor ao sair.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="fourpro-alembic-pg-$(date +%s)-$$"
PUBLISH="${ALEMBIC_PG_PORT:+${ALEMBIC_PG_PORT}:5432}"
PUBLISH="${PUBLISH:-0:5432}"

cleanup() {
  if [[ "${SKIP_DOCKER_CLEANUP:-}" != "1" ]]; then
    docker rm -f "$NAME" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

if ! docker info >/dev/null 2>&1; then
  echo "Erro: Docker não disponível (necessário para Postgres efémero)." >&2
  exit 1
fi

echo "==> Postgres 16 efémero ($NAME) publish ${PUBLISH}"
if ! docker run -d --name "$NAME" \
  -e POSTGRES_USER=fourpro \
  -e POSTGRES_PASSWORD=fourpro_ci_local \
  -e POSTGRES_DB=fourpro \
  -p "${PUBLISH}" \
  postgres:16-alpine >/dev/null; then
  echo "Erro: docker run Postgres falhou." >&2
  exit 1
fi

# Arranque inicial em hosts lentos / I/O partilhado (initdb + CREATE DATABASE)
sleep 3

if [[ -n "${ALEMBIC_PG_PORT:-}" ]]; then
  PORT="${ALEMBIC_PG_PORT}"
else
  PORT=$(docker port "$NAME" 5432 | head -1 | awk -F: '{print $NF}')
fi

postgres_accepting() {
  docker exec "$NAME" psql -U fourpro -d fourpro -tAc "select 1" >/dev/null 2>&1
}

for _ in $(seq 1 120); do
  if postgres_accepting; then
    break
  fi
  sleep 0.5
done
if ! postgres_accepting; then
  echo "Erro: Postgres não aceitou ligações em fourpro a tempo (últimos logs):" >&2
  docker logs "$NAME" 2>&1 | tail -40 >&2 || true
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
  echo "Erro: alembic não encontrado em apps/api/.venv nem .venv." >&2
  exit 1
fi

export DATABASE_URL="postgresql+psycopg2://fourpro:fourpro_ci_local@127.0.0.1:${PORT}/fourpro"
export JWT_SECRET="${JWT_SECRET:-ci-jwt-secret-at-least-32-characters-long-for-alembic-only}"

cd "$ROOT/apps/api"
echo "==> Alembic heads (deve ser 1)"
LINES=$("$ALEMBIC" heads 2>/dev/null | sed '/^\s*$/d' | wc -l | tr -d ' ')
if [[ "$LINES" != "1" ]]; then
  echo "Erro: esperado exactamente 1 head Alembic, linhas não vazias: $LINES" >&2
  "$ALEMBIC" heads
  exit 1
fi

echo "==> Alembic upgrade head"
"$ALEMBIC" upgrade head
echo "==> OK (contentor Postgres removido ao sair; SKIP_DOCKER_CLEANUP=1 para manter)"
