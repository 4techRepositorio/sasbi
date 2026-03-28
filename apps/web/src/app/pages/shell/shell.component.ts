import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs/operators';

import { AuthService } from '../../core/auth.service';
import { TenantContextService } from '../../core/tenant-context.service';

function roleMayUpload(role: string | null | undefined): boolean {
  return role === 'admin' || role === 'analyst';
}

@Component({
  selector: 'app-shell',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  template: `
    <div class="da-shell">
      <aside class="da-shell__aside">
        <div class="da-shell__logo">4Pro_BI</div>
        <p class="da-shell__label">Visão geral</p>
        <nav class="da-shell__nav">
          <a
            routerLink="/app/dashboard"
            routerLinkActive="da-shell__link--active"
            [routerLinkActiveOptions]="{ exact: true }"
            class="da-shell__link"
            >Dashboard</a
          >
        </nav>
        <p class="da-shell__label">Dados</p>
        <nav class="da-shell__nav">
          @if (canUpload()) {
            <a
              routerLink="/app/upload"
              routerLinkActive="da-shell__link--active"
              class="da-shell__link"
              >Upload</a
            >
          }
          <a
            routerLink="/app/datasets"
            routerLinkActive="da-shell__link--active"
            class="da-shell__link"
            >Catálogo</a
          >
          <a
            routerLink="/app/ingestions"
            routerLinkActive="da-shell__link--active"
            class="da-shell__link"
            >Ingestões</a
          >
        </nav>
        <div class="da-shell__spacer"></div>
        <div class="da-shell__user">
          @if (tenantCtx.context(); as ctx) {
            <div class="da-shell__user-meta">Tenant ativo</div>
            <div class="da-shell__tenant">{{ ctx.tenant_name ?? ctx.tenant_slug ?? ctx.tenant_id }}</div>
            <span class="da-shell__role">{{ ctx.role }}</span>
          } @else if (contextError()) {
            <div class="da-shell__warn">{{ contextError() }}</div>
          } @else if (contextLoading()) {
            <div class="da-shell__user-meta">A carregar contexto…</div>
          }
          <button type="button" class="da-shell__logout" (click)="logout()">Terminar sessão</button>
        </div>
      </aside>
      <div class="da-shell__main">
        <header class="da-shell__topbar">
          <span class="da-shell__crumb">{{ shellTitle() }}</span>
        </header>
        <main class="da-shell__content" [class.da-shell__content--fluid]="fluidLayout()">
          <router-outlet />
        </main>
      </div>
    </div>
  `,
  styles: [``],
})
export class ShellComponent implements OnInit {
  readonly auth = inject(AuthService);
  readonly tenantCtx = inject(TenantContextService);
  private readonly router = inject(Router);
  readonly contextLoading = signal(false);
  readonly contextError = signal<string | null>(null);
  /** Rota ativa (para título e layout fluid). */
  readonly activeUrl = signal(this.router.url);

  readonly shellTitle = computed(() => {
    const url = this.activeUrl();
    let r = this.router.routerState.root;
    while (r.firstChild) {
      r = r.firstChild;
    }
    const fromData = r.snapshot.data['shellTitle'] as string | undefined;
    if (fromData) {
      return fromData;
    }
    if (url.includes('/app/dashboard')) {
      return 'Dashboard';
    }
    return 'Workspace';
  });

  readonly fluidLayout = computed(() => this.activeUrl().includes('/app/dashboard'));

  canUpload(): boolean {
    const ctx = this.tenantCtx.context();
    if (ctx) {
      return roleMayUpload(ctx.role);
    }
    return roleMayUpload(this.auth.tenantRole());
  }

  ngOnInit(): void {
    this.router.events.pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd)).subscribe(() => {
      this.activeUrl.set(this.router.url);
    });
    this.contextLoading.set(true);
    this.tenantCtx.load().subscribe({
      next: () => {
        this.contextLoading.set(false);
        this.contextError.set(null);
      },
      error: () => {
        this.contextLoading.set(false);
        this.contextError.set('Não foi possível carregar o contexto do tenant.');
      },
    });
  }

  logout(): void {
    this.tenantCtx.clear();
    this.auth.logout();
  }
}
