# Agentes do Projeto

## 1. Planner
Responsável por transformar demandas em planos executáveis.
Nunca implementa direto sem antes:
- entender objetivo
- mapear impacto
- quebrar em subtarefas
- listar riscos
- definir critérios de aceite

Tarefas complexas com estágios/filas/retries: skill [`ai-workflow-designer`](../.cursor/skills/ai-workflow-designer/SKILL.md).

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

Pipelines complexos: skill [`ai-workflow-designer`](../.cursor/skills/ai-workflow-designer/SKILL.md) + [`create-ingestion-pipeline`](../.cursor/skills/create-ingestion-pipeline/SKILL.md).

## 5. Frontend Architect
Responsável por:
- arquitectura UI (Feature-First, Atomic Design)
- login, admin, workspace, upload UI, dashboards
- UX por tenant e indicação clara do tenant activo
- performance (lazy loading, code splitting, SSR quando necessário)
- componentes reutilizáveis (props tipadas, docs, exemplo, testes)
- design system e fronteira Server/Client (stack alvo React/Next — ver [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md) e [ADR-002](./adr/002-frontend-react-next.md))
- implementação actual em `apps/web` (Angular) até aceite da migração

Skills: `.cursor/skills/frontend-architect`, `create-angular-screen` (actual), `create-next-screen` (alvo).

## 5.1 Figma Design Specialist
Responsável por transformar requisitos e wireframes em **protótipos Figma** como sistema (nunca telas isoladas).

Skill: [`.cursor/skills/figma-design-specialist/SKILL.md`](../.cursor/skills/figma-design-specialist/SKILL.md).  
Agente Cursor: [`.cursor/agents/figma-design-specialist.md`](../.cursor/agents/figma-design-specialist.md).  
Checklist: [`docs/CHECKLISTS/figma-prototype-checklist.md`](./CHECKLISTS/figma-prototype-checklist.md).

Sempre entregar:
- fluxos completos
- componentes reutilizáveis
- Auto Layout, Constraints, Variants, Variables
- Prototype navegável
- Design Tokens alinhados a `--da-*` (`apps/web/src/styles.scss`)
- anotações de handoff para Angular

Coordenar com wireframes em `docs/wireframes/` e com a implementação Frontend — sem misturar regra de domínio no protótipo.

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
Checklist: [`docs/CHECKLISTS/ai-workflow-checklist.md`](./CHECKLISTS/ai-workflow-checklist.md).
Pipeline de ingestão: skill [`create-ingestion-pipeline`](../.cursor/skills/create-ingestion-pipeline/SKILL.md).
Planner / feature plan: skill [`create-feature-plan`](../.cursor/skills/create-feature-plan/SKILL.md).
