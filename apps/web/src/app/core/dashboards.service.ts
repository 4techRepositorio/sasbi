import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_V1 } from './api-base';

/** Alinhado a packages/contracts/fourpro_contracts/dashboard.py */

export type WidgetType = 'kpi' | 'bar_chart' | 'line_chart' | 'table' | 'text';
export type DashboardStatus = 'draft' | 'published' | 'archived';

export interface WidgetQueryRef {
  semantic_model_id?: string | null;
  measures?: Record<string, unknown>[];
  dimensions?: string[];
  filters?: Record<string, unknown>;
  limit?: number;
}

export interface DashboardWidget {
  id: string;
  type: WidgetType;
  title: string;
  x: number;
  y: number;
  w: number;
  h: number;
  query?: WidgetQueryRef | null;
  options?: Record<string, unknown>;
}

export interface DashboardLayout {
  version: number;
  columns: number;
  widgets: DashboardWidget[];
}

export interface DashboardCreate {
  name: string;
  description?: string | null;
  layout?: DashboardLayout;
}

export interface DashboardPatch {
  name?: string | null;
  description?: string | null;
  layout?: DashboardLayout | null;
  status?: DashboardStatus | null;
}

export interface DashboardItem {
  id: string;
  tenant_id: string;
  name: string;
  description: string | null;
  status: DashboardStatus;
  layout: DashboardLayout;
  version: number;
  created_by_user_id: string | null;
  created_at: string;
  updated_at: string;
  published_at: string | null;
}

export interface PaginatedDashboardList {
  items: DashboardItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface DashboardPublishResponse {
  id: string;
  status: 'published';
  version: number;
  published_at: string;
}

@Injectable({ providedIn: 'root' })
export class DashboardsService {
  private readonly http = inject(HttpClient);

  list(params?: {
    limit?: number;
    offset?: number;
    status?: DashboardStatus;
  }): Observable<PaginatedDashboardList> {
    let p = new HttpParams();
    if (params?.limit != null) {
      p = p.set('limit', String(params.limit));
    }
    if (params?.offset != null) {
      p = p.set('offset', String(params.offset));
    }
    if (params?.status) {
      p = p.set('status', params.status);
    }
    return this.http.get<PaginatedDashboardList>(`${API_V1}/dashboards`, { params: p });
  }

  get(id: string): Observable<DashboardItem> {
    return this.http.get<DashboardItem>(`${API_V1}/dashboards/${id}`);
  }

  create(body: DashboardCreate): Observable<DashboardItem> {
    return this.http.post<DashboardItem>(`${API_V1}/dashboards`, body);
  }

  patch(id: string, body: DashboardPatch): Observable<DashboardItem> {
    return this.http.patch<DashboardItem>(`${API_V1}/dashboards/${id}`, body);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${API_V1}/dashboards/${id}`);
  }

  publish(id: string): Observable<DashboardPublishResponse> {
    return this.http.post<DashboardPublishResponse>(`${API_V1}/dashboards/${id}/publish`, {});
  }
}
