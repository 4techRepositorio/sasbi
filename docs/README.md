# Documentação 4Pro_BI — índice

## Visão geral

| Área | Conteúdo |
|------|----------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Blocos do sistema, multitenancy, integração de aceleradores OSS, experiência unificada |
| [VISION.md](./VISION.md) | Produto |
| [ROADMAP.md](./ROADMAP.md) | Fases e ligação a tickets |
| [SECURITY.md](./SECURITY.md) | Política de segurança: reporte, divulgação responsável e controlos na implementação |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Contribuição, gates locais, Dependabot, troubleshooting npm |
| [SECURITY.md (raiz)](../SECURITY.md) | Entrada GitHub *Security policy* → remete a `docs/SECURITY.md` |
| [TENANCY.md](./TENANCY.md) | Modelo multitenant |
| [INGESTION.md](./INGESTION.md) | Pipeline de ficheiros |
| [BILLING.md](./BILLING.md) | Planos e limites |
| [BACKLOG.md](./BACKLOG.md) | Ideias não comprometidas |
| [AGENTS.md](./AGENTS.md) | Uso de agentes / planeamento |

## Execução e tickets

| Área | Conteúdo |
|------|----------|
| [plans/README.md](./plans/README.md) | Plano mestre, resumos por ticket, planos detalhados TICKET-000–014 |
| [plans/EXECUCAO-MESTRE.md](./plans/EXECUCAO-MESTRE.md) | Ordem de trabalho, **execução paralela** (§0), marcos A–E |
| [plans/PARALELA-5-FRENTES.md](./plans/PARALELA-5-FRENTES.md) | 5 frentes paralelas, agentes e prompts (projeto 4Pro_BI) |
| [plans/ORQUESTRACAO-CHATS-AGENTES.md](./plans/ORQUESTRACAO-CHATS-AGENTES.md) | **Orquestração** — vários chats Cursor / worktrees, allowlists, rituais |
| [plans/PROMPTS-CHATS-CURSOR.md](./plans/PROMPTS-CHATS-CURSOR.md) | **Prompts prontos** para colar em cada chat (C0–C6) |
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
| [CHECKLISTS/backend-checklist.md](./CHECKLISTS/backend-checklist.md) | Entrega API |
| [CHECKLISTS/frontend-checklist.md](./CHECKLISTS/frontend-checklist.md) | Entrega Angular |
| [CHECKLISTS/data-checklist.md](./CHECKLISTS/data-checklist.md) | Dados / ingestão |
| [CHECKLISTS/qa-checklist.md](./CHECKLISTS/qa-checklist.md) | QA |

## E2E e CI (referência rápida)

| Ficheiro | Uso |
|----------|-----|
| [`../e2e/README.md`](../e2e/README.md) | Playwright, scripts `run-e2e-*`, variáveis `.env.e2e` |
| [`.github/workflows/README.md`](../.github/workflows/README.md) | Índice dos workflows (CI, E2E manual, reusable smoke API) |

## Ordem de leitura sugerida (nova equipa)

1. `VISION.md` → `ARCHITECTURE.md` → `plans/EXECUCAO-MESTRE.md`  
2. `plans/README.md` + ticket atual em `tickets/`  
3. Wireframes da área em construção  
4. `assets/README.md` se a entrega envolver diagramas ou evidências visuais
