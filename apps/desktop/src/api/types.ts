/**
 * Tipos alinhados a packages/contracts (auth, connectors, dashboard, desktop_sync).
 */
export type ConnectorType =
  | "file"
  | "postgres"
  | "mysql"
  | "sqlserver"
  | "rest_json"
  | "s3_compatible";

export type AuthKind = "none" | "password" | "token" | "api_key" | "aws_sig_v4";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  mfa_required: false;
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;
  tenant_id?: string | null;
  tenant_name?: string | null;
  role?: string | null;
}

export interface MfaChallengeResponse {
  mfa_required: true;
  mfa_token: string;
  expires_in: number;
}

export type LoginResult = TokenResponse | MfaChallengeResponse;

export interface MfaVerifyRequest {
  mfa_token: string;
  code: string;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface MeContextResponse {
  user_id: string;
  tenant_id: string;
  tenant_name: string | null;
  tenant_slug: string | null;
  role: string;
  plan?: {
    code: string;
    name: string;
    max_uploads_per_month: number;
    max_storage_mb: number;
  } | null;
}

export interface DesktopSessionInfo {
  user_id: string;
  tenant_id: string;
  tenant_name: string;
  role: string;
  api_base_url: string;
  features: string[];
}

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

export type DataSourceStatus = "ready" | "syncing" | "error" | "disabled";

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

export interface SyncRequest {
  object_id?: string | null;
  mode?: "full" | "sample";
  sample_limit?: number;
}

export interface SyncEnqueuedResponse {
  sync_run_id: string;
  status: string;
  message: string;
}

export interface DesktopPublishDatasetRequest {
  name: string;
  data_source_id?: string | null;
  object_id?: string | null;
  semantic_fields?: Record<string, unknown>[];
  client_draft_id?: string | null;
}

export interface DesktopPublishDatasetResponse {
  dataset_id: string | null;
  semantic_model_id: string | null;
  sync_run_id: string | null;
  status: "queued" | "processed" | "failed";
  message: string;
}

export type WidgetType = "kpi" | "bar_chart" | "line_chart" | "table" | "text";

export interface DashboardWidget {
  id: string;
  type: WidgetType;
  title: string;
  x: number;
  y: number;
  w: number;
  h: number;
  query?: {
    semantic_model_id?: string | null;
    measures?: Record<string, unknown>[];
    dimensions?: string[];
    filters?: Record<string, unknown>;
    limit?: number;
  } | null;
  options?: Record<string, unknown>;
}

export interface DashboardLayout {
  version: number;
  columns: number;
  widgets: DashboardWidget[];
}

export interface DesktopPublishDashboardRequest {
  name: string;
  description?: string | null;
  layout: DashboardLayout;
  client_draft_id?: string | null;
  publish?: boolean;
}

export interface DesktopPublishDashboardResponse {
  dashboard_id: string;
  version: number;
  status: "draft" | "published";
  message: string;
}

export class ApiError extends Error {
  readonly status: number;
  readonly body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}
