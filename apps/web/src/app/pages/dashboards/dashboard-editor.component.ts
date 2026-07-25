import { DecimalPipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';
import {
  DashboardItem,
  DashboardLayout,
  DashboardsService,
  DashboardWidget,
  WidgetType,
} from '../../core/dashboards.service';
import { QueryResponse, QueryService } from '../../core/query.service';
import { canEditBi, roleFromContext } from '../../core/rbac';
import {
  AggregationOp,
  SemanticModelItem,
  SemanticService,
} from '../../core/semantic.service';
import { TenantContextService } from '../../core/tenant-context.service';

const WIDGET_LABELS: Record<WidgetType, string> = {
  kpi: 'KPI',
  bar_chart: 'Barras',
  line_chart: 'Linha',
  table: 'Tabela',
  text: 'Texto',
};

function newWidgetId(): string {
  return `w_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`;
}

function defaultSize(type: WidgetType): { w: number; h: number } {
  switch (type) {
    case 'kpi':
      return { w: 3, h: 2 };
    case 'text':
      return { w: 4, h: 2 };
    case 'table':
      return { w: 6, h: 4 };
    case 'bar_chart':
    case 'line_chart':
      return { w: 6, h: 4 };
    default: {
      const _exhaustive: never = type;
      return _exhaustive;
    }
  }
}

@Component({
  selector: 'app-dashboard-editor',
  imports: [DecimalPipe, FormsModule, RouterLink],
  template: `
    <div class="da-editor">
      @if (loading()) {
        <p class="da-muted">A carregar dashboard…</p>
      } @else if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
        <a routerLink="/app/dashboards" class="da-btn da-btn--ghost">Voltar à lista</a>
      } @else {
        @if (dashboard(); as dash) {
        <header class="da-editor__toolbar">
          <div class="da-editor__titles">
            <a routerLink="/app/dashboards" class="da-editor__back">← Dashboards</a>
            @if (canEdit()) {
              <input class="da-editor__name" [(ngModel)]="editName" aria-label="Nome do dashboard" />
            } @else {
              <h1 class="da-editor__name-ro">{{ dash.name }}</h1>
            }
            <span [class]="statusPill(dash.status)">{{ statusLabel(dash.status) }}</span>
            <span class="da-muted">v{{ dash.version }}</span>
          </div>
          <div class="da-editor__actions">
            @if (canEdit()) {
              <div class="da-add-menu">
                <span class="da-add-menu__label">Adicionar</span>
                @for (t of widgetTypes; track t) {
                  <button type="button" class="da-btn da-btn--ghost da-btn--sm" (click)="addWidget(t)">
                    {{ widgetLabel(t) }}
                  </button>
                }
              </div>
              <button
                type="button"
                class="da-btn da-btn--ghost"
                (click)="saveDraft()"
                [disabled]="saving()"
              >
                {{ saving() ? 'A guardar…' : 'Guardar rascunho' }}
              </button>
              <button
                type="button"
                class="da-btn da-btn--primary"
                (click)="publish()"
                [disabled]="publishing() || saving()"
              >
                {{ publishing() ? 'A publicar…' : 'Publicar' }}
              </button>
            }
          </div>
        </header>

        @if (actionOk()) {
          <p class="da-inline-ok" role="status">{{ actionOk() }}</p>
        }
        @if (actionErr()) {
          <p class="da-err" role="alert">{{ actionErr() }}</p>
        }

        @if (canEdit()) {
          <label class="da-editor__desc">
            <span>Descrição</span>
            <input type="text" [(ngModel)]="editDescription" />
          </label>
        } @else if (dash.description) {
          <p class="da-card__sub">{{ dash.description }}</p>
        }

        <div class="da-editor__layout">
          <div class="da-canvas" [style.--cols]="layout().columns">
            @if (!widgets().length) {
              <div class="da-canvas__empty">
                <p class="da-muted">
                  @if (canEdit()) {
                    Canvas vazio — adicione widgets na barra superior.
                  } @else {
                    Este dashboard ainda não tem widgets.
                  }
                </p>
              </div>
            } @else {
              @for (w of widgets(); track w.id) {
                <article
                  class="da-widget"
                  [class.da-widget--selected]="selectedId() === w.id"
                  [style.grid-column]="w.x + 1 + ' / span ' + w.w"
                  [style.grid-row]="w.y + 1 + ' / span ' + w.h"
                  (click)="selectWidget(w.id)"
                >
                  <header class="da-widget__head">
                    <strong>{{ w.title || widgetLabel(w.type) }}</strong>
                    <span class="da-widget__type">{{ widgetLabel(w.type) }}</span>
                  </header>
                  <div class="da-widget__body">
                    @switch (w.type) {
                      @case ('text') {
                        <p class="da-widget__text">{{ textBody(w) }}</p>
                      }
                      @case ('kpi') {
                        @if (previewFor(w.id); as prev) {
                          <div class="da-widget-kpi">
                            <span class="da-widget-kpi__value">{{ kpiValue(prev) | number }}</span>
                          </div>
                        } @else {
                          <p class="da-muted da-widget__hint">Pré-visualizar para ver o KPI</p>
                        }
                      }
                      @case ('bar_chart') {
                        @if (previewFor(w.id); as prev) {
                          <div class="da-mini-bars">
                            @for (b of barPoints(prev); track b.label) {
                              <div class="da-mini-bars__item">
                                <div class="da-mini-bars__fill" [style.height.%]="b.pct"></div>
                                <span>{{ b.label }}</span>
                              </div>
                            }
                          </div>
                        } @else {
                          <p class="da-muted da-widget__hint">Ligue uma query e pré-visualize</p>
                        }
                      }
                      @case ('line_chart') {
                        @if (previewFor(w.id); as prev) {
                          <svg class="da-mini-line" viewBox="0 0 200 80" preserveAspectRatio="none">
                            <polyline
                              [attr.points]="linePoints(prev)"
                              fill="none"
                              stroke="url(#lineGrad)"
                              stroke-width="2"
                            />
                            <defs>
                              <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
                                <stop offset="0%" stop-color="#2196f3" />
                                <stop offset="100%" stop-color="#e91e63" />
                              </linearGradient>
                            </defs>
                          </svg>
                        } @else {
                          <p class="da-muted da-widget__hint">Ligue uma query e pré-visualize</p>
                        }
                      }
                      @case ('table') {
                        @if (previewFor(w.id); as prev) {
                          <div class="da-table-wrap da-widget-table">
                            <table class="da-table da-table--compact">
                              <thead>
                                <tr>
                                  @for (c of prev.columns; track c) {
                                    <th>{{ c }}</th>
                                  }
                                </tr>
                              </thead>
                              <tbody>
                                @for (row of prev.rows.slice(0, 5); track $index) {
                                  <tr>
                                    @for (c of prev.columns; track c) {
                                      <td>{{ row[c] }}</td>
                                    }
                                  </tr>
                                }
                              </tbody>
                            </table>
                          </div>
                        } @else {
                          <p class="da-muted da-widget__hint">Ligue uma query e pré-visualize</p>
                        }
                      }
                      @default {
                        <p class="da-muted">Widget</p>
                      }
                    }
                  </div>
                </article>
              }
            }
          </div>

          @if (canEdit()) {
            @if (selected(); as sel) {
            <aside class="da-inspector" aria-label="Propriedades do widget">
              <h3>Propriedades</h3>
              <label class="da-field">
                <span>Título</span>
                <input type="text" [ngModel]="sel.title" (ngModelChange)="patchSelected({ title: $event })" />
              </label>
              <div class="da-field-row">
                <label class="da-field">
                  <span>X</span>
                  <input
                    type="number"
                    min="0"
                    [ngModel]="sel.x"
                    (ngModelChange)="patchSelected({ x: +$event })"
                  />
                </label>
                <label class="da-field">
                  <span>Y</span>
                  <input
                    type="number"
                    min="0"
                    [ngModel]="sel.y"
                    (ngModelChange)="patchSelected({ y: +$event })"
                  />
                </label>
                <label class="da-field">
                  <span>W</span>
                  <input
                    type="number"
                    min="1"
                    max="12"
                    [ngModel]="sel.w"
                    (ngModelChange)="patchSelected({ w: +$event })"
                  />
                </label>
                <label class="da-field">
                  <span>H</span>
                  <input
                    type="number"
                    min="1"
                    [ngModel]="sel.h"
                    (ngModelChange)="patchSelected({ h: +$event })"
                  />
                </label>
              </div>

              @if (sel.type === 'text') {
                <label class="da-field">
                  <span>Conteúdo</span>
                  <textarea
                    rows="4"
                    [ngModel]="textBodyRaw(sel)"
                    (ngModelChange)="patchTextBody($event)"
                  ></textarea>
                </label>
              } @else {
                <h4 class="da-inspector__sub">Query semântica</h4>
                <label class="da-field">
                  <span>Modelo</span>
                  <select
                    [ngModel]="sel.query?.semantic_model_id || ''"
                    (ngModelChange)="patchQueryModel($event)"
                  >
                    <option value="">— selecionar —</option>
                    @for (m of models(); track m.id) {
                      <option [value]="m.id">{{ m.name }}</option>
                    }
                  </select>
                </label>
                <label class="da-field">
                  <span>Medida (campo)</span>
                  <select
                    [ngModel]="measureField(sel)"
                    (ngModelChange)="patchMeasureField($event)"
                  >
                    <option value="">—</option>
                    @for (f of measureFieldsFor(sel); track f.name) {
                      <option [value]="f.name">{{ f.label || f.name }}</option>
                    }
                  </select>
                </label>
                <label class="da-field">
                  <span>Agregação</span>
                  <select [ngModel]="measureOp(sel)" (ngModelChange)="patchMeasureOp($event)">
                    <option value="count">count</option>
                    <option value="sum">sum</option>
                    <option value="avg">avg</option>
                    <option value="min">min</option>
                    <option value="max">max</option>
                  </select>
                </label>
                <label class="da-field">
                  <span>Dimensão (opcional)</span>
                  <select
                    [ngModel]="dimensionField(sel)"
                    (ngModelChange)="patchDimension($event)"
                  >
                    <option value="">— nenhuma —</option>
                    @for (f of dimensionFieldsFor(sel); track f.name) {
                      <option [value]="f.name">{{ f.label || f.name }}</option>
                    }
                  </select>
                </label>
                <button
                  type="button"
                  class="da-btn da-btn--ghost"
                  (click)="previewSelected()"
                  [disabled]="previewing()"
                >
                  {{ previewing() ? 'A consultar…' : 'Pré-visualizar dados' }}
                </button>
              }

              <button type="button" class="da-btn da-btn--ghost da-btn--danger" (click)="removeSelected()">
                Remover widget
              </button>
            </aside>
            }
          }
        </div>
        }
      }
    </div>
  `,
  styles: [
    `
      .da-editor {
        display: flex;
        flex-direction: column;
        gap: 0.85rem;
        min-height: 70vh;
      }
      .da-editor__toolbar {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        gap: 0.75rem;
        padding: 0.85rem 1rem;
        background: var(--da-bg-card);
        border: 1px solid var(--da-border);
        border-radius: var(--da-radius);
        box-shadow: var(--da-shadow-card);
      }
      .da-editor__titles {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.65rem;
      }
      .da-editor__back {
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--da-accent-hover);
        text-decoration: none;
      }
      .da-editor__name {
        font-family: var(--da-font-display);
        font-size: 1.15rem;
        font-weight: 700;
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 0.25rem 0.4rem;
        min-width: 180px;
        background: transparent;
      }
      .da-editor__name:focus {
        border-color: var(--da-border);
        background: #fff;
        outline: none;
      }
      .da-editor__name-ro {
        margin: 0;
        font-size: 1.15rem;
        font-family: var(--da-font-display);
      }
      .da-editor__actions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem;
        align-items: center;
      }
      .da-add-menu {
        display: flex;
        flex-wrap: wrap;
        gap: 0.3rem;
        align-items: center;
        margin-right: 0.35rem;
      }
      .da-add-menu__label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--da-text-muted);
      }
      .da-btn--sm {
        padding: 0.3rem 0.55rem;
        font-size: 0.78rem;
      }
      .da-editor__desc {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        font-size: 0.8rem;
        color: var(--da-text-secondary);
      }
      .da-editor__desc input {
        padding: 0.45rem 0.65rem;
        border: 1px solid var(--da-border);
        border-radius: var(--da-radius-sm);
        font-family: inherit;
      }
      .da-editor__layout {
        display: grid;
        grid-template-columns: 1fr;
        gap: 1rem;
        align-items: start;
      }
      @media (min-width: 960px) {
        .da-editor__layout {
          grid-template-columns: 1fr minmax(260px, 300px);
        }
      }
      .da-canvas {
        display: grid;
        grid-template-columns: repeat(var(--cols, 12), minmax(0, 1fr));
        grid-auto-rows: 64px;
        gap: 0.65rem;
        min-height: 420px;
        padding: 0.85rem;
        background: rgba(255, 255, 255, 0.55);
        border: 1px dashed var(--da-border);
        border-radius: var(--da-radius);
      }
      .da-canvas__empty {
        grid-column: 1 / -1;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 280px;
      }
      .da-widget {
        background: var(--da-bg-card);
        border: 1px solid var(--da-border);
        border-radius: var(--da-radius-sm);
        box-shadow: var(--da-shadow-card);
        overflow: hidden;
        cursor: pointer;
        display: flex;
        flex-direction: column;
        min-width: 0;
      }
      .da-widget--selected {
        border-color: rgba(233, 30, 99, 0.55);
        box-shadow: 0 0 0 2px rgba(233, 30, 99, 0.15);
      }
      .da-widget__head {
        display: flex;
        justify-content: space-between;
        gap: 0.35rem;
        padding: 0.45rem 0.65rem;
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.12), rgba(233, 30, 99, 0.1));
        font-size: 0.82rem;
      }
      .da-widget__type {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--da-text-muted);
      }
      .da-widget__body {
        flex: 1;
        padding: 0.55rem 0.65rem;
        min-height: 0;
        overflow: auto;
      }
      .da-widget__hint,
      .da-widget__text {
        margin: 0;
        font-size: 0.85rem;
      }
      .da-widget-kpi__value {
        font-family: var(--da-font-display);
        font-size: 1.75rem;
        font-weight: 700;
      }
      .da-mini-bars {
        display: flex;
        align-items: flex-end;
        gap: 0.35rem;
        min-height: 100px;
      }
      .da-mini-bars__item {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.2rem;
        font-size: 0.62rem;
        color: var(--da-text-muted);
        min-width: 0;
      }
      .da-mini-bars__fill {
        width: 100%;
        max-width: 28px;
        min-height: 4px;
        border-radius: 4px 4px 1px 1px;
        background: linear-gradient(180deg, #2196f3, #e91e63);
      }
      .da-mini-line {
        width: 100%;
        height: 80px;
        display: block;
      }
      .da-widget-table {
        max-height: 100%;
      }
      .da-inspector {
        padding: 1rem;
        background: var(--da-bg-card);
        border: 1px solid var(--da-border);
        border-radius: var(--da-radius);
        box-shadow: var(--da-shadow-card);
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        position: sticky;
        top: 0.5rem;
      }
      .da-inspector h3 {
        margin: 0;
        font-size: 1rem;
      }
      .da-inspector__sub {
        margin: 0.25rem 0 0;
        font-size: 0.82rem;
        color: var(--da-text-secondary);
      }
      .da-field {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        font-size: 0.78rem;
        color: var(--da-text-secondary);
      }
      .da-field input,
      .da-field select,
      .da-field textarea {
        padding: 0.4rem 0.5rem;
        border: 1px solid var(--da-border);
        border-radius: 6px;
        font-family: inherit;
        font-size: 0.88rem;
      }
      .da-field-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.4rem;
      }
      .da-btn--danger {
        color: var(--da-danger-text);
        border-color: #fecaca;
      }
      .da-inline-ok {
        margin: 0;
        padding: 0.5rem 0.75rem;
        border-radius: var(--da-radius-sm);
        background: var(--da-success-bg);
        color: var(--da-success-text);
        font-size: 0.88rem;
      }
    `,
  ],
})
export class DashboardEditorComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(DashboardsService);
  private readonly queryApi = inject(QueryService);
  private readonly semanticApi = inject(SemanticService);
  private readonly auth = inject(AuthService);
  private readonly tenantCtx = inject(TenantContextService);

  readonly widgetTypes: WidgetType[] = ['kpi', 'bar_chart', 'line_chart', 'table', 'text'];

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly dashboard = signal<DashboardItem | null>(null);
  readonly widgets = signal<DashboardWidget[]>([]);
  readonly layout = signal<DashboardLayout>({ version: 1, columns: 12, widgets: [] });
  readonly selectedId = signal<string | null>(null);
  readonly models = signal<SemanticModelItem[]>([]);
  readonly previews = signal<Record<string, QueryResponse>>({});
  readonly saving = signal(false);
  readonly publishing = signal(false);
  readonly previewing = signal(false);
  readonly actionOk = signal<string | null>(null);
  readonly actionErr = signal<string | null>(null);

  editName = '';
  editDescription = '';

  readonly canEdit = computed(() =>
    canEditBi(roleFromContext(this.tenantCtx.context(), this.auth.tenantRole())),
  );

  readonly selected = computed(() => {
    const id = this.selectedId();
    if (!id) {
      return null;
    }
    return this.widgets().find((w) => w.id === id) ?? null;
  });

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.error.set('Dashboard inválido.');
      this.loading.set(false);
      return;
    }
    this.load(id);
    this.semanticApi.list({ limit: 100 }).subscribe({
      next: (data) => this.models.set(data.items),
      error: () => this.models.set([]),
    });
  }

  load(id: string): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.get(id).subscribe({
      next: (d) => {
        this.dashboard.set(d);
        this.editName = d.name;
        this.editDescription = d.description ?? '';
        const layout = d.layout ?? { version: 1, columns: 12, widgets: [] };
        this.layout.set(layout);
        this.widgets.set([...(layout.widgets ?? [])]);
        this.loading.set(false);
        if (!this.canEdit() && d.status !== 'published') {
          this.actionErr.set('Este dashboard não está publicado. Apenas rascunhos próprios de editores.');
        }
      },
      error: () => {
        this.loading.set(false);
        this.error.set('Não foi possível carregar o dashboard.');
      },
    });
  }

  widgetLabel(t: WidgetType): string {
    return WIDGET_LABELS[t];
  }

  statusLabel(s: string): string {
    const map: Record<string, string> = {
      draft: 'rascunho',
      published: 'publicado',
      archived: 'arquivado',
    };
    return map[s] ?? s;
  }

  statusPill(s: string): string {
    if (s === 'published') {
      return 'da-pill da-pill--processed';
    }
    if (s === 'draft') {
      return 'da-pill da-pill--uploaded';
    }
    return 'da-pill';
  }

  selectWidget(id: string): void {
    this.selectedId.set(id);
  }

  addWidget(type: WidgetType): void {
    const size = defaultSize(type);
    const existing = this.widgets();
    const y = existing.reduce((max, w) => Math.max(max, w.y + w.h), 0);
    const w: DashboardWidget = {
      id: newWidgetId(),
      type,
      title: WIDGET_LABELS[type],
      x: 0,
      y,
      w: size.w,
      h: size.h,
      query:
        type === 'text'
          ? null
          : {
              semantic_model_id: null,
              measures: [],
              dimensions: [],
              filters: {},
              limit: 100,
            },
      options: type === 'text' ? { body: '' } : {},
    };
    this.widgets.set([...existing, w]);
    this.selectedId.set(w.id);
  }

  patchSelected(partial: Partial<DashboardWidget>): void {
    const id = this.selectedId();
    if (!id) {
      return;
    }
    this.widgets.set(
      this.widgets().map((w) => {
        if (w.id !== id) {
          return w;
        }
        return {
          ...w,
          ...partial,
          x: partial.x != null ? Math.max(0, Math.min(11, partial.x)) : w.x,
          y: partial.y != null ? Math.max(0, partial.y) : w.y,
          w: partial.w != null ? Math.max(1, Math.min(12, partial.w)) : w.w,
          h: partial.h != null ? Math.max(1, partial.h) : w.h,
        };
      }),
    );
  }

  patchTextBody(body: string): void {
    const sel = this.selected();
    if (!sel) {
      return;
    }
    this.patchSelected({ options: { ...(sel.options ?? {}), body } });
  }

  patchQueryModel(modelId: string): void {
    const sel = this.selected();
    if (!sel) {
      return;
    }
    this.patchSelected({
      query: {
        ...(sel.query ?? { measures: [], dimensions: [], filters: {}, limit: 100 }),
        semantic_model_id: modelId || null,
      },
    });
  }

  measureField(sel: DashboardWidget): string {
    const m = sel.query?.measures?.[0];
    return m && typeof m['field'] === 'string' ? m['field'] : '';
  }

  measureOp(sel: DashboardWidget): AggregationOp {
    const m = sel.query?.measures?.[0];
    const op = m && typeof m['op'] === 'string' ? m['op'] : 'count';
    if (op === 'sum' || op === 'avg' || op === 'min' || op === 'max' || op === 'count') {
      return op;
    }
    return 'count';
  }

  dimensionField(sel: DashboardWidget): string {
    return sel.query?.dimensions?.[0] ?? '';
  }

  measureFieldsFor(sel: DashboardWidget) {
    const mid = sel.query?.semantic_model_id;
    const model = this.models().find((m) => m.id === mid);
    return (model?.fields ?? []).filter((f) => f.role === 'measure' || f.role === 'attribute');
  }

  dimensionFieldsFor(sel: DashboardWidget) {
    const mid = sel.query?.semantic_model_id;
    const model = this.models().find((m) => m.id === mid);
    return (model?.fields ?? []).filter((f) => f.role === 'dimension' || f.role === 'attribute');
  }

  patchMeasureField(field: string): void {
    const sel = this.selected();
    if (!sel) {
      return;
    }
    const op = this.measureOp(sel);
    this.patchSelected({
      query: {
        ...(sel.query ?? { dimensions: [], filters: {}, limit: 100 }),
        measures: field ? [{ field, op }] : [],
      },
    });
  }

  patchMeasureOp(op: string): void {
    const sel = this.selected();
    if (!sel) {
      return;
    }
    const field = this.measureField(sel);
    const agg: AggregationOp =
      op === 'sum' || op === 'avg' || op === 'min' || op === 'max' || op === 'count' ? op : 'count';
    this.patchSelected({
      query: {
        ...(sel.query ?? { dimensions: [], filters: {}, limit: 100 }),
        measures: field ? [{ field, op: agg }] : [],
      },
    });
  }

  patchDimension(dim: string): void {
    const sel = this.selected();
    if (!sel) {
      return;
    }
    this.patchSelected({
      query: {
        ...(sel.query ?? { measures: [], filters: {}, limit: 100 }),
        dimensions: dim ? [dim] : [],
      },
    });
  }

  removeSelected(): void {
    const id = this.selectedId();
    if (!id) {
      return;
    }
    this.widgets.set(this.widgets().filter((w) => w.id !== id));
    this.selectedId.set(null);
    const next = { ...this.previews() };
    delete next[id];
    this.previews.set(next);
  }

  previewFor(id: string): QueryResponse | null {
    return this.previews()[id] ?? null;
  }

  textBody(w: DashboardWidget): string {
    const body = w.options?.['body'];
    return typeof body === 'string' && body.trim() ? body : 'Texto do widget';
  }

  textBodyRaw(w: DashboardWidget): string {
    const body = w.options?.['body'];
    return typeof body === 'string' ? body : '';
  }

  previewSelected(): void {
    const sel = this.selected();
    if (!sel || sel.type === 'text') {
      return;
    }
    const q = sel.query;
    const modelId = q?.semantic_model_id;
    const measures = (q?.measures ?? [])
      .map((m) => ({
        field: String(m['field'] ?? ''),
        op: (m['op'] as AggregationOp) || 'count',
        alias: m['alias'] != null ? String(m['alias']) : null,
      }))
      .filter((m) => m.field);
    if (!modelId || !measures.length) {
      this.actionErr.set('Selecione modelo e medida para pré-visualizar.');
      return;
    }
    this.previewing.set(true);
    this.actionErr.set(null);
    this.queryApi
      .run({
        semantic_model_id: modelId,
        measures,
        dimensions: q?.dimensions ?? [],
        filters: q?.filters ?? {},
        limit: q?.limit ?? 100,
      })
      .subscribe({
        next: (res) => {
          this.previewing.set(false);
          this.previews.set({ ...this.previews(), [sel.id]: res });
          this.actionOk.set('Pré-visualização atualizada.');
        },
        error: (err: HttpErrorResponse) => {
          this.previewing.set(false);
          this.actionErr.set(this.httpMsg(err, 'Falha na query de pré-visualização.'));
        },
      });
  }

  kpiValue(prev: QueryResponse): number {
    if (!prev.rows.length || !prev.columns.length) {
      return 0;
    }
    const col = prev.columns.find((c) => c !== (prev.columns[0] && this.isLikelyDim(prev, c))) ?? prev.columns[0];
    const raw = prev.rows[0][col];
    const n = Number(raw);
    return Number.isFinite(n) ? n : 0;
  }

  private isLikelyDim(prev: QueryResponse, col: string): boolean {
    return prev.columns.length > 1 && col === prev.columns[0];
  }

  barPoints(prev: QueryResponse): { label: string; pct: number }[] {
    if (!prev.rows.length || !prev.columns.length) {
      return [];
    }
    const dim = prev.columns[0];
    const measure = prev.columns[1] ?? prev.columns[0];
    const vals = prev.rows.map((r) => Number(r[measure]) || 0);
    const max = Math.max(1, ...vals);
    return prev.rows.slice(0, 8).map((r) => ({
      label: String(r[dim] ?? ''),
      pct: ((Number(r[measure]) || 0) / max) * 100,
    }));
  }

  linePoints(prev: QueryResponse): string {
    const pts = this.barPoints(prev);
    if (!pts.length) {
      return '';
    }
    const n = pts.length;
    return pts
      .map((p, i) => {
        const x = n === 1 ? 100 : (i / (n - 1)) * 200;
        const y = 80 - (p.pct / 100) * 70;
        return `${x},${y}`;
      })
      .join(' ');
  }

  saveDraft(): void {
    const dash = this.dashboard();
    if (!dash) {
      return;
    }
    this.saving.set(true);
    this.actionErr.set(null);
    const layout: DashboardLayout = {
      version: this.layout().version || 1,
      columns: this.layout().columns || 12,
      widgets: this.widgets(),
    };
    this.api
      .patch(dash.id, {
        name: this.editName.trim() || dash.name,
        description: this.editDescription.trim() || null,
        layout,
        status: 'draft',
      })
      .subscribe({
        next: (updated) => {
          this.saving.set(false);
          this.dashboard.set(updated);
          this.actionOk.set('Rascunho guardado.');
        },
        error: (err: HttpErrorResponse) => {
          this.saving.set(false);
          this.actionErr.set(this.httpMsg(err, 'Falha ao guardar.'));
        },
      });
  }

  publish(): void {
    const dash = this.dashboard();
    if (!dash) {
      return;
    }
    this.publishing.set(true);
    this.actionErr.set(null);
    const layout: DashboardLayout = {
      version: this.layout().version || 1,
      columns: this.layout().columns || 12,
      widgets: this.widgets(),
    };
    this.api
      .patch(dash.id, {
        name: this.editName.trim() || dash.name,
        description: this.editDescription.trim() || null,
        layout,
      })
      .subscribe({
        next: () => {
          this.api.publish(dash.id).subscribe({
            next: (pub) => {
              this.publishing.set(false);
              this.dashboard.update((d) =>
                d
                  ? {
                      ...d,
                      status: 'published',
                      version: pub.version,
                      published_at: pub.published_at,
                    }
                  : d,
              );
              this.actionOk.set('Dashboard publicado.');
            },
            error: (err: HttpErrorResponse) => {
              this.publishing.set(false);
              this.actionErr.set(this.httpMsg(err, 'Falha ao publicar.'));
            },
          });
        },
        error: (err: HttpErrorResponse) => {
          this.publishing.set(false);
          this.actionErr.set(this.httpMsg(err, 'Falha ao guardar antes de publicar.'));
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
