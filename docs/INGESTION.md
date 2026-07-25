# Ingestion

## O que faz

Pipeline de aquisição e processamento de ficheiros (TXT, CSV, XLS, XLSX, JSON) até ao catálogo, com estados explícitos e isolamento por tenant.

## Como funciona

Fluxo obrigatório:

1. aquisição (upload físico **ou** extract de conector — TICKET-015)
2. registro de metadata
3. validação
4. parsing
5. normalização
6. persistência
7. catálogo
8. logs
9. status final

Hoje a aquisição em produção é **upload de ficheiro**. O programa de conectores unifica fontes no mesmo ciclo de status — ver [`plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md`](./plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md).

### Status mínimos

- `uploaded`
- `validating`
- `parsing`
- `processed`
- `failed`

Diagramas: [diagrams/ingestion-flow.md](./diagrams/ingestion-flow.md).

### Quotas (billing / armazenamento)

- O **POST de upload** (`/api/v1/uploads`) consulta o **BillingService**: limite mensal de ficheiros **e** armazenamento (`max_storage_mb`), somando `size_bytes` das ingestões do tenant.
- Podem aplicar-se limites por **utilizador** e **grupo de quota**.
- O **worker** não duplica a verificação na fila — a cota é na aceitação do upload.
- Uso vs limites: **`GET /api/v1/me/context`** (`storage`).

## Como instalar

API + Postgres + (para parse completo) Redis + Worker — [INSTALLATION.md](./INSTALLATION.md) / [DEPLOYMENT.md](./DEPLOYMENT.md).

## Como configurar

`UPLOAD_DIR`, `MAX_UPLOAD_MB`, `REDIS_URL`, credenciais MinIO em stack completa.

## Como testar

- `pytest` na API; exemplo [`examples/02-upload-ingest.sh`](./examples/02-upload-ingest.sh).
- E2E pipeline quando a stack completa estiver no ar.

## Como evoluir

Novos formatos/estados → contrato `fourpro_contracts.ingestion` + migração + diagramas + OpenAPI. Conectores: TICKET-015.
