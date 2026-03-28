# Docker Compose (desenvolvimento)

## Serviços

- **postgres** — porta `5432` (credenciais padrão em `.env.example` na raiz).
- **redis** — porta `6379`.
- **minio** — no host: API `7291`→9000, consola `7292`→9001 (ver `infra/compose/.env`).

## Uso

Na raiz do repositório ou nesta pasta:

```bash
docker compose -f docker-compose.yml up -d postgres redis
```

Variáveis opcionais: ver comentários em `docker-compose.yml` e `.env.example` na raiz.
