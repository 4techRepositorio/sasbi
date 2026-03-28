# Plano detalhado — TICKET-007 Metadata de ingestão

**Papéis:** Backend Core · QA  
**Status:** planejado  
**Ticket:** `tickets/TICKET-007-ingestion-metadata.md`  
**Resumo:** `PLANOS-POR-TICKET-002-010.md` § TICKET-007

## 1. Objetivo

Persistir cada upload como registo de ingestão com estados explícitos (`uploaded` → `validating` → `parsing` → `processed` | `failed`), mensagem amigável ao utilizador e log técnico separado, sempre com `tenant_id`.

## 2. Validação arquitetural

### 2.1 Escopo

| Incluído | Excluído |
|----------|----------|
| CRUD/listagem metadata | Execução do worker (TICKET-008) |
| API detalhe por `ingestion_id` | Versionamento avançado de schema |

### 2.2 Decisões

1. Transições de estado em serviço único (`IngestionService`) para evitar estados impossíveis.
2. Campos: `original_filename`, `size_bytes`, `status`, `friendly_error`, `technical_log` ou JSON, timestamps.
3. Upload (006) cria registo `uploaded` e dispara validação assíncrona ou síncrona mínima conforme desenho atual.

## 3. Modelo de dados (rascunho)

```text
ingestions
  id UUID PK
  tenant_id FK → tenants NOT NULL
  original_filename VARCHAR
  size_bytes BIGINT
  status VARCHAR NOT NULL
  storage_path VARCHAR
  friendly_error TEXT NULL
  result_summary TEXT NULL
  created_at, updated_at TIMESTAMPTZ
```

## 4. Subtarefas

1. Migration + repository com scope tenant.
2. Serviço de transição de estado + enums.
3. `GET /ingestions`, `GET /ingestions/{id}`.
4. Integração com fluxo de upload.
5. Testes: isolamento tenant; transições válidas/inválidas.

## 5. QA — critérios de aceite

- [ ] Todo upload gera registo ingestão.
- [ ] Estados documentados em `docs/` ou OpenAPI.
- [ ] Falha sempre com `failed` + razão persistida.

## 6. Security

- [ ] `ingestion_id` de outro tenant → 404.

## 7. Riscos

| Risco | Mitigação |
|-------|-----------|
| Race entre API e worker | Locks otimistas ou fila única |

## 8. Dependências

TICKET-006.

## 9. Próximo ticket

TICKET-008 (worker + parsing).
