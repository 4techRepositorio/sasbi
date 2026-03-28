import type { StorageContext } from './tenant-context';

/** Limite em bytes a partir de MB do plano (0 = sem barra útil). */
export function limitBytesFromMb(mb: number): number {
  return Math.max(0, mb) * 1024 * 1024;
}

/** Percentagem de preenchimento (0–100) para barra de progresso. */
export function storageFillPercent(usedBytes: number, limitMb: number): number {
  const cap = limitBytesFromMb(limitMb);
  if (cap <= 0) {
    return 0;
  }
  return Math.min(100, (usedBytes / cap) * 100);
}

export function tenantStoragePercent(st: StorageContext): number {
  return storageFillPercent(st.tenant_used_bytes, st.tenant_limit_mb);
}

/** Limiar (%) para alertas de armazenamento na UI — tenant, utilizador e grupo. */
export const STORAGE_QUOTA_WARN_PERCENT = 90;

/** @deprecated Use `STORAGE_QUOTA_WARN_PERCENT` (mesmo valor). */
export const TENANT_STORAGE_WARN_PERCENT = STORAGE_QUOTA_WARN_PERCENT;

export function isTenantStorageNearPlanLimit(st: StorageContext): boolean {
  return tenantStoragePercent(st) >= STORAGE_QUOTA_WARN_PERCENT;
}

export function userStoragePercent(st: StorageContext): number | null {
  if (st.user_limit_mb == null) {
    return null;
  }
  return storageFillPercent(st.user_used_bytes, st.user_limit_mb);
}

export function groupStoragePercent(st: StorageContext): number | null {
  if (st.group_limit_mb == null || st.group_used_bytes == null) {
    return null;
  }
  return storageFillPercent(st.group_used_bytes, st.group_limit_mb);
}

export function isUserStorageNearLimit(st: StorageContext): boolean {
  const p = userStoragePercent(st);
  return p !== null && p >= STORAGE_QUOTA_WARN_PERCENT;
}

export function isGroupStorageNearLimit(st: StorageContext): boolean {
  const p = groupStoragePercent(st);
  return p !== null && p >= STORAGE_QUOTA_WARN_PERCENT;
}
