import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_V1 } from './api-base';

/** Alinhado a packages/contracts/fourpro_contracts/connectors.py */

export type ConnectorType =
  | 'file'
  | 'postgres'
  | 'mysql'
  | 'sqlserver'
  | 'rest_json'
  | 's3_compatible';

export type DataSourceStatus = 'ready' | 'syncing' | 'error' | 'disabled';

export type SyncRunStatus =
  | 'queued'
  | 'running'
  | 'uploaded'
  | 'validating'
  | 'parsing'
  | 'processed'
  | 'failed';

export type AuthKind = 'none' | 'password' | 'token' | 'api_key' | 'aws_sig_v4';

export interface ConnectorCapability {
  connector_type: ConnectorType;
  display_name: string;
  description: string;
  auth_kinds: AuthKind[];
  supports_incremental: boolean;
  supports_discover: boolean;
  max_sample_rows: number;
  config_schema_hint: Record<string, unknown>;
}

export interface ConnectorCatalogResponse {
  items: ConnectorCapability[];
}

export interface DataSourceCreate {
  name: string;
  connector_type: ConnectorType;
  config: Record<string, unknown>;
  secret?: Record<string, string> | null;
}

export interface DataSourcePatch {
  name?: string | null;
  config?: Record<string, unknown> | null;
  secret?: Record<string, string> | null;
  status?: 'ready' | 'disabled' | null;
}

export interface DataSourceItem {
  id: string;
  tenant_id: string;
  name: string;
  connector_type: ConnectorType;
  config: Record<string, unknown>;
  status: DataSourceStatus;
  has_secret: boolean;
  last_sync_at: string | null;
  last_error: string | null;
  created_by_user_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface PaginatedDataSourceList {
  items: DataSourceItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface ConnectionTestResult {
  ok: boolean;
  message: string;
  details: Record<string, unknown>;
}

export interface DiscoverObject {
  object_id: string;
  name: string;
  kind: string;
  meta: Record<string, unknown>;
}

export interface DiscoverResponse {
  objects: DiscoverObject[];
}

export interface SyncRequest {
  object_id?: string | null;
  mode?: 'full' | 'sample';
  sample_limit?: number;
}

export interface SyncRunItem {
  id: string;
  tenant_id: string;
  data_source_id: string;
  ingestion_id: string | null;
  status: SyncRunStatus;
  object_id: string | null;
  friendly_message: string | null;
  technical_log: string | null;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
}

export interface PaginatedSyncRunList {
  items: SyncRunItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface SyncEnqueuedResponse {
  sync_run_id: string;
  status: SyncRunStatus;
  message: string;
}

@Injectable({ providedIn: 'root' })
export class DataSourcesService {
  private readonly http = inject(HttpClient);

  listConnectors(): Observable<ConnectorCatalogResponse> {
    return this.http.get<ConnectorCatalogResponse>(`${API_V1}/connectors`);
  }

  list(params?: { limit?: number; offset?: number }): Observable<PaginatedDataSourceList> {
    let p = new HttpParams();
    if (params?.limit != null) {
      p = p.set('limit', String(params.limit));
    }
    if (params?.offset != null) {
      p = p.set('offset', String(params.offset));
    }
    return this.http.get<PaginatedDataSourceList>(`${API_V1}/data-sources`, { params: p });
  }

  get(id: string): Observable<DataSourceItem> {
    return this.http.get<DataSourceItem>(`${API_V1}/data-sources/${id}`);
  }

  create(body: DataSourceCreate): Observable<DataSourceItem> {
    return this.http.post<DataSourceItem>(`${API_V1}/data-sources`, body);
  }

  patch(id: string, body: DataSourcePatch): Observable<DataSourceItem> {
    return this.http.patch<DataSourceItem>(`${API_V1}/data-sources/${id}`, body);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${API_V1}/data-sources/${id}`);
  }

  testConnection(id: string): Observable<ConnectionTestResult> {
    return this.http.post<ConnectionTestResult>(`${API_V1}/data-sources/${id}/test`, {});
  }

  /** Teste pré-persistência: envia payload provisório (quando a API o aceitar). */
  testDraft(body: DataSourceCreate): Observable<ConnectionTestResult> {
    return this.http.post<ConnectionTestResult>(`${API_V1}/data-sources/test`, body);
  }

  discover(id: string): Observable<DiscoverResponse> {
    return this.http.post<DiscoverResponse>(`${API_V1}/data-sources/${id}/discover`, {});
  }

  sync(id: string, body: SyncRequest = {}): Observable<SyncEnqueuedResponse> {
    return this.http.post<SyncEnqueuedResponse>(`${API_V1}/data-sources/${id}/sync`, body);
  }

  listSyncRuns(
    id: string,
    params?: { limit?: number; offset?: number },
  ): Observable<PaginatedSyncRunList> {
    let p = new HttpParams();
    if (params?.limit != null) {
      p = p.set('limit', String(params.limit));
    }
    if (params?.offset != null) {
      p = p.set('offset', String(params.offset));
    }
    return this.http.get<PaginatedSyncRunList>(`${API_V1}/data-sources/${id}/sync-runs`, {
      params: p,
    });
  }
}
