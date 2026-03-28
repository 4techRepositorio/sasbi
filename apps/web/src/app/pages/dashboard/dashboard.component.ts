import { DatePipe, DecimalPipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { API_V1 } from '../../core/api-base';

interface DatasetPaginated {
  items: unknown[];
  total: number;
  limit: number;
  offset: number;
}

interface IngestionRow {
  id: string;
  original_filename: string;
  status: string;
  size_bytes: number;
  friendly_error: string | null;
  created_at: string;
}

const PIPELINE_STATUSES = ['uploaded', 'validating', 'parsing', 'processed', 'failed'] as const;

@Component({
  selector: 'app-dashboard',
  imports: [DatePipe, DecimalPipe, RouterLink],
  template: `
    <div class="da-dash">
      <header class="da-dash__hero">
        <h1 class="da-dash__title">Dashboard</h1>
        <p class="da-dash__sub">
          Visão geral do pipeline de dados do tenant — alinhado à área de trabalho tipo solução de analytics.
        </p>
      </header>

      @if (loading()) {
        <p class="da-muted">A carregar indicadores…</p>
      } @else if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
      } @else {
        <div class="da-dash__kpis">
          @for (k of kpis(); track k.id) {
            <article class="da-kpi">
              <span class="da-kpi__label">{{ k.label }}</span>
              <span class="da-kpi__value">{{ k.value | number }}</span>
              @if (k.hint) {
                <span class="da-kpi__hint">{{ k.hint }}</span>
              }
            </article>
          }
        </div>

        <div class="da-dash__grid">
          <section class="da-chart-card" aria-labelledby="dash-chart-title">
            <div class="da-chart-card__head">
              <h2 id="dash-chart-title" class="da-chart-card__title">Pipeline por estado</h2>
              <p class="da-chart-card__sub">Volume de ingestões em cada fase (tenant atual).</p>
            </div>
            <div class="da-chart-card__body">
              <div class="da-bars" role="img" aria-label="Gráfico de barras por estado da ingestão">
                @for (b of bars(); track b.status) {
                  <div class="da-bars__item">
                    <div
                      class="da-bars__fill"
                      [style.height.%]="b.pct"
                      [attr.title]="b.count + ' ' + b.status"
                    ></div>
                    <span class="da-bars__label">{{ b.status }}</span>
                    <span class="da-bars__count">{{ b.count }}</span>
                  </div>
                }
              </div>
            </div>
          </section>

          <section class="da-card da-dash__recent" aria-labelledby="dash-recent-title">
            <div class="da-dash__recent-head">
              <h2 id="dash-recent-title" class="da-card__title">Atividade recente</h2>
              <a routerLink="/app/ingestions" class="da-dash__link-all">Ver ingestões</a>
            </div>
            <p class="da-card__sub">Últimas ingestões registadas neste tenant.</p>
            @if (!recent().length) {
              <p class="da-muted">Sem ingestões. Utilize Upload para enviar ficheiros.</p>
            } @else {
              <div class="da-table-wrap">
                <table class="da-table da-table--compact">
                  <thead>
                    <tr>
                      <th>Ficheiro</th>
                      <th>Estado</th>
                      <th>Tamanho</th>
                      <th>Quando</th>
                    </tr>
                  </thead>
                  <tbody>
                    @for (r of recent(); track r.id) {
                      <tr>
                        <td class="da-dash__fname">{{ r.original_filename }}</td>
                        <td><span [class]="pillClass(r.status)">{{ r.status }}</span></td>
                        <td>{{ r.size_bytes | number }} B</td>
                        <td class="da-cell-date">{{ r.created_at | date: 'short' }}</td>
                      </tr>
                    }
                  </tbody>
                </table>
              </div>
            }
          </section>
        </div>

        <p class="da-dash__foot">
          Catálogo de datasets prontos:
          <a routerLink="/app/datasets">{{ catalogTotal() | number }} no catálogo</a>
        </p>
      }
    </div>
  `,
  styles: [
    `
      .da-dash__fname {
        max-width: 200px;
        word-break: break-word;
      }
      .da-cell-date {
        white-space: nowrap;
        color: var(--da-text-secondary);
        font-size: 0.85rem;
      }
    `,
  ],
})
export class DashboardComponent implements OnInit {
  private readonly http = inject(HttpClient);

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly catalogTotal = signal(0);
  readonly ingestions = signal<IngestionRow[]>([]);

  readonly kpis = computed(() => {
    const list = this.ingestions();
    const inPipeline = list.filter((r) =>
      ['uploaded', 'validating', 'parsing'].includes(r.status),
    ).length;
    const failed = list.filter((r) => r.status === 'failed').length;
    return [
      { id: 'cat', label: 'Datasets no catálogo', value: this.catalogTotal(), hint: 'Estado processed' },
      { id: 'pipe', label: 'Em pipeline', value: inPipeline, hint: 'uploaded → parsing' },
      { id: 'fail', label: 'Falhas', value: failed, hint: 'Requer revisão' },
      { id: 'all', label: 'Total ingestões', value: list.length, hint: 'Histórico' },
    ];
  });

  readonly bars = computed(() => {
    const list = this.ingestions();
    const counts: Record<string, number> = {};
    for (const s of PIPELINE_STATUSES) {
      counts[s] = 0;
    }
    for (const r of list) {
      if (counts[r.status] !== undefined) {
        counts[r.status] += 1;
      }
    }
    const vals = PIPELINE_STATUSES.map((s) => counts[s]);
    const max = Math.max(1, ...vals);
    return PIPELINE_STATUSES.map((status) => ({
      status,
      count: counts[status],
      pct: (counts[status] / max) * 100,
    }));
  });

  readonly recent = computed(() => {
    const list = [...this.ingestions()];
    list.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    return list.slice(0, 6);
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    forkJoin({
      datasets: this.http.get<DatasetPaginated>(`${API_V1}/datasets`),
      ingestions: this.http.get<IngestionRow[]>(`${API_V1}/ingestions`),
    }).subscribe({
      next: ({ datasets, ingestions }) => {
        this.catalogTotal.set(datasets.total ?? 0);
        this.ingestions.set(ingestions);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.error.set('Não foi possível carregar o dashboard.');
      },
    });
  }

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
}
