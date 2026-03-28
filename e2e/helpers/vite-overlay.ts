import type { Page } from '@playwright/test';

/** Dev server Angular/Vite: overlay de erro pode bloquear cliques até ser fechado. */
export async function dismissViteOverlayIfAny(page: Page): Promise<void> {
  const overlay = page.locator('vite-error-overlay');
  if (await overlay.isVisible().catch(() => false)) {
    await page.keyboard.press('Escape');
    await overlay.waitFor({ state: 'hidden', timeout: 5000 }).catch(() => {});
  }
}
