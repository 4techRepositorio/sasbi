---
name: create-next-screen
description: Cria um ecrã Next.js (Feature-First) com estados, testes e documentação
---

# Skill: create-next-screen

Usar quando o alvo for React/Next.js (stack da skill `frontend-architect`). Para `apps/web` Angular actual, usar `create-angular-screen`.

## Passos

1. **Feature folder** — `features/<nome>/` com `components/`, `hooks/`, `schemas/`, `api/`, `types/`, `index.ts`.
2. **Rota thin** — página em `app/.../page.tsx` (Server Component por defeito); interatividade em Client Components filhos.
3. **Atomic Design** — reutilizar atoms/molecules em `shared/ui` antes de criar novos; nunca duplicar.
4. **Formulários** — React Hook Form + Zod quando houver input; schema tipado.
5. **Dados** — TanStack Query (client) ou fetch server; keys com tenant quando aplicável.
6. **Estados de UI** — loading, erro, vazio, sucesso.
7. **Tenant** — ecrãs admin mostram tenant actual.
8. **Componente** — props tipadas + JSDoc `@example` + teste mínimo.
9. **Performance** — `dynamic()` / lazy para widgets pesados; `"use client"` só onde necessário.
10. **Checklist** — preencher itens relevantes em `docs/CHECKLISTS/frontend-checklist.md`.

## Template mínimo de componente

```tsx
/**
 * Filtra datasets por nome.
 *
 * @example
 * <DatasetSearch value={q} onChange={setQ} />
 */
export type DatasetSearchProps = {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
};

export function DatasetSearch({ value, onChange, disabled }: DatasetSearchProps) {
  // ...
}
```
