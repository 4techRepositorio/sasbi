/**
 * Preload — bridge tipada para o renderer (contextIsolation).
 */
import { contextBridge, ipcRenderer } from "electron";
import type { StoredTokens } from "./types";

export type { StoredTokens };

const desktopBridge = {
  getTokens: (): Promise<StoredTokens | null> =>
    ipcRenderer.invoke("auth:getTokens"),
  setTokens: (
    tokens: StoredTokens,
  ): Promise<{ ok: boolean; reason?: string }> =>
    ipcRenderer.invoke("auth:setTokens", tokens),
  clearTokens: (): Promise<{ ok: true }> =>
    ipcRenderer.invoke("auth:clearTokens"),
  getVersion: (): Promise<string> => ipcRenderer.invoke("app:getVersion"),
  getUserDataPath: (): Promise<string> =>
    ipcRenderer.invoke("app:getUserDataPath"),
};

contextBridge.exposeInMainWorld("fourproDesktop", desktopBridge);

export type FourproDesktopBridge = typeof desktopBridge;
