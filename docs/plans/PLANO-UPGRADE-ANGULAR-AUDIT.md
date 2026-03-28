# Plano — Upgrade Angular e redução de `npm audit` (apps/web)

## Contexto

`npm audit` em `apps/web` reporta vulnerabilidades **high** em cadeias transitivas (`tar`, `serialize-javascript`) ligadas a `@angular/cli` e `@angular-devkit/build-angular`. O `npm audit fix` sem `--force` **não** as resolve; o npm sugere saltar para **Angular 21.x**, o que é **major** com breaking changes.

## Objectivo

Reduzir ou eliminar avisos **high** sem comprometer estabilidade do produto, mantendo `ng build`, `typecheck` e smoke E2E verdes.

## Fases sugeridas

### Fase A — Manter major 19 (feito incrementalmente)

- Alinhar todas as dependências `@angular/*` e `@angular-devkit/*` à **mesma patch publicada** (em v19.2.x o último patch do *framework* costuma ser `19.2.20`; CLI/build-kit na mesma linha evita avisos de peer).
- Rever `npm audit` após cada bump de patch; muitas CVEs só desaparecem em majors novos.

### Fase B — Major 20 (intermediário)

- Abrir [Angular Update Guide](https://angular.dev/update-guide) (19 → 20) e num **branch dedicado** em `apps/web` correr `npx @angular/cli@20 update @angular/core@20 @angular/cli@20` (rever diff antes de merge; não há `--dry-run` fiável em todas as versões do CLI).
- Quando a equipa tiver janela: `ng update @angular/core@20 @angular/cli@20` (seguir guia oficial e release notes).
- Correr: `npm run typecheck`, `npm run build`, `./scripts/run-qa-gates.sh`, smoke Playwright com `.env.e2e`.

### Fase C — Major 21+ (alinhado ao `audit fix --force` sugerido)

- Repetir `ng update` até linha estável desejada.
- Validar: rotas, standalone components, i18n, budgets de bundle, proxy dev.

## Critérios de aceite (cada fase)

- [ ] `npm run typecheck` e `npm run build` sem erros.
- [ ] `pytest apps/api/tests` inalterado (API não depende do major Angular).
- [ ] E2E: pelo menos `./scripts/run-e2e-api-smoke-local.sh`; com stack, login + RBAC conforme `e2e/README.md`.
- [ ] Documentar em `CHANGELOG.md` ou release interna a versão Angular alvo.

## Riscos

- Regressões de template strict ou APIs deprecadas entre majors.
- Ferramentas de terceiros (futuras) acopladas à versão do Angular.

## Dono sugerido

- **Frente 5 (Frontend)** com revisão **Frente 5 (QA)** nos gates acima.
