# Worker (Celery)

## Execução local

Com Redis no Compose:

```bash
# Com `infra/compose`: Redis no host usa 16379 por defeito (ver `.env.example`).
export REDIS_URL=redis://127.0.0.1:16379/0
celery -A fourpro_worker.celery_app worker --loglevel=info
```

Smoke: `celery -A fourpro_worker.celery_app call fourpro.ping`

Instalação: `pip install -e ../../packages/shared -e .` (a partir de `apps/worker`).

## Partição do projeto (Frente Backend Data)

Alterações ao pipeline de ingestão, tarefas Celery e `packages/shared` (parsing) pertencem a esta frente. A tarefa `fourpro.parse_ingestion` executa `fourpro_api.jobs.ingestion_parse.run_ingestion_parse`: estados `uploaded` → `validating` (tamanho + `validate_upload_content`) → `parsing` → `processed` ou `failed`, com mensagem amigável e log técnico no registo. Estados e responsabilidades: ver `docs/INGESTION.md`. Novas revisões Alembic **só** para tabelas de dados devem usar ficheiros em `apps/api/alembic/versions/` com prefixo `data__` no nome, sem editar revisões existentes.
