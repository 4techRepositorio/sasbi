import { DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';
import {
  DashboardItem,
  DashboardsService,
  DashboardStatus,
} from '../../core/dashboards.service';
import { canEditBi, roleFromContext } from '../../core/rbac';
import { TenantContextService } from '../../core/tenant-context.service';

@Component({
  selector: 'app-dashboards-list',
  imports: [DatePipe, FormsModule, RouterLink],
  template: `
    <section class="da-card">
      <div class="da-page-head">
        <div>
          <h2 class="da-card__title">Dashboards</h2>
          <p class="da-card__sub">
            Biblioteca de dashboards do tenant — rascunhos e publicados.
          </p>
        </div>
        <div class="da-page-head__actions">
          <label class="da-filter">
            <span>Estado</span>
            <select [(ngModel)]="statusFilter" (ngModelChange)="reload()">
              <option value="">Todos</option>
              <option value="draft">Rascunho</option>
              <option value="published">Publicado</option>
              <option value="archived">Arquivado</option>
            </select>
          </label>
          <button type="button" class="da-btn da-btn--ghost" (click)="reload()" [disabled]="loading()">
            Atualizar
          </button>
          @if (canEdit()) {
            <button type="button" class="da-btn da-btn--primary" (click)="createNew()" [disabled]="creating()">
              {{ creating() ? 'A criar…' : 'Novo dashboard' }}
            </button>
          }
        </div>
      </div>

      @if (actionOk()) {
        <p class="da-inline-ok" role="status">{{ actionOk() }}</p>
      }
      @if (actionErr()) {
        <p class="da-err" role="alert">{{ actionErr() }}</p>
      }

      @if (loading()) {
        <p class="da-muted">A carregar dashboards…</p>
      } @else if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
      } @else if (!rows().length) {
        <div class="da-empty">
          <p class="da-muted">Ainda não há dashboards neste tenant.</p>
          @if (canEdit()) {
            <button type="button" class="da-btn da-btn--primary" (click)="createNew()">
              Criar primeiro dashboard
            </button>
          }
        </div>
      } @else {
        <p class="da-meta">{{ rows().length }} dashboard(s)</p>
        <div class="da-dash-cards">
          @for (d of rows(); track d.id) {
            <article class="da-dash-card">
              <div class="da-dash-card__top">
                <h3>{{ d.name }}</h3>
                <span [class]="statusPill(d.status)">{{ statusLabel(d.status) }}</span>
              </div>
              <p class="da-dash-card__desc">{{ d.description || 'Sem descrição' }}</p>
              <p class="da-dash-card__meta">
                v{{ d.version }} · {{ d.layout.widgets.length }} widget(s) ·
                {{ d.updated_at | date: 'short' }}
              </p>
              <div class="da-dash-card__actions">
                <a [routerLink]="['/app/dashboards', d.id]" class="da-btn da-btn--ghost da-btn--sm">
                  {{ canEdit() && d.status !== 'published' ? 'Editar' : 'Abrir' }}
                </a>
                @if (canEdit() && d.status === 'draft') {
                  <button
                    type="button"
                    class="da-btn da-btn--primary da-btn--sm"
                    (click)="publish(d)"
                    [disabled]="publishingId() === d.id"
                  >
                    Publicar
                  </button>
                }
              </div>
            </article>
          }
        </div>
      }
    </section>
  `,
  styles: [
    `
      .da-page-head {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.5rem;
      }
      .da-page-head__actions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        align-items: flex-end;
      }
      .da-filter {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        font-size: 0.78rem;
        color: var(--da-text-secondary);
      }
      .da-filter select {
        padding: 0.4rem 0.55rem;
        border-radius: var(--da-radius-sm);
        border: 1px solid var(--da-border);
        font-family: inherit;
      }
      .da-empty {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        align-items: flex-start;
      }
      .da-inline-ok {
        margin: 0 0 0.75rem;
        padding: 0.5rem 0.75rem;
        border-radius: var(--da-radius-sm);
        background: var(--da-success-bg);
        color: var(--da-success-text);
        font-size: 0.88rem;
      }
      .da-dash-cards {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 1rem;
        margin-top: 0.75rem;
      }
      .da-dash-card {
        padding: 1.1rem 1.2rem;
        border: 1px solid var(--da-border);
        border-radius: var(--da-radius);
        background: #fff;
        box-shadow: var(--da-shadow-card);
        display: flex;
        flex-direction: column;
        gap: 0.45rem;
      }
      .da-dash-card__top {
        display: flex;
        justify-content: space-between;
        gap: 0.5rem;
        align-items: flex-start;
      }
      .da-dash-card__top h3 {
        margin: 0;
        font-size: 1.05rem;
        font-family: var(--da-font-display);
      }
      .da-dash-card__desc {
        margin: 0;
        font-size: 0.88rem;
        color: var(--da-text-secondary);
        min-height: 2.4em;
      }
      .da-dash-card__meta {
        margin: 0;
        font-size: 0.78rem;
        color: var(--da-text-muted);
      }
      .da-dash-card__actions {
        display: flex;
        gap: 0.4rem;
        margin-top: 0.35rem;
        flex-wrap: wrap;
      }
      .da-btn--sm {
        padding: 0.35rem 0.7rem;
        font-size: 0.8rem;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
      }
    `,
  ],
})
export class DashboardsListComponent implements OnInit {
  private readonly api = inject(DashboardsService);
  private readonly auth = inject(AuthService);
  private readonly tenantCtx = inject(TenantContextService);
  private readonly router = inject(Router);

  statusFilter = '';
  readonly rows = signal<DashboardItem[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly actionOk = signal<string | null>(null);
  readonly actionErr = signal<string | null>(null);
  readonly creating = signal(false);
  readonly publishingId = signal<string | null>(null);

  readonly canEdit = computed(() =>
    canEditBi(roleFromContext(this.tenantCtx.context(), this.auth.tenantRole())),
  );

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.error.set(null);
    const status = (this.statusFilter || undefined) as DashboardStatus | undefined;
    this.api.list({ limit: 100, offset: 0, status }).subscribe({
      next: (data) => {
        this.rows.set(data.items);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.error.set('Não foi possível carregar os dashboards.');
      },
    });
  }

  statusLabel(s: DashboardStatus): string {
    const map: Record<DashboardStatus, string> = {
      draft: 'rascunho',
      published: 'publicado',
      archived: 'arquivado',
    };
    return map[s] ?? s;
  }

  statusPill(s: DashboardStatus): string {
    switch (s) {
      case 'published':
        return 'da-pill da-pill--processed';
      case 'draft':
        return 'da-pill da-pill--uploaded';
      case 'archived':
        return 'da-pill';
      default: {
        const _exhaustive: never = s;
        return _exhaustive;
      }
    }
  }

  createNew(): void {
    this.creating.set(true);
    this.actionErr.set(null);
    this.api
      .create({
        name: 'Novo dashboard',
        description: '',
        layout: { version: 1, columns: 12, widgets: [] },
      })
      .subscribe({
        next: (d) => {
          this.creating.set(false);
          void this.router.navigate(['/app/dashboards', d.id]);
        },
        error: (err: HttpErrorResponse) => {
          this.creating.set(false);
          this.actionErr.set(this.httpMsg(err, 'Falha ao criar dashboard.'));
        },
      });
  }

  publish(d: DashboardItem): void {
    this.publishingId.set(d.id);
    this.api.publish(d.id).subscribe({
      next: () => {
        this.publishingId.set(null);
        this.actionOk.set(`«${d.name}» publicado.`);
        this.reload();
      },
      error: (err: HttpErrorResponse) => {
        this.publishingId.set(null);
        this.actionErr.set(this.httpMsg(err, 'Falha ao publicar.'));
      },
    });
  }

  private httpMsg(err: HttpErrorResponse, fallback: string): string {
    if (err.error && typeof err.error === 'object' && 'detail' in err.error) {
      const detail = (err.error as { detail: unknown }).detail;
      if (typeof detail === 'string') {
        return detail;
      }
    }
    return fallback;
  }
}
