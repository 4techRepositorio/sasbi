# Arquitetura Frontend (4Pro_BI)

Documento de referência do **Frontend Architect**. Complementa [ARCHITECTURE.md](./ARCHITECTURE.md) e a skill `.cursor/skills/frontend-architect`.

## Objectivo

Criar UIs **escaláveis**, **modulares**, **performáticas** e **reutilizáveis**, com isolamento por tenant e experiência nativa 4Pro_BI.

## Stack

### Actual (produção / monorepo)

| Item | Valor |
|------|--------|
| App | `apps/web` |
| Framework | Angular 19 |
| Estilo | SCSS corporativo |
| Skills | `create-angular-screen` |

### Alvo (ADR-002)

| Item | Valor |
|------|--------|
| UI | React |
| Framework | Next.js (App Router) |
| Linguagem | TypeScript strict |
| Estilo | Tailwind CSS |
| Componentes | shadcn/ui (tokens 4Pro_BI) |
| Server state | TanStack Query |
| Forms | React Hook Form + Zod |
| Skills | `frontend-architect`, `create-next-screen` |

Estado da decisão: ver [adr/002-frontend-react-next.md](./adr/002-frontend-react-next.md).

## Convenções obrigatórias

### Feature First

Código agrupado por capacidade de negócio (`auth`, `datasets`, `billing`, …). Cada feature expõe uma API pública mínima via `index.ts`. Rotas (`app/` ou Angular routes) ficam finas.

### Atomic Design

| Nível | Responsabilidade | Exemplo |
|-------|------------------|---------|
| Atoms | Primitivos UI | Button, Input, Badge |
| Molecules | Combinações simples | SearchField, QuotaBar |
| Organisms | Blocos de ecrã | DatasetTable, ShellNav |
| Templates | Layouts | AdminShell, AuthLayout |
| Pages | Composição + dados | DatasetsPage |

### Reutilização

- Proibido duplicar markup/comportamento já existente.
- Após o 2.º uso, extrair para `shared/ui` ou `packages/ui`.
- Aceleradores OSS (shadcn, etc.) só como implementação interna — UX final sem marcas externas.

### Rendering & performance

1. Preferir Server Components / SSR para dados e layout.
2. Client Components apenas para estado, eventos e APIs do browser.
3. Lazy loading e code splitting por rota/feature.
4. Evitar `"use client"` no root sem necessidade.

### Qualidade por componente

Cada componente deve incluir:

1. **Props tipadas** (TypeScript; sem `any`).
2. **Documentação** (JSDoc no export público).
3. **Exemplo de uso** (`@example` ou story).
4. **Testes** mínimos (render + caminho crítico ou estados vazios/erro).

Cada ecrã deve tratar: **loading**, **erro**, **vazio**, **sucesso**. Ecrãs administrativos devem mostrar o **tenant actual**.

## Fronteiras

```text
Browser UI  →  API (contratos)  →  Domain / Services
     ↑                ↑
  Zod (UX)      Auth + tenant + RBAC (fonte da verdade)
```

- Não embutir regras críticas de billing/RBAC só no frontend.
- `tenant_id` nunca é confiado a partir do body/query sem sessão validada.
- Contratos partilhados em `packages/contracts` (impacto documentado antes de mudar).

## Mapa de pastas (alvo Next.js)

```text
features/<feature>/{api,components,hooks,schemas,types,index.ts}
shared/ui/{atoms,molecules,organisms}
shared/{lib,hooks,config}
app/…/page.tsx          # composição de rotas
```

## Relação com Angular actual

Enquanto `apps/web` for Angular:

- Manter separação layout / estado / serviços / componentes.
- Aplicar Feature-First e Atomic Design na organização de pastas sempre que possível.
- Componentes partilhados em `apps/web/src/app/shared` e evolução de `packages/ui`.
- Novos ecrãs: skill `create-angular-screen` + checklist frontend.
- Migração React/Next: apenas após aceite do ADR-002 e plano por feature (sem big-bang).

## Checklists e agentes

- Checklist: [CHECKLISTS/frontend-checklist.md](./CHECKLISTS/frontend-checklist.md)
- Agente: [AGENTS.md](./AGENTS.md) § Frontend Architect
- Regras Cursor: `.cursor/rules/03-frontend.mdc`
