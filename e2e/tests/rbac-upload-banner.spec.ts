import { test, expect } from '@playwright/test';

import { dismissViteOverlayIfAny } from '../helpers/vite-overlay';

const e2eEnabled =
  process.env.E2E_RUN === '1' &&
  !!process.env.E2E_CONSUMER_EMAIL?.trim() &&
  !!process.env.E2E_CONSUMER_PASSWORD?.trim();

test.describe('RBAC — upload (consumer)', () => {
  test.skip(
    () => !e2eEnabled,
    'Defina E2E_RUN=1, E2E_CONSUMER_EMAIL e E2E_CONSUMER_PASSWORD (stack no ar).',
  );

  test('URL directa /app/upload redireciona e mostra aviso de permissão', async ({ page }) => {
    const email = process.env.E2E_CONSUMER_EMAIL!.trim();
    const password = process.env.E2E_CONSUMER_PASSWORD!.trim();

    await page.goto('/login');
    await dismissViteOverlayIfAny(page);
    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="password"]').fill(password);
    await page.getByRole('button', { name: 'Entrar', exact: true }).click();
    await expect(page).toHaveURL(/\/app(\/|$)/, { timeout: 60_000 });

    await page.goto('/app/upload');
    await expect(page).toHaveURL(/\/app\/dashboard/);

    const banner = page.locator('.da-rbac-banner');
    await expect(banner).toBeVisible({ timeout: 15_000 });
    await expect(banner).toContainText('Não tem permissão');
  });
});
