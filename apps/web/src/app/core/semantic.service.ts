import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_V1 } from './api-base';

/** Alinhado a packages/contracts/fourpro_contracts/semantic.py */

export type AggregationOp = 'count' | 'sum' | 'avg' | 'min' | 'max';
export type FieldRole = 'dimension' | 'measure' | 'attribute';

export interface SemanticField {
  name: string;
  source_column: string;
  role: FieldRole;
  data_type: string;
  label?: string | null;
}

export interface SemanticModelCreate {
  name: string;
  dataset_id: string;
  description?: string | null;
  fields?: SemanticField[];
}

export interface SemanticModelPatch {
  name?: string | null;
  description?: string | null;
  fields?: SemanticField[] | null;
}

export interface SemanticModelItem {
  id: string;
  tenant_id: string;
  name: string;
  dataset_id: string;
  description: string | null;
  fields: SemanticField[];
  created_at: string;
  updated_at: string;
}

export interface PaginatedSemanticModelList {
  items: SemanticModelItem[];
  total: number;
  limit: number;
  offset: number;
}

@Injectable({ providedIn: 'root' })
export class SemanticService {
  private readonly http = inject(HttpClient);

  list(params?: { limit?: number; offset?: number }): Observable<PaginatedSemanticModelList> {
    let p = new HttpParams();
    if (params?.limit != null) {
      p = p.set('limit', String(params.limit));
    }
    if (params?.offset != null) {
      p = p.set('offset', String(params.offset));
    }
    return this.http.get<PaginatedSemanticModelList>(`${API_V1}/semantic-models`, { params: p });
  }

  get(id: string): Observable<SemanticModelItem> {
    return this.http.get<SemanticModelItem>(`${API_V1}/semantic-models/${id}`);
  }

  create(body: SemanticModelCreate): Observable<SemanticModelItem> {
    return this.http.post<SemanticModelItem>(`${API_V1}/semantic-models`, body);
  }

  patch(id: string, body: SemanticModelPatch): Observable<SemanticModelItem> {
    return this.http.patch<SemanticModelItem>(`${API_V1}/semantic-models/${id}`, body);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${API_V1}/semantic-models/${id}`);
  }
}
