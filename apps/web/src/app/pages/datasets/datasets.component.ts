import { DatePipe, DecimalPipe } from '@angular/common';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Component, computed, inject, OnInit, signal } from '@angular/core';

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
  imports: [DatePipe, DecimalPipe],
  template: `
    <section class="da-card">
      <h2 class="da-card__title">Catálogo de datasets</h2>
      <p class="da-card__sub">
        Apenas ficheiros com estado <code class="da-code">processed</code> neste tenant — prontos para o workspace /
        dashboards (Fase 3).
      </p>
      @if (total() !== null && total()! > 0) {
        <p class="da-meta">{{ rangeLabel() }}</p>
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
                  <td class="da-cell-date">{{ r.created_at | date: 'short' }}</td>
                </tr>
              }
            </tbody>
          </table>
        </div>
        @if (total() !== null && total()! > pageSize) {
          <div class="da-pager">
            <button
              type="button"
              class="da-btn da-btn--ghost"
              (click)="prevPage()"
              [disabled]="offset() === 0 || loading()"
            >
              Anterior
            </button>
            <span class="da-pager__info">{{ pageIndex() }} / {{ pageCount() }}</span>
            <button
              type="button"
              class="da-btn da-btn--ghost"
              (click)="nextPage()"
              [disabled]="!hasNext() || loading()"
            >
              Seguinte
            </button>
          </div>
        }
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
      .da-pager {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-top: 1rem;
        flex-wrap: wrap;
      }
      .da-pager__info {
        font-size: 0.88rem;
        color: var(--da-text-secondary);
      }
    `,
  ],
})
export class DatasetsComponent implements OnInit {
  private readonly http = inject(HttpClient);

  readonly pageSize = 25;
  readonly offset = signal(0);
  readonly rows = signal<DatasetRow[]>([]);
  readonly total = signal<number | null>(null);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly pageCount = computed(() => {
    const t = this.total();
    if (t === null || t === 0) {
      return 1;
    }
    return Math.max(1, Math.ceil(t / this.pageSize));
  });

  readonly pageIndex = computed(() => {
    const t = this.total() ?? 0;
    if (t === 0) {
      return 1;
    }
    return Math.floor(this.offset() / this.pageSize) + 1;
  });

  readonly rangeLabel = computed(() => {
    const t = this.total();
    if (t === null || t === 0) {
      return '';
    }
    const start = this.offset() + 1;
    const end = Math.min(this.offset() + this.rows().length, t);
    return `A mostrar ${start}–${end} de ${t} no catálogo`;
  });

  ngOnInit(): void {
    this.fetch(0);
  }

  hasNext(): boolean {
    const t = this.total();
    if (t === null) {
      return false;
    }
    return this.offset() + this.pageSize < t;
  }

  prevPage(): void {
    const next = Math.max(0, this.offset() - this.pageSize);
    this.fetch(next);
  }

  nextPage(): void {
    if (!this.hasNext()) {
      return;
    }
    this.fetch(this.offset() + this.pageSize);
  }

  private fetch(offset: number): void {
    this.loading.set(true);
    this.error.set(null);
    const params = new HttpParams().set('limit', String(this.pageSize)).set('offset', String(offset));
    this.http.get<PaginatedDatasets>(`${API_V1}/datasets`, { params }).subscribe({
      next: (data) => {
        this.offset.set(offset);
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
