import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

import { API_V1 } from './api-base';
import type { MeContext } from './tenant-context';

@Injectable({ providedIn: 'root' })
export class TenantContextService {
  private readonly http = inject(HttpClient);
  private readonly _context = signal<MeContext | null>(null);
  readonly context = this._context.asReadonly();

  load(): Observable<MeContext> {
    return this.http.get<MeContext>(`${API_V1}/me/context`).pipe(
      tap((c) => this._context.set(c)),
    );
  }

  clear(): void {
    this._context.set(null);
  }
}
