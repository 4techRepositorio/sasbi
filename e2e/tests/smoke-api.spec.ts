import { test, expect } from '@playwright/test';

/**
 * Smoke HTTP contra API real (Compose, uvicorn local ou staging).
 * Sem E2E_API_BASE_URL o teste é ignorado — não falha em CI nem em clone fresco.
 */
test.describe('API smoke', () => {
  test('GET /api/v1/health responde OK', async ({ request }) => {
    const base = process.env.E2E_API_BASE_URL?.replace(/\/$/, '');
    test.skip(!base, 'Defina E2E_API_BASE_URL (ex.: http://127.0.0.1:8000)');

    const res = await request.get(`${base}/api/v1/health`, { timeout: 5_000 });
    expect(res.ok(), `health falhou: ${res.status()} ${await res.text()}`).toBeTruthy();
  });

  test('GET /api/v1/health/ready responde OK', async ({ request }) => {
    const base = process.env.E2E_API_BASE_URL?.replace(/\/$/, '');
    test.skip(!base, 'Defina E2E_API_BASE_URL (ex.: http://127.0.0.1:8000)');

    const res = await request.get(`${base}/api/v1/health/ready`, { timeout: 5_000 });
    expect(
      res.ok(),
      `health/ready falhou: ${res.status()} ${await res.text()}`,
    ).toBeTruthy();
  });

  test('rota autenticada sem token responde 401 (segurança API)', async ({ request }) => {
    const base = process.env.E2E_API_BASE_URL?.replace(/\/$/, '');
    test.skip(!base, 'Defina E2E_API_BASE_URL (ex.: http://127.0.0.1:8000)');

    const res = await request.get(`${base}/api/v1/me/context`, { timeout: 5_000 });
    expect(res.status(), await res.text()).toBe(401);
  });
});
