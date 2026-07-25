# Engenharia de documentação — 4Pro_BI

## O que faz

Política e mapa da documentação técnica do monorepo. Garante que código e docs evoluem juntos (ADR-004).

## Como funciona

```text
docs/
  README.md              ← índice geral
  DOCUMENTATION.md       ← este mapa / política
  INSTALLATION.md
  DEPLOYMENT.md
  DEVELOPMENT.md
  ARCHITECTURE.md
  diagrams/              ← Mermaid + UML
  openapi/               ← Swagger/OpenAPI snapshot
  examples/              ← cURL / amostras
  adr/                   ← decisões
  CHECKLISTS/            ← DoD e QA
  plans/ + wireframes/   ← execução e UX
```

Runtime Swagger: `http://<api>/docs` · ReDoc: `/redoc` · Schema: `/openapi.json`.

## Como instalar

Clone o repositório; a documentação é Markdown — sem build obrigatório. Para regenerar OpenAPI: `./scripts/export-openapi.sh` (venv com deps da API).

## Como configurar

N/A. Autores devem seguir o checklist [`CHECKLISTS/documentation-checklist.md`](./CHECKLISTS/documentation-checklist.md).

## Como testar

- Preview Markdown + render Mermaid
- Links quebrados (revisão manual / CI futuro)
- Diff de `docs/openapi/openapi.json` após mudanças de API
- Executar `docs/examples/*.sh` contra API local

## Como evoluir

1. Feature → actualizar domínio + checklist.
2. Decisão → ADR.
3. Fluxo → diagrama.
4. API → OpenAPI + exemplos.
5. Entrada em `CHANGELOG.md` e, se fase mudar, `ROADMAP.md`.

Ticket de baseline: [`tickets/TICKET-019-documentation-engineering.md`](../tickets/TICKET-019-documentation-engineering.md).
