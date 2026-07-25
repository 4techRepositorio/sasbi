# OpenAPI / Swagger — 4Pro_BI API

## O que faz

Descreve o contrato HTTP da API (`apps/api`) em OpenAPI 3.x: paths, schemas, autenticação Bearer e códigos de resposta. Serve clientes (web, desktop, integrações) e revisão de impacto em PRs.

## Como funciona

| Superfície | URL (API local em `:7418`) | Origem |
|------------|----------------------------|--------|
| **Swagger UI** | `http://localhost:7418/docs` | FastAPI (runtime) |
| **ReDoc** | `http://localhost:7418/redoc` | FastAPI (runtime) |
| **Schema JSON** | `http://localhost:7418/openapi.json` | FastAPI (runtime) |
| **Snapshot Git** | [`openapi.json`](./openapi.json) | Gerado por `scripts/export-openapi.sh` |

O snapshot no repositório é a referência para diff em PR e consumo offline. Em caso de divergência, o runtime da versão deployada prevalece; o snapshot deve ser regenerado no mesmo PR.

Prefixo estável: **`/api/v1`**.

## Como instalar

Não há instalação separada: a UI Swagger/ReDoc acompanha a API. Para trabalhar só com o ficheiro:

```bash
# após venv + pip install -r requirements-dev.txt
./scripts/export-openapi.sh
```

## Como configurar

- Porta e CORS: `.env` (`API_PUBLISH`, `CORS_ORIGINS`).
- Em produção atrás do Nginx (`apps/web`), o path `/docs` pode estar ou não exposto publicamente — preferir **não** expor Swagger na Internet; usar o snapshot + VPN/staging.
- Autenticação nas rotas protegidas: header `Authorization: Bearer <access_token>`.

## Como testar

1. Subir a API (`docs/INSTALLATION.md` ou `apps/api/README.md`).
2. Abrir `/docs` e executar `GET /api/v1/health`.
3. Login via `POST /api/v1/auth/login` (Authorize no Swagger com o `access_token`).
4. Regenerar e revisar o diff do snapshot:

```bash
./scripts/export-openapi.sh
git diff -- docs/openapi/openapi.json
```

## Como evoluir

- Alterações em routers ou `packages/contracts` → regenerar `openapi.json` no PR.
- Novos estados de ingestão ou campos de `/me/context` → nota de impacto em `docs/ARCHITECTURE.md` ou ADR + este snapshot.
- Versionamento futuro (`/api/v2`) exige ADR de compatibilidade.

## Catálogo resumido (v0.1.0)

| Área | Paths principais |
|------|------------------|
| Health | `GET /health`, `GET /health/ready` |
| Auth | `POST /auth/login`, `/mfa/verify`, `/refresh`, `/forgot-password`, `/reset-password` |
| Contexto | `GET /me/context` |
| Tenant (admin) | members, audit-log, quota-groups |
| Dados | `POST /uploads`, `GET /ingestions`, reprocess, `GET /datasets` |

Exemplos práticos: [`docs/examples/`](../examples/README.md).
