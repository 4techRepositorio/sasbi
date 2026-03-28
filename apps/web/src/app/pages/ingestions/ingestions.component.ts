import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpParams } from '@angular/common/http';
import { DecimalPipe } from '@angular/common';

import { API_V1 } from '../../core/api-base';

interface IngestionRow {
  id: string;
  original_filename: string;
  status: string;
  size_bytes: number;
  friendly_error: string | null;
  result_summary: string | null;
  created_at: string;
}

@Component({
  selector: 'app-ingestions',
  imports: [FormsModule, DecimalPipe],
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
                <th>Erro</th>
                <th>Criado</th>
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
                  <td class="da-cell-err">{{ r.friendly_error ?? '—' }}</td>
                  <td class="da-cell-date">{{ r.created_at }}</td>
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
        max-width: 200px;
        word-break: break-word;
        color: var(--da-warning-text);
      }
      .da-cell-date {
        white-space: nowrap;
        color: var(--da-text-secondary);
      }
    `,
  ],
})
export class IngestionsComponent implements OnInit {
  private readonly http = inject(HttpClient);

  statusFilter = '';
  readonly rows = signal<IngestionRow[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  /** Mapeia estado da API para modificadores visuais (wireframe I2). */
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

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.error.set(null);
    let params = new HttpParams();
    if (this.statusFilter) {
      params = params.set('status', this.statusFilter);
    }
    this.http.get<IngestionRow[]>(`${API_V1}/ingestions`, { params }).subscribe({
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
}
