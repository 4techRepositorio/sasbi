import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';
import { TenantContextService } from '../../core/tenant-context.service';

function formatLoginDetail(detail: unknown): string | null {
  if (typeof detail === 'string') {
    return detail;
  }
  if (Array.isArray(detail)) {
    const parts = detail.map((x) =>
      typeof x === 'object' && x !== null && 'msg' in x ? String((x as { msg: string }).msg) : JSON.stringify(x),
    );
    return parts.join(' · ');
  }
  return null;
}

@Component({
  selector: 'app-login',
  imports: [FormsModule, RouterLink],
  template: `
    <div class="da-auth-layout">
      <div class="da-auth-hero">
        <div class="da-auth-hero__inner">
          <div class="da-auth-hero__brandrow">
            <img class="da-auth-hero__mark" src="branding/logo-mark.svg" alt="" width="56" height="56" />
            <div>
              <p class="da-auth-hero__solution">Business Intelligence</p>
              <p class="da-auth-hero__product">4Pro_BI</p>
            </div>
          </div>
          <h2 class="da-auth-hero__title">BI completo com pipeline de dados por organização</h2>
          <p class="da-auth-hero__text">
            Interface alinhada ao documento <strong>Data Analytics Solution</strong> — dashboards, ETL, catálogo e
            área administrativa multitenant.
          </p>
        </div>
      </div>
      <div class="da-auth-panel">
        <div class="da-auth-card">
          <div class="da-auth-card__head-brand">
            <img src="branding/logo-mark.svg" alt="" width="36" height="36" />
            <div class="da-auth-card__head-lines">
              <span class="da-auth-card__head-product">4Pro_BI</span>
              <span class="da-auth-card__head-solution">Business Intelligence</span>
            </div>
          </div>
          <h1>Bem-vindo de volta</h1>
          <p class="hint">Introduza as credenciais do seu tenant para continuar.</p>
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
                  placeholder="email@organizacao.com"
                />
              </label>
              <div class="da-pw-field">
                <label>
                  <span>Senha</span>
                  <input
                    name="password"
                    [type]="showPassword() ? 'text' : 'password'"
                    [(ngModel)]="password"
                    required
                    autocomplete="current-password"
                    placeholder="A sua senha"
                  />
                </label>
                <button
                  type="button"
                  class="da-pw-toggle"
                  (click)="showPassword.set(!showPassword())"
                  [attr.aria-label]="showPassword() ? 'Ocultar senha' : 'Mostrar senha'"
                >
                  {{ showPassword() ? 'Ocultar' : 'Mostrar' }}
                </button>
              </div>
              <div class="da-login-options">
                <label>
                  <input type="checkbox" name="remember" [(ngModel)]="rememberMe" />
                  Lembrar-me
                </label>
                <a routerLink="/forgot-password">Esqueceu a senha?</a>
              </div>
              <button type="submit" class="da-btn da-btn--primary" [disabled]="loading()">Entrar</button>
              @if (loading()) {
                <p class="da-muted" role="status">A validar credenciais…</p>
              }
              <div class="da-auth-sso-row">
                <button type="button" class="da-btn--sso" disabled title="Em breve">Entrar com SSO</button>
              </div>
              <p class="da-auth-signup">Não tem conta? <a href="#">Cadastre-se</a> <span class="da-muted">(em breve)</span></p>
              <p class="links">
                <a routerLink="/reset-password">Redefinir com token</a>
              </p>
              <div class="da-auth-demo-creds" role="note">
                <strong>Demonstração local</strong><br />
                Após <code>python -m fourpro_api.dev_seed</code>:<br />
                Email <code>admin&#64;local.dev</code> · Senha <code>changeme</code>
              </div>
            </form>
          } @else {
            <form (ngSubmit)="onMfa()">
              <label>
                <span>Código MFA</span>
                <input name="code" [(ngModel)]="mfaCode" required autocomplete="one-time-code" />
              </label>
              <button type="submit" class="da-btn da-btn--primary" [disabled]="loading()">Confirmar</button>
              @if (loading()) {
                <p class="da-muted" role="status">A validar o código MFA…</p>
              }
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
  styles: [],
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
  rememberMe = false;
  readonly showPassword = signal(false);

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
          this.auth.setSession(
            {
              access_token: res['access_token'],
              refresh_token: res['refresh_token'],
              role: typeof res['role'] === 'string' ? res['role'] : null,
            },
            this.rememberMe,
          );
          this.tenantCtx.clear();
          void this.router.navigateByUrl('/app');
          return;
        }
        this.error.set('Resposta inesperada do servidor.');
      },
      error: (err: { error?: { detail?: unknown } }) => {
        this.loading.set(false);
        this.error.set(formatLoginDetail(err?.error?.detail) ?? 'Não foi possível iniciar sessão.');
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
          this.auth.setSession(
            {
              access_token: res['access_token'],
              refresh_token: res['refresh_token'],
              role: typeof res['role'] === 'string' ? res['role'] : null,
            },
            this.rememberMe,
          );
          this.tenantCtx.clear();
          void this.router.navigateByUrl('/app');
          return;
        }
        this.error.set('Resposta inesperada do servidor.');
      },
      error: (err: { error?: { detail?: unknown } }) => {
        this.loading.set(false);
        this.error.set(formatLoginDetail(err?.error?.detail) ?? 'Código inválido.');
      },
    });
  }

  cancelMfa(): void {
    this.step.set('login');
    this.mfaCode = '';
    this.mfaToken = '';
  }
}
