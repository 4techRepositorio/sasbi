# 4Pro_BI — Plataforma SaaS multitenant de dados

Monorepo com API **FastAPI**, frontend **Angular**, worker **Celery**, contratos **Pydantic** e infra **Docker Compose**.

## Início rápido

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
   cd apps/api && uvicorn fourpro_api.main:app --reload --port 6418
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

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| [docs/README.md](docs/README.md) | **Índice** da documentação (arquitectura, planos, wireframes, assets) |
| [docs/assets/README.md](docs/assets/README.md) | Como **imagens e diagramas** são gerados e onde ficam |
| [docs/plans/README.md](docs/plans/README.md) | Planos de execução e tickets |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Blocos e domínios |
| [docs/VISION.md](docs/VISION.md) | Visão de produto |
| [tickets/](tickets/) | Tickets do MVP |
| [docs_planos_antigos/](docs_planos_antigos/plans/README.md) | Planos OSS históricos (P0–P8) |

## Variáveis

Copie [.env.example](.env.example) e ajuste. Nunca commite `.env` com segredos reais.

## Licença

Definir pelo mantenedor do projeto.
