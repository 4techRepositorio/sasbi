# API (FastAPI)

## Pré-requisitos

- Python 3.12+
- Postgres (via `infra/compose`) para desenvolvimento local
- Pacotes locais: na raiz do monorepo, `pip install -r requirements-dev.txt` (ou só contracts + api)

## Variáveis

Ver `.env.example` na raiz do monorepo. Mínimo para subir:

- `DATABASE_URL`
- `JWT_SECRET` (string longa e aleatória em produção)

## Banco e migrações

```bash
cd infra/compose && docker compose up -d postgres
cd ../../apps/api
export DATABASE_URL=postgresql+psycopg2://fourpro:K8mpQ4wxN2vR7sFourProBIdev2026@127.0.0.1:5432/fourpro
export JWT_SECRET=fourpro-bi-dev-jwt-hs256-2026-substituir-em-producao-64chars___
alembic upgrade head
python -m fourpro_api.dev_seed
```

## Servidor

```bash
cd apps/api
export DATABASE_URL=... JWT_SECRET=...
uvicorn fourpro_api.main:app --reload --host 0.0.0.0 --port 6418
```

- Health: `GET http://localhost:6418/api/v1/health` (porta alinhada a `API_PUBLISH` em `.env`)
- Login: `POST http://localhost:6418/api/v1/auth/login`

## Testes

```bash
cd apps/api
pytest -q
```

Usa SQLite em memória por fixture; não exige Docker.
