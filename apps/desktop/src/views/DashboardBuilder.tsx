import { useMemo, useState, type FormEvent } from "react";
import { useAuth } from "../auth/AuthContext";
import type { DashboardWidget, WidgetType } from "../api/types";

function newId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `w-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function DashboardBuilder() {
  const { api } = useAuth();
  const [name, setName] = useState("Dashboard Desktop");
  const [description, setDescription] = useState("");
  const [widgets, setWidgets] = useState<DashboardWidget[]>([]);
  const [widgetTitle, setWidgetTitle] = useState("");
  const [widgetType, setWidgetType] = useState<WidgetType>("kpi");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const layout = useMemo(
    () => ({
      version: 1,
      columns: 12,
      widgets,
    }),
    [widgets],
  );

  function addWidget(e: FormEvent) {
    e.preventDefault();
    const title = widgetTitle.trim() || widgetType.toUpperCase();
    const col = widgets.length % 3;
    const row = Math.floor(widgets.length / 3);
    const next: DashboardWidget = {
      id: newId(),
      type: widgetType,
      title,
      x: col * 4,
      y: row * 3,
      w: widgetType === "table" ? 8 : 4,
      h: widgetType === "table" ? 4 : 3,
      query: null,
      options: {},
    };
    setWidgets((prev) => [...prev, next]);
    setWidgetTitle("");
    setSuccess(null);
    setError(null);
  }

  function removeWidget(id: string) {
    setWidgets((prev) => prev.filter((w) => w.id !== id));
  }

  async function publish(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) {
      setError("Indique um nome para o dashboard.");
      return;
    }
    if (widgets.length === 0) {
      setError("Adicione pelo menos um widget (KPI ou tabela).");
      return;
    }
    setBusy(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await api.publishDashboard({
        name: name.trim(),
        description: description.trim() || null,
        layout,
        client_draft_id: `desktop-dash-${Date.now()}`,
        publish: true,
      });
      setSuccess(
        `${res.message} · id ${res.dashboard_id} · v${res.version} · ${res.status}`,
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Falha ao publicar dashboard.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel" aria-labelledby="dash-title">
      <div className="panel-head">
        <h2 id="dash-title">Construtor de dashboard</h2>
      </div>
      <p className="muted">
        Monte um layout mínimo com widgets KPI e tabela; a publicação envia o
        manifesto para a API do tenant.
      </p>

      {error ? <p className="error-banner" role="alert">{error}</p> : null}
      {success ? <p className="success-banner" role="status">{success}</p> : null}

      <form className="stack form-grid" onSubmit={(e) => void publish(e)}>
        <label>
          Nome
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            maxLength={200}
            disabled={busy}
          />
        </label>
        <label>
          Descrição
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={busy}
          />
        </label>

        <div className="widget-composer">
          <label>
            Tipo
            <select
              value={widgetType}
              onChange={(e) => setWidgetType(e.target.value as WidgetType)}
              disabled={busy}
            >
              <option value="kpi">KPI</option>
              <option value="table">Tabela</option>
            </select>
          </label>
          <label>
            Título do widget
            <input
              value={widgetTitle}
              onChange={(e) => setWidgetTitle(e.target.value)}
              placeholder="ex.: Receita mensal"
              disabled={busy}
            />
          </label>
          <button
            type="button"
            className="btn ghost"
            disabled={busy}
            onClick={(e) => addWidget(e)}
          >
            Adicionar widget
          </button>
        </div>

        {widgets.length === 0 ? (
          <p className="empty-state">Nenhum widget ainda.</p>
        ) : (
          <div className="dash-canvas" aria-label="Pré-visualização do layout">
            {widgets.map((w) => (
              <article
                key={w.id}
                className={`dash-widget type-${w.type}`}
                style={{
                  gridColumn: `span ${Math.min(w.w, 12)}`,
                }}
              >
                <header>
                  <span className="badge">{w.type}</span>
                  <strong>{w.title}</strong>
                  <button
                    type="button"
                    className="btn ghost tiny"
                    onClick={() => removeWidget(w.id)}
                    aria-label={`Remover ${w.title}`}
                  >
                    Remover
                  </button>
                </header>
                <div className="widget-body muted">
                  {w.type === "kpi"
                    ? "Valor KPI (preenchido no Web após query)"
                    : "Grelha tabular (preenchida no Web após query)"}
                </div>
              </article>
            ))}
          </div>
        )}

        <div className="btn-row">
          <button type="submit" className="btn primary" disabled={busy}>
            {busy ? "A publicar…" : "Publicar dashboard"}
          </button>
        </div>
      </form>
    </section>
  );
}
