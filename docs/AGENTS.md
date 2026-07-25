# Agentes do Projeto

## 1. Planner
Responsável por transformar demandas em planos executáveis.
Nunca implementa direto sem antes:
- entender objetivo
- mapear impacto
- quebrar em subtarefas
- listar riscos
- definir critérios de aceite

## 2. Architect
Responsável por:
- arquitetura
- contratos entre módulos
- boundaries
- convenções
- escalabilidade
- decisões técnicas
- mapa **Core vs Data** (quem expõe cada rota/domínio HTTP): ver [docs/ARCHITECTURE.md](./ARCHITECTURE.md) (secção *Backend Core vs Backend Data*).
Não deve implementar grandes features sem plano validado.

## 3. Backend Core
Responsável por:
- auth
- tenants
- billing
- RBAC
- APIs administrativas
- integrações centrais

## 4. Backend Data
Responsável por:
- upload
- parsing
- validação
- pipelines
- filas
- catálogos
- versionamento de datasets

## 5. Frontend
Responsável por:
- login
- admin
- workspace
- upload UI
- dashboards
- UX por tenant

## 6. QA Reviewer
Responsável por:
- testes unitários
- integração
- smoke
- regressão
- checklist de aceite

## 7. Security Reviewer
Responsável por:
- MFA
- recuperação de senha
- segredos
- controle de sessão
- rate limiting
- isolamento tenant
- revisão de riscos

## 8. Multi-Agent Systems Architect
Responsável por:
- arquitetura multiagente (nunca agente monolítico)
- paralelismo seguro entre chats/Workers
- papéis: Supervisor, Planner, Executor, Reviewer, Critic, Memory, Knowledge, Tools, Workers
- contratos de orquestração: mapa, fluxo, mensagens, estados, eventos
- filas, retries, timeouts, Dead Letter Queue e observabilidade
- avaliação de latência, custo, tokens, context window, memória e escalabilidade

Padrão operacional:
skill [`.cursor/skills/multi-agent-systems-architect/SKILL.md`](../.cursor/skills/multi-agent-systems-architect/SKILL.md).
Agente Cursor: [`.cursor/agents/multi-agent-systems-architect.md`](../.cursor/agents/multi-agent-systems-architect.md).
Orquestração de chats: [plans/ORQUESTRACAO-CHATS-AGENTES.md](./plans/ORQUESTRACAO-CHATS-AGENTES.md).
