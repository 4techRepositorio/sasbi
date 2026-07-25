import { useAuth } from "../auth/AuthContext";

export function SessionPanel() {
  const { session, tenantName, tenantId, role, apiBaseUrl, reloadSession } =
    useAuth();

  return (
    <section className="panel" aria-labelledby="session-title">
      <div className="panel-head">
        <h2 id="session-title">Sessão</h2>
        <button type="button" className="btn ghost" onClick={() => void reloadSession()}>
          Actualizar
        </button>
      </div>
      {!session ? (
        <p className="muted">A carregar contexto do tenant…</p>
      ) : (
        <dl className="kv">
          <div>
            <dt>Tenant</dt>
            <dd>{session.tenant_name || tenantName || "—"}</dd>
          </div>
          <div>
            <dt>ID do tenant</dt>
            <dd className="mono">{session.tenant_id || tenantId}</dd>
          </div>
          <div>
            <dt>Papel</dt>
            <dd>{session.role || role}</dd>
          </div>
          <div>
            <dt>Utilizador</dt>
            <dd className="mono">{session.user_id}</dd>
          </div>
          <div>
            <dt>API</dt>
            <dd className="mono">{session.api_base_url || apiBaseUrl}</dd>
          </div>
          <div>
            <dt>Funcionalidades</dt>
            <dd>
              {session.features.length
                ? session.features.join(", ")
                : "— (via /me/context se /desktop/session indisponível)"}
            </dd>
          </div>
        </dl>
      )}
    </section>
  );
}
