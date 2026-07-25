import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_V1 } from './api-base';
import type { AggregationOp } from './semantic.service';

/** Alinhado a packages/contracts/fourpro_contracts/semantic.py (Query*) */

export interface QueryMeasure {
  field: string;
  op: AggregationOp;
  alias?: string | null;
}

export interface QueryRequest {
  semantic_model_id: string;
  measures: QueryMeasure[];
  dimensions?: string[];
  filters?: Record<string, unknown>;
  limit?: number;
}

export interface QueryResponse {
  columns: string[];
  rows: Record<string, unknown>[];
  row_count: number;
  truncated: boolean;
  semantic_model_id: string;
  dataset_id: string;
}

@Injectable({ providedIn: 'root' })
export class QueryService {
  private readonly http = inject(HttpClient);

  run(body: QueryRequest): Observable<QueryResponse> {
    return this.http.post<QueryResponse>(`${API_V1}/query`, body);
  }
}
