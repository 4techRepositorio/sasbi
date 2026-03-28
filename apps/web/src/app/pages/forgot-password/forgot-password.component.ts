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
          <p class="da-auth-hero__product">4Pro_BI</p>
          <h2 class="da-auth-hero__title">Recuperação de conta</h2>
          <p class="da-auth-hero__text">
            Fluxo seguro: mensagem única e token com expiração, alinhado à política de identidade do produto.
          </p>
        </div>
      </div>
      <div class="da-auth-panel">
        <div class="da-auth-card">
          <p class="da-brand-tag">4Pro_BI</p>
          <h1>Recuperar senha</h1>
          <p class="hint">Indique o email. Se existir, enviaremos instruções (ou registo em dev).</p>
          @if (!sent()) {
            <form (ngSubmit)="submit()">
              <label>
                <span>Email</span>
                <input name="email" type="email" [(ngModel)]="email" required autocomplete="email" />
              </label>
              <button type="submit" class="da-btn da-btn--primary" [disabled]="loading()">Enviar pedido</button>
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
