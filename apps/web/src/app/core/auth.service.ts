import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

import { API_V1 } from './api-base';

const KEYS = ['access_token', 'refresh_token', 'tenant_role'] as const;

function clearAllStores(): void {
  for (const k of KEYS) {
    sessionStorage.removeItem(k);
    localStorage.removeItem(k);
  }
}

function pickStorageForSession(remember: boolean): Storage {
  return remember ? localStorage : sessionStorage;
}

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

  /**
   * Guarda tokens no sessionStorage ou localStorage (Lembrar-me), nunca em ambos.
   */
  setSession(
    body: { access_token: string; refresh_token: string; role?: string | null },
    remember = false,
  ): void {
    clearAllStores();
    const st = pickStorageForSession(remember);
    st.setItem('access_token', body.access_token);
    st.setItem('refresh_token', body.refresh_token);
    if (body.role) {
      st.setItem('tenant_role', body.role);
    }
  }

  logout(): void {
    clearAllStores();
    void this.router.navigateByUrl('/login');
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token') ?? sessionStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token') ?? sessionStorage.getItem('refresh_token');
  }

  /** Onde persistir após refresh — mesmo storage que tinha o refresh. */
  tokenTargetStore(): Storage {
    return localStorage.getItem('refresh_token') != null ? localStorage : sessionStorage;
  }

  tenantRole(): string | null {
    return localStorage.getItem('tenant_role') ?? sessionStorage.getItem('tenant_role');
  }

  isLoggedIn(): boolean {
    return !!this.getAccessToken();
  }
}
