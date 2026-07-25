#!/usr/bin/env bash
# Exporta o schema OpenAPI da API FastAPI para docs/openapi/openapi.json
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -x "${ROOT}/.venv/bin/python" ]]; then
  PY="${ROOT}/.venv/bin/python"
elif [[ -x "${ROOT}/apps/api/.venv/bin/python" ]]; then
  PY="${ROOT}/apps/api/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
else
  echo "Python não encontrado. Crie .venv e instale requirements-dev.txt." >&2
  exit 1
fi

export JWT_SECRET="${JWT_SECRET:-fourpro-bi-dev-jwt-hs256-2026-substituir-em-producao-64chars___}"
export DATABASE_URL="${DATABASE_URL:-sqlite+pysqlite:///:memory:}"
export ENVIRONMENT="${ENVIRONMENT:-development}"

mkdir -p "${ROOT}/docs/openapi"

"$PY" - <<'PY'
import json
from pathlib import Path

from fourpro_api.main import create_app

app = create_app()
schema = app.openapi()
out = Path("docs/openapi/openapi.json")
out.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Wrote {out} ({len(schema.get('paths', {}))} paths)")
PY
