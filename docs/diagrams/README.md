# Diagramas — 4Pro_BI

## O que faz

Índice dos diagramas técnicos (Mermaid): contexto do sistema, fluxos, sequências e UML (componentes / classes). Fonte canónica em Markdown para diff em Git.

## Como funciona

| Ficheiro | Tipo | Conteúdo |
|----------|------|----------|
| [system-context.md](./system-context.md) | Contexto / C4 leve | Actores e blocos |
| [auth-sequence.md](./auth-sequence.md) | Sequência | Login, MFA, refresh, reset |
| [ingestion-flow.md](./ingestion-flow.md) | Fluxograma / estado | Pipeline de ficheiros |
| [uml-components.md](./uml-components.md) | UML componentes | Apps e pacotes |
| [uml-class-core.md](./uml-class-core.md) | UML classes | Entidades Core / Data |

Política de export PNG/SVG: [`docs/assets/README.md`](../assets/README.md).

## Como instalar

Nada a instalar: GitHub/Cursor renderizam Mermaid nos `.md`. Export opcional com CLI Mermaid ou IDE → `docs/assets/diagrams/exports/`.

## Como configurar

N/A (documentação estática).

## Como testar

- Abrir o ficheiro no preview Markdown e validar render.
- Em PRs que alterem fluxo: actualizar o diagrama correspondente e referenciar no texto da feature.

## Como evoluir

- Novo domínio HTTP → actualizar `uml-components.md` e OpenAPI.
- Novo estado de ingestão → `ingestion-flow.md` + contrato + ADR se necessário.
- Decisão arquitectural → ADR + diagrama se mudar boundaries.
