import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-forgot-password',
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
          <h2 class="da-auth-hero__title">Recuperação de conta</h2>
          <p class="da-auth-hero__text">
            Fluxo seguro com token limitado no tempo — identidade alinhada à política da plataforma multitenant.
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
          <h1>Recuperar senha</h1>
          <p class="hint">Indique o email. Se existir, enviaremos instruções (ou registo em dev).</p>
          @if (!sent()) {
            <form (ngSubmit)="submit()">
              <label>
                <span>Email</span>
                <input name="email" type="email" [(ngModel)]="email" required autocomplete="email" />
              </label>
              <button type="submit" class="da-btn da-btn--primary" [disabled]="loading()">Enviar pedido</button>
              @if (loading()) {
                <p class="da-muted" role="status">A enviar o pedido…</p>
              }
            </form>
          } @else {
            <p class="ok-text">{{ message() }}</p>
          }
          @if (error()) {
            <p class="error" role="alert">{{ error() }}</p>
          }
          <p class="foot"><a routerLink="/login">← Voltar ao login</a></p>
        </div>
      </div>
    </div>
  `,
  styles: [``],
})
export class ForgotPasswordComponent {
  private readonly auth = inject(AuthService);

  email = '';
  readonly loading = signal(false);
  readonly sent = signal(false);
  readonly message = signal<string | null>(null);
  readonly error = signal<string | null>(null);

  submit(): void {
    this.error.set(null);
    this.loading.set(true);
    this.auth.forgotPassword(this.email.trim()).subscribe({
      next: (res) => {
        this.loading.set(false);
        this.sent.set(true);
        this.message.set(res.detail ?? 'Pedido registado.');
      },
      error: () => {
        this.loading.set(false);
        this.error.set('Não foi possível enviar o pedido. Tente novamente.');
      },
    });
  }
}
