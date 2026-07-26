import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { API_V1 } from '../../core/api-base';
import { TenantContextService } from '../../core/tenant-context.service';

interface DataSourceItem {
  id: string;
  name: string;
  connector_type: string;
  status: string;
  has_secret: boolean;
  updated_at: string;
}

@Component({
  selector: 'app-data-sources',
  imports: [DatePipe, FormsModule],
  template: `
    <section class="da-card">
      <h2 class="da-card__title">Fontes de dados</h2>
      <p class="da-card__sub">
        Conectores do tenant <strong>{{ tenantLabel() }}</strong>. Credenciais nunca são mostradas na listagem.
      </p>

      @if (canEdit()) {
        <form class="da-form" (ngSubmit)="create()">
          <label>
            Nome
            <input class="da-input" name="name" [(ngModel)]="name" required />
          </label>
          <label>
            Tipo
            <select class="da-input" name="type" [(ngModel)]="connectorType">
              <option value="file">Ficheiro</option>
              <option value="postgres">PostgreSQL</option>
              <option value="rest_json">REST JSON</option>
            </select>
          </label>
          <label>
            Segredo (opcional)
            <input class="da-input" name="secret" type="password" [(ngModel)]="secret" autocomplete="off" />
          </label>
          <button class="da-btn" type="submit" [disabled]="busy()">Adicionar fonte</button>
        </form>
      }

      @if (loading()) {
        <p class="da-muted">A carregar…</p>
      } @else if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
      } @else if (!rows().length) {
        <p class="da-muted">Nenhuma fonte registada. Use upload de ficheiro ou adicione um conector.</p>
      } @else {
        <div class="da-table-wrap">
          <table class="da-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Segredo</th>
                <th>Actualizado</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              @for (r of rows(); track r.id) {
                <tr>
                  <td>{{ r.name }}</td>
                  <td>{{ r.connector_type }}</td>
                  <td>{{ r.status }}</td>
                  <td>{{ r.has_secret ? 'sim' : 'não' }}</td>
                  <td>{{ r.updated_at | date: 'short' }}</td>
                  <td>
                    @if (canEdit()) {
                      <button type="button" class="da-btn da-btn--ghost" (click)="sync(r.id)" [disabled]="busy()">
                        Sync
                      </button>
                    }
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      }
      @if (notice()) {
        <p class="da-meta" role="status">{{ notice() }}</p>
      }
    </section>
  `,
  styles: [
    `
      .da-form {
        display: grid;
        gap: 0.75rem;
        margin: 1rem 0 1.5rem;
        max-width: 420px;
      }
      .da-form label {
        display: grid;
        gap: 0.35rem;
        font-size: 0.9rem;
      }
    `,
  ],
})
export class DataSourcesComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly tenantCtx = inject(TenantContextService);

  readonly rows = signal<DataSourceItem[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly busy = signal(false);
  readonly notice = signal<string | null>(null);

  name = '';
  connectorType: 'file' | 'postgres' | 'rest_json' = 'file';
  secret = '';

  tenantLabel(): string {
    const ctx = this.tenantCtx.context();
    return ctx?.tenant_name ?? ctx?.tenant_slug ?? '—';
  }

  canEdit(): boolean {
    const role = this.tenantCtx.context()?.role;
    return role === 'admin' || role === 'analyst';
  }

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.http.get<{ items: DataSourceItem[] }>(`${API_V1}/data-sources`).subscribe({
      next: (res) => {
        this.rows.set(res.items);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Não foi possível carregar as fontes.');
        this.loading.set(false);
      },
    });
  }

  create(): void {
    this.busy.set(true);
    this.notice.set(null);
    const config =
      this.connectorType === 'postgres'
        ? { host: 'localhost', database: 'demo', table: 'sales', limit: 100 }
        : this.connectorType === 'rest_json'
          ? { url: 'https://example.com/data.json', allowlist_hosts: ['example.com'], demo_fallback: true }
          : {};
    this.http
      .post(`${API_V1}/data-sources`, {
        name: this.name,
        connector_type: this.connectorType,
        config,
        secret: this.secret || null,
      })
      .subscribe({
        next: () => {
          this.name = '';
          this.secret = '';
          this.busy.set(false);
          this.reload();
        },
        error: () => {
          this.error.set('Falha ao criar fonte.');
          this.busy.set(false);
        },
      });
  }

  sync(id: string): void {
    this.busy.set(true);
    this.notice.set(null);
    this.http.post<{ status: string }>(`${API_V1}/data-sources/${id}/sync`, {}).subscribe({
      next: (res) => {
        this.notice.set(`Sync ${res.status}`);
        this.busy.set(false);
      },
      error: () => {
        this.error.set('Sync falhou.');
        this.busy.set(false);
      },
    });
  }
}
