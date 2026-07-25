# Design System 4Pro_BI

Fonte de verdade visual da plataforma. **Reutilizar sempre; nunca inventar componente único por ecrã.**

Agente/skill: [Design System Engineer](../.cursor/agents/design-system-engineer.md) · [SKILL](../.cursor/skills/design-system-engineer/SKILL.md)

---

## 1. Princípios

1. **Reuso primeiro** — procurar `.da-*`, tokens `--da-*` e `apps/web/src/app/shared/` antes de criar UI.
2. **Tokens antes de valores** — cores, raios, sombras e espaçamentos vêm de CSS variables.
3. **Uma família visual** — navy + magenta + azul, tipografia Inter/Outfit, shell corporativo.
4. **Estados obrigatórios** — default, hover, focus, disabled, loading, erro, vazio, sucesso.
5. **Acessibilidade** — contraste, foco visível, labels, teclado, `aria-*` quando necessário.
6. **Marca nativa** — experiência **4Pro_BI** (sem marcas de aceleradores OSS na UX).

---

## 2. Tokens

Arquivo: [`packages/ui/scss/_tokens.scss`](../packages/ui/scss/_tokens.scss)  
Importado em [`apps/web/src/styles.scss`](../apps/web/src/styles.scss).

### Cores

| Token | Uso |
|-------|-----|
| `--da-bg-app` | Fundo da aplicação |
| `--da-bg-card` | Superfície de cartão / painel |
| `--da-border` | Bordas neutras |
| `--da-text` / `--da-text-secondary` / `--da-text-muted` | Hierarquia tipográfica |
| `--da-accent` / `--da-accent-hover` / `--da-accent-glow` | Magenta de marca / foco |
| `--da-blue` / `--da-blue-dark` | Azul de apoio / charts |
| `--da-sidebar-*` | Shell lateral escura |
| `--da-success-*` / `--da-danger-text` / `--da-warning-text` | Feedback semântico |
| `--da-chart-head-from/to` | Cabeçalhos de gráfico |

### Tipografia

| Token | Uso |
|-------|-----|
| `--da-font-display` | Títulos (`h1–h3`, `.da-heading`) |
| `--da-font-body` | Corpo (`body`, formulários) |

### Espaçamento

Escala `--da-space-1` … `--da-space-8` (base 4px). Preferir estes tokens em novos estilos.

### Forma

| Token | Uso |
|-------|-----|
| `--da-radius` / `--da-radius-sm` | Cantos de cards / controlos |
| `--da-shadow-card` / `--da-shadow-elevated` | Elevação |
| `--da-focus-ring` | Anel de foco |

### Grid / layout

| Token | Uso |
|-------|-----|
| `--da-shell-aside-width` | Largura da sidebar |
| `--da-content-max` | Largura máxima do conteúdo |

**Boas práticas:** não introduzir hex soltos em templates; se faltar token, adicionar em `_tokens.scss` e documentar aqui.

---

## 3. Inventário de primitives (CSS)

Prefixo global: `.da-*` em `apps/web/src/styles.scss`.

| Área | Classes / padrões | Estados |
|------|-------------------|---------|
| **Shell / menus** | `.da-shell`, `__aside`, `__nav`, `__link`, `__link--active`, `__user`, `__topbar` | hover, active |
| **Cards** | `.da-card`, `__title`, `__sub` | — |
| **Tables** | `.da-table-wrap`, `.da-table`, `.da-table--compact` | hover em linha |
| **Buttons** | `.da-btn`, `--primary`, `--ghost`, `--sso` | hover, active, disabled |
| **Badges** | `.da-pill`, `--uploaded/validating/parsing/processed/failed` | por status de ingestão |
| **Feedback** | `.da-err`, `.da-ok`, `.da-info`, `.da-muted`, `.da-rbac-banner` | erro / sucesso / info |
| **Forms (auth)** | `.da-auth-card form`, `label`, `input` | focus via browser + tokens |
| **Storage / quotas** | `.da-storage*`, aviso ≥90% | warn |
| **Charts (visual)** | tokens `--da-chart-*`, headers em dashboard | — |
| **Modais / Toast / Timeline / Kanban** | *ainda não padronizados* | ver roadmap abaixo |

### Componentes Angular partilhados

| Componente | Path | Notas |
|------------|------|-------|
| `app-storage-quota-block` | `apps/web/src/app/shared/storage-quota-block.component.ts` | Variantes compact/card/dash; export no barrel |

Novos componentes partilhados **devem** ser exportados em `shared/index.ts`.

---

## 4. Exemplos

### Botão primário

```html
<button type="button" class="da-btn da-btn--primary" [disabled]="loading">
  Guardar
</button>
```

### Cartão + tabela

```html
<section class="da-card">
  <h2 class="da-card__title">Ingestões</h2>
  <p class="da-card__sub">Últimos ficheiros do tenant atual.</p>
  <div class="da-table-wrap">
    <table class="da-table">
      <thead>
        <tr>
          <th>Ficheiro</th>
          <th>Estado</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>vendas.csv</td>
          <td><span class="da-pill da-pill--processed">processed</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</section>
```

### Feedback

```html
<p class="da-err" role="alert" *ngIf="error">{{ error }}</p>
<p class="da-ok" role="status" *ngIf="success">{{ success }}</p>
```

Mais exemplos: [`packages/ui/docs/EXAMPLES.md`](../packages/ui/docs/EXAMPLES.md).

---

## 5. Variações e estados

Para **cada** padrão novo, documentar:

| Dimensão | Exemplos |
|----------|----------|
| Variações | primary / ghost / compact / fluid |
| Interação | hover, focus-visible, active |
| Disponibilidade | disabled, loading (aria-busy) |
| Resultado | erro, vazio, sucesso |
| Densidade | default vs `--compact` |

---

## 6. Acessibilidade (mínimo)

- [ ] Contraste texto/fundo ≥ WCAG AA em tokens semânticos
- [ ] Foco visível em controlos interativos (`:focus-visible` / `--da-focus-ring`)
- [ ] Botões e links com nome acessível (texto ou `aria-label`)
- [ ] Formulários: `<label>` associado; erros com `role="alert"`
- [ ] Tabelas com `<th>` e cabeçalhos claros
- [ ] Banners dismissíveis focáveis por teclado
- [ ] Não depender só de cor para estado (badges com texto)

---

## 7. Roadmap do inventário

Padrões a elevar quando a feature chegar (não criar one-off na página):

1. **Modal / dialog** — foco trap, Escape, `role="dialog"`
2. **Toast / snackbar** — fila, aria-live
3. **Inputs / forms** genéricos (fora do auth) — `.da-field`, validação
4. **Timeline** (pipeline de ingestão)
5. **Kanban** (workspace)
6. **Charts** — wrappers partilhados + tokens de série
7. **Ícones** — set SVG único / sprite; tamanhos tokenizados

---

## 8. Como contribuir

1. Abrir chat/agente **Design System Engineer** (ou skill homónima).
2. Validar se já existe padrão.
3. Alterar tokens/primitives/shared + docs + checklist.
4. Frontend (F4) consome; não duplica markup.

Checklist: [`docs/CHECKLISTS/design-system-checklist.md`](./CHECKLISTS/design-system-checklist.md).
