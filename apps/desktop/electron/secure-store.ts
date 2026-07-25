/**
 * Persistência de tokens com electron.safeStorage.
 * Ficheiro binário em userData — nunca em logs nem no renderer em claro.
 */
import { app, safeStorage } from "electron";
import fs from "node:fs";
import path from "node:path";
import type { StoredTokens } from "./types";

export type { StoredTokens };

const FILE_NAME = "session.enc";
const FALLBACK_NAME = "session.fallback.json";

function tokenPath(): string {
  return path.join(app.getPath("userData"), FILE_NAME);
}

function fallbackPath(): string {
  return path.join(app.getPath("userData"), FALLBACK_NAME);
}

export function saveTokens(tokens: StoredTokens): void {
  const payload = JSON.stringify(tokens);
  if (safeStorage.isEncryptionAvailable()) {
    const encrypted = safeStorage.encryptString(payload);
    fs.writeFileSync(tokenPath(), encrypted);
    if (fs.existsSync(fallbackPath())) {
      fs.unlinkSync(fallbackPath());
    }
    return;
  }
  // Fallback só quando o OS não oferece keyring (ex.: CI sem xvfb/keyring).
  fs.writeFileSync(fallbackPath(), payload, { mode: 0o600 });
}

export function loadTokens(): StoredTokens | null {
  try {
    if (fs.existsSync(tokenPath()) && safeStorage.isEncryptionAvailable()) {
      const buf = fs.readFileSync(tokenPath());
      const json = safeStorage.decryptString(buf);
      return JSON.parse(json) as StoredTokens;
    }
    if (fs.existsSync(fallbackPath())) {
      const json = fs.readFileSync(fallbackPath(), "utf8");
      return JSON.parse(json) as StoredTokens;
    }
  } catch (err) {
    console.error("[4Pro_BI Desktop] falha ao ler sessão:", (err as Error).message);
  }
  return null;
}

export function clearTokens(): void {
  for (const p of [tokenPath(), fallbackPath()]) {
    try {
      if (fs.existsSync(p)) {
        fs.unlinkSync(p);
      }
    } catch (err) {
      console.error("[4Pro_BI Desktop] falha ao limpar sessão:", (err as Error).message);
    }
  }
}
