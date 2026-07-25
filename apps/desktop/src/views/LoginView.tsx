import { useState, type FormEvent } from "react";
import { useAuth } from "../auth/AuthContext";

export function LoginView() {
  const { login, verifyMfa, phase, error, clearError, apiBaseUrl } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mfaCode, setMfaCode] = useState("");
  const [busy, setBusy] = useState(false);

  async function onLogin(e: FormEvent) {
    e.preventDefault();
    clearError();
    setBusy(true);
    try {
      await login({ email: email.trim(), password });
    } finally {
      setBusy(false);
    }
  }

  async function onMfa(e: FormEvent) {
    e.preventDefault();
    clearError();
    setBusy(true);
    try {
      await verifyMfa(mfaCode.trim());
    } finally {
      setBusy(false);
    }
  }

  if (phase === "mfa") {
    return (
      <div className="auth-shell">
        <div className="auth-panel">
          <p className="brand-mark">4Pro_BI Desktop</p>
          <h1>Verificação MFA</h1>
          <p className="muted">
            Introduza o código de autenticação multifactor para continuar.
          </p>
          <form onSubmit={onMfa} className="stack">
            <label>
              Código MFA
              <input
                value={mfaCode}
                onChange={(e) => setMfaCode(e.target.value)}
                autoComplete="one-time-code"
                inputMode="numeric"
                required
                minLength={4}
                maxLength={12}
                disabled={busy}
              />
            </label>
            {error ? <p className="error-banner" role="alert">{error}</p> : null}
            <button type="submit" className="btn primary" disabled={busy}>
              {busy ? "A verificar…" : "Confirmar"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-shell">
      <div className="auth-panel">
        <p className="brand-mark">4Pro_BI Desktop</p>
        <h1>Iniciar sessão</h1>
        <p className="muted">
          Autoração de fontes e dashboards no tenant da sua organização.
        </p>
        <form onSubmit={onLogin} className="stack">
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="username"
              required
              disabled={busy}
            />
          </label>
          <label>
            Palavra-passe
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
              disabled={busy}
            />
          </label>
          {error ? <p className="error-banner" role="alert">{error}</p> : null}
          <button type="submit" className="btn primary" disabled={busy}>
            {busy ? "A entrar…" : "Entrar"}
          </button>
        </form>
        <p className="api-hint">API: {apiBaseUrl}</p>
      </div>
    </div>
  );
}
