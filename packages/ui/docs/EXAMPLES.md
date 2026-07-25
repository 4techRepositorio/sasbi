# Exemplos — Design System 4Pro_BI

Complementa [`docs/DESIGN_SYSTEM.md`](../../docs/DESIGN_SYSTEM.md). Copiar e adaptar; não inventar classes paralelas.

---

## Botões

```html
<!-- Primário (CTA) -->
<button type="submit" class="da-btn da-btn--primary">Entrar</button>

<!-- Secundário -->
<button type="button" class="da-btn da-btn--ghost">Cancelar</button>

<!-- Loading / disabled -->
<button type="button" class="da-btn da-btn--primary" disabled aria-busy="true">
  A processar…
</button>
```

**Boas práticas:** um CTA primário por secção; `type` explícito; disabled durante submit.

---

## Badge / pill (ingestão)

```html
<span class="da-pill da-pill--uploaded">uploaded</span>
<span class="da-pill da-pill--validating">validating</span>
<span class="da-pill da-pill--parsing">parsing</span>
<span class="da-pill da-pill--processed">processed</span>
<span class="da-pill da-pill--failed">failed</span>
```

**A11y:** o texto do estado é obrigatório (não só cor).

---

## Card + meta

```html
<article class="da-card">
  <h2 class="da-card__title">Datasets</h2>
  <p class="da-card__sub">Catálogo do tenant atual.</p>
  <p class="da-meta">Atualizado há 2 min</p>
</article>
```

---

## Form feedback

```html
<label for="email">Email</label>
<input id="email" name="email" type="email" autocomplete="username" />

<p class="da-err" role="alert" *ngIf="errorMsg">{{ errorMsg }}</p>
<p class="da-ok" role="status" *ngIf="okMsg">{{ okMsg }}</p>
<p class="da-muted" *ngIf="!items.length">Nenhum registo.</p>
```

**Estados de ecrã:** loading · erro · vazio · sucesso (regra Frontend).

---

## Quota de armazenamento (componente)

```ts
import { StorageQuotaBlockComponent } from '../shared';
```

```html
<app-storage-quota-block variant="compact" />
```

Variantes: ver componente e checklist frontend.

---

## Shell — link de navegação

```html
<a routerLink="/datasets" class="da-shell__link" routerLinkActive="da-shell__link--active">
  Datasets
</a>
```

Tenant atual deve permanecer visível na shell (chip / meta do utilizador).
