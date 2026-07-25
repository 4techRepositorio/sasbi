---
name: frontend-architect
description: Arquitetura frontend Feature-First + Atomic Design (React, Next.js, TypeScript, Tailwind, shadcn/ui, TanStack Query, RHF, Zod). Usar ao criar/revisar UI, estrutura de pastas, design system ou migração frontend.
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

## Objectivos de toda aplicação UI

| Qualidade | Expectativa |
|-----------|-------------|
| Escalável | Features isoladas; rotas thin; sem god-components |
| Modular | Feature-First + Atomic Design; API pública via `index.ts` |
| Performática | SSR/RSC por defeito; lazy loading; code splitting; Client só quando necessário |
| Reutilizável | Nunca duplicar; extrair no 2.º uso para `shared/ui` ou `packages/ui` |

## Princípios obrigatórios (sempre utilizar)

1. **Feature First** — organizar por domínio/feature, não só por tipo técnico.
2. **Atomic Design** — `atoms` → `molecules` → `organisms` → `templates` → `pages`.
3. **Componentes reutilizáveis** — nunca duplicar; partilhar via `shared/ui` / `packages/ui`.
4. **Lazy loading** — rotas e widgets pesados sob demanda.
5. **Code splitting** — `dynamic()` / `React.lazy` / import dinâmico por feature.
6. **SSR quando necessário** — Server Components / RSC por defeito; SEO e dados sensíveis no servidor.
7. **Client Components somente quando necessário** — `"use client"` só para estado, efeitos, event handlers, APIs do browser.
8. **Sem regras de domínio críticas só no cliente** — Zod para UX; authz/tenant na API.
9. **Multitenancy visível** — ecrãs admin mostram o tenant actual.

## Estrutura Feature-First (Next.js App Router)

```text
apps/web-next/   # ou apps/web após migração
  app/                    # rotas (thin)
  features/
    auth/
      api/                # fetchers / server actions / query hooks
      components/         # UI da feature
      hooks/
      schemas/            # Zod
      types/
      index.ts            # API pública da feature
    datasets/
    ...
  shared/
    ui/                   # atoms/molecules/organisms (wrappers shadcn)
      atoms/
      molecules/
      organisms/
    lib/                  # utils, cn(), api client
    hooks/
    config/
```

## Contrato obrigatório de todo componente

Todo componente **deve** ter:

| Requisito | Como |
|-----------|------|
| Props tipadas | `type XProps = { ... }` exportado; sem `any` |
| Documentação | JSDoc no export público |
| Exemplo de uso | bloco `@example` no JSDoc ou `*.stories.tsx` |
| Testes | `*.test.tsx` (ou colocalizado) — render + caminho crítico ou estados vazios/erro |

Estados de ecrã obrigatórios: **loading**, **erro**, **vazio**, **sucesso**.

### Template mínimo

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

### Teste mínimo

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { DatasetSearch } from "./dataset-search";

test("chama onChange ao escrever", async () => {
  const onChange = vi.fn();
  render(<DatasetSearch value="" onChange={onChange} />);
  await userEvent.type(screen.getByRole("searchbox"), "a");
  expect(onChange).toHaveBeenCalled();
});
```

## Receitas de implementação

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

### TanStack Query (keys com tenant)

```tsx
export const datasetKeys = {
  all: (tenantId: string) => ["datasets", tenantId] as const,
  list: (tenantId: string, q: string) => [...datasetKeys.all(tenantId), "list", q] as const,
  detail: (tenantId: string, id: string) => [...datasetKeys.all(tenantId), id] as const,
};
```

- Queries/mutations por feature em `features/<name>/api` ou `hooks`.
- Keys estáveis e **scoped por `tenantId`** quando o cache for partilhado.
- Nunca confiar em `tenant_id` enviado pelo cliente sem sessão validada na API.

### React Hook Form + Zod

```tsx
const schema = z.object({
  email: z.string().email("Email inválido"),
  password: z.string().min(8, "Mínimo 8 caracteres"),
});
type FormValues = z.infer<typeof schema>;

const form = useForm<FormValues>({
  resolver: zodResolver(schema),
  defaultValues: { email: "", password: "" },
});
```

- Schema Zod = fonte de verdade; tipar com `z.infer`.
- Mensagens amigáveis; erros técnicos só em log/telemetria.

### Performance

- Split por rota/feature (`next/dynamic` com `ssr: false` só se inevitável).
- Imagens com componente otimizado do Next.
- Evitar bundles UI pesados no caminho crítico login/shell.
- Preferir Server Components para listas estáticas; Client para filtros interativos.

### Design system

- Wrappers shadcn em `shared/ui`; tokens CSS alinhados a 4Pro_BI.
- Colaborar com skill `senior-ui-designer` para tokens/estados.
- Na UX final: **zero** marcas de libs externas (ver `docs/ARCHITECTURE.md` § Aceleradores).

## Anti-padrões

- Duplicar botões/inputs em vez de atoms partilhados.
- `"use client"` no layout raiz sem necessidade.
- Lógica de billing/RBAC só no frontend.
- Componentes sem props tipadas, sem docs, sem exemplo ou sem teste.
- Importar uma feature inteira noutra (usar API pública via `index.ts`).
- Introduzir React dentro de `apps/web` Angular sem aceite do ADR-002.

## Fluxo ao criar UI nova

1. Confirmar se existe componente reutilizável (grep em `shared/ui` / `packages/ui` / Angular `shared/`).
2. Escolher nível atómico; tipar props; documentar + exemplo + teste.
3. Colocar na feature correcta; expor só o necessário no `index.ts`.
4. Wire na rota (`app/`) com lazy/dynamic se pesado.
5. Tratar loading/erro/vazio/sucesso + tenant visível se admin.
6. Checklist `docs/CHECKLISTS/frontend-checklist.md`.

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
- Skill irmã: `create-next-screen` (scaffold de ecrã); Angular actual: `create-angular-screen`
- UI tokens: skill `senior-ui-designer` (quando disponível no repo)
