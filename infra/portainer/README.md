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

### `RUN_SEED` (bootstrap)

- **`RUN_SEED=true`** — no primeiro arranque (ou quando quiser repor utilizadores de demo), o entrypoint da API corre o seed após migrates.  
- **Após o primeiro bootstrap com dados reais**, definir **`RUN_SEED=false`** para não reexecutar o seed em cada restart (ver modelo [`.env.production.example`](./.env.production.example)).

### `RATE_LIMIT_TRUST_PROXY`

- Com **`true`**, a API usa o IP em `X-Forwarded-For` para o slowapi. Adequado quando o tráfego **só** chega à API via container **`web`** (Nginx já define o cabeçalho) e a porta **`API_PUBLISH`** **não** está exposta ao público.  
- Se a API estiver acessível directamente na Internet, manter **`false`** (default no YAML).

## Scripts na raiz (`scripts/`)

| Script | Função |
|--------|--------|
| [`stack-up.sh`](../../scripts/stack-up.sh) | `docker compose … up -d --build` com `infra/portainer/.env`. |
| [`stack-down.sh`](../../scripts/stack-down.sh) | `docker compose … down` (sem `-v`). Com dados: `STACK_DOWN_VOLUMES=1 ./scripts/stack-down.sh`. |
| [`stack-ps.sh`](../../scripts/stack-ps.sh) | `docker compose ps`. |
| [`stack-logs.sh`](../../scripts/stack-logs.sh) | `docker compose logs -f` (opcional: nomes de serviços). |
| `make stack-up` / `stack-down` / `stack-ps` / `stack-logs` | Atalhos na raiz do repo (`Makefile`). |

## Migrações e pacote `contracts` (staging / produção)

- **Subida do contentor API** — O `docker-entrypoint.sh` da imagem executa **`alembic upgrade head`** antes de arrancar o Uvicorn. Após um deploy com imagem actualizada, o schema fica alinhado sem passo manual extra.
- **Rebuild obrigatório quando mudar código** — O Dockerfile copia `packages/contracts` e instala com `pip install -e`. Novas revisões de contratos ou migrações exigem **rebuild da imagem** (`docker compose ... up -d --build` ou equivalente no Portainer) e **redeploy** dos serviços `api` e `worker` (o worker também embute `apps/api` + contratos no build).
- **`RUN_SEED`** — Em produção, use `RUN_SEED=false` após o primeiro bootstrap para não voltar a executar o seed em cada restart.
- **Só Postgres acessível (API na máquina host)** — Na raiz do repo: `chmod +x scripts/run-db-migrate.sh && ./scripts/run-db-migrate.sh` (carrega `.env` e usa `apps/api/.venv` ou `.venv` para o Alembic).
- **CI (GitHub Actions)** — O workflow `.github/workflows/ci.yml` inclui o job `alembic-postgres` (verificação de **head único** + `upgrade head` em Postgres vazio) em cada push/PR à `main`/`master`.
- **Paridade local sem Postgres instalado** — `scripts/run-alembic-postgres-local.sh` (Docker; porta host aleatória por omissão para evitar conflitos).

## Imagem `web`

- O build usa `apps/web/Dockerfile` com contexto **`apps/web`** (ver `stack-4pro-bi.yml`).  
- Opcionais de produção na API (mesma stack): `REFRESH_RATE_LIMIT`, `RATE_LIMIT_TRUST_PROXY` — ver `docs/ARCHITECTURE.md` e `.env` comentado.

## Pós-deploy

1. API exposta em `API_PUBLISH` (default **`6418`**): `GET /api/v1/health`.  
2. Se `RUN_SEED=true` (default no YAML), o entrypoint corre migrates + seed (`admin@local.dev` / `changeme`).  
3. Web em `WEB_PUBLISH` (**`8081`**). MinIO no host: **`7291`** (S3) e **`7292`** (consola).  
4. E2E browser contra a stack: `./scripts/run-e2e-stack-browser.sh` (com `e2e/.env.e2e`).

## Esteira local (sem Portainer)

Ver `scripts/run-ticket-pipeline.sh` na raiz do repositório.
