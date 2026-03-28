import { DatePipe, DecimalPipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { API_V1 } from '../../core/api-base';
import { AuthService } from '../../core/auth.service';
import { formatBytes } from '../../core/format-bytes';
import {
  groupStoragePercent,
  tenantStoragePercent,
  userStoragePercent,
} from '../../core/storage-usage';
import type { StorageContext } from '../../core/tenant-context';
import { TenantContextService } from '../../core/tenant-context.service';
import { StorageQuotaBlockComponent } from '../../shared';

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

interface DashboardKpi {
  id: string;
  label: string;
  value: number;
  hint: string;
  trend: string;
  trendNeutral: boolean;
}

const PIPELINE_STATUSES = ['uploaded', 'validating', 'parsing', 'processed', 'failed'] as const;

@Component({
  selector: 'app-dashboard',
  imports: [DatePipe, DecimalPipe, RouterLink, StorageQuotaBlockComponent],
  template: `
    <div class="da-dash">
      @if (loading()) {
        <p class="da-muted">A carregar indicadores…</p>
      } @else if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
      } @else {
        <section class="da-dash__welcome" aria-label="Resumo do workspace">
          <div class="da-dash__welcome-text">
            <p class="da-dash__welcome-kicker">Business Intelligence</p>
            <h1 class="da-dash__welcome-title">Dashboard</h1>
            <p class="da-dash__welcome-meta">
              Visão executiva do pipeline e do catálogo — organização atual no contexto multitenant.
            </p>
          </div>
          <span class="da-dash__welcome-badge">Demo</span>
        </section>

        @if (tenantCtx.context(); as dctx) {
          <section class="da-dash__quota" aria-label="Plano e armazenamento">
            <div class="da-dash__quota-grid">
              @if (dctx.plan; as pl) {
                <article class="da-dash__quota-card">
                  <h2 class="da-dash__quota-title">Pacote ativo</h2>
                  <p class="da-dash__quota-lead">{{ pl.name }}</p>
                  <ul class="da-dash__quota-list">
                    <li>Até <strong>{{ pl.max_uploads_per_month | number }}</strong> uploads por mês</li>
                    <li>Até <strong>{{ pl.max_storage_mb | number }}</strong> MB de armazenamento no plano</li>
                  </ul>
                </article>
              }
              @if (dctx.storage; as st) {
                <article class="da-dash__quota-card da-dash__quota-card--storage">
                  <h2 class="da-dash__quota-title">Utilização de armazenamento</h2>
                  <p class="da-dash__quota-sub">Organização (tenant)</p>
                  <app-storage-quota-block
                    [storage]="st"
                    variant="dash"
                    metaStyle="verbose"
                    [showLabel]="false"
                  />
                </article>
              }
            </div>
          </section>
        }

        @if (isEmptyWorkspace()) {
          <p class="da-dash__empty-hint da-muted">
            @if (mayUpload()) {
              Ainda sem dados neste tenant.
              <a routerLink="/app/upload">Enviar um ficheiro</a>
              para iniciar o pipeline.
            } @else {
              Ainda sem dados. Quando houver ingestões processadas, o resumo aparece aqui; consulte também o
              <a routerLink="/app/datasets">catálogo</a>.
            }
          </p>
        }
        <div class="da-dash__kpis">
          @for (k of kpis(); track k.id) {
            <article class="da-kpi">
              <span class="da-kpi__label">{{ k.label }}</span>
              <div class="da-kpi__row">
                <span class="da-kpi__value">{{ k.value | number }}</span>
                <span class="da-kpi__trend" [class.da-kpi__trend--neutral]="k.trendNeutral">{{ k.trend }}</span>
              </div>
              @if (k.hint) {
                <span class="da-kpi__hint">{{ k.hint }}</span>
              }
            </article>
          }
        </div>

        <div class="da-dash__grid">
          <div class="da-dash__col-stack">
            <section class="da-spark-card" aria-labelledby="dash-spark-title">
              <div class="da-spark-card__head">
                <h2 id="dash-spark-title" class="da-spark-card__title">Crescimento de dados</h2>
                <p class="da-spark-card__sub">Evolução ilustrativa (alinhado ao mockup PDF — dados reais em roadmap).</p>
              </div>
              <div class="da-spark-card__body">
                <svg class="da-spark-svg" viewBox="0 0 400 120" preserveAspectRatio="none" aria-hidden="true">
                  <defs>
                    <linearGradient id="dashLineGrad" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stop-color="#2196f3" />
                      <stop offset="100%" stop-color="#e91e63" />
                    </linearGradient>
                  </defs>
                  <path
                    d="M 0 90 L 60 70 L 120 85 L 180 45 L 240 55 L 300 25 L 360 35 L 400 15"
                    fill="none"
                    stroke="url(#dashLineGrad)"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                  <path
                    d="M 0 90 L 60 70 L 120 85 L 180 45 L 240 55 L 300 25 L 360 35 L 400 15 L 400 120 L 0 120 Z"
                    fill="url(#dashLineGrad)"
                    opacity="0.12"
                  />
                </svg>
              </div>
            </section>

            <section class="da-chart-card" aria-labelledby="dash-chart-title">
              <div class="da-chart-card__head">
                <h2 id="dash-chart-title" class="da-chart-card__title">Uploads / pipeline por estado</h2>
                <p class="da-chart-card__sub">Volume por fase no tenant atual (estilo barras do PDF).</p>
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
          </div>

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

        <nav class="da-quick-actions" aria-label="Atalhos principais">
          @if (mayUpload()) {
            <a routerLink="/app/upload" class="da-quick-card da-quick-card--blue">
              <span class="da-quick-card__icon" aria-hidden="true">📤</span>
              <h3 class="da-quick-card__title">Upload de dados</h3>
              <p class="da-quick-card__sub">CSV, Excel, JSON — como no PDF.</p>
            </a>
          }
          <a routerLink="/app/datasets" class="da-quick-card da-quick-card--magenta">
            <span class="da-quick-card__icon" aria-hidden="true">📈</span>
            <h3 class="da-quick-card__title">Explorar catálogo</h3>
            <p class="da-quick-card__sub">Datasets processados do tenant.</p>
          </a>
          <a routerLink="/app/ingestions" class="da-quick-card da-quick-card--amber">
            <span class="da-quick-card__icon" aria-hidden="true">⚙️</span>
            <h3 class="da-quick-card__title">Pipeline ETL</h3>
            <p class="da-quick-card__sub">Ingestões, estados e histórico.</p>
          </a>
        </nav>

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
      .da-dash__empty-hint {
        margin: 0 0 1.25rem;
        line-height: 1.5;
      }
      .da-dash__empty-hint a {
        font-weight: 600;
      }
      .da-dash__col-stack {
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
        min-width: 0;
      }
      .da-dash__quota {
        margin-bottom: 1.5rem;
      }
      .da-dash__quota-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 1rem;
        align-items: start;
      }
      .da-dash__quota-card {
        margin: 0;
        padding: 1.1rem 1.25rem;
        border-radius: var(--da-radius-sm);
        border: 1px solid var(--da-border);
        background: var(--da-bg-card);
        box-shadow: var(--da-shadow-sm, none);
      }
      .da-dash__quota-card--storage .da-storage {
        margin-top: 0.35rem;
      }
      .da-dash__quota-title {
        margin: 0 0 0.5rem;
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--da-text);
        font-family: var(--da-font-display);
      }
      .da-dash__quota-lead {
        margin: 0 0 0.65rem;
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--da-accent-hover);
      }
      .da-dash__quota-sub {
        margin: 0 0 0.35rem;
        font-size: 0.8rem;
        color: var(--da-text-muted);
      }
      .da-dash__quota-list {
        margin: 0;
        padding-left: 1.15rem;
        color: var(--da-text-secondary);
        font-size: 0.88rem;
        line-height: 1.55;
      }
    `,
  ],
})
export class DashboardComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly auth = inject(AuthService);
  readonly tenantCtx = inject(TenantContextService);

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly catalogTotal = signal(0);
  readonly ingestions = signal<IngestionRow[]>([]);

  readonly kpis = computed((): DashboardKpi[] => {
    const list = this.ingestions();
    const cat = this.catalogTotal();
    const inPipeline = list.filter((r) =>
      ['uploaded', 'validating', 'parsing'].includes(r.status),
    ).length;
    const failed = list.filter((r) => r.status === 'failed').length;
    const total = list.length;
    return [
      {
        id: 'cat',
        label: 'Datasets no catálogo',
        value: cat,
        hint: 'Estado processed',
        trend: cat > 0 ? '+12.5%' : '—',
        trendNeutral: cat === 0,
      },
      {
        id: 'pipe',
        label: 'Em pipeline',
        value: inPipeline,
        hint: 'uploaded → parsing',
        trend: inPipeline > 0 ? '+18.2%' : '—',
        trendNeutral: inPipeline === 0,
      },
      {
        id: 'fail',
        label: 'Falhas',
        value: failed,
        hint: 'Requer revisão',
        trend: failed > 0 ? '−3%' : '0%',
        trendNeutral: failed === 0,
      },
      {
        id: 'all',
        label: 'Total ingestões',
        value: total,
        hint: 'Histórico',
        trend: total > 0 ? '+8%' : '—',
        trendNeutral: total === 0,
      },
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

  readonly isEmptyWorkspace = computed(
    () => this.catalogTotal() === 0 && this.ingestions().length === 0,
  );

  readonly mayUpload = computed(() => {
    const r = this.tenantCtx.context()?.role ?? this.auth.tenantRole();
    return r === 'admin' || r === 'analyst';
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.tenantCtx.load().subscribe({ error: () => undefined });
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
