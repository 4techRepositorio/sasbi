import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-reset-password',
  imports: [FormsModule, RouterLink],
  template: `
    <div class="da-auth-layout">
      <div class="da-auth-hero">
        <div class="da-auth-hero__inner">
          <p class="da-auth-hero__product">4Pro_BI</p>
          <h2 class="da-auth-hero__title">Nova credencial</h2>
          <p class="da-auth-hero__text">Token de uso único. Depois do sucesso, inicie sessão com a nova senha.</p>
        </div>
      </div>
      <div class="da-auth-panel">
        <div class="da-auth-card">
          <p class="da-brand-tag">4Pro_BI</p>
          <h1>Nova senha</h1>
          <p class="hint">Cole o token do email e defina a nova senha (mín. 8 caracteres).</p>
          @if (!done()) {
            <form (ngSubmit)="submit()">
              <label>
                <span>Token</span>
                <input name="token" type="text" [(ngModel)]="token" required autocomplete="one-time-code" />
              </label>
              <label>
                <span>Nova senha</span>
                <input
                  name="pw1"
                  type="password"
                  [(ngModel)]="password"
                  required
                  minlength="8"
                  autocomplete="new-password"
                />
              </label>
              <label>
                <span>Confirmar senha</span>
                <input name="pw2" type="password" [(ngModel)]="password2" required minlength="8" />
              </label>
              <button type="submit" class="da-btn da-btn--primary" [disabled]="loading()">Atualizar senha</button>
            </form>
          } @else {
            <p class="ok-text">Senha atualizada. Pode iniciar sessão.</p>
            <p class="foot"><a routerLink="/login">Ir para login</a></p>
          }
          @if (error()) {
            <p class="error" role="alert">{{ error() }}</p>
          }
          @if (!done()) {
            <p class="foot"><a routerLink="/login">← Voltar ao login</a></p>
          }
        </div>
      </div>
    </div>
  `,
  styles: [``],
})
export class ResetPasswordComponent implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly route = inject(ActivatedRoute);

  token = '';
  password = '';
  password2 = '';
  readonly loading = signal(false);
  readonly done = signal(false);
  readonly error = signal<string | null>(null);

  ngOnInit(): void {
    this.route.queryParamMap.subscribe((q) => {
      const t = q.get('token');
      if (t) {
        this.token = t;
      }
    });
  }

  submit(): void {
    this.error.set(null);
    if (this.password !== this.password2) {
      this.error.set('As senhas não coincidem.');
      return;
    }
    this.loading.set(true);
    this.auth.resetPassword(this.token.trim(), this.password).subscribe({
      next: () => {
        this.loading.set(false);
        this.done.set(true);
      },
      error: (err: { error?: { detail?: string } }) => {
        this.loading.set(false);
        const d = err?.error?.detail;
        this.error.set(typeof d === 'string' ? d : 'Não foi possível atualizar a senha.');
      },
    });
  }
}
