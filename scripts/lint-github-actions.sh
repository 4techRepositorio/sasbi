#!/usr/bin/env bash
# Valida sintaxe dos workflows com actionlint (opcional).
# 1) binário `actionlint` no PATH, ou
# 2) Docker: imagem rhysd/actionlint (fallback automático se Docker disponível).
# Instalação nativa: https://github.com/rhysd/actionlint
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

run_native() {
  exec actionlint "$ROOT/.github/workflows"/*.yml
}

run_docker() {
  echo "==> actionlint via Docker (rhysd/actionlint)"
  exec docker run --rm \
    -v "$ROOT:/repo" \
    -w /repo \
    rhysd/actionlint:latest \
    -color \
    .github/workflows/*.yml
}

if command -v actionlint >/dev/null 2>&1; then
  run_native
fi

if [[ "${ACTIONLINT_NO_DOCKER:-0}" != "1" ]] && docker info &>/dev/null; then
  run_docker
fi

echo "actionlint não disponível." >&2
echo "  Opção A: instalar https://github.com/rhysd/actionlint#install" >&2
echo "  Opção B: Docker no PATH e ACTIONLINT_NO_DOCKER=0 (omissão)" >&2
echo "  Opção C: ACTIONLINT_NO_DOCKER=1 para forçar falha sem Docker" >&2
exit 1
