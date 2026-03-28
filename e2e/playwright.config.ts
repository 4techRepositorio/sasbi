import { defineConfig, devices } from '@playwright/test';

const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? 'http://127.0.0.1:4200';
const isCi = process.env.CI === 'true';

/** Em CI ou com PLAYWRIGHT_HTML_REPORT=1 gera pasta playwright-report/ (artefactos no GitHub Actions). */
const reporter =
  isCi || process.env.PLAYWRIGHT_HTML_REPORT === '1'
    ? [['list'], ['html', { open: 'never', outputFolder: 'playwright-report' }]]
    : [['list']];

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  forbidOnly: isCi,
  retries: isCi ? 1 : 0,
  workers: 1,
  reporter,
  timeout: 60_000,
  use: {
    baseURL,
    trace: 'on-first-retry',
    ...devices['Desktop Chrome'],
  },
});
