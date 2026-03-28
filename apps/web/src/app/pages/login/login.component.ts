import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';
import { TenantContextService } from '../../core/tenant-context.service';

@Component({
  selector: 'app-login',
  imports: [FormsModule, RouterLink],
  template: `
    <div class="da-auth-layout">
      <div class="da-auth-hero">
        <div class="da-auth-hero__inner">
          <p class="da-auth-hero__product">4Pro_BI</p>
          <h2 class="da-auth-hero__title">Data analytics multitenant</h2>
          <p class="da-auth-hero__text">
            Upload, ingestão e catálogo de dados por organização — base alinhada ao workspace
            <span class="da-hero-ref">Data Analytics Solution</span>.
          </p>
        </div>
      </div>
      <div class="da-auth-panel">
        <div class="da-auth-card">
          <h1>Iniciar sessão</h1>
          <p class="hint">Credenciais do tenant (email e senha).</p>
          @if (step() === 'login') {
            <form (ngSubmit)="onLogin()">
              <label>
                <span>Email</span>
                <input
                  name="email"
                  type="email"
                  [(ngModel)]="email"
                  required
                  autocomplete="username"
                />
              </label>
              <label>
                <span>Senha</span>
                <input
                  name="password"
                  type="password"
                  [(ngModel)]="password"
                  required
                  autocomplete="current-password"
                />
              </label>
              <button type="submit" class="da-btn da-btn--primary" [disabled]="loading()">Entrar</button>
              <p class="links">
                <a routerLink="/forgot-password">Esqueci a senha</a>
                ·
                <a routerLink="/reset-password">Redefinir com token</a>
              </p>
            </form>
          } @else {
            <form (ngSubmit)="onMfa()">
              <label>
                <span>Código MFA</span>
                <input name="code" [(ngModel)]="mfaCode" required autocomplete="one-time-code" />
              </label>
              <button type="submit" class="da-btn da-btn--primary" [disabled]="loading()">Confirmar</button>
              <button type="button" class="da-btn da-btn--ghost" (click)="cancelMfa()" [disabled]="loading()">
                Voltar
              </button>
            </form>
          }
          @if (error()) {
            <p class="error" role="alert">{{ error() }}</p>
          }
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      .da-hero-ref {
        display: block;
        margin-top: 0.75rem;
        font-size: 0.85rem;
        color: rgba(148, 163, 184, 0.95);
      }
    `,
  ],
})
export class LoginComponent {
  private readonly auth = inject(AuthService);
  private readonly tenantCtx = inject(TenantContextService);
  private readonly router = inject(Router);

  email = '';
  password = '';
  mfaCode = '';
  readonly step = signal<'login' | 'mfa'>('login');
  private mfaToken = '';
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);

  onLogin(): void {
    this.error.set(null);
    this.loading.set(true);
    this.auth.login(this.email.trim(), this.password).subscribe({
      next: (res) => {
        this.loading.set(false);
        if (res['mfa_required'] === true) {
          this.mfaToken = String(res['mfa_token'] ?? '');
          this.step.set('mfa');
          return;
        }
        if (typeof res['access_token'] === 'string' && typeof res['refresh_token'] === 'string') {
          this.auth.setSession({
            access_token: res['access_token'],
            refresh_token: res['refresh_token'],
            role: typeof res['role'] === 'string' ? res['role'] : null,
          });
          this.tenantCtx.clear();
          void this.router.navigateByUrl('/app');
          return;
        }
        this.error.set('Resposta inesperada do servidor.');
      },
      error: (err: { error?: { detail?: string } }) => {
        this.loading.set(false);
        const d = err?.error?.detail;
        this.error.set(typeof d === 'string' ? d : 'Não foi possível iniciar sessão.');
      },
    });
  }

  onMfa(): void {
    this.error.set(null);
    this.loading.set(true);
    this.auth.verifyMfa(this.mfaToken, this.mfaCode.trim()).subscribe({
      next: (res) => {
        this.loading.set(false);
        if (typeof res['access_token'] === 'string' && typeof res['refresh_token'] === 'string') {
          this.auth.setSession({
            access_token: res['access_token'],
            refresh_token: res['refresh_token'],
            role: typeof res['role'] === 'string' ? res['role'] : null,
          });
          this.tenantCtx.clear();
          void this.router.navigateByUrl('/app');
          return;
        }
        this.error.set('Resposta inesperada do servidor.');
      },
      error: (err: { error?: { detail?: string } }) => {
        this.loading.set(false);
        const d = err?.error?.detail;
        this.error.set(typeof d === 'string' ? d : 'Código inválido.');
      },
    });
  }

  cancelMfa(): void {
    this.step.set('login');
    this.mfaCode = '';
    this.mfaToken = '';
  }
}
