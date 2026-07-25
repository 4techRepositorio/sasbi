# Plano detalhado — TICKET-015 Framework de conectores

**Papéis:** Architect · Backend Data · Backend Core · Security · QA  
**Status:** planejado  
**Ticket:** `tickets/TICKET-015-connector-framework.md`  
**ADR:** `docs/adr/001-bi-platform-connectors-desktop-web.md`

## 1. Objetivo

Introduzir SPI de conectores, persistência de fontes por tenant, cofre de credenciais e jobs de extract, com conectores O1 (`postgres`, `rest_json`) e adaptação do upload actual ao conector `file`.

## 2. Regras de negócio

1. Toda fonte (`data_source`) tem `tenant_id` do principal autenticado.
2. Segredos nunca voltam em GET de listagem/detalhe (apenas máscaras / `has_secret`).
3. `test_connection` e `sync` exigem membership + papel mínimo (analyst/admin — alinhar TICKET-005).
4. Sync cria ou actualiza ingestão no ciclo de status existente; falhas gravam log técnico + mensagem amigável.
5. Billing pode recusar nova fonte se o plano esgotar `max_data_sources` (campo novo ou stub documentado).
6. Egress de plugins: apenas hosts/ports allowlisted na config do conector (validação server-side).

## 3. Impacto técnico

| Área | Mudança |
|------|---------|
| **contracts** | `fourpro_contracts.connectors` — tipos de conector, config schemas, DTOs fonte/job |
| **packages/connectors** | SPI Python + implementações `file`, `postgres`, `rest_json` |
| **API** | routers/services/repos; migrações `data__` + `core__` vault |
| **worker** | task `sync_data_source` invocando plugin |
| **segurança** | encriptação Fernet/KMS-ready; audit events |
| **billing** | limite opcional de fontes |
| **docs** | `INGESTION.md`, `ARCHITECTURE.md` |

## 4. Modelo de dados (mínimo)

- `data_sources`: id, tenant_id, name, connector_type, config_json (sem secrets), status, created_by, timestamps
- `connector_credentials`: id, tenant_id, data_source_id, secret_encrypted, key_version
- `data_source_sync_runs`: id, tenant_id, data_source_id, ingestion_id?, status, logs, timestamps

## 5. APIs sugeridas

| Método | Rota | Notas |
|--------|------|-------|
| GET | `/api/v1/connectors` | Catálogo de tipos + capabilities |
| GET/POST | `/api/v1/data-sources` | List/create |
| GET/PATCH/DELETE | `/api/v1/data-sources/{id}` | Tenant-scoped |
| POST | `/api/v1/data-sources/{id}/test` | test_connection |
| POST | `/api/v1/data-sources/{id}/sync` | enqueue |
| GET | `/api/v1/data-sources/{id}/sync-runs` | histórico |

## 6. Subtarefas

1. ADR já aceite; fechar JSON Schema config O1.
2. Pacote `packages/connectors` + testes unitários SPI.
3. Migrações + credential service (Core).
4. APIs + serviços + repositórios com filtro tenant.
5. Worker task + integração pipeline ingestão.
6. Adaptar `file` (compatibilidade com `POST /uploads`).
7. Implementar `postgres` e `rest_json`.
8. UI mínima opcional (pode ficar no 016): senão API-only neste ticket.
9. Checklists data/security + CHANGELOG.

## 7. Critérios de aceite

- [ ] Isolamento tenant em todas as rotas e jobs.
- [ ] Secret nunca em response body de list/get.
- [ ] Sync Postgres de tabela pequena → dataset `processed` no catálogo.
- [ ] REST JSON com paginação simples → mesmo fluxo.
- [ ] Upload ficheiro regressão verde.
- [ ] Testes mínimos pytest + um teste de negação cross-tenant.

## 8. Riscos

| Risco | Mitigação |
|-------|-----------|
| SQL injection via config | Query parametrizada; deny raw SQL do cliente no MVP |
| SSRF no REST | Allowlist URL; bloqueio de IPs privados salvo config admin |
| SPI instável | Versionar `connector_api_version` |

## 9. Dependências

004–010; coordenação F1 em contratos antes de merge API.
