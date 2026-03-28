import { DecimalPipe } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';

import { TenantContextService } from '../../core/tenant-context.service';

@Component({
  selector: 'app-billing-overview',
  imports: [DecimalPipe],
  template: `
    <div class="da-card">
      <h1 class="da-card__title">Cobrança e pacote</h1>
      <p class="da-card__sub">
        Resumo do plano associado ao tenant — alinhado à navegação do PDF (área Cobrança).
      </p>
      @if (loading()) {
        <p class="da-muted">A carregar…</p>
      } @else if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
      } @else {
        @if (tenantCtx.context(); as ctx) {
          @if (ctx.plan; as pl) {
            <dl class="da-billing-dl">
              <dt>Pacote</dt>
              <dd>{{ pl.name }} <span class="da-muted">({{ pl.code }})</span></dd>
              <dt>Uploads por mês (limite)</dt>
              <dd>{{ pl.max_uploads_per_month | number }}</dd>
              <dt>Armazenamento (MB)</dt>
              <dd>{{ pl.max_storage_mb | number }}</dd>
            </dl>
          } @else {
            <p class="da-muted">Nenhum plano associado a este tenant.</p>
          }
        } @else {
          <p class="da-muted">Sem contexto do tenant.</p>
        }
      }
    </div>
  `,
  styles: [
    `
      .da-billing-dl {
        display: grid;
        grid-template-columns: 200px 1fr;
        gap: 0.65rem 1.25rem;
        margin: 0;
        font-size: 0.9rem;
      }
      .da-billing-dl dt {
        margin: 0;
        color: var(--da-text-muted);
        font-weight: 600;
      }
      .da-billing-dl dd {
        margin: 0;
        color: var(--da-text);
      }
    `,
  ],
})
export class BillingOverviewComponent implements OnInit {
  readonly tenantCtx = inject(TenantContextService);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  ngOnInit(): void {
    if (this.tenantCtx.context()) {
      this.loading.set(false);
      return;
    }
    this.tenantCtx.load().subscribe({
      next: () => {
        this.loading.set(false);
        this.error.set(null);
      },
      error: () => {
        this.loading.set(false);
        this.error.set('Não foi possível carregar o contexto.');
      },
    });
  }
}
