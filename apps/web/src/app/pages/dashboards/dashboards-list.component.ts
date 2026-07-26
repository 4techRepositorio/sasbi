import { DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { DashboardService, DashboardSummary } from '../../core/dashboard.service';
import { TenantContextService } from '../../core/tenant-context.service';

@Component({
  selector: 'app-dashboards-list',
  imports: [DatePipe, FormsModule, RouterLink],
  template: `
    <section class="da-card">
      <div class="da-card__head">
        <div>
          <h2 class="da-card__title">Dashboards</h2>
          <p class="da-card__sub">
            Canvas do workspace no tenant
            <strong>{{ tenantLabel() }}</strong> — widgets ligados ao catálogo.
          </p>
        </div>
        @if (canEdit()) {
          <form class="da-inline-form" (ngSubmit)="create()">
            <input
              class="da-input"
              name="title"
              [(ngModel)]="newTitle"
              placeholder="Novo dashboard"
              required
            />
            <button class="da-btn" type="submit" [disabled]="creating() || !newTitle.trim()">
              Criar
            </button>
          </form>
        }
      </div>

      @if (loading()) {
        <p class="da-muted">A carregar…</p>
      } @else if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
      } @else if (!rows().length) {
        <p class="da-muted">Ainda não há dashboards. Crie o primeiro para começar o workspace BI.</p>
      } @else {
        <ul class="da-list">
          @for (d of rows(); track d.id) {
            <li class="da-list__item">
              <a [routerLink]="['/app/dashboards', d.id]" class="da-list__link">
                <span class="da-list__title">{{ d.title }}</span>
                <span class="da-meta">{{ d.widget_count }} widgets · {{ d.updated_at | date: 'short' }}</span>
              </a>
            </li>
          }
        </ul>
      }
    </section>
  `,
  styles: [
    `
      .da-card__head {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
      }
      .da-inline-form {
        display: flex;
        gap: 0.5rem;
        align-items: center;
      }
      .da-list {
        list-style: none;
        margin: 0;
        padding: 0;
      }
      .da-list__item + .da-list__item {
        border-top: 1px solid var(--da-border, #e5e7eb);
      }
      .da-list__link {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        padding: 0.85rem 0;
        text-decoration: none;
        color: inherit;
      }
      .da-list__title {
        font-weight: 600;
      }
    `,
  ],
})
export class DashboardsListComponent implements OnInit {
  private readonly api = inject(DashboardService);
  private readonly tenantCtx = inject(TenantContextService);

  readonly rows = signal<DashboardSummary[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly creating = signal(false);
  newTitle = '';

  tenantLabel(): string {
    const ctx = this.tenantCtx.context();
    return ctx?.tenant_name ?? ctx?.tenant_slug ?? ctx?.tenant_id ?? '—';
  }

  canEdit(): boolean {
    const role = this.tenantCtx.context()?.role;
    return role === 'admin' || role === 'analyst';
  }

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.list().subscribe({
      next: (res) => {
        this.rows.set(res.items);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Não foi possível carregar os dashboards.');
        this.loading.set(false);
      },
    });
  }

  create(): void {
    const title = this.newTitle.trim();
    if (!title) {
      return;
    }
    this.creating.set(true);
    this.api.create({ title, widgets: [] }).subscribe({
      next: () => {
        this.newTitle = '';
        this.creating.set(false);
        this.reload();
      },
      error: () => {
        this.error.set('Não foi possível criar o dashboard.');
        this.creating.set(false);
      },
    });
  }
}
