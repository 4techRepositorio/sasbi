export interface StoredTokens {
  access_token: string;
  refresh_token: string;
  expires_at?: number;
  tenant_id?: string | null;
  tenant_name?: string | null;
  role?: string | null;
}
