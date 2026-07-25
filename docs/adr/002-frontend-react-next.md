# ADR-002 — Stack frontend alvo: React + Next.js

**Estado:** proposto  
**Data:** 2026-07-25  
**Decisores:** Frontend Architect · Architect · Product · QA · Security  
**Relacionados:** `docs/FRONTEND_ARCHITECTURE.md`, `docs/ARCHITECTURE.md`, ADR-001 (cliente Web), TICKET-011, TICKET-018

## Contexto

O portal actual vive em `apps/web` (**Angular 19**), alinhado às rules Cursor e aos tickets base. A frente Frontend Architect define um stack alvo orientado a:

- Feature-First + Atomic Design
- SSR / RSC com Client Components só quando necessário
- Design system com Tailwind + shadcn/ui (tokens 4Pro_BI)
- Dados com TanStack Query; formulários com React Hook Form + Zod
- Componentes sempre com props tipadas, documentação, exemplo e testes

Migrar sem decisão formal criaria divergência com CI (`ng build`), e2e e documentação existentes.

## Decisão (proposta)

1. **Manter Angular** em `apps/web` como implementação canónica até aceite explícito deste ADR e plano de migração por fatias.
2. **Adoptar como stack alvo** React + Next.js (App Router) + TypeScript + Tailwind + shadcn/ui + TanStack Query + RHF + Zod, documentado em `docs/FRONTEND_ARCHITECTURE.md` e skills:
   - `.cursor/skills/frontend-architect`
   - `.cursor/skills/create-next-screen`
3. **Migração** (se aceite) será **faseada por feature**, com paridade de rotas, guards/RBAC, tenant context e e2e; sem big-bang.
4. **Experiência unificada 4Pro_BI** mantém-se: aceleradores (shadcn, etc.) sem marcas externas na UX final (ARCHITECTURE.md § Aceleradores).
5. **ADR-001** (híbrido canvas Web) permanece válido; a escolha do motor de UI (Angular vs React) é ortogonal ao BFF/proxy de BI.

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| A — Permanecer só Angular | Menor risco, CI/e2e maduros | Menos alinhado ao stack pedido pelo Frontend Architect |
| B — Big-bang para Next.js | Stack único rápido | Alto risco de regressão auth/tenant/upload |
| C — Faseado (esta ADR) | Controlo de risco, skills e docs já alinhados | Dual-stack temporário |

## Consequências

- Agents não devem escrever React dentro de `apps/web` Angular sem aceite desta ADR.
- Novos greenfields Next.js só após aceite + ticket de scaffold (pasta, Docker, CI).
- Checklist frontend inclui critérios do stack alvo sem invalidar o Angular actual.
- Aceite futuro exige actualizar `.cursor/rules/03-frontend.mdc`, `ARCHITECTURE.md` (bloco Web App), CI e skills Angular → Next.

## Critérios para aceitar a migração

- [ ] Plano por fatias (auth → shell → upload → catálogo → billing → BI)
- [ ] Paridade de testes e2e críticos
- [ ] Contratos OpenAPI / `packages/contracts` sem regressão
- [ ] Quotas, MFA, RBAC e indicação de tenant preservados
- [ ] Build/CI Next.js green + smoke

## Estado seguinte

Enquanto **proposto**: aplicar princípios (modularidade, tipagem, testes, Feature-First) no Angular; preparar skills/docs para o alvo React/Next.
