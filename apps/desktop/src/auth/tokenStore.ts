/**
 * Persistência de sessão via bridge Electron (safeStorage).
 * Em browser puro (testes Vite), usa memory fallback — nunca localStorage com tokens.
 */
import type { StoredTokens } from "../shared/session-types";
import type { TokenResponse } from "../api/types";

const memory = new Map<string, StoredTokens>();

function bridge() {
  return typeof window !== "undefined" ? window.fourproDesktop : undefined;
}

export async function readStoredTokens(): Promise<StoredTokens | null> {
  const b = bridge();
  if (b) return b.getTokens();
  return memory.get("session") ?? null;
}

export async function writeStoredTokens(
  tokens: StoredTokens,
): Promise<{ ok: boolean; reason?: string }> {
  const b = bridge();
  if (b) return b.setTokens(tokens);
  memory.set("session", tokens);
  return { ok: true };
}

export async function clearStoredTokens(): Promise<void> {
  const b = bridge();
  if (b) {
    await b.clearTokens();
    return;
  }
  memory.delete("session");
}

export function tokensFromResponse(res: TokenResponse): StoredTokens {
  return {
    access_token: res.access_token,
    refresh_token: res.refresh_token,
    expires_at: Date.now() + res.expires_in * 1000,
    tenant_id: res.tenant_id ?? null,
    tenant_name: res.tenant_name ?? null,
    role: res.role ?? null,
  };
}
