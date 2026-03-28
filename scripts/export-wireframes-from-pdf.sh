#!/usr/bin/env bash
# Gera PNGs a partir de «Data Analytics Solution.pdf» (raiz do repo) para docs/assets/wireframes/exports/.
# Requisito: poppler-utils (pdftoppm).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PDF="${ROOT}/Data Analytics Solution.pdf"
OUT="${ROOT}/docs/assets/wireframes/exports"
PREFIX="${OUT}/data-analytics-solution-p"

if ! command -v pdftoppm >/dev/null 2>&1; then
  echo "Erro: precisa de pdftoppm (ex.: apt install poppler-utils)." >&2
  exit 1
fi

if [[ ! -f "${PDF}" ]]; then
  echo "Erro: PDF em falta: ${PDF}" >&2
  exit 1
fi

mkdir -p "${OUT}"
rm -f "${PREFIX}"-*.png
pdftoppm -png "${PDF}" "${PREFIX}"
count="$(find "${OUT}" -maxdepth 1 -name 'data-analytics-solution-p-*.png' | wc -l)"
echo "OK: ${count} página(s) em ${OUT}/ (prefixo data-analytics-solution-p-)"
