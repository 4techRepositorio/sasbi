# TICKET-018 — Frontend Architect: stack React/Next (ADR-002)

## Objetivo

Formalizar o papel **Frontend Architect** e o stack alvo (React, Next.js, TypeScript, Tailwind, shadcn/ui, TanStack Query, React Hook Form, Zod), com convenções Feature-First, Atomic Design e qualidade por componente — sem migrar `apps/web` Angular até aceite do ADR.

## Escopo

- Skill `frontend-architect` e `create-next-screen`
- `docs/FRONTEND_ARCHITECTURE.md`
- ADR-002 (estado: proposto)
- Actualização de AGENTS, checklist frontend e rule `03-frontend.mdc`
- Referência em `ARCHITECTURE.md`
- Plano detalhado em `docs/plans/TICKET-018-frontend-architect-detailed-plan.md`

## Fora de escopo

- Scaffold de app Next.js em produção
- Migração de rotas Angular → React
- Alteração de CI de `ng build` para Next
- Mudança de contratos API

## Impacto técnico

| Área | Impacto |
|------|---------|
| backend | nenhum |
| frontend | convenções e docs; código Angular inalterado |
| dados | nenhum |
| segurança | princípios de tenant/RBAC reforçados na doc |
| billing | nenhum |

## Subtarefas

1. [x] Publicar skills e documentação
2. [x] ADR-002 proposto
3. [ ] Revisão Product/Architect — aceitar ou rejeitar ADR-002
4. [ ] Se aceite: ticket de scaffold Next + plano de migração por fatias
5. [ ] Se rejeitado: manter Angular e arquivar stack alvo como referência opcional

## Critérios de aceite

- [x] Skill e docs disponíveis no repo
- [x] Agents não misturam React em `apps/web` sem ADR aceite
- [x] Checklist frontend inclui critérios de arquitectura
- [ ] Decisão explícita sobre ADR-002 registada (aceite / rejeitado / adiado)

## Riscos

- Dual-stack temporário se a migração avançar sem plano por fatias
- Confusão de agents entre Angular actual e React alvo — mitigado por ADR + rule `03-frontend.mdc`

## Dependências

- ADR-001 (cliente Web / BI híbrido)
- CI e e2e actuais de `apps/web`

## Plano detalhado

[`docs/plans/TICKET-018-frontend-architect-detailed-plan.md`](../docs/plans/TICKET-018-frontend-architect-detailed-plan.md)
