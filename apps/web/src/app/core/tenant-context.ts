export interface PlanContext {
  code: string;
  name: string;
  max_uploads_per_month: number;
  max_storage_mb: number;
}

export interface MeContext {
  user_id: string;
  tenant_id: string;
  tenant_name: string | null;
  tenant_slug: string | null;
  role: string;
  plan: PlanContext | null;
}
