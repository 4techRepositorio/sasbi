---
name: create-angular-screen
description: Cria uma tela Angular completa
---

# Skill: create-angular-screen

Usar para ecrãs em `apps/web` (Angular 19). Para o stack alvo React/Next, usar `frontend-architect` + `create-next-screen` (só após aceite do ADR-002).

## Passos

1. **Confirmar reutilização** — grep em `shared/`, `packages/ui` e páginas existentes; nunca duplicar.
2. **Design System** — reutilizar tokens `--da-*`, classes `.da-*` e `shared/` (ver skill `design-system-engineer` e `docs/DESIGN_SYSTEM.md`). Só criar componentes auxiliares de página se não existirem no DS; padrões novos sobem ao DS.
3. **Página/container** — em `pages/<feature>/` (ou `features/<feature>/` se estiver a convergir); rota thin com `loadComponent` em `app.routes.ts`.
4. **Atomic Design** — extrair molecules/organisms para `shared/` no 2.º uso; barrel `shared/index.ts`.
5. **Serviço de API** — em `core/` ou serviço da feature; sem regra crítica de domínio só no template.
6. **Estados de UI** — loading, erro, vazio, sucesso.
7. **Tenant** — ecrãs admin mostram tenant actual (shell / contexto).
8. **Contrato de componente** — inputs tipados + JSDoc + `@example` (+ teste quando runner unitário existir).
9. **Responsividade** — padrão visual corporativo e limpo (4Pro_BI, `--da-*`).
10. **Lazy loading** — rotas e widgets pesados via `loadComponent` / import dinâmico.
11. **Checklist** — `docs/CHECKLISTS/frontend-checklist.md`.

## Template mínimo

```ts
/**
 * Filtra datasets por nome.
 *
 * @example
 * <app-dataset-search [value]="q" (valueChange)="q = $event" />
 */
@Component({
  selector: 'app-dataset-search',
  standalone: true,
  template: `<!-- ... -->`,
})
export class DatasetSearchComponent {
  readonly value = input.required<string>();
  readonly valueChange = output<string>();
  readonly disabled = input(false);
}
```

## Referências

- `docs/FRONTEND_ARCHITECTURE.md`
- `docs/DESIGN_SYSTEM.md`
- skill `frontend-architect`
- skill `design-system-engineer`
- `.cursor/rules/03-frontend.mdc`
