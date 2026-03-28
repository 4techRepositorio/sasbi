/** Formatação legível para quotas e tamanhos de ficheiro. */
export function formatBytes(n: number): string {
  if (n < 0 || Number.isNaN(n)) {
    return '—';
  }
  if (n < 1024) {
    return `${n} B`;
  }
  if (n < 1024 * 1024) {
    return `${(n / 1024).toFixed(1)} KB`;
  }
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}
