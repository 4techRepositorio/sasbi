#!/usr/bin/env bash
# Executa seed_e2e_storage_warn.py com o venv da API (quando existir).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "Defina DATABASE_URL (mesmo valor que a API)." >&2
  exit 1
fi
export JWT_SECRET="${JWT_SECRET:-e2e-seed-placeholder-jwt-secret-32chars!!}"
PY="$ROOT/apps/api/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="python3"
fi
exec "$PY" "$ROOT/scripts/seed_e2e_storage_warn.py"
