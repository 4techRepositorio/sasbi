import { useState } from "react";
import { useAuth } from "./auth/AuthContext";
import { LoginView } from "./views/LoginView";
import { SessionPanel } from "./views/SessionPanel";
import { DataSourceWizard } from "./views/DataSourceWizard";
import { DashboardBuilder } from "./views/DashboardBuilder";

type NavId = "session" | "sources" | "dashboard";

const NAV: { id: NavId; label: string }[] = [
  { id: "session", label: "Sessão" },
  { id: "sources", label: "Fontes de dados" },
  { id: "dashboard", label: "Dashboard" },
];

export function App() {
  const { phase, tenantName, role, logout, error } = useAuth();
  const [nav, setNav] = useState<NavId>("sources");

  if (phase === "booting") {
    return (
      <div className="boot-screen">
        <p className="brand-mark">4Pro_BI Desktop</p>
        <p className="muted">A iniciar…</p>
      </div>
    );
  }

  if (phase === "anonymous" || phase === "mfa") {
    return <LoginView />;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="brand-mark">4Pro_BI Desktop</span>
          <span className="tenant-pill" title="Tenant activo">
            {tenantName ?? "Tenant"}
          </span>
          {role ? <span className="role-pill">{role}</span> : null}
        </div>
        <nav className="side-nav" aria-label="Principal">
          {NAV.map((item) => (
            <button
              key={item.id}
              type="button"
              className={nav === item.id ? "nav-item active" : "nav-item"}
              onClick={() => setNav(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
        <div className="sidebar-foot">
          <button type="button" className="btn ghost block" onClick={() => void logout()}>
            Terminar sessão
          </button>
        </div>
      </aside>
      <main className="main">
        {error ? <p className="error-banner sticky" role="alert">{error}</p> : null}
        {nav === "session" ? <SessionPanel /> : null}
        {nav === "sources" ? <DataSourceWizard /> : null}
        {nav === "dashboard" ? <DashboardBuilder /> : null}
      </main>
    </div>
  );
}
