import { DatePipe, JsonPipe } from '@angular/common';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { API_V1 } from '../../core/api-base';

interface TenantAuditLogItem {
  id: string;
  created_at: string;
  action: string;
  actor_user_id: string | null;
  tenant_id: string | null;
  context: Record<string, unknown> | null;
}

interface TenantAuditLogListResponse {
  items: TenantAuditLogItem[];
  limit: number;
  offset: number;
  since_applied: string | null;
}

@Component({
  selector: 'app-tenant-audit-log',
  imports: [DatePipe, FormsModule, JsonPipe],
  template: `
    <section class="da-card">
      <h2 class="da-card__title">Auditoria do tenant</h2>
      <p class="da-card__sub">
        Registo de eventos sensíveis desta organização (apenas administradores). Use o filtro de data para
        exportações incrementais (ex.: integração externa).
      </p>
      <div class="da-toolbar da-toolbar--wrap">
        <label class="da-field">
          <span class="da-field__label">Eventos desde (opcional)</span>
          <input
            type="datetime-local"
            class="da-input"
            [(ngModel)]="sinceLocal"
            [disabled]="loading()"
          />
        </label>
        <div class="da-toolbar__actions">
          <button type="button" class="da-btn da-btn--primary" (click)="applySince()" [disabled]="loading()">
            Aplicar filtro
          </button>
          <button type="button" class="da-btn da-btn--ghost" (click)="clearSince()" [disabled]="loading()">
            Limpar filtro
          </button>
          <button type="button" class="da-btn da-btn--ghost" (click)="reload()" [disabled]="loading()">
            Atualizar
          </button>
          <button
            type="button"
            class="da-btn da-btn--ghost"
            data-testid="tenant-audit-export-csv"
            (click)="exportCsv()"
            [disabled]="loading() || exporting()"
          >
            Exportar CSV
          </button>
        </div>
      </div>
      @if (sinceIso()) {
        <p class="da-muted da-since-hint">
          Filtro activo: API <code>since</code> = {{ sinceIso() }}
          @if (lastResponse()?.since_applied) {
            <span> (confirmado na resposta)</span>
          }
        </p>
      }
      <div class="da-pagination" role="navigation" aria-label="Paginação">
        <button
          type="button"
          class="da-btn da-btn--ghost"
          (click)="prevPage()"
          [disabled]="loading() || offset() === 0"
        >
          Anterior
        </button>
        <span class="da-pagination__meta"
          >{{ offset() + 1 }}–{{ offset() + rows().length }} · limite {{ pageSize }}</span
        >
        <button
          type="button"
          class="da-btn da-btn--ghost"
          (click)="nextPage()"
          [disabled]="loading() || !canGoNext()"
        >
          Seguinte
        </button>
      </div>
      @if (loading()) {
        <p class="da-muted">A carregar…</p>
      } @else if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
      } @else if (!rows().length) {
        <p class="da-muted">Nenhum evento nesta página.</p>
      } @else {
        <div class="da-table-wrap da-table-wrap--wide">
          <table class="da-table da-table--compact">
            <thead>
              <tr>
                <th>Quando</th>
                <th>Acção</th>
                <th>Actor</th>
                <th>Contexto</th>
              </tr>
            </thead>
            <tbody>
              @for (r of rows(); track r.id) {
                <tr>
                  <td class="da-cell-date">{{ r.created_at | date: 'medium' }}</td>
                  <td><code class="da-code-action">{{ r.action }}</code></td>
                  <td class="da-cell-mono">{{ r.actor_user_id ?? '—' }}</td>
                  <td class="da-cell-context">
                    @if (r.context && objectKeys(r.context).length) {
                      <pre class="da-pre">{{ r.context | json }}</pre>
                    } @else {
                      <span class="da-muted">—</span>
                    }
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      }
    </section>
  `,
  styles: [
    `
      .da-toolbar--wrap {
        flex-wrap: wrap;
        gap: 1rem;
        align-items: flex-end;
      }
      .da-toolbar__actions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
      }
      .da-field {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
      }
      .da-field__label {
        font-size: 0.8rem;
        color: var(--da-text-secondary);
      }
      .da-input {
        min-width: 12rem;
        padding: 0.45rem 0.6rem;
        border-radius: 6px;
        border: 1px solid var(--da-border);
        background: var(--da-surface);
        color: var(--da-text);
      }
      .da-since-hint {
        font-size: 0.85rem;
        margin-top: 0.25rem;
      }
      .da-since-hint code {
        font-size: 0.8rem;
      }
      .da-pagination {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 1rem 0;
        flex-wrap: wrap;
      }
      .da-pagination__meta {
        font-size: 0.88rem;
        color: var(--da-text-secondary);
      }
      .da-table--compact td {
        vertical-align: top;
        font-size: 0.88rem;
      }
      .da-cell-mono {
        font-family: ui-monospace, monospace;
        font-size: 0.8rem;
        word-break: break-all;
        max-width: 10rem;
      }
      .da-code-action {
        font-size: 0.78rem;
        word-break: break-word;
      }
      .da-cell-context {
        max-width: 24rem;
      }
      .da-pre {
        margin: 0;
        font-size: 0.72rem;
        white-space: pre-wrap;
        word-break: break-word;
        max-height: 6rem;
        overflow: auto;
        padding: 0.35rem;
        border-radius: 4px;
        background: rgba(0, 0, 0, 0.2);
      }
    `,
  ],
})
export class TenantAuditLogComponent implements OnInit {
  private readonly http = inject(HttpClient);

  readonly pageSize = 25;

  readonly rows = signal<TenantAuditLogItem[]>([]);
  readonly loading = signal(true);
  readonly exporting = signal(false);
  readonly error = signal<string | null>(null);
  readonly offset = signal(0);
  readonly sinceIso = signal<string | null>(null);
  /** Valor ligado ao &lt;input datetime-local&gt; (hora local). */
  sinceLocal: string | null = null;
  readonly lastResponse = signal<TenantAuditLogListResponse | null>(null);

  ngOnInit(): void {
    this.reload();
  }

  objectKeys(obj: Record<string, unknown>): string[] {
    return Object.keys(obj);
  }

  applySince(): void {
    if (!this.sinceLocal) {
      this.sinceIso.set(null);
    } else {
      const d = new Date(this.sinceLocal);
      if (Number.isNaN(d.getTime())) {
        this.error.set('Data/hora inválida.');
        return;
      }
      this.sinceIso.set(d.toISOString());
    }
    this.offset.set(0);
    this.reload();
  }

  clearSince(): void {
    this.sinceLocal = null;
    this.sinceIso.set(null);
    this.offset.set(0);
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.error.set(null);
    let params = new HttpParams().set('limit', String(this.pageSize)).set('offset', String(this.offset()));
    const since = this.sinceIso();
    if (since) {
      params = params.set('since', since);
    }
    this.http.get<TenantAuditLogListResponse>(`${API_V1}/tenant/audit-log`, { params }).subscribe({
      next: (res) => {
        this.lastResponse.set(res);
        this.rows.set(res.items ?? []);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.error.set('Não foi possível carregar a auditoria ou permissão insuficiente.');
      },
    });
  }

  canGoNext(): boolean {
    return this.rows().length >= this.pageSize;
  }

  prevPage(): void {
    const nextOff = Math.max(0, this.offset() - this.pageSize);
    this.offset.set(nextOff);
    this.reload();
  }

  nextPage(): void {
    if (!this.canGoNext()) {
      return;
    }
    this.offset.set(this.offset() + this.pageSize);
    this.reload();
  }

  exportCsv(): void {
    this.exporting.set(true);
    this.error.set(null);
    let params = new HttpParams().set('max_rows', '5000');
    const since = this.sinceIso();
    if (since) {
      params = params.set('since', since);
    }
    this.http
      .get(`${API_V1}/tenant/audit-log/export.csv`, {
        params,
        responseType: 'blob',
        observe: 'response',
      })
      .subscribe({
        next: (res) => {
          this.exporting.set(false);
          const blob = res.body;
          if (!blob || blob.size === 0) {
            this.error.set('Exportação vazia ou inválida.');
            return;
          }
          const cd = res.headers.get('Content-Disposition');
          let filename = 'tenant-audit-export.csv';
          const m = cd?.match(/filename="?([^";]+)"?/i);
          if (m?.[1]) {
            filename = m[1].trim();
          }
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          a.click();
          URL.revokeObjectURL(url);
        },
        error: () => {
          this.exporting.set(false);
          this.error.set('Não foi possível exportar (permissão ou rede).');
        },
      });
  }
}
