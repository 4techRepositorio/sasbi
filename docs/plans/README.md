# Planos de execução (4Pro_BI)

Índice geral da documentação: [../README.md](../README.md). Imagens e diagramas: [../assets/README.md](../assets/README.md). **Trabalho em paralelo por toda a equipa:** ver secção **§0** em [EXECUCAO-MESTRE.md](./EXECUCAO-MESTRE.md).

| Documento | Descrição |
|-----------|-----------|
| [EXECUCAO-MESTRE.md](./EXECUCAO-MESTRE.md) | Fases, ordem dos tickets, critérios globais |
| [PLANOS-POR-TICKET-000-001.md](./PLANOS-POR-TICKET-000-001.md) | Resumo executável dos tickets 000–001 |
| [PLANOS-POR-TICKET-002-010.md](./PLANOS-POR-TICKET-002-010.md) | Resumo executável dos tickets 002–010 |
| [PLANOS-POR-TICKET-011-014.md](./PLANOS-POR-TICKET-011-014.md) | Resumo fases seguintes (Marcos B/C/E + CI, tickets 011–014) |
| [PLANOS-POR-TICKET-015-017.md](./PLANOS-POR-TICKET-015-017.md) | Resumo plataforma BI (conectores, semântica/Web, Desktop) |
| [PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md](./PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md) | **Plano mestre** BI: SPI de conectores + Web + Desktop |
| [PARALELA-5-FRENTES.md](./PARALELA-5-FRENTES.md) | **5 frentes paralelas**, agentes e prompts (gestão técnica 4Pro_BI) |
| [../wireframes/](../wireframes/) | Validação de wireframes e referências |
| [../adr/001-bi-platform-connectors-desktop-web.md](../adr/001-bi-platform-connectors-desktop-web.md) | ADR-001 plataforma BI |
| [../adr/005-frontend-react-next.md](../adr/005-frontend-react-next.md) | ADR-005 stack frontend React/Next (proposto) |
| [../FRONTEND_ARCHITECTURE.md](../FRONTEND_ARCHITECTURE.md) | Arquitectura frontend (Frontend Architect) |

## Planos detalhados por ticket

| Ticket | Plano detalhado |
|--------|-----------------|
| TICKET-000 | [TICKET-000-scaffold-monorepo-detailed-plan.md](./TICKET-000-scaffold-monorepo-detailed-plan.md) |
| TICKET-001 | [TICKET-001-auth-core-detailed-plan.md](./TICKET-001-auth-core-detailed-plan.md) |
| TICKET-002 | [TICKET-002-password-recovery-detailed-plan.md](./TICKET-002-password-recovery-detailed-plan.md) |
| TICKET-003 | [TICKET-003-mfa-email-detailed-plan.md](./TICKET-003-mfa-email-detailed-plan.md) |
| TICKET-004 | [TICKET-004-tenant-foundation-detailed-plan.md](./TICKET-004-tenant-foundation-detailed-plan.md) |
| TICKET-005 | [TICKET-005-rbac-detailed-plan.md](./TICKET-005-rbac-detailed-plan.md) |
| TICKET-006 | [TICKET-006-file-upload-detailed-plan.md](./TICKET-006-file-upload-detailed-plan.md) |
| TICKET-007 | [TICKET-007-ingestion-metadata-detailed-plan.md](./TICKET-007-ingestion-metadata-detailed-plan.md) |
| TICKET-008 | [TICKET-008-parser-pipeline-detailed-plan.md](./TICKET-008-parser-pipeline-detailed-plan.md) |
| TICKET-009 | [TICKET-009-dataset-catalog-detailed-plan.md](./TICKET-009-dataset-catalog-detailed-plan.md) |
| TICKET-010 | [TICKET-010-billing-core-detailed-plan.md](./TICKET-010-billing-core-detailed-plan.md) |
| TICKET-011 | [TICKET-011-workspace-dashboards-detailed-plan.md](./TICKET-011-workspace-dashboards-detailed-plan.md) |
| TICKET-012 | [TICKET-012-data-governance-detailed-plan.md](./TICKET-012-data-governance-detailed-plan.md) |
| TICKET-013 | [TICKET-013-observability-enterprise-detailed-plan.md](./TICKET-013-observability-enterprise-detailed-plan.md) |
| TICKET-014 | [TICKET-014-ci-quality-gates-detailed-plan.md](./TICKET-014-ci-quality-gates-detailed-plan.md) |
| TICKET-015 | [TICKET-015-connector-framework-detailed-plan.md](./TICKET-015-connector-framework-detailed-plan.md) |
| TICKET-016 | [TICKET-016-semantic-web-bi-detailed-plan.md](./TICKET-016-semantic-web-bi-detailed-plan.md) |
| TICKET-017 | [TICKET-017-desktop-authoring-detailed-plan.md](./TICKET-017-desktop-authoring-detailed-plan.md) |
| TICKET-018 | [TICKET-018-frontend-architect-detailed-plan.md](./TICKET-018-frontend-architect-detailed-plan.md) |

**Cartões curtos:** [`tickets/`](../../tickets/README.md)

**Como executar:** um ticket por PR quando possível; após cada entrega, atualizar checklist em `docs/CHECKLISTS/` e nota curta em `CHANGELOG.md` (raiz).
