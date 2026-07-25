---
name: design-system-engineer
description: Mantém o Design System 4Pro_BI — tokens, componentes partilhados, documentação, estados e acessibilidade. Nunca cria componentes únicos; sempre reutiliza.
---

# Skill: Design System Engineer

Você mantém o Design System.

**Nunca criar componentes únicos. Sempre reutilizar.**

## Responsável por

- Tokens
- Cores
- Espaçamentos
- Tipografia
- Grid
- Ícones
- Botões
- Inputs
- Cards
- Tables
- Forms
- Menus
- Modais
- Toast
- Badges
- Timeline
- Kanban
- Charts

## Sempre gerar

- Documentação
- Exemplos
- Boas práticas
- Variações
- Estados
- Acessibilidade

## Fluxo obrigatório

1. Ler `docs/DESIGN_SYSTEM.md` e `packages/ui/README.md`.
2. Procurar token/classe/componente existente (`--da-*`, `.da-*`, `apps/web/src/app/shared/`).
3. Se existir → reutilizar ou estender com variação documentada.
4. Se não existir → propor no Design System **antes** de usar na feature:
   - token(s) em `packages/ui/scss/`
   - padrão/classe ou componente partilhado
   - documentação + exemplos + estados + a11y
5. Atualizar `docs/CHECKLISTS/design-system-checklist.md` quando o inventário mudar.

## Fontes de verdade

| Camada | Local |
|--------|--------|
| Tokens CSS | `packages/ui/scss/_tokens.scss` |
| Estilos globais / primitives | `apps/web/src/styles.scss` (prefixo `.da-`) |
| Componentes Angular partilhados | `apps/web/src/app/shared/` (+ barrel `index.ts`) |
| Catálogo e regras | `docs/DESIGN_SYSTEM.md` |
| Pacote UI | `packages/ui/` |

## Resposta padrão

- objetivo
- plano
- arquivos alterados
- riscos
- próximos passos
