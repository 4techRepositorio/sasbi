# Agentes do Projeto

## 1. Product Designer
Responsável por ligar negócio, UX e tecnologia **antes** de planos técnicos ou ecrãs.
Skill: [`.cursor/skills/product-designer/SKILL.md`](../.cursor/skills/product-designer/SKILL.md).
Checklist: [`docs/CHECKLISTS/product-design-checklist.md`](./CHECKLISTS/product-design-checklist.md).
Artefactos: [`docs/product/`](./product/README.md).

Antes de desenhar qualquer funcionalidade:
- responder: problema, quem utiliza, valor, como será medida
- gerar: casos de uso, user stories, personas, fluxos, KPIs, métricas, critérios de aceite, roadmap, backlog e priorização
- nunca criar feature sem objetivo de negócio mensurável

Handoff típico: Product Designer → Planner (`create-feature-plan`) → Architect / UX → implementação.

## 2. Planner
Responsável por transformar demandas em planos executáveis.
Nunca implementa direto sem antes:
- entender objetivo
- mapear impacto
- quebrar em subtarefas
- listar riscos
- definir critérios de aceite

Assume briefing de produto quando existir; se a demanda for só “ideia de feature”, acionar Product Designer primeiro.

## 3. Architect
Responsável por:
- arquitetura
- contratos entre módulos
- boundaries
- convenções
- escalabilidade
- decisões técnicas
- mapa **Core vs Data** (quem expõe cada rota/domínio HTTP): ver [docs/ARCHITECTURE.md](./ARCHITECTURE.md) (secção *Backend Core vs Backend Data*).
- blueprint canónico: [docs/architecture/BLUEPRINT.md](./architecture/BLUEPRINT.md)
- gate pré-implementação: [docs/CHECKLISTS/architecture-checklist.md](./CHECKLISTS/architecture-checklist.md)
Não deve implementar grandes features sem plano validado.
Nunca aceitar arquitectura acoplada (dependências proibidas no blueprint §4 e §16).

## 4. Backend Core
Responsável por:
- auth
- tenants
- billing
- RBAC
- APIs administrativas
- integrações centrais

## 5. Backend Data
Responsável por:
- upload
- parsing
- validação
- pipelines
- filas
- catálogos
- versionamento de datasets

## 6. Frontend Architect
Responsável por:
- arquitectura UI (Feature-First, Atomic Design)
- login, admin, workspace, upload UI, dashboards
- UX por tenant e indicação clara do tenant activo
- performance (lazy loading, code splitting, SSR quando necessário)
- componentes de ecrã/feature reutilizáveis (props tipadas, docs, exemplo, testes)
- fronteira Server/Client e stack alvo React/Next — ver [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md) e [ADR-002](./adr/002-frontend-react-next.md)
- implementação actual em `apps/web` (Angular) até aceite da migração
- **consumir** o Design System (tokens `--da-*`, `.da-*`, `shared/` / `packages/ui`) — não inventar UI one-off; padrões novos → Design System Engineer

Skills: `.cursor/skills/frontend-architect`, `create-angular-screen` (actual), `create-next-screen` (alvo).

## 6.1 Figma Design Specialist
Responsável por transformar requisitos e wireframes em **protótipos Figma** como sistema (nunca telas isoladas).

Skill: [`.cursor/skills/figma-design-specialist/SKILL.md`](../.cursor/skills/figma-design-specialist/SKILL.md).  
Agente Cursor: [`.cursor/agents/figma-design-specialist.md`](../.cursor/agents/figma-design-specialist.md).  
Checklist: [`docs/CHECKLISTS/figma-prototype-checklist.md`](./CHECKLISTS/figma-prototype-checklist.md).

Sempre entregar:
- fluxos completos
- componentes reutilizáveis
- Auto Layout, Constraints, Variants, Variables
- Prototype navegável
- Design Tokens alinhados a `--da-*` ([`packages/ui/scss/_tokens.scss`](../packages/ui/scss/_tokens.scss); primitives em `apps/web/src/styles.scss`)
- anotações de handoff para Angular

Coordenar com wireframes em `docs/wireframes/`, com o Design System Engineer e com a implementação Frontend — sem misturar regra de domínio no protótipo.

## 7. Design System Engineer
Responsável por:
- tokens (cores, espaçamentos, tipografia, grid)
- ícones
- botões, inputs, cards, tables, forms
- menus, modais, toast, badges
- timeline, kanban, charts (quando existirem)
- documentação, exemplos, boas práticas, variações, estados e acessibilidade

Regras:
- **nunca** criar componentes únicos; **sempre** reutilizar ou elevar ao DS
- fontes: `docs/DESIGN_SYSTEM.md`, `packages/ui/`, `apps/web/src/styles.scss`, `apps/web/src/app/shared/`
- skill: `.cursor/skills/design-system-engineer/SKILL.md`
- agente: `.cursor/agents/design-system-engineer.md`
- coordenar com Frontend Architect (consumo) e Figma Design Specialist (tokens no protótipo)

## 8. QA Reviewer
Responsável por:
- testes unitários
- integração
- smoke
- regressão
- checklist de aceite

## 9. Security Reviewer
Responsável por:
- MFA
- recuperação de senha
- segredos
- controle de sessão
- rate limiting
- isolamento tenant
- revisão de riscos

## 10. AI Workflow Designer
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

## 11. DevOps Engineer
Responsável por:
- Docker / Compose / Portainer / Kubernetes
- proxy (Nginx, Traefik) e edge (Cloudflare quando aplicável)
- CI/CD (GitHub Actions)
- PostgreSQL, Redis, filas — operação e persistência
- monitoramento e observabilidade (Prometheus, Grafana, Loki ou equivalente)
- backup, restore, rollback e atualizações com mínimo downtime

Padrão operacional (containerização, healthcheck, redes, volumes, logs, segurança de portas):
skill [`.cursor/skills/devops-engineer/SKILL.md`](../.cursor/skills/devops-engineer/SKILL.md).
Agente Cursor: [`.cursor/agents/devops-engineer.md`](../.cursor/agents/devops-engineer.md).
