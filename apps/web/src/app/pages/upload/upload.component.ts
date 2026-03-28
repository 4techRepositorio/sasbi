import { Component, ElementRef, inject, signal, viewChild } from '@angular/core';
import { RouterLink } from '@angular/router';

import { formatBytes } from '../../core/format-bytes';
import { TenantContextService } from '../../core/tenant-context.service';
import { UploadService, type UploadResult } from '../../core/upload.service';
import { StorageQuotaBlockComponent } from '../../shared';

function formatUploadError(err: unknown): string {
  const e = err as { error?: { detail?: unknown }; status?: number };
  const d = e?.error?.detail;
  if (typeof d === 'string') {
    return d;
  }
  if (Array.isArray(d)) {
    return d.map((x) => (typeof x === 'object' && x && 'msg' in x ? String((x as { msg: string }).msg) : JSON.stringify(x))).join('; ');
  }
  if (d && typeof d === 'object') {
    const o = d as Record<string, unknown>;
    if (typeof o['error'] === 'string') {
      const allowed = o['allowed'];
      if (Array.isArray(allowed)) {
        return `${o['error']} Tipos permitidos: ${allowed.join(', ')}.`;
      }
      return o['error'];
    }
  }
  if (e?.status === 413) {
    return 'O ficheiro excede o tamanho máximo permitido pelo servidor.';
  }
  if (e?.status === 403) {
    return 'Não tem permissão para enviar ficheiros neste perfil.';
  }
  if (e?.status === 402) {
    if (typeof d === 'string') {
      return d;
    }
    return 'Plano inativo ou limite do pacote esgotado (uploads ou armazenamento). Contacte o administrador.';
  }
  return 'Não foi possível concluir o envio. Verifique a ligação e os limites do plano.';
}

@Component({
  selector: 'app-upload',
  imports: [RouterLink, StorageQuotaBlockComponent],
  template: `
    <section class="da-card da-upload" [attr.aria-busy]="uploading()">
      <h2 class="da-card__title">Upload de ficheiro</h2>
      @if (tenantCtx.context(); as ctx) {
        <p class="da-meta">
          Envio para o tenant:
          <strong>{{ ctx.tenant_name ?? ctx.tenant_slug ?? ctx.tenant_id }}</strong>
        </p>
        @if (ctx.storage; as st) {
          <app-storage-quota-block [storage]="st" variant="card" metaStyle="verbose" />
        }
      }
      <p class="da-card__sub">
        Formatos: CSV, TXT, JSON, XLS, XLSX. O servidor valida extensão e conteúdo.
        <strong>Recebido não significa processado</strong> — o estado da ingestão aparece em Ingestões.
      </p>

      @if (result(); as res) {
        <div class="da-upload-success" role="status">
          <p class="da-upload-success__title">Ficheiro recebido com sucesso</p>
          <ul class="da-upload-success__list">
            <li><span class="da-muted">Ficheiro</span> {{ res.original_filename }}</li>
            <li><span class="da-muted">Tamanho</span> {{ formatBytes(res.size_bytes) }}</li>
            <li>
              <span class="da-muted">ID de ingestão</span>
              <code class="da-code">{{ res.id }}</code>
            </li>
            <li>
              <span class="da-muted">Estado</span>
              <span class="da-pill da-pill--uploaded">{{ res.status }}</span>
            </li>
          </ul>
          <p class="da-upload-success__async">
            O processamento corre em segundo plano; o estado actualiza-se em
            <a routerLink="/app/ingestions">Ingestões</a>.
          </p>
          <div class="da-upload-success__actions">
            <button type="button" class="da-btn da-btn--primary" (click)="startAnother()">Enviar outro ficheiro</button>
            <a routerLink="/app/ingestions" class="da-btn da-btn--ghost da-upload-link">Ver em Ingestões</a>
          </div>
        </div>
      } @else {
        <div class="da-upload-body">
          @if (!file()) {
            <div class="da-upload-empty">
              <p class="da-upload-empty__title">Nenhum ficheiro selecionado</p>
              <p class="da-upload-empty__hint">
                Escolha um ficheiro suportado para iniciar o envio. Tipos aceites: csv, txt, json, xls, xlsx.
              </p>
            </div>
          } @else {
            <div class="da-upload-file">
              <p class="da-upload-file__name">{{ file()!.name }}</p>
              <p class="da-upload-file__meta">{{ formatBytes(file()!.size) }}</p>
              <button type="button" class="da-btn da-btn--ghost da-upload-file__change" (click)="clearPick()" [disabled]="uploading()">
                Alterar ficheiro
              </button>
            </div>
          }

          <input
            #fileInput
            type="file"
            class="da-upload-input"
            accept=".csv,.txt,.json,.xlsx,.xls,text/csv,text/plain,application/json"
            (change)="onPick($event)"
            [disabled]="uploading()"
          />

          <div class="da-upload-row da-upload-row--actions">
            <button type="button" class="da-btn da-btn--ghost" (click)="triggerPick()" [disabled]="uploading()">
              {{ file() ? 'Escolher outro…' : 'Escolher ficheiro…' }}
            </button>
            <button
              type="button"
              class="da-btn da-btn--primary"
              (click)="upload()"
              [disabled]="!file() || uploading()"
            >
              Enviar
            </button>
          </div>
        </div>

        @if (uploading()) {
          <div class="da-upload-loading">
            <span class="da-upload-spinner" aria-hidden="true"></span>
            <p class="da-upload-loading__text">A enviar o ficheiro…</p>
            <p class="da-upload-loading__sub">Não feche esta página até concluir.</p>
          </div>
        }

        @if (error()) {
          <p class="da-err da-upload-err" role="alert">{{ error() }}</p>
        }
      }
    </section>
  `,
  styles: [
    `
      .da-upload {
        position: relative;
      }
      .da-upload-body {
        display: flex;
        flex-direction: column;
        gap: 1rem;
      }
      .da-upload-input {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        border: 0;
      }
      .da-upload-empty {
        text-align: center;
        padding: 1.75rem 1rem;
        border: 2px dashed var(--da-border);
        border-radius: var(--da-radius-sm);
        background: #f8fafc;
      }
      .da-upload-empty__title {
        margin: 0 0 0.35rem;
        font-family: var(--da-font-display);
        font-weight: 600;
        font-size: 1rem;
        color: var(--da-text-secondary);
      }
      .da-upload-empty__hint {
        margin: 0;
        font-size: 0.85rem;
        color: var(--da-text-muted);
        max-width: 36rem;
        margin-inline: auto;
        line-height: 1.45;
      }
      .da-upload-file {
        padding: 1rem 1.1rem;
        border-radius: var(--da-radius-sm);
        border: 1px solid var(--da-border);
        background: #f8fafc;
      }
      .da-upload-file__name {
        margin: 0 0 0.25rem;
        font-weight: 600;
        font-size: 0.95rem;
        word-break: break-word;
      }
      .da-upload-file__meta {
        margin: 0 0 0.65rem;
        font-size: 0.82rem;
        color: var(--da-text-muted);
      }
      .da-upload-file__change {
        font-size: 0.82rem;
        padding: 0.35rem 0.75rem;
      }
      .da-upload-row--actions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        align-items: center;
      }
      .da-upload-loading {
        margin-top: 1rem;
        padding: 1rem 1.1rem;
        border-radius: var(--da-radius-sm);
        background: rgba(6, 182, 212, 0.08);
        border: 1px solid rgba(6, 182, 212, 0.25);
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.75rem 1rem;
      }
      .da-upload-spinner {
        width: 1.35rem;
        height: 1.35rem;
        border: 3px solid rgba(6, 182, 212, 0.25);
        border-top-color: var(--da-accent);
        border-radius: 50%;
        animation: da-upload-spin 0.7s linear infinite;
        flex-shrink: 0;
      }
      @keyframes da-upload-spin {
        to {
          transform: rotate(360deg);
        }
      }
      .da-upload-loading__text {
        margin: 0;
        font-weight: 600;
        color: var(--da-accent-hover);
        font-size: 0.9rem;
      }
      .da-upload-loading__sub {
        margin: 0;
        width: 100%;
        flex-basis: 100%;
        font-size: 0.8rem;
        color: var(--da-text-muted);
        padding-left: calc(1.35rem + 0.75rem);
      }
      .da-upload-err {
        margin-top: 1rem;
        margin-bottom: 0;
      }
      .da-upload-success {
        margin-top: 0.25rem;
        padding: 1.1rem 1.2rem;
        border-radius: var(--da-radius-sm);
        background: var(--da-success-bg);
        border: 1px solid rgba(22, 101, 52, 0.2);
      }
      .da-upload-success__title {
        margin: 0 0 0.75rem;
        font-weight: 600;
        color: var(--da-success-text);
        font-size: 1rem;
      }
      .da-upload-success__async {
        margin: 0 0 0.85rem;
        font-size: 0.88rem;
        line-height: 1.45;
        color: var(--da-text-secondary);
      }
      .da-upload-success__async a {
        font-weight: 600;
        color: var(--da-accent-hover);
      }
      .da-upload-success__list {
        margin: 0 0 1rem;
        padding-left: 1.1rem;
        color: var(--da-text);
        font-size: 0.9rem;
        line-height: 1.6;
      }
      .da-upload-success__list li {
        margin-bottom: 0.25rem;
      }
      .da-upload-success__actions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
      }
      .da-upload-link {
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }
    `,
  ],
})
export class UploadComponent {
  readonly tenantCtx = inject(TenantContextService);
  private readonly uploadApi = inject(UploadService);
  private readonly fileInput = viewChild.required<ElementRef<HTMLInputElement>>('fileInput');

  readonly file = signal<File | null>(null);
  readonly uploading = signal(false);
  readonly error = signal<string | null>(null);
  readonly result = signal<UploadResult | null>(null);

  readonly formatBytes = formatBytes;

  triggerPick(): void {
    this.fileInput().nativeElement.click();
  }

  onPick(ev: Event): void {
    this.error.set(null);
    const input = ev.target as HTMLInputElement;
    const f = input.files?.[0];
    this.file.set(f ?? null);
  }

  clearPick(): void {
    this.error.set(null);
    this.file.set(null);
    this.fileInput().nativeElement.value = '';
  }

  startAnother(): void {
    this.result.set(null);
    this.clearPick();
  }

  upload(): void {
    const f = this.file();
    if (!f) {
      return;
    }
    this.uploading.set(true);
    this.error.set(null);
    this.uploadApi.uploadFile(f).subscribe({
      next: (body) => {
        this.uploading.set(false);
        this.result.set(body);
        this.file.set(null);
        this.fileInput().nativeElement.value = '';
        this.tenantCtx.load().subscribe({ error: () => undefined });
      },
      error: (err: unknown) => {
        this.uploading.set(false);
        this.error.set(formatUploadError(err));
      },
    });
  }
}
