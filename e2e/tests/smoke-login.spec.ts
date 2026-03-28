import { test, expect } from '@playwright/test';

import { dismissViteOverlayIfAny } from '../helpers/vite-overlay';

/**
 * Smoke UI: formulário de login (sem MFA).
 * Requer `PLAYWRIGHT_BASE_URL` (playwright.config) e credenciais de teste.
 */
test.describe('Login smoke', () => {
  test.skip(
    () => !process.env.E2E_USER_EMAIL?.trim() || !process.env.E2E_USER_PASSWORD?.trim(),
    'Defina E2E_USER_EMAIL e E2E_USER_PASSWORD',
  );

  test('página de login e fluxo feliz até /app', async ({ page }) => {
    const email = process.env.E2E_USER_EMAIL!.trim();
    const password = process.env.E2E_USER_PASSWORD!.trim();

    await page.goto('/login');
    await dismissViteOverlayIfAny(page);
    await expect(page.getByRole('heading', { name: /bem-vindo de volta/i })).toBeVisible();

    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="password"]').fill(password);
    await page.getByRole('button', { name: 'Entrar', exact: true }).click();

    const mfaField = page.getByRole('textbox', { name: /código mfa/i });
    if (await mfaField.isVisible({ timeout: 4000 }).catch(() => false)) {
      test.skip(true, 'Conta com MFA — use utilizador E2E sem MFA ou estenda o teste');
    }

    await expect(page).toHaveURL(/\/app(\/|$)/, { timeout: 20_000 });
    await expect(page.getByText(/4pro|dashboard|tenant ativo/i).first()).toBeVisible({
      timeout: 15_000,
    });
  });
});
