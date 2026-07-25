# Roadmap

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
