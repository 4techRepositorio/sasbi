# QA Checklist

Índice dos ficheiros em `.github/workflows/`: [`.github/workflows/README.md`](../../.github/workflows/README.md).

## Gates obrigatórios (iguais ao CI)

| Gate | Comando | Se falhar |
|------|---------|-----------|
| Ruff | `ruff check` + `ruff format --check` em `apps/api/fourpro_api` e `apps/api/tests` (linha 100; isort activo) | `ruff format apps/api/fourpro_api apps/api/tests` e `ruff check --fix` onde seguro |
| API | `.venv/bin/python -m pytest apps/api/tests -q --tb=short` (após `pip install -r requirements-dev.txt` num venv) | Ver traceback; reexecutar: `.venv/bin/python -m pytest apps/api/tests/test_<area>.py -vv` |
| Alembic + Postgres | **CI:** job `alembic-postgres` em `.github/workflows/ci.yml` (head único + `upgrade head` em Postgres vazio). **Local:** `./scripts/run-alembic-postgres-local.sh` (Docker + venv com Alembic) | Ver saída `alembic heads`; conflito de revisões = corrigir cadeia em `apps/api/alembic/versions/` |
| Migrações (BD já a correr) | `./scripts/run-db-migrate.sh` com `DATABASE_URL` no `.env` | Postgres acessível; mesma ordem que entrypoint da API em deploy |
| Web (tsc) | `cd apps/web && npm ci && npm run typecheck` | Erros de tipos em `src/` |
| Web (build) | `cd apps/web && npm run build` | Correr `npm run build` com saída completa; ver erros de template |
| E2E | `cd e2e && npm ci && npx playwright test` | Sem stack/credenciais = só *skipped* (OK). Com env: ver `e2e/README.md` e `e2e/test-results/` |
| E2E API (local) | `./scripts/run-e2e-api-smoke-local.sh` | Smoke `GET /api/v1/health` e `/health/ready` sem Docker; requer `.venv` na raiz. **CI:** job `e2e-api-smoke-local` em `.github/workflows/ci.yml` |
| E2E API smoke | `./scripts/run-e2e-api-smoke.sh` | Exige API no ar; default URL usa `API_PUBLISH` do `.env` na raiz (**7418** em dev local). Portainer: `E2E_API_BASE_URL=http://127.0.0.1:6418` |
| E2E login UI | `E2E_INSTALL_BROWSERS=1 ./scripts/run-e2e-ui-login-smoke.sh` | Exige front + `E2E_USER_*` em `e2e/.env.e2e` |
| E2E auditoria | `E2E_INSTALL_BROWSERS=1 ./scripts/run-e2e-audit-smoke.sh` | Conta **admin** sem MFA; rota `/app/tenant-audit` |
| E2E RBAC | `./scripts/run-e2e-rbac-smoke.sh` | Exige consumer + `PLAYWRIGHT_BASE_URL` em `.env.e2e` |
| E2E suite local | `./scripts/run-e2e-all-local.sh` | Opcional `E2E_INSTALL_BROWSERS=1`; ver `e2e/README.md` |
| E2E stack Docker | `./scripts/run-e2e-stack-browser.sh` | Espera API (`6418`) + web (`8081`); `e2e/.env.e2e` com admin, consumer e `E2E_RUN=1` |
| Stack Portainer | `./scripts/stack-up.sh` / `./scripts/stack-down.sh` | Subir ou parar stack local; `STACK_DOWN_VOLUMES=1` só para limpar volumes |
| E2E GitHub | *Actions* → **E2E (manual)** | `e2e-dispatch.yml`: modo **full** (browser) ou **api_stack** (só smoke HTTP); artefactos `e2e-artifacts-full` / `e2e-artifacts-api_stack` |
| E2E one-shot (GH) | *Actions* → **E2E one-shot (manual)** | `e2e-one-shot-dispatch.yml` — paridade com `make e2e-one-shot` (Postgres Docker efémero na VM do runner) |
| E2E dispatch CLI | `./scripts/gh-e2e-dispatch.sh [ref] [modo]` | `modo` = `full` (omissão) ou `api_stack`; requer `gh auth login` |
| E2E + Docker DB | `./scripts/run-e2e-docker-foundation.sh` | Só Postgres+Redis; depois Alembic/seed/uvicorn conforme `e2e/README.md` |
| E2E one-shot | `make e2e-one-shot` ou `./scripts/run-e2e-one-shot-stack.sh` | Docker Postgres efémero + stack + Playwright (ver `E2E_ONE_SHOT_*`). `make qa-optional-full` = opcionais + one-shot |
| QA opcional | `./scripts/run-qa-optional.sh` | Alembic Postgres smoke + E2E browser se `e2e/.env.e2e` existir. `QA_OPTIONAL_E2E_ONE_SHOT=1` acrescenta `run-e2e-one-shot-stack.sh` (Docker + suite completa) |
| E2E manual `api_stack` | *Actions* ou `gh-e2e-dispatch.sh ref api_stack` | Workflow sem Angular; artefacto `e2e-artifacts-api_stack` |
| Workflows YAML (opcional) | `make lint-actions` | [actionlint](https://github.com/rhysd/actionlint) no PATH ou Docker (`rhysd/actionlint`); `ACTIONLINT_NO_DOCKER=1` força só PATH |
| Dependabot | `.github/dependabot.yml` | PRs de deps; validar com `./scripts/run-qa-gates.sh` |
| E2E API semanal | `.github/workflows/e2e-api-smoke-weekly.yml` | Cron + *dispatch*; reutiliza `reusable-e2e-api-smoke.yml` (mesmo que o job CI) |

**Variáveis de ambiente** (pytest API, alinhadas a `.github/workflows/ci.yml`):

- `DATABASE_URL=sqlite:///:memory:`
- `JWT_SECRET` — mínimo 32 caracteres (ex.: o valor usado no CI)
- `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` — opcionais; o `conftest.py` define defaults

**Paridade local com CI** (recomendado antes de PR): cria/usar `.venv` na raiz, Ruff, pytest, typecheck/build web e Playwright (e2e).

```bash
chmod +x scripts/run-qa-gates.sh   # uma vez
./scripts/run-qa-gates.sh
# Opcional: mesmo gate que o job alembic-postgres (Docker obrigatório):
RUN_ALEMBIC_PG_LOCAL=1 ./scripts/run-qa-gates.sh
# Make: make qa | make qa-alembic | make qa-optional | make qa-optional-full | make e2e-api-local | make e2e-one-shot | make e2e-dispatch | make migrate | make alembic-pg-local | make lint-actions | make wireframes-export
```

O script cria `.venv/` na raiz do monorepo — já ignorado por `.gitignore` na raiz do repositório.

### Dependabot (opcional)

PRs automáticos semanais/mensais: [`.github/dependabot.yml`](../../.github/dependabot.yml) (npm, pip por pacote, **GitHub Actions**). Rever major bumps (Angular, FastAPI) com testes completos.

### Issues e CODEOWNERS (opcional)

- Modelos: [`.github/ISSUE_TEMPLATE/`](../../.github/ISSUE_TEMPLATE/) (`bug_report`, `feature_request`).
- PR: [`.github/pull_request_template.md`](../../.github/pull_request_template.md).
- [`.github/CODEOWNERS`](../../.github/CODEOWNERS) — descomentar `@org/equipa` quando existirem equipas no GitHub.

### `npm audit` (apps/web)

`npm audit fix` **sem** `--force` costuma **não** resolver avisos em cadeias `tar` / `serialize-javascript` trazidas por `@angular/cli` e `build-angular`; o `npm` sugere major Angular (quebra compatível). Tratar como risco **dev/build-time** — roadmap: [docs/plans/PLANO-UPGRADE-ANGULAR-AUDIT.md](../plans/PLANO-UPGRADE-ANGULAR-AUDIT.md). Não usar `audit fix --force` em CI sem testes completos.

## Regressão coberta em `apps/api/tests` (mapa rápido)

| Área | Ficheiros de teste (exemplos) |
|------|--------------------------------|
| Auth / sessão | `test_auth.py`, `test_audit_log.py` |
| MFA | `test_mfa_flow.py` |
| Reset de senha | `test_password_reset.py`, `test_security_password.py` |
| Contexto tenant / me | `test_me_context.py`, `test_storage_quota.py` (campo `storage` em `/me/context`) |
| RBAC / membros | `test_tenant_members.py`, `test_upload_rbac.py` |
| Upload / ingestões | `test_upload_rbac.py`, `test_ingestions.py`, `test_parse_job.py` |
| Catálogo | `test_datasets_catalog.py` |
| Billing / quotas | `test_billing_enforcement.py`, `test_storage_quota.py` (plano, utilizador, grupo) |
| Health | `test_health.py` (`/health`, `/health/ready`) |
| E2E quotas UI | `context-storage-ui.spec.ts` — bloco na shell; `E2E_EXPECT_STORAGE_WARN=1` + seed/limpeza scripts; CI: `e2e-seed-storage-dispatch.yml` (scripts) e `e2e-storage-warn-browser-dispatch.yml` (API+ng+Playwright) |

## Critérios de aceite por feature

- Fluxo feliz validado
- Erro esperado validado (mensagem ou código HTTP coerente)
- Permissão validada (403 quando aplicável)
- Isolamento por tenant validado
- Contratos impactados revisados (`packages/contracts` quando a frente alterar DTOs)
- Checklists de backend/frontend atualizados quando a entrega o exigir

## E2E / smoke browser

- Pasta `e2e/` — Playwright; testes sem variáveis (`E2E_API_BASE_URL`, credenciais, `E2E_RUN=1` para RBAC) ficam **skipped** (exit 0).
- `tenant-audit.spec.ts`: admin (`E2E_USER_*`) abre `/app/tenant-audit`, export CSV (download); consumer com `E2E_RUN=1` valida redirect + banner em URL directa. API: `test_tenant_audit_log.py` (JSON + `export.csv`).
- Stack Docker + browser: `./scripts/run-e2e-stack-browser.sh` após `docker compose up` em `infra/portainer` (requer `e2e/.env.e2e` com credenciais do seed).
- CI: job `e2e-api-smoke-local` em `.github/workflows/ci.yml` corre smoke API + Playwright; testes sem credenciais podem ficar *skipped* (exit 0).
- Ver `e2e/README.md` para URLs e credenciais de exemplo.
- **Wireframes (opcional):** PNG a partir do PDF — `make wireframes-export` ou `bash scripts/export-wireframes-from-pdf.sh`. Capturas da app — `E2E_WIREFRAME_CAPTURES=1` + `cd e2e && npm run test:wireframe-captures` (front no ar; `E2E_USER_*` admin sem MFA; inclui sidebar `workspace-shell-v1-*`, dashboard, pipeline, billing/settings/auditoria).
