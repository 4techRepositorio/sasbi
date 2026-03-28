import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { RbacNoticeService } from './rbac-notice.service';
import { TenantContextService } from './tenant-context.service';

/** RBAC: papel da API (/me/context) quando já carregado; senão fallback ao login (sessionStorage). */
export function roleGuard(allowed: readonly string[]): CanActivateFn {
  return () => {
    const router = inject(Router);
    const tenantCtx = inject(TenantContextService);
    const rbacNotice = inject(RbacNoticeService);
    const fromApi = tenantCtx.context()?.role;
    const role = fromApi ?? sessionStorage.getItem('tenant_role');
    if (role && allowed.includes(role)) {
      return true;
    }
    rbacNotice.showAccessDenied();
    return router.createUrlTree(['/app/dashboard']);
  };
}
