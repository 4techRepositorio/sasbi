# Scripts (raiz do monorepo)

Índice curto dos scripts mais usados. Detalhes adicionais: `infra/portainer/README.md`, `e2e/README.md`, `CONTRIBUTING.md`.

| Script | Uso |
|--------|-----|
| `run-qa-gates.sh` | Gates principais (Ruff, pytest API, build web, smoke Playwright API). |
| `run-qa-optional.sh` | Alembic em Postgres Docker + E2E browser opcional (`QA_OPTIONAL_E2E_ONE_SHOT`). |
| `run-db-migrate.sh` | `alembic upgrade head` com `DATABASE_URL` do `.env`. |
| `run-alembic-postgres-local.sh` | Smoke equivalente ao job CI `alembic-postgres` (Postgres em Docker). |
| `run-e2e-api-smoke-local.sh` | API SQLite + smoke Playwright só API. |
| `run-e2e-one-shot-stack.sh` | Stack Docker + Playwright (demora). |
| `gh-e2e-dispatch.sh` | Dispara workflow E2E no GitHub (`gh workflow run`). |
| `lint-github-actions.sh` | actionlint nos workflows (também `make lint-actions`). |
| `dev-local.sh` | Arranque local de desenvolvimento (ver comentários no ficheiro). |
| `stack-up.sh` / `stack-down.sh` / `stack-ps.sh` / `stack-logs.sh` | Compose Portainer (`make stack-up`, `stack-down`, `stack-ps`, `stack-logs`; ver `infra/portainer/`). |
| `export-wireframes-from-pdf.sh` | Rasteriza `Data Analytics Solution.pdf` → `docs/assets/wireframes/exports/data-analytics-solution-p-*.png` (requer `pdftoppm`). Também `make wireframes-export`. |

Outros (`run-e2e-*.sh`, `run-ticket-pipeline.sh`, etc.) servem cenários específicos de QA ou pipelines internos.
