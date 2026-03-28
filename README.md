# 4Pro_BI — Plataforma SaaS multitenant de dados

Monorepo com API **FastAPI**, frontend **Angular**, worker **Celery**, contratos **Pydantic** e infra **Docker Compose**.

## Início rápido

Em máquina partilhada (portas não clássicas no `.env`): **`./scripts/dev-local.sh`** sobe Postgres/Redis/MinIO e mostra os comandos para API (**7418**) + **`ng serve`** (**4200**).

1. **Infra local**
   ```bash
   cd infra/compose && docker compose up -d postgres redis
   ```
2. **Python (API + pacotes)**
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements-dev.txt
   ```
3. **Migrações e seed**
   ```bash
   cp -n .env.example .env 2>/dev/null || true
   set -a && [ -f .env ] && . ./.env && set +a
   cd apps/api && alembic upgrade head && python -m fourpro_api.dev_seed
   ```
   Credenciais padrão já estão em `.env` e `.env.example` (sincronizadas).
4. **API**
   ```bash
   cd apps/api && uvicorn fourpro_api.main:app --reload --port 7418
   ```
5. **Web**
   ```bash
   cd apps/web && npm start
   ```
   Com Docker/Portainer, a UI fica tipicamente em **http://localhost:8081** (porta 8081 no host; 80/8080 evitados).

## Portainer (stacks)

Definições em [infra/portainer/](infra/portainer/README.md): stack completa `stack-4pro-bi.yml` (Postgres, Redis, MinIO, API, Worker, Web). No Portainer use **Stacks → Add stack** e o Compose path `infra/portainer/stack-4pro-bi.yml`.

## Esteira de tickets (local)

```bash
./scripts/run-ticket-pipeline.sh
```

Sobe Postgres/Redis, aplica migrações, seed, `pytest` e indica smoke da API.

## Qualidade, migrações e paridade com CI

Índice dos scripts: [scripts/README.md](scripts/README.md).

| Objectivo | Comando |
|-----------|---------|
| Gates iguais ao GitHub Actions (Ruff, pytest API, Angular, Playwright) | `./scripts/run-qa-gates.sh` ou `make qa` |
| Acima + Alembic em Postgres efémero (Docker), como o job `alembic-postgres` | `RUN_ALEMBIC_PG_LOCAL=1 ./scripts/run-qa-gates.sh` ou `make qa-alembic` |
| Opcional: Alembic smoke + E2E browser (se `e2e/.env.e2e`) | `make qa-optional` |
| Só smoke API Playwright + uvicorn SQLite (rápido) | `make e2e-api-local` |
| Disparar **E2E (manual)** no GitHub (`gh`) | `make e2e-dispatch` |
| `alembic upgrade head` com `DATABASE_URL` do `.env` | `./scripts/run-db-migrate.sh` ou `make migrate` |
| Só Postgres Docker + head único + upgrade (smoke rápido) | `./scripts/run-alembic-postgres-local.sh` ou `make alembic-pg-local` |
| CI manual no GitHub | *Actions* → workflow **CI** → **Run workflow** (`workflow_dispatch`) |
| Smoke API semanal (cron + dispatch) | *Actions* → **E2E API smoke (semanal)** |
| Lint workflows (opcional, [actionlint](https://github.com/rhysd/actionlint)) | `make lint-actions` |

**Pre-commit (opcional):** `pip install pre-commit && pre-commit install` — usa `.pre-commit-config.yaml` (Ruff na API).

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| [docs/README.md](docs/README.md) | **Índice** da documentação (arquitectura, planos, wireframes, assets) |
| [docs/assets/README.md](docs/assets/README.md) | Como **imagens e diagramas** são gerados e onde ficam |
| [docs/plans/README.md](docs/plans/README.md) | Planos de execução e tickets |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Blocos e domínios |
| [docs/VISION.md](docs/VISION.md) | Visão de produto |
| [tickets/](tickets/) | Tickets do projeto 4Pro_BI |
| [docs_planos_antigos/](docs_planos_antigos/plans/README.md) | Planos OSS históricos (P0–P8) |

## Variáveis

Copie [.env.example](.env.example) e ajuste. Nunca commite `.env` com segredos reais.

## Contribuir e segurança

- [CONTRIBUTING.md](CONTRIBUTING.md) — gates locais, frentes do monorepo, migrações.
- [docs/SECURITY.md](docs/SECURITY.md) — política de segurança (reporte + controlos); [SECURITY.md](SECURITY.md) na raiz é o atalho para o GitHub.

## Licença

Definir pelo mantenedor do projeto.
