import { test, expect } from '@playwright/test';

import { dismissViteOverlayIfAny } from '../helpers/vite-overlay';

/**
 * UI de quotas: `data-testid="storage-quota-block"` na shell após login.
 * Requer as mesmas credenciais que smoke-login (sem MFA) e front a apontar para API com /me/context.storage.
 */
test.describe('Contexto — armazenamento na shell', () => {
  test.skip(
    () => !process.env.E2E_USER_EMAIL?.trim() || !process.env.E2E_USER_PASSWORD?.trim(),
    'Defina E2E_USER_EMAIL e E2E_USER_PASSWORD',
  );

  test('sidebar mostra bloco de quotas (storage-quota-block) após login', async ({ page }) => {
    const email = process.env.E2E_USER_EMAIL!.trim();
    const password = process.env.E2E_USER_PASSWORD!.trim();

    await page.goto('/login');
    await dismissViteOverlayIfAny(page);
    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="password"]').fill(password);
    await page.getByRole('button', { name: 'Entrar', exact: true }).click();

    const mfaField = page.getByRole('textbox', { name: /código mfa/i });
    if (await mfaField.isVisible({ timeout: 4000 }).catch(() => false)) {
      test.skip(true, 'Conta com MFA — use utilizador E2E sem MFA');
    }

    await expect(page).toHaveURL(/\/app(\/|$)/, { timeout: 20_000 });

    await expect(page.getByTestId('storage-quota-block')).toBeVisible({ timeout: 15_000 });
    await expect(page.getByTestId('storage-quota-block').getByRole('progressbar')).toBeVisible({
      timeout: 5000,
    });
  });
});
