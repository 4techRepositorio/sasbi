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

## 8. AI Workflow Designer
Responsável por:
- transformar tarefas complexas em pipelines
- estágios: Entrada, Validação, Planejamento, Execução, Verificação, Correção, Entrega
- avaliação: Dependências, Paralelismo, Cache, Memória, Persistência, Retries, Fallback, Métricas
- bounds explícitos (sem loops infinitos) — `max_attempts`, deadline, DLQ/`failed`
- alinhamento de workflows de produto (ingestão/worker) e de orquestração de chats

Padrão operacional:
skill [`.cursor/skills/ai-workflow-designer/SKILL.md`](../.cursor/skills/ai-workflow-designer/SKILL.md).
Agente Cursor: [`.cursor/agents/ai-workflow-designer.md`](../.cursor/agents/ai-workflow-designer.md).
Pipeline de ingestão: skill [`create-ingestion-pipeline`](../.cursor/skills/create-ingestion-pipeline/SKILL.md).
