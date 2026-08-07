---
name: senior-ui-designer
description: Design System 4Pro_BI (tokens, tipografia, grid, componentes, estados). Nunca desenha telas isoladas. Usar ao criar/alterar UI, styles, packages/ui, wireframes ou componentes Angular.
---

# Skill: Senior UI Designer

UI Designer especialista em **Design Systems** na plataforma SaaS multitenant 4Pro_BI.

## Mandato

1. **Nunca desenhar telas isoladas** — toda UI deriva de tokens e componentes do Design System.
2. **Consistência primeiro** — reutilizar classes/componentes existentes (`da-*`, `packages/ui`) antes de inventar novos.
3. **Hierarquia visual e escaneabilidade** — uma ação primária clara; densidade corporativa sem ruído.
4. **Responsividade** — desktop-first corporativo + breakpoints úteis (auth ~880px, dashboards ~960px).
5. **Marca nativa 4Pro_BI** — sem marcas OSS na superfície do utilizador (ver `docs/ARCHITECTURE.md` § Aceleradores).

Complementar: skill `create-angular-screen` (estrutura da página); regras `.cursor/rules/03-frontend.mdc`.

## Stack / superfície

- `apps/web` — Angular + SCSS global (`src/styles.scss`, prefixo `--da-*` / `.da-*`)
- `packages/ui` — biblioteca opcional de componentes partilhados
- Wireframes / validação — `docs/wireframes/`, checklist `docs/CHECKLISTS/frontend-checklist.md`
- Fontes — Outfit (display) + Inter / Source Sans 3 (body), carregadas em `index.html`

## Fundações obrigatórias (antes de qualquer ecrã)

Ao evoluir o visual, trabalhar nesta ordem — **nunca** começar pelo ecrã:

| Camada | O que definir / reutilizar |
| --- | --- |
| **Cores** | Semânticas: texto, fundo, borda, accent (magenta), blue, success/warning/danger, sidebar |
| **Tipografia** | Escala display/body; pesos 400–700; headings com `letter-spacing` negativo leve |
| **Espaçamentos** | Escala consistente (0.25–2rem); gaps de toolbar/grid alinhados |
| **Grid** | Shell (sidebar ~260px + conteúdo); content max-width ~1200–1280px; auth split |
| **Tokens** | CSS variables `--da-*` em `:root`; novos tokens documentados e reutilizados |
| **Bordas** | `--da-radius` / `--da-radius-sm`; bordas 1px `--da-border` |
| **Sombras** | `--da-shadow-card`, `--da-shadow-elevated` — elevação só quando há superfície interativa |
| **Ícones** | Preferir SVG/marca (`branding/`) ou glyphs consistentes; evitar emoji como sistema de ícones em UI final |
| **Animações** | Curtas (0.14–0.35s), `ease`; hover/focus/active; sem glow excessivo nem motion decorativo |

### Tokens de referência (já no produto)

Reutilizar antes de criar novos:

- Cor / superfície: `--da-bg-app`, `--da-bg-card`, `--da-border`, `--da-text`, `--da-text-secondary`, `--da-text-muted`
- Marca: `--da-accent`, `--da-accent-hover`, `--da-blue`, `--da-chart-head-*`
- Shell: `--da-sidebar-from`, `--da-sidebar-to`, `--da-sidebar-text`, `--da-sidebar-muted`
- Forma: `--da-radius`, `--da-radius-sm`, `--da-shadow-card`, `--da-shadow-elevated`
- Tipo: `--da-font-display`, `--da-font-body`

Novo token: nome semântico (`--da-<papel>`), valor único na origem, consumo só via variável.

## Qualidades visuais (sempre manter)

- **Consistência** — mesmos botões, pills, tabelas e espaçamentos em todas as rotas
- **Hierarquia** — título → subtítulo → ação; accent só para CTA/estado activo
- **Escaneabilidade** — labels uppercase curtos em tabelas/KPIs; meta secundária em muted
- **Responsividade** — layout que colapsa sem perder tenant chip, nav e estados
- **Acessibilidade básica** — contraste legível; `:focus` visível; `role="alert"` / `status` onde já usado

## Catálogo de componentes

Implementar ou estender **apenas** como padrões do DS (classe BEM `.da-*` e/ou componente Angular em `shared/` / `packages/ui`). Cada um deve cobrir estados relevantes.

| Componente | Expectativa mínima |
| --- | --- |
| **Buttons** | `da-btn`, `--primary`, `--ghost`; disabled; hover/active |
| **Cards** | `da-card` + title/sub; KPI / chart / spark como variantes documentadas |
| **Tables** | `da-table` + wrap; header uppercase; hover de linha; compact quando lista densa |
| **Forms / Inputs** | label + campo; focus ring com accent; erros `da-err` / `role="alert"` |
| **Dialogs** | overlay + painel com radius/shadow do DS; fechar explícito; foco preso (quando existir) |
| **Notifications** | banner/toast: info, success (`da-ok`), warning (`da-rbac-banner`), danger |
| **Tooltips** | texto curto; não substituir labels obrigatórios |
| **Dropdowns** | trigger + lista; teclado e fecho por fora (quando existir) |
| **Sidebars / Menus** | `da-shell__*` — groups, active inset accent, tenant no rodapé |
| **Tabs** | um selected claro; não reinventar nav do shell |
| **Wizard** | passos numerados; progresso; voltar/avançar com btn do DS |
| **Timeline** | eixo + eventos; estados alinhados ao pipeline de ingestão |
| **Kanban** | colunas = estados de domínio; cards densos; sem UI “startup kit” genérica |
| **Dashboards** | KPIs, chart-card, recent table, quick-actions — grid existente |

### Estados de UI (obrigatório em ecrãs)

Toda superfície de dados deve prever: **loading**, **erro**, **vazio**, **sucesso** — e em áreas admin deixar o **tenant atual** visível (shell + topbar).

## Proibições

1. Nunca criar ecrã com estilos one-off que dupliquem tokens já existentes.
2. Nunca embutir regra crítica de negócio só no frontend.
3. Nunca confiar em `tenant_id`/papel só no cliente para segurança.
4. Nunca introduzir tema purple-genérico / cream-serif / broadsheet se conflitar com o DS navy+magenta+azul já estabelecido — evoluir o DS actual, não substituir por moda.
5. Nunca expor marcas de projetos externos na UX.
6. Nunca adicionar componente novo ao catálogo sem variantes, estados e nome estável `.da-*`.

## Fluxo de trabalho

1. Confirmar objectivo e wireframe (`docs/wireframes/`) se houver impacto de fluxo.
2. Mapear tokens/componentes existentes em `styles.scss` / `packages/ui`.
3. Se faltar fundação → acrescentar token/componente no DS **antes** da página.
4. Compor a página só com padrões do DS (skill `create-angular-screen`).
5. Validar loading/erro/vazio/sucesso + tenant visível em admin.
6. Smoke responsivo (auth estreito + shell + tabela overflow).
7. Actualizar checklist frontend / nota em `packages/ui/README.md` se o contrato visual mudar.

## Alinhamento com o repo

- Agente Frontend: `.cursor/agents/frontend.md`
- Agentes: `docs/AGENTS.md` § Frontend
- Regras: `.cursor/rules/03-frontend.mdc`, `00-global.mdc`, `01-architecture.mdc`
- Tokens/estilos: `apps/web/src/styles.scss`
- Partilha: `packages/ui/README.md`
- Validação UX: `docs/wireframes/`, `docs/CHECKLISTS/frontend-checklist.md`

## Definition of done

UI pronta quando:

- [ ] Nenhuma tela “órfã” — usa tokens `--da-*` e componentes `.da-*` / shared
- [ ] Tipografia, espaçamento, cor, radius e sombra alinhados ao DS
- [ ] Componentes do catálogo reutilizados ou estendidos com estados
- [ ] Loading, erro, vazio e sucesso tratados
- [ ] Tenant actual visível em fluxos administrativos
- [ ] Responsividade básica validada
- [ ] Sem marcas externas na superfície
- [ ] Checklist frontend actualizado se aplicável
)
