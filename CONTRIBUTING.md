# Contribuir no 4Pro_BI

## Antes de abrir PR

1. **Arquitectura** (features novas / mudanças estruturais): validar [`docs/architecture/BLUEPRINT.md`](docs/architecture/BLUEPRINT.md) e preencher [`docs/CHECKLISTS/architecture-checklist.md`](docs/CHECKLISTS/architecture-checklist.md).
2. **Gates locais** (paridade com CI): `./scripts/run-qa-gates.sh` ou `make qa`.
3. **Opcional — Alembic em Postgres Docker** (igual ao job `alembic-postgres`): `make alembic-pg-local` ou `RUN_ALEMBIC_PG_LOCAL=1 make qa`.
4. **Pre-commit** (opcional): `pip install pre-commit && pre-commit install` — Ruff na API.

## Frentes e ficheiros (resumo)

O repositório usa **ownership por pastas** (ver `docs/plans/PROMPTS-CHATS-CURSOR.md`, `docs/architecture/BLUEPRINT.md` e `docs/ARCHITECTURE.md`):

- **Contratos** — `packages/contracts` (coordenar impacto em clientes).
- **Core API** — auth, tenant, billing, `me`, `health`; **não** ingestions/uploads sem coordenação.
- **Data API** — uploads, ingestions, datasets, jobs; **não** alterar `main.py` sem PR Core.
- **Web** — só `apps/web/`.
- **QA / CI** — `apps/api/tests`, `docs/CHECKLISTS/`, `.github/workflows/`, `e2e/`.

## Migrações

- Core: ficheiros Alembic com prefixo `core__` no nome; dados: `data__`.
- Uma única **head**; o CI valida com Postgres vazio.

## Commits e PRs

- Mensagens claras; PRs pequenos facilitam revisão.
- Descrever riscos e passos de deploy se houver migração ou alteração de contrato.
- Ao abrir PR no GitHub, usa o modelo em [`.github/pull_request_template.md`](.github/pull_request_template.md) (checklist automática).

## Issues e propriedade de código

- Modelos em [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/) (com `labels` no frontmatter). Na primeira vez, corre **Actions → Sync issue labels → Run workflow** ([`sync-labels.yml`](.github/workflows/sync-labels.yml)) para criar `bug`, `triage` e `enhancement` no repositório.
- [`.github/ISSUE_TEMPLATE/config.yml`](.github/ISSUE_TEMPLATE/config.yml) — `contact_links` (ex.: link ao `docs/SECURITY.md` do teu fork via URL absoluta no GitHub).
- [`.github/CODEOWNERS`](.github/CODEOWNERS) — hoje só com comentários e exemplos; descomente e atribua `@org/equipa` quando existirem equipas no GitHub.

## Dependabot

O repositório inclui [`.github/dependabot.yml`](.github/dependabot.yml) (npm em `apps/web` e `e2e`, pip em `apps/api`, `apps/worker`, `packages/contracts`, `packages/shared`, e **GitHub Actions** mensal). Revisar PRs automáticos com especial atenção a major versions (Angular, etc.).

## Problemas com `npm ci` (`ENOTEMPTY`)

Em alguns ambientes (NFS, contentores, I/O concorrente), apagar `node_modules` pode falhar. Tente:

```bash
cd apps/web
chmod -R u+w node_modules 2>/dev/null || true
find node_modules -mindepth 1 -delete 2>/dev/null || rm -rf node_modules
npm ci
```

Se persistir, `npm install` (sem apagar `package-lock.json`) pode reparar a árvore antes de voltar a `npm ci`.

## Wireframes (PDF e capturas)

- **PDF → PNG:** `make wireframes-export` ou `bash scripts/export-wireframes-from-pdf.sh` (dependência: `poppler-utils`). Saída: `docs/assets/wireframes/exports/`.
- **Capturas da app** (para folhas `docs/wireframes/validation-*.md`): com o front no ar e `e2e/.env.e2e` configurado (`E2E_USER_*` = **admin** sem MFA), `cd e2e && E2E_WIREFRAME_CAPTURES=1 npm run test:wireframe-captures` — ver `e2e/README.md`.
