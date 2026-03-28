# Plano detalhado — TICKET-009 Catálogo de datasets

**Papéis:** Backend Core · Frontend · QA  
**Status:** planejado  
**Ticket:** `tickets/TICKET-009-dataset-catalog.md`  
**Resumo:** `PLANOS-POR-TICKET-002-010.md` § TICKET-009

## 1. Objetivo

Expor listagem paginada (e filtros mínimos) de datasets **processados** por tenant, com contrato estável (`packages/contracts` ou OpenAPI), e tela Angular alinhada aos wireframes de catálogo.

## 2. Validação arquitetural

### 2.1 Escopo

| Incluído | Excluído |
|----------|----------|
| `GET /datasets` com paginação | Workspace analítico integrado (Fase 3) |
| DTOs versionados | Full-text search avançado |

### 2.2 Decisões

1. Apenas ingestões/datasets com `status = processed` entram no catálogo (view ou query dedicada).
2. Resposta: `items`, `total`, `limit`, `offset` (ou cursor — documentar).
3. Frontend: tabela com loading/erro/vazio/sucesso.

## 3. Subtarefas

1. Query repository com `tenant_id` obrigatório.
2. Router + schemas Pydantic espelhados em contracts TS se existir pacote.
3. Testes: dois tenants, listagens independentes.
4. Angular: serviço HTTP + página catálogo.
5. Atualizar wireframe validation se necessário.

## 4. QA — critérios de aceite

- [ ] Consumer/analyst vê apenas dados do seu tenant.
- [ ] Paginação correta com `total` consistente.
- [ ] Checklist frontend.

## 5. Security

- [ ] Nenhum dataset sem filtro tenant.

## 6. Riscos

| Risco | Mitigação |
|-------|-----------|
| Leak por join errado | Review + teste regressão |

## 7. Dependências

TICKET-008 (datasets processados existem).

## 8. Próximo ticket

TICKET-010 (billing / quotas) e roadmap workspace (Marco C).
