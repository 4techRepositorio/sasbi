# TICKET-018 — Plano detalhado: Frontend Architect (React/Next)

## Objectivo

Fixar o mandato do **Frontend Architect** e o stack alvo React · Next.js · TypeScript · Tailwind · shadcn/ui · TanStack Query · React Hook Form · Zod, com Feature-First, Atomic Design e contrato de componente — **sem** migrar `apps/web` até aceite do ADR-002.

## Contexto

- Produção actual: Angular 19 em `apps/web` (CI `ng build`, e2e Playwright).
- Skill e docs: `.cursor/skills/frontend-architect`, `docs/FRONTEND_ARCHITECTURE.md`.
- ADR: [002-frontend-react-next.md](../adr/002-frontend-react-next.md) (proposto).

## Escopo desta entrega (docs/skills)

| Inclui | Exclui |
|--------|--------|
| Skills, ADR, checklist, AGENTS, rules | Scaffold Next.js em `apps/` |
| Princípios aplicáveis também ao Angular | Big-bang de migração |
| Ticket + plano de decisão | Alteração de contratos API |

## Fatias futuras (só se ADR aceite)

1. **Scaffold** — `apps/web-next` (ou rename), Docker, health, CI paralelo.
2. **Auth** — login, refresh, MFA, reset (paridade e2e).
3. **Shell + tenant context** — RBAC, indicação de tenant, quotas.
4. **Upload / ingestões / datasets** — estados de pipeline.
5. **Billing / admin** — membros, auditoria, quotas.
6. **Workspace / BI** — alinhado a ADR-001; cutover e remoção Angular.

## Critérios de aceite (fase docs)

- [x] Skill `frontend-architect` com stack, princípios e receitas
- [x] Skill `create-next-screen` para scaffold de ecrã
- [x] `FRONTEND_ARCHITECTURE.md` + ADR-002 proposto
- [x] Rule `03-frontend.mdc` referencia stack alvo sem forçar React em Angular
- [x] Diretrizes operacionais no doc canónico + agente Cursor `frontend.md` alinhado
- [x] Skill `create-angular-screen` alinhada ao contrato de componente
- [ ] Decisão Product/Architect sobre ADR-002

## Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Agents misturam React em `apps/web` | ADR + rule explícita + skill |
| Dual-stack sem plano | Migração só por fatias após aceite |
| Divergência design system | Tokens 4Pro_BI; skill UI Designer |

## Dependências

- ADR-001, checklists frontend/QA, CI e e2e de `apps/web`.
