import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { DashboardDetail, DashboardService } from '../../core/dashboard.service';
import { TenantContextService } from '../../core/tenant-context.service';

@Component({
  selector: 'app-dashboard-view',
  imports: [RouterLink],
  template: `
    <section class="da-card">
      <p class="da-meta">
        <a routerLink="/app/dashboards">← Dashboards</a>
        · Tenant {{ tenantLabel() }}
      </p>
      @if (loading()) {
        <p class="da-muted">A carregar…</p>
      } @else if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
      } @else if (dash()) {
        @let d = dash()!;
        <header class="da-dash-head">
          <div>
            <h2 class="da-card__title">{{ d.title }}</h2>
            @if (d.description) {
              <p class="da-card__sub">{{ d.description }}</p>
            }
          </div>
          <button type="button" class="da-btn da-btn--ghost" (click)="exportSnap()">Exportar JSON</button>
        </header>

        @if (!d.widgets.length) {
          <p class="da-muted">Dashboard sem widgets. Adicione KPIs ou tabelas via API / Desktop.</p>
        } @else {
          <div class="da-widgets">
            @for (w of d.widgets; track w.id) {
              <article class="da-widget">
                <h3 class="da-widget__title">{{ w.title }}</h3>
                <p class="da-meta">{{ w.widget_type }}</p>
                @if (w.dataset_id && w.dataset_available === false) {
                  <p class="da-warn" role="status">
                    Dataset indisponível neste tenant — o widget não pode ser renderizado.
                  </p>
                } @else if (w.dataset_id) {
                  <p class="da-muted">Dataset {{ w.dataset_id }}</p>
                } @else {
                  <p class="da-muted">Sem dataset associado</p>
                }
              </article>
            }
          </div>
        }
      }
    </section>
  `,
  styles: [
    `
      .da-dash-head {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        align-items: flex-start;
        margin-bottom: 1.25rem;
      }
      .da-widgets {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 1rem;
      }
      .da-widget {
        border: 1px solid var(--da-border, #e5e7eb);
        border-radius: 8px;
        padding: 1rem;
        background: var(--da-surface, #fff);
      }
      .da-widget__title {
        margin: 0 0 0.35rem;
        font-size: 1rem;
      }
      .da-warn {
        color: var(--da-warning, #b45309);
        margin: 0.5rem 0 0;
      }
    `,
  ],
})
export class DashboardViewComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(DashboardService);
  private readonly tenantCtx = inject(TenantContextService);

  readonly dash = signal<DashboardDetail | null>(null);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  tenantLabel(): string {
    const ctx = this.tenantCtx.context();
    return ctx?.tenant_name ?? ctx?.tenant_slug ?? '—';
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.error.set('Dashboard inválido.');
      this.loading.set(false);
      return;
    }
    this.api.get(id).subscribe({
      next: (d) => {
        this.dash.set(d);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Não foi possível carregar o dashboard.');
        this.loading.set(false);
      },
    });
  }

  exportSnap(): void {
    const d = this.dash();
    if (!d) {
      return;
    }
    this.api.export(d.id).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${d.title || 'dashboard'}.json`;
        a.click();
        URL.revokeObjectURL(url);
      },
      error: () => this.error.set('Exportação falhou.'),
    });
  }
}
