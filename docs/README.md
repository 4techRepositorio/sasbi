# Documentação 4Pro_BI — índice

## Visão geral

| Área | Conteúdo |
|------|----------|
| [architecture/BLUEPRINT.md](./architecture/BLUEPRINT.md) | **Blueprint Architect** — pastas, bounded contexts, portas, eventos, filas, APIs, versionamento, trade-offs |
| [architecture/README.md](./architecture/README.md) | Índice do pacote de arquitectura |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Blocos do sistema, multitenancy, integração de aceleradores OSS, experiência unificada |
| [adr/002-modular-monolith-clean-architecture.md](./adr/002-modular-monolith-clean-architecture.md) | ADR modular monolith + Clean Architecture + Celery (**colisão de número 002** — ver nota no PR) |
| [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md) | Frontend Architect: Feature-First, Atomic Design, stack alvo React/Next |
| [adr/002-frontend-react-next.md](./adr/002-frontend-react-next.md) | ADR stack frontend alvo React + Next.js (proposto; **colisão de número 002**) |
| [VISION.md](./VISION.md) | Produto |
| [product/README.md](./product/README.md) | Briefings Product Designer (problema, valor, KPIs) |
| [ROADMAP.md](./ROADMAP.md) | Fases e ligação a tickets |
| [adr/001-bi-platform-connectors-desktop-web.md](./adr/001-bi-platform-connectors-desktop-web.md) | ADR-001: conectores + Web + Desktop |
| [plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md](./plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md) | Plano mestre plataforma BI |
| [SECURITY.md](./SECURITY.md) | Política de segurança: reporte, divulgação responsável e controlos na implementação |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Contribuição, gates locais, Dependabot, troubleshooting npm |
| [SECURITY.md (raiz)](../SECURITY.md) | Entrada GitHub *Security policy* → remete a `docs/SECURITY.md` |
| [TENANCY.md](./TENANCY.md) | Modelo multitenant |
| [INGESTION.md](./INGESTION.md) | Pipeline de ficheiros |
| [BILLING.md](./BILLING.md) | Planos e limites |
| [BACKLOG.md](./BACKLOG.md) | Ideias não comprometidas |
| [AGENTS.md](./AGENTS.md) | Uso de agentes / planeamento (incl. Multi-Agent Systems Architect, AI Workflow Designer) |
| [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md) | Design System — tokens, primitives, a11y, reuso |

## Execução e tickets

| Área | Conteúdo |
|------|----------|
| [plans/README.md](./plans/README.md) | Plano mestre, resumos por ticket, planos detalhados TICKET-000–017 |
| [plans/EXECUCAO-MESTRE.md](./plans/EXECUCAO-MESTRE.md) | Ordem de trabalho, **execução paralela** (§0), marcos A–E |
| [plans/PARALELA-5-FRENTES.md](./plans/PARALELA-5-FRENTES.md) | 5 frentes paralelas, agentes e prompts (projeto 4Pro_BI) |
| [plans/ORQUESTRACAO-CHATS-AGENTES.md](./plans/ORQUESTRACAO-CHATS-AGENTES.md) | **Orquestração** — vários chats Cursor / worktrees, allowlists, rituais |
| [plans/PROMPTS-CHATS-CURSOR.md](./plans/PROMPTS-CHATS-CURSOR.md) | **Prompts prontos** para colar em cada chat (C0–C7) |
| [`../tickets/`](../tickets/README.md) | Cartões curtos por ticket |

## UX e validação

| Área | Conteúdo |
|------|----------|
| [wireframes/README.md](./wireframes/README.md) | Critérios de validação antes do píxel-perfect |
| [wireframes/REFERENCIAS-MATERIAIS-LEGADOS.md](./wireframes/REFERENCIAS-MATERIAIS-LEGADOS.md) | PDF, protótipo, planos históricos |
| [e2e/README.md](../e2e/README.md) § capturas wireframe | `E2E_WIREFRAME_CAPTURES=1` → PNG em `docs/assets/wireframes/exports/` |

## Imagens, diagramas e artefactos visuais

**Onde e como são gerados:** [assets/README.md](./assets/README.md) (diagramas Mermaid, exports de wireframe, capturas, exports do produto, imagens Docker).

## Checklists

| Ficheiro | Uso |
|----------|-----|
| [CHECKLISTS/feature-definition-of-done.md](./CHECKLISTS/feature-definition-of-done.md) | DoD por feature |
| [CHECKLISTS/architecture-checklist.md](./CHECKLISTS/architecture-checklist.md) | Gate Architect antes de implementar |
| [CHECKLISTS/product-design-checklist.md](./CHECKLISTS/product-design-checklist.md) | Briefing de produto (antes do plano técnico) |
| [CHECKLISTS/backend-checklist.md](./CHECKLISTS/backend-checklist.md) | Entrega API |
| [CHECKLISTS/frontend-checklist.md](./CHECKLISTS/frontend-checklist.md) | Entrega frontend (Angular actual + critérios Architect) |
| [CHECKLISTS/design-system-checklist.md](./CHECKLISTS/design-system-checklist.md) | Tokens, primitives, a11y |
| [CHECKLISTS/data-checklist.md](./CHECKLISTS/data-checklist.md) | Dados / ingestão |
| [CHECKLISTS/qa-checklist.md](./CHECKLISTS/qa-checklist.md) | QA |
| [CHECKLISTS/ai-workflow-checklist.md](./CHECKLISTS/ai-workflow-checklist.md) | Pipelines inteligentes (7 estágios + bounds) |

## E2E e CI (referência rápida)

| Ficheiro | Uso |
|----------|-----|
| [`../e2e/README.md`](../e2e/README.md) | Playwright, scripts `run-e2e-*`, variáveis `.env.e2e` |
| [`.github/workflows/README.md`](../.github/workflows/README.md) | Índice dos workflows (CI, E2E manual, reusable smoke API) |

## Ordem de leitura sugerida (nova equipa)

1. `VISION.md` → `product/` (briefings) → `architecture/BLUEPRINT.md` → `ARCHITECTURE.md` → `plans/EXECUCAO-MESTRE.md`  
2. `plans/README.md` + ticket atual em `tickets/`  
3. Wireframes da área em construção  
4. `assets/README.md` se a entrega envolver diagramas ou evidências visuais  
5. Features estruturais: preencher `CHECKLISTS/architecture-checklist.md`
