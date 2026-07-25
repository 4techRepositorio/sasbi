import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { useAuth } from "../auth/AuthContext";
import { ApiError } from "../api/types";
import type {
  ConnectorCapability,
  ConnectorType,
  DataSourceCreate,
  DataSourceItem,
} from "../api/types";

type WizardStep = "list" | "pick" | "configure" | "done";

const MVP_TYPES: ConnectorType[] = ["postgres", "rest_json"];

const FALLBACK_CONNECTORS: ConnectorCapability[] = [
  {
    connector_type: "postgres",
    display_name: "PostgreSQL",
    description: "Base de dados PostgreSQL (host, base, utilizador).",
    auth_kinds: ["password"],
    supports_incremental: true,
    supports_discover: true,
    max_sample_rows: 100,
    config_schema_hint: {
      host: "string",
      port: "number",
      database: "string",
      username: "string",
      ssl: "boolean",
    },
  },
  {
    connector_type: "rest_json",
    display_name: "API REST (JSON)",
    description: "Endpoint HTTP que devolve JSON tabular ou lista de objectos.",
    auth_kinds: ["none", "token", "api_key"],
    supports_incremental: false,
    supports_discover: true,
    max_sample_rows: 100,
    config_schema_hint: {
      base_url: "string",
      path: "string",
      method: "GET|POST",
    },
  },
];

export function DataSourceWizard() {
  const { api } = useAuth();
  const [step, setStep] = useState<WizardStep>("list");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [sources, setSources] = useState<DataSourceItem[]>([]);
  const [catalog, setCatalog] = useState<ConnectorCapability[]>([]);
  const [selected, setSelected] = useState<ConnectorCapability | null>(null);
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState<DataSourceItem | null>(null);

  // Form state
  const [name, setName] = useState("");
  const [host, setHost] = useState("127.0.0.1");
  const [port, setPort] = useState("5432");
  const [database, setDatabase] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [ssl, setSsl] = useState(false);
  const [baseUrl, setBaseUrl] = useState("https://");
  const [restPath, setRestPath] = useState("/data");
  const [apiKey, setApiKey] = useState("");
  const [objectId, setObjectId] = useState("");
  const [datasetName, setDatasetName] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      let items: ConnectorCapability[] = [];
      try {
        const cat = await api.listConnectors();
        items = cat.items.filter((c) => MVP_TYPES.includes(c.connector_type));
      } catch (err) {
        if (err instanceof ApiError && (err.status === 404 || err.status >= 500)) {
          items = FALLBACK_CONNECTORS;
          setError(
            "Catálogo de conectores ainda não disponível na API — a usar tipos MVP locais (postgres / REST).",
          );
        } else {
          throw err;
        }
      }
      setCatalog(items.length ? items : FALLBACK_CONNECTORS);

      try {
        const list = await api.listDataSources();
        setSources(list.items);
      } catch (err) {
        if (!(err instanceof ApiError && err.status === 404)) {
          throw err;
        }
        setSources([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao carregar fontes.");
    } finally {
      setLoading(false);
    }
  }, [api]);

  useEffect(() => {
    void load();
  }, [load]);

  const draftBody = useMemo((): DataSourceCreate | null => {
    if (!selected) return null;
    if (selected.connector_type === "postgres") {
      const secret: Record<string, string> | null = password
        ? { password }
        : null;
      return {
        name: name.trim(),
        connector_type: "postgres",
        config: {
          host: host.trim(),
          port: Number(port) || 5432,
          database: database.trim(),
          username: username.trim(),
          ssl,
        },
        secret,
      };
    }
    const secret: Record<string, string> | null = apiKey
      ? { api_key: apiKey }
      : null;
    return {
      name: name.trim(),
      connector_type: "rest_json",
      config: {
        base_url: baseUrl.trim(),
        path: restPath.trim(),
        method: "GET",
      },
      secret,
    };
  }, [
    selected,
    name,
    host,
    port,
    database,
    username,
    password,
    ssl,
    baseUrl,
    restPath,
    apiKey,
  ]);

  async function onTest(e?: FormEvent) {
    e?.preventDefault();
    if (!draftBody || !draftBody.name) {
      setError("Indique um nome para a fonte.");
      return;
    }
    setBusy(true);
    setError(null);
    setSuccess(null);
    try {
      let result;
      try {
        result = await api.testConnectionDraft(draftBody);
      } catch (err) {
        if (err instanceof ApiError && err.status === 404 && saved) {
          result = await api.testConnection(saved.id);
        } else if (err instanceof ApiError && err.status === 404) {
          setSuccess(
            "Endpoint de teste pré-gravação indisponível. Grave a fonte e teste depois.",
          );
          return;
        } else {
          throw err;
        }
      }
      if (result.ok) {
        setSuccess(result.message || "Ligação bem-sucedida.");
      } else {
        setError(result.message || "Falha no teste de ligação.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro no teste.");
    } finally {
      setBusy(false);
    }
  }

  async function onSave(e: FormEvent) {
    e.preventDefault();
    if (!draftBody || !draftBody.name) {
      setError("Indique um nome para a fonte.");
      return;
    }
    setBusy(true);
    setError(null);
    setSuccess(null);
    try {
      const item = await api.createDataSource(draftBody);
      setSaved(item);
      setSources((prev) => [item, ...prev]);
      setStep("done");
      setSuccess(`Fonte «${item.name}» gravada.`);
      setDatasetName(item.name);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao gravar fonte.");
    } finally {
      setBusy(false);
    }
  }

  async function onSyncAndPublish() {
    if (!saved) return;
    setBusy(true);
    setError(null);
    setSuccess(null);
    try {
      let syncMsg = "";
      try {
        const sync = await api.triggerSync(saved.id, {
          object_id: objectId.trim() || null,
          mode: "full",
        });
        syncMsg = sync.message;
      } catch (err) {
        if (!(err instanceof ApiError && err.status === 404)) {
          throw err;
        }
        syncMsg = "Sync API ainda não disponível — a publicar dataset.";
      }

      const pub = await api.publishDataset({
        name: (datasetName || saved.name).trim(),
        data_source_id: saved.id,
        object_id: objectId.trim() || null,
        client_draft_id: `desktop-${saved.id}`,
      });
      setSuccess(
        `${syncMsg} Publicação: ${pub.message} (estado: ${pub.status}${
          pub.dataset_id ? `, dataset ${pub.dataset_id}` : ""
        }).`,
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Falha ao sincronizar/publicar.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function syncExisting(id: string) {
    setBusy(true);
    setError(null);
    setSuccess(null);
    try {
      const sync = await api.triggerSync(id, { mode: "full" });
      setSuccess(sync.message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha no sync.");
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <section className="panel">
        <p className="muted">A carregar fontes de dados…</p>
      </section>
    );
  }

  return (
    <section className="panel" aria-labelledby="ds-title">
      <div className="panel-head">
        <h2 id="ds-title">Fontes de dados</h2>
        {step !== "list" ? (
          <button
            type="button"
            className="btn ghost"
            onClick={() => {
              setStep("list");
              setSaved(null);
              setSuccess(null);
              setError(null);
            }}
          >
            Voltar à lista
          </button>
        ) : (
          <button
            type="button"
            className="btn primary"
            onClick={() => {
              setStep("pick");
              setError(null);
              setSuccess(null);
            }}
          >
            Nova fonte
          </button>
        )}
      </div>

      {error ? <p className="error-banner" role="alert">{error}</p> : null}
      {success ? <p className="success-banner" role="status">{success}</p> : null}

      {step === "list" ? (
        sources.length === 0 ? (
          <p className="empty-state">
            Ainda não há fontes neste tenant. Crie uma ligação PostgreSQL ou REST.
          </p>
        ) : (
          <ul className="source-list">
            {sources.map((s) => (
              <li key={s.id}>
                <div>
                  <strong>{s.name}</strong>
                  <span className="muted">
                    {" "}
                    · {s.connector_type} · {s.status}
                  </span>
                </div>
                <button
                  type="button"
                  className="btn ghost"
                  disabled={busy}
                  onClick={() => void syncExisting(s.id)}
                >
                  Sincronizar
                </button>
              </li>
            ))}
          </ul>
        )
      ) : null}

      {step === "pick" ? (
        <div className="connector-grid">
          {catalog.map((c) => (
            <button
              key={c.connector_type}
              type="button"
              className="connector-card"
              onClick={() => {
                setSelected(c);
                setName("");
                setStep("configure");
              }}
            >
              <strong>{c.display_name}</strong>
              <span className="muted">{c.description}</span>
            </button>
          ))}
        </div>
      ) : null}

      {step === "configure" && selected ? (
        <form className="stack form-grid" onSubmit={(e) => void onSave(e)}>
          <label>
            Nome da fonte
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              maxLength={200}
              disabled={busy}
            />
          </label>

          {selected.connector_type === "postgres" ? (
            <>
              <label>
                Host
                <input
                  value={host}
                  onChange={(e) => setHost(e.target.value)}
                  required
                  disabled={busy}
                />
              </label>
              <label>
                Porta
                <input
                  value={port}
                  onChange={(e) => setPort(e.target.value)}
                  required
                  disabled={busy}
                />
              </label>
              <label>
                Base de dados
                <input
                  value={database}
                  onChange={(e) => setDatabase(e.target.value)}
                  required
                  disabled={busy}
                />
              </label>
              <label>
                Utilizador
                <input
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
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
                  autoComplete="new-password"
                  disabled={busy}
                />
              </label>
              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={ssl}
                  onChange={(e) => setSsl(e.target.checked)}
                  disabled={busy}
                />
                Usar SSL
              </label>
            </>
          ) : (
            <>
              <label>
                URL base
                <input
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  required
                  disabled={busy}
                />
              </label>
              <label>
                Caminho
                <input
                  value={restPath}
                  onChange={(e) => setRestPath(e.target.value)}
                  required
                  disabled={busy}
                />
              </label>
              <label>
                API key (opcional)
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  autoComplete="off"
                  disabled={busy}
                />
              </label>
            </>
          )}

          <div className="btn-row">
            <button
              type="button"
              className="btn ghost"
              disabled={busy}
              onClick={() => void onTest()}
            >
              Testar ligação
            </button>
            <button type="submit" className="btn primary" disabled={busy}>
              {busy ? "A gravar…" : "Gravar fonte"}
            </button>
          </div>
        </form>
      ) : null}

      {step === "done" && saved ? (
        <div className="stack">
          <p>
            Fonte <strong>{saved.name}</strong> pronta. Dispare sync e publique o
            dataset para o catálogo do tenant.
          </p>
          <label>
            Objecto / tabela (opcional)
            <input
              value={objectId}
              onChange={(e) => setObjectId(e.target.value)}
              placeholder="ex.: public.vendas"
              disabled={busy}
            />
          </label>
          <label>
            Nome do dataset
            <input
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              required
              disabled={busy}
            />
          </label>
          <div className="btn-row">
            <button
              type="button"
              className="btn primary"
              disabled={busy}
              onClick={() => void onSyncAndPublish()}
            >
              {busy ? "A publicar…" : "Sincronizar e publicar dataset"}
            </button>
          </div>
        </div>
      ) : null}
    </section>
  );
}
