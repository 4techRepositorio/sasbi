# Worker (Celery)

## Execução local

Com Redis no Compose:

```bash
export REDIS_URL=redis://127.0.0.1:6379/0
celery -A fourpro_worker.celery_app worker --loglevel=info
```

Smoke: `celery -A fourpro_worker.celery_app call fourpro.ping`

Instalação: `pip install -e ../../packages/shared -e .` (a partir de `apps/worker`).
