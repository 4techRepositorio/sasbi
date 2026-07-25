#!/usr/bin/env bash
# Exemplo: login, contexto e refresh.
set -euo pipefail

API_BASE="${API_BASE:-http://127.0.0.1:7418}"
EMAIL="${E2E_USER_EMAIL:-admin@local.dev}"
PASSWORD="${E2E_USER_PASSWORD:-changeme}"

echo "== Health =="
curl -sS "${API_BASE}/api/v1/health"
echo

echo "== Login =="
LOGIN_JSON="$(curl -sS -X POST "${API_BASE}/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}")"
echo "${LOGIN_JSON}"

if command -v jq >/dev/null 2>&1; then
  ACCESS="$(echo "${LOGIN_JSON}" | jq -r '.access_token // empty')"
  REFRESH="$(echo "${LOGIN_JSON}" | jq -r '.refresh_token // empty')"
  MFA="$(echo "${LOGIN_JSON}" | jq -r '.mfa_required // false')"
else
  echo "Instale jq para extrair tokens automaticamente." >&2
  exit 0
fi

if [[ "${MFA}" == "true" ]]; then
  echo "Conta com MFA: complete POST /api/v1/auth/mfa/verify com o código (email ou logs)." >&2
  exit 0
fi

echo "== Me / context =="
curl -sS "${API_BASE}/api/v1/me/context" \
  -H "Authorization: Bearer ${ACCESS}"
echo

echo "== Refresh =="
curl -sS -X POST "${API_BASE}/api/v1/auth/refresh" \
  -H 'Content-Type: application/json' \
  -d "{\"refresh_token\":\"${REFRESH}\"}"
echo
