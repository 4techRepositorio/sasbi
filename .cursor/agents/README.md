# Agentes Cursor — 4Pro_BI

Subagentes do projeto em `.cursor/agents/*.md` (frontmatter YAML + instruções).

## Como usar

1. **Chat dedicado** — abrir um chat por agente e colar o prompt de [`docs/plans/PROMPTS-CHATS-CURSOR.md`](../../docs/plans/PROMPTS-CHATS-CURSOR.md) (C0–C6) ou [`PROMPTS-CHATS-BI.md`](../../docs/plans/PROMPTS-CHATS-BI.md) (B0–B4).
2. **Slash / menção** — invocar pelo `name` do frontmatter (ex.: `/coordenador`, `/connectors`).
3. **Task tool** — o agente pai delega quando a `description` corresponder à tarefa.

## Mapa — fase base (F1–F5)

| Agente | Chat | Frente | Escrita típica |
|--------|------|--------|----------------|
| [`coordenador`](./coordenador.md) | C0 | Coordenação | só docs de orquestração (readonly preferido) |
| [`architect`](./architect.md) | C1 | F1 | `docs/`, `packages/contracts/` |
| [`backend-core`](./backend-core.md) | C2 | F2 | auth, tenant, billing, `main.py` |
| [`backend-data`](./backend-data.md) | C3 | F3 | upload, ingestão, worker, catálogo |
| [`frontend`](./frontend.md) | C4 | F4 | `apps/web/` |
| [`qa-reviewer`](./qa-reviewer.md) | C5 | F5 | testes, CI, checklists |
| [`security-reviewer`](./security-reviewer.md) | C6 | transversal | readonly — revisão |
| [`planner`](./planner.md) | — | plano | tickets/planos sem código de produto |

## Mapa — Fase 4 BI (paralelismo 015–017)

| Agente | Chat | Ticket | Escrita típica |
|--------|------|--------|----------------|
| [`coordenador`](./coordenador.md) | B0 | gates G5 | orquestração |
| [`connectors`](./connectors.md) | B1 | **015** | SPI, `packages/connectors`, sync worker |
| [`semantic-bi`](./semantic-bi.md) | B2 | **016** (+011) | query/semântica + Web Fontes/dashboards |
| [`desktop`](./desktop.md) | B3 | **017** | `apps/desktop/` |
| [`qa-reviewer`](./qa-reviewer.md) | B4 | transversal | testes conectores/query/Desktop smoke |

Plano: [`docs/plans/PARALELA-BI-FRENTES.md`](../../docs/plans/PARALELA-BI-FRENTES.md).

## Regras anti-colisão

- Respeitar allowlists em [`ORQUESTRACAO-CHATS-AGENTES.md`](../../docs/plans/ORQUESTRACAO-CHATS-AGENTES.md).
- Contratos: só **architect** / F1 altera `packages/contracts`.
- `main.py` e `models/__init__.py`: só **backend-core**.
- Migrações: prefixo `core__*` (Core) vs `data__*` (Data/Connectors).
