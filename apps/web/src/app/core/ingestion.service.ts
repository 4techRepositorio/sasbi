import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_V1 } from './api-base';

/** Forma alinhada à API /ingestions (campos usados na UI). */
export interface IngestionDto {
  id: string;
  tenant_id: string;
  original_filename: string;
  status: string;
  size_bytes: number;
  content_type: string | null;
  content_sha256: string | null;
  uploaded_by_user_id: string | null;
  friendly_error: string | null;
  result_summary: string | null;
  created_at: string;
}

@Injectable({ providedIn: 'root' })
export class IngestionService {
  private readonly http = inject(HttpClient);

  list(params?: { status?: string }): Observable<IngestionDto[]> {
    let p = new HttpParams();
    if (params?.status) {
      p = p.set('status', params.status);
    }
    return this.http.get<IngestionDto[]>(`${API_V1}/ingestions`, { params: p });
  }

  /** Reenfileira parse (admin/analyst). */
  reprocess(id: string): Observable<IngestionDto> {
    return this.http.post<IngestionDto>(`${API_V1}/ingestions/${id}/reprocess`, {});
  }
}
