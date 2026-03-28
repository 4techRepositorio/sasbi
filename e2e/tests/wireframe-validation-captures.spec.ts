import * as path from 'path';

import { expect, test } from '@playwright/test';

import { dismissViteOverlayIfAny } from '../helpers/vite-overlay';

/** Saída alinhada a `docs/wireframes/validation-*.md` (nomes sugeridos nas tabelas). */
const EXPORTS_DIR = path.join(__dirname, '..', '..', 'docs', 'assets', 'wireframes', 'exports');

function yyyymmdd(): string {
  return new Date().toISOString().slice(0, 10).replace(/-/g, '');
}

test.describe('Wireframe — capturas para validation docs', () => {
  test.beforeEach(() => {
    test.skip(
      process.env.E2E_WIREFRAME_CAPTURES !== '1',
      'Defina E2E_WIREFRAME_CAPTURES=1 para gravar PNG em docs/assets/wireframes/exports/',
    );
  });

  test('ecrãs públicos (login, forgot, reset)', async ({ page }) => {
    const d = yyyymmdd();

    await page.goto('/login');
    await dismissViteOverlayIfAny(page);
    await expect(page.getByRole('heading', { name: /bem-vindo de volta/i })).toBeVisible();
    await page.screenshot({ path: path.join(EXPORTS_DIR, `identity-login-v1-${d}.png`), fullPage: true });

    await page.goto('/forgot-password');
    await dismissViteOverlayIfAny(page);
    await page.screenshot({ path: path.join(EXPORTS_DIR, `identity-forgot-v1-${d}.png`), fullPage: true });

    await page.goto('/reset-password');
    await dismissViteOverlayIfAny(page);
    await page.screenshot({ path: path.join(EXPORTS_DIR, `identity-reset-v1-${d}.png`), fullPage: true });
  });

  test('área /app (dashboard, pipeline, admin, plano)', async ({ page }) => {
    const email = process.env.E2E_USER_EMAIL?.trim() ?? '';
    const password = process.env.E2E_USER_PASSWORD?.trim() ?? '';
    test.skip(!email || !password, 'Defina E2E_USER_EMAIL e E2E_USER_PASSWORD');

    const d = yyyymmdd();

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

    await page.goto('/app/dashboard');
    await page.waitForLoadState('networkidle').catch(() => undefined);

    const shellAside = page.locator('aside.da-shell__aside');
    await expect(shellAside).toBeVisible({ timeout: 15_000 });
    await shellAside.screenshot({ path: path.join(EXPORTS_DIR, `workspace-shell-v1-${d}.png`) });

    await page.screenshot({ path: path.join(EXPORTS_DIR, `workspace-dashboard-v1-${d}.png`), fullPage: true });

    await page.goto('/app/upload');
    await dismissViteOverlayIfAny(page);
    await page.screenshot({ path: path.join(EXPORTS_DIR, `pipeline-upload-v1-${d}.png`), fullPage: true });

    await page.goto('/app/ingestions');
    await page.screenshot({ path: path.join(EXPORTS_DIR, `pipeline-ingestions-v1-${d}.png`), fullPage: true });

    await page.goto('/app/datasets');
    await page.screenshot({ path: path.join(EXPORTS_DIR, `pipeline-datasets-v1-${d}.png`), fullPage: true });

    await page.goto('/app/tenant-users');
    await page.screenshot({ path: path.join(EXPORTS_DIR, `identity-admin-users-v1-${d}.png`), fullPage: true });

    await page.goto('/app/tenant-audit');
    await dismissViteOverlayIfAny(page);
    await page.screenshot({ path: path.join(EXPORTS_DIR, `tenant-audit-v1-${d}.png`), fullPage: true });

    await page.goto('/app/billing');
    await dismissViteOverlayIfAny(page);
    await page.screenshot({ path: path.join(EXPORTS_DIR, `billing-overview-v1-${d}.png`), fullPage: true });

    await page.goto('/app/settings');
    await dismissViteOverlayIfAny(page);
    await page.screenshot({ path: path.join(EXPORTS_DIR, `settings-placeholder-v1-${d}.png`), fullPage: true });
  });
});
