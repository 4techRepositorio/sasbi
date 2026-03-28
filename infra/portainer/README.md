# Deploy no Portainer (Stacks)

Este diretório contém **definições de Stack** no formato Docker Compose, prontas para **Portainer → Stacks → Add stack**.

## Arquivos

| Stack | Uso |
|-------|-----|
| [stack-4pro-bi.yml](./stack-4pro-bi.yml) | **Recomendado:** Postgres, Redis, MinIO, API, Worker e Web em uma única stack. |
| [stack-4pro-data-only.yml](./stack-4pro-data-only.yml) | Somente dados; rede nomeada `fourpro_data` para outra stack de app (avançado). |

## Build / contexto

- O ficheiro `stack-4pro-bi.yml` assume localização em **`infra/portainer/`** dentro do repo. Os `build.context` usam `../..` (raiz do monorepo) para que `apps/api/Dockerfile` encontre `packages/`.
- No Portainer: **Compose path** `infra/portainer/stack-4pro-bi.yml` a partir da raiz do Git.
- Se colar a stack na raiz do repo, ajuste `context` para `.` e `dockerfile` como nos Dockerfiles originais.

Se o Portainer só montar a subpasta `infra/portainer`, **o build falhará** (Dockerfile precisa de `packages/` e `apps/`). Soluções:

1. Clonar o repo completo e definir **stack from file** com contexto na raiz; ou  
2. Gerar imagens num CI e referenciar apenas `image:` em vez de `build:`.

## Variáveis obrigatórias (produção)

- `JWT_SECRET` — string longa e aleatória.  
- `MINIO_ROOT_PASSWORD` — credencial da consola MinIO.

## Pós-deploy

1. API exposta em `API_PUBLISH` (default **`6418`**): `GET /api/v1/health`.  
2. Se `RUN_SEED=true` (default no YAML), o entrypoint corre migrates + seed (`admin@local.dev` / `changeme`).  
3. Web em `WEB_PUBLISH` (**`8081`**). MinIO no host: **`7291`** (S3) e **`7292`** (consola).

## Esteira local (sem Portainer)

Ver `scripts/run-ticket-pipeline.sh` na raiz do repositório.
