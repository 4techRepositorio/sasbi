# Roadmap

## O que faz

Compromissos de produto por fase, ligados a tickets e planos detalhados.

## Como funciona

Fases 1–2 cobrem o núcleo SaaS (auth, tenant, ingestão, billing). Fase 3 governação/workspace. Fase 4 plataforma BI (conectores, semântica, desktop). Documentação e CI são faixas transversais.

## Fase 1
- auth
- tenant
- usuários
- grupos
- upload básico
- catálogo básico

## Fase 2
- pipeline assíncrona
- billing
- limites por plano
- admin

## Fase 3

- dashboards básicos — **TICKET-011** (`docs/plans/TICKET-011-workspace-dashboards-detailed-plan.md`)
- customização por tenant — **TICKET-011** (com ADR embed vs canvas)
- camadas governadas de dados — **TICKET-012** (`docs/plans/TICKET-012-data-governance-detailed-plan.md`)
- auditoria avançada — **TICKET-013**
- observabilidade — **TICKET-013** (`docs/plans/TICKET-013-observability-enterprise-detailed-plan.md`)

## Fase 4 — Plataforma BI (conectores + Web + Desktop)

Plano mestre: [`docs/plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md`](./plans/PLATAFORMA-BI-CONNECTORS-DESKTOP-WEB.md) · ADR [`001`](./adr/001-bi-platform-connectors-desktop-web.md)

- framework de conectores / plugins — **TICKET-015**
- camada semântica + BI Web — **TICKET-016** (coordena com 011)
- Desktop de autoração — **TICKET-017**
- ondas O2/O3 de conectores, schedules e seats — evolução pós-017

## CI / qualidade

- pipeline em PR — **TICKET-014** (`docs/plans/TICKET-014-ci-quality-gates-detailed-plan.md`)

## Documentação (transversal)

- baseline de engenharia de docs — **TICKET-018** (`tickets/TICKET-018-documentation-engineering.md`)
- guias install/deploy/dev, OpenAPI versionado, exemplos, diagramas, ADR-002
- evolução: cada feature actualiza docs no mesmo PR (checklist em `docs/CHECKLISTS/documentation-checklist.md`)

## Como instalar / configurar / testar / evoluir

Ver [INSTALLATION.md](./INSTALLATION.md), [DEVELOPMENT.md](./DEVELOPMENT.md). Alterar este roadmap só com acordo de produto; reflectir em `tickets/` e `CHANGELOG.md`.
