/**
 * Processo principal Electron — 4Pro_BI Desktop (TICKET-017).
 * Tokens só em safeStorage; renderer acede via IPC tipado no preload.
 */
import {
  app,
  BrowserWindow,
  ipcMain,
  safeStorage,
  session,
} from "electron";
import fs from "node:fs";
import path from "node:path";
import type { StoredTokens } from "./types";
import { clearTokens, loadTokens, saveTokens } from "./secure-store";

const isDev = Boolean(process.env.VITE_DEV_SERVER_URL);

let mainWindow: BrowserWindow | null = null;

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 840,
    minWidth: 960,
    minHeight: 640,
    title: "4Pro_BI Desktop",
    backgroundColor: "#0f1419",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  mainWindow.setMenuBarVisibility(false);

  if (isDev && process.env.VITE_DEV_SERVER_URL) {
    void mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
    mainWindow.webContents.openDevTools({ mode: "detach" });
  } else {
    void mainWindow.loadFile(path.join(__dirname, "../dist/index.html"));
  }

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

function registerIpc(): void {
  ipcMain.handle("auth:getTokens", (): StoredTokens | null => {
    return loadTokens();
  });

  ipcMain.handle(
    "auth:setTokens",
    (_event, tokens: StoredTokens): { ok: boolean; reason?: string } => {
      if (!tokens?.access_token || !tokens?.refresh_token) {
        return { ok: false, reason: "tokens_invalidos" };
      }
      if (!safeStorage.isEncryptionAvailable()) {
        console.warn(
          "[4Pro_BI Desktop] safeStorage indisponível — tokens guardados com fallback local (só desenvolvimento).",
        );
      }
      saveTokens(tokens);
      return { ok: true };
    },
  );

  ipcMain.handle("auth:clearTokens", (): { ok: true } => {
    clearTokens();
    return { ok: true };
  });

  ipcMain.handle("app:getVersion", (): string => app.getVersion());

  ipcMain.handle("app:getUserDataPath", (): string => app.getPath("userData"));
}

app.whenReady().then(() => {
  try {
    fs.mkdirSync(app.getPath("userData"), { recursive: true });
  } catch {
    /* ignore */
  }

  session.defaultSession.webRequest.onBeforeRequest((details, callback) => {
    const url = details.url;
    const allowed =
      url.startsWith("file://") ||
      url.startsWith("devtools://") ||
      url.startsWith("http://127.0.0.1:5179") ||
      url.startsWith("http://localhost:5179") ||
      url.startsWith("http://127.0.0.1:") ||
      url.startsWith("http://localhost:") ||
      url.startsWith("https://");
    callback({ cancel: !allowed });
  });

  registerIpc();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
