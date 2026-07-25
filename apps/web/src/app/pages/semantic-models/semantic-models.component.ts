import { DatePipe } from '@angular/common';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { API_V1 } from '../../core/api-base';
import { AuthService } from '../../core/auth.service';
import { canEditBi, roleFromContext } from '../../core/rbac';
import {
  FieldRole,
  SemanticField,
  SemanticModelItem,
  SemanticService,
} from '../../core/semantic.service';
import { TenantContextService } from '../../core/tenant-context.service';

interface DatasetOption {
  id: string;
  original_filename: string;
}

interface PaginatedDatasets {
  items: DatasetOption[];
  total: number;
}

const EMPTY_FIELD = (): SemanticField => ({
  name: '',
  source_column: '',
  role: 'attribute',
  data_type: 'string',
  label: '',
});

@Component({
  selector: 'app-semantic-models',
  imports: [DatePipe, FormsModule],
  template: `
    <section class="da-card">
      <div class="da-page-head">
        <div>
          <h2 class="da-card__title">Modelos semânticos</h2>
          <p class="da-card__sub">
            Mapeie colunas do dataset para dimensões e medidas usadas nos dashboards.
          </p>
        </div>
        <div class="da-page-head__actions">
          <button type="button" class="da-btn da-btn--ghost" (click)="reload()" [disabled]="loading()">
            Atualizar
          </button>
          @if (canEdit()) {
            <button type="button" class="da-btn da-btn--primary" (click)="openCreate()">
              Novo modelo
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
        <p class="da-muted">A carregar modelos…</p>
      } @else if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
      } @else if (!rows().length) {
        <div class="da-empty">
          <p class="da-muted">Ainda não há modelos semânticos neste tenant.</p>
          @if (canEdit()) {
            <button type="button" class="da-btn da-btn--primary" (click)="openCreate()">
              Criar primeiro modelo
            </button>
          }
        </div>
      } @else {
        <p class="da-meta">{{ rows().length }} modelo(s)</p>
        <div class="da-table-wrap">
          <table class="da-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Dataset</th>
                <th>Campos</th>
                <th>Atualizado</th>
                @if (canEdit()) {
                  <th class="da-th-actions">Ações</th>
                }
              </tr>
            </thead>
            <tbody>
              @for (r of rows(); track r.id) {
                <tr>
                  <td>
                    <strong>{{ r.name }}</strong>
                    @if (r.description) {
                      <div class="da-row-sub">{{ r.description }}</div>
                    }
                  </td>
                  <td><code class="da-code">{{ shortId(r.dataset_id) }}</code></td>
                    <td>{{ r.fields.length }}</td>
                  <td class="da-cell-date">{{ r.updated_at | date: 'short' }}</td>
                  @if (canEdit()) {
                    <td class="da-td-actions">
                      <button type="button" class="da-btn da-btn--ghost da-btn--sm" (click)="openEdit(r)">
                        Editar
                      </button>
                      <button
                        type="button"
                        class="da-btn da-btn--ghost da-btn--sm"
                        (click)="remove(r)"
                        [disabled]="deletingId() === r.id"
                      >
                        Remover
                      </button>
                    </td>
                  }
                </tr>
              }
            </tbody>
          </table>
        </div>
      }
    </section>

    @if (editorOpen()) {
      <div class="da-modal-backdrop" (click)="closeEditor()" role="presentation"></div>
      <div class="da-modal da-modal--wide" role="dialog" aria-modal="true" aria-labelledby="sm-title">
        <header class="da-modal__head">
          <h3 id="sm-title">{{ editingId() ? 'Editar modelo' : 'Novo modelo semântico' }}</h3>
          <button type="button" class="da-modal__close" (click)="closeEditor()" aria-label="Fechar">
            ×
          </button>
        </header>
        <div class="da-modal__body">
          <div class="da-form-grid">
            <label class="da-field da-field--full">
              <span>Nome</span>
              <input type="text" [(ngModel)]="formName" maxlength="200" />
            </label>
            <label class="da-field da-field--full">
              <span>Descrição</span>
              <input type="text" [(ngModel)]="formDescription" />
            </label>
            <label class="da-field da-field--full">
              <span>Dataset (catálogo)</span>
              <select [(ngModel)]="formDatasetId" [disabled]="!!editingId()">
                <option value="">— selecionar —</option>
                @for (d of datasets(); track d.id) {
                  <option [value]="d.id">{{ d.original_filename }} ({{ shortId(d.id) }})</option>
                }
              </select>
            </label>
          </div>

          <div class="da-fields-head">
            <h4>Campos</h4>
            <button type="button" class="da-btn da-btn--ghost da-btn--sm" (click)="addField()">
              + Campo
            </button>
          </div>
          @if (!formFields.length) {
            <p class="da-muted">Adicione pelo menos um campo (dimensão ou medida).</p>
          } @else {
            <div class="da-table-wrap">
              <table class="da-table da-table--compact">
                <thead>
                  <tr>
                    <th>Nome lógico</th>
                    <th>Coluna origem</th>
                    <th>Papel</th>
                    <th>Tipo</th>
                    <th>Rótulo</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  @for (f of formFields; track $index; let i = $index) {
                    <tr>
                      <td><input class="da-input-sm" [(ngModel)]="f.name" /></td>
                      <td><input class="da-input-sm" [(ngModel)]="f.source_column" /></td>
                      <td>
                        <select class="da-input-sm" [(ngModel)]="f.role">
                          <option value="dimension">dimensão</option>
                          <option value="measure">medida</option>
                          <option value="attribute">atributo</option>
                        </select>
                      </td>
                      <td>
                        <select class="da-input-sm" [(ngModel)]="f.data_type">
                          <option value="string">string</option>
                          <option value="number">number</option>
                          <option value="integer">integer</option>
                          <option value="boolean">boolean</option>
                          <option value="date">date</option>
                          <option value="datetime">datetime</option>
                        </select>
                      </td>
                      <td><input class="da-input-sm" [(ngModel)]="f.label" /></td>
                      <td>
                        <button type="button" class="da-btn da-btn--ghost da-btn--sm" (click)="removeField(i)">
                          ×
                        </button>
                      </td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
          }
        </div>
        <footer class="da-modal__foot">
          <button type="button" class="da-btn da-btn--ghost" (click)="closeEditor()">Cancelar</button>
          <button
            type="button"
            class="da-btn da-btn--primary"
            (click)="save()"
            [disabled]="saving() || !formName.trim() || !formDatasetId"
          >
            {{ saving() ? 'A guardar…' : 'Guardar' }}
          </button>
        </footer>
      </div>
    }
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
        gap: 0.5rem;
        flex-wrap: wrap;
      }
      .da-empty {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        align-items: flex-start;
      }
      .da-row-sub {
        font-size: 0.8rem;
        color: var(--da-text-secondary);
        margin-top: 0.15rem;
      }
      .da-cell-date {
        white-space: nowrap;
        color: var(--da-text-secondary);
      }
      .da-td-actions {
        display: flex;
        gap: 0.35rem;
        flex-wrap: wrap;
      }
      .da-btn--sm {
        padding: 0.35rem 0.65rem;
        font-size: 0.8rem;
      }
      .da-inline-ok {
        margin: 0 0 0.75rem;
        padding: 0.5rem 0.75rem;
        border-radius: var(--da-radius-sm);
        background: var(--da-success-bg);
        color: var(--da-success-text);
        font-size: 0.88rem;
      }
      .da-form-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.85rem;
        margin-bottom: 1.25rem;
      }
      .da-field {
        display: flex;
        flex-direction: column;
        gap: 0.3rem;
        font-size: 0.82rem;
        color: var(--da-text-secondary);
      }
      .da-field--full {
        grid-column: 1 / -1;
      }
      .da-field input,
      .da-field select {
        padding: 0.5rem 0.65rem;
        border: 1px solid var(--da-border);
        border-radius: var(--da-radius-sm);
        font-family: inherit;
        font-size: 0.95rem;
      }
      .da-fields-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
      }
      .da-fields-head h4 {
        margin: 0;
        font-size: 0.95rem;
      }
      .da-input-sm {
        width: 100%;
        min-width: 0;
        padding: 0.35rem 0.45rem;
        border: 1px solid var(--da-border);
        border-radius: 6px;
        font-family: inherit;
        font-size: 0.82rem;
      }
    `,
  ],
})
export class SemanticModelsComponent implements OnInit {
  private readonly api = inject(SemanticService);
  private readonly http = inject(HttpClient);
  private readonly auth = inject(AuthService);
  private readonly tenantCtx = inject(TenantContextService);

  readonly rows = signal<SemanticModelItem[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly actionOk = signal<string | null>(null);
  readonly actionErr = signal<string | null>(null);
  readonly deletingId = signal<string | null>(null);

  readonly editorOpen = signal(false);
  readonly editingId = signal<string | null>(null);
  readonly saving = signal(false);
  readonly datasets = signal<DatasetOption[]>([]);

  formName = '';
  formDescription = '';
  formDatasetId = '';
  formFields: SemanticField[] = [];

  readonly canEdit = computed(() =>
    canEditBi(roleFromContext(this.tenantCtx.context(), this.auth.tenantRole())),
  );

  ngOnInit(): void {
    this.reload();
    this.loadDatasets();
  }

  reload(): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.list({ limit: 100, offset: 0 }).subscribe({
      next: (data) => {
        this.rows.set(data.items);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.error.set('Não foi possível carregar os modelos semânticos.');
      },
    });
  }

  loadDatasets(): void {
    const params = new HttpParams().set('limit', '100').set('offset', '0');
    this.http.get<PaginatedDatasets>(`${API_V1}/datasets`, { params }).subscribe({
      next: (data) => this.datasets.set(data.items ?? []),
      error: () => this.datasets.set([]),
    });
  }

  shortId(id: string): string {
    return id.length > 10 ? `${id.slice(0, 8)}…` : id;
  }

  openCreate(): void {
    this.editingId.set(null);
    this.formName = '';
    this.formDescription = '';
    this.formDatasetId = '';
    this.formFields = [EMPTY_FIELD()];
    this.editorOpen.set(true);
  }

  openEdit(row: SemanticModelItem): void {
    this.editingId.set(row.id);
    this.formName = row.name;
    this.formDescription = row.description ?? '';
    this.formDatasetId = row.dataset_id;
    this.formFields = (row.fields ?? []).map((f) => ({
      name: f.name,
      source_column: f.source_column,
      role: f.role as FieldRole,
      data_type: f.data_type || 'string',
      label: f.label ?? '',
    }));
    if (!this.formFields.length) {
      this.formFields = [EMPTY_FIELD()];
    }
    this.editorOpen.set(true);
  }

  closeEditor(): void {
    this.editorOpen.set(false);
  }

  addField(): void {
    this.formFields = [...this.formFields, EMPTY_FIELD()];
  }

  removeField(index: number): void {
    this.formFields = this.formFields.filter((_, i) => i !== index);
  }

  save(): void {
    const fields = this.formFields
      .map((f) => ({
        name: f.name.trim(),
        source_column: f.source_column.trim(),
        role: f.role,
        data_type: f.data_type || 'string',
        label: (f.label ?? '').toString().trim() || null,
      }))
      .filter((f) => f.name && f.source_column);

    if (!this.formName.trim() || !this.formDatasetId) {
      this.actionErr.set('Nome e dataset são obrigatórios.');
      return;
    }

    this.saving.set(true);
    this.actionErr.set(null);
    const id = this.editingId();
    if (id) {
      this.api
        .patch(id, {
          name: this.formName.trim(),
          description: this.formDescription.trim() || null,
          fields,
        })
        .subscribe({
          next: () => {
            this.saving.set(false);
            this.closeEditor();
            this.actionOk.set('Modelo atualizado.');
            this.reload();
          },
          error: (err: HttpErrorResponse) => {
            this.saving.set(false);
            this.actionErr.set(this.httpMsg(err, 'Falha ao atualizar o modelo.'));
          },
        });
    } else {
      this.api
        .create({
          name: this.formName.trim(),
          dataset_id: this.formDatasetId,
          description: this.formDescription.trim() || null,
          fields,
        })
        .subscribe({
          next: () => {
            this.saving.set(false);
            this.closeEditor();
            this.actionOk.set('Modelo criado.');
            this.reload();
          },
          error: (err: HttpErrorResponse) => {
            this.saving.set(false);
            this.actionErr.set(this.httpMsg(err, 'Falha ao criar o modelo.'));
          },
        });
    }
  }

  remove(row: SemanticModelItem): void {
    if (!confirm(`Remover o modelo «${row.name}»?`)) {
      return;
    }
    this.deletingId.set(row.id);
    this.api.delete(row.id).subscribe({
      next: () => {
        this.deletingId.set(null);
        this.actionOk.set('Modelo removido.');
        this.reload();
      },
      error: (err: HttpErrorResponse) => {
        this.deletingId.set(null);
        this.actionErr.set(this.httpMsg(err, 'Falha ao remover.'));
      },
    });
  }

  private httpMsg(err: HttpErrorResponse, fallback: string): string {
    if (err.error && typeof err.error === 'object' && 'detail' in err.error) {
      const d = (err.error as { detail: unknown }).detail;
      if (typeof d === 'string') {
        return d;
      }
    }
    return fallback;
  }
}
