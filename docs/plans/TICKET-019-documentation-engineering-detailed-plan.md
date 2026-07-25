# Plano detalhado — TICKET-019 Documentation Engineering

## Objectivo

Fechar a lacuna de documentação canónica (guias, OpenAPI, exemplos, diagramas, ADR) sem alterar comportamento runtime.

## Entregáveis

1. ADR-004 padrões de documentação; ADR-003 reservado para Desktop runtime (ADR-002 = frontend React/Next no `main`)
2. `docs/INSTALLATION.md`, `DEPLOYMENT.md`, `DEVELOPMENT.md`, `DOCUMENTATION.md`
3. `docs/openapi/` + `scripts/export-openapi.sh` + `make openapi`
4. `docs/examples/` (auth + upload)
5. `docs/diagrams/` (contexto, auth, ingestão, UML)
6. Checklist + DoD + índices + CHANGELOG/ROADMAP + ticket

## Critérios de aceite

Ver cartão [`tickets/TICKET-019-documentation-engineering.md`](../../tickets/TICKET-019-documentation-engineering.md).

## Riscos

Snapshot OpenAPI desactualizado — mitigado por script e checklist de PR.

## Nota de numeração

Ramo de origem usava TICKET-018 / ADR-002; renumerado no merge com `main` para TICKET-019 / ADR-004.
