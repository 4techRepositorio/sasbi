# Architecture Decision Records (ADRs)

## O que faz

Regista decisões arquitecturais relevantes com contexto, decisão e consequências.

## Como funciona

| ADR | Título | Estado |
|-----|--------|--------|
| [000](./000-contract-slices.md) | Fatias de contratos (`fourpro_contracts`) | Aceite |
| [001](./001-bi-platform-connectors-desktop-web.md) | Plataforma BI: conectores + Web + Desktop | Aceite |
| [002](./002-documentation-standards.md) | Padrões de documentação técnica | Aceite |
| 003 *(reservado)* | Runtime Desktop (Electron vs Tauri) — pós spike TICKET-017 | Proposto |

Template mínimo para novos ADRs:

```markdown
# ADR-XXX — Título
## Estado
## Contexto
## Decisão
## Consequências
## Alternativas rejeitadas
```

## Como instalar / configurar

N/A — documentos Markdown em Git.

## Como testar

Review em PR: a decisão está clara? impacto em contratos/deploy mencionado?

## Como evoluir

Numeração sequencial; actualizar `docs/ARCHITECTURE.md` quando a decisão mudar boundaries. Não apagar ADRs — marcar `Superseded by ADR-YYY`.
