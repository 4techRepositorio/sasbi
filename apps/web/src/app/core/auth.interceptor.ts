import { HttpBackend, HttpClient, HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';

import { API_V1 } from './api-base';
import { AuthService } from './auth.service';

function skipRefreshOn401(url: string): boolean {
  return (
    url.includes(`${API_V1}/auth/login`) ||
    url.includes(`${API_V1}/auth/refresh`) ||
    url.includes(`${API_V1}/auth/forgot-password`) ||
    url.includes(`${API_V1}/auth/reset-password`) ||
    url.includes(`${API_V1}/auth/mfa/verify`)
  );
}

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = sessionStorage.getItem('access_token');
  const authReq = token ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }) : req;

  return next(authReq).pipe(
    catchError((err: HttpErrorResponse) => {
      if (err.status !== 401 || skipRefreshOn401(req.url)) {
        return throwError(() => err);
      }
      const rt = sessionStorage.getItem('refresh_token');
      if (!rt) {
        inject(AuthService).logout();
        return throwError(() => err);
      }
      const backend = inject(HttpBackend);
      const plain = new HttpClient(backend);
      return plain
        .post<Record<string, unknown>>(`${API_V1}/auth/refresh`, { refresh_token: rt })
        .pipe(
          switchMap((body) => {
            if (typeof body['access_token'] !== 'string' || typeof body['refresh_token'] !== 'string') {
              inject(AuthService).logout();
              return throwError(() => err);
            }
            sessionStorage.setItem('access_token', body['access_token']);
            sessionStorage.setItem('refresh_token', body['refresh_token']);
            if (typeof body['role'] === 'string') {
              sessionStorage.setItem('tenant_role', body['role']);
            } else {
              sessionStorage.removeItem('tenant_role');
            }
            const retry = req.clone({
              setHeaders: { Authorization: `Bearer ${body['access_token']}` },
            });
            return next(retry);
          }),
          catchError(() => {
            inject(AuthService).logout();
            return throwError(() => err);
          }),
        );
    }),
  );
};
