#!/usr/bin/env bash
# Remove linhas `e2e-seed-storage-warn.bin` da BD (par do seed de quotas E2E).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "Defina DATABASE_URL." >&2
  exit 1
fi
export JWT_SECRET="${JWT_SECRET:-e2e-cleanup-placeholder-jwt-secret-32chars!}"
PY="$ROOT/apps/api/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="python3"
fi
exec "$PY" "$ROOT/scripts/cleanup_e2e_storage_seed.py" "$@"
