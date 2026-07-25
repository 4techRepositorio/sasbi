---
name: create-angular-screen
description: Cria uma tela Angular completa
---

# Skill: create-angular-screen

Usar para ecrãs em `apps/web` (Angular 19). Para o stack alvo React/Next, usar `frontend-architect` + `create-next-screen` (só após aceite do ADR-002).

## Passos

1. **Confirmar reutilização** — grep em `shared/`, `packages/ui` e páginas existentes; nunca duplicar.
2. **Página/container** — em `pages/<feature>/` (ou `features/<feature>/` se estiver a convergir); rota thin com `loadComponent` em `app.routes.ts`.
3. **Atomic Design** — extrair molecules/organisms para `shared/` no 2.º uso; barrel `shared/index.ts`.
4. **Serviço de API** — em `core/` ou serviço da feature; sem regra crítica de domínio só no template.
5. **Estados de UI** — loading, erro, vazio, sucesso.
6. **Tenant** — ecrãs admin mostram tenant actual (shell / contexto).
7. **Contrato de componente** — inputs tipados + JSDoc + `@example` (+ teste quando runner unitário existir).
8. **Responsividade** — padrão visual corporativo (`--da-*`).
9. **Lazy loading** — rotas e widgets pesados via `loadComponent` / import dinâmico.
10. **Checklist** — `docs/CHECKLISTS/frontend-checklist.md`.

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
- skill `frontend-architect`
- `.cursor/rules/03-frontend.mdc`
