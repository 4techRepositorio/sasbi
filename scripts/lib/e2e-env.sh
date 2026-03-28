# shellcheck shell=bash
# Lê uma linha KEY=valor do ficheiro (primeira ocorrência de KEY); stdout = valor ou vazio.
fourpro_read_env_key() {
  local file="${1:?}" key="${2:?}"
  [[ -f "$file" ]] || return 0
  grep -E "^${key}=" "$file" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '\r' | sed 's/^"\(.*\)"$/\1/'
}

# Porta da API no host para smokes (alinha a API_PUBLISH no .env da raiz; defeito 7418 — evita Portainer em 6418).
fourpro_e2e_api_publish_port() {
  local root="${1:?}"
  local f="$root/.env"
  local val
  val="$(fourpro_read_env_key "$f" API_PUBLISH)"
  echo "${val:-7418}"
}

# Carrega e2e/.env.e2e se existir (KEY=valor, sem export na linha — set -a exporta tudo).
e2e_load_dotenv() {
  local root="${1:?}"
  local f="$root/e2e/.env.e2e"
  if [[ -f "$f" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$f"
    set +a
    echo "==> Carregado $f"
  else
    echo "==> (info) $f não existe — exporte variáveis ou: cp e2e/.env.e2e.example e2e/.env.e2e"
  fi
}

e2e_install_browsers_if_requested() {
  if [[ "${E2E_INSTALL_BROWSERS:-0}" == "1" ]]; then
    echo "==> Playwright: install chromium (--with-deps)"
    (cd "$1/e2e" && npx playwright install --with-deps chromium)
  fi
}
