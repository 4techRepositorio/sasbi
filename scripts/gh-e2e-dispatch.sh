#!/usr/bin/env bash
# Dispara o workflow "E2E (manual)" (e2e-dispatch.yml).
# Uso: gh-e2e-dispatch.sh [ref] [full|api_stack]
# Requer: gh auth login (https://cli.github.com)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v gh >/dev/null 2>&1; then
  echo "Instale a GitHub CLI: https://cli.github.com" >&2
  echo "Alternativa: no repositório → Actions → E2E (manual) → Run workflow." >&2
  exit 1
fi

REF="${1:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)}"
MODE="${2:-full}"
if [[ "$MODE" != "full" && "$MODE" != "api_stack" ]]; then
  echo "Modo inválido: $MODE (use full ou api_stack)" >&2
  exit 1
fi
echo "==> Disparar e2e-dispatch.yml ref=$REF mode=$MODE"
gh workflow run e2e-dispatch.yml --ref "$REF" -f "mode=$MODE"
echo "==> Últimos runs (aguarde alguns segundos e actualize):"
sleep 2
gh run list --workflow=e2e-dispatch.yml --limit 5
