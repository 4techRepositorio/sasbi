import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, inject, OnInit, signal } from '@angular/core';

import { API_V1 } from '../../core/api-base';

interface TenantMemberItem {
  user_id: string;
  email: string;
  role: string;
  is_active: boolean;
  membership_created_at: string;
}

interface TenantMemberListResponse {
  items: TenantMemberItem[];
}

@Component({
  selector: 'app-tenant-users',
  imports: [DatePipe],
  template: `
    <section class="da-card">
      <h2 class="da-card__title">Membros do tenant</h2>
      <p class="da-card__sub">
        Utilizadores com acesso a esta organização e respetivo papel (apenas administradores).
      </p>
      <div class="da-toolbar">
        <button type="button" class="da-btn da-btn--ghost" (click)="reload()" [disabled]="loading()">
          Atualizar
        </button>
      </div>
      @if (loading()) {
        <p class="da-muted">A carregar…</p>
      } @else if (error()) {
        <p class="da-err" role="alert">{{ error() }}</p>
      } @else if (!rows().length) {
        <p class="da-muted">Nenhum membro encontrado.</p>
      } @else {
        <div class="da-table-wrap">
          <table class="da-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Papel</th>
                <th>Ativo</th>
                <th>Membro desde</th>
              </tr>
            </thead>
            <tbody>
              @for (r of rows(); track r.user_id) {
                <tr>
                  <td>{{ r.email }}</td>
                  <td><span class="da-pill da-pill--role">{{ r.role }}</span></td>
                  <td>{{ r.is_active ? 'Sim' : 'Não' }}</td>
                  <td class="da-cell-date">{{ r.membership_created_at | date: 'short' }}</td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      }
    </section>
  `,
  styles: [
    `
      .da-pill--role {
        background: rgba(6, 182, 212, 0.12);
        color: var(--da-accent-hover);
        text-transform: lowercase;
      }
      .da-cell-date {
        white-space: nowrap;
        color: var(--da-text-secondary);
        font-size: 0.88rem;
      }
    `,
  ],
})
export class TenantUsersComponent implements OnInit {
  private readonly http = inject(HttpClient);

  readonly rows = signal<TenantMemberItem[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.error.set(null);
    this.http.get<TenantMemberListResponse>(`${API_V1}/tenant/members`).subscribe({
      next: (res) => {
        this.rows.set(res.items ?? []);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.error.set('Não foi possível carregar os membros ou permissão insuficiente.');
      },
    });
  }
}
