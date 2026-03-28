# Workflows GitHub Actions (4Pro_BI)

| Ficheiro | Quando corre | Notas |
|----------|----------------|-------|
| `ci.yml` | Push/PR `main`/`master`, `workflow_dispatch` | Ruff, pytest, Alembic+Postgres, build web, **e2e-api-smoke-local** → chama `reusable-e2e-api-smoke.yml`. |
| `reusable-e2e-api-smoke.yml` | Só via `workflow_call` | Playwright `smoke-api` + uvicorn SQLite; inputs `artifact-name`, `artifact-retention-days`. |
| `e2e-api-smoke-weekly.yml` | Cron (segunda 07:00 UTC) + `workflow_dispatch` | Mesmo job que o smoke API do CI (reutilizável). |
| `e2e-dispatch.yml` | `workflow_dispatch` | Stack Postgres+Redis+API+ng; modo **full** ou **api_stack**. |
| `e2e-one-shot-dispatch.yml` | `workflow_dispatch` | E2E one-shot (Postgres Docker + Alembic + API + `ng serve` + Playwright); inputs para saltar `npm ci`/instalação de browser quando o runner já tem cache. |
| `e2e-seed-storage-dispatch.yml` | `workflow_dispatch` | Postgres (serviço) + Alembic + `dev_seed` + `scripts/seed_e2e_storage_warn.py` + `cleanup_e2e_storage_seed.py` (validação dos scripts). |
| `e2e-storage-warn-browser-dispatch.yml` | `workflow_dispatch` | API + `ng serve` + Playwright `context-storage-ui` (fluxo de aviso de armazenamento no browser). |

## Outros ficheiros em `.github/`

| Ficheiro | Uso |
|----------|-----|
| [`dependabot.yml`](../dependabot.yml) | Dependabot (npm, pip, GitHub Actions) — **não** é um workflow. |
| [`CODEOWNERS`](../CODEOWNERS) | Revisores por caminho (descomentar equipas). |
| [`pull_request_template.md`](../pull_request_template.md) | Checklist de PR. |

## Manutenção

Alterações ao fluxo “smoke API no Actions”: **`reusable-e2e-api-smoke.yml`** + **`scripts/run-e2e-api-smoke-local.sh`** (sem duplicar passos noutros YAML).

## Validação local (opcional)

`make lint-actions` usa `actionlint` no PATH **ou**, se Docker estiver disponível, a imagem `rhysd/actionlint:latest` (defina `ACTIONLINT_NO_DOCKER=1` para desativar o fallback).

```bash
make lint-actions
# ou: actionlint .github/workflows/*.yml
```
fina `ACTIONLINT_NO_DOCKER=1` para desativar o fallback).

```bash
make lint-actions
# ou: actionlint .github/workflows/*.yml
```
