# Arquitetura Frontend (4Pro_BI)

Documento de referência do **Frontend Architect**. Complementa [ARCHITECTURE.md](./ARCHITECTURE.md) e a skill `.cursor/skills/frontend-architect`.

## Objectivo

Criar aplicações UI **escaláveis**, **modulares**, **performáticas** e **reutilizáveis**, com isolamento por tenant e experiência nativa 4Pro_BI.

| Qualidade | Expectativa |
|-----------|-------------|
| Escalável | Features isoladas; rotas thin; sem god-components |
| Modular | Feature-First + Atomic Design; API pública via `index.ts` / barrels |
| Performática | SSR/RSC por defeito (alvo); lazy loading; code splitting; Client só quando necessário |
| Reutilizável | Nunca duplicar; extrair no 2.º uso para `shared` / `packages/ui` |

---

## Stack

### Actual (produção / monorepo)

| Item | Valor |
|------|--------|
| App | `apps/web` |
| Framework | Angular 19 |
| Estilo | SCSS corporativo (`--da-*`) |
| Skills | `create-angular-screen` |

### Alvo (ADR-002)

| Item | Valor |
|------|--------|
| UI | React |
| Framework | Next.js (App Router) |
| Linguagem | TypeScript strict |
| Estilo | Tailwind CSS |
| Design system | shadcn/ui (tokens nativos 4Pro_BI) |
| Server state | TanStack Query |
| Forms | React Hook Form + Zod |
| Skills | `frontend-architect`, `create-next-screen` |

Estado da decisão: [adr/002-frontend-react-next.md](./adr/002-frontend-react-next.md) (**proposto** — sem scaffold React em `apps/web` até aceite).

---

## Diretrizes obrigatórias (sempre utilizar)

1. **Feature First** — organizar por domínio/feature, não só por tipo técnico.
2. **Atomic Design** — `atoms` → `molecules` → `organisms` → `templates` → `pages`.
3. **Componentes reutilizáveis** — nunca duplicar; partilhar via `shared` / `packages/ui`.
4. **Lazy loading** — rotas e widgets pesados sob demanda.
5. **Code splitting** — `loadComponent` (Angular) / `dynamic()` · `React.lazy` (Next) por feature.
6. **SSR quando necessário** — Server Components / RSC por defeito no alvo; SEO e dados sensíveis no servidor.
7. **Client Components somente quando necessário** — `"use client"` só para estado, efeitos, event handlers, APIs do browser.
8. **Sem regras de domínio críticas só no cliente** — validação UX no form; authz/tenant na API.
9. **Multitenancy visível** — ecrãs admin mostram o tenant actual.
10. **Contrato de componente** — props tipadas + documentação + exemplo + testes (ver abaixo).

---

## Feature First

Código agrupado por capacidade de negócio (`auth`, `datasets`, `billing`, …). Cada feature expõe uma API pública mínima. Rotas ficam finas (só composição + guards).

### Mapa alvo (Next.js App Router)

```text
apps/web-next/          # ou apps/web após migração (só com ADR aceite)
  app/                  # rotas thin
  features/
    auth/
      api/              # fetchers / server actions / query hooks
      components/
      hooks/
      schemas/          # Zod
      types/
      index.ts          # API pública da feature
    datasets/
    ...
  shared/
    ui/
      atoms/
      molecules/
      organisms/
    lib/                # utils, cn(), api client
    hooks/
    config/
```

### Mapa actual (Angular `apps/web`) — convergência

| Conceito | Local actual | Evolução recomendada |
|----------|--------------|----------------------|
| Rotas thin | `app.routes.ts` + `loadComponent` | Manter; evitar lógica no ficheiro de rotas |
| Features | `pages/<feature>/` | Preferir `features/<feature>/` em código novo quando o custo for baixo |
| Core (auth, tenant, HTTP) | `core/` | Manter partilhado; sem UI |
| UI partilhada | `shared/` (+ barrel `shared/index.ts`) | Atoms/molecules aqui; extrair no 2.º uso |
| API pública | barrels `index.ts` | Exportar só o necessário |

Exemplo de referência de reutilização: `app-storage-quota-block` em `shared/storage-quota-block.component.ts`.

---

## Atomic Design

| Nível | Responsabilidade | Exemplo |
|-------|------------------|---------|
| Atoms | Primitivos UI | Button, Input, Badge |
| Molecules | Combinações simples | SearchField, QuotaBar |
| Organisms | Blocos de ecrã | DatasetTable, ShellNav |
| Templates | Layouts | AdminShell, AuthLayout |
| Pages | Composição + dados | DatasetsPage |

Antes de criar um componente: **grep** em `shared/`, `packages/ui` e na feature. Se já existir, reutilizar ou estender.

---

## Contrato obrigatório de todo componente

| Requisito | Como |
|-----------|------|
| Props tipadas | `type XProps` / `input()` tipado; sem `any` |
| Documentação | JSDoc no export público / classe |
| Exemplo de uso | bloco `@example` no JSDoc ou story |
| Testes | `*.test.tsx` / `*.spec.ts` — render + caminho crítico ou estados vazios/erro |

Estados de ecrã obrigatórios: **loading**, **erro**, **vazio**, **sucesso**.

### Template (alvo React/Next)

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

### Template (Angular actual)

```ts
/**
 * Filtra datasets por nome.
 *
 * @example
 * <app-dataset-search [value]="q" (valueChange)="q = $event" />
 */
@Component({ selector: 'app-dataset-search', /* ... */ })
export class DatasetSearchComponent {
  readonly value = input.required<string>();
  readonly valueChange = output<string>();
  readonly disabled = input(false);
}
```

### Teste mínimo (alvo)

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

> Nota: `apps/web` Angular ainda não tem runner unitário dedicado no `package.json`. Novos componentes devem cumprir tipagem + JSDoc + `@example`; testes unitários entram com o ticket de CI/unitários ou no cutover Next. E2E Playwright continua a cobrir fluxos críticos.

---

## Receitas (stack alvo)

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

- Schema Zod = fonte de verdade tipada (`z.infer`).
- Mensagens amigáveis; erros técnicos só em log/telemetria.

### Performance

- Split por rota/feature (`next/dynamic` com `ssr: false` só se inevitável).
- Imagens com componente otimizado do Next.
- Evitar bundles UI pesados no caminho crítico login/shell.
- Preferir Server Components para listas estáticas; Client para filtros interativos.

### Design system

- Wrappers shadcn em `shared/ui`; tokens CSS alinhados a 4Pro_BI (`--da-*` no Angular actual).
- Na UX final: **zero** marcas de libs externas (ver ARCHITECTURE.md § Aceleradores).

---

## Fronteiras

```text
Browser UI  →  API (contratos)  →  Domain / Services
     ↑                ↑
  Zod / forms (UX)   Auth + tenant + RBAC (fonte da verdade)
```

- Não embutir regras críticas de billing/RBAC só no frontend.
- `tenant_id` nunca é confiado a partir do body/query sem sessão validada.
- Contratos partilhados em `packages/contracts` (impacto documentado antes de mudar).

---

## Anti-padrões

- Duplicar botões/inputs em vez de atoms partilhados.
- `"use client"` no layout raiz sem necessidade.
- Lógica de billing/RBAC só no frontend.
- Componentes sem props tipadas, sem docs, sem exemplo ou sem teste (quando runner existir).
- Importar uma feature inteira noutra (usar API pública via `index.ts`).
- Introduzir React dentro de `apps/web` Angular sem aceite do ADR-002.
- God-components (página com toda a lógica + markup sem extrair organismos).

---

## Fluxo ao criar UI nova

1. Confirmar se existe componente reutilizável (grep em `shared/` / `packages/ui`).
2. Escolher nível atómico; tipar props; documentar + `@example` (+ teste quando aplicável).
3. Colocar na feature correcta; expor só o necessário no barrel.
4. Wire na rota com lazy/`loadComponent` se pesado.
5. Tratar loading / erro / vazio / sucesso + tenant visível se admin.
6. Checklist [CHECKLISTS/frontend-checklist.md](./CHECKLISTS/frontend-checklist.md).

---

## Relação com Angular actual

Enquanto `apps/web` for Angular:

- Manter separação layout / estado / serviços / componentes.
- Aplicar Feature-First e Atomic Design na organização sempre que possível.
- Componentes partilhados em `apps/web/src/app/shared` e evolução de `packages/ui`.
- Novos ecrãs: skill `create-angular-screen` + checklist frontend.
- Migração React/Next: apenas após aceite do ADR-002 e plano por feature (sem big-bang). Fatias previstas: scaffold → auth → shell/tenant → upload/catálogo → billing/admin → workspace/BI.

---

## Checklists e agentes

- Checklist: [CHECKLISTS/frontend-checklist.md](./CHECKLISTS/frontend-checklist.md)
- Agente: [AGENTS.md](./AGENTS.md) § Frontend Architect · Cursor: `.cursor/agents/frontend.md`
- Regras Cursor: `.cursor/rules/03-frontend.mdc`
- Skills: `.cursor/skills/frontend-architect`, `create-angular-screen`, `create-next-screen`
- Ticket: [TICKET-018](../tickets/TICKET-018-frontend-architect-react-next.md) · [plano detalhado](./plans/TICKET-018-frontend-architect-detailed-plan.md)
