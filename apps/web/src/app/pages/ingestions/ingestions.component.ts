import { DatePipe, DecimalPipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AuthService } from '../../core/auth.service';
import { IngestionDto, IngestionService } from '../../core/ingestion.service';
import { TenantContextService } from '../../core/tenant-context.service';

@Component({
  selector: 'app-ingestions',
  imports: [DatePipe, FormsModule, DecimalPipe],
  template: `
    <section class="da-card">
      <h2 class="da-card__title">Pipeline de ingestão</h2>
      <p class="da-card__sub">
        Histórico e estados: uploaded → validating → parsing → processed / failed (isolado por tenant).
      </p>
      <div class="da-toolbar">
        <label>
          <span>Filtrar por estado</span>
          <select [(ngModel)]="statusFilter" (ngModelChange)="reload()">
            <option value="">Todos</option>
            <option value="uploaded">uploaded</option>
            <option value="validating">validating</option>
            <option value="parsing">parsing</option>
            <option value="processed">processed</option>
            <option value="failed">failed</option>
          </select>
        </label>
        <button type="button" class="da-btn da-btn--ghost" (click)="reload()" [disabled]="loading()">
          Atualizar
        </button>
      </div>
      @if (actionOk()) {
        <p class="da-inline-ok" role="status">{{ actionOk() }}</p>
      }
      @if (actionErr()) {
        <p class="da-err" role="alert">{{ actionErr() }}</p>
      }
      @if (loading()) {
        <p class="da-muted">A carregar…</p>
      } @else if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
      } @else if (!rows().length) {
        <p class="da-muted">Sem ingestões neste tenant.</p>
      } @else {
        <div class="da-table-wrap">
          <table class="da-table">
            <thead>
              <tr>
                <th>Ficheiro</th>
                <th>Estado</th>
                <th>Tamanho</th>
                <th>Resumo</th>
                <th>Erro</th>
                <th>Criado</th>
                @if (canReprocess()) {
                  <th class="da-th-actions">Ações</th>
                }
              </tr>
            </thead>
            <tbody>
              @for (r of rows(); track r.id) {
                <tr>
                  <td>{{ r.original_filename }}</td>
                  <td>
                    <span [class]="pillClass(r.status)">{{ r.status }}</span>
                  </td>
                  <td>{{ r.size_bytes | number }} B</td>
                  <td class="da-cell-summary">{{ r.result_summary ?? '—' }}</td>
                  <td class="da-cell-err">{{ r.friendly_error ?? '—' }}</td>
                  <td class="da-cell-date">{{ r.created_at | date: 'short' }}</td>
                  @if (canReprocess()) {
                    <td class="da-td-actions">
                      @if (reprocessable(r)) {
                        <button
                          type="button"
                          class="da-btn da-btn--ghost da-btn--sm"
                          (click)="reprocess(r)"
                          [disabled]="reprocessingId() === r.id"
                        >
                          {{ reprocessingId() === r.id ? 'A enviar…' : 'Reprocessar' }}
                        </button>
                      } @else {
                        <span class="da-muted da-actions-dash">—</span>
                      }
                    </td>
                  }
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
      .da-cell-err {
        max-width: 180px;
        word-break: break-word;
        color: var(--da-warning-text);
      }
      .da-cell-summary {
        max-width: 200px;
        word-break: break-word;
        font-size: 0.88rem;
        color: var(--da-text-secondary);
      }
      .da-cell-date {
        white-space: nowrap;
        color: var(--da-text-secondary);
      }
      .da-th-actions,
      .da-td-actions {
        width: 1%;
        white-space: nowrap;
        vertical-align: middle;
      }
      .da-btn--sm {
        padding: 0.35rem 0.65rem;
        font-size: 0.8rem;
      }
      .da-actions-dash {
        font-size: 0.85rem;
      }
      .da-inline-ok {
        margin: 0 0 0.75rem;
        padding: 0.5rem 0.75rem;
        border-radius: var(--da-radius-sm);
        background: var(--da-success-bg);
        color: var(--da-success-text);
        font-size: 0.88rem;
      }
    `,
  ],
})
export class IngestionsComponent implements OnInit {
  private readonly ingestionApi = inject(IngestionService);
  private readonly auth = inject(AuthService);
  private readonly tenantCtx = inject(TenantContextService);

  statusFilter = '';
  readonly rows = signal<IngestionDto[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly reprocessingId = signal<string | null>(null);
  readonly actionOk = signal<string | null>(null);
  readonly actionErr = signal<string | null>(null);

  pillClass(status: string): string {
    const mod: Record<string, string> = {
      processed: 'da-pill da-pill--processed',
      failed: 'da-pill da-pill--failed',
      uploaded: 'da-pill da-pill--uploaded',
      parsing: 'da-pill da-pill--parsing',
      validating: 'da-pill da-pill--validating',
    };
    return mod[status] ?? 'da-pill';
  }

  canReprocess(): boolean {
    const r = this.tenantCtx.context()?.role ?? this.auth.tenantRole();
    return r === 'admin' || r === 'analyst';
  }

  reprocessable(r: IngestionDto): boolean {
    return !['validating', 'parsing'].includes(r.status);
  }

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.actionOk.set(null);
    this.actionErr.set(null);
    this.loadRows();
  }

  private loadRows(): void {
    this.loading.set(true);
    this.error.set(null);
    const status = this.statusFilter || undefined;
    this.ingestionApi.list({ status }).subscribe({
      next: (data) => {
        this.rows.set(data);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.error.set('Não foi possível carregar as ingestões.');
      },
    });
  }

  reprocess(r: IngestionDto): void {
    this.actionOk.set(null);
    this.actionErr.set(null);
    this.reprocessingId.set(r.id);
    this.ingestionApi.reprocess(r.id).subscribe({
      next: () => {
        this.reprocessingId.set(null);
        this.actionErr.set(null);
        this.loading.set(true);
        this.error.set(null);
        const status = this.statusFilter || undefined;
        this.ingestionApi.list({ status }).subscribe({
          next: (data) => {
            this.rows.set(data);
            this.loading.set(false);
            this.actionOk.set('Ingestão reenfileirada para processamento.');
          },
          error: () => {
            this.loading.set(false);
            this.error.set('Não foi possível atualizar a lista após reprocessar.');
          },
        });
      },
      error: (err: HttpErrorResponse) => {
        this.reprocessingId.set(null);
        const d = err.error?.detail;
        if (err.status === 409) {
          this.actionErr.set(typeof d === 'string' ? d : 'A ingestão ainda está a ser processada.');
        } else if (err.status === 403) {
          this.actionErr.set('Sem permissão para reprocessar.');
        } else {
          this.actionErr.set(typeof d === 'string' ? d : 'Não foi possível reprocessar.');
        }
      },
    });
  }
}
