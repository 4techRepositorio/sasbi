# Plano detalhado — TICKET-008 Pipeline de parsing (worker)

**Papéis:** Backend Worker · Backend Core · QA  
**Status:** planejado  
**Ticket:** `tickets/TICKET-008-parser-pipeline.md`  
**Resumo:** `PLANOS-POR-TICKET-002-010.md` § TICKET-008

## 1. Objetivo

Processar ingestões de forma assíncrona (Redis + Celery ou equivalente): consumir por `ingestion_id`, atualizar estados, aplicar parsers por extensão, gravar resultado ou `failed` com motivo técnico, permitir reprocessamento básico.

## 2. Validação arquitetural

### 2.1 Escopo

| Incluído | Excluído |
|----------|----------|
| Task principal parse | dbt / camadas medalha (roadmap Marco B) |
| Retry policy mínima + dead-letter visível | Auto-scaling workers |

### 2.2 Decisões

1. Worker lê ficheiro do storage pelo path da ingestão; valida `tenant_id` no registo.
2. Parsers em `packages/shared` ou módulo dedicado por formato.
3. Sucesso: estado `processed` + `result_summary` (ex.: linhas, colunas).
4. Falha: `failed` + log; nunca silêncio sem atualização de estado.

## 3. Subtarefas

1. Configurar fila e worker image no Compose.
2. Task `parse_ingestion(ingestion_id)` com idempotência básica.
3. Handlers por extensão; fallback erro claro para não suportado.
4. API opcional “reprocessar” (admin) ou flag interna — documentar.
5. Testes: fixture pequeno por formato; tenant isolation.

## 4. QA — critérios de aceite

- [ ] Ficheiro válido sobe o estado até `processed`.
- [ ] Ficheiro inválido → `failed` com mensagem técnica armazenada.
- [ ] Worker restart não corrompe estado (regra documentada).

## 5. Security

- [ ] Worker não aceita `tenant_id` externo sem cruzar com registo DB.

## 6. Riscos

| Risco | Mitigação |
|-------|-----------|
| OOM em ficheiros grandes | Limites de tamanho; streaming quando possível |

## 7. Dependências

TICKET-007.

## 8. Próximo ticket

TICKET-009 (catálogo expõe apenas `processed`).
