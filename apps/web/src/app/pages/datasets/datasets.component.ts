import { Component, inject, OnInit, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';

import { API_V1 } from '../../core/api-base';

interface DatasetRow {
  id: string;
  original_filename: string;
  status: string;
  size_bytes: number;
  result_summary: string | null;
  created_at: string;
}

interface PaginatedDatasets {
  items: DatasetRow[];
  total: number;
  limit: number;
  offset: number;
}

@Component({
  selector: 'app-datasets',
  imports: [DecimalPipe],
  template: `
    <section class="da-card">
      <h2 class="da-card__title">Catálogo de datasets</h2>
      <p class="da-card__sub">
        Apenas ficheiros com estado <code class="da-code">processed</code> neste tenant — prontos para o workspace /
        dashboards (Fase 3).
      </p>
      @if (total() !== null) {
        <p class="da-meta">Total no catálogo: {{ total() }}</p>
      }
      @if (loading()) {
        <p class="da-muted">A carregar…</p>
      } @else if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
      } @else if (!rows().length) {
        <p class="da-muted">Ainda não há datasets processados. Envie ficheiros em Upload e aguarde a ingestão.</p>
      } @else {
        <div class="da-table-wrap">
          <table class="da-table">
            <thead>
              <tr>
                <th>Ficheiro</th>
                <th>Tamanho</th>
                <th>Resumo</th>
                <th>Criado</th>
              </tr>
            </thead>
            <tbody>
              @for (r of rows(); track r.id) {
                <tr>
                  <td>{{ r.original_filename }}</td>
                  <td>{{ r.size_bytes | number }} B</td>
                  <td class="da-cell-summary">{{ r.result_summary ?? '—' }}</td>
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
      .da-cell-summary {
        max-width: 280px;
        word-break: break-word;
      }
      .da-cell-date {
        white-space: nowrap;
        color: var(--da-text-secondary);
      }
    `,
  ],
})
export class DatasetsComponent implements OnInit {
  private readonly http = inject(HttpClient);

  readonly rows = signal<DatasetRow[]>([]);
  readonly total = signal<number | null>(null);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  ngOnInit(): void {
    this.http.get<PaginatedDatasets>(`${API_V1}/datasets`).subscribe({
      next: (data) => {
        this.rows.set(data.items);
        this.total.set(data.total);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.error.set('Não foi possível carregar os datasets.');
      },
    });
  }
}
