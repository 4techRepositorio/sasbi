import type { StoredTokens } from "./shared/session-types";

export interface FourproDesktopBridge {
  getTokens: () => Promise<StoredTokens | null>;
  setTokens: (
    tokens: StoredTokens,
  ) => Promise<{ ok: boolean; reason?: string }>;
  clearTokens: () => Promise<{ ok: true }>;
  getVersion: () => Promise<string>;
  getUserDataPath: () => Promise<string>;
}
