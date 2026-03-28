# E2E (Frente QA)

Testes **Playwright** contra stack **web + API** (Portainer, ou `uvicorn` + `ng serve` com proxy).

- Não duplicar contratos já cobertos em `apps/api/tests/`.
- Fluxos: health da API, login, RBAC (consumer → `/app/upload` → banner), auditoria admin (`/app/tenant-audit`), quotas na shell (`context-storage-ui`).

## Notas de robustez (dev)

- Botão de login: usar **«Entrar»** exacto nos testes — «Entrar com SSO» também casa com `/entrar/i`.
- Título da página de login: **«Bem-vindo de volta»**.
- `ng serve`: o overlay `vite-error-overlay` pode bloquear cliques; os testes usam `dismissViteOverlayIfAny` (`e2e/helpers/vite-overlay.ts`).

## Configuração

```bash
cp e2e/.env.e2e.example e2e/.env.e2e
# editar URLs e credenciais (alinhadas a `fourpro_api.dev_seed` em dev)
```

Ficheiros: `e2e/.env.e2e.example` (modelo), `e2e/.env.e2e` (local, **ignorado pelo Git**).

## Scripts na raiz do repo (`scripts/`)

| Script | O que faz |
|--------|-----------|
| `run-e2e-api-smoke-local.sh` | Sobe **uvicorn** com SQLite em memória, corre smoke API, encerra. Sem Docker nem Alembic; exporta `E2E_API_BASE_URL`. Porta: `E2E_LOCAL_API_PORT` (default `18765`). |
| `run-e2e-api-smoke.sh` | Só HTTP: `/api/v1/health` e `/api/v1/health/ready`. Lê `e2e/.env.e2e` se existir. Default API = `API_PUBLISH` no `.env` raiz (**7418** dev local); Portainer: `E2E_API_BASE_URL=http://127.0.0.1:6418`. |
| `run-e2e-ui-login-smoke.sh` | Login até `/app`. Exige `E2E_USER_*` + front em `PLAYWRIGHT_BASE_URL`. `E2E_INSTALL_BROWSERS=1` instala Chromium. |
| `run-e2e-audit-smoke.sh` | Login → `/app/tenant-audit` (admin). Mesmas variáveis que login; corre `tenant-audit.spec.ts`. |
| `run-e2e-rbac-smoke.sh` | RBAC upload (consumer). Exige `E2E_CONSUMER_*`, define `E2E_RUN=1`. |
| `run-e2e-all-local.sh` | Suite completa: carrega `.env.e2e`, defaults API = `API_PUBLISH` (`.env` raiz), front **4200** (`ng serve`); skips onde faltam credenciais. |
| `run-e2e-stack-browser.sh` | Espera `GET /api/v1/health` (default API `6418`) e o front (`8081`), depois Playwright; `E2E_RUN=1` por omissão. Use após `docker compose up` em `infra/portainer`. |
| `run-e2e-local.sh` | **Obriga** `.env.e2e` com admin (`E2E_USER_*`), consumer (`E2E_CONSUMER_*`) e `PLAYWRIGHT_BASE_URL`; instala browsers (`E2E_SKIP_BROWSER_INSTALL=1` para desligar). |
| `run-e2e-docker-foundation.sh` | Sobe **Postgres + Redis** (`infra/compose/docker-compose.yml`, portas host 15432/16379). Imprime `DATABASE_URL` / `REDIS_URL` e próximos passos (alembic, uvicorn, `run-e2e-local.sh`). |
| `gh-e2e-dispatch.sh` | Dispara **E2E (manual)** via `gh` (2.º arg: `full` ou `api_stack`). |
| `run-e2e-one-shot-stack.sh` | **Um comando:** Postgres efémero (Docker), Alembic, `dev_seed`, API e `ng serve` em portas TCP livres (ou fixas via `E2E_ONE_SHOT_*_PORT`), proxy gerado, Playwright (~10 testes com env opcionais). Opcional: `E2E_EXPECT_STORAGE_WARN=1` corre `scripts/seed_e2e_storage_warn.py` após o seed; `E2E_WIREFRAME_CAPTURES=1` cria `docs/assets/wireframes/exports/` e grava PNG. Atalho: `make e2e-one-shot`. |
| `run-e2e-storage-warn-browser-local.sh` | Réplica do workflow **E2E storage warn browser**: SQLite em `/tmp` (ou `DATABASE_URL`), `alembic` + `dev_seed` + seed quota, API `:8765`, `ng serve` `:4200` com `proxy.conf.e2e-storage-warn.json`, Playwright só `context-storage-ui.spec.ts` (`E2E_EXPECT_STORAGE_WARN=1` por omissão; cleanup no `EXIT`). |
| `run-qa-optional.sh` | Alembic+Postgres local e, com `e2e/.env.e2e`, suite browser. `QA_OPTIONAL_E2E_ONE_SHOT=1` ou **`make qa-optional-full`** acrescenta o one-shot. |

```bash
chmod +x scripts/run-e2e-*.sh   # uma vez
./scripts/run-e2e-api-smoke-local.sh
./scripts/run-e2e-api-smoke.sh
E2E_INSTALL_BROWSERS=1 ./scripts/run-e2e-ui-login-smoke.sh
```

## npm (`cd e2e`)

```bash
npm ci
npm run test:api      # só smoke-api
npm run test:login
npm run test:rbac
npm run test:audit
npm run test:wireframe-captures  # só com E2E_WIREFRAME_CAPTURES=1 (grava PNG em docs/assets/…/exports/)
npm run test:html     # relatório em playwright-report/ (PLAYWRIGHT_HTML_REPORT=1)
npm run install:browsers
npm test              # tudo (respeita skips sem env)
```

## Variáveis

| Variável | Uso |
|----------|-----|
| `PLAYWRIGHT_BASE_URL` | URL do front (default em config: `http://127.0.0.1:8081`; `.env.example` usa `4200` com proxy). |
| `E2E_API_BASE_URL` | Origem da API (sem path) — smoke API. |
| `E2E_SKIP_NPM_CI` | `1` — `run-e2e-api-smoke-local.sh` não corre `npm ci` (CI já instalou deps). |
| `E2E_LOCAL_API_PORT` | Porta do uvicorn efémero no script local (default `18765`). |
| `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` | Admin: login, `tenant-audit` (sem MFA), `context-storage-ui` (bloco de armazenamento na sidebar). |
| `E2E_EXPECT_STORAGE_WARN` | `1` — segundo teste em `context-storage-ui.spec.ts` (`data-storage-warn="true"`); exige tenant com uso ≥90 % do plano. |
| `E2E_RUN=1` + `E2E_CONSUMER_*` | RBAC upload + parte consumer de `tenant-audit.spec.ts`. |
| `E2E_STACK_API_URL` / `E2E_STACK_WEB_URL` | Sobrescreve URLs esperadas por `run-e2e-stack-browser.sh` (default `6418` / `8081`). |
| `E2E_WIREFRAME_CAPTURES=1` | Activa `tests/wireframe-validation-captures.spec.ts`: grava PNG em `docs/assets/wireframes/exports/` — `identity-*`, `workspace-shell-v1-*` (sidebar), `workspace-dashboard-v1-*`, `pipeline-*`, `identity-admin-users-v1-*`, `tenant-audit-v1-*`, `billing-overview-v1-*`, `settings-placeholder-v1-*` (revisar antes de commit; convive com `data-analytics-solution-p-*.png`). Requer front no ar; rotas `/app/*` precisam `E2E_USER_*` **admin** sem MFA. |

### Capturas para `docs/wireframes/validation-*.md` (opcional)

```bash
cd e2e
set -a && [ -f .env.e2e ] && . ./.env.e2e && set +a
E2E_WIREFRAME_CAPTURES=1 npm run test:wireframe-captures
```

### Alerta `data-storage-warn` (teste opcional)

1. **One-shot:** `E2E_EXPECT_STORAGE_WARN=1 ./scripts/run-e2e-one-shot-stack.sh` — o script corre o seed de quota após `dev_seed` (BD efémera; sem cleanup manual).
2. **BD persistente (dev):** com a mesma `DATABASE_URL` que a API: `./scripts/run-seed-e2e-storage-warn.sh` (insere uma linha em `file_ingestions` até ~91,5 % do `max_storage_mb` do tenant `demo`).
3. Exportar `E2E_EXPECT_STORAGE_WARN=1` e correr `context-storage-ui.spec.ts` (ou a suite Playwright completa).
4. **Reverter** a BD de desenvolvimento: `./scripts/run-cleanup-e2e-storage-warn.sh` (ou `python scripts/cleanup_e2e_storage_seed.py`; `--dry-run` para pré-visualizar).

**CI manual:**

- *E2E seed storage scripts* (`e2e-seed-storage-dispatch.yml`) — só scripts seed/cleanup em SQLite.
- *E2E storage warn browser* (`e2e-storage-warn-browser-dispatch.yml`) — API `:8765` + `ng serve` com `apps/web/proxy.conf.e2e-storage-warn.json` + Playwright `context-storage-ui.spec.ts` (ambos os testes, com `E2E_EXPECT_STORAGE_WARN=1`).

**Réplica local:** `./scripts/run-e2e-storage-warn-browser-local.sh` (SQLite em `/tmp` por omissão; requer `npm ci` em `apps/web` e `e2e` e Chromium do Playwright). Alternativa manual (3 terminais): `alembic` + `dev_seed` + `scripts/seed_e2e_storage_warn.py`; `uvicorn` em `8765`; `ng serve --proxy-config apps/web/proxy.conf.e2e-storage-warn.json`; na pasta `e2e` com `E2E_USER_*` e `E2E_EXPECT_STORAGE_WARN=1`, `npx playwright test tests/context-storage-ui.spec.ts`; depois `run-cleanup-e2e-storage-warn.sh`.

## Stack local (resumo)

```bash
cd apps/api && alembic upgrade head && python -m fourpro_api.dev_seed
# API: uvicorn (DATABASE_URL, JWT_SECRET, REDIS_URL, UPLOAD_DIR)
# Web: cd apps/web && npm run start -- --host 127.0.0.1 --port 4200 --proxy-config proxy.conf.ci.json
./scripts/run-e2e-local.sh
```

**Stack Docker (Portainer):** após `docker compose -f infra/portainer/stack-4pro-bi.yml --env-file infra/portainer/.env up -d`, `./scripts/run-e2e-stack-browser.sh` (ajuste `e2e/.env.e2e` às credenciais do seed).

Linux: se faltar `.so` no Chromium, na pasta `e2e/`: `sudo npx playwright install-deps chromium`.

## CI

Índice: [`.github/workflows/README.md`](../.github/workflows/README.md).

- **PR/push:** `.github/workflows/ci.yml` — job `e2e-api-smoke-local` chama **`reusable-e2e-api-smoke.yml`** (Playwright `smoke-api` + uvicorn SQLite).
- **Manual completo (browser):** *Actions* → **E2E (manual)** → *Run workflow* (`.github/workflows/e2e-dispatch.yml`; credenciais `admin@local.dev` / `consumer@local.dev` no YAML).

### Artefactos (após E2E manual)

O workflow faz upload de **`e2e-artifacts-full`** ou **`e2e-artifacts-api_stack`** (segundo o modo): relatório HTML Playwright, `test-results/`, cópias de `/tmp/fourpro-api.log` e `/tmp/fourpro-ng.log` (este último só em `full`). Retenção: 7 dias.

### Modos do workflow **E2E (manual)**

| Modo | Conteúdo |
|------|----------|
| `full` (omissão) | Postgres + Redis + API + `ng serve` + suite Playwright browser. |
| `api_stack` | Sem Angular — API real + `tests/smoke-api.spec.ts` apenas (mais rápido). |

Na UI: *Run workflow* → escolher **mode**. Na CLI: `./scripts/gh-e2e-dispatch.sh main api_stack`.

### Disparo via GitHub CLI (opcional)

```bash
chmod +x scripts/gh-e2e-dispatch.sh
./scripts/gh-e2e-dispatch.sh                    # ref = branch actual, mode=full
./scripts/gh-e2e-dispatch.sh main               # main, full
./scripts/gh-e2e-dispatch.sh main api_stack     # só smoke API no GitHub
```

### Base de dados local com Docker (opcional)

```bash
chmod +x scripts/run-e2e-docker-foundation.sh
./scripts/run-e2e-docker-foundation.sh
# seguir os exports e comandos impressos (Alembic + seed + uvicorn + ng serve)
```

Gates locais (inclui smoke API): `./scripts/run-qa-gates.sh` ou **`make qa`** na raiz.

**Opcional CI:** `.github/workflows/e2e-api-smoke-weekly.yml` — *schedule* segunda 07:00 UTC + *workflow_dispatch* (só smoke API, sem browser).

**E2E one-shot no GitHub:** `.github/workflows/e2e-one-shot-dispatch.yml` — *Actions* → **E2E one-shot (manual)** → *Run workflow* (Docker + Postgres efémero + `ng serve` + Playwright; ~45 min timeout).

### QA opcional (pós-gates)

```bash
./scripts/run-qa-optional.sh
E2E_INSTALL_BROWSERS=1 ./scripts/run-qa-optional.sh
make qa-optional-full   # inclui run-e2e-one-shot-stack.sh (Docker + suite completa)
```

### Dependabot

`.github/dependabot.yml` — PRs para `apps/web`, `e2e`, pacotes Python (`apps/api`, `packages/*`, `apps/worker`) e *github-actions* mensal. Validar com `./scripts/run-qa-gates.sh`.
