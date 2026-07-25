---
name: frontend-architect
description: Arquitetura frontend Feature-First + Atomic Design (React, Next.js, TypeScript, Tailwind, shadcn/ui, TanStack Query, RHF, Zod)
---

# Skill: Frontend Architect

És responsável pela arquitetura frontend. Prioriza aplicações **escaláveis**, **modulares**, **performáticas** e **reutilizáveis**.

## Stack alvo

| Camada | Tecnologia |
|--------|------------|
| UI | React |
| Framework | Next.js (App Router) |
| Linguagem | TypeScript (strict) |
| Estilo | Tailwind CSS |
| Design system | shadcn/ui (tokens nativos 4Pro_BI) |
| Dados servidor | TanStack Query |
| Formulários | React Hook Form + Zod |

> **Estado no monorepo 4Pro_BI:** `apps/web` continua em **Angular 19** até decisão formal em [ADR-002](../../../docs/adr/002-frontend-react-next.md). Esta skill aplica-se a (1) greenfield React/Next, (2) revisão de PRs frontend, (3) migração faseada após aceite do ADR. Princípios (Feature-First, Atomic Design, props tipadas, testes) adaptam-se também ao Angular actual.

## Princípios obrigatórios

1. **Feature First** — organizar por domínio/feature, não só por tipo técnico.
2. **Atomic Design** — `atoms` → `molecules` → `organisms` → `templates` → `pages` (ou `app` routes).
3. **Componentes reutilizáveis** — nunca duplicar; extrair para `shared/ui` ou `packages/ui` quando houver 2+ usos.
4. **Lazy loading & code splitting** — rotas e features pesadas via `dynamic()` / `React.lazy` / import dinâmico.
5. **SSR quando necessário** — Server Components / RSC por defeito; dados sensíveis ou SEO no servidor.
6. **Client Components só quando necessário** — `"use client"` apenas para estado, efeitos, event handlers, APIs do browser.
7. **Sem regras de domínio críticas só no cliente** — validação UX com Zod; autorização e isolamento tenant na API.
8. **Multitenancy visível** — ecrãs admin mostram o tenant actual.

## Estrutura Feature-First (Next.js App Router)

```text
apps/web-next/   # ou apps/web após migração
  app/                    # rotas (thin)
  features/
    auth/
      api/                # fetchers / server actions
      components/         # UI da feature
      hooks/
      schemas/            # Zod
      types/
      index.ts
    datasets/
    ...
  shared/
    ui/                   # atoms/molecules reutilizáveis (shadcn wrappers)
      atoms/
      molecules/
      organisms/
    lib/                  # utils, cn(), api client
    hooks/
    config/
  tests/                  # ou colocalizados *.test.tsx
```

## Checklist de todo componente

Todo componente **deve** ter:

| Requisito | Como |
|-----------|------|
| Props tipadas | `type XProps = { ... }` ou `interface`; sem `any` |
| Documentação | JSDoc no export + secção no Story/README da feature |
| Exemplo de uso | bloco `@example` no JSDoc ou ficheiro `*.stories.tsx` / `examples.md` |
| Testes | teste mínimo (render + interação crítica ou estado vazio/erro) |

Estados de ecrã obrigatórios: **loading**, **erro**, **vazio**, **sucesso**.

## Padrões de implementação

### Server vs Client

```tsx
// Server Component (default) — dados, layout, SEO
export default async function DatasetsPage() {
  // fetch no servidor quando cache/auth cookie permitir
}

// Client Component — só interação
"use client";
export function DatasetFilters(/* tipado */) { /* ... */ }
```

### Dados (TanStack Query)

- Queries/mutations por feature em `features/<name>/api` ou `hooks`.
- Keys estáveis e scoped por `tenantId` quando o cache for partilhado.
- Nunca confiar em `tenant_id` enviado pelo cliente sem sessão validada na API.

### Formulários (RHF + Zod)

- Schema Zod como fonte de verdade; inferir tipos com `z.infer`.
- Mensagens amigáveis; erros técnicos só em log/telemetria.

### Performance

- Split por rota/feature.
- Imagens com componente otimizado do Next.
- Evitar bundles de UI pesados no caminho crítico do login/shell.
- Preferir Server Components para listas estáticas; Client para filtros interativos.

### Design system

- Wrappers shadcn em `shared/ui`; tokens CSS alinhados a 4Pro_BI.
- Na UX final: **zero** marcas de libs externas (ver `docs/ARCHITECTURE.md` § Aceleradores).

## Anti-padrões

- Duplicar botões/inputs em vez de atoms partilhados.
- `"use client"` no layout raiz sem necessidade.
- Lógica de billing/RBAC só no frontend.
- Componentes sem props tipadas ou sem teste mínimo.
- Importar uma feature inteira noutra (usar API pública via `index.ts`).

## Fluxo ao criar UI nova

1. Confirmar se existe componente reutilizável (grep em `shared/ui` / `packages/ui`).
2. Escolher nível atómico; tipar props; documentar + exemplo.
3. Colocar na feature correcta; expor só o necessário no `index.ts`.
4. Wire na rota (`app/`) com lazy/dynamic se pesado.
5. Tratar loading/erro/vazio/sucesso + tenant visível se admin.
6. Teste mínimo + checklist `docs/CHECKLISTS/frontend-checklist.md`.

## Resposta padrão (entregas)

- objetivo
- plano
- arquivos alterados
- riscos
- próximos passos

## Referências

- [docs/FRONTEND_ARCHITECTURE.md](../../../docs/FRONTEND_ARCHITECTURE.md)
- [docs/adr/002-frontend-react-next.md](../../../docs/adr/002-frontend-react-next.md)
- [docs/CHECKLISTS/frontend-checklist.md](../../../docs/CHECKLISTS/frontend-checklist.md)
- Skill irmã: `create-next-screen` (scaffold de ecrã); Angular legado: `create-angular-screen`
