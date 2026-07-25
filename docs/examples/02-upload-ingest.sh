#!/usr/bin/env bash
# Exemplo: upload → listar ingestões → catálogo (requer papel admin ou analyst).
set -euo pipefail

API_BASE="${API_BASE:-http://127.0.0.1:7418}"
EMAIL="${E2E_USER_EMAIL:-admin@local.dev}"
PASSWORD="${E2E_USER_PASSWORD:-changeme}"
SAMPLE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/sample-data.csv"

if ! command -v jq >/dev/null 2>&1; then
  echo "jq é obrigatório para este exemplo." >&2
  exit 1
fi

LOGIN_JSON="$(curl -sS -X POST "${API_BASE}/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}")"
ACCESS="$(echo "${LOGIN_JSON}" | jq -r '.access_token // empty')"
if [[ -z "${ACCESS}" ]]; then
  echo "Login falhou: ${LOGIN_JSON}" >&2
  exit 1
fi

echo "== Upload =="
UPLOAD_JSON="$(curl -sS -X POST "${API_BASE}/api/v1/uploads" \
  -H "Authorization: Bearer ${ACCESS}" \
  -F "file=@${SAMPLE};type=text/csv")"
echo "${UPLOAD_JSON}"
INGESTION_ID="$(echo "${UPLOAD_JSON}" | jq -r '.id // empty')"

echo "== Ingestões =="
curl -sS "${API_BASE}/api/v1/ingestions" \
  -H "Authorization: Bearer ${ACCESS}"
echo

if [[ -n "${INGESTION_ID}" ]]; then
  echo "== Detalhe ${INGESTION_ID} =="
  curl -sS "${API_BASE}/api/v1/ingestions/${INGESTION_ID}" \
    -H "Authorization: Bearer ${ACCESS}"
  echo
fi

echo "== Datasets (só processed) =="
curl -sS "${API_BASE}/api/v1/datasets" \
  -H "Authorization: Bearer ${ACCESS}"
echo

echo "Nota: sem worker Celery activo o estado pode ficar em 'uploaded'."
