import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

/** RBAC (TICKET-005): só papéis listados acedem à rota. */
export function roleGuard(allowed: readonly string[]): CanActivateFn {
  return () => {
    const router = inject(Router);
    const role = sessionStorage.getItem('tenant_role');
    if (role && allowed.includes(role)) {
      return true;
    }
    return router.createUrlTree(['/app/datasets']);
  };
}
