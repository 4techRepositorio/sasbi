import type { MeContext } from './tenant-context';

/** Papéis que podem editar fontes, modelos e dashboards. */
export function canEditBi(role: string | null | undefined): boolean {
  return role === 'admin' || role === 'analyst';
}

export function roleFromContext(
  ctx: MeContext | null | undefined,
  fallback: string | null | undefined,
): string | null {
  return ctx?.role ?? fallback ?? null;
}
