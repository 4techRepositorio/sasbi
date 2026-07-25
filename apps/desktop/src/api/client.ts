/**
 * Cliente HTTP da API 4Pro_BI — base URL via VITE_API_BASE_URL.
 */
import {
  ApiError,
  type ConnectionTestResult,
  type ConnectorCatalogResponse,
  type DataSourceCreate,
  type DataSourceItem,
  type DesktopPublishDashboardRequest,
  type DesktopPublishDashboardResponse,
  type DesktopPublishDatasetRequest,
  type DesktopPublishDatasetResponse,
  type DesktopSessionInfo,
  type LoginRequest,
  type LoginResult,
  type MeContextResponse,
  type MfaVerifyRequest,
  type PaginatedDataSourceList,
  type SyncEnqueuedResponse,
  type SyncRequest,
  type TokenResponse,
} from "./types";

export const DEFAULT_API_BASE_URL = "http://127.0.0.1:7418";

export function resolveApiBaseUrl(
  envValue: string | undefined = import.meta.env.VITE_API_BASE_URL,
): string {
  const raw = (envValue ?? DEFAULT_API_BASE_URL).trim().replace(/\/+$/, "");
  return raw || DEFAULT_API_BASE_URL;
}

export interface TokenProvider {
  getAccessToken: () => string | null;
  getRefreshToken: () => string | null;
  onTokensRefreshed: (tokens: TokenResponse) => void | Promise<void>;
  onAuthExpired: () => void | Promise<void>;
}

type FetchLike = typeof fetch;

export class ApiClient {
  readonly baseUrl: string;
  private readonly tokens: TokenProvider;
  private readonly fetchImpl: FetchLike;
  private refreshInFlight: Promise<TokenResponse | null> | null = null;

  constructor(
    baseUrl: string,
    tokens: TokenProvider,
    fetchImpl: FetchLike = fetch.bind(globalThis),
  ) {
    this.baseUrl = baseUrl.replace(/\/+$/, "");
    this.tokens = tokens;
    this.fetchImpl = fetchImpl;
  }

  private url(path: string): string {
    const p = path.startsWith("/") ? path : `/${path}`;
    return `${this.baseUrl}${p}`;
  }

  private async parseBody(res: Response): Promise<unknown> {
    const text = await res.text();
    if (!text) return null;
    try {
      return JSON.parse(text) as unknown;
    } catch {
      return text;
    }
  }

  private friendlyError(status: number, body: unknown): string {
    if (body && typeof body === "object" && "detail" in body) {
      const detail = (body as { detail: unknown }).detail;
      if (typeof detail === "string") return detail;
      if (Array.isArray(detail)) {
        return detail
          .map((d) =>
            typeof d === "object" && d && "msg" in d
              ? String((d as { msg: unknown }).msg)
              : JSON.stringify(d),
          )
          .join("; ");
      }
    }
    if (status === 401) return "Sessão inválida ou expirada.";
    if (status === 403) return "Sem permissão para esta operação.";
    if (status === 404) return "Recurso não encontrado.";
    if (status >= 500) return "Erro no servidor. Tente novamente.";
    return `Pedido falhou (${status}).`;
  }

  async request<T>(
    path: string,
    init: RequestInit = {},
    opts: { auth?: boolean; retry?: boolean } = {},
  ): Promise<T> {
    const { auth = true, retry = true } = opts;
    const headers = new Headers(init.headers);
    if (!headers.has("Content-Type") && init.body) {
      headers.set("Content-Type", "application/json");
    }
    if (auth) {
      const access = this.tokens.getAccessToken();
      if (access) {
        headers.set("Authorization", `Bearer ${access}`);
      }
    }

    const res = await this.fetchImpl(this.url(path), { ...init, headers });
    if (res.status === 401 && auth && retry) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        return this.request<T>(path, init, { auth, retry: false });
      }
      await this.tokens.onAuthExpired();
    }

    const body = await this.parseBody(res);
    if (!res.ok) {
      throw new ApiError(this.friendlyError(res.status, body), res.status, body);
    }
    return body as T;
  }

  private async refreshAccessToken(): Promise<TokenResponse | null> {
    if (this.refreshInFlight) return this.refreshInFlight;
    const refresh = this.tokens.getRefreshToken();
    if (!refresh) return null;

    this.refreshInFlight = (async () => {
      try {
        const tokens = await this.request<TokenResponse>(
          "/api/v1/auth/refresh",
          {
            method: "POST",
            body: JSON.stringify({ refresh_token: refresh }),
          },
          { auth: false, retry: false },
        );
        await this.tokens.onTokensRefreshed(tokens);
        return tokens;
      } catch {
        return null;
      } finally {
        this.refreshInFlight = null;
      }
    })();

    return this.refreshInFlight;
  }

  login(body: LoginRequest): Promise<LoginResult> {
    return this.request<LoginResult>(
      "/api/v1/auth/login",
      { method: "POST", body: JSON.stringify(body) },
      { auth: false },
    );
  }

  verifyMfa(body: MfaVerifyRequest): Promise<TokenResponse> {
    return this.request<TokenResponse>(
      "/api/v1/auth/mfa/verify",
      { method: "POST", body: JSON.stringify(body) },
      { auth: false },
    );
  }

  refresh(refreshToken: string): Promise<TokenResponse> {
    return this.request<TokenResponse>(
      "/api/v1/auth/refresh",
      {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
      },
      { auth: false },
    );
  }

  getMeContext(): Promise<MeContextResponse> {
    return this.request<MeContextResponse>("/api/v1/me/context");
  }

  /**
   * Prefere GET /api/v1/desktop/session; se 404, mapeia /me/context.
   */
  async getSessionInfo(): Promise<DesktopSessionInfo> {
    try {
      return await this.request<DesktopSessionInfo>("/api/v1/desktop/session", {
        method: "GET",
      });
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        const ctx = await this.getMeContext();
        return {
          user_id: ctx.user_id,
          tenant_id: ctx.tenant_id,
          tenant_name: ctx.tenant_name ?? "Tenant",
          role: ctx.role,
          api_base_url: this.baseUrl,
          features: [],
        };
      }
      throw err;
    }
  }

  listConnectors(): Promise<ConnectorCatalogResponse> {
    return this.request<ConnectorCatalogResponse>("/api/v1/connectors");
  }

  listDataSources(
    limit = 50,
    offset = 0,
  ): Promise<PaginatedDataSourceList> {
    return this.request<PaginatedDataSourceList>(
      `/api/v1/data-sources?limit=${limit}&offset=${offset}`,
    );
  }

  createDataSource(body: DataSourceCreate): Promise<DataSourceItem> {
    return this.request<DataSourceItem>("/api/v1/data-sources", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  testConnection(
    id: string,
    body?: { config?: Record<string, unknown>; secret?: Record<string, string> },
  ): Promise<ConnectionTestResult> {
    return this.request<ConnectionTestResult>(
      `/api/v1/data-sources/${encodeURIComponent(id)}/test`,
      {
        method: "POST",
        body: JSON.stringify(body ?? {}),
      },
    );
  }

  /**
   * Teste antes de persistir — POST /api/v1/data-sources/test (se disponível).
   * Fallback: cria recurso temporário não é feito aqui; devolve erro amigável.
   */
  testConnectionDraft(body: DataSourceCreate): Promise<ConnectionTestResult> {
    return this.request<ConnectionTestResult>("/api/v1/data-sources/test", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  triggerSync(
    id: string,
    body: SyncRequest = { mode: "full" },
  ): Promise<SyncEnqueuedResponse> {
    return this.request<SyncEnqueuedResponse>(
      `/api/v1/data-sources/${encodeURIComponent(id)}/sync`,
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    );
  }

  publishDataset(
    body: DesktopPublishDatasetRequest,
  ): Promise<DesktopPublishDatasetResponse> {
    return this.request<DesktopPublishDatasetResponse>(
      "/api/v1/desktop/publish-dataset",
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    );
  }

  publishDashboard(
    body: DesktopPublishDashboardRequest,
  ): Promise<DesktopPublishDashboardResponse> {
    return this.request<DesktopPublishDashboardResponse>(
      "/api/v1/desktop/publish-dashboard",
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    );
  }
}
