import { DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AuthService } from '../../core/auth.service';
import {
  ConnectorCapability,
  ConnectorType,
  DataSourceCreate,
  DataSourceItem,
  DataSourcesService,
  SyncRunItem,
} from '../../core/data-sources.service';
import { canEditBi, roleFromContext } from '../../core/rbac';
import { TenantContextService } from '../../core/tenant-context.service';

type WizardStep = 'type' | 'config' | 'test' | 'save';

const CONNECTOR_LABELS: Record<ConnectorType, string> = {
  file: 'Ficheiro',
  postgres: 'PostgreSQL',
  mysql: 'MySQL',
  sqlserver: 'SQL Server',
  rest_json: 'API REST (JSON)',
  s3_compatible: 'Armazenamento S3-compatível',
};

@Component({
  selector: 'app-data-sources',
  imports: [DatePipe, FormsModule],
  template: `
    <section class="da-card">
      <div class="da-page-head">
        <div>
          <h2 class="da-card__title">Fontes de dados</h2>
          <p class="da-card__sub">
            Conectores do tenant — configurar, testar e sincronizar para o catálogo.
          </p>
        </div>
        <div class="da-page-head__actions">
          <button type="button" class="da-btn da-btn--ghost" (click)="reload()" [disabled]="loading()">
            Atualizar
          </button>
          @if (canEdit()) {
            <button type="button" class="da-btn da-btn--primary" (click)="openWizard()">
              Nova fonte
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
        <p class="da-muted">A carregar fontes…</p>
      } @else if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
      } @else if (!rows().length) {
        <div class="da-empty">
          <p class="da-muted">Ainda não há fontes de dados neste tenant.</p>
          @if (canEdit()) {
            <button type="button" class="da-btn da-btn--primary" (click)="openWizard()">
              Criar primeira fonte
            </button>
          }
        </div>
      } @else {
        <p class="da-meta">{{ rows().length }} fonte(s) · total API {{ total() }}</p>
        <div class="da-table-wrap">
          <table class="da-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Última sync</th>
                <th>Erro</th>
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
                    @if (r.has_secret) {
                      <span class="da-meta-chip" title="Credenciais configuradas">sec</span>
                    }
                  </td>
                  <td>{{ connectorLabel(r.connector_type) }}</td>
                  <td><span [class]="statusPill(r.status)">{{ statusLabel(r.status) }}</span></td>
                  <td class="da-cell-date">
                    {{ r.last_sync_at ? (r.last_sync_at | date: 'short') : '—' }}
                  </td>
                  <td class="da-cell-err">{{ r.last_error ?? '—' }}</td>
                  @if (canEdit()) {
                    <td class="da-td-actions">
                      <button
                        type="button"
                        class="da-btn da-btn--ghost da-btn--sm"
                        (click)="syncNow(r)"
                        [disabled]="syncingId() === r.id || r.status === 'syncing'"
                      >
                        {{ syncingId() === r.id ? 'A sync…' : 'Sincronizar' }}
                      </button>
                      <button
                        type="button"
                        class="da-btn da-btn--ghost da-btn--sm"
                        (click)="openHistory(r)"
                      >
                        Histórico
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

    @if (wizardOpen()) {
      <div class="da-modal-backdrop" (click)="closeWizard()" role="presentation"></div>
      <div class="da-modal" role="dialog" aria-modal="true" aria-labelledby="ds-wizard-title">
        <header class="da-modal__head">
          <h3 id="ds-wizard-title">Nova fonte de dados</h3>
          <button type="button" class="da-modal__close" (click)="closeWizard()" aria-label="Fechar">
            ×
          </button>
        </header>
        <div class="da-wizard-steps" aria-label="Passos">
          <span [class.active]="wizardStep() === 'type'">1. Tipo</span>
          <span [class.active]="wizardStep() === 'config'">2. Configuração</span>
          <span [class.active]="wizardStep() === 'test'">3. Teste</span>
          <span [class.active]="wizardStep() === 'save'">4. Guardar</span>
        </div>
        <div class="da-modal__body">
          @if (wizardStep() === 'type') {
            @if (connectorsLoading()) {
              <p class="da-muted">A carregar conectores…</p>
            } @else if (connectorsError()) {
              <p class="da-err">{{ connectorsError() }}</p>
            } @else if (!connectors().length) {
              <p class="da-muted">Nenhum conector disponível.</p>
            } @else {
              <div class="da-connector-grid">
                @for (c of connectors(); track c.connector_type) {
                  <button
                    type="button"
                    class="da-connector-card"
                    [class.da-connector-card--selected]="draftType() === c.connector_type"
                    (click)="selectConnector(c)"
                  >
                    <strong>{{ c.display_name || connectorLabel(c.connector_type) }}</strong>
                    <span>{{ c.description || '—' }}</span>
                  </button>
                }
              </div>
            }
          }
          @if (wizardStep() === 'config') {
            <div class="da-form-grid">
              <label class="da-field">
                <span>Nome</span>
                <input type="text" [(ngModel)]="draftName" maxlength="200" required />
              </label>
              @switch (draftType()) {
                @case ('postgres') {
                  <label class="da-field">
                    <span>Host</span>
                    <input type="text" [(ngModel)]="cfgHost" placeholder="db.exemplo.local" />
                  </label>
                  <label class="da-field">
                    <span>Porta</span>
                    <input type="number" [(ngModel)]="cfgPort" />
                  </label>
                  <label class="da-field">
                    <span>Base de dados</span>
                    <input type="text" [(ngModel)]="cfgDatabase" />
                  </label>
                  <label class="da-field">
                    <span>Utilizador</span>
                    <input type="text" [(ngModel)]="cfgUser" autocomplete="off" />
                  </label>
                  <label class="da-field">
                    <span>Palavra-passe</span>
                    <input type="password" [(ngModel)]="cfgPassword" autocomplete="new-password" />
                  </label>
                  <label class="da-field">
                    <span>Schema (opcional)</span>
                    <input type="text" [(ngModel)]="cfgSchema" placeholder="public" />
                  </label>
                }
                @case ('mysql') {
                  <label class="da-field">
                    <span>Host</span>
                    <input type="text" [(ngModel)]="cfgHost" />
                  </label>
                  <label class="da-field">
                    <span>Porta</span>
                    <input type="number" [(ngModel)]="cfgPort" />
                  </label>
                  <label class="da-field">
                    <span>Base de dados</span>
                    <input type="text" [(ngModel)]="cfgDatabase" />
                  </label>
                  <label class="da-field">
                    <span>Utilizador</span>
                    <input type="text" [(ngModel)]="cfgUser" autocomplete="off" />
                  </label>
                  <label class="da-field">
                    <span>Palavra-passe</span>
                    <input type="password" [(ngModel)]="cfgPassword" autocomplete="new-password" />
                  </label>
                }
                @case ('sqlserver') {
                  <label class="da-field">
                    <span>Host</span>
                    <input type="text" [(ngModel)]="cfgHost" />
                  </label>
                  <label class="da-field">
                    <span>Porta</span>
                    <input type="number" [(ngModel)]="cfgPort" />
                  </label>
                  <label class="da-field">
                    <span>Base de dados</span>
                    <input type="text" [(ngModel)]="cfgDatabase" />
                  </label>
                  <label class="da-field">
                    <span>Utilizador</span>
                    <input type="text" [(ngModel)]="cfgUser" autocomplete="off" />
                  </label>
                  <label class="da-field">
                    <span>Palavra-passe</span>
                    <input type="password" [(ngModel)]="cfgPassword" autocomplete="new-password" />
                  </label>
                }
                @case ('rest_json') {
                  <label class="da-field da-field--full">
                    <span>URL base</span>
                    <input type="url" [(ngModel)]="cfgUrl" placeholder="https://api.exemplo.com/v1" />
                  </label>
                  <label class="da-field">
                    <span>Método</span>
                    <select [(ngModel)]="cfgMethod">
                      <option value="GET">GET</option>
                      <option value="POST">POST</option>
                    </select>
                  </label>
                  <label class="da-field">
                    <span>API key / token (opcional)</span>
                    <input type="password" [(ngModel)]="cfgToken" autocomplete="new-password" />
                  </label>
                }
                @case ('s3_compatible') {
                  <label class="da-field da-field--full">
                    <span>Endpoint</span>
                    <input type="url" [(ngModel)]="cfgEndpoint" />
                  </label>
                  <label class="da-field">
                    <span>Bucket</span>
                    <input type="text" [(ngModel)]="cfgBucket" />
                  </label>
                  <label class="da-field">
                    <span>Prefixo (opcional)</span>
                    <input type="text" [(ngModel)]="cfgPrefix" />
                  </label>
                  <label class="da-field">
                    <span>Access key</span>
                    <input type="text" [(ngModel)]="cfgAccessKey" autocomplete="off" />
                  </label>
                  <label class="da-field">
                    <span>Secret key</span>
                    <input type="password" [(ngModel)]="cfgSecretKey" autocomplete="new-password" />
                  </label>
                }
                @case ('file') {
                  <label class="da-field da-field--full">
                    <span>Caminho / padrão (opcional)</span>
                    <input type="text" [(ngModel)]="cfgPath" placeholder="uploads/*.csv" />
                  </label>
                  <p class="da-muted">
                    Fontes do tipo ficheiro complementam o Upload existente; a sync cria ingestões no pipeline.
                  </p>
                }
                @default {
                  <p class="da-muted">Selecione um tipo de conector.</p>
                }
              }
            </div>
          }
          @if (wizardStep() === 'test') {
            <p class="da-card__sub">
              Teste a ligação antes de guardar. Credenciais não são devolvidas pela API após persistência.
            </p>
            @if (testResult(); as tr) {
              <p [class]="tr.ok ? 'da-inline-ok' : 'da-err'" role="status">{{ tr.message }}</p>
            }
            <button
              type="button"
              class="da-btn da-btn--ghost"
              (click)="runTest()"
              [disabled]="testing() || !draftName.trim()"
            >
              {{ testing() ? 'A testar…' : 'Testar ligação' }}
            </button>
          }
          @if (wizardStep() === 'save') {
            <dl class="da-summary">
              <div>
                <dt>Nome</dt>
                <dd>{{ draftName }}</dd>
              </div>
              <div>
                <dt>Tipo</dt>
                <dd>{{ draftType() ? connectorLabel(draftType()!) : '—' }}</dd>
              </div>
              <div>
                <dt>Teste</dt>
                <dd>{{ testResult()?.ok ? 'OK' : testResult() ? 'Falhou / não validado' : 'Não executado' }}</dd>
              </div>
            </dl>
            @if (saving()) {
              <p class="da-muted">A guardar…</p>
            }
          }
        </div>
        <footer class="da-modal__foot">
          <button type="button" class="da-btn da-btn--ghost" (click)="wizardBack()" [disabled]="wizardStep() === 'type'">
            Anterior
          </button>
          <div class="da-modal__foot-right">
            <button type="button" class="da-btn da-btn--ghost" (click)="closeWizard()">Cancelar</button>
            @if (wizardStep() !== 'save') {
              <button
                type="button"
                class="da-btn da-btn--primary"
                (click)="wizardNext()"
                [disabled]="!canWizardNext()"
              >
                Seguinte
              </button>
            } @else {
              <button
                type="button"
                class="da-btn da-btn--primary"
                (click)="saveSource()"
                [disabled]="saving() || !draftName.trim()"
              >
                {{ saving() ? 'A guardar…' : 'Guardar fonte' }}
              </button>
            }
          </div>
        </footer>
      </div>
    }

    @if (historyOpen()) {
      <div class="da-drawer-backdrop" (click)="closeHistory()" role="presentation"></div>
      <aside class="da-drawer" role="dialog" aria-labelledby="sync-hist-title">
        <header class="da-drawer__head">
          <div>
            <h3 id="sync-hist-title">Histórico de sincronização</h3>
            <p class="da-muted">{{ historySource()?.name }}</p>
          </div>
          <button type="button" class="da-modal__close" (click)="closeHistory()" aria-label="Fechar">
            ×
          </button>
        </header>
        <div class="da-drawer__body">
          @if (historyLoading()) {
            <p class="da-muted">A carregar…</p>
          } @else if (historyError()) {
            <p class="da-err">{{ historyError() }}</p>
          } @else if (!historyRuns().length) {
            <p class="da-muted">Sem execuções de sync para esta fonte.</p>
          } @else {
            <ul class="da-timeline">
              @for (run of historyRuns(); track run.id) {
                <li>
                  <span [class]="statusPill(run.status)">{{ run.status }}</span>
                  <div class="da-timeline__meta">
                    <strong>{{ run.friendly_message || 'Sync' }}</strong>
                    <span>{{ run.created_at | date: 'short' }}</span>
                    @if (run.object_id) {
                      <span class="da-code">{{ run.object_id }}</span>
                    }
                  </div>
                  @if (run.technical_log) {
                    <pre class="da-tech-log">{{ run.technical_log }}</pre>
                  }
                </li>
              }
            </ul>
          }
        </div>
      </aside>
    }
  `,
  styles: [
    `
      .da-page-head {
        display: flex;
        flex-wrap: wrap;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.5rem;
      }
      .da-page-head__actions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
      }
      .da-empty {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.75rem;
      }
      .da-meta-chip {
        margin-left: 0.35rem;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--da-text-muted);
        border: 1px solid var(--da-border);
        border-radius: 4px;
        padding: 0.1rem 0.3rem;
      }
      .da-cell-err {
        max-width: 180px;
        word-break: break-word;
        color: var(--da-warning-text);
        font-size: 0.85rem;
      }
      .da-cell-date {
        white-space: nowrap;
        color: var(--da-text-secondary);
      }
      .da-th-actions,
      .da-td-actions {
        white-space: nowrap;
      }
      .da-td-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
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
      .da-connector-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 0.75rem;
      }
      .da-connector-card {
        text-align: left;
        padding: 0.9rem 1rem;
        border-radius: var(--da-radius-sm);
        border: 1px solid var(--da-border);
        background: #fff;
        cursor: pointer;
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
        font-family: inherit;
      }
      .da-connector-card span {
        font-size: 0.8rem;
        color: var(--da-text-secondary);
        line-height: 1.35;
      }
      .da-connector-card--selected,
      .da-connector-card:hover {
        border-color: rgba(233, 30, 99, 0.45);
        box-shadow: 0 0 0 2px rgba(233, 30, 99, 0.12);
      }
      .da-form-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.85rem;
      }
      @media (max-width: 640px) {
        .da-form-grid {
          grid-template-columns: 1fr;
        }
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
      .da-summary {
        margin: 0;
        display: grid;
        gap: 0.75rem;
      }
      .da-summary dt {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--da-text-muted);
      }
      .da-summary dd {
        margin: 0.15rem 0 0;
        font-weight: 600;
      }
      .da-timeline {
        list-style: none;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        gap: 1rem;
      }
      .da-timeline__meta {
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
        margin-top: 0.35rem;
        font-size: 0.85rem;
        color: var(--da-text-secondary);
      }
      .da-tech-log {
        margin: 0.4rem 0 0;
        padding: 0.5rem 0.65rem;
        background: #f8fafc;
        border: 1px solid var(--da-border);
        border-radius: 6px;
        font-size: 0.72rem;
        overflow-x: auto;
        max-height: 120px;
      }
    `,
  ],
})
export class DataSourcesComponent implements OnInit {
  private readonly api = inject(DataSourcesService);
  private readonly auth = inject(AuthService);
  private readonly tenantCtx = inject(TenantContextService);

  readonly rows = signal<DataSourceItem[]>([]);
  readonly total = signal(0);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly actionOk = signal<string | null>(null);
  readonly actionErr = signal<string | null>(null);
  readonly syncingId = signal<string | null>(null);

  readonly wizardOpen = signal(false);
  readonly wizardStep = signal<WizardStep>('type');
  readonly connectors = signal<ConnectorCapability[]>([]);
  readonly connectorsLoading = signal(false);
  readonly connectorsError = signal<string | null>(null);
  readonly draftType = signal<ConnectorType | null>(null);
  readonly testing = signal(false);
  readonly testResult = signal<{ ok: boolean; message: string } | null>(null);
  readonly saving = signal(false);

  draftName = '';
  cfgHost = '';
  cfgPort = 5432;
  cfgDatabase = '';
  cfgUser = '';
  cfgPassword = '';
  cfgSchema = '';
  cfgUrl = '';
  cfgMethod = 'GET';
  cfgToken = '';
  cfgEndpoint = '';
  cfgBucket = '';
  cfgPrefix = '';
  cfgAccessKey = '';
  cfgSecretKey = '';
  cfgPath = '';

  readonly historyOpen = signal(false);
  readonly historySource = signal<DataSourceItem | null>(null);
  readonly historyRuns = signal<SyncRunItem[]>([]);
  readonly historyLoading = signal(false);
  readonly historyError = signal<string | null>(null);

  readonly canEdit = computed(() =>
    canEditBi(roleFromContext(this.tenantCtx.context(), this.auth.tenantRole())),
  );

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.list({ limit: 100, offset: 0 }).subscribe({
      next: (data) => {
        this.rows.set(data.items);
        this.total.set(data.total);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.error.set('Não foi possível carregar as fontes de dados.');
      },
    });
  }

  connectorLabel(t: ConnectorType): string {
    return CONNECTOR_LABELS[t] ?? t;
  }

  statusLabel(s: string): string {
    const map: Record<string, string> = {
      ready: 'pronta',
      syncing: 'a sincronizar',
      error: 'erro',
      disabled: 'desativada',
    };
    return map[s] ?? s;
  }

  statusPill(status: string): string {
    const mod: Record<string, string> = {
      ready: 'da-pill da-pill--processed',
      processed: 'da-pill da-pill--processed',
      syncing: 'da-pill da-pill--parsing',
      running: 'da-pill da-pill--parsing',
      queued: 'da-pill da-pill--uploaded',
      uploaded: 'da-pill da-pill--uploaded',
      validating: 'da-pill da-pill--validating',
      parsing: 'da-pill da-pill--parsing',
      error: 'da-pill da-pill--failed',
      failed: 'da-pill da-pill--failed',
      disabled: 'da-pill',
    };
    return mod[status] ?? 'da-pill';
  }

  openWizard(): void {
    this.resetDraft();
    this.wizardOpen.set(true);
    this.wizardStep.set('type');
    this.loadConnectors();
  }

  closeWizard(): void {
    this.wizardOpen.set(false);
  }

  loadConnectors(): void {
    this.connectorsLoading.set(true);
    this.connectorsError.set(null);
    this.api.listConnectors().subscribe({
      next: (res) => {
        this.connectors.set(res.items ?? []);
        this.connectorsLoading.set(false);
      },
      error: () => {
        this.connectorsLoading.set(false);
        this.connectorsError.set('Não foi possível carregar o catálogo de conectores.');
        this.connectors.set(
          (['file', 'postgres', 'mysql', 'sqlserver', 'rest_json', 's3_compatible'] as ConnectorType[]).map(
            (connector_type) => ({
              connector_type,
              display_name: CONNECTOR_LABELS[connector_type],
              description: 'Conector 4Pro_BI',
              auth_kinds: [],
              supports_incremental: false,
              supports_discover: true,
              max_sample_rows: 100,
              config_schema_hint: {},
            }),
          ),
        );
      },
    });
  }

  selectConnector(c: ConnectorCapability): void {
    this.draftType.set(c.connector_type);
    if (c.connector_type === 'mysql') {
      this.cfgPort = 3306;
    } else if (c.connector_type === 'sqlserver') {
      this.cfgPort = 1433;
    } else if (c.connector_type === 'postgres') {
      this.cfgPort = 5432;
    }
  }

  canWizardNext(): boolean {
    const step = this.wizardStep();
    if (step === 'type') {
      return this.draftType() != null;
    }
    if (step === 'config') {
      return this.draftName.trim().length > 0 && this.draftType() != null;
    }
    return true;
  }

  wizardNext(): void {
    const order: WizardStep[] = ['type', 'config', 'test', 'save'];
    const i = order.indexOf(this.wizardStep());
    if (i < order.length - 1 && this.canWizardNext()) {
      this.wizardStep.set(order[i + 1]);
    }
  }

  wizardBack(): void {
    const order: WizardStep[] = ['type', 'config', 'test', 'save'];
    const i = order.indexOf(this.wizardStep());
    if (i > 0) {
      this.wizardStep.set(order[i - 1]);
    }
  }

  runTest(): void {
    const body = this.buildCreateBody();
    if (!body) {
      return;
    }
    this.testing.set(true);
    this.testResult.set(null);
    this.api.testDraft(body).subscribe({
      next: (res) => {
        this.testing.set(false);
        this.testResult.set({ ok: res.ok, message: res.message });
      },
      error: (err: HttpErrorResponse) => {
        this.testing.set(false);
        const msg =
          (err.error && typeof err.error === 'object' && 'detail' in err.error
            ? String((err.error as { detail: unknown }).detail)
            : null) || 'Teste indisponível (API). Pode guardar e testar após criar a fonte.';
        this.testResult.set({ ok: false, message: msg });
      },
    });
  }

  saveSource(): void {
    const body = this.buildCreateBody();
    if (!body) {
      return;
    }
    this.saving.set(true);
    this.actionErr.set(null);
    this.api.create(body).subscribe({
      next: () => {
        this.saving.set(false);
        this.closeWizard();
        this.actionOk.set('Fonte de dados criada com sucesso.');
        this.reload();
      },
      error: (err: HttpErrorResponse) => {
        this.saving.set(false);
        this.actionErr.set(this.httpMsg(err, 'Não foi possível criar a fonte.'));
      },
    });
  }

  syncNow(row: DataSourceItem): void {
    this.syncingId.set(row.id);
    this.actionOk.set(null);
    this.actionErr.set(null);
    this.api.sync(row.id, { mode: 'full' }).subscribe({
      next: (res) => {
        this.syncingId.set(null);
        this.actionOk.set(res.message || 'Sincronização enfileirada.');
        this.reload();
      },
      error: (err: HttpErrorResponse) => {
        this.syncingId.set(null);
        this.actionErr.set(this.httpMsg(err, 'Falha ao iniciar sincronização.'));
      },
    });
  }

  openHistory(row: DataSourceItem): void {
    this.historySource.set(row);
    this.historyOpen.set(true);
    this.historyLoading.set(true);
    this.historyError.set(null);
    this.api.listSyncRuns(row.id, { limit: 50, offset: 0 }).subscribe({
      next: (data) => {
        this.historyRuns.set(data.items);
        this.historyLoading.set(false);
      },
      error: () => {
        this.historyLoading.set(false);
        this.historyError.set('Não foi possível carregar o histórico de sync.');
      },
    });
  }

  closeHistory(): void {
    this.historyOpen.set(false);
    this.historySource.set(null);
  }

  private buildCreateBody(): DataSourceCreate | null {
    const type = this.draftType();
    const name = this.draftName.trim();
    if (!type || !name) {
      return null;
    }
    const config: Record<string, unknown> = {};
    let secret: Record<string, string> | undefined;

    switch (type) {
      case 'postgres':
      case 'mysql':
      case 'sqlserver':
        config['host'] = this.cfgHost.trim();
        config['port'] = Number(this.cfgPort) || 0;
        config['database'] = this.cfgDatabase.trim();
        config['user'] = this.cfgUser.trim();
        if (type === 'postgres' && this.cfgSchema.trim()) {
          config['schema'] = this.cfgSchema.trim();
        }
        if (this.cfgPassword) {
          secret = { password: this.cfgPassword };
        }
        break;
      case 'rest_json':
        config['base_url'] = this.cfgUrl.trim();
        config['method'] = this.cfgMethod;
        if (this.cfgToken) {
          secret = { token: this.cfgToken };
        }
        break;
      case 's3_compatible':
        config['endpoint'] = this.cfgEndpoint.trim();
        config['bucket'] = this.cfgBucket.trim();
        if (this.cfgPrefix.trim()) {
          config['prefix'] = this.cfgPrefix.trim();
        }
        if (this.cfgAccessKey || this.cfgSecretKey) {
          secret = {
            access_key: this.cfgAccessKey,
            secret_key: this.cfgSecretKey,
          };
        }
        break;
      case 'file':
        if (this.cfgPath.trim()) {
          config['path'] = this.cfgPath.trim();
        }
        break;
      default: {
        const _exhaustive: never = type;
        void _exhaustive;
        break;
      }
    }

    return { name, connector_type: type, config, secret: secret ?? null };
  }

  private resetDraft(): void {
    this.draftType.set(null);
    this.draftName = '';
    this.cfgHost = '';
    this.cfgPort = 5432;
    this.cfgDatabase = '';
    this.cfgUser = '';
    this.cfgPassword = '';
    this.cfgSchema = '';
    this.cfgUrl = '';
    this.cfgMethod = 'GET';
    this.cfgToken = '';
    this.cfgEndpoint = '';
    this.cfgBucket = '';
    this.cfgPrefix = '';
    this.cfgAccessKey = '';
    this.cfgSecretKey = '';
    this.cfgPath = '';
    this.testResult.set(null);
    this.testing.set(false);
    this.saving.set(false);
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
