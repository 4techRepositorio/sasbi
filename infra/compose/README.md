# Docker Compose (desenvolvimento)

## Serviços

- **postgres** — no host: `15432`→5432 (defeito; evita colisão com Postgres na 5432 do host). Ajuste `POSTGRES_PORT` no `.env`.
- **redis** — no host: `16379`→6379 (defeito; evita colisão com Redis na 6379 do host). Ajuste `REDIS_PORT` no `.env`.
- **minio** — no host: API `17291`→9000, consola `17292`→9001 (defeito; ajuste `MINIO_*` no `.env`).

## Uso

Na raiz do repositório ou nesta pasta:

```bash
docker compose -f docker-compose.yml up -d postgres redis
```

Variáveis opcionais: ver comentários em `docker-compose.yml` e `.env.example` na raiz.
