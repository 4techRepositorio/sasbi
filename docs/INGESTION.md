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

## Fontes de dados (conectores)

Além de `POST /api/v1/uploads`, a aquisição pode vir de uma **fonte** (`data_sources`):

1. `GET /api/v1/connectors` — catálogo de tipos (`file`, `postgres`, `mysql`, `sqlserver`, `rest_json`, `s3_compatible`).
2. CRUD em `/api/v1/data-sources` — config sem segredos; `secret` só em create/patch (nunca em GET).
3. `POST .../test`, `.../discover`, `.../sample-schema`, `.../sync`.
4. Worker `fourpro.sync_data_source`: extract → ficheiro em stage → `FileIngestion` → mesmo pipeline de parse.

Credenciais: tabela `connector_credentials` (Fernet; `CREDENTIALS_FERNET_KEY` ou derivação de `JWT_SECRET` só em dev).

**Billing:** `BillingService.ensure_data_source_allowed` exige plano activo; limite `max_data_sources` no plano é stub até migração futura.

SPI interno: `packages/connectors` (ver README do pacote).

Hoje a aquisição em produção combina **upload de ficheiro** e **sync de conector** no mesmo ciclo de status — ver
[`docs/plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md`](./plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md).

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
