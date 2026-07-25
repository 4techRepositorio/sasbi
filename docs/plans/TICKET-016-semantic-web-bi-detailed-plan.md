# Plano detalhado — TICKET-016 Semântica e BI Web

**Papéis:** Architect · Backend Data · Frontend · Security · QA  
**Status:** planejado  
**Ticket:** `tickets/TICKET-016-semantic-web-bi.md`  
**ADR:** `docs/adr/001-bi-platform-connectors-desktop-web.md`  
**Coordena com:** TICKET-011

## 1. Objetivo

Definir modelo semântico mínimo por tenant, API de agregação segura e integração com o workspace Web para dashboards nativos 4Pro_BI.

## 2. Regras de negócio

1. Todo objecto semântico e resultado de query filtra por `tenant_id` do principal.
2. Utilizador só consulta datasets do catálogo do seu tenant (e papéis RBAC).
3. MVP: agregações `count`, `sum`, `avg`, `min`, `max` + `group_by` em colunas allowlisted do schema do dataset.
4. Sem SQL arbitrário do browser; o backend compõe a query.
5. Limites de linhas/tempo por plano (billing).
6. UI sem marcas de motores OSS; erros genéricos ao utilizador.

## 3. Impacto técnico

| Área | Mudança |
|------|---------|
| **contracts** | `semantic.py` — SemanticModel, QueryRequest/Response |
| **API** | `/api/v1/semantic/...`, `/api/v1/query` |
| **storage** | Metadados semânticos; dados em tabelas analíticas ou JSON processado (ADR com 012) |
| **web** | Página Fontes de dados; widgets TICKET-011 usam query API |
| **acelerador** | Se Cube/equivalente: só BFF + guest token (ARCHITECTURE § Aceleradores) |

## 4. Decisão com TICKET-011

Confirmar **híbrido**: canvas Angular consome `/query`; motor embed avançado só se ADR-011 o exigir, sempre atrás do proxy 4Pro_BI.

## 5. Subtarefas

1. Schema semântico mínimo (YAML/JSON por dataset) + migrations.
2. Query service com allowlist de colunas + testes tenant.
3. Endpoint query + rate limit.
4. UI Fontes de dados (lista sync do 015) + binding widgets.
5. Documentar em ARCHITECTURE + wireframe validation.
6. Checklist frontend/backend/qa.

## 6. Critérios de aceite

- [ ] Cross-tenant query impossível (teste automatizado).
- [ ] Consumer read-only não altera modelo semântico.
- [ ] Dashboard Web mostra KPI a partir de dataset processado.
- [ ] Dataset falhado/indisponível → placeholder (wireframe D5).
- [ ] Contratos com nota de impacto.

## 7. Riscos

| Risco | Mitigação |
|-------|-----------|
| Full scan caro | Limites, amostragem, índices, cache Redis |
| Duplicar TICKET-011 | Um único modelo de dashboard; 016 só alimenta dados |

## 8. Dependências

009, 011, 015; 005; 012 para camadas se query ler silver/gold.
