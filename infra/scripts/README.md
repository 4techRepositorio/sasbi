# Scripts

Scripts auxiliares de setup, build e validação.

## Na raiz do repositório (`scripts/`)

| Script | Função |
|--------|--------|
| `run-qa-gates.sh` | Paridade com CI (Ruff, pytest API, build Angular, Playwright). |
| `run-db-migrate.sh` | `alembic upgrade head` com `DATABASE_URL` do `.env` (venv `apps/api/.venv` ou `.venv`). |
| `run-alembic-postgres-local.sh` | Paridade com CI: Postgres 16 em Docker + head único + `upgrade head` (sem `.env`). |
| `run-e2e-local.sh`, `run-e2e-api-smoke.sh`, `run-ticket-pipeline.sh` | Fluxos e2e / pipeline de tickets. |

Migrações em stack Docker/Portainer: ver `infra/portainer/README.md` (entrypoint da API já corre Alembic).
