# Exemplos — 4Pro_BI API

## O que faz

Scripts e pedidos HTTP de referência para exercitar a API sem UI: autenticação, contexto, upload/ingestão e catálogo.

## Como funciona

| Ficheiro | Cenário |
|----------|---------|
| [01-auth.sh](./01-auth.sh) | Login + refresh + `/me/context` |
| [02-upload-ingest.sh](./02-upload-ingest.sh) | Upload CSV → poll ingestão → datasets |
| [sample-data.csv](./sample-data.csv) | Ficheiro mínimo para upload |

Assumem API em `http://127.0.0.1:7418` (override com `API_BASE`). Credenciais default do seed de desenvolvimento.

## Como instalar

```bash
# API a correr (ver docs/INSTALLATION.md)
chmod +x docs/examples/*.sh
```

Dependências: `curl`, `bash`; `jq` recomendado.

## Como configurar

```bash
export API_BASE=http://127.0.0.1:7418
export E2E_USER_EMAIL=admin@local.dev
export E2E_USER_PASSWORD=changeme
```

## Como testar

```bash
./docs/examples/01-auth.sh
./docs/examples/02-upload-ingest.sh
```

Esperado: HTTP 200 no login/contexto; upload cria ingestão; eventual `processed` quando o worker estiver activo (sem worker o estado pode permanecer `uploaded`).

## Como evoluir

Novos endpoints públicos → acrescentar exemplo aqui + regenerar OpenAPI. Não commitar tokens reais nem `.env` de produção.
