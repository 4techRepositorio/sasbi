/**
 * Scaffold Electron — Desktop 4Pro_BI (TICKET-017).
 * Auth + publish contra a API do tenant; sem cromo de terceiros na UX.
 */
const { app, BrowserWindow, ipcMain, safeStorage } = require('electron');
const path = require('path');
const { login, publishDataset, publishDashboard } = require('./api-client');

const API_BASE = process.env.FOURPRO_API_BASE || 'http://127.0.0.1:7418/api/v1';
let accessToken = null;

function createWindow() {
  const win = new BrowserWindow({
    width: 1100,
    height: 720,
    title: 'Desktop 4Pro_BI',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  win.loadFile(path.join(__dirname, 'index.html'));
}

app.whenReady().then(() => {
  ipcMain.handle('auth:login', async (_e, email, password) => {
    const tokens = await login(API_BASE, email, password);
    accessToken = tokens.access_token;
    if (safeStorage.isEncryptionAvailable() && tokens.refresh_token) {
      // Placeholder: persistência segura em evoluções.
      void safeStorage.encryptString(tokens.refresh_token);
    }
    return { ok: true, tenant_hint: tokens.token_type };
  });

  ipcMain.handle('desktop:publish-dataset', async (_e, payload) => {
    if (!accessToken) {
      throw new Error('Não autenticado');
    }
    return publishDataset(API_BASE, accessToken, payload);
  });

  ipcMain.handle('desktop:publish-dashboard', async (_e, payload) => {
    if (!accessToken) {
      throw new Error('Não autenticado');
    }
    return publishDashboard(API_BASE, accessToken, payload);
  });

  createWindow();
});

app.on('window-all-closed', () => {
  accessToken = null;
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
