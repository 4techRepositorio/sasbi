import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

import { API_V1 } from './api-base';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);

  login(email: string, password: string) {
    return this.http.post<Record<string, unknown>>(`${API_V1}/auth/login`, { email, password });
  }

  verifyMfa(mfaToken: string, code: string) {
    return this.http.post<Record<string, unknown>>(`${API_V1}/auth/mfa/verify`, {
      mfa_token: mfaToken,
      code,
    });
  }

  forgotPassword(email: string) {
    return this.http.post<{ detail: string }>(`${API_V1}/auth/forgot-password`, { email });
  }

  resetPassword(token: string, newPassword: string) {
    return this.http.post<{ detail?: string }>(`${API_V1}/auth/reset-password`, {
      token,
      new_password: newPassword,
    });
  }

  setSession(body: { access_token: string; refresh_token: string; role?: string | null }): void {
    sessionStorage.setItem('access_token', body.access_token);
    sessionStorage.setItem('refresh_token', body.refresh_token);
    if (body.role) {
      sessionStorage.setItem('tenant_role', body.role);
    } else {
      sessionStorage.removeItem('tenant_role');
    }
  }

  logout(): void {
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('tenant_role');
    void this.router.navigateByUrl('/login');
  }

  /** Papel no tenant atual (após login). */
  tenantRole(): string | null {
    return sessionStorage.getItem('tenant_role');
  }

  isLoggedIn(): boolean {
    return !!sessionStorage.getItem('access_token');
  }
}
