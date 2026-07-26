# UI — Design System 4Pro_BI

Biblioteca de **tokens** e referência de componentes partilhados do `apps/web` (Angular).  
Objetivo: reutilizar layout e padrões visuais **sem duplicar markup** (Atomic Design — ver [docs/FRONTEND_ARCHITECTURE.md](../../docs/FRONTEND_ARCHITECTURE.md)).

> **Regra de ouro:** nunca criar componentes únicos de ecrã. Sempre reutilizar ou elevar ao Design System.

## Estrutura

```
packages/ui/
  scss/_tokens.scss      # tokens CSS (--da-*) — fonte de verdade
  docs/EXAMPLES.md       # exemplos copiáveis
  docs/BEST-PRACTICES.md # boas práticas e anti-padrões
  README.md              # este ficheiro
```

Primitives CSS (botões, cards, tabelas, shell, …) vivem hoje em  
`apps/web/src/styles.scss` (prefixo `.da-*`), consumindo os tokens acima.

Componentes Angular partilhados: `apps/web/src/app/shared/` (+ `index.ts`).

## Documentação

| Doc | Conteúdo |
|-----|----------|
| [docs/DESIGN_SYSTEM.md](../../docs/DESIGN_SYSTEM.md) | Catálogo, tokens, estados, a11y, roadmap |
| [docs/EXAMPLES.md](./docs/EXAMPLES.md) | Exemplos |
| [docs/BEST-PRACTICES.md](./docs/BEST-PRACTICES.md) | Boas práticas |
| [design-system-checklist.md](../../docs/CHECKLISTS/design-system-checklist.md) | Checklist de PR |

## Agente

- Skill: `.cursor/skills/design-system-engineer/SKILL.md`
- Agente: `.cursor/agents/design-system-engineer.md`
- Consumo / arquitectura de ecrãs: skill `frontend-architect`
- Protótipos: skill `figma-design-specialist` (tokens alinhados a `--da-*`)

## Alinhamento de produto

Na superfície que o utilizador final vê, manter experiência **4Pro_BI**  
(ver [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md), secção sobre aceleradores e experiência unificada).

Stack alvo ([ADR-005](../../docs/adr/005-frontend-react-next.md)): evolução eventual para tokens/componentes consumíveis por React/Next; até lá, esta pasta serve o Angular actual.
