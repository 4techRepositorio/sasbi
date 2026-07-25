# Agentes do Projeto

Definições Cursor (subagentes invocáveis): [`.cursor/agents/README.md`](../.cursor/agents/README.md).  
Orquestração fase base: [`plans/ORQUESTRACAO-CHATS-AGENTES.md`](./plans/ORQUESTRACAO-CHATS-AGENTES.md) · Fase 4 BI: [`plans/PARALELA-BI-FRENTES.md`](./plans/PARALELA-BI-FRENTES.md).

## 1. Planner (`/planner`)
Responsável por transformar demandas em planos executáveis.
Nunca implementa direto sem antes:
- entender objetivo
- mapear impacto
- quebrar em subtarefas
- listar riscos
- definir critérios de aceite

## 2. Architect (`/architect`)
Responsável por:
- arquitetura
- contratos entre módulos
- boundaries
- convenções
- escalabilidade
- decisões técnicas
- mapa **Core vs Data** (quem expõe cada rota/domínio HTTP): ver [docs/ARCHITECTURE.md](./ARCHITECTURE.md) (secção *Backend Core vs Backend Data*).
Não deve implementar grandes features sem plano validado.

## 3. Backend Core (`/backend-core`)
Responsável por:
- auth
- tenants
- billing
- RBAC
- APIs administrativas
- integrações centrais
- cofre de credenciais (lado Core) para conectores

## 4. Backend Data (`/backend-data`)
Responsável por:
- upload
- parsing
- validação
- pipelines
- filas
- catálogos
- versionamento de datasets

## 5. Frontend (`/frontend`)
Responsável por:
- login
- admin
- workspace
- upload UI
- dashboards
- UX por tenant

## 6. QA Reviewer (`/qa-reviewer`)
Responsável por:
- testes unitários
- integração
- smoke
- regressão
- checklist de aceite

## 7. Security Reviewer (`/security-reviewer`)
Responsável por:
- MFA
- recuperação de senha
- segredos
- controle de sessão
- rate limiting
- isolamento tenant
- revisão de riscos (incl. vault, SSRF de conectores, tokens Desktop)

## 8. Coordenador (`/coordenador`)
Responsável por:
- gates e ondas de paralelismo
- fila Alembic / `main.py`
- apontar o agente certo sem implementar produto

## 9. Connectors (`/connectors`) — Fase 4
Responsável por:
- SPI `packages/connectors`
- data sources + sync (TICKET-015)
- plugins file / SQL / REST

## 10. Semantic / BI Web (`/semantic-bi`) — Fase 4
Responsável por:
- modelo semântico e API de query (TICKET-016)
- ligação a dashboards Web (TICKET-011)

## 11. Desktop (`/desktop`) — Fase 4
Responsável por:
- app `apps/desktop` (TICKET-017)
- autoração e publish para o tenant
