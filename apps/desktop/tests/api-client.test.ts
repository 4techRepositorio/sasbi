import { describe, expect, it, vi } from "vitest";
import {
  ApiClient,
  DEFAULT_API_BASE_URL,
  resolveApiBaseUrl,
} from "../src/api/client";
import { ApiError, type TokenResponse } from "../src/api/types";
import { tokensFromResponse } from "../src/auth/tokenStore";

describe("resolveApiBaseUrl", () => {
  it("usa o default 7418 quando env vazio", () => {
    expect(resolveApiBaseUrl(undefined)).toBe(DEFAULT_API_BASE_URL);
    expect(resolveApiBaseUrl("")).toBe(DEFAULT_API_BASE_URL);
    expect(resolveApiBaseUrl("   ")).toBe(DEFAULT_API_BASE_URL);
  });

  it("remove barra final", () => {
    expect(resolveApiBaseUrl("http://127.0.0.1:7418/")).toBe(
      "http://127.0.0.1:7418",
    );
  });
});

describe("tokensFromResponse", () => {
  it("mapeia TokenResponse para armazenamento", () => {
    const res: TokenResponse = {
      mfa_required: false,
      access_token: "a",
      refresh_token: "r",
      token_type: "bearer",
      expires_in: 900,
      tenant_id: "t1",
      tenant_name: "Acme",
      role: "admin",
    };
    const stored = tokensFromResponse(res);
    expect(stored.access_token).toBe("a");
    expect(stored.refresh_token).toBe("r");
    expect(stored.tenant_name).toBe("Acme");
    expect(stored.expires_at).toBeGreaterThan(Date.now());
  });
});

describe("ApiClient", () => {
  it("login POST /api/v1/auth/login", async () => {
    const fetchMock = vi.fn(
      async (_input: RequestInfo | URL, _init?: RequestInit) =>
        Response.json({
          mfa_required: false,
          access_token: "acc",
          refresh_token: "ref",
          token_type: "bearer",
          expires_in: 60,
          tenant_id: "tid",
          tenant_name: "Demo",
          role: "admin",
        }),
    );
    const client = new ApiClient(
      "http://127.0.0.1:7418",
      {
        getAccessToken: () => null,
        getRefreshToken: () => null,
        onTokensRefreshed: () => undefined,
        onAuthExpired: () => undefined,
      },
      fetchMock as unknown as typeof fetch,
    );
    const result = await client.login({
      email: "a@b.com",
      password: "secret",
    });
    expect(result.mfa_required).toBe(false);
    expect(fetchMock).toHaveBeenCalledOnce();
    expect(fetchMock.mock.calls[0]?.[0]).toBe(
      "http://127.0.0.1:7418/api/v1/auth/login",
    );
    expect(fetchMock.mock.calls[0]?.[1]?.method).toBe("POST");
  });

  it("getSessionInfo faz fallback para /me/context em 404", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/api/v1/desktop/session")) {
        return new Response(JSON.stringify({ detail: "Not Found" }), {
          status: 404,
          headers: { "Content-Type": "application/json" },
        });
      }
      if (url.endsWith("/api/v1/me/context")) {
        return Response.json({
          user_id: "u1",
          tenant_id: "t1",
          tenant_name: "Tenant X",
          tenant_slug: "tx",
          role: "admin",
        });
      }
      return new Response("unexpected", { status: 500 });
    });

    const client = new ApiClient(
      "http://127.0.0.1:7418",
      {
        getAccessToken: () => "tok",
        getRefreshToken: () => "ref",
        onTokensRefreshed: () => undefined,
        onAuthExpired: () => undefined,
      },
      fetchMock as unknown as typeof fetch,
    );

    const session = await client.getSessionInfo();
    expect(session.tenant_name).toBe("Tenant X");
    expect(session.api_base_url).toBe("http://127.0.0.1:7418");
    expect(session.features).toEqual([]);
  });

  it("lança ApiError amigável em 403", async () => {
    const fetchMock = vi.fn(
      async () =>
        new Response(JSON.stringify({ detail: "Forbidden" }), {
          status: 403,
          headers: { "Content-Type": "application/json" },
        }),
    );
    const client = new ApiClient(
      "http://api.test",
      {
        getAccessToken: () => "tok",
        getRefreshToken: () => null,
        onTokensRefreshed: () => undefined,
        onAuthExpired: () => undefined,
      },
      fetchMock as unknown as typeof fetch,
    );
    await expect(client.listConnectors()).rejects.toBeInstanceOf(ApiError);
    await expect(client.listConnectors()).rejects.toMatchObject({
      message: "Forbidden",
      status: 403,
    });
  });
});
