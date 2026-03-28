import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs/operators';

import { AuthService } from '../../core/auth.service';
import { RbacNoticeService } from '../../core/rbac-notice.service';
import { TenantContextService } from '../../core/tenant-context.service';
import { StorageQuotaBlockComponent } from '../../shared';

function roleMayUpload(role: string | null | undefined): boolean {
  return role === 'admin' || role === 'analyst';
}

function isAdmin(role: string | null | undefined): boolean {
  return role === 'admin';
}

@Component({
  selector: 'app-shell',
  imports: [RouterLink, RouterLinkActive, RouterOutlet, StorageQuotaBlockComponent],
  template: `
    <div class="da-shell">
      <aside class="da-shell__aside">
        <a routerLink="/app/dashboard" class="da-shell__brand" aria-label="4Pro_BI — início">
          <img class="da-shell__brand-mark" src="branding/logo-mark.svg" alt="" width="40" height="40" />
          <div class="da-shell__brand-text">
            <span class="da-shell__brand-name">4Pro_BI</span>
            <span class="da-shell__brand-tag">Business Intelligence</span>
          </div>
        </a>
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
        <p class="da-shell__label">ETL &amp; dados</p>
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
            routerLink="/app/ingestions"
            routerLinkActive="da-shell__link--active"
            class="da-shell__link"
            >Ingestões</a
          >
          <a
            routerLink="/app/datasets"
            routerLinkActive="da-shell__link--active"
            class="da-shell__link"
            >Catálogo</a
          >
        </nav>
        @if (isAdminNav()) {
          <p class="da-shell__label">Administração</p>
          <nav class="da-shell__nav">
            <a
              routerLink="/app/tenant-users"
              routerLinkActive="da-shell__link--active"
              class="da-shell__link"
              >Equipa</a
            >
            <a
              routerLink="/app/tenant-audit"
              routerLinkActive="da-shell__link--active"
              class="da-shell__link"
              >Auditoria</a
            >
          </nav>
        }
        <p class="da-shell__label">Plano &amp; sistema</p>
        <nav class="da-shell__nav">
          <a
            routerLink="/app/billing"
            routerLinkActive="da-shell__link--active"
            class="da-shell__link"
            >Cobrança</a
          >
          <a
            routerLink="/app/settings"
            routerLinkActive="da-shell__link--active"
            class="da-shell__link"
            >Configurações</a
          >
        </nav>
        <div class="da-shell__spacer"></div>
        <div class="da-shell__user">
          @if (tenantCtx.context(); as ctx) {
            <div class="da-shell__user-meta">Tenant ativo</div>
            <div class="da-shell__tenant">{{ ctx.tenant_name ?? ctx.tenant_slug ?? ctx.tenant_id }}</div>
            <span class="da-shell__role">{{ ctx.role }}</span>
            @if (ctx.plan; as pl) {
              <div class="da-shell__plan" [attr.title]="'Pacote ' + pl.code">
                {{ pl.name }} · até {{ pl.max_uploads_per_month }} uploads/mês
              </div>
            }
            @if (ctx.storage; as st) {
              <app-storage-quota-block [storage]="st" variant="compact" metaStyle="short" />
            }
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
          <div class="da-shell__topbar-right">
            <span class="da-demo-pill" title="Ambiente de demonstração">Demo</span>
            @if (tenantTopChip(); as chip) {
              <span class="da-shell__tenant-chip" title="Organização atual (tenant)">{{ chip }}</span>
            }
          </div>
        </header>
        <main class="da-shell__content" [class.da-shell__content--fluid]="fluidLayout()">
          @if (rbacNotice.message(); as notice) {
            <div class="da-rbac-banner" role="alert">
              <span class="da-rbac-banner__text">{{ notice }}</span>
              <button type="button" class="da-rbac-banner__dismiss" (click)="dismissRbacNotice()">Dispensar</button>
            </div>
          }
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
  readonly rbacNotice = inject(RbacNoticeService);
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

  /** Repete o tenant na topbar (requisito UX administrativa). */
  readonly tenantTopChip = computed(() => {
    const ctx = this.tenantCtx.context();
    if (!ctx) {
      return null;
    }
    return ctx.tenant_name ?? ctx.tenant_slug ?? ctx.tenant_id;
  });

  canUpload(): boolean {
    const ctx = this.tenantCtx.context();
    if (ctx) {
      return roleMayUpload(ctx.role);
    }
    return roleMayUpload(this.auth.tenantRole());
  }

  isAdminNav(): boolean {
    const ctx = this.tenantCtx.context();
    if (ctx) {
      return isAdmin(ctx.role);
    }
    return isAdmin(this.auth.tenantRole());
  }

  dismissRbacNotice(): void {
    this.rbacNotice.clear();
  }

  ngOnInit(): void {
    this.router.events.pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd)).subscribe(() => {
      this.activeUrl.set(this.router.url);
      this.rbacNotice.clear();
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
