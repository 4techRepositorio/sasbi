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

    const apiCheck = await page.evaluate(async () => {
      const tok =
        sessionStorage.getItem('access_token') ?? localStorage.getItem('access_token');
      if (!tok) {
        return { ok: false as const, reason: 'sem access_token no storage' };
      }
      const r = await fetch('/api/v1/me/context', {
        headers: { Authorization: `Bearer ${tok}` },
      });
      if (!r.ok) {
        return { ok: false as const, reason: `HTTP ${r.status}` };
      }
      const j = (await r.json()) as { storage?: unknown };
      return { ok: true as const, hasStorage: j.storage != null };
    });

    if (!apiCheck.ok) {
      test.skip(true, `/me/context indisponível: ${apiCheck.reason}`);
    }
    if (!apiCheck.hasStorage) {
      test.skip(true, 'API /me/context sem campo storage');
    }

    // Shell (sidebar) e dashboard podem ambos renderizar o bloco — este teste valida só a sidebar.
    const quota = page.locator('.da-shell__aside').getByTestId('storage-quota-block');
    await expect(quota, 'API tem storage mas a shell não mostra o bloco na sidebar').toBeVisible({
      timeout: 15_000,
    });
    await expect(quota.getByRole('progressbar').first()).toBeVisible({
      timeout: 10_000,
    });
  });

  /**
   * Opcional: validar `data-storage-warn="true"` quando o tenant tiver ≥90 % do plano.
   * Preparar dados (ex.: ingestões que somem uso) e exportar E2E_EXPECT_STORAGE_WARN=1.
   */
  test('opcional: alerta de quota do tenant (data-storage-warn)', async ({ page }) => {
    test.skip(
      process.env.E2E_EXPECT_STORAGE_WARN !== '1',
      'Defina E2E_EXPECT_STORAGE_WARN=1 após preparar tenant com uso ≥90 % do plano',
    );

    const email = process.env.E2E_USER_EMAIL!.trim();
    const password = process.env.E2E_USER_PASSWORD!.trim();

    await page.goto('/login');
    await dismissViteOverlayIfAny(page);
    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="password"]').fill(password);
    await page.getByRole('button', { name: 'Entrar', exact: true }).click();

    const mfaField = page.getByRole('textbox', { name: /código mfa/i });
    if (await mfaField.isVisible({ timeout: 4000 }).catch(() => false)) {
      test.skip(true, 'Conta com MFA');
    }

    await expect(page).toHaveURL(/\/app(\/|$)/, { timeout: 20_000 });
    const block = page.locator('.da-shell__aside').getByTestId('storage-quota-block');
    await expect(block).toBeVisible({ timeout: 25_000 });
    await expect(block).toHaveAttribute('data-storage-warn', 'true');
  });
});
