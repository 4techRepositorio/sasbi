import { test, expect } from '@playwright/test';

import { dismissViteOverlayIfAny } from '../helpers/vite-overlay';

/**
 * UI: página de auditoria (admin). Requer utilizador E2E com papel admin e sem MFA.
 */
test.describe('Auditoria do tenant (admin)', () => {
  test.skip(
    () => !process.env.E2E_USER_EMAIL?.trim() || !process.env.E2E_USER_PASSWORD?.trim(),
    'Defina E2E_USER_EMAIL e E2E_USER_PASSWORD (conta admin, sem MFA)',
  );

  test('acesso a /app/tenant-audit após login', async ({ page }) => {
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

    await page.waitForURL(/\/app(\/|$)/, { timeout: 20_000 });

    await page.goto('/app/tenant-audit');
    await expect(page).toHaveURL(/\/app\/tenant-audit/);
    await expect(page.getByRole('heading', { name: /auditoria do tenant/i })).toBeVisible({
      timeout: 15_000,
    });
    const emptyOrTable = page.locator('p.da-muted, table.da-table');
    await expect(emptyOrTable.first()).toBeVisible({ timeout: 10_000 });
  });
});

const consumerE2e =
  process.env.E2E_RUN === '1' &&
  !!process.env.E2E_CONSUMER_EMAIL?.trim() &&
  !!process.env.E2E_CONSUMER_PASSWORD?.trim();

/**
 * Consumer não deve ver auditoria (mesmo padrão que /app/upload).
 */
test.describe('Auditoria do tenant (RBAC consumer)', () => {
  test.skip(
    () => !consumerE2e,
    'Defina E2E_RUN=1, E2E_CONSUMER_EMAIL e E2E_CONSUMER_PASSWORD',
  );

  test('URL directa /app/tenant-audit redireciona e mostra aviso', async ({ page }) => {
    const email = process.env.E2E_CONSUMER_EMAIL!.trim();
    const password = process.env.E2E_CONSUMER_PASSWORD!.trim();

    await page.goto('/login');
    await dismissViteOverlayIfAny(page);
    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="password"]').fill(password);
    await page.getByRole('button', { name: 'Entrar', exact: true }).click();
    await expect(page).toHaveURL(/\/app(\/|$)/, { timeout: 60_000 });

    await page.goto('/app/tenant-audit');
    await expect(page).toHaveURL(/\/app\/dashboard/);

    const banner = page.locator('.da-rbac-banner');
    await expect(banner).toBeVisible({ timeout: 15_000 });
    await expect(banner).toContainText('Não tem permissão');
  });
});
