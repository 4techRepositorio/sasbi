import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { ApiClient, resolveApiBaseUrl } from "../api/client";
import type {
  DesktopSessionInfo,
  LoginRequest,
  TokenResponse,
} from "../api/types";
import {
  clearStoredTokens,
  readStoredTokens,
  tokensFromResponse,
  writeStoredTokens,
} from "./tokenStore";

export type AuthPhase =
  | "booting"
  | "anonymous"
  | "mfa"
  | "authenticated"
  | "error";

interface AuthState {
  phase: AuthPhase;
  api: ApiClient;
  accessToken: string | null;
  refreshToken: string | null;
  tenantName: string | null;
  tenantId: string | null;
  role: string | null;
  session: DesktopSessionInfo | null;
  mfaToken: string | null;
  error: string | null;
  apiBaseUrl: string;
}

interface AuthContextValue extends AuthState {
  login: (creds: LoginRequest) => Promise<void>;
  verifyMfa: (code: string) => Promise<void>;
  logout: () => Promise<void>;
  reloadSession: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const apiBaseUrl = resolveApiBaseUrl();
  const [phase, setPhase] = useState<AuthPhase>("booting");
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [tenantName, setTenantName] = useState<string | null>(null);
  const [tenantId, setTenantId] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [session, setSession] = useState<DesktopSessionInfo | null>(null);
  const [mfaToken, setMfaToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const applyTokens = useCallback(async (res: TokenResponse) => {
    const stored = tokensFromResponse(res);
    await writeStoredTokens(stored);
    setAccessToken(stored.access_token);
    setRefreshToken(stored.refresh_token);
    setTenantId(stored.tenant_id ?? null);
    setTenantName(stored.tenant_name ?? null);
    setRole(stored.role ?? null);
    setMfaToken(null);
    setPhase("authenticated");
  }, []);

  const onAuthExpired = useCallback(async () => {
    await clearStoredTokens();
    setAccessToken(null);
    setRefreshToken(null);
    setSession(null);
    setTenantName(null);
    setTenantId(null);
    setRole(null);
    setPhase("anonymous");
    setError("Sessão expirada. Inicie sessão novamente.");
  }, []);

  const api = useMemo(
    () =>
      new ApiClient(apiBaseUrl, {
        getAccessToken: () => accessToken,
        getRefreshToken: () => refreshToken,
        onTokensRefreshed: applyTokens,
        onAuthExpired,
      }),
    [apiBaseUrl, accessToken, refreshToken, applyTokens, onAuthExpired],
  );

  const reloadSession = useCallback(async () => {
    const info = await api.getSessionInfo();
    setSession(info);
    setTenantId(info.tenant_id);
    setTenantName(info.tenant_name);
    setRole(info.role);
  }, [api]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const stored = await readStoredTokens();
        if (cancelled) return;
        if (!stored?.access_token) {
          setPhase("anonymous");
          return;
        }
        setAccessToken(stored.access_token);
        setRefreshToken(stored.refresh_token);
        setTenantId(stored.tenant_id ?? null);
        setTenantName(stored.tenant_name ?? null);
        setRole(stored.role ?? null);
        setPhase("authenticated");
      } catch {
        if (!cancelled) {
          setPhase("anonymous");
          setError("Não foi possível restaurar a sessão.");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (phase !== "authenticated" || !accessToken) return;
    let cancelled = false;
    (async () => {
      try {
        await reloadSession();
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Falha ao carregar contexto da sessão.",
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [phase, accessToken, reloadSession]);

  const login = useCallback(
    async (creds: LoginRequest) => {
      setError(null);
      try {
        const result = await api.login(creds);
        if (result.mfa_required) {
          setMfaToken(result.mfa_token);
          setPhase("mfa");
          return;
        }
        await applyTokens(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Falha no login.");
        setPhase("anonymous");
      }
    },
    [api, applyTokens],
  );

  const verifyMfa = useCallback(
    async (code: string) => {
      if (!mfaToken) {
        setError("Desafio MFA em falta. Volte a iniciar sessão.");
        setPhase("anonymous");
        return;
      }
      setError(null);
      try {
        const tokens = await api.verifyMfa({ mfa_token: mfaToken, code });
        await applyTokens(tokens);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Código MFA inválido.");
      }
    },
    [api, mfaToken, applyTokens],
  );

  const logout = useCallback(async () => {
    await clearStoredTokens();
    setAccessToken(null);
    setRefreshToken(null);
    setSession(null);
    setTenantName(null);
    setTenantId(null);
    setRole(null);
    setMfaToken(null);
    setError(null);
    setPhase("anonymous");
  }, []);

  const value: AuthContextValue = {
    phase,
    api,
    accessToken,
    refreshToken,
    tenantName,
    tenantId,
    role,
    session,
    mfaToken,
    error,
    apiBaseUrl,
    login,
    verifyMfa,
    logout,
    reloadSession,
    clearError: () => setError(null),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }
  return ctx;
}
