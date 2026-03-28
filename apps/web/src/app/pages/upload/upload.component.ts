import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { API_V1 } from '../../core/api-base';

@Component({
  selector: 'app-upload',
  template: `
    <section class="da-card">
      <h2 class="da-card__title">Upload de ficheiro</h2>
      <p class="da-card__sub">
        Tipos: CSV, TXT, JSON, XLS, XLSX. O servidor valida conteúdo e tipo.
        <strong>Recebido não significa processado</strong> — o estado segue em Ingestões.
      </p>
      <div class="da-upload-row">
        <input type="file" (change)="onPick($event)" [disabled]="uploading()" />
        <button type="button" class="da-btn da-btn--primary" (click)="upload()" [disabled]="!file() || uploading()">
          Enviar
        </button>
      </div>
      @if (uploading()) {
        <p class="da-info">A enviar…</p>
      }
      @if (message()) {
        <pre class="da-ok">{{ message() }}</pre>
      }
      @if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
      }
    </section>
  `,
  styles: [``],
})
export class UploadComponent {
  private readonly http = inject(HttpClient);

  readonly file = signal<File | null>(null);
  readonly uploading = signal(false);
  readonly message = signal<string | null>(null);
  readonly error = signal<string | null>(null);

  onPick(ev: Event): void {
    this.message.set(null);
    this.error.set(null);
    const input = ev.target as HTMLInputElement;
    const f = input.files?.[0];
    this.file.set(f ?? null);
  }

  upload(): void {
    const f = this.file();
    if (!f) {
      return;
    }
    const fd = new FormData();
    fd.append('file', f, f.name);
    this.uploading.set(true);
    this.message.set(null);
    this.error.set(null);
    this.http.post<Record<string, unknown>>(`${API_V1}/uploads`, fd).subscribe({
      next: (body) => {
        this.uploading.set(false);
        this.message.set(JSON.stringify(body, null, 2));
        this.file.set(null);
      },
      error: (err: { error?: { detail?: unknown } }) => {
        this.uploading.set(false);
        const d = err?.error?.detail;
        if (typeof d === 'string') {
          this.error.set(d);
        } else if (d && typeof d === 'object') {
          this.error.set(JSON.stringify(d));
        } else {
          this.error.set('Falha no upload. Verifique permissões e limites do plano.');
        }
      },
    });
  }
}
