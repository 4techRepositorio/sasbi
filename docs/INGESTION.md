# Ingestion

## Fluxo obrigatório
1. aquisição (upload físico **ou** extract de conector — TICKET-015)
2. registro de metadata
3. validação
4. parsing
5. normalização
6. persistência
7. catálogo
8. logs
9. status final

Aquisição suportada: **upload de ficheiro** (`POST /uploads`) e **sync de conector**
(`POST /data-sources/{id}/sync`) via SPI (`file`, `postgres`, `rest_json`). Ambos
criam `file_ingestions` no ciclo de status abaixo, com `correlation_id` e camada
inicial `bronze` (promoção: ADR-004 / `POST /datasets/{id}/promote`).
Ver [`docs/plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md`](./plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md).

## Status mínimos
- uploaded
- validating
- parsing
- processed
- failed

## Quotas (billing / armazenamento)

- O **POST de upload** (`/api/v1/uploads`) consulta o **BillingService** do Core: limite mensal de ficheiros **e** limite de armazenamento (`max_storage_mb` do plano), somando `size_bytes` dos registos de ingestão do tenant.
- Podem aplicar-se ainda limites por **utilizador** (`tenant_memberships.max_storage_mb`) e por **grupo de quota** (`tenant_quota_groups`), conforme configuração do tenant.
- O **worker** de parsing não cria novo ficheiro de upload; não duplica esta verificação na fila — a cota é garantida na aceitação do upload.
- O utilizador vê uso vs limites no contexto **`GET /api/v1/me/context`** (`storage` em `fourpro_contracts.billing`).
