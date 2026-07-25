# Documentação 4Pro_BI — índice

Toda documentação técnica deve responder: **o que faz**, **como funciona**, **como instalar**, **como configurar**, **como testar**, **como evoluir**. Política: [DOCUMENTATION.md](./DOCUMENTATION.md) · [ADR-002](./adr/002-documentation-standards.md).

## Guias canónicos

| Área | Conteúdo |
|------|----------|
| [INSTALLATION.md](./INSTALLATION.md) | Instalação local |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Deploy Compose / Portainer |
| [DEVELOPMENT.md](./DEVELOPMENT.md) | Desenvolvimento, testes, ownership |
| [DOCUMENTATION.md](./DOCUMENTATION.md) | Mapa e política de docs |

## Visão e arquitectura

| Área | Conteúdo |
|------|----------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Blocos, multitenancy, aceleradores OSS |
| [VISION.md](./VISION.md) | Produto |
| [ROADMAP.md](./ROADMAP.md) | Fases e tickets |
| [SECURITY.md](./SECURITY.md) | Política de segurança |
| [TENANCY.md](./TENANCY.md) | Modelo multitenant |
| [INGESTION.md](./INGESTION.md) | Pipeline de ficheiros |
| [BILLING.md](./BILLING.md) | Planos e limites |
| [BACKLOG.md](./BACKLOG.md) | Ideias não comprometidas |
| [AGENTS.md](./AGENTS.md) | Papéis de agentes |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Contribuição e gates |
| [SECURITY.md (raiz)](../SECURITY.md) | Atalho GitHub Security policy |
| [CHANGELOG.md](../CHANGELOG.md) | Histórico de alterações |

## API — OpenAPI / Swagger / Exemplos

| Área | Conteúdo |
|------|----------|
| [openapi/README.md](./openapi/README.md) | Swagger UI, ReDoc, snapshot |
| [openapi/openapi.json](./openapi/openapi.json) | Schema OpenAPI 3 (Git) |
| [examples/README.md](./examples/README.md) | Scripts cURL (auth, upload) |

Runtime (API no ar): `/docs` · `/redoc` · `/openapi.json`. Regenerar: `./scripts/export-openapi.sh`.

## Diagramas (Mermaid / UML)

| Área | Conteúdo |
|------|----------|
| [diagrams/README.md](./diagrams/README.md) | Índice |
| [diagrams/system-context.md](./diagrams/system-context.md) | Contexto do sistema |
| [diagrams/auth-sequence.md](./diagrams/auth-sequence.md) | Sequência auth |
| [diagrams/ingestion-flow.md](./diagrams/ingestion-flow.md) | Fluxo / estados ingestão |
| [diagrams/uml-components.md](./diagrams/uml-components.md) | UML componentes |
| [diagrams/uml-class-core.md](./diagrams/uml-class-core.md) | UML classes |
| [assets/README.md](./assets/README.md) | Exports PNG/SVG opcionais |

## ADRs

| Área | Conteúdo |
|------|----------|
| [adr/README.md](./adr/README.md) | Índice de ADRs |
| [adr/000-contract-slices.md](./adr/000-contract-slices.md) | Fatias de contratos |
| [adr/001-bi-platform-connectors-desktop-web.md](./adr/001-bi-platform-connectors-desktop-web.md) | Conectores + Web + Desktop |
| [adr/002-documentation-standards.md](./adr/002-documentation-standards.md) | Padrões de documentação |

## Execução e tickets

| Área | Conteúdo |
|------|----------|
| [plans/README.md](./plans/README.md) | Plano mestre e tickets detalhados 000–017 |
| [plans/EXECUCAO-MESTRE.md](./plans/EXECUCAO-MESTRE.md) | Ordem e paralelismo |
| [plans/PARALELA-5-FRENTES.md](./plans/PARALELA-5-FRENTES.md) | 5 frentes paralelas |
| [plans/ORQUESTRACAO-CHATS-AGENTES.md](./plans/ORQUESTRACAO-CHATS-AGENTES.md) | Orquestração de chats |
| [plans/PROMPTS-CHATS-CURSOR.md](./plans/PROMPTS-CHATS-CURSOR.md) | Prompts prontos |
| [plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md](./plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md) | Plano mestre BI |
| [`../tickets/`](../tickets/README.md) | Cartões curtos (incl. TICKET-018 docs) |

## UX e validação

| Área | Conteúdo |
|------|----------|
| [wireframes/README.md](./wireframes/README.md) | Critérios de validação |
| [wireframes/REFERENCIAS-MATERIAIS-LEGADOS.md](./wireframes/REFERENCIAS-MATERIAIS-LEGADOS.md) | Materiais legados |
| [e2e/README.md](../e2e/README.md) | Playwright; capturas wireframe |

## Checklists

| Ficheiro | Uso |
|----------|-----|
| [CHECKLISTS/documentation-checklist.md](./CHECKLISTS/documentation-checklist.md) | Docs obrigatórias |
| [CHECKLISTS/feature-definition-of-done.md](./CHECKLISTS/feature-definition-of-done.md) | DoD por feature |
| [CHECKLISTS/backend-checklist.md](./CHECKLISTS/backend-checklist.md) | Entrega API |
| [CHECKLISTS/frontend-checklist.md](./CHECKLISTS/frontend-checklist.md) | Entrega Angular |
| [CHECKLISTS/data-checklist.md](./CHECKLISTS/data-checklist.md) | Dados / ingestão |
| [CHECKLISTS/qa-checklist.md](./CHECKLISTS/qa-checklist.md) | QA |

## E2E e CI

| Ficheiro | Uso |
|----------|-----|
| [`../e2e/README.md`](../e2e/README.md) | Scripts e `.env.e2e` |
| [`.github/workflows/README.md`](../.github/workflows/README.md) | Workflows CI/E2E |

## Ordem de leitura sugerida (nova equipa)

1. `VISION.md` → `ARCHITECTURE.md` → `INSTALLATION.md` → `DEVELOPMENT.md`  
2. `openapi/README.md` + `examples/` (primeiro pedido HTTP)  
3. `diagrams/` (contexto, auth, ingestão)  
4. `plans/EXECUCAO-MESTRE.md` + ticket actual  
5. `DEPLOYMENT.md` antes do primeiro deploy
