import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_V1 } from './api-base';

export interface DashboardWidget {
  id?: string;
  widget_type: 'kpi' | 'table' | 'chart';
  title: string;
  dataset_id: string | null;
  config: Record<string, unknown>;
  position: Record<string, unknown>;
  dataset_available?: boolean;
}

export interface DashboardSummary {
  id: string;
  tenant_id: string;
  title: string;
  description: string | null;
  updated_at: string;
  widget_count: number;
}

export interface DashboardDetail extends DashboardSummary {
  layout_json: Record<string, unknown>;
  widgets: DashboardWidget[];
  created_at: string;
}

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private readonly http = inject(HttpClient);

  list(limit = 50, offset = 0): Observable<{ items: DashboardSummary[]; total: number }> {
    const params = new HttpParams().set('limit', limit).set('offset', offset);
    return this.http.get<{ items: DashboardSummary[]; total: number }>(`${API_V1}/dashboards`, {
      params,
    });
  }

  get(id: string): Observable<DashboardDetail> {
    return this.http.get<DashboardDetail>(`${API_V1}/dashboards/${id}`);
  }

  create(body: {
    title: string;
    description?: string;
    widgets?: DashboardWidget[];
  }): Observable<DashboardDetail> {
    return this.http.post<DashboardDetail>(`${API_V1}/dashboards`, body);
  }

  export(id: string): Observable<Blob> {
    return this.http.get(`${API_V1}/dashboards/${id}/export`, {
      responseType: 'blob',
    });
  }
}
