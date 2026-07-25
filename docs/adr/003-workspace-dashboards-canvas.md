# ADR-003 — Workspace dashboards: canvas nativo (MVP)

**Estado:** aceite  
**Data:** 2026-07-25  
**Tickets:** TICKET-011 (coordena com 016)  
**Relacionado:** ADR-001 (híbrido Web + query API)

## Contexto

O plano detalhado do TICKET-011 exige escolha explícita entre embed OSS (A), canvas próprio (B) ou híbrido (C). A UX final deve ser nativa 4Pro_BI, sem cromo de terceiros.

## Decisão

1. **MVP (esta entrega):** opção **B — canvas Angular próprio** com widgets KPI, tabela e gráfico simples, layout JSON versionado em `dashboards.layout_json` / `dashboard_widgets`.
2. **Evolução (TICKET-016+):** caminho **C — híbrido**: widgets passam a consumir a **query API semântica** (`/api/v1/query`); um futuro motor embutido só via BFF nativo sem marcas OSS na UI.
3. **RBAC:** `admin` e `analyst` criam/editam; `consumer` só lê.
4. **Export MVP:** `GET .../export` devolve pacote JSON (snapshot de layout + metadados); PNG/PDF fica fase seguinte.

## Consequências

- Sem dependência de embed multitenant no MVP.
- Widgets com dataset em falta mostram placeholder (critério D5).
- Isolamento estrito por `tenant_id` do JWT.
