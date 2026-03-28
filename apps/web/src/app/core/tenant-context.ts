export interface PlanContext {
  code: string;
  name: string;
  max_uploads_per_month: number;
  max_storage_mb: number;
}

export interface StorageContext {
  tenant_used_bytes: number;
  tenant_limit_mb: number;
  user_used_bytes: number;
  user_limit_mb: number | null;
  group_used_bytes: number | null;
  group_limit_mb: number | null;
  group_id: string | null;
  group_name: string | null;
}

export interface MeContext {
  user_id: string;
  tenant_id: string;
  tenant_name: string | null;
  tenant_slug: string | null;
  role: string;
  plan: PlanContext | null;
  storage: StorageContext | null;
}
